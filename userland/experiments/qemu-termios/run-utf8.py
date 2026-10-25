#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Run UTF-8 byte/character boundary checks with approved consumer inputs."""
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    work = Path(tempfile.mkdtemp(prefix='tr-utf8-', dir=ROOT / 'build'))
    work.chmod(0o755)
    inputs = work / 'inputs'
    inputs.mkdir()
    report = dict(status='incomplete', work=str(work), python=sys.version)

    def save():
        (work / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    print(str(work), flush=True)
    try:
        prior = ROOT / 'build/qemu-consumers-0c7_83ua'
        evidence = ROOT / 'docs/evidence/qemu-consumer-regression-2026-09-07'
        approval = json.loads((evidence / 'maintainer-review.json').read_text())
        if sha(evidence / 'verification.json') != approval['verification_sha256']:
            raise RuntimeError('approval evidence drift')
        inventory = json.loads((evidence / 'verification.json').read_text())['attempts']
        pinned = [r for r in inventory if r['root'] == str(prior)]
        if len(pinned) != 1 or sha(prior / 'summary.json') != pinned[0]['summary_sha256']:
            raise RuntimeError('consumer receipt drift')
        receipt = json.loads((prior / 'summary.json').read_text())
        if receipt['container']['cleanup'] != 'absent':
            raise RuntimeError('consumer cleanup unresolved')
        for name, digest in receipt['inputs'].items():
            source = prior / 'inputs' / name
            if sha(source) != digest:
                raise RuntimeError('consumer input drift: ' + name)
            dest = inputs / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
        paths = [Path(__file__), HERE / 'check-utf8.py', HERE / 'UTF8-PLAN.md',
                 ROOT / 'experiments/dash-reference/container-process.py',
                 ROOT / 'experiments/command-runner/process.py', prior / 'summary.json',
                 evidence / 'maintainer-review.json', evidence / 'verification.json']
        if sha(paths[4]) != receipt['inputs']['process.py']:
            raise RuntimeError('process helper changed')
        if sha(paths[3]) != receipt['sources'][str(paths[3])]:
            raise RuntimeError('container helper changed')
        shutil.copyfile(paths[1], inputs / 'check-utf8.py')
        build_receipt = Path(sys.argv[1]).resolve() / 'summary.json'
        build = json.loads(build_receipt.read_text())
        if build['status'] != 'pass':
            raise RuntimeError('speed fixture build incomplete')
        paths.append(build_receipt)
        for name, row in build['binaries'].items():
            source = Path(row['path'])
            if sha(source) != row['sha256']:
                raise RuntimeError('fixture drift')
            dest = inputs / 'locale' / name
            dest.parent.mkdir(parents=True)
            shutil.copyfile(source, dest)
            dest.chmod(0o755)
        report['sources'] = {str(p): sha(p) for p in paths}
        report['inputs'] = {str(p.relative_to(inputs)): sha(p) for p in inputs.rglob('*') if p.is_file()}
        save()
        container = runpy.run_path(str(paths[3]))
        client = container['Client'](container['selected_descriptor'](work), work)
        state = container['run_container'](client, receipt['container']['image'],
            ['/usr/local/bin/python3', '/inputs/check-utf8.py'], work, timeout=120, inputs=inputs)
        report['container'] = state
        save()
        if not state['complete'] or state['guest_exit'] != 0:
            raise RuntimeError('recovery guest incomplete')
        result = json.loads((work / 'guest.stdout').read_text())
        report['results'] = result
        expected = [(locale, case) for locale in ['C', 'C.UTF-8']
                    for case in ['probe', 'case', 'alpha-delete', 'literal-delete', 'squeeze']]
        if (result['status'] != 'pass' or [(r['locale'], r['case']) for r in result['results']] != expected
                or not all(r['passed'] for r in result['results'])):
            raise RuntimeError('UTF-8 inventory or oracle failed')
        for path, digest in report['sources'].items():
            if sha(Path(path)) != digest:
                raise RuntimeError('source drift')
        report['status'] = 'pass'
    except (OSError, ValueError, RuntimeError, KeyError) as error:
        report['error'] = str(error)
    save()
    print(report['status'], flush=True)
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
