# SPDX-License-Identifier: BSD-2-Clause
"""Run scoped native-memory conformance with explicit strict-libc inputs."""
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import tempfile

from evidence import compact_run
from deps import ROOT
from regression import Parser
from memory_probe import build
from native_smoke import run


def check_budget(serial, large):
    rows = re.findall(r'^NATIVE MEMORY admitted slot=[0-9]+ generation=[0-9]+ used=([0-9]+) remaining=([0-9]+)$', serial, re.MULTILINE)
    quota = 2048 if large else 128
    if not rows or any(int(used) == 0 or int(used) + int(free) != quota for used, free in rows):
        raise RuntimeError('admission budget differs from selected profile')


def check_fp_rejection(serial):
    terminals = re.findall(r'^NATIVE terminal slot=([01]) generation=0 kind=1 detail=([0-9]+)$', serial, re.MULTILINE)
    summaries = re.findall(r'^NATIVE terminal task=([01]) status=([0-9]+) output=([0-9]+) fs=([0-9a-f]+) ticks=[0-9]+$', serial, re.MULTILINE)
    if len(terminals) != 2 or {slot for slot, _ in terminals} != {'0', '1'}:
        raise RuntimeError('missing FP rejection terminals')
    statuses = {slot: int(status) for slot, status in terminals}
    if 174 not in statuses.values() or any(status not in (0, 174) for status in statuses.values()):
        raise RuntimeError('wrong FP rejection reason')
    if len(summaries) != 2 or {row[0] for row in summaries} != {'0', '1'}:
        raise RuntimeError('missing FP rejection summaries')
    for slot, status, output, fs in summaries:
        if int(status) != statuses[slot] or int(output) != (24 if int(status) == 0 else 0) or int(fs, 16) == 0:
            raise RuntimeError('inconsistent FP rejection summary')


def suite(libc_build, tools_lock, large=False):
    out = Path(tempfile.mkdtemp(prefix='memory-suite-', dir=ROOT / 'zig-out'))
    record = {'format': 'aether-native-memory-evidence-v1', 'status': 'incomplete', 'cases': [], 'large': large}
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    record['sources'] = {str(p.relative_to(ROOT)): sha(p) for parent in ('kernel', 'user/native-memory', 'scripts')
                         for p in (ROOT / parent).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    record['sources']['build.zig'] = sha(ROOT / 'build.zig')
    print('[RUNNING] Evidence:', out, flush=True)
    try:
        images = {}
        for label, fault in [('positive', None), ('read', 'FAULT_READ'), ('write', 'FAULT_WRITE'),
                             ('unmap', 'FAULT_UNMAP'), ('metadata', 'METADATA_DENIAL'), ('stop', 'STOP_LIVE')]:
            build(libc_build, tools_lock, out / label, fault, large)
            images[label] = out / label / 'native-c.bin'
        if large:
            build(libc_build, tools_lock, out / 'bad-boundary', 'BAD_BOUNDARY', True)
            images['bad-boundary'] = out / 'bad-boundary/native-c.bin'
        record['supervisor_commands'] = []
        for label, configs, worker in [('supervised', [], 'positive'),
                                        ('stop-live', ['stop_live'], 'stop'),
                                        ('bad-stop', ['stop_live', 'bad_stop'], 'stop')]:
            supervisor = out / (label + '.raw')
            command = ['rustc', '+1.98.0', '--edition=2024', '--target=x86_64-unknown-none',
                       '-C', 'opt-level=2', '-C', 'panic=abort', '-C', 'relocation-model=static',
                       '-C', 'link-arg=-Tuser/protection/linker.ld', '-C', 'link-arg=--oformat=binary',
                       'user/native-memory/supervisor.rs', '-o', str(supervisor)]
            for config in configs: command += ['--cfg', config]
            subprocess.run(command, cwd=ROOT, check=True, timeout=120)
            code = supervisor.read_bytes()
            if not 0 < len(code) <= 4096: raise RuntimeError('supervisor size')
            raw = images[worker].read_bytes()
            images[label] = out / (label + '.bin')
            images[label].write_bytes(struct.pack('<8sII', b'AENSUP01', len(raw)-40, len(code)) + raw[8:40] + raw[40:] + code)
            record['supervisor_commands'].append(command)
        cases = [('positive', 'positive', None, None),
                 ('read', 'read', None, 142), ('write', 'write', None, 142), ('unmap', 'unmap', None, 142),
                 ('no-grant', 'positive', 'native-memory-no-grant', 61),
                 ('skip-protect', 'positive', 'native-memory-skip-protect', 78),
                 ('skip-zero', 'positive', 'native-memory-skip-zero', -1),
                 ('skip-fp', 'positive', 'native-skip-fp', 174),
                 ('metadata-retry', 'metadata', 'native-memory-deny-protect-once', None),
                 ('supervised', 'supervised', None, None),
                 ('stop-live', 'stop-live', None, None), ('bad-stop', 'bad-stop', None, 304)]
        if large:
            cases = [(label, image, flag, 123 if label == 'skip-protect' else failure)
                     for label, image, flag, failure in cases]
            cases.append(('bad-boundary', 'bad-boundary', None, 129))
        for label, image_key, flag, failure in cases:
            destination = out / ('run-' + label); destination.mkdir()
            command = ['zig', 'build', '-Dsmp=false', '-Dnative-memory=true',
                       '-Dnative-c-image=' + str(images[image_key]), '-p', str(destination),
                       '--cache-dir', str(ROOT / '.zig-cache'), '--global-cache-dir', str(ROOT / '.zig-cache/global')]
            if large: command += ['-Dnative-memory-large=true']
            if flag: command += ['-D' + flag + '=true']
            case = {'name': label, 'status': 'incomplete', 'command': command,
                    'envelope_sha256': sha(images[image_key])}
            record['cases'].append(case)
            print('[RUNNING]', label, flush=True)
            with (destination / 'build.log').open('wb') as log:
                subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=180)
            panic = None if failure is None else b'native runtime backing not zeroed' if failure == -1 else b'native C profile rejected'
            context = ()
            if failure is not None and failure != -1:
                kind = 2 if failure == 142 else 1
                context = (f'NATIVE terminal slot=0 generation=0 kind={kind} detail={failure}'.encode(),)
                # Wait for both tasks to terminate; the retained log must also
                # establish peer completion after the hardware fault below.
            if label == 'skip-fp':
                context = ()
            if label == 'bad-stop':
                context = (b'NATIVE supervisor result=304 reclaimed=0',)
            run(destination / 'aether.iso', expected_panic=panic, panic_context=context,
                marker=b'AETHER NATIVE SUPERVISION PASS' if label in ('supervised', 'stop-live', 'bad-stop') else b'AETHER NATIVE C PASS')
            serial = (destination / 'native-serial.log').read_text()
            check_budget(serial, large)
            if label == 'skip-fp':
                check_fp_rejection(serial)
            if failure == 142:
                error = 7 if label == 'write' else 4
                if not re.search(r'NATIVE fault vector=14 rip=[0-9a-f]+ error=' + str(error) + r'\n', serial):
                    raise RuntimeError('wrong hardware fault')
                if not re.search(r'NATIVE terminal task=1 status=0 output=24 fs=[0-9a-f]+ ticks=[0-9]+\n', serial):
                    raise RuntimeError('peer did not complete after fault')
            if label in ('supervised', 'stop-live') and 'NATIVE terminal slot=0 generation=2 kind=1 detail=0\n' not in serial:
                raise RuntimeError('missing replacement completion')
            if label == 'stop-live':
                occupancy = re.findall(r'NATIVE MEMORY admitted slot=0 generation=([12]) used=([0-9]+) remaining=([0-9]+)\n', serial)
                if len(occupancy) != 2 or occupancy[0][0] != '1' or occupancy[1][0] != '2' or occupancy[0][1:] != occupancy[1][1:]:
                    raise RuntimeError('replacement quota differs from original admission')
                if 'NATIVE terminal slot=1 generation=1 kind=1 detail=0\n' not in serial:
                    raise RuntimeError('peer did not finish during stop/replacement')
            case.update(status='pass', iso_sha256=sha(destination / 'aether.iso'),
                        serial_sha256=sha(destination / 'native-serial.log'), expected_panic=panic.decode() if panic else None)
        for name, digest in record['sources'].items():
            if sha(ROOT / name) != digest: raise RuntimeError('sources changed during suite')
        record['status'] = 'pass'
    finally:
        (out / 'results.json').write_text(json.dumps(record, indent=2) + '\n')
        compact_run(out, record)
    print(f'[PASS] {len(cases)} memory cases:', out)


if __name__ == '__main__':
    parser = Parser(description=__doc__)
    parser.add_argument('--large', action='store_true', help='Run opt-in 8 MiB backing profile')
    parser.add_argument('--libc-build', required=True)
    parser.add_argument('--tools-lock', required=True)
    parser.add_argument('--version', action='version', version='aether-memory-smoke 1')
    args = parser.parse_args()
    try:
        suite(args.libc_build, args.tools_lock, args.large)
    except (OSError, RuntimeError, TimeoutError, subprocess.SubprocessError) as error:
        parser.exit(1, f'[FAIL] {error}\n')
