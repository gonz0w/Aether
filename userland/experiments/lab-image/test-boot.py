# SPDX-License-Identifier: BSD-2-Clause
"""Host admission and semantic oracle controls for the ABI24 boot command."""
import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

import boot
import serial_oracle


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--kit', required=True, type=Path)
    parser.add_argument('--kit-seal', required=True)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    receipt, workload, process = boot.verify(args.kit, args.kit_seal)
    boot.need(not args.output.exists(), 'new test output')
    boot.need(args.output.resolve().is_relative_to(boot.ROOT / 'build'),
              'test output under build')
    args.output.mkdir(parents=True)
    report = {'status': 'incomplete', 'python': sys.version, 'admission': [],
              'cli': [], 'oracle': [], 'source': {}}
    for name in ['boot.py', 'boot-driver.py', 'serial_oracle.py', 'test-boot.py']:
        path = boot.HERE / name
        ast.parse(path.read_text(), filename=str(path))
        report['source'][name] = boot.sha(path)
    fixture = args.output / 'kit'
    shutil.copytree(args.kit, fixture)
    original = {str(f.relative_to(fixture)): f.read_bytes()
                for f in fixture.rglob('*') if f.is_file()}

    def reseal():
        (fixture / 'SHA256SUMS').write_text(''.join(
            boot.sha(fixture / name) + '  ' + name + '\n'
            for name in sorted(original) if name != 'SHA256SUMS'))
        return boot.sha(fixture / 'SHA256SUMS')

    def reject(label, change, resealed=False):
        try:
            change()
            selected = (boot.sha(fixture / 'SHA256SUMS') if resealed == 'manifest'
                        else reseal() if resealed else args.kit_seal)
            try:
                boot.verify(fixture, selected)
            except (ValueError, FileNotFoundError, KeyError) as error:
                report['admission'].append({'case': label, 'error': str(error)})
            else:
                raise ValueError('admitted invalid kit: ' + label)
        finally:
            for path in fixture.rglob('*'):
                if path.is_symlink() or (path.is_file()
                                        and str(path.relative_to(fixture)) not in original):
                    path.unlink()
            for path in sorted(fixture.rglob('*'), reverse=True):
                if path.is_dir() and path != fixture / 'licenses':
                    path.rmdir()
            for name, data in original.items():
                (fixture / name).write_bytes(data)

    reject('tampered-iso', lambda: (fixture / 'aether.iso').write_bytes(b'wrong'))
    reject('missing-firmware', lambda: (fixture / 'vars.fd').unlink())
    reject('symlink', lambda: ((fixture / 'vars.fd').unlink(),
                              (fixture / 'vars.fd').symlink_to(args.kit.resolve() / 'vars.fd')))
    reject('extra-directory', lambda: (fixture / 'extra').mkdir())
    reject('invalid-receipt-object', lambda: (fixture / 'receipt.json').write_text('[]'), True)
    reject('extra-file', lambda: (fixture / 'unlisted').write_bytes(b'wrong'))
    reject('duplicate', lambda: (fixture / 'SHA256SUMS').write_bytes(
        original['SHA256SUMS'] + original['SHA256SUMS'].splitlines()[0] + b'\n'), 'manifest')
    # Select malformed manifests explicitly to reach namespace validation.
    for label, entry in [('traversal', '../escape'), ('absolute', '/escape')]:
        data = ('0' * 64 + '  ' + entry + '\n').encode()
        (fixture / 'SHA256SUMS').write_bytes(data)
        try:
            boot.verify(fixture, boot.sha(fixture / 'SHA256SUMS'))
        except ValueError as error:
            report['admission'].append({'case': label, 'error': str(error)})
        else:
            raise ValueError('invalid namespace admitted')
        (fixture / 'SHA256SUMS').write_bytes(original['SHA256SUMS'])

    def receipt_change(field, value):
        data = json.loads(original['receipt.json'])
        data[field] = value
        (fixture / 'receipt.json').write_text(json.dumps(data))

    reject('wrong-profile', lambda: receipt_change('profile', 'AENMX008/ABI23'), True)
    reject('failed-build', lambda: receipt_change('status', 'failed'), True)
    reject('unqualified-command', lambda: (fixture / 'command-1.sh').write_bytes(b'exit\n'), True)

    def tool_change():
        data = json.loads(original['receipt.json'])
        data['tools']['qemu-system-x86_64']['sha256'] = '0' * 64
        (fixture / 'receipt.json').write_text(json.dumps(data))

    reject('wrong-tool', tool_change, True)
    boot.verify(fixture, args.kit_seal)
    for label, flags, code, stream in [
        ('help', ['--help'], 0, 'stdout'),
        ('version', ['--version'], 0, 'stdout'),
        ('usage', [], 64, 'stderr'),
        ('invalid-delay', ['--kit', str(args.kit), '--kit-seal', args.kit_seal,
                           '--output', str(args.output / 'never'), '--delay', '1'], 64, 'stderr'),
        ('missing', ['--kit', str(args.output / 'missing'), '--kit-seal', args.kit_seal,
                     '--output', str(args.output / 'never')], 2, 'stderr'),
        ('seal', ['--kit', str(args.kit), '--kit-seal', '0' * 64,
                  '--output', str(args.output / 'never')], 1, 'stderr'),
        ('existing-output', ['--kit', str(args.kit), '--kit-seal', args.kit_seal,
                             '--output', str(args.output)], 1, 'stderr'),
        ('outside-output', ['--kit', str(args.kit), '--kit-seal', args.kit_seal,
                            '--output', '/private/tmp/aether-boot-must-not-create'], 1, 'stderr'),
    ]:
        result = process.run([sys.executable, '-B', str(boot.HERE / 'boot.py'), *flags],
                             cwd=boot.ROOT, env=process.clean_env(args.output),
                             work=args.output, label=label, timeout=15,
                             file_limit=16 * 1024**2)
        boot.need(result.returncode == code and result.record['complete']
                  and result.record['cleanup'] == 'complete', 'CLI exit: ' + label)
        # The receipt field naming is owned by the process helper; inspect files.
        other = args.output / (label + ('.stderr' if stream == 'stdout' else '.stdout'))
        selected = args.output / (label + '.' + stream)
        boot.need(selected.read_bytes() and not other.read_bytes(), 'CLI streams: ' + label)
        report['cli'].append({'case': label, 'process': result.record})
    prior = boot.ROOT / 'docs/evidence/sysinit-read-race-consumer-2026-10-04'
    for name, pin in {
        'fixed-delayed.json': 'e8f63c4ac301ac8107041ac36ba9ca10edc9a3426a90d273bd062524c2033926',
        'fixed-delayed-serial.log': '99dbe1410c3d0ec25201bdc19e52b9daf3f2b039787b11ca4f3796893c9e09f5',
    }.items():
        boot.need(boot.sha(prior / name) == pin, 'retained oracle fixture')
    raw = (prior / 'fixed-delayed-serial.log').read_bytes()
    record = json.loads((prior / 'fixed-delayed.json').read_text())
    report['baseline'] = serial_oracle.check(raw, record, workload)
    for label, data, observed in [
        ('missing-terminal', raw.replace(b'NATIVE terminal slot=0 generation=1 kind=1 detail=0\n', b''), record),
        ('wrong-uart', raw.replace(b'closed ok', b'closed NO'), record),
        ('wrong-reclaim', raw.replace(b'reclaimed=10\n', b'reclaimed=9\n'), record),
        ('missing-input', raw, dict(record, events=record['events'][:-1])),
    ]:
        try:
            serial_oracle.check(data, observed, workload)
        except ValueError as error:
            report['oracle'].append({'case': label, 'error': str(error)})
        else:
            raise ValueError('oracle accepted: ' + label)
    report['status'] = 'pass'
    (args.output / 'tests.json').write_text(json.dumps(report, indent=2) + '\n')
    print('13 kit denials, eight CLI contracts and four oracle mutations pass')


if __name__ == '__main__':
    main()
