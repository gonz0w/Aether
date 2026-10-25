#!/usr/bin/env python3
"""Bounded large-TLS Linux reference; no native ABI or loader changes."""
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
IMAGE = '8d0dff22866c67ea5de1d66ff04a54f17e610a11e3a5c970414820663c7649a4'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def require(ok, message):
    if not ok:
        raise RuntimeError(message)

tools = json.loads((HERE/'tools.lock.json').read_text())['tools']
for name, tool in tools.items():
    require(sha(Path(tool['path'])) == tool['sha256'], 'tool hash: ' + name)
ref = Path(json.loads((HERE/'evidence.json').read_text())['output'])
lib = ref/'stage/usr/lib'
out = Path(tempfile.mkdtemp(prefix='large-tls-', dir=ROOT/'build'))
(out/'tmp').mkdir()
env = {'PATH':'/usr/bin:/bin', 'LC_ALL':'C', 'TMPDIR':str(out/'tmp')}
commands = []
def run(name, cmd, expected=0):
    r = subprocess.run(cmd, env=env, capture_output=True, timeout=60)
    (out/(name+'.stdout')).write_bytes(r.stdout)
    (out/(name+'.trace')).write_bytes(r.stderr)
    commands.append({'name':name, 'argv':cmd, 'exit':r.returncode})
    require(r.returncode == expected, name + ': inspect ' + str(out))
    return r
cc = [tools['clang']['path'], '--no-default-config', '--target=x86_64-linux-musl', '--sysroot='+str(ref/'stage')]
obj, elf = out/'large-tls.o', out/'large-tls.elf'
run('compile', cc + ['-std=c11','-O2','-Wall','-Wextra','-Werror','-fstack-protector-strong','-nostdinc','-isystem',str(ref/'stage/usr/include'),'-c',str(HERE/'large-tls.c'),'-o',str(obj)])
run('link', cc + ['-fuse-ld='+tools['lld']['path'],'-nostdlib','-static','-Wl,-z,noexecstack','-Wl,--no-undefined',str(lib/'crt1.o'),str(lib/'crti.o'),str(obj),str(lib/'libc.a'),str(lib/'crtn.o'),'-o',str(elf)])
require(not run('undefined',[tools['nm']['path'],'--undefined-only','--extern-only',str(elf)]).stdout.strip(),'undefined symbol')
require(b'There are no relocations' in run('relocations',[tools['readelf']['path'],'-r',str(elf)]).stdout,'relocations')
run('headers',[tools['readelf']['path'],'-h','-l',str(elf)])
data = elf.read_bytes()
require(data[:6] == b'\x7fELF\x02\x01' and struct.unpack_from('<HH',data,16) == (2,62),'ELF target')
off = struct.unpack_from('<Q',data,32)[0]
size,count = struct.unpack_from('<HH',data,54)
headers = [struct.unpack_from('<IIQQQQQQ',data,off+i*size) for i in range(count)]
require(not any(h[0] in (2,3) or (h[0]==1 and h[1]&3==3) for h in headers),'dynamic or WX')
require(any(h[0]==0x6474e551 and not h[1]&1 for h in headers),'NX stack')
tls = [h for h in headers if h[0]==7]
require(len(tls)==1 and tls[0][5]==8192 and tls[0][6]==16384 and tls[0][7]==64,'TLS shape')
# Corrupt the actual file-backed initializer: witness must notice, before output.
bad = bytearray(data)
bad[tls[0][2]] ^= 1
(out/'corrupt.elf').write_bytes(bad)
(out/'corrupt.elf').chmod(0o755)
base = ['/opt/homebrew/bin/podman','run','--rm','--pull=never','--network=none','--read-only','--cap-drop=all','--security-opt=no-new-privileges','--user=65534:65534','--mount','type=bind,src='+str(out)+',dst=/inputs,ro=true','--entrypoint=qemu-x86_64',IMAGE,'-strace']
results = []
for case, binary, arg, status in [('pass','large-tls.elf','c',0),('bad-argument','large-tls.elf','x',10),('corrupt-initializer','corrupt.elf','c',12)]:
    r = run(case,base+['/inputs/'+binary,arg],status)
    require(r.stdout == (b'AETHER LARGE TLS PASS\n' if status==0 else b''),'output: '+case)
    calls = re.findall(r'^\d+ (\w+)\(',r.stderr.decode(),re.M)
    require('mmap' in calls and 'arch_prctl' in calls and calls.index('mmap') < calls.index('arch_prctl'),'pre-TLS mapping: '+case)
    require('exit_group' in calls,'exit: '+case)
    results.append({'case':case,'exit':status,'syscalls':calls,'trace_sha256':sha(out/(case+'.trace'))})
evidence = {'schema':'aether-userland.large-tls-evidence.v1','scope':'QEMU Linux user emulation only; one initial thread; no Aether execution',
    'output':str(out),'image_id':IMAGE,'source_sha256':sha(HERE/'large-tls.c'),'script_sha256':sha(Path(__file__)),
    'tools_lock_sha256':sha(HERE/'tools.lock.json'),'reference_evidence_sha256':sha(HERE/'evidence.json'),
    'sdk_inputs':{str(p.relative_to(ref)):sha(p) for p in sorted((ref/'stage').rglob('*')) if p.is_file()},
    'elf_sha256':sha(elf),'elf_bytes':len(data),'corrupt_elf_sha256':sha(out/'corrupt.elf'),'tls_header':tls[0],
    'commands':commands,'results':results}
(out/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
print('[OK] Three large-TLS reference cases passed.')
print('Evidence: ' + str(out))
