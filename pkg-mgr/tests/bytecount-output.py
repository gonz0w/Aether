#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Exercise a built or transported host command with exact byte/status checks."""
import os
from pathlib import Path
import subprocess
import sys
binary = str(Path(sys.argv[1]).resolve())
def run(args, data=b'', locale='C'):
    env = dict(os.environ); env.pop('LC_ALL', None)
    if locale is not None: env['LC_ALL'] = locale
    return subprocess.run([binary, *args], input=data, capture_output=True, env=env, timeout=10)
for data in (b'', b'abcdef', bytes(range(256))*13, b'x'*65537):
    r=run(['--decimal'],data)
    assert (r.returncode,r.stdout,r.stderr)==(0,str(len(data)).encode()+b'\n',b'')
for args,locale in (([], 'C'), (['--wrong'],'C'), (['--decimal','extra'],'C'), (['--decimal'],None), (['--decimal'],'invalid')):
    r=run(args,locale=locale)
    assert r.returncode==64 and r.stdout==b'' and r.stderr==b'bytecount: expected --decimal and LC_ALL=C\n'
r=run(['--version']);assert (r.returncode,r.stdout,r.stderr)==(0,b'bytecount 0.1\n',b'')
r=run(['--help']);assert r.returncode==0 and b'Usage: bytecount --decimal\n' in r.stdout and not r.stderr
print('PASS: eleven host bytecount output/status cases')
