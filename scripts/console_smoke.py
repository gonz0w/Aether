# SPDX-License-Identifier: BSD-2-Clause
"""Build and exercise the native serial grant using an explicitly pinned musl SDK."""
import hashlib
import json
import os
import re
from pathlib import Path
import select
import shutil
import struct
import subprocess
import tempfile
import time
from datetime import datetime, timezone

from evidence import compact_run
from deps import ROOT, DEPS, LOCK, verify
from regression import Parser


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inputs():
    paths = [ROOT / 'build.zig']
    for name in ('kernel', 'user', 'scripts', 'tests', 'boot'):
        paths.extend(p for p in (ROOT / name).rglob('*')
                     if p.is_file() and '__pycache__' not in p.parts)
    return {str(p.relative_to(ROOT)): sha(p) for p in paths}


def suite(libc_build, tools_lock, handoff=False, handoff_fault=False, relay=False, connections=False):
    relay = relay or connections
    sdk = Path(libc_build).resolve()
    lock = Path(tools_lock).resolve()
    out = Path(tempfile.mkdtemp(prefix='console-', dir=ROOT / 'zig-out'))
    report = {'status': 'incomplete', 'start_utc': datetime.now(timezone.utc).isoformat(),
              'connections': connections, 'relay': relay, 'handoff': handoff, 'handoff_fault': handoff_fault,
              'sources': inputs(), 'commands': [], 'cases': [], 'scope': 'BSP UART transport only'}
    print('[RUNNING] Evidence:', out, flush=True)

    def command(args, label):
        entry = {'argv': [str(a) for a in args], 'start_utc': datetime.now(timezone.utc).isoformat()}
        report['commands'].append(entry)
        with (out / (label + '.log')).open('wb') as log:
            result = subprocess.run(entry['argv'], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, timeout=180)
        entry.update(exit_code=result.returncode, end_utc=datetime.now(timezone.utc).isoformat())
        if result.returncode:
            raise RuntimeError('command failed: ' + label)

    try:
        verify()
        receipt = json.loads((sdk / 'evidence.json').read_text())
        tools = json.loads(lock.read_text())['tools']
        lib = sdk / 'stage/usr/lib'
        if sha(lib / 'libc.a') != receipt['libc_archive_sha256'] or not receipt.get('libc_patches'):
            raise RuntimeError('strict SDK receipt mismatch')
        for name in ('clang', 'lld'):
            if sha(Path(tools[name]['path']).resolve()) != tools[name]['sha256']:
                raise RuntimeError('tool pin mismatch: ' + name)
        report['sdk'] = {'receipt': sha(sdk / 'evidence.json'), 'libc': sha(lib / 'libc.a'), 'tools_lock': sha(lock)}
        if subprocess.check_output(['qemu-system-x86_64', '--version'], text=True).splitlines()[0] != 'QEMU emulator version ' + LOCK['qemu']:
            raise RuntimeError('QEMU version mismatch')
        cc = [tools['clang']['path'], '--no-default-config', '--target=x86_64-linux-musl', '--sysroot=' + str(sdk / 'empty-root')]
        for name, source in [('worker', 'user/native-console/relay.c' if relay else 'user/native-console/recipient.c' if handoff else 'user/native-console/worker.c'), ('adapter', 'user/native-memory/adapter.c')]:
            command(cc + ['-std=c11', '-D_GNU_SOURCE', '-O2', '-Wall', '-Wextra', '-Werror',
                          '-ffreestanding', '-fno-builtin', '-fstack-protector-strong', '-nostdinc',
                          '-isystem', str(sdk / 'stage/usr/include')] + (['-DHANDOFF_FAULT'] if handoff_fault else []) + (['-DCONNECTIONS_CONSOLE'] if connections else []) + ['-c', source, '-o', out / (name + '.o')], name)
        command(cc + ['-fuse-ld=' + tools['lld']['path'], '-nostdlib', '-static', '-Wl,-z,noexecstack', '-Wl,--no-undefined',
                      lib / 'crt1.o', lib / 'crti.o', out / 'worker.o', out / 'adapter.o', lib / 'libc.a', lib / 'crtn.o',
                      '-o', out / 'worker.elf'], 'link')
        command(['rustc', '+1.98.0', '--edition=2024', '--target=x86_64-unknown-none', '-C', 'opt-level=s', '-C', 'lto=fat', '-C', 'codegen-units=1',
                 '-C', 'panic=abort', '-C', 'relocation-model=static', '-C', 'link-arg=-Tuser/native-launch/linker.ld',
                 '-C', 'link-arg=--oformat=binary', 'user/native-console/relay.rs' if relay else 'user/native-console/handoff.rs' if handoff else 'user/native-console/owner.rs', '-o', out / 'owner.raw'] + (['--cfg', 'handoff_fault'] if handoff_fault else []) + (['--cfg', 'connections_console'] if connections else []), 'owner')
        worker, owner = (out / 'worker.elf').read_bytes(), (out / 'owner.raw').read_bytes()
        if connections:
            owner += bytes(16384 - len(owner))
            envelope = struct.pack('<8sIIIIII', b'AENMX003', len(worker), len(worker), len(worker), len(owner), 0, 0) + os.urandom(48) + worker + worker + worker + owner
        elif relay:
            envelope = struct.pack('<8sIIII', b'AENSC003', len(worker), len(worker), len(owner), 0) + os.urandom(32) + worker + worker + owner
        else:
            envelope = struct.pack('<8sII', b'AENSC002' if handoff else b'AENSC001', len(worker), len(owner)) + os.urandom(32) + worker + owner
        (out / 'console.bin').write_bytes(envelope)
        command(['zig', 'build', '-Dsmp=false', '-Dnative-c-image=' + str(out / 'console.bin'),
                 '--cache-dir', '.zig-cache', '--global-cache-dir', '.zig-cache/global', '--prefix', out / 'image'], 'build')
        image = out / 'image/aether.iso'
        if not image.is_file():
            image = out / 'image/boot/aether.iso'
        for label, payload, expected in [('positive', b'a\0\x1b\rZ9\n!', b'AETHER NATIVE CONSOLE PASS'),
                                          ('wrong-input', b'b\0\x1b\rZ9\n!', b'NATIVE supervisor result=941 reclaimed=0' if relay else b'NATIVE supervisor result=941 reclaimed=1' if handoff else b'NATIVE supervisor result=901 reclaimed=3')]:
            variables = out / (label + '-vars.fd')
            shutil.copyfile(DEPS / 'firmware/vars.fd', variables)
            args = ['qemu-system-x86_64', '-machine', 'pc-q35-11.1', '-accel', 'tcg', '-cpu', 'qemu64', '-smp', '1', '-m', '256M',
                    '-drive', f'if=pflash,format=raw,readonly=on,file={DEPS / "firmware/code.fd"}',
                    '-drive', f'if=pflash,format=raw,file={variables}', '-cdrom', str(image), '-boot', 'd',
                    '-nic', 'none', '-vga', 'std', '-display', 'none', '-serial', 'stdio', '-monitor', 'none', '-no-reboot', '-no-shutdown']
            case = {'name': label, 'argv': args, 'start_utc': datetime.now(timezone.utc).isoformat(), 'status': 'incomplete'}
            report['cases'].append(case)
            data = bytearray()
            sent = False
            with (out / (label + '-qemu.log')).open('wb') as log:
                process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=log)
                try:
                    deadline = time.monotonic() + 30
                    while time.monotonic() < deadline:
                        if select.select([process.stdout], [], [], 0.1)[0]:
                            chunk = os.read(process.stdout.fileno(), 4096)
                            if not chunk:
                                raise RuntimeError('QEMU exited before acceptance')
                            data.extend(chunk)
                        if not sent and b'CONSOLE READY\n' in data:
                            process.stdin.write(payload)
                            process.stdin.flush()
                            sent = True
                        if expected in data and (label == 'positive' or b'native C profile rejected' in data):
                            break
                        if b'AETHER PANIC: ' in data and b'\n' in data.split(b'AETHER PANIC: ', 1)[1] and label == 'positive':
                            raise RuntimeError('unexpected kernel panic')
                    else:
                        raise TimeoutError('console acceptance deadline: ' + label)
                    if label == 'positive' and handoff_fault and b'NATIVE terminal slot=0 generation=2 kind=2 detail=134\n' not in data:
                        raise RuntimeError('recipient fault evidence missing')
                    if not sent:
                        raise RuntimeError('no real input exchange')
                    if label == 'positive' and b'CONSOLE ECHO:' + payload + b'\n0123456789abcdefghijklmnopqrstuv\n' not in data:
                        raise RuntimeError('serial output mismatch')
                    if label != 'positive' and b'AETHER NATIVE CONSOLE PASS' in data:
                        raise RuntimeError('wrong input was accepted')
                    if connections:
                        terminals = [line for line in data.splitlines() if line.startswith(b'NATIVE terminal')]
                        if label == 'positive':
                            wanted = [f'NATIVE terminal slot={slot} generation={gen} kind=1 detail=0'.encode() for slot, gen in [(0, 1), (1, 1), (0, 2), (1, 2), (2, 1), (0, 3)]]
                            if sorted(terminals) != sorted(wanted) or b'NATIVE supervisor result=100 reclaimed=6' not in data:
                                raise RuntimeError('console/process lifecycle mismatch')
                        elif b'NATIVE terminal slot=1 generation=1 kind=1 detail=74' not in data:
                            raise RuntimeError('wrong input lacks peer rejection')
                    case['status'] = 'pass'
                finally:
                    (out / (label + '-serial.log')).write_bytes(data)
                    if process.poll() is None:
                        process.terminate()
                        try:
                            process.wait(timeout=3)
                        except subprocess.TimeoutExpired:
                            process.kill()
                            process.wait(timeout=3)
                            raise RuntimeError('QEMU required forced teardown')
                    process.stdin.close()
                    process.stdout.close()
                    case['end_utc'] = datetime.now(timezone.utc).isoformat()
        if inputs() != report['sources']:
            raise RuntimeError('source drift during console qualification')
        report['status'] = 'pass'
    except BaseException as error:
        report['error'] = str(error)
        raise
    finally:
        report['end_utc'] = datetime.now(timezone.utc).isoformat()
        report['artifacts'] = {str(p.relative_to(out)): sha(p) for p in out.rglob('*') if p.is_file()}
        (out / 'results.json').write_text(json.dumps(report, indent=2) + '\n')
        compact_run(out, report)
    print('[PASS] Real serial exchange, grant denial and close:', out)


def run_dash_console(image, wrong=False, legacy=False, resume=False, old_cleanup=False, wrong_exit=False, repeat=False, repeat_failure=None, redirect=False):
    """Private dash exchange; fixed ASCII witnesses, not a terminal emulator."""
    out = image.parent
    variables = out / 'dash-vars.fd'
    shutil.copyfile(DEPS / 'firmware/vars.fd', variables)
    args = ['qemu-system-x86_64', '-machine', 'pc-q35-11.1', '-accel', 'tcg', '-cpu', 'qemu64', '-smp', '1', '-m', '256M',
            '-drive', f'if=pflash,format=raw,readonly=on,file={DEPS / "firmware/code.fd"}',
            '-drive', f'if=pflash,format=raw,file={variables}', '-cdrom', str(image), '-boot', 'd',
            '-nic', 'none', '-vga', 'std', '-display', 'none', '-serial', 'stdio', '-monitor', 'none', '-no-reboot', '-no-shutdown']
    report = {'argv': args, 'start_utc': datetime.now(timezone.utc).isoformat(), 'events': [], 'status': 'incomplete'}
    data = bytearray()
    commands = children = continuations = 0
    with (out / 'dash-qemu.log').open('wb') as log:
        process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=log)
        try:
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                if select.select([process.stdout], [], [], 0.05)[0]:
                    chunk = os.read(process.stdout.fileno(), 4096)
                    if not chunk: raise RuntimeError('dash QEMU ended before acceptance')
                    data.extend(chunk)
                if data.count(b'SHELL READY\n') > commands:
                    payload = b'echo redirected >&2; /next\n' if redirect else b'/next\n' if resume or repeat else b'/next; exit $?\n'
                    process.stdin.write(payload); process.stdin.flush()
                    commands += 1
                    report['events'].append({'kind': 'command', 'bytes_hex': payload.hex(), 'session': commands})
                if data.count(b'CHILD READY\n') > children:
                    payload = b'b' if wrong else b'a'
                    process.stdin.write(payload); process.stdin.flush()
                    children += 1
                    report['events'].append({'kind': 'child-input', 'bytes_hex': payload.hex(), 'session': 1 if repeat else children, **({'child': children} if repeat else {})})
                if repeat and data.count(b'$ ') >= commands + 1 and continuations == 0:
                    terminal = f'NATIVE terminal slot=2 generation={commands} kind=1 detail=72'.encode()
                    if terminal not in data or children != commands:
                        raise RuntimeError('repeat prompt before child terminal/input')
                    payload = b'echo restored; /next\n' if redirect and commands == 1 else b'/next\n' if commands < 3 else b'echo $?;exit 0\n'
                    process.stdin.write(payload); process.stdin.flush()
                    if commands < 3:
                        commands += 1
                        report['events'].append({'kind': 'command', 'bytes_hex': payload.hex(), 'session': 1, 'child': commands})
                    else:
                        continuations += 1
                        report['events'].append({'kind': 'continuation', 'bytes_hex': payload.hex(), 'session': 1})
                if resume and data.count(b'$ ') >= 2 * (continuations + 1):
                    generation = continuations + 1
                    terminal = f'NATIVE terminal slot=2 generation={generation} kind=1 detail=72'.encode()
                    if terminal not in data or children != generation:
                        raise RuntimeError('shell resumed before child terminal/input')
                    code = 0 if generation == 1 else 8 if wrong_exit else 7
                    payload = f'echo $?;exit {code}\n'.encode()
                    process.stdin.write(payload); process.stdin.flush()
                    continuations += 1
                    report['events'].append({'kind': 'continuation', 'bytes_hex': payload.hex(), 'session': generation})
                if b'AETHER NATIVE CONSOLE PASS' in data:
                    if wrong or legacy or old_cleanup or wrong_exit or repeat_failure or commands != (3 if repeat else 2) or children != (3 if repeat else 2):
                        raise RuntimeError('dash console exchange count or wrong-input acceptance')
                    if repeat and (continuations != 1 or data.count(b'SHELL READY\n') != 1 or data.count(b'$ ') != 4 or data.count(b'$ 72\n') != 1):
                        raise RuntimeError('missing repeated shell status or prompt')
                    if redirect and (data.count(b'redirected\n') != 1 or data.count(b'restored\n') != 1):
                        raise RuntimeError('missing redirected/restored builtin output')
                    if resume and (continuations != 2 or data.count(b'$ ') != 4 or data.count(b'$ 72\n') != 2):
                        raise RuntimeError('missing resumed shell status or prompt')
                    break
                if b'AETHER PANIC: native C profile rejected\n' in data:
                    if repeat_failure in ('closed', 'closed-exec'):
                        owner = 2150 if repeat_failure == 'closed' else 2120
                        if commands != 1 or children != 0 or continuations != 0 or data.count(b'redirected\n') != 1 or b'NATIVE terminal slot=2' in data or f'NATIVE supervisor result={owner} reclaimed=0'.encode() not in data:
                            raise RuntimeError('missing closed-descriptor snapshot rejection')
                        break
                    if repeat_failure:
                        owner = 2151 if repeat_failure == 'token' else 1950
                        if commands != 2 or children != 1 or continuations != 0 or f'NATIVE supervisor result={owner} reclaimed=1'.encode() not in data:
                            raise RuntimeError('missing repeated-child rejection')
                        if repeat_failure == 'boot' and b'NATIVE terminal slot=2 generation=2 kind=1 detail=224' not in data:
                            raise RuntimeError('missing stale bootstrap rejection')
                        break
                    if old_cleanup or wrong_exit:
                        generation, status, owner, reclaims = (1, 0, 2131, 0) if old_cleanup else (2, 8, 2130, 2)
                        if commands != generation or children != generation or continuations != generation or f'NATIVE terminal slot=0 generation={generation} kind=1 detail={status}'.encode() not in data or f'NATIVE supervisor result={owner} reclaimed={reclaims}'.encode() not in data:
                            raise RuntimeError('missing resumed shell rejection')
                        break
                    if legacy:
                        if commands != 1 or children != 0 or b'sh: 0: Pipe call failed' not in data or b'NATIVE supervisor result=2140 reclaimed=0' not in data:
                            raise RuntimeError('missing legacy tee rejection')
                        break
                    if not wrong or commands != 1 or children != 1 or b'NATIVE terminal slot=2 generation=1 kind=1 detail=224' not in data or b'NATIVE supervisor result=2130 reclaimed=0' not in data:
                        raise RuntimeError('unexpected dash console rejection')
                    break
            else:
                raise TimeoutError('dash console exchange deadline')
            report['status'] = 'pass'
        finally:
            (out / 'native-serial.log').write_bytes(data)
            if process.poll() is None:
                process.terminate()
                try: process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill(); process.wait(timeout=3)
                    report['forced_teardown'] = True
            process.stdin.close(); process.stdout.close()
            report['end_utc'] = datetime.now(timezone.utc).isoformat()
            (out / 'dash-exchange.json').write_text(json.dumps(report, indent=2) + '\n')
    if report.get('forced_teardown'): raise RuntimeError('dash QEMU required forced teardown')
    print('PASS: actual dash serial exchange' + (' wrong-input rejection' if wrong else ''))


def run_pipe_console(image, wrong=False, stale_token=False, external=False, exec_rejection=None):
    """Two prompt-driven substitutions; existing serial exec driver stays separate."""
    out = image.parent
    variables = out / 'dash-vars.fd'
    shutil.copyfile(DEPS / 'firmware/vars.fd', variables)
    args = ['qemu-system-x86_64', '-machine', 'pc-q35-11.1', '-accel', 'tcg', '-cpu', 'qemu64', '-smp', '1', '-m', '256M',
            '-drive', f'if=pflash,format=raw,readonly=on,file={DEPS / "firmware/code.fd"}',
            '-drive', f'if=pflash,format=raw,file={variables}', '-cdrom', str(image), '-boot', 'd',
            '-nic', 'none', '-vga', 'std', '-display', 'none', '-serial', 'stdio', '-monitor', 'none', '-no-reboot', '-no-shutdown']
    payloads = [b'a=$(echo pipe); echo "$a"\n', b'b=$(echo pipe); echo "$b"\n', b'exit 0\n', b'echo clean; exit 0\n']
    if external:
        payloads = [payload.replace(b'echo pipe', b'/next') for payload in payloads]
    if wrong:
        payloads[0] = payloads[0].replace(b'pipe', b'nope')
    report = {'argv': args, 'start_utc': datetime.now(timezone.utc).isoformat(), 'events': [], 'status': 'incomplete'}
    data = bytearray()
    sent = 0
    ready_at = None
    with (out / 'dash-qemu.log').open('wb') as log:
        process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=log)
        try:
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                if select.select([process.stdout], [], [], 0.02)[0]:
                    chunk = os.read(process.stdout.fileno(), 4096)
                    if not chunk:
                        raise RuntimeError('pipe console ended before acceptance')
                    data.extend(chunk)
                if sent < 4 and data.count(b'$ ') == sent + 1 and data.count(b'SHELL READY\n') == (2 if sent == 3 else 1):
                    if ready_at is None:
                        ready_at = time.monotonic()
                    if time.monotonic() - ready_at >= 0.1:
                        if sent in (1, 2) and f'NATIVE terminal slot=2 generation={sent} kind=1 detail=0'.encode() not in data:
                            raise RuntimeError('substitution prompt before child terminal')
                        if sent == 3 and b'NATIVE terminal slot=0 generation=1 kind=1 detail=0' not in data:
                            raise RuntimeError('replacement prompt before prior shell terminal')
                        payload = payloads[sent]
                        process.stdin.write(payload); process.stdin.flush()
                        report['events'].append({'kind': 'command', 'step': sent + 1, 'bytes_hex': payload.hex(), 'prompt_count': data.count(b'$ ')})
                        sent += 1
                        ready_at = None
                if b'AETHER NATIVE CONSOLE PASS\n' in data:
                    if wrong or stale_token or exec_rejection or sent != 4 or data.count(b'$ ') != 4 or data.count(b'SHELL READY\n') != 2 or data.count(b'pipe\n') != 2 or data.count(b'clean\n') != 1:
                        raise RuntimeError('serial substitution output or exchange mismatch')
                    expected = [f'NATIVE terminal slot={slot} generation={gen} kind=1 detail={17 if slot == 1 else 0}'.encode() for slot, gen in [(2,1),(2,2),(0,1),(0,2),(1,1),(1,2)]]
                    if re.findall(rb'NATIVE terminal slot=\d+ generation=\d+ kind=\d+ detail=\d+', data) != expected or b'NATIVE supervisor result=100 reclaimed=6' not in data:
                        raise RuntimeError('serial substitution lifetime mismatch')
                    break
                if b'AETHER PANIC:' in data and b'\n' in data[data.index(b'AETHER PANIC:'):]:
                    expected = b'NATIVE supervisor result=2182 reclaimed=0' if wrong else b'NATIVE supervisor result=2179 reclaimed=1'
                    if exec_rejection:
                        expected = f'NATIVE supervisor result={2184 if exec_rejection == "stale" else 2176} reclaimed=1'.encode()
                    if not (wrong or stale_token or exec_rejection) or expected not in data or b'AETHER PANIC: native C profile rejected\n' not in data or sent != (1 if wrong else 2):
                        raise RuntimeError('unexpected serial substitution rejection')
                    terminals = re.findall(rb'NATIVE terminal slot=\d+ generation=\d+ kind=\d+ detail=\d+', data)
                    expected_terminals = [] if wrong else [b'NATIVE terminal slot=2 generation=1 kind=1 detail=0']
                    if exec_rejection == 'grant':
                        expected_terminals.append(b'NATIVE terminal slot=2 generation=2 kind=1 detail=227')
                    if exec_rejection and (data.count(b'pipe\n') != 1 or data.count(b'SHELL READY\n') != 1 or data.count(b'$ ') != 2):
                        raise RuntimeError('external substitution rejection output mismatch')
                    if terminals != expected_terminals:
                        raise RuntimeError('wrong rejection terminal history')
                    break
            else:
                raise TimeoutError('serial substitution deadline')
            report['status'] = 'pass'
        finally:
            (out / 'native-serial.log').write_bytes(data)
            if process.poll() is None:
                process.terminate()
                try: process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill(); process.wait(timeout=3)
                    report['forced_teardown'] = True
            process.stdin.close(); process.stdout.close()
            report['end_utc'] = datetime.now(timezone.utc).isoformat()
            (out / 'dash-exchange.json').write_text(json.dumps(report, indent=2) + '\n')
    if report.get('forced_teardown'):
        raise RuntimeError('pipe console required forced teardown')
    print('PASS: actual dash serial substitution' + (' rejection control' if wrong or stale_token else ''))


if __name__ == '__main__':
    parser = Parser(description=__doc__)
    parser.add_argument('--libc-build', required=True)
    parser.add_argument('--tools-lock', required=True)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--relay', action='store_true')
    mode.add_argument('--connections', action='store_true')
    mode.add_argument('--handoff', action='store_true')
    mode.add_argument('--handoff-fault', action='store_true')
    parser.add_argument('--version', action='version', version='aether-console-smoke 1')
    args = parser.parse_args()
    try:
        suite(args.libc_build, args.tools_lock, args.handoff or args.handoff_fault, args.handoff_fault, args.relay, args.connections)
    except (OSError, RuntimeError, TimeoutError, subprocess.SubprocessError) as error:
        parser.exit(1, f'[FAIL] {error}\n')


_PIPELINE_BEFORE = b"0123456789" * 8
_PIPELINE_DIAGNOSTIC = b"stderr-0123456789" * 4
_PIPELINE_AFTER = b"after-" + b"9876543210" * 8


def check_pipeline_console(data):
    """Host-only workload oracle; the serial owner enforces authority and lifetime."""
    if b'AETHER PANIC:' in data:
        raise RuntimeError('pipeline unexpected panic')
    if data.count(b'AETHER NATIVE CONSOLE PASS\n') != 1:
        raise RuntimeError('pipeline completion marker missing')
    if data.count(b'$ ') != 9:
        raise RuntimeError('pipeline command/prompt mismatch')
    if data.count(b'NATIVE supervisor result=100 reclaimed=15\n') != 1:
        raise RuntimeError('pipeline cleanup mismatch')
    terminals = re.findall(rb'NATIVE terminal slot=\d+ generation=\d+ kind=\d+ detail=\d+', data)
    expected = [f'NATIVE terminal slot={slot} generation={gen} kind=1 detail=0'.encode()
                for gen in (1, 2, 3) for slot in range(5)]
    if sorted(terminals) != sorted(expected):
        raise RuntimeError('pipeline terminal history mismatch')
    body = bytes(data[data.index(b'$ '):])
    body = re.sub(rb'NATIVE (?:MEMORY admitted slot=\d+ generation=\d+ used=\d+ remaining=\d+|terminal slot=\d+ generation=\d+ kind=\d+ detail=\d+|supervisor result=100 reclaimed=15)\n', b'', body)
    body = body.replace(b'AETHER NATIVE CONSOLE PASS\n', b'')
    expected_body = (b'$ ' + _PIPELINE_BEFORE + b'\n' + _PIPELINE_DIAGNOSTIC +
                     b'\n$ pipe data\n$ ' + _PIPELINE_AFTER + b'\n') * 3
    if body != expected_body:
        raise RuntimeError('pipeline UART output mismatch')


def pipeline_dash_run(image, bad_grant=False):
    """Enter a real parent pipeline and a follow-up at observed serial prompts."""
    out = image.parent
    variables = out / 'dash-vars.fd'
    shutil.copyfile(DEPS / 'firmware/vars.fd', variables)
    args = ['qemu-system-x86_64', '-machine', 'pc-q35-11.1', '-accel', 'tcg', '-cpu', 'qemu64',
            '-smp', '1', '-m', '256M',
            '-drive', f'if=pflash,format=raw,readonly=on,file={DEPS / "firmware/code.fd"}',
            '-drive', f'if=pflash,format=raw,file={variables}', '-cdrom', str(image), '-boot', 'd',
            '-nic', 'none', '-vga', 'std', '-display', 'none', '-serial', 'stdio',
            '-monitor', 'none', '-no-reboot', '-no-shutdown']
    pipeline = b"printf 'pipe data\\n' | /inputs/helper copy | /inputs/helper copy\n"
    before = b"printf '" + _PIPELINE_BEFORE + b"\\n'; printf '" + _PIPELINE_DIAGNOSTIC + b"\\n' >&2\n"
    after = b"printf '" + _PIPELINE_AFTER + b"\\n'; exit 0\n"
    payloads = [before, pipeline, after] * 3
    report = dict(argv=args, start_utc=datetime.now(timezone.utc).isoformat(),
                  events=[], status='incomplete')
    data = bytearray()
    sent = 0
    ready_at = None
    with (out / 'dash-qemu.log').open('wb') as log:
        process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=log)
        try:
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                if select.select([process.stdout], [], [], 0.02)[0]:
                    chunk = os.read(process.stdout.fileno(), 4096)
                    if not chunk:
                        raise RuntimeError('pipeline console ended before acceptance')
                    data.extend(chunk)
                    if len(data) > 1024 * 1024:
                        raise RuntimeError('pipeline serial log budget exceeded')
                if sent < 9 and data.count(b'$ ') == sent + 1:
                    if ready_at is None:
                        ready_at = time.monotonic()
                    if time.monotonic() - ready_at >= 0.1:
                        generation = sent // 3 + 1
                        if sent % 3 == 2:
                            for slot in (2, 3, 4):
                                if f'NATIVE terminal slot={slot} generation={generation} kind=1 detail=0'.encode() not in data:
                                    raise RuntimeError('returned prompt before pipeline child terminal')
                        elif sent % 3 == 0 and generation > 1:
                            if f'NATIVE terminal slot=0 generation={generation-1} kind=1 detail=0'.encode() not in data:
                                raise RuntimeError('fresh prompt before prior parent terminal')
                        process.stdin.write(payloads[sent]); process.stdin.flush()
                        report['events'].append(dict(step=sent+1, bytes_hex=payloads[sent].hex(),
                                                     prompt_count=data.count(b'$ ')))
                        sent += 1
                        ready_at = None
                if b'AETHER NATIVE CONSOLE PASS\n' in data:
                    if bad_grant or sent != 9:
                        raise RuntimeError('pipeline command/prompt mismatch')
                    check_pipeline_console(data)
                    break
                if b'AETHER PANIC:' in data and b'\n' in data[data.index(b'AETHER PANIC:'):]:
                    if not bad_grant or b'NATIVE supervisor result=2795 reclaimed=0\n' not in data:
                        raise RuntimeError('unexpected pipeline rejection')
                    if b'AETHER PANIC: native C profile rejected\n' not in data or sent != 0:
                        raise RuntimeError('incorrect pipeline rejection context')
                    break
            else:
                raise TimeoutError('pipeline console deadline')
            report['status'] = 'pass'
        except RuntimeError as error:
            report.update(status='rejected', reason=str(error))
            raise
        finally:
            (out / 'native-serial.log').write_bytes(data)
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill(); process.wait(timeout=3)
                    report['forced_teardown'] = True
            process.stdin.close(); process.stdout.close()
            report['end_utc'] = datetime.now(timezone.utc).isoformat()
            (out / 'dash-exchange.json').write_text(json.dumps(report, indent=2) + '\n')
    if report.get('forced_teardown'):
        raise RuntimeError('pipeline console required forced teardown')
    print('PASS: interactive parent pipeline' + (' rejection control' if bad_grant else ''))
