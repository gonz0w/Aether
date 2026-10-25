#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Measure bounded GNU byte workload with approved consumer inputs."""
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
    work = Path(tempfile.mkdtemp(prefix='tr-workload-', dir=ROOT / 'build'))
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
        paths = [Path(__file__), HERE / 'check-workload.py', HERE / 'WORKLOAD-PLAN.md',
                 ROOT / 'experiments/dash-reference/container-process.py',
                 ROOT / 'experiments/command-runner/process.py', prior / 'summary.json',
                 evidence / 'maintainer-review.json', evidence / 'verification.json']
        if sha(paths[4]) != receipt['inputs']['process.py']:
            raise RuntimeError('process helper changed')
        if sha(paths[3]) != receipt['sources'][str(paths[3])]:
            raise RuntimeError('container helper changed')
        shutil.copyfile(paths[1], inputs / 'check-workload.py')
        lock_path = ROOT / 'experiments/tr-stty-reference/source.lock.json'
        paths.append(lock_path)
        lock = json.loads(lock_path.read_text())['busybox']
        import tarfile
        archive_path = ROOT / lock['archive']
        if sha(archive_path) != lock['sha256']:
            raise RuntimeError('BusyBox archive drift')
        report['archive'] = lock
        cases = ['tr-d-alnum-works', 'tr-d-works', 'tr-non-gnu',
                 'tr-rejects-wrong-class', 'tr-works']
        with tarfile.open(archive_path) as archive:
            for name in ['testsuite/tr/' + c for c in cases] + ['testsuite/README', 'LICENSE', 'coreutils/tr.c']:
                member = archive.getmember('busybox-1.38.0/' + name)
                if not member.isfile():
                    raise RuntimeError('nonregular test input')
                target = inputs / ('legacy/' + Path(name).name)
                target.parent.mkdir(exist_ok=True)
                target.write_bytes(archive.extractfile(member).read())
        candidate_receipt = ROOT / 'build/busybox-musl-qdkunzpu/evidence.json'
        paths.append(candidate_receipt)
        binary = json.loads(candidate_receipt.read_text())['binaries']['tr']
        source = Path(binary['path'])
        if sha(source) != binary['sha256']:
            raise RuntimeError('BusyBox binary drift')
        config = source.parent / '.config'
        if 'CONFIG_FEATURE_TR_CLASSES=y' not in config.read_text():
            raise RuntimeError('required class feature absent')
        paths.append(config)
        shutil.copyfile(source, inputs / 'busybox_unstripped')
        (inputs / 'busybox_unstripped').chmod(0o755)
        for mode in ['normal', 'control']:
            target = inputs / mode / 'busybox'
            target.parent.mkdir()
            body = ('exit 99\n' if mode == 'control' else
                'LD_LIBRARY_PATH=/inputs/lib exec /inputs/patched /inputs/busybox_unstripped \"$@\"\n')
            target.write_text('#!/bin/sh\n' + body)
            target.chmod(0o755)
        report['sources'] = {str(p): sha(p) for p in paths}
        report['inputs'] = {str(p.relative_to(inputs)): sha(p) for p in inputs.rglob('*') if p.is_file()}
        save()
        container = runpy.run_path(str(paths[3]))
        client = container['Client'](container['selected_descriptor'](work), work)
        state = container['run_container'](client, receipt['container']['image'],
            ['/usr/local/bin/python3', '/inputs/check-workload.py'], work, timeout=120, inputs=inputs)
        report['container'] = state
        save()
        if not state['complete'] or state['guest_exit'] != 0:
            raise RuntimeError('legacy guest incomplete')
        result = json.loads((work / 'guest.stdout').read_text())
        report['results'] = result
        expected = [('warmup', 65536, 0)] + [('measured', size, rep)
                    for size in [65536, 1048576] for rep in range(1, 4)]
        if (result['status'] != 'pass' or
                [(r['phase'], r['input_bytes'], r['repeat']) for r in result['results']] != expected or
                not all(r['passed'] and r['process']['cleanup'] == 'complete' for r in result['results'])):
            raise RuntimeError('workload inventory or correctness failed')
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
