# SPDX-License-Identifier: BSD-2-Clause
"""Offline bounded serial-session lab kit builder; Python 3.10+."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import sys
import types

ROOT = Path(__file__).resolve().parents[2]
PROFILE = 'AENMX008/ABI23'
PROFILES = {PROFILE: b'AENMX008', 'AENMX009/ABI24': b'AENMX009'}
VERSION = 'aether-lab-image 0.1.0'
FILES = {'image/aether.iso', 'image/native-c.bin', 'image/aether',
         'image/lifecycle.bin', 'image/smp-supervisor.bin', 'image/display.bin',
         'image/protection.bin', 'firmware/code.fd', 'firmware/vars.fd',
         'licenses/musl-COPYRIGHT', 'licenses/limine-LICENSE',
         'licenses/edk2-licenses.txt'}
HELPER_PIN = '9f0c0464c10fa23bfc7c3c91fe26b04e5ab063ca058eeb6d41542d98c6186e4e'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def ordinary(path):
    if not path.exists():
        raise FileNotFoundError(str(path))
    need(path.is_file() and not path.is_symlink(), 'regular input required')


def read_json(path):
    ordinary(path)
    need(path.stat().st_size <= 64 * 1024, 'manifest size limit')
    return json.loads(path.read_text())


def verify_bundle(bundle, seal):
    ordinary(bundle / 'SHA256SUMS')
    need(sha(bundle / 'SHA256SUMS') == seal, 'SDK seal mismatch')
    need((bundle / 'SHA256SUMS').stat().st_size <= 128 * 1024,
         'SDK manifest size limit')
    expected = {}
    for line in (bundle / 'SHA256SUMS').read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        path = Path(name)
        need(not path.is_absolute() and '..' not in path.parts
             and str(path) == name and name not in expected,
             'invalid SDK namespace')
        ordinary(bundle / name)
        need(sha(bundle / name) == digest, 'SDK member mismatch')
        expected[name] = digest
    members = list(bundle.rglob('*'))
    need(not bundle.is_symlink() and not any(p.is_symlink() for p in members),
         'SDK links are unsupported')
    need({str(p.relative_to(bundle)) for p in members
          if p.is_file() and p != bundle / 'SHA256SUMS'} == set(expected),
         'SDK namespace mismatch')
    need(expected.get('support/process.py') == HELPER_PIN,
         'owned process helper mismatch')
    return expected


def load_support(bundle, name):
    path = bundle / 'support' / (name + '.py')
    selected = types.ModuleType('lab_selected_' + name)
    selected.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), selected.__dict__)
    return selected


def inputs(source, expected_seal):
    need(not source.is_symlink(), 'input directory cannot be a link')
    lock_path = source / 'lab-inputs.json'
    ordinary(lock_path)
    need(sha(lock_path) == expected_seal, 'lab input seal mismatch')
    lock = read_json(lock_path)
    need(lock.get('schema') == 'aether-lab-inputs-v1'
         and lock.get('profile') in PROFILES, 'lab profile mismatch')
    need(isinstance(lock.get('files'), dict) and set(lock['files']) == FILES,
         'boot input inventory mismatch')
    for name, identity in lock['files'].items():
        path = source / name
        ordinary(path)
        need(isinstance(identity, dict)
             and type(identity.get('bytes')) is int
             and 0 < identity['bytes'] <= 32 * 1024**2
             and path.stat().st_size == identity['bytes']
             and sha(path) == identity.get('sha256'), 'boot input mismatch')
    need(isinstance(lock.get('tools'), dict)
         and set(lock['tools']) == {'xorriso', 'qemu-system-x86_64'},
         'tool inventory mismatch')
    for identity in lock['tools'].values():
        path = Path(identity['path'])
        need(path.is_absolute() and sha(path.resolve()) == identity['sha256'],
             'tool identity mismatch')
    verify_bundle(source / 'bundle', lock['bundle_seal'])
    members = list(source.rglob('*'))
    need(not any(p.is_symlink() for p in members), 'input links unsupported')
    data = (source / 'image/native-c.bin').read_bytes()
    need(len(data) >= 112, 'short native envelope')
    magic, parent, helper, spare, owner, reserved = struct.unpack(
        '<8sIIIIQ', data[:32])
    need(magic == PROFILES[lock['profile']] and reserved == 0 and min(parent, helper, owner) > 0
         and spare == parent and len(data) == 112 + parent + helper + spare + owner,
         'native envelope profile or extent mismatch')
    offset = 112
    parts = []
    for length in [parent, helper, spare, owner]:
        parts.append(hashlib.sha256(data[offset:offset + length]).hexdigest())
        offset += length
    need(parts[0] == parts[2], 'alternate parent must match')
    return lock, parts


def build(source, output, expected_seal):
    source = Path(source)
    # Reject links before resolution; resolution alone would hide their presence.
    need(not source.is_symlink(), 'input directory cannot be a link')
    source = source.resolve()
    output = Path(output).absolute()
    need(not output.exists() and not output.is_symlink(),
         'output must be a new directory')
    output = output.resolve()
    need(output.is_relative_to(ROOT / 'build')
         and not output.is_relative_to(source), 'output must be under build')
    lock, parts = inputs(source, expected_seal)
    bundle = source / 'bundle'
    process = load_support(bundle, 'process')
    builder = load_support(bundle, 'rebuild')
    output.mkdir(parents=True)
    receipt = {'schema': 'aether-lab-build-v1', 'status': 'incomplete',
               'profile': lock['profile'], 'input_seal': expected_seal,
               'bundle_seal': lock['bundle_seal'], 'input_files': lock['files'],
               'tools': lock['tools'], 'python': sys.version,
               'builder_sha256': sha(Path(__file__)), 'commands': [],
               'review': 'SSDK-06 deferred; independent review pending',
               'scope': 'bounded UEFI VM serial fixture; no physical lab acceptance'}

    def save():
        (output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')

    save()
    try:
        clients = builder.rebuild(bundle, output / 'clients', lock['bundle_seal'])
        need(clients['profile'] == lock['profile']
             and clients['parent_sha256'] == parts[0]
             and clients['helper_sha256'] == parts[1],
             'rebuilt clients do not match qualified boot payload')
        receipt['clients'] = clients
        extracted = output / 'iso-check'
        extracted.mkdir()
        for name in ['native-c.bin', 'aether', 'lifecycle.bin',
                     'smp-supervisor.bin', 'display.bin', 'protection.bin']:
            result = process.run(
                [lock['tools']['xorriso']['path'], '-osirrox', 'on', '-indev',
                 str(source / 'image/aether.iso'), '-extract', '/boot/' + name,
                 str(extracted / name)], cwd=output, env=process.clean_env(output),
                work=output, label='iso-' + name, timeout=60,
                file_limit=16 * 1024**2)
            receipt['commands'].append(result.record)
            save()
            need(result.returncode == 0 and result.record['complete']
                 and result.record['cleanup'] == 'complete',
                 'ISO inspection failed')
            need(sha(extracted / name) == lock['files']['image/' + name]['sha256'],
                 'ISO boot component mismatch')
        # Revalidate before publication; no relabeling or rebuilding owner/kernel.
        inputs(source, expected_seal)
        kit = output / 'kit'
        kit.mkdir()
        shutil.copy2(source / 'image/aether.iso', kit / 'aether.iso')
        for name in ['code.fd', 'vars.fd']:
            shutil.copy2(source / 'firmware' / name, kit / name)
        boot = 'BOOT-ABI24.md' if lock['profile'] == 'AENMX009/ABI24' else 'BOOT.md'
        shutil.copy2(ROOT / 'experiments/lab-image' / boot, kit / 'BOOT.md')
        shutil.copy2(ROOT / 'LICENSE', kit / 'LICENSE')
        licenses = kit / 'licenses'
        licenses.mkdir()
        for path in (source / 'licenses').iterdir():
            shutil.copy2(path, licenses / path.name)
        shutil.copy2(bundle / 'producer/user/native-command/dash-inputs/COPYING.dash',
                     licenses / 'COPYING.dash')
        shutil.copy2(ROOT / 'experiments/dash-native/serial-session/command-1.sh',
                     kit / 'command-1.sh')
        shutil.copy2(ROOT / 'experiments/dash-native/serial-session/command-2.sh',
                     kit / 'command-2.sh')
        shutil.copy2(ROOT / 'experiments/dash-native/serial-session/command-3.sh',
                     kit / 'command-3.sh')
        receipt.update(status='pass', native='NOT RUN by builder',
                       payload_parts=parts,
                       kit={str(f.relative_to(kit)): {'sha256': sha(f), 'bytes': f.stat().st_size}
                            for f in sorted(kit.rglob('*')) if f.is_file()})
        save()
        return receipt
    except (OSError, ValueError, RuntimeError) as error:
        receipt.update(status='failed', error=str(error))
        save()
        raise


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print('[ERROR] ' + json.dumps(message, ensure_ascii=True), file=sys.stderr)
        raise SystemExit(64)


def main(argv=None):
    parser = Parser(description='Build a pinned UEFI VM serial-session lab kit.',
                    epilog='Example: --inputs build/lab-inputs --input-seal SHA256 '
                           '--output build/lab-kit. See experiments/lab-image/BOOT.md '
                           'for the bounded workload and boot instructions.')
    parser.add_argument('--version', action='version', version=VERSION)
    parser.add_argument('--inputs', required=True, type=Path,
                        help='directory containing lab-inputs.json and sealed SDK')
    parser.add_argument('--input-seal', required=True,
                        help='externally selected SHA256 of lab-inputs.json')
    parser.add_argument('--output', required=True, type=Path,
                        help='new output directory under build/')
    args = parser.parse_args(argv)
    try:
        build(args.inputs, args.output, args.input_seal)
    except FileNotFoundError as error:
        print('[BLOCKED] ' + json.dumps(str(error), ensure_ascii=True), file=sys.stderr)
        return 2
    except (OSError, ValueError, RuntimeError, KeyError, TypeError) as error:
        print('[ERROR] ' + json.dumps(str(error), ensure_ascii=True), file=sys.stderr)
        return 1
    print(str((args.output / 'kit').absolute()))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
