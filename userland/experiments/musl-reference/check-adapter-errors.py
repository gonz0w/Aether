#!/usr/bin/env python3
"""Raw brk ENOSYS and strict metadata protection adaptation experiment."""
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import tempfile
import tarfile
import difflib

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
out = Path(tempfile.mkdtemp(prefix='adapter-errors-', dir=ROOT/'build'))
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
obj, elf = out/'adapter-errors.o', out/'adapter-errors.elf'
run('compile', cc + ['-std=c11','-O2','-Wall','-Wextra','-Werror','-fstack-protector-strong','-fno-builtin','-nostdinc','-isystem',str(ref/'stage/usr/include'),'-c',str(HERE/'adapter-errors.c'),'-o',str(obj)])
archive = ROOT/'build/musl-audit/musl-1.2.6.tar.gz'
require(sha(archive)=='d585fd3b613c66151fc3249e8ed44f77020cb5e6c1e635a616d3f9f82460512a', 'source archive pin')
with tarfile.open(archive) as tar:
    tar.extractall(out, filter='data')
src = out/'musl-1.2.6'
glue = src/'src/malloc/mallocng/glue.h'
original_glue = glue.read_text()
old = '#define brk(p) ((uintptr_t)__syscall(SYS_brk, p))'
require(original_glue.count(old)==1,'brk injection anchor')
glue.write_text(original_glue.replace(old,'extern uintptr_t aether_test_brk(uintptr_t);\n#define brk(p) aether_test_brk((uintptr_t)(p))'))
malloc_source = src/'src/malloc/mallocng/malloc.c'
original_malloc = malloc_source.read_text()
anchor = '&& errno != ENOSYS'
require(original_malloc.count(anchor)==1,'strict patch anchor')
flags = ['-std=c99','-O2','-nostdinc','-ffreestanding','-fno-stack-protector','-fno-strict-aliasing','-D_XOPEN_SOURCE=700']
for include in [src/'arch/x86_64',src/'arch/generic',src/'src/include',src/'src/internal',ref/'stage/usr/include',src/'include']:
    flags += ['-I',str(include)]
for variant in ['baseline','strict']:
    malloc_source.write_text(original_malloc if variant=='baseline' else original_malloc.replace(anchor,''))
    run('malloc-'+variant,cc+flags+['-c',str(malloc_source),'-o',str(out/'malloc.o')])
    elf = out/(variant+'.elf')
    run('link', cc + ['-fuse-ld='+tools['lld']['path'],'-nostdlib','-static','-Wl,-z,noexecstack','-Wl,--no-undefined','-Wl,--wrap=mprotect',str(lib/'crt1.o'),str(lib/'crti.o'),str(obj),str(out/'malloc.o'),str(lib/'libc.a'),str(lib/'crtn.o'),'-o',str(elf)])
patch = ''.join(difflib.unified_diff(original_malloc.splitlines(True),malloc_source.read_text().splitlines(True),fromfile='malloc.c',tofile='malloc.c'))
(out/'strict.patch').write_text(patch)
for variant in ['baseline','strict']:
    elf = out/(variant+'.elf')
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
for variant, case, status in [('baseline','pass',0),('baseline','eacces',0),('baseline','enosys',40),('strict','enosys',0)]:
    label = variant+'-'+case
    r = run(label,base+['-strace','/inputs/'+variant+'.elf',case],status)
    require(r.stdout == (b'AETHER ADAPTER ERRORS PASS\n' if status==0 else b''),'output: '+label)
    trace = r.stderr.decode()
    require(('--- SIGSEGV {' in trace)==(status==40),'fault oracle: '+label)
    calls = re.findall(r'^\d+ (\w+)\(',trace,re.M)
    require('brk' not in calls and 'mmap' in calls and 'exit_group' in calls,'injection/fallback trace')
    results.append({'case':label,'exit':status,'trace_sha256':sha(out/(label+'.trace'))})
evidence = {'schema':'aether-userland.adapter-errors-evidence.v1','scope':'Linux-emulated allocator object injection: raw brk ENOSYS; baseline versus strict metadata mprotect error handling; not native implementation',
    'output':str(out),'image_id':IMAGE,'source_sha256':sha(HERE/'adapter-errors.c'),'script_sha256':sha(Path(__file__)),
    'tools_lock_sha256':sha(HERE/'tools.lock.json'),'reference_evidence_sha256':sha(HERE/'evidence.json'),
    'sdk_pin_evidence_sha256':sha(HERE/'large-tls-evidence.json'),
    'runtime_identity_evidence_sha256':sha(HERE/'runtime-evidence.json'),
    'elf_sha256':{v:sha(out/(v+'.elf')) for v in ['baseline','strict']}, 'archive_sha256':sha(archive),'strict_patch_sha256':sha(out/'strict.patch'),'injected_glue_sha256':sha(glue),
    'commands':commands,'results':results}
(out/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
print('[OK] Four adapter error cases passed.')
print('Evidence: ' + str(out))
