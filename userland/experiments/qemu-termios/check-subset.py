#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Exact byte deletion cases for observed package tr expressions."""
import json
from pathlib import Path
import runpy
import sys


def main():
    process = runpy.run_path('/inputs/process.py')
    work = Path('/scratch')
    env = process['clean_env'](work)
    env['LD_LIBRARY_PATH'] = '/inputs/lib'
    rows = []
    specs = [('whitespace', '[:space:]', {9, 10, 11, 12, 13, 32}),
             ('binding', r'\012\040-\176', {10} | set(range(32, 127)))]
    for provider, command in [('gnu', ['/inputs/patched', '/inputs/bin/tr']),
                              ('busybox', ['/inputs/patched', '/inputs/busybox_unstripped', 'tr'])]:
        for kind, operand, removed in specs:
            samples = [('all-bytes', bytes(range(256))), ('empty', b'')]
            if kind == 'whitespace':
                samples.append(('numeric', b' \t123\n\r\v\f'))
            for sample, data in samples:
                expected = bytes(b for b in data if b not in removed)
                result = process['run'](command + ['-d', operand], cwd=work, env=env,
                    work=work, label=provider + '-' + kind + '-' + sample,
                    timeout=15, input=data, file_limit=1024**2)
                rows.append(dict(provider=provider, kind=kind, sample=sample, process=result.record,
                    input_hex=data.hex(), expected_hex=expected.hex(), actual_hex=result.stdout.hex(),
                    stderr_hex=result.stderr.hex(), passed=result.record['complete'] and result.returncode == 0
                    and result.stdout == expected and result.stderr == b''))
    passed = len(rows) == 10 and all(row['passed'] for row in rows)
    print(json.dumps(dict(status='pass' if passed else 'incomplete', python=sys.version, results=rows), indent=2))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
