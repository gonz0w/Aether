# SPDX-License-Identifier: BSD-2-Clause
"""Replay one frozen owner schedule with bounded I/O and complete panic framing."""
import json
import os
from pathlib import Path
import re
import select
import shutil
import subprocess
import sys
import time
import types
from boot import verify, need, sha
import serial_oracle as oracle

kit = Path(sys.argv[1])
seal = sys.argv[2]
P = Path(sys.argv[3])
initial_delay = int(sys.argv[4])
need(initial_delay in (0, 35), 'worker delay')
receipt, workload, owner = verify(kit, seal)
case = 'session'
selected = 'sealed-kit'
fragment = 7
pace = 0
iso = kit / 'aether.iso'
qemu = receipt['tools']['qemu-system-x86_64']
work = P
need(not (P / 'session.json').exists(), 'case output exists')
out = work / case
out.mkdir()
variables = out / 'vars.fd'
shutil.copy2(kit / 'vars.fd', variables)
argv = [qemu['path'], '-machine', 'pc-q35-11.1', '-accel', 'tcg', '-cpu', 'qemu64',
        '-smp', '1', '-m', '256M', '-drive',
        'if=pflash,format=raw,readonly=on,file=' + str(kit / 'code.fd'),
        '-drive', 'if=pflash,format=raw,file=' + str(variables),
        '-cdrom', str(iso), '-boot', 'd', '-nic', 'none', '-vga', 'std',
        '-display', 'none', '-serial', 'stdio', '-monitor', 'none',
        '-no-reboot', '-no-shutdown']
expected = bytes.fromhex(workload['expected.uart'])
exchange = json.loads(bytes.fromhex(workload['exchange.json']))
raw = bytearray()
events = []
record = {'status': 'incomplete', 'case': case, 'owner': selected,
          'label': 'delayed' if initial_delay else 'immediate', 'argv': argv,
          'events': events, 'cleanup': 'not-started', 'driver_sha256': sha(Path(__file__)),
          'iso_sha256': sha(iso), 'fragment_bytes': fragment,
          'fragment_pace_seconds': pace}
child = None
try:
    with (out / 'qemu.stderr').open('wb') as error:
        child = subprocess.Popen(argv, cwd=out, env=owner.clean_env(out),
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=error)
        start = time.monotonic()
        prompt_at = None
        boundary = 2
        while time.monotonic() - start < 90:
            need((out / 'qemu.stderr').stat().st_size <= 4 * 1024**2, 'stderr bound')
            if select.select([child.stdout], [], [], 0.02)[0]:
                chunk = os.read(child.stdout.fileno(), 4096)
                need(bool(chunk), 'emulator exited before complete outcome')
                raw.extend(chunk)
                need(len(raw) < 1024 * 1024, 'serial bound')
            panic = re.search(rb'AETHER PANIC: [^\n]*\n', raw)
            if panic:
                record['status'] = 'fail-native-owner'
                raise ValueError('unexpected native owner failure')
            # Keep collecting failures through the complete kernel panic line.
            if b'SESSION owner failed' in raw or b'SYSINIT-CHECK ' in raw:
                continue
            halt = re.search(oracle.HALT, raw)
            if halt:
                record.update(ticks=int(halt[1]), idle=int(halt[2]), reclaims=int(halt[3]))
                record['status'] = 'pass'
                break
            if oracle.BOUNDARY not in raw:
                continue
            cursor = raw.index(oracle.BOUNDARY) + len(oracle.BOUNDARY)
            uart = bytearray()
            positions = []
            partial = False
            while cursor < len(raw):
                rest = bytes(raw[cursor:])
                matched = re.match(oracle.ADMISSION, rest) or re.match(oracle.TERMINAL, rest)
                if matched:
                    cursor += len(matched[0])
                    continue
                if (rest.startswith(b'NATIVE ') or b'NATIVE '.startswith(rest)) and b'\n' not in rest:
                    partial = True
                    break
                uart.append(raw[cursor])
                positions.append(cursor)
                cursor += 1
            if partial or len(events) >= 3 or len(uart) < boundary:
                continue
            need(bytes(uart) == expected[:boundary], 'exact prompt prefix')
            if prompt_at is None:
                prompt_at = time.monotonic()
            phase = len(events) + 1
            delay = initial_delay if phase == 1 else 2 if initial_delay else 0
            if time.monotonic() - prompt_at < delay:
                continue
            data = bytes.fromhex(workload['command-' + str(phase) + '.sh'])
            need((kit / ('command-' + str(phase) + '.sh')).read_bytes() == data, 'command pin')
            writes = []
            sent = 0
            while sent < len(data):
                requested = data[sent:sent + fragment]
                accepted = child.stdin.write(requested)
                child.stdin.flush()
                need(accepted is not None and 0 < accepted <= len(requested), 'input progress')
                writes.append({'offset': sent, 'requested_hex': requested.hex(), 'accepted': accepted})
                sent += accepted
                if pace:
                    time.sleep(pace)
            events.append({'generation': 1, 'phase': phase, 'prompt_uart_offset': boundary,
                           'prompt_raw_offset': positions[boundary - 1] + 1,
                           'observed_raw_bytes': len(raw), 'writes': writes,
                           'delay_seconds': time.monotonic() - prompt_at})
            boundary += len(bytes.fromhex(exchange['steps'][phase - 1]['expected_uart_after_input_hex'])) + 2
            prompt_at = None
        else:
            record['status'] = 'timeout'
            raise TimeoutError('native deadline')
except BaseException as error:
    record['error'] = repr(error)
    raise
finally:
    if child is not None:
        child.terminate()
        try:
            child.wait(timeout=3)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait(timeout=3)
        record.update(cleanup='emulator-reaped', emulator_exit=child.returncode)
    (P / 'serial.log').write_bytes(raw)
    (P / (case + '.json')).write_text(json.dumps(record, indent=2) + '\n')
if record['status'] == 'pass':
    record['independent_oracle'] = oracle.check(bytes(raw), record, workload)
    (P / (case + '.json')).write_text(json.dumps(record, indent=2) + '\n')
print(case, record['status'])
