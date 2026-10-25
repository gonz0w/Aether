#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Compare literal brackets and plain ranges using explicit byte arrays."""
import json
from pathlib import Path
import runpy
import sys


def main():
    process = runpy.run_path('/inputs/process.py')
    work = Path('/scratch')
    env = process['clean_env'](work)
    env['LD_LIBRARY_PATH'] = '/inputs/lib'
    alphabet = b'abcdefghijklmnopqrstuvwxyz'
    rotated = b'nopqrstuvwxyzabcdefghijklm'
    phrase = b'fdhrnzvfu bffvsentr\n'
    rows = []
    specs = [('bracketed', ['[a-z]', '[n-z][a-m]'], b'[' + alphabet + b']',
              b'[nopqrstuvwxyz][abcdefghijklm]'),
             ('plain', ['a-z', 'n-za-m'], alphabet, rotated)]
    for provider, command in [('gnu', ['/inputs/patched', '/inputs/bin/tr']),
                              ('busybox', ['/inputs/patched', '/inputs/busybox_unstripped', 'tr'])]:
        for form, args, source, target in specs:
            table = bytearray(range(256))
            for old, new in zip(source, target):
                table[old] = new
            for sample, data in [('phrase', phrase), ('all-bytes', bytes(range(256)))]:
                expected = data.translate(bytes(table))
                result = process['run'](command + args, cwd=work, env=env, work=work,
                    label=provider + '-' + form + '-' + sample, timeout=15,
                    input=data, file_limit=1024**2)
                passed = result.record['complete'] and result.returncode == 0 and result.stdout == expected and result.stderr == b''
                if sample == 'phrase':
                    passed = passed and ((result.stdout == b'squeamish ossifrage\n') == (form == 'plain'))
                rows.append(dict(provider=provider, form=form, sample=sample,
                    source_array_hex=source.hex(), target_array_hex=target.hex(),
                    input_hex=data.hex(), expected_hex=expected.hex(), actual_hex=result.stdout.hex(),
                    stderr_hex=result.stderr.hex(), process=result.record, passed=passed))
    passed = len(rows) == 8 and all(r['passed'] for r in rows)
    print(json.dumps(dict(status='pass' if passed else 'incomplete', python=sys.version, results=rows), indent=2))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
