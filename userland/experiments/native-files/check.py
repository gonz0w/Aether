#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Independent C client of the kernel-owned read-only file-service experiment."""
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
p.add_argument('--writable',action='store_true',help='test optional writable scratch; default remains read-only')
p.add_argument('--descriptors',action='store_true',help='test private single-client descriptor facade over writable service')
p.add_argument('--fd-failures',action='store_true',help='inject descriptor reply/close failures after real service completion')
p.add_argument('--libc-files',action='store_true',help='test bounded libc entry points using the descriptor facade')
p.add_argument('--stdio-files',action='store_true',help='test bounded buffered musl file I/O with native memory')
a=p.parse_args();sdk=a.sdk.resolve()
if a.stdio_files:a.libc_files=True
need_modes=sum([a.libc_files,a.fd_failures])
if need_modes>1:p.error('--libc-files and --fd-failures are mutually exclusive')
if a.libc_files:a.descriptors=True
if a.fd_failures:a.descriptors=True
if a.descriptors:a.writable=True
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
work=Path(tempfile.mkdtemp(prefix='native-stdio-files-' if a.stdio_files else 'native-libc-files-' if a.libc_files else 'native-fd-failures-' if a.fd_failures else 'native-fd-userland-' if a.descriptors else 'native-writable-userland-' if a.writable else 'native-files-userland-',dir=ROOT/'build'));print(work,flush=True)
ignored={'.git','.zig-cache','zig-out','__pycache__','.DS_Store'}
shutil.copytree(a.aether,work/'Aether',ignore=lambda path,names:set(names)&ignored)
kernel=work/'Aether'
sources={str(p.relative_to(kernel)):sha(p) for p in kernel.rglob('*') if p.is_file() and '.deps' not in p.relative_to(kernel).parts}
# Reject a copy assembled while its input source was changing.
for name,h in sources.items():need(sha(a.aether/name)==h,'kernel changed during snapshot: '+name)
local={str(p):sha(p) for p in HERE.iterdir() if p.is_file()}
local.update({str(p):sha(p) for p in (HERE.parent/'native-channel').glob('channel.*')})
if a.stdio_files:
    memory_source=HERE.parent/'native-c/native_memory.c'
    local[str(memory_source)]=sha(memory_source)
report={'schema':'aether-userland.native-files.v1','status':'incomplete','scope':'independent userland read-only file client with owner Rust service and conformance supervisor; no POSIX VFS, writable files or sys-init adoption','writable':a.writable,'output':str(work),'kernel_source_root':str(a.aether.resolve()),'kernel_sources':sources,'local_sources':local,'sdk_inputs':inventory,'libc_receipt_sha256':sha(sdk/'evidence.json'),'tools_lock_sha256':sha(toollock),'tools':tools,'commands':[],'cases':[]}
def save():(work/'evidence.json').write_text(json.dumps(report,indent=2)+'\n')
def run(label,cmd):
    r=subprocess.run(cmd,cwd=kernel,capture_output=True,timeout=180)
    (work/(label+'.log')).write_bytes(r.stdout+r.stderr)
    report['commands'].append({'name':label,'argv':cmd,'cwd':str(kernel),'exit':r.returncode});save()
    need(r.returncode==0,label+' failed; '+str(work));return r
if a.writable:report['scope']='independent bounded writable-scratch client with owner Rust service/supervisor; no POSIX VFS, persistence or sys-init adoption'
if a.descriptors:report['scope']='private four-descriptor/two-open-file single-thread userland facade; no libc interposition, fork/exec, signals or POSIX conformance'
report['descriptors']=a.descriptors
report['fd_failures']=a.fd_failures
report['libc_files']=a.libc_files
report['stdio_files']=a.stdio_files
if a.libc_files:report['scope']='single-thread pinned musl read/write/close/dup/dup2 hook plus bounded replacement open/lseek; fixture-created writable FD, no POSIX filesystem or native shell'
if a.fd_failures:report['injection_scope']='test-only consumer exchange wrapper after complete native service reply; discarded/replaced reply, no physical channel loss'
save()
try:
    for label,cmd in [('zig-version',['zig','version']),('rust-version',['rustc','+1.98.0','--version']),('qemu-version',['qemu-system-x86_64','--version'])]:run(label,cmd)
    report['boot_dependency_manifest']=json.loads((kernel/'.deps/manifest.json').read_text())
    cc=[tools['clang']['path'],'--no-default-config','--target=x86_64-linux-musl','--sysroot='+str(sdk/'empty-root')]
    flags=['-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-fstack-protector-strong','-nostdinc','-isystem',str(sdk/'stage/usr/include')]
    run('channel',cc+flags+['-c',str(HERE.parent/'native-channel/channel.c'),'-o',str(work/'channel.o')])
    clients=['client','truncated']
    builds=[('client','client.c',[]),('truncated','client.c',['-DTRUNCATED']),('service-start','service-start.c',[])]
    if a.descriptors:
        clients=['client','frozen-offset','early-close','leak-close']
        builds=[(name,'client.c',['-DDESCRIPTORS']+(['-D'+name.upper().replace('-','_')] if name!='client' else [])) for name in clients]+[('service-start','service-start.c',[])]
    if a.fd_failures:
        fault_cases=[('lost-open',1,None),('lost-write',2,None),('malformed-close',3,None),('close-error',4,None),('ignore-poison',2,'IGNORE_POISON'),('leak-retain',4,'LEAK_RETAIN'),('relax-reply',3,'RELAX_REPLY')]
        clients=[name for name,_,_ in fault_cases]
        builds=[(name,'client.c',['-DFD_FAILURES','-DFAILURE_MODE='+str(mode)]+(['-D'+control] if control else [])) for name,mode,control in fault_cases]+[('service-start','service-start.c',[])]
    if a.libc_files:
        clients=['client','wrong-errno','ignore-flags','frozen-offset']
        builds=[(name,'client.c',['-DLIBC_FILES','-D_POSIX_C_SOURCE=200809L']+(['-D'+name.upper().replace('-','_')] if name!='client' else [])) for name in clients]+[('service-start','service-start.c',[]),('libc-probe','libc-probe.c',[])]
        run('channel-facade',cc+flags+['-D__aether_io=__aether_channel_fallback','-c',str(HERE.parent/'native-channel/channel.c'),'-o',str(work/'channel-facade.o')])
        audit=['src/unistd/'+name+'.c' for name in ['read','write','close','dup','dup2','lseek']]+['src/fcntl/open.c','src/fcntl/openat.c','src/thread/__syscall_cp.c','src/thread/pthread_cancel.c','arch/x86_64/syscall_arch.h']
        report['musl_audit_sources']={name:sha(sdk/'musl-1.2.6'/name) for name in audit};save()
    stdio_objects=[]
    if a.stdio_files:
        report['scope']='bounded musl buffered FILE calls with native memory, adapted fdopen/fopen and internal I/O plus checked input fflush; no threads, TTY or POSIX filesystem'
        clients=['client','baseline-flush','corrupt-vector','leak-poll-errno']
        builds=[(name,'client.c',['-DLIBC_FILES','-DSTDIO_FILES','-D_POSIX_C_SOURCE=200809L']+(['-D'+name.upper().replace('-','_')] if name in ['corrupt-vector','leak-poll-errno'] else [])) for name in clients]+[('service-start','service-start.c',[]),('libc-probe','stdio-probe.c',[])]
        run('native-memory',cc+flags+['-c',str(memory_source),'-o',str(work/'native-memory.o')])
        stdio_objects.append(work/'native-memory.o')
        musl=sdk/'musl-1.2.6'
        internal=['-Wno-sign-compare','-Wno-unused-parameter','-I'+str(musl/'src/include'),'-I'+str(musl/'src/internal'),'-I'+str(musl/'arch/x86_64'),'-I'+str(musl/'arch/generic'),'-include',str(HERE/'stdio-transport.h')]
        report['stdio_inputs']={str(p.relative_to(musl)):sha(p) for folder in ['src/include','src/internal','arch/x86_64','arch/generic','include','src/stdio'] for p in (musl/folder).rglob('*') if p.is_file()}
        save()
        changes={
            '__stdio_read':('syscall(SYS_readv,','aether_readv('),
            '__stdio_write':('syscall(SYS_writev,','aether_writev('),
            '__stdio_seek':('__lseek(f->fd,','aether_stdio_seek(f->fd,'),
            '__fdopen':('weak_alias(__fdopen, fdopen);',''),
            'fflush':('if (f->rpos != f->rend) f->seek(f, f->rpos-f->rend, SEEK_CUR);','if (f->rpos != f->rend && f->seek(f, f->rpos-f->rend, SEEK_CUR)<0) { f->flags |= F_ERR; FUNLOCK(f); return EOF; }')}
        report['stdio_patches']={}
        for name,(old,new) in changes.items():
            origin=musl/('src/stdio/'+name+'.c');text=origin.read_text();need(text.count(old)==1,'stdio mutation anchor changed: '+name)
            changed=text.replace(old,new)
            if name=='__fdopen':changed=changed.replace('FILE *__fdopen(', 'FILE *__aether_fdopen_core(')
            source=work/(name+'.c');source.write_text(changed)
            report['stdio_patches'][name]={'source':str(origin),'before_sha256':sha(origin),'after_sha256':sha(source),'old':old,'new':new,'rename':'__aether_fdopen_core' if name=='__fdopen' else None};save()
            obj=work/(name+'.o');run(name+'-compile',cc+flags+internal+['-c',str(source),'-o',str(obj)])
            stdio_objects.append(obj)
            if name=='fflush':run('baseline-flush-compile',cc+flags+internal+['-c',str(origin),'-o',str(work/'fflush-baseline.o')])
    for name,source,opts in builds:
        run(name+'-compile',cc+flags+opts+(['-DWRITABLE'] if a.writable and source=='client.c' else [])+['-c',str(HERE/source),'-o',str(work/(name+'.o'))])
    owner_service=kernel/'user/native-files/service.rs'
    text=owner_service.read_text();anchor='if handle != 0xf001 && !write_root'
    need(text.count(anchor)==1,'root-denial mutation anchor changed')
    mutated=work/'bad_root.rs';mutated.write_text(text.replace(anchor,'if handle != 0xf001 && handle != 0 && !write_root'))
    report['root_mutation']={'owner_source_sha256':sha(owner_service),'mutated_source_sha256':sha(mutated),'scope':'test-only acceptance of root zero on the already delegated connection'}
    libs={}
    variants=[('service',owner_service,None),('wrong-data',owner_service,'wrong_data')]+([('skip-zero',owner_service,'skip_truncate_zero'),('ignore-rights',owner_service,'ignore_write_rights')] if a.writable else [('wrong-root',mutated,None)])
    if a.descriptors:variants=[('service',owner_service,None)]
    for name,source,cfg in variants:
        lib=work/(name+'.a');cmd=['rustc','+1.98.0','--edition=2024','--target=x86_64-unknown-none','--crate-name','file_service','--crate-type=staticlib','-C','opt-level=2','-C','panic=abort','-C','relocation-model=static',str(source),'-o',str(lib)]
        if a.writable:cmd+=['--cfg','writable']
        if cfg:cmd+=['--cfg',cfg]
        run(name+'-rust',cmd);libs[name]=lib
    lib=sdk/'stage/usr/lib';images={}
    for name,objects in [(name,[work/(name+'.o')]) for name in clients]+[(name,[work/'service-start.o',archive]) for name,archive in libs.items()]:
        if a.libc_files and name in clients:objects+=[work/'libc-probe.o']
        if a.stdio_files and name in clients:objects += [work/'fflush-baseline.o' if name=='baseline-flush' and obj.name=='fflush.o' else obj for obj in stdio_objects]
        channel=work/('channel-facade.o' if a.libc_files and name in clients else 'channel.o')
        elf=work/(name+'.elf')
        run(name+'-link',cc+['--ld-path='+tools['lld']['path'],'-nostdlib','-static','-Wl,-z,noexecstack','-Wl,--no-undefined','-Wl,-Map,'+str(work/(name+'.map')),str(lib/'crt1.o'),str(lib/'crti.o')]+[str(p) for p in objects]+[str(channel),str(lib/'libc.a'),str(lib/'crtn.o'),'-o',str(elf)])
        need(not run(name+'-undefined',[tools['nm']['path'],'--undefined-only','--extern-only',str(elf)]).stdout.strip(),'undefined symbols')
        import re
        need(not re.search(rb'\bsyscall\b',run(name+'-disassembly',[tools['objdump']['path'],'-d',str(elf)]).stdout),'Linux syscall instruction')
        run(name+'-headers',[tools['readelf']['path'],'-h','-l',str(elf)])
        data=elf.read_bytes();offset=struct.unpack_from('<Q',data,32)[0];width,count=struct.unpack_from('<HH',data,54)
        headers=[struct.unpack_from('<IIQQQQQQ',data,offset+i*width) for i in range(count)]
        need(any(h[0]==7 and h[1]==4 and 0<h[6]<=4096 for h in headers),'native profile requires bounded TLS')
        images[name]=data
    supervisor=work/'supervisor.raw'
    run('supervisor',['rustc','+1.98.0','--edition=2024','--target=x86_64-unknown-none','-C','opt-level=2','-C','panic=abort','-C','relocation-model=static','-C','link-arg=-Tuser/native-launch/linker.ld','-C','link-arg=--oformat=binary','user/native-files/supervisor.rs','-o',str(supervisor)])
    code=supervisor.read_bytes();need(0<len(code)<=4096,'supervisor bound')
    entropy=os.urandom(32);sys.path.insert(0,str(kernel/'scripts'));from native_smoke import run as smoke
    cases=[('positive','service','client',None),('wrong-data','wrong-data','client','NATIVE terminal slot=1 generation=1 kind=1 detail=171'),('truncated','service','truncated','NATIVE terminal slot=0 generation=1 kind=1 detail=121'),('wrong-root','wrong-root','client','NATIVE terminal slot=1 generation=1 kind=1 detail=150')]
    if a.writable:cases=[('positive','service','client',None),('wrong-data','wrong-data','client','NATIVE terminal slot=1 generation=1 kind=1 detail=205'),('skip-zero','skip-zero','client','NATIVE terminal slot=1 generation=1 kind=1 detail=219'),('ignore-rights','ignore-rights','client','NATIVE terminal slot=1 generation=1 kind=1 detail=218')]
    if a.descriptors:cases=[('positive','service','client',None)]+[(name,'service',name,'NATIVE terminal slot=1 generation=1 kind=1 detail='+str(code)) for name,code in [('frozen-offset',207),('early-close',213),('leak-close',216)]]
    if a.fd_failures:cases=[(name,'service',name,('NATIVE terminal slot=1 generation=1 kind=1 detail='+str({'ignore-poison':195,'leak-retain':193,'relax-reply':189}[name])) if control else None) for name,_,control in fault_cases]
    if a.libc_files:cases=[('positive','service','client',None)]+[(name,'service',name,'NATIVE terminal slot=1 generation=1 kind=1 detail='+str(code)) for name,code in [('wrong-errno',200),('ignore-flags',201),('frozen-offset',205)]]
    if a.stdio_files:cases=[('positive','service','client',None),('baseline-flush','service','baseline-flush','NATIVE terminal slot=1 generation=1 kind=1 detail=189'),('corrupt-vector','service','corrupt-vector','NATIVE terminal slot=1 generation=1 kind=1 detail=186'),('leak-poll-errno','service','leak-poll-errno','NATIVE terminal slot=1 generation=1 kind=1 detail=196')]
    for name,service,client,terminal in cases:
        dest=work/name;dest.mkdir();first,second=images[service],images[client]
        payload=dest/'native-c.bin';payload.write_bytes(struct.pack('<8sIIII',b'AENFS001',len(first),len(second),len(code),0)+entropy+first+second+code)
        run(name+'-kernel',['zig','build']+(['-Dnative-memory=true'] if a.stdio_files else [])+['-Dsmp=false','-Dnative-c-image='+str(payload),'-p',str(dest),'--cache-dir',str(kernel/'.zig-cache'),'--global-cache-dir',str(kernel/'.zig-cache/global')])
        context=(terminal.encode(),b'NATIVE supervisor result=611 reclaimed=0') if terminal else ()
        report['commands'].append({'name':name+'-smoke','function':'native_smoke.run','module_sha256':sources['scripts/native_smoke.py'],'image':str(dest/'aether.iso'),'expected_panic':'native C profile rejected' if terminal else None,'panic_context':[x.decode() for x in context],'marker':'AETHER NATIVE FILE SERVICE PASS'});save()
        smoke(dest/'aether.iso',expected_panic=b'native C profile rejected' if terminal else None,panic_context=context,marker=b'AETHER NATIVE FILE SERVICE PASS')
        lines=(dest/'native-serial.log').read_text().splitlines()
        if terminal:need('AETHER NATIVE FILE SERVICE PASS' not in lines,'negative emitted pass')
        else:
            for line in ['NATIVE terminal slot=0 generation=1 kind=1 detail=17','NATIVE terminal slot=1 generation=1 kind=1 detail=29','NATIVE terminal slot=0 generation=2 kind=1 detail=33','NATIVE supervisor result=100 reclaimed=3']:need(line in lines,'missing native outcome: '+line)
        report['cases'].append({'case':name,'result':'pass','negative':bool(terminal),'supervisor_sha256':sha(supervisor),'envelope_sha256':sha(payload),'iso_sha256':sha(dest/'aether.iso'),'serial_sha256':sha(dest/'native-serial.log')});save();print(name+': PASS',flush=True)
    need({str(p.relative_to(sdk)):sha(p) for p in (sdk/'stage').rglob('*') if p.is_file()}==inventory,'SDK changed during run')
    for name,h in sources.items():need(sha(kernel/name)==h,'isolated source changed: '+name)
    for name,h in local.items():need(sha(Path(name))==h,'consumer source changed during run')
    if a.stdio_files:
        for name,h in report['stdio_inputs'].items():need(sha(musl/name)==h,'musl stdio input changed: '+name)
    report['artifacts']={name:sha(work/(name+'.elf')) for name in images};report['status']='pass'
finally:save()
