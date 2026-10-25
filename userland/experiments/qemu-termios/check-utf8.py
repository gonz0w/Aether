#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Characterize byte behavior separately from Unicode character expectations."""
import json
from pathlib import Path
import runpy
import sys


def main():
    process = runpy.run_path('/inputs/process.py')
    work = Path('/scratch')
    rows = []
    cases = [
        ('case', ['[:upper:]', '[:lower:]'], 'AZ ÉΣ🙂'.encode(), 'az ÉΣ🙂'.encode(), 'az éσ🙂'.encode()),
        ('alpha-delete', ['-d', '[:alpha:]'], 'AéZΩ'.encode(), 'éΩ'.encode(), b''),
        ('literal-delete', ['-d', 'é'], 'éê!'.encode(), b'\xaa!', 'ê!'.encode()),
        ('squeeze', ['-s', 'é'], 'éé'.encode(), 'éé'.encode(), 'é'.encode()),
    ]
    for number, locale in enumerate(['C', 'C.UTF-8']):
        env = process['clean_env'](work)
        env.update(LC_ALL=locale, LD_LIBRARY_PATH='/inputs/lib')
        probe = process['run'](['/inputs/patched', '/inputs/locale/probe'], cwd=work, env=env,
            work=work, label=str(number) + '-probe', timeout=10, file_limit=1024**2)
        expected = b'1\tASCII\t1\t0\t233\n' if number == 0 else b'1\tUTF-8\t4\t0\t233\n'
        rows.append(dict(locale=locale, case='probe', process=probe.record, stdout_hex=probe.stdout.hex(),
            stderr_hex=probe.stderr.hex(), passed=probe.record['complete'] and probe.returncode == 0
            and probe.stdout == expected and probe.stderr == b''))
        for case, args, data, expected, character_expected in cases:
            result = process['run'](['/inputs/patched', '/inputs/bin/tr'] + args, cwd=work, env=env,
                work=work, label=str(number) + '-' + case, timeout=10, input=data, file_limit=1024**2)
            try:
                result.stdout.decode('utf-8', errors='strict')
                valid = True
            except UnicodeDecodeError:
                valid = False
            passed = (result.record['complete'] and result.returncode == 0 and result.stdout == expected
                and result.stderr == b'' and valid == (case != 'literal-delete')
                and result.stdout != character_expected)
            rows.append(dict(locale=locale, case=case, process=result.record, input_hex=data.hex(),
                expected_hex=expected.hex(), actual_hex=result.stdout.hex(), stderr_hex=result.stderr.hex(),
                utf8_valid=valid, character_expected_hex=character_expected.hex(),
                character_expectation_met=result.stdout == character_expected, passed=passed))
    passed = len(rows) == 10 and all(r['passed'] for r in rows)
    print(json.dumps(dict(status='pass' if passed else 'incomplete', python=sys.version, results=rows), indent=2))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
