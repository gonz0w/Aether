#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Synthetic profile grammar/policy controls; no SDK package acceptance."""
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile

repo = Path(__file__).resolve().parents[1]
def sha(data):
    return hashlib.sha256(data).hexdigest()

with tempfile.TemporaryDirectory(prefix='pkg-sdk-profile-cases-') as directory:
    root = Path(directory)
    temporary = root/'scratch'
    temporary.mkdir()
    target, build, native = (root/name for name in ('target.kv', 'build receipt', 'native receipt'))
    build.write_bytes(b'synthetic build receipt\n')
    native.write_bytes(b'synthetic native receipt\n')
    rows = ['format=cross-sdk-target-v1', 'role=build-inputs-only',
            'build_os=FixtureOS', 'build_arch=fixture64', 'compiler_target=fixture-none',
            'build_receipt_sha256='+sha(build.read_bytes()),
            'native_profile_sha256='+sha(native.read_bytes()), 'modes=recorded-0000-0777']
    good = ('\n'.join(rows)+'\n').encode()
    original_pin = sha(good)
    count = 0
    def check(label, data=good, status=1, pin=None, build_path=build, native_path=native, env=None):
        global count
        target.write_bytes(data)
        before = {p.name:p.read_bytes() for p in (target, build, native)}
        result = subprocess.run(['sh', str(repo/'mk/sdk-profile.sh'), str(target),
                                 sha(data) if pin is None else pin, str(build_path), str(native_path)],
                                env=dict(os.environ, TMPDIR=str(temporary), **(env or {})),
                                capture_output=True, timeout=10)
        assert result.returncode == status, (label, result.returncode, result.stderr)
        assert result.stdout == b'', (label, result.stdout)
        if status == 1:
            assert result.stderr.startswith(b'sdk-profile-error:'), (label, result.stderr)
        assert before == {p.name:p.read_bytes() for p in (target, build, native)}, label
        assert not list(temporary.iterdir()), label
        count += 1
    check('valid', status=0)
    for i in range(8):
        check(f'missing-{i}', ('\n'.join(rows[:i]+rows[i+1:])+'\n').encode())
        check(f'duplicate-{i}', ('\n'.join(rows[:i]+[rows[i]]+rows[i:])+'\n').encode())
        changed = rows.copy(); changed[i] = 'unknown='+changed[i].split('=',1)[1]
        check(f'unknown-{i}', ('\n'.join(changed)+'\n').encode())
    for i in range(7):
        changed=rows.copy(); changed[i],changed[i+1]=changed[i+1],changed[i]
        check(f'reorder-{i}', ('\n'.join(changed)+'\n').encode())
    for label, data in [('empty',b''),('no-lf',good[:-1]),('crlf',good.replace(b'\n',b'\r\n')),
                        ('nul',good.replace(b'FixtureOS',b'Fixture\x00OS')),
                        ('nonascii',good.replace(b'FixtureOS',b'Fixture\xffOS')),
                        ('blank',good+b'\n'),('oversize',b'x'*4097),
                        ('4096-invalid',b'x'*4096),('comment',good+b'# ignored\n')]:
        check(label,data)
    for index,value in [(0,'cross-sdk-target-v2'),(1,'native-executable'),(2,''),
                        (2,'x'*129),(2,'has space'),(3,'_invalid'),(4,'target/other'),
                        (5,'a'*63),(5,'A'*64),(6,'g'*64),(7,'normalized-0644')]:
        changed=rows.copy(); changed[index]=rows[index].split('=',1)[0]+'='+value
        check(f'value-{index}-{len(value)}', ('\n'.join(changed)+'\n').encode())
    changed=rows.copy(); changed[2]='build_os='+'x'*128
    check('max-identity', ('\n'.join(changed)+'\n').encode(),status=0)
    check('wrong-pin',pin='0'*64)
    check('native-hash-is-not-target-pin',pin=sha(native.read_bytes()))
    build.write_bytes(b'substituted build receipt\n')
    check('receipt-bytes')
    changed=good.replace(rows[5].encode(),('build_receipt_sha256='+sha(build.read_bytes())).encode())
    check('self-consistent-substitution-old-policy',changed,pin=original_pin)
    check('explicitly-selected-new-profile',changed,status=0)
    build.write_bytes(b'synthetic build receipt\n')
    native.write_bytes(b'changed native\n'); check('native-bytes')
    native.write_bytes(b'synthetic native receipt\n')
    check('bad-pin-syntax',pin='bad',status=64)
    check('missing-receipt',build_path=root/'missing')
    check('directory-receipt',build_path=temporary)
    link=root/'link'; link.symlink_to(build); check('symlink-receipt',build_path=link); link.unlink()
    os.link(build,link); check('hardlink-receipt'); link.unlink()
    # Force a selected hash provider to fail; no fallback to another provider.
    tools=root/'tools'; tools.mkdir()
    provider=tools/'sha256sum'; provider.write_text('#!/bin/sh\nexit 7\n'); provider.chmod(0o700)
    check('hash-provider-failure',env={'PATH':str(tools)+os.pathsep+os.environ['PATH']})
print(f'PASS: {count} SDK profile grammar, pin, receipt and preservation controls (synthetic)')
