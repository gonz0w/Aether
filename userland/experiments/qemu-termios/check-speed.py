#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Measure static stty cfsetispeed failure and pass-through on owned PTYs."""
import json
import os
from pathlib import Path
import pty
import runpy
import sys
import termios


def main():
    process = runpy.run_path('/inputs/process.py')
    work = Path('/scratch')
    env = process['clean_env'](work)
    env['LD_LIBRARY_PATH'] = '/inputs/lib'
    report = dict(status='incomplete', python=sys.version, results=[])
    try:
        for mode in ['baseline', 'failure', 'passthrough']:
            master, slave = pty.openpty()
            row = dict(mode=mode, passed=False)
            report['results'].append(row)
            before = termios.tcgetattr(slave)
            try:
                result = process['run'](['/inputs/patched', '/inputs/speed/' + mode + '/stty',
                    '-F', os.ttyname(slave), 'ispeed', '9600'], cwd=work, env=env,
                    work=work, label=mode, timeout=10, file_limit=1024**2)
                after = termios.tcgetattr(slave)
                marker = b'speed-wrapper-called\n'
                expected_stderr = (b'' if mode == 'baseline' else marker * (2 if mode == 'passthrough' else 1))
                if mode == 'failure':
                    expected_stderr += b"stty: unsupported ispeed '9600'\n"
                row.update(process=result.record, stdout_hex=result.stdout.hex(),
                    stderr=result.stderr.decode(errors='replace'), before=repr(before), after=repr(after))
                row['passed'] = (result.record['complete'] and result.returncode == (1 if mode == 'failure' else 0)
                    and result.stdout == b'' and result.stderr == expected_stderr
                    and ((after == before) == (mode == 'failure')))
            finally:
                try:
                    termios.tcsetattr(slave, termios.TCSANOW, before)
                    row['restored'] = termios.tcgetattr(slave) == before
                finally:
                    os.close(slave)
                    os.close(master)
                    row['endpoints_closed'] = True
        report['status'] = 'pass' if all(r['passed'] and r['restored'] for r in report['results']) else 'incomplete'
    except (OSError, ValueError, RuntimeError) as error:
        report['error'] = str(error)
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
