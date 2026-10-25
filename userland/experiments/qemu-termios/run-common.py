#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Repeat existing seventeen-fixture GNU/BusyBox comparison; Python 3.10+."""
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    previous = Path(sys.argv[1]).resolve()
    prior = json.loads((previous / 'summary.json').read_text())
    if prior.get('container', {}).get('cleanup') != 'absent':
        raise RuntimeError('previous execution cleanup unresolved')
    work = Path(tempfile.mkdtemp(prefix='qemu-common-', dir=ROOT / 'build'))
    work.chmod(0o755)
    print(str(work), flush=True)
    report = {'status': 'incomplete', 'work': str(work), 'python': sys.version, 'runs': {}}

    def save():
        (work / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    try:
        source = ROOT / 'experiments/tr-stty-reference/cases.py'
        adapter = ROOT / 'experiments/dash-reference/container-process.py'
        report['sources'] = {str(p): sha(p) for p in [Path(__file__), source, adapter,
            ROOT / 'experiments/command-runner/process.py',
            ROOT / 'experiments/qemu-termios/COMMON-PLAN.md', previous / 'summary.json']}
        container = runpy.run_path(str(adapter))
        descriptor = container['selected_descriptor'](work)
        for provider, build in [('gnu', 'coreutils-musl-bdcrzzq6'), ('busybox', 'busybox-musl-qdkunzpu')]:
            run = work / provider
            inputs = run / 'inputs'
            inputs.mkdir(parents=True)
            for name in ['patched', 'lib/libglib-2.0.so.0', 'lib/libatomic.so.1']:
                path = previous / 'inputs' / name
                if sha(path) != prior['inputs'][name]:
                    raise RuntimeError('runtime drift')
                dest = inputs / name
                dest.parent.mkdir(exist_ok=True)
                shutil.copy2(path, dest)
            receipt_path = ROOT / 'build' / build / 'evidence.json'
            receipt = json.loads(receipt_path.read_text())
            if set(receipt['binaries']) != {'tr', 'stty'}:
                raise RuntimeError('unexpected candidate inventory')
            for name, row in receipt['binaries'].items():
                path = Path(row['path'])
                if sha(path) != row['sha256']:
                    raise RuntimeError('candidate drift')
                target_name = 'busybox_unstripped' if provider == 'busybox' else name
                shutil.copyfile(path, inputs / target_name)
                (inputs / target_name).chmod(0o755)
                row['path'] = '/inputs/' + target_name
            (inputs / 'evidence.json').write_text(json.dumps(receipt, indent=2) + '\n')
            guest = source.read_text()
            changes = {
                '"/usr/bin/qemu-x86_64"': '"/inputs/patched"',
                'env={"PATH": "/usr/bin:/bin", "LC_ALL": "C"}': 'env={"PATH": "/usr/bin:/bin", "LC_ALL": "C", "LD_LIBRARY_PATH": "/inputs/lib"}',
                'print("PASS" if summary["pass"] else "INCOMPLETE")': 'print(json.dumps(summary, indent=2))',
            }
            for old, new in changes.items():
                if guest.count(old) != (2 if old == '"/usr/bin/qemu-x86_64"' else 1):
                    raise RuntimeError('guest adapter anchor changed')
                guest = guest.replace(old, new)
            (inputs / 'cases.py').write_text(guest)
            row = {'receipt_sha256': sha(receipt_path), 'inputs': {
                str(p.relative_to(inputs)): sha(p) for p in inputs.rglob('*') if p.is_file()}}
            report['runs'][provider] = row
            save()
            state = container['run_container'](container['Client'](descriptor, run),
                prior['container']['image'], ['/usr/local/bin/python3', '/inputs/cases.py', '/inputs'],
                run, timeout=180, inputs=inputs)
            row['container'] = state
            save()
            if not state['complete']:
                raise RuntimeError('container incomplete')
            result = json.loads((run / 'guest.stdout').read_text())
            row['results'] = result
            failures = [r['case'] for r in result['results'] if not r['pass']]
            expected = [] if provider == 'gnu' else ['repeat', 'print-class', 'invalid-class', 'reversed-range']
            row['regression_matches_prior'] = (len(result['results']) == 17 and failures == expected
                and state['guest_exit'] == (0 if provider == 'gnu' else 1)
                and result['qemu_sha256'] == row['inputs']['patched'])
            if not row['regression_matches_prior']:
                raise RuntimeError('comparison changed')
        for path, digest in report['sources'].items():
            if sha(Path(path)) != digest:
                raise RuntimeError('source drift')
        report['status'] = 'regression-matches-prior'
    except (OSError, ValueError, RuntimeError, KeyError) as error:
        report['error'] = str(error)
    save()
    print(report['status'], flush=True)
    return 0 if report['status'] == 'regression-matches-prior' else 1


if __name__ == '__main__':
    raise SystemExit(main())
