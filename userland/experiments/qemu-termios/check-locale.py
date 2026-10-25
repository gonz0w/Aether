#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Observe candidate codesets independently of host locale availability."""
import json
from pathlib import Path
import runpy
import sys


def main():
    process = runpy.run_path('/inputs/process.py')
    work = Path('/scratch')
    rows = []
    for number, locale in enumerate(['C', 'POSIX', 'C.UTF-8', 'en_US.ISO-8859-1', 'aether_missing_locale']):
        env = process['clean_env'](work)
        env.update(LC_ALL=locale, LD_LIBRARY_PATH='/inputs/lib')
        for kind in ['probe', 'tr']:
            if kind == 'probe':
                argv = ['/inputs/patched', '/inputs/locale/probe']
                data = b''
                expected = b'1\tASCII\t1\t0\t233\n' if number < 2 else b'1\tUTF-8\t4\t0\t233\n'
            else:
                argv = ['/inputs/patched', '/inputs/bin/tr', '[:upper:]', '[:lower:]']
                data = b'AZaz\xe9\xc9\n'
                expected = b'azaz\xe9\xc9\n'
            result = process['run'](argv, cwd=work, env=env, work=work,
                label=str(number) + '-' + kind, timeout=10, input=data, file_limit=1024**2)
            passed = (result.record['complete'] and result.returncode == 0
                and result.stdout == expected and result.stderr == b'')
            rows.append(dict(locale=locale, kind=kind, process=result.record, input_hex=data.hex(),
                expected_hex=expected.hex(), actual_hex=result.stdout.hex(), stderr_hex=result.stderr.hex(), passed=passed))
    passed = len(rows) == 10 and all(r['passed'] for r in rows)
    print(json.dumps(dict(status='pass' if passed else 'incomplete', python=sys.version, results=rows), indent=2))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
