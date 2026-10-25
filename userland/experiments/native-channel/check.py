#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Independent C consumers of kernel-owned bounded launch/channel v1."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--aether',type=Path,required=True)
p.add_argument('--sdk',type=Path,required=True)
a=p.parse_args();sdk=a.sdk.resolve()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(ok,msg):
    if not ok:raise RuntimeError(msg)
toollock=ROOT/'experiments/musl-reference/tools.lock.json'
tools=json.loads(toollock.read_text())['tools']
for name,t in tools.items():need(sha(Path(t['path']))==t['sha256'],'tool changed: '+name)
receipt=json.loads((sdk/'evidence.json').read_text())
need(sha(sdk/'stage/usr/lib/libc.a')==receipt['libc_archive_sha256'] and receipt['libc_patches'],'strict libc receipt mismatch')
paths=list((sdk/'stage').rglob('*'));need(not any(p.is_symlink() for p in paths),'SDK symlink')
inventory={str(p.relative_to(sdk)):sha(p) for p in paths if p.is_file()}
work=Path(tempfile.mkdtemp(prefix='native-channel-userland-',dir=ROOT/'build'));print(work,flush=True)
ignored={'.git','.zig-cache','zig-out','__pycache__','.DS_Store'}
shutil.copytree(a.aether,work/'Aether',ignore=lambda path,names:set(names)&ignored)
kernel=work/'Aether'
sources={str(p.relative_to(kernel)):sha(p) for p in kernel.rglob('*') if p.is_file() and '.deps' not in p.relative_to(kernel).parts}
# Reject a copy assembled while its input source was changing.
for name,h in sources.items():need(sha(a.aether/name)==h,'kernel changed during snapshot: '+name)
local={str(p):sha(p) for p in HERE.iterdir() if p.is_file()}
report={'schema':'aether-userland.native-channel.v1','status':'incomplete','scope':'independent userland C consumers with kernel-owned conformance supervisor; no sys-init adoption, POSIX descriptors or shell','output':str(work),'kernel_source_root':str(a.aether.resolve()),'kernel_sources':sources,'local_sources':local,'sdk_inputs':inventory,'libc_receipt_sha256':sha(sdk/'evidence.json'),'tools_lock_sha256':sha(toollock),'tools':tools,'commands':[],'cases':[]}
def save():(work/'evidence.json').write_text(json.dumps(report,indent=2)+'\n')
def run(label,cmd):
    r=subprocess.run(cmd,cwd=kernel,capture_output=True,timeout=180)
    (work/(label+'.log')).write_bytes(r.stdout+r.stderr)
    report['commands'].append({'name':label,'argv':cmd,'cwd':str(kernel),'exit':r.returncode});save()
    need(r.returncode==0,label+' failed; '+str(work));return r
save()
try:
    run('zig-version',['zig','version'])
    run('rust-version',['rustc','+1.98.0','--version'])
    run('qemu-version',['qemu-system-x86_64','--version'])
    report['boot_dependency_manifest']=json.loads((kernel/'.deps/manifest.json').read_text())
    cc=[tools['clang']['path'],'--no-default-config','--target=x86_64-linux-musl','--sysroot='+str(sdk/'empty-root')]
    flags=['-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-fstack-protector-strong','-nostdinc','-isystem',str(sdk/'stage/usr/include')]
    run('adapter',cc+flags+['-c',str(HERE/'channel.c'),'-o',str(work/'channel.o')])
    images={};lib=sdk/'stage/usr/lib'
    for name,options in [('writer',['-DWRITER']),('reader',[]),('corrupt',['-DWRITER','-DCORRUPT_STREAM'])]:
        obj=work/(name+'.o');elf=work/(name+'.elf')
        run(name+'-compile',cc+flags+options+['-c',str(HERE/'helper.c'),'-o',str(obj)])
        run(name+'-link',cc+['--ld-path='+tools['lld']['path'],'-nostdlib','-static','-Wl,-z,noexecstack','-Wl,--no-undefined','-Wl,-Map,'+str(work/(name+'.map')),str(lib/'crt1.o'),str(lib/'crti.o'),str(obj),str(work/'channel.o'),str(lib/'libc.a'),str(lib/'crtn.o'),'-o',str(elf)])
        need(not run(name+'-undefined',[tools['nm']['path'],'--undefined-only','--extern-only',str(elf)]).stdout.strip(),'undefined symbols')
        dis=run(name+'-disassembly',[tools['objdump']['path'],'-d',str(elf)]).stdout
        import re
        need(not re.search(rb'\bsyscall\b',dis),'Linux syscall instruction')
        run(name+'-headers',[tools['readelf']['path'],'-h','-l',str(elf)])
        images[name]=elf.read_bytes()
    original=kernel/'user/native-channel/supervisor.rs'
    mutation=work/'startup-mutation.rs'
    text=original.read_text()
    need(text.count('let b=args(')==1 and text.count('    if cfg!(stop_writer){')==1,'startup mutation anchors changed')
    mutated=text.replace('let b=args(','let mut b=args(').replace('    if cfg!(stop_writer){','    a.strings[0][0]=b\'x\'; b.strings[0][0]=b\'y\';\n    core::hint::black_box((&a, &b));\n    if cfg!(stop_writer){')
    mutation.write_text(mutated)
    report['startup_mutation']={'owner_source_sha256':sha(original),'mutated_source_sha256':sha(mutation),'scope':'test-only overwrite of source argv records after both successful launches; no supervisor policy change'}
    entropy=os.urandom(32)
    sys.path.insert(0,str(kernel/'scripts'))
    from native_smoke import run as smoke
    cases=[('positive',None,'writer',original),('writer-fault','fault_writer','writer',original),('writer-stop','stop_writer','writer',original),('wrong-count','bad_count','writer',original),('startup-copy',None,'writer',mutation),('wrong-pattern',None,'corrupt',original)]
    for name,cfg,writer,supervisor in cases:
        dest=work/name;dest.mkdir();raw=dest/'supervisor.raw'
        cmd=['rustc','+1.98.0','--edition=2024','--target=x86_64-unknown-none','-C','opt-level=2','-C','panic=abort','-C','relocation-model=static','-C','link-arg=-Tuser/native-launch/linker.ld','-C','link-arg=--oformat=binary',str(supervisor),'-o',str(raw)]
        if cfg:cmd+=['--cfg',cfg]
        run(name+'-supervisor',cmd);code=raw.read_bytes();need(0<len(code)<=4096,'supervisor bound')
        first,second=images[writer],images['reader']
        payload=dest/'native-c.bin';payload.write_bytes(struct.pack('<8sIIII',b'AENCH001',len(first),len(second),len(code),0)+entropy+first+second+code)
        run(name+'-kernel',['zig','build','-Dsmp=false','-Dnative-c-image='+str(payload),'-p',str(dest),'--cache-dir',str(kernel/'.zig-cache'),'--global-cache-dir',str(kernel/'.zig-cache/global')])
        negative=name in ('wrong-count','wrong-pattern')
        context=(b'NATIVE terminal slot=1 generation=1 kind=1 detail=103',b'NATIVE supervisor result=511 reclaimed=0') if negative else ()
        report['commands'].append({'name':name+'-smoke','function':'native_smoke.run','module_sha256':sources['scripts/native_smoke.py'],'image':str(dest/'aether.iso'),'expected_panic':'native C profile rejected' if negative else None,'panic_context':[x.decode() for x in context],'marker':'AETHER NATIVE CHANNEL PASS'})
        save()
        smoke(dest/'aether.iso',expected_panic=b'native C profile rejected' if negative else None,panic_context=context,marker=b'AETHER NATIVE CHANNEL PASS')
        lines=(dest/'native-serial.log').read_text().splitlines()
        if negative:need('AETHER NATIVE CHANNEL PASS' not in lines,'negative emitted pass')
        else:
            kind,detail=(2,134) if name=='writer-fault' else (3,143) if name=='writer-stop' else (1,17)
            expected=['NATIVE terminal slot=1 generation=1 kind=1 detail=29','NATIVE terminal slot=0 generation=2 kind=1 detail=33','NATIVE supervisor result=100 reclaimed=3']
            # Controlled stop is validated by the owner supervisor's terminal()
            # guard; this profile does not emit a producer terminal serial line.
            if name!='writer-stop':expected.append(f'NATIVE terminal slot=0 generation=1 kind={kind} detail={detail}')
            for line in expected:
                need(line in lines,'missing native outcome: '+line)
        report['cases'].append({'case':name,'result':'pass','negative':negative,'supervisor_sha256':sha(raw),'envelope_sha256':sha(payload),'iso_sha256':sha(dest/'aether.iso'),'serial_sha256':sha(dest/'native-serial.log')});save()
        print(name+': PASS',flush=True)
    need({str(p.relative_to(sdk)):sha(p) for p in (sdk/'stage').rglob('*') if p.is_file()}==inventory,'SDK changed during run')
    for name,h in sources.items():need(sha(kernel/name)==h,'isolated source changed: '+name)
    for name,h in local.items():need(sha(Path(name))==h,'consumer source changed during run')
    report['artifacts']={name:sha(work/(name+'.elf')) for name in images}
    report['status']='pass'
finally:save()
