#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Repeat GNU extended tests with receipt-pinned corrected QEMU; Python 3.10+."""
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    work = Path(tempfile.mkdtemp(prefix='qemu-consumers-', dir=ROOT / 'build'))
    work.chmod(0o755)
    inputs = work / 'inputs'
    inputs.mkdir()
    report = dict(status='incomplete', work=str(work), python=sys.version)

    def save():
        (work / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')

    print(str(work), flush=True)
    save()
    try:
        witness = ROOT / 'build/qemu-pty-x0qwtqas'
        receipt = json.loads((witness / 'summary.json').read_text())
        approved = ROOT / 'docs/evidence/qemu-offline-build-2026-09-07'
        review = json.loads((approved / 'maintainer-review.json').read_text())
        if sha(witness / 'summary.json') != review['evidence_sha256']['pty-summary.json']:
            raise RuntimeError('unapproved PTY receipt')
        if receipt['status'] != 'pass' or receipt['container']['cleanup'] != 'absent':
            raise RuntimeError('PTY prerequisite incomplete')
        sources = [Path(__file__), HERE / 'CONSUMER-PLAN.md', witness / 'summary.json',
                   approved / 'maintainer-review.json',
                   ROOT / 'experiments/dash-reference/container-process.py',
                   ROOT / 'experiments/command-runner/process.py',
                   ROOT / 'experiments/tr-stty-reference/shell-cases.py',
                   ROOT / 'experiments/tr-stty-reference/source.lock.json']
        for name, digest in receipt['inputs'].items():
            source = witness / 'inputs' / name
            if sha(source) != digest:
                raise RuntimeError('runtime input drift: ' + name)
            dest = inputs / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
        for rel in ['docs/evidence/gnu-stty-extended-2026-09-06/candidate-receipt.json',
                    'build/getlimits-musl-eoy5yrnq/evidence.json']:
            path = ROOT / rel
            sources.append(path)
            for name, row in json.loads(path.read_text())['binaries'].items():
                source = Path(row['path'])
                if sha(source) != row['sha256']:
                    raise RuntimeError('candidate drift: ' + name)
                dest = inputs / 'bin' / name
                dest.parent.mkdir(exist_ok=True)
                shutil.copyfile(source, dest)
                dest.chmod(0o755)
                wrapper = inputs / 'src' / name
                wrapper.parent.mkdir(exist_ok=True)
                wrapper.write_text('#!/bin/sh\nLD_LIBRARY_PATH=/inputs/lib exec /inputs/patched /inputs/bin/' + name + ' "$@"\n')
                wrapper.chmod(0o755)
        lock = json.loads((sources[7]).read_text())['coreutils']
        archive_path = ROOT / lock['archive']
        if sha(archive_path) != lock['sha256']:
            raise RuntimeError('upstream archive drift')
        report['archive'] = lock
        with tarfile.open(archive_path) as archive:
            for name in ['tests/init.sh', 'init.cfg', 'COPYING', 'tests/tr/tr-case-class.sh',
                         'tests/stty/stty-row-col.sh', 'tests/stty/stty-invalid.sh',
                         'tests/stty/stty.sh', 'tests/stty/stty-pairs.sh', 'src/stty.c']:
                entry = archive.getmember('coreutils-9.11/' + name)
                if not entry.isfile():
                    raise RuntimeError('nonregular upstream input')
                dest = inputs / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(archive.extractfile(entry).read())
        guest = sources[6].read_text()
        old = 'Path("/usr/bin/qemu-x86_64")'
        if guest.count(old) != 1:
            raise RuntimeError('guest identity anchor changed')
        (inputs / 'shell-cases.py').write_text(guest.replace(old, 'Path("/inputs/patched")'))
        report['sources'] = {str(p): sha(p) for p in sources}
        report['inputs'] = {str(p.relative_to(inputs)): sha(p) for p in inputs.rglob('*') if p.is_file()}
        save()
        container = runpy.run_path(str(sources[4]))
        client = container['Client'](container['selected_descriptor'](work), work)
        state = container['run_container'](client, receipt['container']['image'],
                    ['/usr/local/bin/python3', '/inputs/shell-cases.py', '/inputs', '--extended'],
                    work, timeout=420, inputs=inputs)
        report['container'] = state
        save()
        if not state['complete']:
            raise RuntimeError('container lifecycle incomplete')
        results = json.loads((work / 'guest.stdout').read_text())
        report['results'] = results
        if (state['guest_exit'] != 0 or not results['pass'] or len(results['results']) != 6
                or results['qemu_sha256'] != report['inputs']['patched']):
            raise RuntimeError('GNU suite or restoration incomplete')
        for path, digest in report['sources'].items():
            if sha(Path(path)) != digest:
                raise RuntimeError('source changed during execution')
        report['status'] = 'pass'
    except (OSError, ValueError, RuntimeError, KeyError) as error:
        report['error'] = str(error)
    save()
    print(report['status'], flush=True)
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
