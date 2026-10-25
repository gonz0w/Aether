#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Run unchanged BusyBox legacy tr scripts and failure controls."""
import json
from pathlib import Path
import runpy
import sys

CASES = ['tr-d-alnum-works', 'tr-d-works', 'tr-non-gnu', 'tr-rejects-wrong-class', 'tr-works']


def main():
    process = runpy.run_path('/inputs/process.py')
    report = dict(status='incomplete', python=sys.version, results=[])
    try:
        for mode in ['normal', 'control']:
            for case in CASES:
                work = Path('/scratch') / (mode + '-' + case)
                work.mkdir()
                env = process['clean_env'](work)
                env.update(PATH='/inputs/' + mode + ':/inputs/src:/usr/bin:/bin', ECHO='/bin/echo')
                result = process['run'](['/bin/sh', '-x', '-e', '/inputs/legacy/' + case],
                    cwd=work, env=env, work=work, label='test', timeout=15, file_limit=1024**2)
                row = dict(mode=mode, case=case, process=result.record,
                    stdout=result.stdout.decode(errors='replace'), stderr=result.stderr.decode(errors='replace'),
                    comparisons={p.name:p.read_bytes().hex() for p in work.glob('logfile.*')})
                row['pass'] = result.record['complete'] and result.returncode == (0 if mode == 'normal' else 99)
                if mode == 'normal' and case == 'tr-non-gnu':
                    row['pass'] = row['pass'] and result.stdout == b'squeamish ossifrage\n'
                report['results'].append(row)
        report['status'] = 'pass' if all(r['pass'] for r in report['results']) else 'incomplete'
    except (OSError, ValueError, RuntimeError) as error:
        report['error'] = str(error)
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
