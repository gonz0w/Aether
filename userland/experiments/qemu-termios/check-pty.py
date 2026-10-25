#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Linux guest PTY checks; baseline loss is an explicit negative control."""
import hashlib
import json
from pathlib import Path
import pty
import runpy
import sys
import termios
import os

INPUTS = Path('/inputs')
WORK = Path('/scratch')
PROCESS = runpy.run_path(str(INPUTS / 'process.py'))
CMSPAR = 0x40000000  # Linux generic termbits, used by both selected architectures.


def main():
    report = {'status': 'incomplete', 'python': sys.version, 'results': []}
    providers = [('baseline', [str(INPUTS / 'baseline'), str(INPUTS / 'stty')]),
                 ('patched', [str(INPUTS / 'patched'), str(INPUTS / 'stty')]),
                 ('image', ['/usr/bin/stty'])]
    notice = Path('/usr/share/doc/gcc-14-base/copyright').read_text()
    report['libatomic_notice_from_image'] = notice
    report['image_stty_sha256'] = hashlib.sha256(Path('/usr/bin/stty').read_bytes()).hexdigest()
    try:
        for provider, prefix in providers:
            for case in ('set', 'seeded-read', 'clear', 'partial-failure'):
                master, slave = pty.openpty()
                before = termios.tcgetattr(slave)
                row = {'provider': provider, 'case': case, 'status': 'incomplete'}
                report['results'].append(row)
                try:
                    if case in ('seeded-read', 'clear'):
                        seeded = termios.tcgetattr(slave)
                        seeded[2] |= CMSPAR
                        termios.tcsetattr(slave, termios.TCSANOW, seeded)
                        if not termios.tcgetattr(slave)[2] & CMSPAR:
                            raise RuntimeError('host PTY seed did not persist')
                    options = {'set': ['cmspar'], 'seeded-read': ['-a'],
                               'clear': ['-cmspar'],
                               'partial-failure': ['cmspar', 'parenb']}[case]
                    env = PROCESS['clean_env'](WORK)
                    if provider != 'image':
                        env['LD_LIBRARY_PATH'] = '/inputs/lib'
                    result = PROCESS['run'](prefix + ['-F', os.ttyname(slave)] + options,
                                           cwd=WORK, env=env,
                                           work=WORK, label=provider + '-' + case,
                                           timeout=10, file_limit=1024**2)
                    after = termios.tcgetattr(slave)
                    row.update(process=result.record, stdout=result.stdout.decode(errors='replace'),
                               stderr=result.stderr.decode(errors='replace'),
                               before=repr(before), after=repr(after),
                               cmspar=bool(after[2] & CMSPAR))
                    expected_exit = int(case == 'partial-failure' or
                                        (case == 'set' and provider == 'baseline'))
                    if not result.record['complete'] or result.returncode != expected_exit:
                        raise RuntimeError('wrong operation outcome')
                    if case == 'seeded-read':
                        token = '-cmspar' if provider == 'baseline' else 'cmspar'
                        if token not in row['stdout'].replace(';', ' ').split():
                            raise RuntimeError('wrong CMSPAR readback')
                        expected_bit = True
                    else:
                        expected_bit = case != 'clear' and provider != 'baseline'
                    if row['cmspar'] != expected_bit:
                        raise RuntimeError('wrong host CMSPAR state')
                    if case == 'partial-failure':
                        if after[2] & termios.PARENB:
                            raise RuntimeError('PTY unexpectedly accepted PARENB')
                        if 'unable to perform all requested operations' not in row['stderr']:
                            raise RuntimeError('wrong partial-failure diagnostic')
                    row['status'] = 'pass'
                finally:
                    try:
                        termios.tcsetattr(slave, termios.TCSANOW, before)
                        row['restored'] = termios.tcgetattr(slave) == before
                        if not row['restored']:
                            raise RuntimeError('PTY restoration mismatch')
                    finally:
                        os.close(slave)
                        os.close(master)
        report['status'] = 'pass'
    except (OSError, ValueError, RuntimeError) as error:
        report['error'] = str(error)
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
