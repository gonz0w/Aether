#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Repeat pinned GNU/BusyBox upstream tr suites with corrected QEMU."""
import hashlib
import json
from pathlib import Path
import re
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
    prior_root = Path(sys.argv[1]).resolve()
    prior = json.loads((prior_root / 'summary.json').read_text())
    if prior['container']['cleanup'] != 'absent':
        raise RuntimeError('unresolved prior cleanup')
    work = Path(tempfile.mkdtemp(prefix='qemu-upstream-', dir=ROOT / 'build'))
    work.chmod(0o755)
    print(str(work), flush=True)
    report = dict(status='incomplete', work=str(work), python=sys.version, runs={})

    def save():
        (work / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    try:
        ref = ROOT / 'experiments/tr-stty-reference'
        paths = [Path(__file__), HERE / 'UPSTREAM-PLAN.md',
                 ROOT / 'experiments/dash-reference/container-process.py',
                 ROOT / 'experiments/command-runner/process.py',
                 ref / 'source.lock.json', ref / 'perl-helpers.lock.json',
                 prior_root / 'summary.json']
        report['sources'] = {str(p): sha(p) for p in paths}
        locks = json.loads(paths[4].read_text())
        container = runpy.run_path(str(paths[2]))
        descriptor = container['selected_descriptor'](work)
        for name in ['gnu', 'gnu-control', 'busybox']:
            run = work / name
            inputs = run / 'inputs'
            inputs.mkdir(parents=True)
            for rel in ['patched', 'lib/libglib-2.0.so.0', 'lib/libatomic.so.1']:
                source = prior_root / 'inputs' / rel
                if sha(source) != prior['inputs'][rel]:
                    raise RuntimeError('runtime drift')
                dest = inputs / rel
                dest.parent.mkdir(exist_ok=True)
                shutil.copy2(source, dest)
            busy = name == 'busybox'
            build = 'busybox-musl-qdkunzpu' if busy else 'coreutils-musl-bdcrzzq6'
            receipt = ROOT / 'build' / build / 'evidence.json'
            binary = json.loads(receipt.read_text())['binaries']['tr']
            if sha(Path(binary['path'])) != binary['sha256']:
                raise RuntimeError('binary drift')
            dest = inputs / ('busybox_unstripped' if busy else 'bin/tr')
            dest.parent.mkdir(exist_ok=True)
            shutil.copyfile(binary['path'], dest)
            dest.chmod(0o755)
            lock = locks['busybox' if busy else 'coreutils']
            archive_path = ROOT / lock['archive']
            if sha(archive_path) != lock['sha256']:
                raise RuntimeError('archive drift')
            members = (['testsuite/testing.sh', 'testsuite/tr.tests', 'LICENSE'] if busy else
                       ['tests/Coreutils.pm', 'tests/CuSkip.pm', 'tests/tr/tr.pl', 'COPYING'])
            prefix = 'busybox-1.38.0/' if busy else 'coreutils-9.11/'
            with tarfile.open(archive_path) as archive:
                for rel in members:
                    entry = archive.getmember(prefix + rel)
                    if not entry.isfile():
                        raise RuntimeError('nonregular upstream input')
                    (inputs / Path(rel).name).write_bytes(archive.extractfile(entry).read())
            expected = set()
            if not busy:
                helpers = json.loads(paths[5].read_text())
                for rel, row in helpers['files'].items():
                    source = ROOT / helpers['root'] / rel
                    if sha(source) != row['sha256']:
                        raise RuntimeError('Perl helper drift')
                    target = inputs / rel
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(source, target)
                names = re.findall(r"^  \['([^']+)'", (inputs / 'tr.pl').read_text(), re.MULTILINE)
                expected = {n + suffix for n in names for suffix in ['.p', '.r']}
                if len(expected) != 134 or len(expected) != 2 * len(names):
                    raise RuntimeError('upstream inventory changed')
            body = ('exit 99\n' if name == 'gnu-control' else
                    'LD_LIBRARY_PATH=/inputs/lib exec /inputs/patched /inputs/' + str(dest.relative_to(inputs))
                    + (' tr' if busy else '') + ' "$@"\n')
            (inputs / 'tr').write_text('#!/bin/sh\n' + body)
            (inputs / 'tr').chmod(0o755)
            script = '#!/bin/sh\nset -e\ncd /scratch\nexport PATH=/inputs:/usr/bin:/bin\n'
            script += '/usr/bin/uname -a\n/usr/bin/sha256sum /inputs/patched\n'
            if busy:
                script += ('export OPTIONFLAGS=:FEATURE_TR_CLASSES:FEATURE_TR_EQUIV:\n'
                           'export ECHO=/bin/echo\ncp /inputs/testing.sh /scratch/testing.sh\n'
                           'exec /bin/bash /inputs/tr.tests\n')
            else:
                script += ('/usr/bin/perl -v\n/usr/bin/sha256sum /usr/bin/perl\n'
                           'export built_programs=tr VERBOSE=1 DEBUG=0 srcdir=/inputs\n'
                           'exec /usr/bin/perl -I /inputs -MCuSkip -MCoreutils /inputs/tr.pl\n')
            (inputs / 'run.sh').write_text(script)
            row = dict(receipt_sha256=sha(receipt), archive=lock, inputs={
                str(p.relative_to(inputs)): sha(p) for p in inputs.rglob('*') if p.is_file()})
            report['runs'][name] = row
            save()
            state = container['run_container'](container['Client'](descriptor, run), prior['container']['image'],
                ['/bin/bash', '/inputs/run.sh'], run, timeout=180, inputs=inputs)
            row['container'] = state
            save()
            if not state['complete']:
                raise RuntimeError('container incomplete')
            stdout = (run / 'guest.stdout').read_text()
            stderr = (run / 'guest.stderr').read_text()
            if busy:
                row['count'] = sum(line.startswith('PASS: ') for line in stdout.splitlines())
                passed = row['count'] == 5 and 'FAIL:' not in stdout and 'SKIPPED:' not in stdout and state['guest_exit'] == 0
            else:
                observed = re.findall(r'^([a-zA-Z0-9-]+\.[pr])\.\.\.$', stderr, re.MULTILINE)
                row.update(expected=sorted(expected), observed=observed)
                passed = set(observed) == expected and len(observed) == len(expected)
                passed = passed and (state['guest_exit'] == 1 and 'exit status mismatch' in stderr
                    if name == 'gnu-control' else state['guest_exit'] == 0)
            row['pass'] = passed
            if not passed:
                raise RuntimeError('upstream oracle failed: ' + name)
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
