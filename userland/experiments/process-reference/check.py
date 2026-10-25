#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Nine bounded process/FD outcomes on the pinned Linux reference SDK."""
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
out=Path(tempfile.mkdtemp(prefix='process-reference-',dir=ROOT/'build'))
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
run('compile',cc+['-std=c11','-O2','-Wall','-Wextra','-Werror','-fstack-protector-strong','-c',str(HERE/'probe.c'),'-o',str(out/'probe.o')])
lib=sdk/'stage/usr/lib'
run('link',cc+['--ld-path='+tools['lld']['path'],'-nostdlib','-static','-Wl,-z,noexecstack','-Wl,--no-undefined',str(lib/'crt1.o'),str(lib/'crti.o'),str(out/'probe.o'),str(lib/'libc.a'),str(lib/'crtn.o'),'-o',str(out/'probe')])
require(not run('undefined',[tools['nm']['path'],'--undefined-only','--extern-only',str(out/'probe')]).stdout.strip(),'undefined symbols')
run('headers',[tools['readelf']['path'],'-h','-l',str(out/'probe')])
data=(out/'probe').read_bytes()
require(data[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<HH',data,16)==(2,62),'ELF target')
off=struct.unpack_from('<Q',data,32)[0];size,count=struct.unpack_from('<HH',data,54)
h=[struct.unpack_from('<IIQQQQQQ',data,off+i*size) for i in range(count)]
require(not any(x[0] in (2,3) or (x[0]==1 and x[1]&3==3) for x in h),'dynamic or W+X')
require(any(x[0]==0x6474e551 and not x[1]&1 for x in h),'NX stack')
(out/'not-executable').write_text('not executable\n');(out/'not-executable').chmod(0o644)
base=['/opt/homebrew/bin/podman','run','--rm','--pull=never','--network=none','--read-only','--cap-drop=all','--security-opt=no-new-privileges','--user=65534:65534','--memory=512m','--pids-limit=32','--tmpfs','/scratch:rw,noexec,nosuid,size=16m,mode=1777','--mount','type=bind,src='+str(out)+',dst=/inputs,ro=true','--entrypoint=/usr/bin/qemu-x86_64',IMAGE,'-strace','/inputs/probe']
cases=[('fork',0),('reopen-control',20),('exec',0),('cloexec-control',21),('failed-exec',0),('pipe',0),('writer-control',22),('fd-exhaustion',0),('vfork-exit',0)]
results=[]
for name,status in cases:
    r=run(name,base+[name],status)
    require(not r.stdout,name+': unexpected stdout')
    require(b'exit_group(' in r.stderr,name+': missing guest exit')
    results.append({'case':name,'exit':status,'trace_sha256':sha(out/(name+'.trace')),'stdout_sha256':sha(out/(name+'.stdout'))})
audit=['src/process/fork.c','src/process/_Fork.c','src/process/x86_64/vfork.s','src/process/execve.c','src/process/waitpid.c','src/linux/wait3.c','src/linux/wait4.c','src/fcntl/fcntl.c','src/fcntl/open.c','src/unistd/pipe.c','src/unistd/pipe2.c','src/unistd/dup.c','src/unistd/dup2.c','src/unistd/close.c','src/internal/syscall.h','src/signal/block.c','src/thread/__syscall_cp.c','src/thread/x86_64/syscall_cp.s']
e={'schema':'aether-userland.process-reference.v1','scope':'single-threaded QEMU Linux reference; exec through explicit native emulator; no native Aether process support, concurrency proof or source authentication','output':str(out),'source_sha256':sha(HERE/'probe.c'),'script_sha256':sha(Path(__file__)),'tools_lock_sha256':sha(REF/'tools.lock.json'),'sdk_inputs':inventory,'musl_archive_sha256':sha(archive),'audit_sources':{p:sha(src/p) for p in audit},'image_id':IMAGE,'environment':env,'elf_sha256':sha(out/'probe'),'elf_bytes':len(data),'headers':h,'commands':commands,'results':results}
(out/'evidence.json').write_text(json.dumps(e,indent=2)+'\n')
print('Nine process/descriptor reference outcomes passed: '+str(out))
