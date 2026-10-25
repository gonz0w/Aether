#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Separate Linux PTY recovery from upstream natural restoration."""
import fcntl
import json
import os
from pathlib import Path
import pty
import runpy
import struct
import sys
import termios
import time


def state(fd):
    return termios.tcgetattr(fd), fcntl.ioctl(fd, termios.TIOCGWINSZ, bytes(8))


def restore(fd, saved):
    termios.tcsetattr(fd, termios.TCSANOW, saved[0])
    fcntl.ioctl(fd, termios.TIOCSWINSZ, saved[1])


def child(mode, device):
    fd = os.open(device, os.O_RDWR)
    os.dup2(fd, 0)
    if fd != 0:
        os.close(fd)
    fcntl.ioctl(0, termios.TIOCSCTTY, 0)
    if mode == 'main':
        os.execve('/bin/bash', ['/bin/bash', '-c',
            'exec 9>&2; exec /bin/bash /inputs/tests/stty/stty.sh'], dict(os.environ))
    changed = termios.tcgetattr(0)
    changed[3] ^= termios.ECHO
    termios.tcsetattr(0, termios.TCSANOW, changed)
    fcntl.ioctl(0, termios.TIOCSWINSZ, struct.pack('HHHH', 31, 97, 0, 0))
    print('mutation-complete', flush=True)
    if mode == 'timeout':
        time.sleep(60)
    return 23


def main():
    process = runpy.run_path('/inputs/process.py')
    work = Path('/scratch')
    env = process['clean_env'](work)
    env.update(PATH='/inputs/src:/usr/bin:/bin', srcdir='/inputs', abs_top_srcdir='/inputs',
               built_programs='tr stty', RUN_EXPENSIVE_TESTS='yes', VERBOSE='yes',
               SHELL='/bin/bash', PATH_SEPARATOR=':')
    report = dict(status='incomplete', python=sys.version, results=[])
    try:
        for case in ['main', 'exit23', 'timeout', 'omitted-recovery']:
            master, slave = pty.openpty()
            row = dict(case=case, status='incomplete')
            report['results'].append(row)
            saved = None
            try:
                fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack('HHHH', 24, 80, 0, 0))
                saved = state(slave)
                result = process['run'](['/usr/local/bin/python3', '/inputs/check-recovery.py',
                    '--child', case, os.ttyname(slave)], cwd=work, env=env, work=work,
                    label=case, timeout=2 if case == 'timeout' else 45, file_limit=1024**2)
                natural = state(slave)
                row.update(process=result.record, stdout=result.stdout.decode(errors='replace'),
                           stderr=result.stderr.decode(errors='replace'), before=repr(saved),
                           natural=repr(natural), naturally_restored=natural == saved)
                if result.record['cleanup'] != 'complete':
                    raise RuntimeError('process cleanup unresolved')
                if case == 'timeout':
                    expected = (result.record['failure'] == 'timeout' and not result.record['complete']
                                and result.returncode == -9 and 'mutation-complete' in row['stdout'])
                else:
                    expected = result.record['complete'] and result.returncode == (0 if case == 'main' else 23)
                if not expected or natural == saved:
                    raise RuntimeError('outcome or natural state mismatch')
                if case != 'omitted-recovery':
                    restore(slave, saved)
                row['explicit_restored'] = state(slave) == saved
                row['explicit_state'] = repr(state(slave))
                if row['explicit_restored'] != (case != 'omitted-recovery'):
                    raise RuntimeError('recovery oracle mismatch')
                row['status'] = 'pass'
            finally:
                try:
                    if saved is not None:
                        restore(slave, saved)
                        row['finally_restored'] = state(slave) == saved
                        if not row['finally_restored']:
                            raise RuntimeError('final recovery mismatch')
                finally:
                    os.close(slave)
                    os.close(master)
                    row['endpoints_closed'] = True
        report['status'] = 'pass'
    except (OSError, ValueError, RuntimeError) as error:
        report['error'] = str(error)
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    if sys.argv[1:2] == ['--child']:
        raise SystemExit(child(sys.argv[2], sys.argv[3]))
    raise SystemExit(main())
