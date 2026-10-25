# SPDX-License-Identifier: BSD-2-Clause
"""Qualify explicit large static startup images with pinned native musl inputs."""
import datetime
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

from evidence import compact_run
from deps import ROOT
from memory_probe import build
from memory_smoke import check_budget
from native_smoke import run
from regression import Parser, inputs


def mutate(raw, kind):
    """Mutate a producer-owned ELF, preserving unrelated bytes for each control."""
    data = bytearray(raw)
    if kind == 'pie':
        struct.pack_into('<H', data, 16, 3)
        return bytes(data)
    if kind == 'file-limit':
        return bytes(data) + bytes(8 * 1024 * 1024 + 1 - len(data))
    offset = struct.unpack_from('<Q', data, 32)[0]
    count = struct.unpack_from('<H', data, 56)[0]
    headers = [offset + i * 56 for i in range(count)]
    writable = [h for h in headers if struct.unpack_from('<II', data, h) == (1, 6)]
    if not writable:
        raise RuntimeError('fixture requires writable storage')
    h = max(writable, key=lambda item: struct.unpack_from('<Q', data, item + 40)[0])
    address = struct.unpack_from('<Q', data, h + 16)[0]
    size = struct.unpack_from('<Q', data, h + 40)[0]
    if kind == 'wx':
        struct.pack_into('<I', data, h + 4, 7)
    elif kind == 'quota':
        struct.pack_into('<Q', data, h + 40, 2048 * 4096)
    elif kind in ('stack', 'arena'):
        delta = (0x08000000 if kind == 'stack' else 0x10000000) - (address & ~4095)
        for header in headers:
            view = struct.unpack_from('<Q', data, header + 16)[0]
            if address <= view < address + size:
                struct.pack_into('<Q', data, header + 16, view + delta)
    else:
        raise ValueError('unknown image mutation')
    return bytes(data)


def suite(libc_build, tools_lock):
    out = Path(tempfile.mkdtemp(prefix='native-image-', dir=ROOT / 'zig-out'))
    record = {'status': 'incomplete', 'sources': inputs(), 'cases': [], 'commands': []}
    print('[RUNNING] Evidence:', out, file=sys.stderr, flush=True)
    def save():
        (out / 'results.json').write_text(json.dumps(record, indent=2) + '\n')
    def command(argv, log):
        item = {'argv': argv, 'start_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
        record['commands'].append(item)
        try:
            with log.open('wb') as stream:
                item['exit_code'] = subprocess.run(argv, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, timeout=180).returncode
            if item['exit_code'] != 0:
                raise RuntimeError('command failed: ' + str(log))
        finally:
            item['end_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            save()
    try:
        build(libc_build, tools_lock, out / 'probe', None, large_image=True)
        build(libc_build, tools_lock, out / 'stop-probe', 'STOP_LIVE', large_image=True)
        raw = (out / 'probe/native-c.bin').read_bytes()
        if len(raw) <= 1024 * 1024 + 40:
            raise RuntimeError('fixture did not exceed old file limit')
        images = {'positive': out / 'probe/native-c.bin'}
        for kind in ('pie', 'wx', 'quota', 'stack', 'arena', 'file-limit'):
            path = out / (kind + '.bin')
            path.write_bytes(raw[:40] + mutate(raw[40:], kind))
            images[kind] = path
        supervisor = out / 'supervisor.raw'
        command(['rustc', '+1.98.0', '--edition=2024', '--target=x86_64-unknown-none', '-C', 'opt-level=2', '-C', 'panic=abort', '-C', 'relocation-model=static', '-C', 'link-arg=-Tuser/protection/linker.ld', '-C', 'link-arg=--oformat=binary', '--cfg', 'stop_live', 'user/native-memory/supervisor.rs', '-o', str(supervisor)], out / 'supervisor.log')
        code = supervisor.read_bytes()
        if not 0 < len(code) <= 4096:
            raise RuntimeError('supervisor size')
        stop = (out / 'stop-probe/native-c.bin').read_bytes()
        images['replacement'] = out / 'replacement.bin'
        images['replacement'].write_bytes(struct.pack('<8sII', b'AENSUP01', len(stop)-40, len(code)) + stop[8:40] + stop[40:] + code)
        cases = [('positive', None), ('replacement', None), ('old-profile', b'native C profile rejected')]
        cases += [(kind, b'invalid native layout' if kind in ('stack', 'arena') else b'invalid native ELF') for kind in ('pie', 'wx', 'quota', 'stack', 'arena', 'file-limit')]
        for name, panic in cases:
            print('[RUNNING]', name, file=sys.stderr, flush=True)
            destination = out / ('run-' + name)
            destination.mkdir()
            envelope = images['positive' if name == 'old-profile' else name]
            case = {'name': name, 'status': 'incomplete', 'expected_panic': panic.decode() if panic else None, 'envelope_sha256': hashlib.sha256(envelope.read_bytes()).hexdigest()}
            record['cases'].append(case)
            argv = ['zig', 'build', '-Dsmp=false', '-Dnative-memory=true', '-Dnative-memory-large=true', '-Dnative-c-image=' + str(envelope), '-p', str(destination), '--cache-dir', str(ROOT / '.zig-cache'), '--global-cache-dir', str(ROOT / '.zig-cache/global')]
            if name != 'old-profile':
                argv.append('-Dnative-image-large=true')
            command(argv, destination / 'build.log')
            case['start_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            run(destination / 'aether.iso', expected_panic=panic, marker=b'AETHER NATIVE SUPERVISION PASS' if name == 'replacement' else b'AETHER NATIVE C PASS')
            serial = (destination / 'native-serial.log').read_text()
            if panic:
                if 'NATIVE MEMORY admitted' in serial:
                    raise RuntimeError('rejected image admitted a worker')
            else:
                check_budget(serial, True)
                if name == 'replacement' and 'NATIVE terminal slot=0 generation=2 kind=1 detail=0\n' not in serial:
                    raise RuntimeError('replacement did not complete')
            case.update(status='pass', end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), iso_sha256=hashlib.sha256((destination / 'aether.iso').read_bytes()).hexdigest(), serial_sha256=hashlib.sha256(serial.encode()).hexdigest())
            save()
        if inputs() != record['sources']:
            raise RuntimeError('sources changed during suite')
        record['status'] = 'pass'
    finally:
        save()
        compact_run(out, record)
    print('[PASS] large static image cases:', len(cases), flush=True)


if __name__ == '__main__':
    parser = Parser(description=__doc__)
    parser.add_argument('--libc-build', required=True)
    parser.add_argument('--tools-lock', required=True)
    parser.add_argument('--version', action='version', version='aether-native-image-smoke 1')
    args = parser.parse_args()
    try:
        suite(args.libc_build, args.tools_lock)
    except (OSError, RuntimeError, ValueError, TimeoutError, subprocess.SubprocessError) as error:
        parser.exit(1, f'[FAIL] {error}\n')
