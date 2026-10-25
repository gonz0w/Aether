#!/usr/bin/env python3
"""Injected mremap failure exercises the unmodified musl realloc fallback."""
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
# Pin the retained SDK using the previously recorded large-TLS input inventory.
prior = json.loads((HERE/'large-tls-evidence.json').read_text())
paths = list((ref/'stage').rglob('*'))
require(not any(p.is_symlink() for p in paths), 'SDK symlink')
actual = {str(p.relative_to(ref)):sha(p) for p in paths if p.is_file()}
require(actual == prior['sdk_inputs'], 'SDK changed since retained input pin')
lib = ref/'stage/usr/lib'
out = Path(tempfile.mkdtemp(prefix='allocator-fallback-', dir=ROOT/'build'))
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
obj, elf = out/'allocator-fallback.o', out/'allocator-fallback.elf'
run('compile', cc + ['-std=c11','-O2','-Wall','-Wextra','-Werror','-fstack-protector-strong','-fno-builtin','-nostdinc','-isystem',str(ref/'stage/usr/include'),'-c',str(HERE/'allocator-fallback.c'),'-o',str(obj)])
run('link', cc + ['-fuse-ld='+tools['lld']['path'],'-nostdlib','-static','-Wl,-z,noexecstack','-Wl,--no-undefined','-Wl,--wrap=__mremap',str(lib/'crt1.o'),str(lib/'crti.o'),str(obj),str(lib/'libc.a'),str(lib/'crtn.o'),'-o',str(elf)])
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
base = ['/opt/homebrew/bin/podman','run','--rm','--pull=never','--network=none','--read-only','--cap-drop=all','--memory=512m','--pids-limit=32','--security-opt=no-new-privileges','--user=65534:65534','--mount','type=bind,src='+str(out)+',dst=/inputs,ro=true','--entrypoint=qemu-x86_64',IMAGE]
results = []
for case, status in [('pass', 0), ('real-remap', 20), ('corrupt-copy', 21)]:
    r = run(case,base+['-strace','/inputs/allocator-fallback.elf',case],status)
    require(r.stdout == (b'AETHER ALLOCATOR FALLBACK PASS\n' if status==0 else b''),'output: '+case)
    trace = r.stderr.decode()
    calls = re.findall(r'^\d+ (\w+)\(',trace,re.M)
    require('mmap' in calls and 'munmap' in calls and 'exit_group' in calls,'mapping/exit trace')
    if case == 'real-remap':
        require(re.search(r'mremap\([^\n]* = (?:0x[0-9a-f]+|[1-9][0-9]*)',trace), 'real remap control')
    else:
        require('mremap' not in calls, 'injection bypassed')
        mappings = re.findall(r'mmap\(NULL,(\d+),[^\n]* = (0x[0-9a-f]+)',trace)
        old = [address for size,address in mappings if 1048576 <= int(size) < 1052672]
        new = [address for size,address in mappings if 2097152 <= int(size) < 2101248]
        require(len(old)==1 and len(new)==1 and old[0]!=new[0], 'fallback mappings')
        for address in (old[0],new[0]):
            require(re.search(r'munmap\('+address+r',\d+\) = 0',trace), 'mapping not released')
        require(trace.index('munmap('+old[0]) > trace.index(' = '+new[0]), 'old released before replacement')
    results.append({'case':case,'exit':status,'syscalls':calls,'trace_sha256':sha(out/(case+'.trace'))})
evidence = {'schema':'aether-userland.allocator-fallback-evidence.v1','scope':'Link-time mremap ENOSYS injection into Linux reference; musl realloc unchanged; not native denial or allocator metadata exhaustion',
    'output':str(out),'image_id':IMAGE,'source_sha256':sha(HERE/'allocator-fallback.c'),'script_sha256':sha(Path(__file__)),
    'tools_lock_sha256':sha(HERE/'tools.lock.json'),'reference_evidence_sha256':sha(HERE/'evidence.json'),
    'sdk_pin_evidence_sha256':sha(HERE/'large-tls-evidence.json'),
    'runtime_identity_evidence_sha256':sha(HERE/'runtime-evidence.json'),
    'elf_sha256':sha(elf),'elf_bytes':len(data),
    'commands':commands,'results':results}
(out/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
print('[OK] Allocator fallback and two semantic controls passed.')
print('Evidence: ' + str(out))
