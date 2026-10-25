# SPDX-License-Identifier: BSD-2-Clause
"""Bounded ABI24 candidate workload and independent producer acceptance oracle."""
# check() below is copied unchanged from the sealed Aether-userland producer
# oracle (BSD-2-Clause); see docs/aether-session.lock.json for origin identity.
import json
from pathlib import Path
import re
import os
import selectors
import signal
import subprocess
import time


def need(ok, message):
    if not ok:
        raise ValueError(message)


BOUNDARY = b'NATIVE SUPERVISION: sys-init owns launch/retry policy; bounded local grants\n'
ADMISSION = rb'NATIVE MEMORY admitted slot=([0-4]) generation=([0-9]+) used=([0-9]+) remaining=([0-9]+)\n'
TERMINAL = rb'NATIVE terminal slot=([0-4]) generation=([0-9]+) kind=([0-9]+) detail=([0-9]+)\n'
HALT = rb'NATIVE init halted ticks=([0-9]+) idle=([0-9]+) reclaimed=([0-9]+)\n'


def check(raw, record, workload):
    need(raw.count(BOUNDARY) == 1, 'unique supervision boundary')
    need(b'AETHER PANIC:' not in raw and b'NATIVE supervisor result=' not in raw
         and b'NATIVE SESSION ' not in raw, 'no alternate failure/completion')
    cursor = raw.index(BOUNDARY) + len(BOUNDARY)
    uart = bytearray()
    positions = []
    admitted = []
    terminal = []
    halt = []
    while cursor < len(raw):
        rest = raw[cursor:]
        match = re.match(ADMISSION, rest)
        if match:
            admitted.append((tuple(map(int, match.groups())), cursor))
        else:
            match = re.match(TERMINAL, rest)
            if match:
                terminal.append((tuple(map(int, match.groups())), cursor))
            else:
                match = re.match(HALT, rest)
                if match:
                    halt.append((tuple(map(int, match.groups())), cursor))
        if match:
            cursor += len(match[0])
        else:
            # Unknown/malformed diagnostics remain bytes and fail exact UART.
            uart.append(raw[cursor])
            positions.append(cursor)
            cursor += 1
    need(len(halt) == 1 and halt[0][1] + len(re.match(HALT, raw[halt[0][1]:])[0]) == len(raw), 'unique final halt')
    polling = record['label'] == 'polling-limit'
    expected_uart = b'$ ' if polling else bytes.fromhex(workload['expected.uart'])
    need(bytes(uart) == expected_uart, 'exact UART bytes')
    expected_terminal = {(0, 1, 1, 0)}
    if not polling:
        expected_terminal |= {(2, g, 1, 0) for g in range(1, 6)}
        expected_terminal |= {(s, g, 1, 0) for s in (3, 4) for g in (1, 2)}
    need(len(terminal) == len(expected_terminal)
         and {x for x, _ in terminal} == expected_terminal, 'exact terminal identities')
    expected_admitted = {(0, 1)} if polling else {(0, 1), (2, 1), (2, 3), (2, 5), (3, 1), (3, 2), (4, 1), (4, 2)}
    need(len(admitted) == len(expected_admitted)
         and {x[:2] for x, _ in admitted} == expected_admitted, 'exact admission identities')
    need(all(x[2:] == ((73, 55) if x[0] == 0 else (24, 104))
             for x, _ in admitted), 'bounded memory observations')
    need(all(offset < halt[0][1] for _, offset in terminal), 'all terminals before halt')
    events = record['events']
    need(len(events) == (0 if polling else 3), 'input count')
    offset = 0
    exchange = json.loads(bytes.fromhex(workload['exchange.json']))
    for i, event in enumerate(events):
        phase = i + 1
        offset += 2
        raw_boundary = positions[offset - 1] + 1
        need((event['generation'], event['phase'], event['prompt_uart_offset']) == (1, phase, offset)
             and event['prompt_raw_offset'] == raw_boundary
             and event['observed_raw_bytes'] >= raw_boundary, 'prompt-driven input')
        required = {(2, 1), (2, 2), (3, 1), (4, 1)} if phase >= 2 else set()
        if phase >= 3:
            required |= {(2, 3), (2, 4), (3, 2), (4, 2)}
        prior = {x[:2] for x, at in terminal if at < raw_boundary}
        need(required <= prior, 'phase cleanup before next prompt')
        command = bytes.fromhex(workload['command-' + str(phase) + '.sh'])
        sent = 0
        for write in event['writes']:
            requested = bytes.fromhex(write['requested_hex'])
            accepted = write['accepted']
            need(write['offset'] == sent and 0 < accepted <= len(requested)
                 and requested == command[sent:sent + len(requested)], 'exact input fragments')
            sent += accepted
        need(sent == len(command) and len(event['writes']) >= 2, 'complete fragmented input')
        need(event['delay_seconds'] >= (35 if record['label'] == 'delayed' and phase == 1
                                       else 2 if record['label'] == 'delayed' else 0), 'input delay')
        offset += len(bytes.fromhex(exchange['steps'][i]['expected_uart_after_input_hex']))
    ticks, idle, reclaims = halt[0][0]
    need((ticks, idle, reclaims) == (record['ticks'], record['idle'], record['reclaims'])
         and reclaims == len(expected_terminal), 'halt receipt agreement')
    if record['label'] == 'delayed':
        need(ticks > 3000 and idle > 3000, 'idle witness')
    if polling:
        need(ticks < 3000, 'old polling exhausted before delayed input')
    need(record['cleanup'] == 'emulator-reaped', 'emulator cleanup')
    return {'uart_bytes': len(uart), 'terminals': len(terminal), 'admissions': len(admitted)}


def qemu_args(qemu, image, code, variables):
    return [qemu, '-machine', 'pc-q35-11.1', '-accel', 'tcg', '-cpu', 'qemu64',
            '-smp', '1', '-m', '256M', '-drive',
            f'if=pflash,format=raw,readonly=on,file={code}', '-drive',
            f'if=pflash,format=raw,file={variables}', '-cdrom', str(image),
            '-display', 'none', '-serial', 'stdio', '-monitor', 'none',
            '-net', 'none', '-no-reboot']


def smoke(output, qemu, workload, delayed=False):
    label = 'delayed' if delayed else 'immediate'
    variables = output / 'smoke-vars.fd'
    variables.write_bytes((output / 'kit/vars.fd').read_bytes())
    argv = qemu_args(qemu, output / 'aether.iso', output / 'kit/code.fd', variables)
    record = {'label': label, 'status': 'incomplete', 'argv': argv, 'events': []}
    raw, stderr = bytearray(), bytearray()
    child = None
    try:
        environment = os.environ.copy()
        environment.pop('DYLD_LIBRARY_PATH', None)
        child = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, start_new_session=True, env=environment)
        os.set_blocking(child.stdin.fileno(), False)
        deadline = time.monotonic() + 90
        prompt_at, boundary = None, 2
        expected = bytes.fromhex(workload['expected.uart'])
        exchange = json.loads(bytes.fromhex(workload['exchange.json']))
        with selectors.DefaultSelector() as selector:
            selector.register(child.stdout, selectors.EVENT_READ, raw)
            selector.register(child.stderr, selectors.EVENT_READ, stderr)
            while time.monotonic() < deadline:
                for key, _ in selector.select(0.02):
                    chunk = os.read(key.fd, 4096)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    limit = 1024 * 1024 if key.data is raw else 4 * 1024 * 1024
                    available = limit - len(key.data)
                    key.data.extend(chunk[:available])
                    need(len(chunk) <= available, 'native output exceeds budget')
                need(b'AETHER PANIC:' not in raw, 'guest failed')
                halt = re.search(HALT, raw)
                if halt:
                    ticks, idle, reclaims = map(int, halt.groups())
                    record.update(ticks=ticks, idle=idle, reclaims=reclaims)
                    break
                need(selector.get_map(),
                     'guest exited before complete halt')
                if len(record['events']) == 3 or BOUNDARY not in raw:
                    continue
                rest = bytes(raw).split(BOUNDARY, 1)[1]
                uart, positions = bytearray(), []
                offset = bytes(raw).index(BOUNDARY) + len(BOUNDARY)
                partial = False
                while rest:
                    marker = re.match(rb'(?:' + ADMISSION + rb'|' + TERMINAL + rb')', rest)
                    if marker:
                        offset += len(marker[0]); rest = rest[len(marker[0]):]
                        continue
                    if (rest.startswith(b'NATIVE ') or b'NATIVE '.startswith(rest)) and b'\n' not in rest:
                        partial = True; break
                    uart.append(rest[0]); positions.append(offset)
                    rest = rest[1:]; offset += 1
                if partial or len(uart) < boundary:
                    continue
                need(bytes(uart[:boundary]) == expected[:boundary], 'unexpected prompt/stream')
                if prompt_at is None:
                    prompt_at = time.monotonic()
                phase = len(record['events']) + 1
                delay = (35 if phase == 1 else 2) if delayed else 0
                if time.monotonic() - prompt_at < delay:
                    continue
                command = bytes.fromhex(workload[f'command-{phase}.sh'])
                writes, sent = [], 0
                while sent < len(command):
                    chunk = command[sent:sent + 7]
                    need(time.monotonic() < deadline, 'native input deadline exceeded')
                    try:
                        accepted = os.write(child.stdin.fileno(), chunk)
                    except BlockingIOError:
                        time.sleep(0.01)
                        continue
                    need(accepted and accepted <= len(chunk), 'input write failed')
                    writes.append({'offset': sent, 'requested_hex': chunk.hex(), 'accepted': accepted})
                    sent += accepted
                record['events'].append({'generation': 1, 'phase': phase,
                    'prompt_uart_offset': boundary, 'prompt_raw_offset': positions[boundary - 1] + 1,
                    'observed_raw_bytes': len(raw), 'delay_seconds': time.monotonic() - prompt_at,
                    'writes': writes})
                boundary += len(bytes.fromhex(exchange['steps'][phase - 1]['expected_uart_after_input_hex'])) + 2
                prompt_at = None
            else:
                raise TimeoutError('native deadline exceeded')
    except BaseException as error:
        record.update(status='fail', error=repr(error))
        raise
    finally:
        if child is not None:
            try:
                if child.poll() is None:
                    os.killpg(child.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                child.wait(timeout=3)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait(timeout=3)
            record.update(cleanup='emulator-reaped', emulator_exit=child.returncode)
            child.stdin.close()
            child.stdout.close()
            child.stderr.close()
        (output / 'serial.log').write_bytes(raw)
        (output / 'qemu.stderr').write_bytes(stderr)
        (output / 'smoke.json').write_text(json.dumps(record, indent=2) + '\n')
    try:
        record['oracle'] = check(bytes(raw), record, workload)
        record['status'] = 'pass'
    except BaseException as error:
        record.update(status='fail', error=repr(error))
        raise
    finally:
        (output / 'smoke.json').write_text(json.dumps(record, indent=2) + '\n')
    return record
