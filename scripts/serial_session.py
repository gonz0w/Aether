# SPDX-License-Identifier: BSD-2-Clause
"""Frozen prompt-driven SESSION input and strict UART/lifecycle framing."""
import hashlib
import json
import os
from pathlib import Path
import re
import select
import shutil
import subprocess
import time
from datetime import datetime, timezone
from fixture_inputs import read_inputs
from deps import ROOT, DEPS

PACKET = ROOT / 'tests/fixtures/serial-session-2026-09-29'
CASES = [
    ('composed', '', '', None, 30),
    ('wrong-env', 'SESSION_WRONG_ENV', 'session_wrong_env', 2800, 2),
    ('bad-byte', '', 'serial_bad_byte', None, 30),
    ('bad-substitution', '', 'session_bad_substitution', 2801, 6),
    ('fd-leak', 'SESSION_FD_LEAK', 'session_fd_leak', 2802, 10),
    ('stale-wait', 'SESSION_STALE_WAIT', '', None, 30),
    ('stale-reference', 'SERIAL_STALE_REFERENCE', '', None, 30),
    ('wrong-grant', '', 'serial_wrong_grant', 2891, 1),
    ('cancel', '', 'serial_cancel', 2890, 5),
    ('stderr-error', '', 'serial_stderr_error', 2892, 10),
    ('stderr-route', '', 'serial_stderr_route', None, 30),
]
# copies, execs, parent terminal kind/detail, stdout, prompt count, inputs sent
NEGATIVES = {
    'wrong-env': (1, 1, 1, 31, b'', 1, 1),
    'bad-substitution': (5, 4, 1, 33, b'argv ok\npipe data\n', 2, 2),
    'fd-leak': (9, 7, 1, 35, b'argv ok\npipe data\nsubstitution ok\npipe data\n', 3, 3),
    'wrong-grant': (0, 0, 3, 143, b'', 0, 0),
    'cancel': (4, 3, 3, 143, b'argv ok\npipe data\n', 2, 1),
    'stderr-error': (9, 7, 1, 141, b'argv ok\npipe data\nsubstitution ok\npipe data\nclosed ok\nsession ok\n', 3, 3),
}


def consumer_inputs():
    return read_inputs('serial-session-2026-09-29', INPUTS)


INPUTS = json.loads((PACKET / 'pin.json').read_text())
BOUNDARY = b'NATIVE SUPERVISION: sys-init owns launch/retry policy; bounded local grants\n'
RECORDS = [
    (b'NATIVE MEMORY admitted ', rb'NATIVE MEMORY admitted slot=[0-4] generation=[0-9]+ used=[0-9]+ remaining=[0-9]+\n'),
    (b'NATIVE terminal ', rb'NATIVE terminal slot=[0-4] generation=[0-9]+ kind=[0-9]+ detail=[0-9]+\n'),
    (b'NATIVE SESSION ', rb'NATIVE SESSION generation=[1-3] copies=[0-9]+ execs=[0-9]+ stdout=[0-9a-f]* stderr=[0-9a-f]*\n'),
    (b'NATIVE supervisor ', rb'NATIVE supervisor result=[0-9]+ reclaimed=[0-9]+\n'),
    (b'AETHER NATIVE CONSOLE PASS', rb'AETHER NATIVE CONSOLE PASS\n'),
    (b'AETHER PANIC:', rb'AETHER PANIC: native C profile rejected\n'),
]


def decode(raw):
    """Known records consume exact spans; every other byte is UART, never dropped."""
    start = raw.find(BOUNDARY)
    if start < 0:
        return b'', [], []
    cursor = start + len(BOUNDARY)
    uart, positions, records = bytearray(), [], []
    while cursor < len(raw):
        rest = raw[cursor:]
        selected = next(((prefix, pattern) for prefix, pattern in RECORDS
                         if rest.startswith(prefix) or prefix.startswith(rest)), None)
        if selected:
            prefix, pattern = selected
            end = rest.find(b'\n')
            if end < 0:
                break
            line = rest[:end + 1]
            if not re.fullmatch(pattern, line):
                raise RuntimeError('SERIAL-SESSION malformed kernel record')
            records.append(dict(start=cursor, end=cursor + len(line), text=line.decode().rstrip('\n')))
            cursor += len(line)
        else:
            uart.append(raw[cursor])
            positions.append(cursor)
            cursor += 1
    return bytes(uart), positions, records


def prompt_boundaries(inputs):
    exchange = json.loads(inputs['exchange.json'])
    offset, result = 0, []
    for generation in range(1, 4):
        for phase in range(1, 4):
            offset += 2
            result.append((generation, phase, offset))
            offset += len(bytes.fromhex(exchange['steps'][phase - 1]['expected_uart_after_input_hex']))
    return result


def validate_prompt(generation, phase, uart, records, inputs):
    boundary = next(n for g, p, n in prompt_boundaries(inputs) if (g, p) == (generation, phase))
    if uart != (inputs['expected.uart'] * 3)[:boundary]:
        raise RuntimeError('SERIAL-SESSION prompt/byte mismatch')
    texts = [r['text'] for r in records]
    if sum(s.startswith(f'NATIVE MEMORY admitted slot=0 generation={generation} ') for s in texts) != 1:
        raise RuntimeError('SERIAL-SESSION parent generation mismatch')
    required = []
    if generation > 1:
        required.append((0, generation - 1))
    if phase >= 2:
        required += [(2, 5 * generation - 4), (2, 5 * generation - 3),
                     (3, 2 * generation - 1), (4, 2 * generation - 1)]
    if phase >= 3:
        required += [(2, 5 * generation - 2), (2, 5 * generation - 1),
                     (3, 2 * generation), (4, 2 * generation)]
    for slot, epoch in required:
        if texts.count(f'NATIVE terminal slot={slot} generation={epoch} kind=1 detail=0') != 1:
            raise RuntimeError('SERIAL-SESSION prompt before phase cleanup')


def check_serial(raw, events, inputs):
    uart, positions, records = decode(raw)
    if uart != inputs['expected.uart'] * 3:
        raise RuntimeError('SERIAL-SESSION UART mismatch')
    # Reuse the accepted SESSION lifecycle oracle with explicitly separate prompt stderr.
    from session_smoke import check_session
    expected = inputs.copy()
    expected['expected.stderr'] = b'$ ' * 3 + inputs['expected.stderr']
    serial = '\n'.join(r['text'] for r in records).replace('AETHER NATIVE CONSOLE PASS', 'AETHER NATIVE CONNECTIONS PASS')
    check_session(serial, 'composed', expected)
    texts = [r['text'] for r in records]
    admitted = [(int(m[1]), int(m[2])) for t in texts if (m := re.fullmatch(r'NATIVE MEMORY admitted slot=(\d+) generation=(\d+) used=\d+ remaining=\d+', t))]
    wanted = {(0, g) for g in range(1, 4)} | {(2, g) for g in (1, 3, 5, 6, 8, 10, 11, 13, 15)} | {(slot, g) for slot in (3, 4) for g in range(1, 7)}
    if len(admitted) != 24 or set(admitted) != wanted:
        raise RuntimeError('SERIAL-SESSION admission identity mismatch')
    for generation in range(1, 4):
        observed = next(i for i, t in enumerate(texts) if t.startswith(f'NATIVE SESSION generation={generation} '))
        ids = {(0, generation)} | {(2, g) for g in range(5*generation-4, 5*generation+1)} | {(slot, g) for slot in (3, 4) for g in (2*generation-1, 2*generation)}
        for slot, epoch in ids:
            if texts.index(f'NATIVE terminal slot={slot} generation={epoch} kind=1 detail=0') >= observed:
                raise RuntimeError('SERIAL-SESSION observation before generation cleanup')
        if generation < 3:
            next_parent = next(i for i, t in enumerate(texts) if t.startswith(f'NATIVE MEMORY admitted slot=0 generation={generation+1} '))
            if observed >= next_parent:
                raise RuntimeError('SERIAL-SESSION parent reuse before observation')
    check_events(raw, events, inputs, 9)
    return records


def check_events(raw, events, inputs, count):
    uart, positions, records = decode(raw)
    if len(events) != count:
        raise RuntimeError('SERIAL-SESSION input count mismatch')
    for event, (generation, phase, boundary) in zip(events, prompt_boundaries(inputs)):
        if (event['generation'], event['phase'], event['prompt_uart_offset']) != (generation, phase, boundary):
            raise RuntimeError('SERIAL-SESSION stale prompt/generation')
        raw_prompt = positions[boundary - 1] + 1
        if event['prompt_raw_offset'] != raw_prompt or event['observed_raw_bytes'] < raw_prompt:
            raise RuntimeError('SERIAL-SESSION input before prompt')
        prior = [r for r in records if r['end'] <= raw_prompt]
        validate_prompt(generation, phase, uart[:boundary], prior, inputs)
        wanted = inputs[f'command-{phase}.sh']
        offset = 0
        for write in event['writes']:
            requested = bytes.fromhex(write['requested_hex'])
            count = write['accepted']
            if write['offset'] != offset or not 0 < count <= len(requested) or requested != wanted[offset:offset + len(requested)]:
                raise RuntimeError('SERIAL-SESSION input offset/byte mismatch')
            offset += count
        if offset != len(wanted) or len(event['writes']) < 2:
            raise RuntimeError('SERIAL-SESSION incomplete short-write input')
    return records


def check_run(raw, events, inputs, label):
    if label not in NEGATIVES:
        expected = inputs.copy()
        if label == 'bad-byte':
            expected['expected.uart'] = inputs['expected.uart'].replace(b'pipe data', b'PiPe data')
        if label == 'stderr-route':
            expected['expected.stdout'] = inputs['expected.stdout'].replace(b'session ok\n', b'session diagnostic\nsession ok\n')
            expected['expected.stderr'] = b''
        check_serial(raw, events, expected)
        if label in ('bad-byte', 'stderr-route'):
            try:
                check_serial(raw, events, inputs)
            except RuntimeError:
                return
            raise RuntimeError('SERIAL-SESSION UART corruption escaped positive oracle')
        return
    from session_smoke import observations
    copies, execs, kind, detail, stdout, prompts, sent = NEGATIVES[label]
    uart, positions, records = decode(raw)
    texts = [r['text'] for r in records]
    _, _, _, result, reclaimed = next(c for c in CASES if c[0] == label)
    completion = f'NATIVE supervisor result={result} reclaimed={reclaimed}'
    if texts.count(completion) != 1 or sum(t.startswith('NATIVE supervisor result=') for t in texts) != 1:
        raise RuntimeError('SERIAL-SESSION negative completion mismatch')
    if texts.count('AETHER PANIC: native C profile rejected') != 1 or 'AETHER NATIVE CONSOLE PASS' in texts:
        raise RuntimeError('SERIAL-SESSION negative final marker mismatch')
    rows = observations('\n'.join(texts))
    if rows != [(1, copies, execs, stdout, b'$ ' * prompts)]:
        raise RuntimeError('SERIAL-SESSION negative streams/counts mismatch')
    wanted = inputs['expected.uart'][:len(stdout) + prompts * 2]
    if label == 'stderr-error':
        wanted = inputs['expected.uart'].replace(b'session diagnostic\n', b'')
    if uart != wanted:
        raise RuntimeError('SERIAL-SESSION negative UART mismatch')
    rounds = (0, 0) if not copies else (1, 0) if copies == 1 else (2, 1) if copies == 4 else (3, 1) if copies == 5 else (5, 2)
    children = {(2, g) for g in range(1, rounds[0]+1)} | {(slot, g) for slot in (3, 4) for g in range(1, rounds[1]+1)}
    terminal = [(0, 1, kind, detail)] + [(slot, g, 1, 91 if label == 'wrong-env' else 95 if label == 'fd-leak' and (slot, g) == (2, 5) else 0) for slot, g in children]
    actual = [tuple(map(int, re.fullmatch(r'NATIVE terminal slot=(\d+) generation=(\d+) kind=(\d+) detail=(\d+)', t).groups())) for t in texts if t.startswith('NATIVE terminal ')]
    if len(actual) != reclaimed or sorted(actual) != sorted(terminal):
        raise RuntimeError('SERIAL-SESSION negative terminal mismatch')
    admitted = {(0, 1)} | (children - {(2, g) for g in (2, 4)})
    actual_admitted = [(int(m[1]), int(m[2])) for t in texts if (m := re.fullmatch(r'NATIVE MEMORY admitted slot=(\d+) generation=(\d+) used=\d+ remaining=\d+', t))]
    if len(actual_admitted) != len(admitted) or set(actual_admitted) != admitted:
        raise RuntimeError('SERIAL-SESSION negative admission mismatch')
    observed = [i for i, t in enumerate(texts) if t.startswith('NATIVE SESSION ')]
    terminals = [i for i, t in enumerate(texts) if t.startswith('NATIVE terminal ')]
    if not max(terminals) < observed[0] < texts.index(completion) < texts.index('AETHER PANIC: native C profile rejected'):
        raise RuntimeError('SERIAL-SESSION negative cleanup order mismatch')
    check_events(raw, events, inputs, sent)
    if label == 'cancel':
        boundary = len(uart)
        prior = [r for r in records if r['end'] <= positions[boundary-1]+1]
        validate_prompt(1, 2, uart, prior, inputs)


def run_serial(image, label='composed'):
    out = image.parent
    variables = out / 'serial-vars.fd'
    shutil.copyfile(DEPS / 'firmware/vars.fd', variables)
    argv = ['qemu-system-x86_64', '-machine', 'pc-q35-11.1', '-accel', 'tcg', '-cpu', 'qemu64',
            '-smp', '1', '-m', '256M', '-drive', f'if=pflash,format=raw,readonly=on,file={DEPS / "firmware/code.fd"}',
            '-drive', f'if=pflash,format=raw,file={variables}', '-cdrom', str(image), '-boot', 'd',
            '-nic', 'none', '-vga', 'std', '-display', 'none', '-serial', 'stdio', '-monitor', 'none', '-no-reboot', '-no-shutdown']
    inputs = consumer_inputs()
    if label == 'bad-byte':
        inputs['expected.uart'] = inputs['expected.uart'].replace(b'pipe data', b'PiPe data')
    boundaries = prompt_boundaries(inputs)
    input_limit = NEGATIVES[label][-1] if label in NEGATIVES else 9
    raw, events = bytearray(), []
    report = dict(argv=argv, case=label, start_utc=datetime.now(timezone.utc).isoformat(), status='incomplete')
    with (out / 'serial-qemu.log').open('wb') as log:
        process = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=log)
        try:
            deadline = time.monotonic() + 45
            while time.monotonic() < deadline:
                if select.select([process.stdout], [], [], 0.02)[0]:
                    chunk = os.read(process.stdout.fileno(), 4096)
                    if not chunk:
                        raise RuntimeError('SERIAL-SESSION early emulator exit')
                    raw.extend(chunk)
                    if len(raw) > 1024 * 1024:
                        raise RuntimeError('SERIAL-SESSION log budget exceeded')
                uart, positions, records = decode(bytes(raw))
                texts = [r['text'] for r in records]
                if 'AETHER PANIC: native C profile rejected' in texts or 'AETHER NATIVE CONSOLE PASS' in texts:
                    check_run(bytes(raw), events, consumer_inputs(), label)
                    report['status'] = 'pass'
                    break
                if len(events) < input_limit:
                    generation, phase, boundary = boundaries[len(events)]
                    if len(uart) >= boundary:
                        validate_prompt(generation, phase, uart, records, inputs)
                        event = dict(generation=generation, phase=phase, prompt_uart_offset=boundary,
                                     prompt_raw_offset=positions[boundary - 1] + 1, observed_raw_bytes=len(raw), writes=[])
                        wanted, offset = inputs[f'command-{phase}.sh'], 0
                        while offset < len(wanted):
                            requested = wanted[offset:offset + 7]
                            accepted = os.write(process.stdin.fileno(), requested)
                            if not 0 < accepted <= len(requested):
                                raise RuntimeError('SERIAL-SESSION short write made no progress')
                            event['writes'].append(dict(offset=offset, requested_hex=requested.hex(), accepted=accepted))
                            offset += accepted
                        events.append(event)
            else:
                raise TimeoutError('SERIAL-SESSION native deadline')
        finally:
            (out / 'native-serial.log').write_bytes(raw)
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=3)
                    report['forced_teardown'] = True
            process.stdin.close()
            process.stdout.close()
            report.update(events=events, end_utc=datetime.now(timezone.utc).isoformat(), process_reaped=True)
            (out / 'serial-exchange.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: prompt-driven serial SESSION ' + label, flush=True)
