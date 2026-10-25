# SPDX-License-Identifier: BSD-2-Clause
"""Verify and exercise one sealed ABI24 developer kit; Python 3.10+."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import types

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
HELPER_PIN = '9f0c0464c10fa23bfc7c3c91fe26b04e5ab063ca058eeb6d41542d98c6186e4e'
WORKLOAD_PIN = '1e9540b7be7a8cd6fd4fc2f1bc9ce43327281dd7355ae48f89195dc0f616de85'
REQUIRED = {'aether.iso', 'code.fd', 'vars.fd', 'BOOT.md', 'LICENSE',
            'command-1.sh', 'command-2.sh', 'command-3.sh', 'receipt.json',
            'licenses/COPYING.dash', 'licenses/musl-COPYRIGHT',
            'licenses/limine-LICENSE', 'licenses/edk2-licenses.txt'}


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def ordinary(path, limit=32 * 1024**2):
    if not path.exists():
        raise FileNotFoundError(str(path))
    need(path.is_file() and not path.is_symlink()
         and 0 < path.stat().st_size <= limit, 'regular bounded file required')


def json_file(path):
    ordinary(path, 1024 * 1024)
    value = json.loads(path.read_text())
    need(isinstance(value, dict), 'JSON object required')
    return value


def verify(kit, seal):
    need(re.fullmatch('[0-9a-f]{64}', seal) is not None, 'invalid kit seal')
    need(not kit.is_symlink(), 'kit link unsupported')
    ordinary(kit / 'SHA256SUMS', 64 * 1024)
    need(sha(kit / 'SHA256SUMS') == seal, 'kit seal mismatch')
    pins = {}
    for line in (kit / 'SHA256SUMS').read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        path = Path(name)
        need(re.fullmatch('[0-9a-f]{64}', digest) is not None
             and not path.is_absolute() and '..' not in path.parts
             and str(path) == name and name not in pins, 'kit manifest entry')
        ordinary(kit / name)
        need(sha(kit / name) == digest, 'kit member mismatch')
        pins[name] = digest
    need(set(pins) in (REQUIRED, REQUIRED | {'OWNER.md'}),
         'unsupported kit inventory')
    members = []
    for member in kit.rglob('*'):
        need(len(members) < 32, 'kit namespace bound')
        members.append(member)
    need({str(f.relative_to(kit)) for f in members if f.is_dir()}
         == {'licenses'}, 'kit directory inventory')
    need(not any(f.is_symlink() for f in members), 'kit links unsupported')
    need({str(f.relative_to(kit)) for f in members if not f.is_dir()}
         == set(pins) | {'SHA256SUMS'}, 'kit namespace mismatch')
    receipt = json_file(kit / 'receipt.json')
    need(receipt.get('schema') == 'aether-lab-build-v1'
         and receipt.get('status') == 'pass'
         and receipt.get('profile') == 'AENMX009/ABI24', 'ABI24 build required')
    need(receipt['input_files']['image/aether.iso']['sha256']
         == pins['aether.iso'], 'build ISO binding')
    for name in ['code.fd', 'vars.fd']:
        need(receipt['input_files']['firmware/' + name]['sha256'] == pins[name],
             'build firmware binding')
    qemu = receipt['tools']['qemu-system-x86_64']
    need(isinstance(qemu, dict) and isinstance(qemu.get('path'), str)
         and isinstance(qemu.get('sha256'), str), 'QEMU record required')
    tool = Path(qemu['path'])
    need(tool.is_absolute() and sha(tool.resolve()) == qemu['sha256'],
         'QEMU identity mismatch')
    workload_path = HERE / 'workload-abi24.json'
    need(sha(workload_path) == WORKLOAD_PIN, 'workload identity')
    workload = json_file(workload_path)
    for phase in range(1, 4):
        name = 'command-' + str(phase) + '.sh'
        need((kit / name).read_bytes() == bytes.fromhex(workload[name]),
             'qualified command mismatch')
    helper = ROOT / 'experiments/command-runner/process.py'
    need(sha(helper) == HELPER_PIN, 'owned process helper identity')
    process = types.ModuleType('lab_boot_process')
    exec(compile(helper.read_bytes(), str(helper), 'exec'), process.__dict__)
    return receipt, workload, process


def run(kit, seal, output, delay):
    receipt, workload, process = verify(kit, seal)
    need(delay in (0, 35), 'unsupported delay')
    need(not output.exists() and not output.is_symlink(), 'new output required')
    output = output.resolve()
    need(output.is_relative_to(ROOT / 'build')
         and not output.is_relative_to(kit.resolve()), 'output must be under build')
    output.mkdir(parents=True)
    record = {'schema': 'aether-lab-boot-v1', 'status': 'incomplete',
              'kit': str(kit.resolve()), 'kit_seal': seal, 'delay_seconds': delay,
              'python': sys.version, 'python_sha256': sha(Path(sys.executable)),
              'sources': {name: sha(HERE / name) for name in
                          ['boot.py', 'boot-driver.py', 'serial_oracle.py',
                           'workload-abi24.json']},
              'qemu': receipt['tools']['qemu-system-x86_64'],
              'scope': 'bounded ABI24 developer VM; no release or hardware claim'}
    path = output / 'receipt.json'
    path.write_text(json.dumps(record, indent=2) + '\n')
    result = process.run(
        [sys.executable, '-B', str(HERE / 'boot-driver.py'), str(kit.resolve()),
         seal, str(output), str(delay)], cwd=ROOT, env=process.clean_env(output),
        work=output, label='native', timeout=105, file_limit=16 * 1024**2)
    record['process'] = result.record
    passed = (result.returncode == 0 and result.record['complete']
              and result.record['cleanup'] == 'complete')
    record['status'] = 'pass' if passed else 'failed'
    if passed:
        session = json_file(output / 'session.json')
        need(session['status'] == 'pass', 'native witness missing')
        record['native'] = session['independent_oracle']
    path.write_text(json.dumps(record, indent=2) + '\n')
    need(passed, 'native boot check failed; inspect output receipt and logs')
    return output


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print('[ERROR] ' + json.dumps(message, ensure_ascii=True), file=sys.stderr)
        raise SystemExit(64)


def main(argv=None):
    parser = Parser(description='Check a sealed ABI24 lab kit in a fresh VM.')
    parser.add_argument('--version', action='version',
                        version='aether-lab-boot 0.1.0')
    parser.add_argument('--kit', required=True, type=Path)
    parser.add_argument('--kit-seal', required=True)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--delay', type=int, choices=[0, 35], default=0,
                        help='seconds idle at the first prompt (default: 0)')
    args = parser.parse_args(argv)
    try:
        print(run(args.kit, args.kit_seal, args.output, args.delay))
    except FileNotFoundError as error:
        print('[ERROR] ' + json.dumps(str(error), ensure_ascii=True),
              file=sys.stderr)
        return 2
    except (ValueError, KeyError, TypeError, OSError) as error:
        print('[ERROR] ' + json.dumps(str(error), ensure_ascii=True),
              file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
