#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Build and admit the fixed AF09 owner/shell/helper dependency offline."""
import argparse
import ast
import hashlib
import io
import json
from pathlib import Path
import re
import runpy
import shutil
import shlex
import struct
import sys
import tarfile
import tempfile
import time

from deps import ROOT
import fs_home_launch as launch

SCHEMA = 'aether-guarded-af09-inputs-v1'
ARTIFACTS = ('owner.elf', 'owner.bin', 'shell.elf', 'helper.elf', 'envelope.bin')
PROFILE = dict(envelope='AENFS005', nested='AENMX010', abi=31, protocol='AFSRPC09',
    file_wire='AEFW0001', write_wire=True, paths=True, dup2=True, cwd=False,
    libc_file_write=False, selection='fs_home_probe_three', provider_attempts=3,
    utc_min=1791290040, utc_max_exclusive=1791290100, rtc='2026-10-06T12:34:00,clock=vm')
BOUNDS = dict(domains=7, channels=12, backing_bytes=35*1024*1024,
    owner_code=49152, owner_resident=8192, owner_stack=8192, owner_usable_stack=8184,
    owner_workspace=4096, owner_backing_pages=128, engine_backing_pages=8192,
    engine_loader_pages=2048, process_loader_pages=128, engine_file_bytes=8*1024*1024,
    process_file_bytes=1024*1024, writer_seconds=60, writer_ticks=6000,
    reader_seconds=30, reader_ticks=3000, capture_bytes=65536)
PROCESS_PIN = '9f0c0464c10fa23bfc7c3c91fe26b04e5ab063ca058eeb6d41542d98c6186e4e'
OWNER_CENSUS = ('native-home.rs', 'native-home-tests.rs', 'launch-home-owner.rs',
                'launch-home-owner-tests.rs', 'home-native-fixture.c')
FIELDS = {'format','status','native_executed','profile','bounds','engine',
    'producer_receipt','owner_receipt','owner_reuse','measurement','admission',
    'artifacts','inputs','tools','commands','kernel_build','final_input_verification'}
S = ROOT/'userland/experiments/filesystem-service'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return launch.read_json(path)


def sha_string(value):
    return isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value) is not None


def verify_map(inputs, generated=None):
    generated = generated or {}
    if not isinstance(inputs,dict) or not inputs:
        raise ValueError('AF09 guarded missing input map')
    for name, expected in inputs.items():
        path=Path(name)
        if not path.is_absolute() or not sha_string(expected):
            raise ValueError('AF09 guarded input map shape')
        if path.is_file():
            if digest(path)!=expected:
                raise ValueError('AF09 guarded input changed: '+name)
        elif generated.get(name)!=expected:
            raise ValueError('AF09 guarded unavailable input: '+name)
    return dict(inputs)


def literal(path,name):
    nodes=[n.value for n in ast.walk(ast.parse(path.read_text())) if isinstance(n,ast.Assign)
           and any(isinstance(t,ast.Name) and t.id==name for t in n.targets)]
    if len(nodes)!=1:raise ValueError('AF09 guarded unique recipe literal: '+name)
    return ast.literal_eval(nodes[0])


def owner_generated(report):
    """Recreate only the 47 disposed receipt23 input leaves, without extracting."""
    from source_paths import relocate
    work=Path(report.get('work',''))
    if ('..' in work.parts or relocate(work).parent!=ROOT/'userland/build'
            or not work.name.startswith('filesystem-home-')):
        raise ValueError('AF09 owner historical work identity')
    compare=ROOT/'sys-init/scripts/owner_compare.py'
    checker=S/'check-file-writes.py'
    for path in (compare,checker):
        recorded=[expected for name,expected in report.get('sources',{}).items()
                  if relocate(name)==path]
        if recorded!=[digest(path)]:
            raise ValueError('AF09 owner historical recipe changed')
    recipe=runpy.run_path(str(compare))
    sdk=ROOT/'.deps/native-current/sdk'
    archive=sdk/'musl-1.2.6.tar.gz'
    recipe['verified'](archive.read_bytes(),recipe['ARCHIVE_SHA'],str(archive))
    with tarfile.open(fileobj=io.BytesIO(archive.read_bytes()),mode='r:gz') as source:
        bodies={}
        for name,expected in recipe['MEMBERS'].items():
            infos=[m for m in source.getmembers() if m.name=='musl-1.2.6/'+name]
            if len(infos)!=1 or not infos[0].isfile():raise ValueError('AF09 owner tar member')
            bodies[name]=recipe['verified'](source.extractfile(infos[0]).read(),expected,name)
    values={'memcmp.c':bodies['src/string/memcmp.c']}
    for name,expected in recipe['HEADERS'].items():
        values['include/'+name]=recipe['verified']((sdk/'stage/usr/include'/name).read_bytes(),expected,name)
    body=values['memcmp.c'];old=b'const unsigned char *l'
    if body.count(old)!=1:raise ValueError('AF09 owner signed comparison anchor')
    values['signed.c']=body.replace(old,b'const signed char *l')
    generated={str(work/'musl-compare'/name):hashlib.sha256(body).hexdigest() for name,body in values.items()}
    controls=literal(checker,'c_controls')
    if len(controls)!=6 or len({row[0] for row in controls})!=6:
        raise ValueError('AF09 owner six C control recipes')
    names=('fd-file-write-tests.c','fd-facade.h','fd-client.h','fd-protocol.h',
           'fd-file-write.h','fd-client.c','fd-facade.c')
    for label,filename,before,after,_ in controls:
        if filename not in names:raise ValueError('AF09 owner C control source')
        for name in names:
            body=(S/name).read_text()
            if name==filename:
                if body.count(before)!=1:raise ValueError('AF09 owner C control anchor')
                body=body.replace(before,after,1)
            generated[str(work/('FILE-C-control-'+label)/name)]=hashlib.sha256(body.encode()).hexdigest()
    unavailable={name:expected for name,expected in report['sources'].items() if not Path(name).is_file()}
    if len(generated)!=47 or unavailable!=generated:
        raise ValueError('AF09 owner exact disposed input identities')
    return generated


def checked_producer(path):
    report,inputs=launch.checked_receipt(path,'producer')
    for name in launch.generated_sources(report):inputs.pop(name)
    return report,inputs


def owner_receipt(path,producer):
    report=read_json(path)
    if (report.get('schema')!='aether-home-owner-evidence-v1' or report.get('status')!='pass'
            or report.get('native_executed') is not False or report.get('cleanup')!='complete'
            or report.get('final_input_verification')!='pass' or len(report.get('rows',[]))!=891
            or len(report.get('home_owner_controls',[]))!=9):
        raise ValueError('AF09 historical owner coverage/status')
    for row in report['rows']:
        process=row.get('process',{})
        if (process.get('complete') is not True or process.get('cleanup')!='complete'
                or process.get('exit')!=row.get('expected_exit',0)):
            raise ValueError('AF09 historical owner incomplete child')
    generated=owner_generated(report)
    sources=dict(report['sources'])
    excluded={}
    for filename in OWNER_CENSUS:
        name=str(S/filename)
        if name not in sources or producer.get('sources',{}).get(name)!=digest(name):
            raise ValueError('AF09 census exclusion requires fresh producer coverage')
        excluded[name]=dict(historical_sha256=sources.pop(name),current_sha256=digest(name),
            impact='Census only in owner host receipt; not an owner crate/C translation unit. Fresh native producer covers current bytes.')
    # A bounded traversal of actual receipt compiler argv independently rejects
    # any excluded file that was a direct compile input. The owner builder also
    # records rustc dep-info for the freshly rebuilt real owner graph.
    for row in report['rows']:
        argv=row['process'].get('argv',[])
        if argv and Path(argv[0]).name in ('rustc','clippy-driver','clang') and any(arg in excluded for arg in argv):
            raise ValueError('AF09 excluded census file was a compiler input')
    inputs=verify_map(sources,generated)
    for name in generated:inputs.pop(name)
    inputs.update(verify_map(report['rust_native_libraries']))
    for tool in report['tools'].values():inputs.update(verify_map({tool['path']:tool['sha256']}))
    inputs[str(Path(path).absolute())]=digest(path)
    impact=dict(scope='historical host coverage with explicit input impact',children=891,
        fresh_host_qualification=False,excluded_census=excluded,
        reconstructed_generated=generated,generated_recipes=dict(compare=str(ROOT/'sys-init/scripts/owner_compare.py'),
        c_controls=str(S/'check-file-writes.py')),fresh_measurement='home_owner_build.build on current real sources')
    return report,inputs,impact


def envelope(engine,shell,helper,owner):
    if not (0<len(engine)<=8*1024*1024 and 0<len(shell)<=1024*1024
            and 0<len(helper)<=1024*1024 and 0<len(owner)<=49152):
        raise ValueError('AF09 guarded envelope extent')
    nested=struct.pack('<8sIIIIQ',b'AENMX010',len(shell),len(shell),len(helper),len(owner),0)+bytes(range(80))+shell+shell+helper+owner
    return struct.pack('<8sII',b'AENFS005',len(engine),len(nested))+bytes(range(32))+engine+nested


def checked_members(directory,seal):
    root=Path(directory).absolute()
    if root.is_symlink() or not root.is_dir() or not sha_string(seal):raise ValueError('AF09 guarded dependency path/seal')
    root=root.resolve()
    manifest=root/'SHA256SUMS'
    if manifest.is_symlink() or not manifest.is_file() or manifest.stat().st_size>4096 or digest(manifest)!=seal:
        raise ValueError('AF09 guarded manifest identity')
    members={}
    for line in manifest.read_text().splitlines():
        if not re.fullmatch(r'[0-9a-f]{64}  [a-z.]+',line):raise ValueError('AF09 guarded member shape')
        expected,name=line.split('  ',1)
        if name in members:raise ValueError('AF09 guarded duplicate member')
        members[name]=expected
    wanted=set(ARTIFACTS)|{'inputs.json'}
    if set(members)!=wanted or {p.name for p in root.iterdir()}!=wanted|{'SHA256SUMS'}:
        raise ValueError('AF09 guarded exact member closure')
    total=0
    for name,expected in members.items():
        path=root/name
        ceiling=16*1024*1024 if name=='inputs.json' else 12*1024*1024 if name=='envelope.bin' else 1024*1024
        if path.is_symlink() or not path.is_file() or not 0<path.stat().st_size<=ceiling or digest(path)!=expected:
            raise ValueError('AF09 guarded member identity/extent')
        total+=path.stat().st_size
    if total>24*1024*1024:raise ValueError('AF09 guarded total dependency extent')
    return members


def kernel_flags():
    from fs_session import FLAGS
    return [*FLAGS,'native-fs-session-init','native-fs-owner-data','native-fs-owner-stack']


def validate_record(record):
    if (not isinstance(record,dict) or set(record)!=FIELDS or record.get('format')!=SCHEMA
            or record.get('status')!='prepared' or record.get('native_executed') is not False
            or record.get('profile')!=PROFILE or record.get('bounds')!=BOUNDS
            or record.get('final_input_verification')!='pass'):
        raise ValueError('AF09 guarded exact profile/status/fields')
    for name,keys in [('engine',{'directory','seal','elf_sha256'}),('producer_receipt',{'path','sha256'}),('owner_receipt',{'path','sha256'})]:
        row=record[name]
        if not isinstance(row,dict) or set(row)!=keys or any(not sha_string(row[k]) for k in keys-{'directory','path'}):
            raise ValueError('AF09 guarded association identity')
    relative=Path(record['engine']['directory'])
    if (relative.as_posix()!=record['engine']['directory'] or relative.is_absolute() or relative.parent!=Path('.deps') or not relative.name.startswith('fs-launch-af09-')):
        raise ValueError('AF09 guarded engine selection')
    measurement=record['measurement'];stack=measurement.get('stack',{})
    if (measurement.get('code_budget')!=49152 or measurement.get('code_fits') is not True
            or not 0<measurement.get('code_bytes',0)<=49152 or measurement.get('resident_fits') is not True
            or measurement.get('native_executed') is not False
            or not 0<measurement.get('runtime_bytes',0)<=4096 or not 0<measurement.get('alignment',0)<=4096
            or measurement.get('mapped_bytes')!=8192 or measurement.get('workspace_bytes')!=4096
            or stack.get('status')!='pass' or stack.get('usable_stack_bytes')!=8184
            or not 0<stack.get('entry_stack_bytes',0)<=8184):raise ValueError('AF09 guarded owner fit')
    pages=record['admission']
    if (set(pages)!={'engine_pages','shell_pages','helper_pages','owner_bytes'}
            or any(type(n) is not int for n in pages.values())
            or not 16<pages['engine_pages']<=2048 or not 16<pages['shell_pages']<=128
            or not 16<pages['helper_pages']<=128 or pages['owner_bytes']!=measurement['code_bytes']):
        raise ValueError('AF09 guarded measured new loader geometry')
    if set(record['artifacts'])!=set(ARTIFACTS):raise ValueError('AF09 guarded artifact coverage')
    for name,row in record['artifacts'].items():
        if (set(row)!={'sha256','bytes'} or not sha_string(row['sha256'])
                or type(row['bytes']) is not int or row['bytes']<=0):raise ValueError('AF09 guarded artifact identity')
    if not record['inputs'] or not record['tools'] or not record['commands']:raise ValueError('AF09 guarded consumed closure missing')
    for command in record['commands']:
        p=command.get('process',{})
        if command.get('status')!='pass' or p.get('complete') is not True or p.get('cleanup')!='complete' or p.get('exit')!=command.get('expected_exit',0):
            raise ValueError('AF09 guarded successful child missing')
    if (set(record['kernel_build'])!={'sha256','native_executed','flags'}
            or record['kernel_build'].get('native_executed') is not False
            or record['kernel_build'].get('flags')!=kernel_flags()
            or not sha_string(record['kernel_build'].get('sha256'))):raise ValueError('AF09 guarded actual kernel build')


def owned_runner():
    path=ROOT/'userland/experiments/command-runner/process.py'
    if digest(path)!=PROCESS_PIN:raise ValueError('AF09 guarded owned-process pin')
    import importlib.util
    spec=importlib.util.spec_from_file_location('af09_inputs_process',path)
    proc=importlib.util.module_from_spec(spec);sys.modules[spec.name]=proc;spec.loader.exec_module(proc)
    return proc


def rust_wrapper(path):
    """Private named Rust descendant: fixed compiler and private LLVM only."""
    compiler=Path(path)
    library=compiler.parent.parent/'lib'
    return ('#!/bin/sh\ncase "${1-}" in\n'
        '  +1.98.0) shift ;;\n'
        '  +*) printf "%s\\n" "unsupported pinned Rust selector" >&2; exit 64 ;;\n'
        'esac\nDYLD_LIBRARY_PATH='+shlex.quote(str(library))+' exec '+shlex.quote(str(compiler))+' "$@"\n')


def kernel_environment(work,tools,record,command):
    """Bind build.zig's named descendants without importing the caller's PATH."""
    from deps import LOCK
    work=Path(work);folder=work/'tool-bin';folder.mkdir()
    defaults={'python3':Path(sys.executable).resolve(),
        'xorriso':Path('/opt/homebrew/bin/xorriso'),
        'qemu':Path('/opt/homebrew/bin/qemu-system-x86_64')}
    for name in ('python3','xorriso','qemu'):
        selected=tools.get(name)
        path=Path(selected['path']) if selected else defaults[name]
        if not path.is_absolute() or not path.is_file():
            raise ValueError('AF09 required named tool unavailable: '+name)
        path=path.resolve()
        actual=digest(path)
        if selected and selected['sha256']!=actual:
            raise ValueError('AF09 named tool changed: '+name)
        tools[name]=dict(path=str(path),sha256=actual)
    if digest(tools['rustc']['path'])!=tools['rustc']['sha256']:
        raise ValueError('AF09 pinned Rust compiler changed')
    for name in ('python3','rustc','xorriso','qemu'):
        record.setdefault('inputs',{})[tools[name]['path']]=tools[name]['sha256']
    bindings={}
    for name in ('python3','xorriso'):
        target=Path(tools[name]['path'])
        link=folder/name;link.symlink_to(target)
        bindings[name]=dict(link=str(link),path=str(target),sha256=tools[name]['sha256'])
    body=rust_wrapper(tools['rustc']['path'])
    wrapper=folder/'rustc';wrapper.write_text(body);wrapper.chmod(0o755)
    routing=dict(environment=dict(PATH=str(folder)+':/usr/bin:/bin'),bindings=bindings,
        rust_compiler=dict(tools['rustc']),rust_wrapper=dict(path=str(wrapper),body=body,sha256=digest(wrapper)),
        generator_sha256=digest(__file__),prospective_qemu=dict(tools['qemu'],expected_version=LOCK['qemu'],executed=False),
        versions=dict(python='3.14.7',rust='1.98.0',xorriso=LOCK['xorriso']))
    verify_kernel_environment(routing)
    python=command('kernel-python-version',[tools['python3']['path'],'--version']).strip()
    rust=command('kernel-rust-version',[tools['rustc']['path'],'--version']).split()
    optical=command('kernel-xorriso-version',[tools['xorriso']['path'],'-version'])
    if python!='Python 3.14.7' or len(rust)<2 or rust[1]!='1.98.0' or ('xorriso version   :  '+LOCK['xorriso']) not in optical:
        raise ValueError('AF09 named descendant version differs from pinned build profile')
    verify_kernel_environment(routing)
    record['kernel_tool_routing']=routing
    return routing


def verify_kernel_environment(routing):
    for item in routing['bindings'].values():
        if Path(item['link']).resolve()!=Path(item['path']).resolve() or digest(item['path'])!=item['sha256']:
            raise ValueError('AF09 named descendant binding changed')
    compiler=routing['rust_compiler'];wrapper=routing['rust_wrapper']
    body=rust_wrapper(compiler['path'])
    if (digest(compiler['path'])!=compiler['sha256'] or wrapper['body']!=body
            or hashlib.sha256(body.encode()).hexdigest()!=wrapper['sha256']
            or Path(wrapper['path']).is_symlink() or digest(wrapper['path'])!=wrapper['sha256']
            or digest(routing['prospective_qemu']['path'])!=routing['prospective_qemu']['sha256']):
        raise ValueError('AF09 named Rust recipe/compiler or prospective emulator changed')


def routing_receipt(record):
    rows=[row for row in record['commands'] if row.get('label')=='actual-kernel-build']
    if len(rows)!=1 or not isinstance(rows[0].get('tool_routing'),dict):
        raise ValueError('AF09 actual kernel named-tool routing receipt missing')
    from deps import LOCK
    routing=rows[0]['tool_routing'];compiler=record['tools']['rustc']
    body=rust_wrapper(compiler['path'])
    wrapper_path=Path(routing.get('rust_wrapper',{}).get('path',''))
    environment=routing.get('environment',{})
    if (not wrapper_path.is_absolute() or wrapper_path.name!='rustc'
            or environment!={'PATH':str(wrapper_path.parent)+':/usr/bin:/bin'}
            or routing.get('versions')!=dict(python='3.14.7',rust='1.98.0',xorriso=LOCK['xorriso'])
            or routing.get('prospective_qemu')!=dict(record['tools']['qemu'],expected_version=LOCK['qemu'],executed=False)
            or rows[0]['process'].get('environment',{}).get('PATH')!=environment['PATH']
            or 'DYLD_LIBRARY_PATH' in rows[0]['process'].get('environment',{})):
        raise ValueError('AF09 sealed named descendant environment/version differs')
    if (routing.get('rust_compiler')!=compiler or routing.get('rust_wrapper',{}).get('body')!=body
            or routing['rust_wrapper'].get('sha256')!=hashlib.sha256(body.encode()).hexdigest()
            or routing.get('generator_sha256')!=digest(__file__)
            or 'DYLD_LIBRARY_PATH' in routing.get('environment',{})):
        raise ValueError('AF09 sealed named-tool recipe/identity differs')
    for name in ('python3','xorriso'):
        expected=record['tools'][name];item=routing.get('bindings',{}).get(name,{})
        if item.get('link')!=str(wrapper_path.parent/name) or any(item.get(key)!=expected[key] for key in ('path','sha256')):
            raise ValueError('AF09 sealed named descendant identity differs')


def command_runner(work,proc,tools,deadline,record):
    if not isinstance(proc,launch.CleanupTrackedProcess):
        proc=launch.CleanupTrackedProcess(proc,record)
    routing=None
    def command(label,args):
        nonlocal routing
        if label=='actual-kernel-build' and routing is None:
            routing=kernel_environment(work,tools,record,command)
        remaining=deadline-time.monotonic()
        if remaining<=0:raise RuntimeError('AF09 guarded cumulative target deadline')
        args=list(map(str,args))
        env=proc.clean_env(work)
        if routing is not None:
            verify_kernel_environment(routing);env.update(routing['environment'])
        result=proc.run(args,cwd=ROOT,env=env,work=work,
            label='inputs-%04d-%s'%(len(record.setdefault('commands',[])),label),timeout=min(180,remaining))
        good=result.returncode==0 and result.record['complete'] and result.record['cleanup']=='complete'
        record['commands'].append(dict(label=label,status='pass' if good else 'failed',process=result.record,
            stdout_sha256=hashlib.sha256(result.stdout).hexdigest(),stderr_sha256=hashlib.sha256(result.stderr).hexdigest(),
            tail=(result.stdout+result.stderr).decode(errors='replace')[-7000:] if not good else
                (result.stdout+result.stderr).decode(errors='replace')[-1000:]))
        if routing is not None:
            verify_kernel_environment(routing)
            if label=='actual-kernel-build':record['commands'][-1]['tool_routing']=routing
        if not good:raise RuntimeError('AF09 guarded child failed: '+label)
        return (result.stdout+result.stderr).decode(errors='replace')
    return command


def admit(root,engine,work,command,tools):
    """Run current kernel parsers on final ELF bytes and the exact envelope."""
    stage=work/'admission';stage.mkdir()
    for name,source in [('engine.elf',engine),('shell.elf',root/'shell.elf'),('helper.elf',root/'helper.elf')]:
        shutil.copyfile(source,stage/name)
    shutil.copyfile(root/'envelope.bin',stage/'envelope.bin')
    # Separate native_elf and composition modules avoid loading the same Zig
    # file in two module namespaces. Both children consume the same final bytes.
    (stage/'elf.zig').write_text(r'''const std=@import("std");const elf=@import("native_elf");
fn pages(image: *const elf.Image) usize {var n:usize=16;for(image.segments[0..image.count])|s|{n+=(s.address%4096+s.memsz+4095)/4096;}return n;}
fn check(comptime name:[]const u8, limits:elf.Limits) !usize {
const raw=@embedFile(name);const image=try elf.parseWithLimits(raw,limits);const n=pages(&image);
try std.testing.expectError(error.InvalidImage,elf.parseWithLimits(raw,.{.file_bytes=limits.file_bytes,.pages=n-1}));
const bad=try std.heap.page_allocator.dupe(u8,raw);defer std.heap.page_allocator.free(bad);const ph=std.mem.readInt(u64,bad[32..40],.little);const count=std.mem.readInt(u16,bad[56..58],.little);var tls:?usize=null;var load:?usize=null;
for(0..count)|i|{const at=ph+i*56;const k=std.mem.readInt(u32,bad[at..][0..4],.little);if(k==7)tls=at;if(k==1)load=at;}
try std.testing.expect(tls!=null and load!=null);
std.mem.writeInt(u32,bad[tls.?..][0..4],0,.little);try std.testing.expectError(error.InvalidImage,elf.parseWithLimits(bad,limits));
@memcpy(bad,raw);std.mem.writeInt(u32,bad[load.?+4..][0..4],7,.little);try std.testing.expectError(error.InvalidImage,elf.parseWithLimits(bad,limits));return n;}
pub fn main() !void {const e=try check("engine.elf",elf.large_limits);const s=try check("shell.elf",.{});const h=try check("helper.elf",.{});std.debug.print("AF09_PAGES {d} {d} {d}\n",.{e,s,h});}
''')
    text=command('actual-elf-parser',[tools['zig']['path'],'run','--cache-dir',work/'zig-cache',
        '--global-cache-dir',ROOT/'.zig-cache/global','-O','ReleaseSafe','--dep','native_elf',
        '-Mroot='+str(stage/'elf.zig'),'-Mnative_elf='+str(ROOT/'kernel/native_elf.zig')])
    found=re.findall(r'^AF09_PAGES (\d+) (\d+) (\d+)$',text,re.M)
    if len(found)!=1:raise ValueError('AF09 guarded actual parser page observation')
    (stage/'composition.zig').write_text(r'''const std=@import("std");const c=@import("composition");
pub fn main() !void {const raw=@embedFile("envelope.bin");const b=try c.parseOwnerStack(raw);
try std.testing.expectEqualSlices(u8,@embedFile("engine.elf"),b.engine);
try std.testing.expectEqualSlices(u8,@embedFile("shell.elf"),b.session.images[0]);
try std.testing.expectEqualSlices(u8,@embedFile("shell.elf"),b.session.images[1]);
try std.testing.expectEqualSlices(u8,@embedFile("helper.elf"),b.session.images[2]);
try std.testing.expectError(error.InvalidComposition,c.parseOwnerData(raw));
const bad=try std.heap.page_allocator.dupe(u8,raw);defer std.heap.page_allocator.free(bad);@memcpy(bad[0..8],"AENFS004");try std.testing.expectError(error.InvalidComposition,c.parseOwnerStack(bad));
@memcpy(bad,raw);const n=48+b.engine.len;@memcpy(bad[n..][0..8],"AENMX009");try std.testing.expectError(error.InvalidComposition,c.parseOwnerStack(bad));
@memcpy(bad,raw);bad[n+24]=1;try std.testing.expectError(error.InvalidComposition,c.parseOwnerStack(bad));
try std.testing.expectError(error.InvalidComposition,c.parseOwnerStack(raw[0..raw.len-1]));
std.debug.print("AF09_COMPOSITION {d}\n",.{b.session.supervisor.len});}
''')
    text=command('actual-composition-parser',[tools['zig']['path'],'run','--cache-dir',work/'zig-cache',
        '--global-cache-dir',ROOT/'.zig-cache/global','-O','ReleaseSafe','--dep','composition',
        '-Mroot='+str(stage/'composition.zig'),'-Mcomposition='+str(ROOT/'kernel/native_fs_session.zig')])
    owner=re.findall(r'^AF09_COMPOSITION (\d+)$',text,re.M)
    if len(owner)!=1:raise ValueError('AF09 guarded composition observation')
    e,s,h=map(int,found[0])
    return dict(engine_pages=e,shell_pages=s,helper_pages=h,owner_bytes=int(owner[0]))


def owner_pair(root,measurement,command,tools):
    """Reinspect the actual raw-owner pair; it is deliberately not process ELF."""
    elf=(root/'owner.elf').read_bytes();raw=(root/'owner.bin').read_bytes()
    if (len(elf)<64 or elf[:8]!=b'\x7fELF\x02\x01\x01\x00'
            or struct.unpack_from('<HHI',elf,16)!=(2,62,1)
            or struct.unpack_from('<Q',elf,24)[0]!=0x400000):raise ValueError('AF09 owner ELF identity')
    offset=struct.unpack_from('<Q',elf,32)[0];stride,count=struct.unpack_from('<HH',elf,54)
    if stride!=56 or not 0<count<=16 or offset+stride*count>len(elf):raise ValueError('AF09 owner program extent')
    loads=[]
    for i in range(count):
        kind,flags,at,address,_,length,memory,_=struct.unpack_from('<IIQQQQQQ',elf,offset+i*stride)
        if kind not in (1,6,0x6474e551,0x6474e552) or at+length>len(elf):raise ValueError('AF09 owner program kind/extent')
        if kind==1:
            if flags!=5 or address!=0x400000 or length!=memory:raise ValueError('AF09 owner RX raw layout')
            loads.append(elf[at:at+length])
    shoff=struct.unpack_from('<Q',elf,40)[0];shstride,shnum,shnames=struct.unpack_from('<HHH',elf,58)
    if shstride!=64 or not 0<shnum<=256 or shoff+shstride*shnum>len(elf) or not 0<shnames<shnum:
        raise ValueError('AF09 owner section table')
    sections=[struct.unpack_from('<IIQQQQIIQQ',elf,shoff+i*shstride) for i in range(shnum)]
    names=sections[shnames]
    if names[1]!=3 or names[4]+names[5]>len(elf):raise ValueError('AF09 owner section names')
    strings=elf[names[4]:names[4]+names[5]];allocated=[]
    for section in sections:
        name,kind,flags,address,at,length,_,_,_,_=section
        if kind!=8 and at+length>len(elf):raise ValueError('AF09 owner section extent')
        if flags&2 and length:
            if name>=len(strings) or strings.find(b'\0',name)<0:raise ValueError('AF09 owner section label')
            label=strings[name:strings.index(b'\0',name)]
            if label!=b'.text' or kind!=1 or address!=0x400000 or length!=len(raw):
                raise ValueError('AF09 owner extra allocated/writable section')
            allocated.append(elf[at:at+length])
    if allocated!=[raw]:raise ValueError('AF09 owner unique text section')
    if loads!=[raw] or len(raw)!=measurement['code_bytes']:raise ValueError('AF09 owner ELF/raw correspondence')
    if (measurement.get('elf_sha256')!=digest(root/'owner.elf')
            or measurement.get('raw_sha256')!=digest(root/'owner.bin')):raise ValueError('AF09 owner measured artifact identity')
    if command('owner-pair-imports',[tools['nm']['path'],'--undefined-only',root/'owner.elf']).strip():
        raise ValueError('AF09 owner unresolved import')
    assembly=command('owner-pair-stack',[tools['objdump']['path'],'-d','--no-show-raw-insn',
        '--x86-asm-syntax=intel',root/'owner.elf'])
    from owner_stack import inspect
    stack=inspect(assembly,root/'owner.elf',stack_bytes=8192)
    if stack['entry_stack_bytes']!=measurement['stack']['entry_stack_bytes']:
        raise ValueError('AF09 owner actual conservative stack correspondence')


def output_path(destination):
    destination=Path(destination).absolute()
    if (destination.parent!=ROOT/'.deps' or destination.parent.resolve()!=destination.parent
            or not destination.name.startswith('fs-owner-af09-') or destination.exists() or destination.is_symlink()):
        raise ValueError('AF09 guarded requires unused .deps/fs-owner-af09-* output')
    return destination


def merge_dependency_inputs(record,probe):
    inputs=record.setdefault('inputs',{})
    inputs.update(probe['sources']);inputs.update(record['home_probe_native_headers'])
    for dep in record['home_probe_dependencies']:
        root=Path(dep['path']);manifest=root/'SHA256SUMS'
        inputs[str(manifest)]=digest(manifest)
        for line in manifest.read_text().splitlines():
            expected,name=line.split('  ',1);inputs[str(root/name)]=expected
    return inputs


def required_sources():
    paths={Path(__file__).resolve(),ROOT/'tests/test_fs_home_inputs.py',ROOT/'build.zig'}
    manifest=ROOT/'build.zig.zon'
    if manifest.exists() or manifest.is_symlink():
        paths.add(manifest)
    for directory in ('kernel','user','scripts'):
        paths.update(p for p in (ROOT/directory).rglob('*') if p.is_file()
            and '__pycache__' not in p.parts and p.name!='.DS_Store')
    builder=runpy.run_path(str(ROOT/'sys-init/scripts/home_owner_build.py'))
    owner=ROOT/'sys-init/prototypes/native-filesystem-session'
    original=ROOT/'sys-init/scripts/check-home-owner.py'
    observation=ROOT/'sys-init/scripts/check-file-write-observations.py'
    roots=[S/filename for _,filename,_ in literal(original,'producer_crates')]
    roots += [owner/filename for _,filename,_ in literal(observation,'OWNER_CRATES')]
    roots += [owner/'native_owner.rs',owner/'owner_entry.rs']
    paths.update(builder['rust_sources'](roots))
    paths.update((ROOT/'sys-init/scripts/home_owner_build.py',ROOT/'sys-init/tests/home_owner_build_tests.py',
        original,observation,ROOT/'sys-init/scripts/owner_compare.py',ROOT/'sys-init/scripts/owner_measure.py',
        ROOT/'sys-init/tests/owner_compare.c',ROOT/'docs/native-fs-owner-stack-v1.json'))
    probe=runpy.run_path(str(S/'home_probe_build.py'))
    paths.update(S/name for name in probe['NAMES'])
    paths.update((S/'home_probe_build.py',S/'check-home-wire.py',ROOT/'userland/experiments/command-runner/process.py'))
    return paths


def intake(directory,seal,*,deadline=None):
    root=Path(directory).absolute()
    members=checked_members(root,seal)
    record=read_json(root/'inputs.json');validate_record(record)
    for name,row in record['artifacts'].items():
        if members[name]!=row['sha256'] or (root/name).stat().st_size!=row['bytes']:
            raise ValueError('AF09 guarded artifact/record correspondence')
    engine=launch.intake(ROOT/record['engine']['directory'],record['engine']['seal'])
    if engine['elf_sha256']!=record['engine']['elf_sha256']:raise ValueError('AF09 guarded engine association')
    if read_json(ROOT/record['engine']['directory']/'build.json')['qualification_sha256']!=digest(record['producer_receipt']['path']):
        raise ValueError('AF09 guarded engine/producer receipt association')
    producer,producer_inputs=checked_producer(record['producer_receipt']['path'])
    _,owner_inputs,impact=owner_receipt(record['owner_receipt']['path'],producer)
    if impact!=record['owner_reuse']:raise ValueError('AF09 guarded historical reuse impact drift')
    associations={**producer_inputs,**owner_inputs}
    if any(record['inputs'].get(name)!=expected for name,expected in associations.items()):
        raise ValueError('AF09 guarded receipt input map coverage')
    for key in ('producer_receipt','owner_receipt'):
        if digest(record[key]['path'])!=record[key]['sha256']:raise ValueError('AF09 guarded receipt identity')
    if not {str(p) for p in required_sources()} <= record['inputs'].keys():
        raise ValueError('AF09 guarded complete consumed source map coverage')
    verify_map(record['inputs'])
    for tool in record['tools'].values():verify_map({tool['path']:tool['sha256']})
    routing_receipt(record)
    actual=envelope(Path(engine['elf']).read_bytes(),(root/'shell.elf').read_bytes(),
        (root/'helper.elf').read_bytes(),(root/'owner.bin').read_bytes())
    if (root/'envelope.bin').read_bytes()!=actual:raise ValueError('AF09 guarded exact envelope artifact correspondence')
    audit_dir=ROOT/'userland/docs/evidence/filesystem-home-prep-2026-10-24/guarded-inputs/intake'
    audit_dir.mkdir(parents=True,exist_ok=True)
    audit_path=next_receipt(audit_dir)
    receipt=dict(status='running',commands=[],inputs=record['inputs'],native_executed=False,directory=str(root),seal=seal)
    work=None;work_identity=None
    try:
        work=Path(tempfile.mkdtemp(prefix='fs-home-intake-',dir=ROOT/'userland/build'))
        work_identity=directory_identity(work)
        intake_deadline=min(time.monotonic()+300,deadline) if deadline is not None else time.monotonic()+300
        command=command_runner(work,owned_runner(),record['tools'],intake_deadline,receipt)
        owner_pair(root,record['measurement'],command,record['tools'])
        if admit(root,Path(engine['elf']),work,command,record['tools'])!=record['admission']:
            raise ValueError('AF09 guarded actual parser geometry changed')
        verify_map(record['inputs'])
        if checked_members(root,seal)!=members:raise ValueError('AF09 guarded dependency changed during intake')
        if time.monotonic()>intake_deadline:raise RuntimeError('AF09 guarded intake deadline after verification')
        receipt.update(status='pass',final_input_verification='pass')
    except BaseException as error:
        receipt.update(status='failed',error=type(error).__name__+': '+str(error));raise
    finally:
        primary=sys.exception();errors=[]
        if launch.process_cleanup_unresolved(receipt,primary):
            launch.retain_unresolved(receipt,[work,root],primary)
        elif work is not None:remove_owned(work,work_identity,errors,'intake-work')
        finish_attempt(receipt,audit_path,errors,primary)
    return dict(format=SCHEMA,directory=str(root),seal=seal,engine=record['engine'],
        admission=record['admission'],measurement=record['measurement'],native_executed=False)


def _build(destination,engine_directory,engine_seal,producer_receipt,owner_qualification,detail,receipt):
    """Construct one selected dependency under the outer attempt receipt."""
    destination=output_path(destination)
    engine_directory=Path(engine_directory).absolute()
    engine=launch.intake(engine_directory,engine_seal)
    producer,inputs=checked_producer(producer_receipt)
    _,owner_inputs,impact=owner_receipt(owner_qualification,producer);inputs.update(owner_inputs)
    if read_json(engine_directory/'build.json')['qualification_sha256']!=digest(producer_receipt):
        raise ValueError('AF09 guarded engine/producer receipt association')
    engine_record=read_json(engine_directory/'build.json')
    inputs.update(engine_record['inputs'])
    inputs[str(engine_directory/'SHA256SUMS')]=engine_seal
    inputs.update({str(engine_directory/name):expected for name,expected in launch.closure(engine_directory,engine_seal)[1].items()})
    tools=dict(producer['tools'])
    for name,tool in engine_record['tools'].items():
        if name in tools and tools[name]!=tool:raise ValueError('AF09 guarded tool selection conflict')
        tools[name]=tool
    if 'zig' not in tools:raise ValueError('AF09 guarded engine lacks pinned Zig')
    inputs[str(Path(__file__).resolve())]=digest(__file__)
    inputs[str(ROOT/'tests/test_fs_home_inputs.py')]=digest(ROOT/'tests/test_fs_home_inputs.py')
    inputs[str(ROOT/'userland/experiments/command-runner/process.py')]=PROCESS_PIN
    # Freeze the actual native kernel build graph before any child runs. The
    # dependency contains hashes, not copies of these current source trees.
    for directory in ('kernel','user','scripts'):
        inputs.update({str(p):digest(p) for p in sorted((ROOT/directory).rglob('*'))
            if p.is_file() and '__pycache__' not in p.parts and p.name!='.DS_Store'})
    inputs.update({str(p):digest(p) for p in required_sources()})
    verify_map(inputs)
    work=Path(tempfile.mkdtemp(prefix='fs-home-inputs-',dir=ROOT/'userland/build'))
    detail['work']=str(work)
    detail['work_identity']=directory_identity(work)
    detail.update(status='preparing',native_executed=False,inputs=inputs,tools=tools,rows=[],commands=[],
        destination=str(destination),producer_receipt=str(Path(producer_receipt).absolute()),owner_receipt=str(Path(owner_qualification).absolute()),
        owner_reuse=impact,work=str(work))
    deadline=time.monotonic()+1800
    proc=launch.CleanupTrackedProcess(owned_runner(),detail)
    command=command_runner(work,proc,tools,deadline,detail)
    destination.mkdir();detail['destination_created']=True
    detail['destination_identity']=directory_identity(destination)
    try:
        owner_builder=runpy.run_path(str(ROOT/'sys-init/scripts/home_owner_build.py'))
        owner=owner_builder['build'](ROOT,work,proc,tools,deadline,detail)
        probe=runpy.run_path(str(S/'home_probe_build.py'))['build'](work,proc,tools,deadline,detail)
        if launch.process_cleanup_unresolved(detail):
            raise RuntimeError('AF09 guarded imported cleanup unconfirmed')
        merge_dependency_inputs(detail,probe)
        # Imported builders return owned artifacts and retain all original
        # processes. Promote their outcomes without erasing expected denials.
        for row in detail['rows']:
            p=row['process'];expected=row.get('expected_exit',0)
            if p['exit']!=expected or not p['complete'] or p['cleanup']!='complete':
                raise RuntimeError('AF09 guarded imported builder child')
        for name,source in [('owner.elf',owner['elf']),('owner.bin',owner['raw']),('shell.elf',probe['shell']),('helper.elf',probe['helper'])]:
            shutil.copyfile(source,destination/name)
        (destination/'envelope.bin').write_bytes(envelope(Path(engine['elf']).read_bytes(),
            (destination/'shell.elf').read_bytes(),(destination/'helper.elf').read_bytes(),(destination/'owner.bin').read_bytes()))
        owner_pair(destination,owner['measurement'],command,tools)
        admission=admit(destination,Path(engine['elf']),work,command,tools)
        flags=kernel_flags()
        command('actual-kernel-build',[tools['zig']['path'],'build','-p',work/'kernel-build',
            '--cache-dir',work/'zig-cache','--global-cache-dir',ROOT/'.zig-cache/global','-Dsmp=false',
            '-Dnative-c-image='+str(destination/'envelope.bin'),*['-D'+f+'=true' for f in flags]])
        kernel=dict(sha256=digest(work/'kernel-build/bin/aether'),native_executed=False,flags=flags)
        verify_map(detail['inputs'])
        launch.intake(engine_directory,engine_seal)
        launch.checked_receipt(producer_receipt,'producer');owner_receipt(owner_qualification,producer)
        commands=list(detail['commands'])
        for row in detail['rows']:
            commands.append(dict(label=row['label'],status='pass',process=row['process'],expected_exit=row.get('expected_exit',0)))
        selected=dict(format=SCHEMA,status='prepared',native_executed=False,profile=dict(PROFILE),bounds=dict(BOUNDS),
            engine=dict(directory=str(engine_directory.relative_to(ROOT)),seal=engine_seal,elf_sha256=engine['elf_sha256']),
            producer_receipt=dict(path=str(Path(producer_receipt).absolute()),sha256=digest(producer_receipt)),
            owner_receipt=dict(path=str(Path(owner_qualification).absolute()),sha256=digest(owner_qualification)),owner_reuse=impact,
            measurement=owner['measurement'],admission=admission,
            artifacts={n:dict(sha256=digest(destination/n),bytes=(destination/n).stat().st_size) for n in ARTIFACTS},
            inputs=detail['inputs'],tools=tools,commands=commands,kernel_build=kernel,final_input_verification='pass')
        validate_record(selected)
        (destination/'inputs.json').write_text(json.dumps(selected,indent=2)+'\n')
        (destination/'SHA256SUMS').write_text(''.join(digest(destination/n)+'  '+n+'\n' for n in sorted((*ARTIFACTS,'inputs.json'))))
        seal=digest(destination/'SHA256SUMS')
        # Intake reparses the final retained bytes; publication never relies on
        # a pre-copy artifact or a parser report from the original builder.
        result=intake(destination,seal,deadline=deadline)
        if time.monotonic()>deadline:raise RuntimeError('AF09 guarded target deadline after verification')
        detail.update(status='pass',final_input_verification='pass',result=result,artifacts=selected['artifacts'])
    except BaseException as error:
        detail.update(status='failed',error=type(error).__name__+': '+str(error))
        raise
    return dict(result,receipt=str(receipt))


def directory_identity(path):
    st=Path(path).lstat()
    if Path(path).is_symlink() or not Path(path).is_dir():raise ValueError('AF09 owned directory identity')
    return [st.st_dev,st.st_ino]


def remove_owned(path,identity,errors,label):
    try:
        if not path.exists() and not path.is_symlink():return
        if identity is None or directory_identity(path)!=identity:
            raise ValueError('owned directory identity changed; foreign output preserved')
        shutil.rmtree(path)
    except BaseException as error:
        errors.append(dict(label=label,path=str(path),error=type(error).__name__+': '+str(error)))


def finish_attempt(detail,receipt,errors,primary):
    unresolved=launch.process_cleanup_unresolved(detail,primary)
    detail['cleanup']='unresolved' if unresolved else 'failed' if errors else 'complete'
    if unresolved:
        launch.retain_unresolved(detail,[],primary)
        detail.setdefault('error','AF09 child cleanup unconfirmed')
    if errors:
        detail['status']='failed';detail['cleanup_errors']=errors
        detail.setdefault('error','AF09 owned cleanup failed')
    try:receipt.write_text(json.dumps(detail,indent=2)+'\n')
    except BaseException as error:
        if errors:error.add_note('AF09 cleanup failures: '+json.dumps(errors))
        if primary is None:raise
        primary.add_note('AF09 receipt write failed: '+type(error).__name__+': '+str(error))
    if errors or unresolved:
        message=('AF09 child cleanup unconfirmed' if unresolved else 'AF09 owned cleanup failed')+'; see '+str(receipt)
        if primary is None:
            error=RuntimeError(message)
            if unresolved:launch.retain_unresolved(detail,[],error)
            raise error
        primary.add_note(message)


def next_receipt(directory):
    indices=[int(p.stem.split('-')[-1]) for p in directory.glob('attempt-*.json')]
    path=directory/('attempt-%02d.json'%(max(indices,default=0)+1))
    with path.open('x') as stream:stream.write('{"status":"starting"}\n')
    return path


def build(destination,engine_directory,engine_seal,producer_receipt,owner_qualification):
    evidence=ROOT/'userland/docs/evidence/filesystem-home-prep-2026-10-24/guarded-inputs/build'
    evidence.mkdir(parents=True,exist_ok=True)
    receipt=next_receipt(evidence)
    detail=dict(status='preflight',native_executed=False,destination=str(destination),commands=[])
    try:
        return _build(destination,engine_directory,engine_seal,producer_receipt,owner_qualification,detail,receipt)
    except BaseException as error:
        detail.update(status='failed',error=type(error).__name__+': '+str(error))
        raise
    finally:
        primary=sys.exception()
        errors=[]
        if launch.process_cleanup_unresolved(detail,primary):
            paths=[detail.get('work')]
            if detail.get('destination_created'):paths.append(detail['destination'])
            launch.retain_unresolved(detail,paths,primary)
        else:
            if detail.get('work'):
                remove_owned(Path(detail['work']),detail.get('work_identity'),errors,'work')
            if errors:detail['status']='failed'
            if detail.get('destination_created') and detail['status']!='pass':
                remove_owned(Path(detail['destination']),detail.get('destination_identity'),errors,'destination')
        try:
            finish_attempt(detail,receipt,errors,primary)
        except BaseException as error:
            # A receipt publication error also makes a newly built dependency
            # unsuccessful. Its ownership flag is independent of mkdir failure.
            if primary is None and detail['status']=='pass' and detail.get('destination_created'):
                detail.update(status='failed',error='receipt publication failed: '+type(error).__name__+': '+str(error))
                remove_owned(Path(detail['destination']),detail.get('destination_identity'),errors,'destination')
                detail['cleanup']='failed' if errors else 'complete'
                if errors:detail['cleanup_errors']=errors
                try:receipt.write_text(json.dumps(detail,indent=2)+'\n')
                except BaseException as write_error:error.add_note('Failure receipt unavailable: '+str(write_error))
            raise


def main():
    class Parser(argparse.ArgumentParser):
        def error(self,message):
            self.print_usage(sys.stderr);self.exit(64,'[ERROR] '+ascii(message)[1:-1]+'\n')
    parser=Parser(description=__doc__,epilog='Offline preparation only. Keep the compact receipt; correct failed prerequisites before a new output. Guest execution requires a fresh disposition.')
    parser.add_argument('--version',action='version',version='aether-fs-home-inputs 1')
    parser.add_argument('--engine',required=True,type=Path)
    parser.add_argument('--engine-seal',required=True)
    parser.add_argument('--producer-receipt',required=True,type=Path)
    parser.add_argument('--owner-receipt',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path,help='unused .deps/fs-owner-af09-* dependency')
    args=parser.parse_args()
    print(json.dumps(build(args.output,args.engine,args.engine_seal,args.producer_receipt,args.owner_receipt)))


if __name__=='__main__':
    try:main()
    except ValueError as error:
        print('[BLOCKED] '+ascii(str(error))[1:-1],file=sys.stderr);raise SystemExit(2)
    except (OSError,RuntimeError) as error:
        print('[ERROR] '+ascii(str(error))[1:-1],file=sys.stderr);raise SystemExit(1)
