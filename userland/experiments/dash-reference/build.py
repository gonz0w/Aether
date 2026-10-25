#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Offline dash cross-build; target generators execute in pinned Linux emulation."""
import hashlib
import json
from pathlib import Path
import re
import runpy
import struct
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REF = ROOT / 'experiments/musl-reference'
IMAGE = '8d0dff22866c67ea5de1d66ff04a54f17e610a11e3a5c970414820663c7649a4'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def require(ok, message):
    if not ok: raise RuntimeError(message)
lock = json.loads((HERE/'source.lock.json').read_text())
archive = ROOT/lock['archive']
require(sha(archive) == lock['sha256'], 'source digest mismatch')
tools = json.loads((REF/'tools.lock.json').read_text())['tools']
for key, tool in tools.items():
    require(sha(Path(tool['path'])) == tool['sha256'], 'tool changed: '+key)
sdk = Path(json.loads((REF/'evidence.json').read_text())['output'])
paths = list((sdk/'stage').rglob('*'))
require(not any(p.is_symlink() for p in paths), 'SDK symlink')
inventory = {str(p.relative_to(sdk)):sha(p) for p in paths if p.is_file()}
require(inventory == json.loads((REF/'large-tls-evidence.json').read_text())['sdk_inputs'], 'SDK changed')
out = Path(tempfile.mkdtemp(prefix='dash-reference-', dir=ROOT/'build'))
(out/'tmp').mkdir()
print(out, flush=True)
container_module = runpy.run_path(str(HERE/'container-process.py'))
process = container_module['PROCESS']
descriptor = container_module['selected_descriptor'](out)
with tarfile.open(archive) as tar: tar.extractall(out, filter='data')
src = out/('dash-'+lock['version'])
obj = out/'obj'
obj.mkdir()
lib = sdk/'stage/usr/lib'
cc = [tools['clang']['path'], '--no-default-config', '--target=x86_64-linux-musl',
      '--sysroot='+str(sdk/'stage'), '-nostdinc', '-isystem', str(sdk/'stage/usr/include'),
      '--ld-path='+tools['lld']['path']]
# Separate compile/preprocess from explicit target-only startup/library linking.
wrapper = out/'cc.py'
wrapper.write_text('#!'+sys.executable+'\nimport os,sys\nargs=sys.argv[1:]\ncc='+repr(cc)+'\n'
    +'if not any(x in args for x in ["-c","-E","-S"]):\n'
    +'    args=["-nostdlib","-static","-Wl,-z,noexecstack","-Wl,--no-undefined",'+repr(str(lib/'crt1.o'))+','+repr(str(lib/'crti.o'))+']+args+['+repr(str(lib/'libc.a'))+','+repr(str(lib/'crtn.o'))+']\n'
    +'os.execv(cc[0],cc+args)\n')
wrapper.chmod(0o755)
# The same target compiler builds generators, but never launches containers.
gen = out/'cc-for-build.py'
gen.write_text('#!'+sys.executable+'\nimport os,sys\nos.execv('+repr(str(wrapper))+',['+repr(str(wrapper))+']+sys.argv[1:])\n')
gen.chmod(0o755)
env = {'PATH':'/usr/bin:/bin','LC_ALL':'C','TMPDIR':str(out/'tmp'),
       'CC':str(wrapper),'CC_FOR_BUILD':str(gen),'CFLAGS':'-O2 -fstack-protector-strong',
       'CFLAGS_FOR_BUILD':'-O2','CONFIG_SHELL':'/bin/sh'}
commands = []
def run(name, args, cwd=obj, status=0):
    r = process['run'](args,cwd=cwd,env=env,work=out,label=name,timeout=240)
    (out/(name+'.stdout')).write_bytes(r.stdout)
    (out/(name+'.stderr')).write_bytes(r.stderr)
    commands.append({'name':name,'argv':args,'cwd':str(cwd),'exit':r.returncode})
    (out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
    require(r.record['complete'] and r.returncode == status,name+' failed: '+str(out))
    return r.stdout
run('configure',['/bin/sh',str(src/'configure'),'--build=aarch64-apple-darwin','--host=x86_64-linux-musl',
                 '--prefix=/usr','--without-libedit','--disable-tee','--disable-memfd-create'])
# Invoke target generators outside make's process tree, each with its own cleanup.
makefile = (src/'src/Makefile.am').read_text()
require('HELPERS = mkinit mksyntax mknodes mksignames' in makefile,
        'generator inventory changed')
match = re.search(r'dash_CFILES = (.*?)\ndash_SOURCES', makefile, re.S)
require(match is not None, 'generator source list changed')
cfiles = match.group(1).replace('\\', '').split()
require(len(cfiles) == 27 and all((src/'src'/f).is_file() for f in cfiles),
        'generator source arguments changed')
helpers = ['mkinit', 'mksyntax', 'mknodes', 'mksignames']
run('make-generators', [tools['make']['path'], '-C', 'src', '-j1', 'V=1']
    + helpers + ['builtins.h'])
for name in helpers:
    executable = obj/'src'/name
    executable.rename(executable.with_suffix('.elf'))
    executable.write_text('#!/bin/sh\nexit 97\n')
    executable.chmod(0o755)
    run('guard-'+name, [str(executable)], status=97)
generator_results = []
for name in helpers:
    work = out/('generator-'+name)
    work.mkdir()
    args = ([str(src/'src'/f) for f in cfiles] if name == 'mkinit' else
            [str(src/'src/nodetypes'), str(src/'src/nodes.c.pat')]
            if name == 'mknodes' else [])
    input_hashes = {str(p):sha(p) for p in [obj/'src'/(name+'.elf')] + [Path(a) for a in args]}
    (work/'inputs.json').write_text(json.dumps(input_hashes,indent=2)+'\n')
    state = container_module['run_container'](
        container_module['Client'](descriptor, work), IMAGE,
        ['/usr/bin/qemu-x86_64', str(obj/'src'/(name+'.elf'))] + args, work,
        generator_root=out, generator_cwd=obj/'src')
    require(state['complete'] and state['guest_exit'] == 0,
            'generator failed: '+str(work))
    require(all(sha(Path(p)) == h for p,h in input_hashes.items()), 'generator inputs changed')
    outputs = {'mkinit':['init.c'], 'mksyntax':['syntax.c','syntax.h'], 'mknodes':['nodes.c','nodes.h'], 'mksignames':['signames.c']}[name]
    generator_results.append({'name':name, 'receipt':str(work/'container.json'), 'inputs':input_hashes, 'guard_sha256':sha(obj/'src'/name), 'outputs':{f:sha(obj/'src'/f) for f in outputs}})
run('make',[tools['make']['path'],'-j1','V=1'])
for record in generator_results:
    require(sha(obj/'src'/record['name']) == record['guard_sha256'], 'generator guard changed')
    require(all(sha(obj/'src'/f) == h for f,h in record['outputs'].items()), 'generated output changed during make')
elf = obj/'src/dash'
data = elf.read_bytes()
require(data[:6] == b'\x7fELF\x02\x01' and struct.unpack_from('<HH',data,16)==(2,62),'ELF target')
off = struct.unpack_from('<Q',data,32)[0]
size,count = struct.unpack_from('<HH',data,54)
headers = [struct.unpack_from('<IIQQQQQQ',data,off+i*size) for i in range(count)]
require(not any(h[0] in (2,3) or (h[0]==1 and h[1]&3==3) for h in headers),'dynamic or W+X')
require(any(h[0]==0x6474e551 and not h[1]&1 for h in headers),'executable stack')
require(not run('undefined',[tools['nm']['path'],'--undefined-only','--extern-only',str(elf)]).strip(),'undefined symbols')
run('headers',[tools['readelf']['path'],'-h','-l',str(elf)])
run('object-imports',[tools['nm']['path'],'--undefined-only']+[str(p) for p in sorted((obj/'src').rglob('*.o'))])
# Preserve upstream notices; no real-prefix installation.
(out/'COPYING.dash').write_bytes((src/'COPYING').read_bytes())
evidence = {'schema':'aether-userland.dash-build.v1','scope':'static Linux x86-64 reference; no Aether shell execution',
 'output':str(out),'source_lock_sha256':sha(HERE/'source.lock.json'),'script_sha256':sha(Path(__file__)),
 'tools_lock_sha256':sha(REF/'tools.lock.json'),'sdk_inputs':inventory,'image_id':IMAGE,'environment':env,
 'build_isolation':'private host outputs; no host sandbox claim; no network fetch in build; emulated generators network=none',
 'host_tools_scope':'LLVM executable pins; host Python, shell, make utilities and shared libraries are not full hermetic closure',
 'patches':[],'elf_sha256':sha(elf),'elf_bytes':len(data),'headers':headers,
 'files':{str(p.relative_to(out)):sha(p) for p in [wrapper,gen,obj/'config.h',obj/'config.log',obj/'src/signames.c',out/'COPYING.dash']},
 'commands':commands,'generators':generator_results,'container_client':descriptor,
 'container_adapter_sha256':sha(HERE/'container-process.py'),'process_helper_sha256':sha(ROOT/'experiments/command-runner/process.py')}
(out/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
print('Dash reference build passed: '+str(out))
