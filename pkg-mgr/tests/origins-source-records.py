#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Independent subprocess oracles for the OC-H2 read-only host inspector."""
import copy
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[1]
ROOT = Path(tempfile.mkdtemp(prefix='.pkg-mgr-live-origins-records-', dir=REPO)).resolve()
print('origins-records: retained_root=' + str(ROOT), flush=True)
INSPECTOR = REPO / 'tests/origins_source_record.py'
FIXTURE = REPO / 'fixtures/origins-records/source.json'
RESULTS = []


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + chr(10)).encode('ascii')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    original = FIXTURE.read_bytes()
    baseline = json.loads(original)
    fixture_pin = (FIXTURE.parent / 'source.sha256').read_text().strip()
    require(hashlib.sha256(original).hexdigest() == fixture_pin, 'fixture pin changed')
    sentinel = ROOT / 'package-state-sentinel'
    sentinel.write_bytes(b'unchanged package/world/trust test sentinel')
    sentinel_hash = hashlib.sha256(sentinel.read_bytes()).hexdigest()
    expected = json.loads((FIXTURE.parent / 'expected.json').read_text())
    cases = [('canonical', original, None, None, expected)]

    def mutation(name, change, code='format-invalid', summary=None):
        value = copy.deepcopy(baseline)
        change(value)
        cases.append((name, encode(value), code, None, summary))

    for field in baseline:
        mutation('missing-' + field, lambda r, f=field: r.pop(f))
    mutation('unknown-field', lambda r: r.update(extra='inert'))
    mutation('unknown-schema', lambda r: r.update(schema='origins-source-v9'), 'unsupported-schema')
    mutation('unknown-feature', lambda r: r.update(required_features=['network-build']), 'unsupported-feature')
    for name, field, value in [('flat-package','package','zlib'), ('uppercase-package','package','Aether/zlib'),
                                ('negative-revision','revision',-1), ('zero-revision','revision',0),
                                ('overflow-integer','revision',9007199254740992),
                                ('float','revision',1.0), ('boolean','revision',True),
                                ('null','sdk',None), ('empty-version','version',''),
                                ('version-too-long','version','x'*129), ('control-text','version',chr(27))]:
        mutation(name, lambda r, f=field, v=value: r.update({f:v}))
    for name, value in [('absolute-path','/source'), ('dot-path','a/../source'),
                        ('uppercase-path','Makefile'), ('backslash-path','a'+chr(92)+'b'),
                        ('empty-component','a//b'), ('component-limit','a'*65)]:
        mutation(name, lambda r,v=value: r['inputs'][0].update(path=v))
    mutation('duplicate-input', lambda r: r['inputs'].append(copy.deepcopy(r['inputs'][0])), 'order-or-duplicate')
    mutation('input-order', lambda r: r['inputs'].reverse(), 'order-or-duplicate')
    def prefix(r):
        r['inputs'][0]['path']='a'
        r['inputs'][1]['path']='a/b'
        r['recipe']='a'
    mutation('path-prefix', prefix, 'path-conflict')
    mutation('missing-source', lambda r: r['inputs'][1].update(kind='data'))
    mutation('second-recipe', lambda r: r['inputs'][1].update(kind='recipe'))
    mutation('unknown-input-field', lambda r: r['inputs'][0].update(exec='touch forbidden'))
    mutation('wrong-recipe-kind', lambda r: r.update(recipe='source.tar'))
    mutation('missing-patch-reference', lambda r: r.update(patches=['missing.patch']))
    mutation('unlisted-helper', lambda r: r['inputs'][1].update(kind='helper'))
    mutation('invalid-kind-type', lambda r: r['inputs'][0].update(kind=[]))
    mutation('origin-too-long', lambda r: r['inputs'][0].update(origin='x'*4097))
    mutation('size-negative', lambda r: r['sdk'].update(size=-1))
    mutation('size-too-large', lambda r: r['sdk'].update(size=1073741825))
    mutation('uppercase-digest', lambda r: r['sdk'].update(sha256='A'*64))
    mutation('unknown-ref-key', lambda r: r['sdk'].update(url='https://invalid.example'))
    mutation('same-hash-size-conflict', lambda r: r['sdk'].update(sha256='a'*64,size=99), 'reference-conflict')
    mutation('duplicate-option', lambda r: r.update(options=[{'name':'x','value':''}]*2), 'order-or-duplicate')
    mutation('option-too-long', lambda r: r.update(options=[{'name':'x','value':'a'*1025}]))
    mutation('empty-licenses', lambda r: r.update(licenses=[]))
    mutation('duplicate-evidence', lambda r: r['evidence'].append(copy.deepcopy(r['evidence'][0])), 'order-or-duplicate')
    mutation('too-many-options', lambda r: r.update(options=[{'name':'x'+str(n),'value':''} for n in range(257)]))
    mutation('too-many-dependencies', lambda r: r.update(dependencies=[{}]*1025))
    mutation('too-many-inputs', lambda r: r.update(inputs=[{}]*4097))
    mutation('empty-inputs', lambda r: r.update(inputs=[]))
    mutation('too-many-evidence', lambda r: r.update(evidence=[{}]*257))
    def patch_order(r):
        for name, kind in [('fix-a.patch','patch'),('fix-b.patch','patch'),('helper.sh','helper')]:
            item = copy.deepcopy(r['inputs'][0])
            item.update(path=name, kind=kind)
            r['inputs'].append(item)
        r['inputs'].sort(key=lambda item: item['path'])
        r['patches']=['fix-b.patch','fix-a.patch']
        r['helpers']=['helper.sh']
    mutation('ordered-patches-and-helper', patch_order, None, dict(expected,input_count=5))
    dependency={'package':'aether/dep','record':{'sha256':'f'*64,'size':12},'role':'build'}
    mutation('unknown-role', lambda r: r.update(dependencies=[dict(dependency,role='execute')]))
    mutation('dual-role-same-package', lambda r: r.update(dependencies=[dependency,dict(dependency,role='target')]), 'order-or-duplicate')
    dependency_summary=dict(expected, dependency_count=1, referenced_object_count=6)
    mutation('unresolved-dependency', lambda r: r.update(dependencies=[dependency]), None, dependency_summary)
    mutation('large-sdk-inspection', lambda r: r['sdk'].update(size=1073741824), None,
             dict(expected,byte_handoff='over-16-mib'))
    mutation('transfer-exact-limit', lambda r: r['sdk'].update(size=16777216), None, expected)
    mutation('transfer-over-limit', lambda r: r['sdk'].update(size=16777217), None,
             dict(expected,byte_handoff='over-16-mib'))
    mutation('string-brackets', lambda r: r.update(options=[{'name':'custom','value':'['*40+']'*40}]), None, expected)
    mutation('string-escapes', lambda r: r.update(options=[{'name':'custom','value':chr(34)+chr(92)}]), None, expected)
    marker=ROOT/'must-not-exist'
    hostile='$(touch '+str(marker)+'); `touch '+str(marker)+'`'
    mutation('inert-shell-origin', lambda r: r['inputs'][0].update(origin=hostile), None, expected)
    mutation('inert-shell-option', lambda r: r.update(options=[{'name':'custom','value':hostile}]), None, expected)
    # Hand-authored byte mutations exercise the wire representation, not just dict shape.
    cases += [
        ('wrong-pin',original,'identity-mismatch','0'*64,None),
        ('invalid-pin',original,'pin-invalid','BAD',None),
        ('duplicate-root-key',b'{"schema":"origins-source-v1",'+original[1:],'duplicate-key',None,None),
        ('duplicate-nested-key',original.replace(b'"size":1',b'"size":1,"size":1',1),'duplicate-key',None,None),
        ('pretty-json',(json.dumps(baseline,indent=2)+chr(10)).encode(),'noncanonical',None,None),
        ('alternate-unicode-escape',original.replace(b'aether',bytes([92])+b'u0061ether'),'noncanonical',None,None),
        ('missing-lf',original[:-1],'noncanonical',None,None),
        ('extra-lf',original+bytes([10]),'noncanonical',None,None),
        ('nonascii',original+bytes([255]),'format-invalid',None,None),
        ('nul',original+bytes([0]),'format-invalid',None,None),
        ('trailing-json',original+b'{}','format-invalid',None,None),
        ('nan',original.replace(b'"revision":1',b'"revision":NaN'),'format-invalid',None,None),
        ('huge-number',original.replace(b'"revision":1',b'"revision":'+b'9'*10000),'format-invalid',None,None),
        ('leading-zero',original.replace(b'"revision":1',b'"revision":01'),'format-invalid',None,None),
        ('depth-eight',b'['*8+b'0'+b']'*8+bytes([10]),'format-invalid',None,None),
        ('depth-nine',b'['*9+b'0'+b']'*9+bytes([10]),'limit-exceeded',None,None),
        ('size-exact-limit',b' '*1048576,'format-invalid',None,None),
        ('size-over-limit',b' '*1048577,'limit-exceeded',None,None),
    ]
    for name, raw, code, pin, summary in cases:
        path=ROOT/(name+'.json')
        path.write_bytes(raw)
        pin=pin or hashlib.sha256(raw).hexdigest()
        argv=[sys.executable,'-B',str(INSPECTOR),str(path),pin]
        result=subprocess.run(argv,capture_output=True,timeout=5,cwd=ROOT,
                              env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',LC_ALL='C'))
        (ROOT/(name+'.stdout')).write_bytes(result.stdout)
        (ROOT/(name+'.stderr')).write_bytes(result.stderr)
        ok=result.returncode==(2 if code else 0)
        if code:
            expected_error=('[BLOCKED] PKG-ORIGINS-'+code.upper()+': Record inspection rejected.'+chr(10)).encode()
            ok=ok and result.stdout==b'' and result.stderr==expected_error
        else:
            wanted=dict(summary,record_sha256=pin)
            ok=ok and result.stdout==encode(wanted) and result.stderr==b''
        unchanged=path.read_bytes()==raw and hashlib.sha256(sentinel.read_bytes()).hexdigest()==sentinel_hash
        unchanged=unchanged and not marker.exists() and not (ROOT/'trust').exists()
        RESULTS.append({'case':name,'expected':code or 'inspection-only','exit':result.returncode,
                        'result':'pass' if ok and unchanged else 'fail','command':argv,
                        'input_sha256':hashlib.sha256(raw).hexdigest(),'unchanged':unchanged})
        require(ok and unchanged, 'case failed: '+name)
    # File boundary controls run the actual CLI, never block on a FIFO.
    link=ROOT/'linked-record'; link.symlink_to(FIXTURE)
    fifo=ROOT/'fifo-record'; os.mkfifo(fifo,0o600)
    for name,path,exit_code,code in [('missing',ROOT/'absent',1,'IO-ERROR'),
                                   ('symlink',link,1,'IO-ERROR'),
                                   ('fifo',fifo,2,'FILE-TYPE-INVALID')]:
        r=subprocess.run([sys.executable,'-B',str(INSPECTOR),str(path),fixture_pin],capture_output=True,timeout=5)
        (ROOT/(name+'.stdout')).write_bytes(r.stdout); (ROOT/(name+'.stderr')).write_bytes(r.stderr)
        ok=r.returncode==exit_code and not r.stdout and ('PKG-ORIGINS-'+code+':').encode() in r.stderr
        RESULTS.append({'case':name,'result':'pass' if ok else 'fail','exit':r.returncode})
        require(ok,'file boundary failed: '+name)
    read_fd, write_fd = os.pipe()
    os.close(read_fd)
    try:
        r = subprocess.run([sys.executable, '-B', str(INSPECTOR), str(FIXTURE), fixture_pin],
                           stdout=write_fd, stderr=subprocess.PIPE, timeout=5)
    finally:
        os.close(write_fd)
    (ROOT/'closed-output.stderr').write_bytes(r.stderr)
    ok = r.returncode == 1 and b'PKG-ORIGINS-IO-ERROR:' in r.stderr
    RESULTS.append({'case':'closed-output','result':'pass' if ok else 'fail','exit':r.returncode})
    require(ok, 'closed output must fail without a successful report')
    for option in ('--help','--version'):
        r=subprocess.run([sys.executable,'-B',str(INSPECTOR),option],capture_output=True,timeout=5)
        require(r.returncode==0 and r.stdout and not r.stderr, 'help/version failure')
    r=subprocess.run([sys.executable,'-B',str(INSPECTOR)],capture_output=True,timeout=5)
    require(r.returncode==64 and not r.stdout and b'PKG-ORIGINS-USAGE:' in r.stderr,'usage failure')
    print('PASS: '+str(len(RESULTS))+' source-record cases; help/version/usage; no execution or admission')


if __name__=='__main__':
    status=1
    try:
        main(); status=0
    except (ValueError,OSError,subprocess.SubprocessError) as error:
        print('FAIL: '+str(error),file=sys.stderr)
    finally:
        (ROOT/'result.json').write_text(json.dumps({'exit':status,'cases':RESULTS,
            'platform':platform.platform(),'python':sys.version,'inputs':{
                str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (INSPECTOR,Path(__file__).resolve(),FIXTURE)},
            'scope':'OC-H2 synthetic host record inspection only'},indent=2))
    sys.exit(status)
