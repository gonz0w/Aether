#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Checked descriptor fallback comparison on the pinned Linux reference SDK."""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tarfile
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
REF=ROOT/'experiments/musl-reference'
IMAGE='8d0dff22866c67ea5de1d66ff04a54f17e610a11e3a5c970414820663c7649a4'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(ok,msg):
    if not ok:raise RuntimeError(msg)
tools=json.loads((REF/'tools.lock.json').read_text())['tools']
for key,t in tools.items():require(sha(Path(t['path']))==t['sha256'],'tool changed: '+key)
sdk=Path(json.loads((REF/'evidence.json').read_text())['output'])
paths=list((sdk/'stage').rglob('*'))
require(not any(p.is_symlink() for p in paths),'SDK symlink')
inventory={str(p.relative_to(sdk)):sha(p) for p in paths if p.is_file()}
require(inventory==json.loads((REF/'large-tls-evidence.json').read_text())['sdk_inputs'],'SDK changed')
archive=ROOT/'build/musl-audit/musl-1.2.6.tar.gz'
require(sha(archive)=='d585fd3b613c66151fc3249e8ed44f77020cb5e6c1e635a616d3f9f82460512a','musl archive changed')
out=Path(tempfile.mkdtemp(prefix='descriptor-fallback-',dir=ROOT/'build'))
print(out,flush=True)
with tarfile.open(archive) as t:t.extractall(out,filter='data')
src=out/'musl-1.2.6'
(out/'tmp').mkdir()
env={'PATH':'/usr/bin:/bin','LC_ALL':'C','TMPDIR':str(out/'tmp')}
commands=[]
def run(name,args,status=0):
    r=subprocess.run(args,env=env,capture_output=True,timeout=45)
    (out/(name+'.stdout')).write_bytes(r.stdout);(out/(name+'.trace')).write_bytes(r.stderr)
    commands.append({'name':name,'argv':args,'expected_exit':status,'exit':r.returncode})
    (out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
    require(r.returncode==status,name+': unexpected status '+str(r.returncode)+'; '+str(out))
    return r
cc=[tools['clang']['path'],'--no-default-config','--target=x86_64-linux-musl','--sysroot='+str(sdk/'stage'),'-nostdinc','-isystem',str(sdk/'stage/usr/include')]
run('compile-probe',cc+['-std=c11','-O2','-Wall','-Wextra','-Werror','-fstack-protector-strong','-c',str(HERE/'probe.c'),'-o',str(out/'probe.o')])
lock=json.loads((HERE/'patch.lock.json').read_text())
require(sha(HERE/'checked.patch')==lock['sha256'],'patch changed')
original={p:(src/p).read_bytes() for p in lock['files']}
for p,h in lock['files'].items():require(sha(src/p)==h['before'],'source anchor changed: '+p)
run('patch',['/usr/bin/patch','--batch','-p1','-d',str(src),'-i',str(HERE/'checked.patch')])
checked={p:(src/p).read_bytes() for p in lock['files']}
for p,h in lock['files'].items():require(sha(src/p)==h['after'],'patched source changed: '+p)
injection='''
/* Test-only interception, added identically to baseline and checked objects. */
extern long test_raw(long, long, long, long);
#undef __syscall1
#undef __syscall2
#undef __syscall3
#define __syscall1(n,a) test_raw(n,(long)(a),0,0)
#define __syscall2(n,a,b) test_raw(n,(long)(a),(long)(b),0)
#define __syscall3(n,a,b,c) test_raw(n,(long)(a),(long)(b),(long)(c))
'''
flags=['-std=c99','-O2','-nostdinc','-ffreestanding','-fno-stack-protector','-fno-strict-aliasing','-D_XOPEN_SOURCE=700']
for inc in [src/'arch/x86_64',src/'arch/generic',src/'src/include',src/'src/internal',sdk/'stage/usr/include',src/'include']:flags+=['-I',str(inc)]
lib=sdk/'stage/usr/lib';injected={}
for variant,texts in [('baseline',original),('checked',checked)]:
    objs=[]
    for name,raw in texts.items():
        text=raw.decode();anchor='#include "syscall.h"\n'
        require(text.count(anchor)==1,'injection anchor')
        (src/name).write_text(text.replace(anchor,anchor+injection))
        obj=out/(variant+'-'+Path(name).stem+'.o');objs.append(str(obj))
        injected[variant+'/'+name]=sha(src/name)
        run(variant+'-'+Path(name).stem,cc+flags+['-c',str(src/name),'-o',str(obj)])
    elf=out/(variant+'.elf')
    run(variant+'-link',cc+['--ld-path='+tools['lld']['path'],'-nostdlib','-static','-Wl,-z,noexecstack','-Wl,--no-undefined',str(lib/'crt1.o'),str(lib/'crti.o'),str(out/'probe.o')]+objs+[str(lib/'libc.a'),str(lib/'crtn.o'),'-o',str(elf)])
    require(not run(variant+'-undefined',[tools['nm']['path'],'--undefined-only','--extern-only',str(elf)]).stdout.strip(),'undefined symbols')
    run(variant+'-headers',[tools['readelf']['path'],'-h','-l',str(elf)])
    data=elf.read_bytes()
    require(data[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<HH',data,16)==(2,62),'ELF target')
    off=struct.unpack_from('<Q',data,32)[0];size,count=struct.unpack_from('<HH',data,54)
    h=[struct.unpack_from('<IIQQQQQQ',data,off+i*size) for i in range(count)]
    require(not any(x[0] in (2,3) or (x[0]==1 and x[1]&3==3) for x in h),'dynamic or W+X')
    require(any(x[0]==0x6474e551 and not x[1]&1 for x in h),'NX stack')
base=['/opt/homebrew/bin/podman','run','--rm','--pull=never','--network=none','--read-only','--cap-drop=all','--security-opt=no-new-privileges','--user=65534:65534','--memory=512m','--pids-limit=32','--mount','type=bind,src='+str(out)+',dst=/inputs,ro=true','--entrypoint=/usr/bin/qemu-x86_64',IMAGE,'-strace']
# kind, emulate missing atomic operation, setter ordinal to deny, raw errno.
cases=[('dup-fallback-ok','dup',1,0,13),('dup-eacces','dup',1,1,13),('dup-enosys','dup',1,1,38),
 ('pipe-fallback-ok','pipe',1,0,13),('pipe-cloexec-first','pipe',1,1,13),('pipe-cloexec-second','pipe',1,2,13),
 ('pipe-nonblock-first','pipe',1,3,13),('pipe-nonblock-second','pipe',1,4,13),
 ('dup-atomic-extra-setter-denied','dup',0,1,13),('pipe-atomic','pipe',0,0,13)]
results=[]
for variant in ['baseline','checked']:
    for label,kind,fallback,deny,error in cases:
        status=20 if variant=='baseline' and fallback and deny else 0
        name=variant+'-'+label
        r=run(name,base+['/inputs/'+variant+'.elf',str(int(variant=='checked')),kind,str(fallback),str(deny),str(error)],status)
        require(not r.stdout and b'exit_group(' in r.stderr,name+': unexpected output or missing guest exit')
        results.append({'case':name,'exit':status,'injection':{'atomic_unsupported':bool(fallback),'setter_ordinal':deny,'errno':error if deny else None},'trace_sha256':sha(out/(name+'.trace')),'stdout_sha256':sha(out/(name+'.stdout'))})
e={'schema':'aether-userland.descriptor-fallback.v1','scope':'Linux-emulated replacement-object syscall injection; single-thread checked fallback comparison only; no native adoption or atomicity proof','output':str(out),'source_sha256':sha(HERE/'probe.c'),'script_sha256':sha(Path(__file__)),'tools_lock_sha256':sha(REF/'tools.lock.json'),'sdk_inputs':inventory,'archive_sha256':sha(archive),'patch_lock_sha256':sha(HERE/'patch.lock.json'),'patch_sha256':sha(HERE/'checked.patch'),'injected_source_hashes':injected,'injection_text':injection,'image_id':IMAGE,'environment':env,'elf_sha256':{v:sha(out/(v+'.elf')) for v in ['baseline','checked']},'commands':commands,'results':results}
(out/'evidence.json').write_text(json.dumps(e,indent=2)+'\n')
print('Twenty descriptor fallback outcomes passed: '+str(out))
