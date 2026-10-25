#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Subtract dash's own definitions from its object imports; not a syscall audit."""
import hashlib
import json
from pathlib import Path
import runpy
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROCESS = runpy.run_path(str(ROOT / 'experiments/command-runner/process.py'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(build, tool, *, timeout=30, file_limit=1024**2):
    """Inspect a trusted build tree with a pinned host tool; Python 3.10+."""
    build = Path(build).resolve()
    if sha(Path(tool['path'])) != tool['sha256']:
        raise ValueError('nm tool pin mismatch')
    paths = sorted((build / 'obj/src').rglob('*.o'))
    if not paths:
        raise ValueError('no dash objects')
    work = Path(tempfile.mkdtemp(prefix='dash-imports-', dir=ROOT / 'build'))
    undefined, defined, objects = set(), set(), {}
    for index, path in enumerate(paths):
        objects[str(path.relative_to(build))] = sha(path)
        result = PROCESS['run'](
            [tool['path'], '--extern-only', str(path)], cwd=build,
            env=PROCESS['clean_env'](work), work=work, label=f'nm-{index}',
            timeout=timeout, file_limit=file_limit,
        )
        if not result.record['complete'] or result.returncode != 0:
            raise ValueError(f'nm inspection failed; retained evidence: {work}')
        for line in result.stdout.decode('utf-8').splitlines():
            fields = line.split()
            if len(fields) >= 2:
                if fields[-2] == 'U':
                    undefined.add(fields[-1])
                elif fields[-2].isupper():
                    defined.add(fields[-1])
    report = {
        'scope': 'undefined external symbols across dash objects minus '
                 'definitions in those objects; libc internal syscall paths '
                 'require separate audit',
        'script_sha256': sha(Path(__file__)),
        'objects': objects,
        'symbols': sorted(undefined - defined),
    }
    (build / 'libc-imports.json').write_text(json.dumps(report, indent=2) + '\n')
    (work / 'result.json').write_text(json.dumps({
        'report': str(build / 'libc-imports.json'),
        'report_sha256': sha(build / 'libc-imports.json'),
        'helper_sha256': sha(ROOT / 'experiments/command-runner/process.py'),
    }, indent=2) + '\n')
    return work


def main():
    build = Path(sys.argv[1]).resolve()
    tool = json.loads((HERE.parent / 'musl-reference/tools.lock.json')
                      .read_text())['tools']['nm']
    audit(build, tool)


if __name__ == '__main__':
    main()
