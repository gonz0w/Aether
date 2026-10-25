#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Build the separate sealed AF07 operational owner; execute no guest."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from deps import ROOT, verify
from fs_launch import labels, origins, recipe, validate_destination
from fs_launch_intake import intake as old_launch_intake
import openzfs_fs_metadata_service as metadata
from service_runtime_smoke import sealed
from source_paths import dependency_input, relocate

OWNER = ROOT / 'userland/build/service-deliveries/filesystem-af07-owner-2026-10-21-v1'
OWNER_SEAL = 'a5113edeb55d6ae38905bca047cbf6c290dc0ff25ab958556840194586a5b052'
OWNER_OBJECT = '10e401f8f5aaf7c33ce70081abb5cec2a310598ec17811325728c4c0c2604b7b'
CURRENT = ROOT/'.deps/fs-launch-2026-10-20-v4'
SCHEMA = 'aether-fs-metadata-launch-build-v1'
REQUIRED = {'main':'launch-metadata-owner.o', 'aether_fs_launch_serve':'launch-metadata-owner.o',
            'aether_fs_engine_run':'filesystem-engine.o', 'aether_fs_engine_import':'filesystem-import.o',
            'aether_fs_metadata_run':'launch-engine.o', 'aether_zpl_getattr':'launch-engine.o',
            'spa_import':'launch-engine.o', 'spa_export':'launch-engine.o'}
FORBIDDEN = {'aether_fs_owner_probe','aether_pool_namespace_write','aether_spa_import_probe',
             'aether_fs_directories_run'}
FRAME_FILES = {'pool-launch-label.su','metadata-provider.su','filesystem-import.su','filesystem-engine.su'}


def closure(directory, expected, count=None):
    root = Path(directory).absolute()
    if root.resolve() != root or not root.is_dir():
        raise ValueError('AF07 launch requires a real directory')
    manifest = root/'SHA256SUMS'
    if manifest.is_symlink() or manifest.stat().st_size > 1024*1024:
        raise ValueError('AF07 launch manifest path/size')
    members = sealed(root, expected, count if count is not None else len(manifest.read_text().splitlines()))
    actual = set()
    for path in root.rglob('*'):
        if path.is_symlink():
            raise ValueError('AF07 launch symlink')
        if path.is_file():
            actual.add(str(path.relative_to(root)))
    if actual != members.keys() | {'SHA256SUMS'}:
        raise ValueError('AF07 launch member closure')
    return root, members


def owner_intake(directory=OWNER):
    root, members = closure(directory, OWNER_SEAL, 18)
    if members.get('objects/launch-metadata-owner.o') != OWNER_OBJECT:
        raise ValueError('AF07 owner object identity')
    data = json.loads((root/'inputs.json').read_text())
    build = json.loads((root/'build.json').read_text())
    service = metadata.intake()
    dependency = dict(format='aether-af07-owner-dependency-v1',
        relative_directory='../filesystem-service-metadata-2026-10-21-v1',
        manifest_sha256=metadata.SEAL, members=77, object='objects/filesystem-metadata.o',
        object_sha256=metadata.OBJECT, protocol='AFSRPC07', entry='aether_fs_metadata_run',
        root_rights=31, launch_state_bytes=136, service_result_bytes=72)
    if (data.get('format') != 'aether-af07-operational-owner-input-v1'
            or json.loads((root/'dependency.json').read_text()) != dependency
            or build.get('native_executed') is not False or build.get('full_engine_linked') is not False):
        raise ValueError('AF07 owner dependency/coverage')
    for version in ('minimum','current'):
        row = build.get(version,{})
        if (row.get('status') != 'pass' or row.get('native_executed') is not False
                or row.get('full_engine_linked') is not False or row.get('native_object_sha256') != OWNER_OBJECT
                or row.get('native_object_bytes') != (root/'objects/launch-metadata-owner.o').stat().st_size):
            raise ValueError('AF07 owner compiler/object coverage')
    inputs = {str(root/'SHA256SUMS'):OWNER_SEAL, **{str(root/n):h for n,h in members.items()}, **service['inputs']}
    for name, checksum in data['sources'].items():
        if members.get('source/'+Path(name).name) != checksum:
            raise ValueError('AF07 owner source snapshot')
    for name in ('filesystem-engine.h','metadata-service.h','native-service.h'):
        source = metadata.SERVICE/name if name=='filesystem-engine.h' else Path(service['root'])/'source'/name
        if metadata.digest(source) != members.get('abi/'+name):
            raise ValueError('AF07 owner ABI: '+name)
        inputs[str(source)] = members['abi/'+name]
    # Historical STATE/builder hashes describe what the producer inspected.
    # Only these unchanged engine contracts are active composition prerequisites.
    before = data['producer_and_before']['producer']
    for name in ('user/storage/service-runtime/filesystem-engine.c',
                 'user/storage/openzfs-volume/filesystem-import.c'):
        if metadata.digest(ROOT/name) != before[name]:
            raise ValueError('AF07 owner engine contract: '+name)
        inputs[str(ROOT/name)] = before[name]
    for name, checksum in ({v['path']:v['sha256'] for v in data['tools'].values()}
            | data['rust_native_libraries'] | data['clang_resource_headers']).items():
        if not Path(name).is_absolute() or metadata.digest(Path(name)) != checksum:
            raise ValueError('AF07 owner tool/library: '+name)
        inputs[name] = checksum
    return dict(root=str(root),manifest_sha256=OWNER_SEAL,object=str(root/'objects/launch-metadata-owner.o'),
                object_sha256=OWNER_OBJECT,source=str(root/'source/launch-metadata-owner.rs'),
                inputs=inputs,tools=data['tools'],service=service,native_acceptance=False)


def strong_symbols(symbols, required=REQUIRED):
    for name in required:
        rows = [line.split() for line in symbols.splitlines() if line.split()[-1:]==[name]]
        if len(rows)!=1 or len(rows[0])!=3 or rows[0][1]!='T':
            raise ValueError('AF07 launch strong definition: '+name)
    if any(line.split()[-1] in FORBIDDEN for line in symbols.splitlines() if line.strip()):
        raise ValueError('AF07 launch retained old service/fixture')


def check_frames(frames):
    if set(frames)!=FRAME_FILES or any('dynamic' in text or not text.strip() or
            any(int(row.split('\t')[1])>8192 for row in text.splitlines()) for text in frames.values()):
        raise ValueError('AF07 launch local frame bound; not full stack proof')


def intake(directory, expected):
    root, members = closure(directory, expected)
    required = {'build.json','preparation.json','filesystem.elf','SOURCE.md',
                'notices/openzfs/LICENSE','notices/openzfs/COPYRIGHT','notices/openzfs/NOTICE',
                'notices/COPYRIGHT.musl','notices/LICENSE'}
    if not required <= members.keys():
        raise ValueError('AF07 launch required closure')
    record = json.loads((root/'build.json').read_text())
    if (record.get('schema') != SCHEMA or record.get('status') != 'pass' or record.get('executed') is not False
            or record.get('owner_manifest_sha256') != OWNER_SEAL or record.get('service_manifest_sha256') != metadata.SEAL
            or record.get('elf_sha256') != members['filesystem.elf']
            or record.get('elf_bytes') != (root/'filesystem.elf').stat().st_size
            or set(record.get('origins',{})) != REQUIRED.keys()
            or any(Path(record['origins'][k]).name != v for k,v in REQUIRED.items())
            or not record.get('structural_loader','').startswith('ELF structural pages=')):
        raise ValueError('AF07 launch build identity/coverage')
    owner = owner_intake()
    recorded_inputs = {str(relocate(n)): h for n, h in record.get('inputs', {}).items()}
    if len(recorded_inputs) != len(record.get('inputs', {})):
        raise ValueError('AF07 launch relocated input collision')
    if not record.get('commands') or any(recorded_inputs.get(n)!=h for n,h in owner['inputs'].items()):
        raise ValueError('AF07 launch missing consumed closure')
    check_frames(record.get('local_frames',{}))
    for name, checksum in record['inputs'].items():
        if not Path(name).is_absolute() or metadata.digest(dependency_input(name, checksum)) != checksum:
            raise ValueError('AF07 launch consumed input drift: '+name)
    return dict(manifest_sha256=expected,elf=str(root/'filesystem.elf'),elf_sha256=members['filesystem.elf'],
                members=len(members),executed=False,native_acceptance=False,
                scope='AF07 linked/loader candidate only; operational native and sys-init qualification pending')


def destination_path(destination):
    destination = validate_destination(destination)
    if not destination.name.startswith('fs-launch-af07-'):
        raise ValueError('AF07 launch requires an unused .deps/fs-launch-af07-* destination')
    return destination


def build(destination):
    destination = destination_path(destination)
    owner = owner_intake()
    old = old_launch_intake(CURRENT)
    verify()
    tools = json.loads((ROOT/'.deps/native-current/sdk/tools.lock.json').read_text())['tools']
    temporary = Path(tempfile.mkdtemp(prefix='fs-metadata-launch-',dir=ROOT/'zig-out'))
    work = temporary/'launch';work.mkdir()
    result = dict(schema=SCHEMA,status='preparing',executed=False,commands=[],inputs=dict(owner['inputs']),
        owner_manifest_sha256=OWNER_SEAL,service_manifest_sha256=metadata.SEAL,tools=tools,
        scope='Separate operational AF07 ELF link/intake only; no VM/sys-init/release acceptance')
    result['inputs'].update({str(p):metadata.digest(p) for directory in ('user','kernel','scripts')
        for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='.DS_Store'})
    result['inputs'][str(ROOT/'.deps/native-current/current-inputs.json')] = metadata.digest(ROOT/'.deps/native-current/current-inputs.json')
    destination.mkdir()
    def command(argv, log, rejection=None):
        args = list(map(str,argv))
        with Path(log).open('w') as stream:
            try:run = subprocess.run(args,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,timeout=180)
            except subprocess.TimeoutExpired:
                result['commands'].append(dict(argv=args,status='timeout',seconds=180,
                    log_sha256=metadata.digest(Path(log)),tail=Path(log).read_text(errors='replace')[-4000:]));raise
        text = Path(log).read_text(errors='replace')
        bad = (run.returncode==0 or rejection not in text) if rejection else run.returncode!=0
        result['commands'].append(dict(argv=args,exit_code=run.returncode,expected_rejection=rejection,
            log_sha256=metadata.digest(Path(log)),tail=text[-4000:] if bad else text[-160:]))
        if bad:raise RuntimeError('AF07 launch build failed: '+str(log))
        return text
    try:
        print('[RUNNING] AF07 operational link preparation: '+str(temporary),file=sys.stderr,flush=True)
        preparation = metadata.prepare_engine(temporary/'base',command,tools)
        compose(temporary/'base',preparation,owner,work,destination,command,result)
        for name, checksum in result['inputs'].items():
            if metadata.digest(Path(name)) != checksum:raise ValueError('AF07 launch input drift: '+name)
        if owner_intake()!=owner or old_launch_intake(CURRENT)!=old:
            raise ValueError('AF07 launch owner/default drift')
        result.update(status='pass',elf_sha256=metadata.digest(destination/'filesystem.elf'),
                      elf_bytes=(destination/'filesystem.elf').stat().st_size)
    except BaseException as error:
        result.update(status='failed',error=str(error));raise
    finally:
        result['cleanup']=dict(native_attempted=False,removed_generated_members=sum(p.is_file() for p in temporary.rglob('*')))
        shutil.rmtree(temporary)
        if result['status']!='pass':
            for path in destination.iterdir():
                if path.is_dir():shutil.rmtree(path)
                else:path.unlink()
        (destination/'build.json').write_text(json.dumps(result,indent=2)+'\n')
    members = sorted(p for p in destination.rglob('*') if p.is_file())
    (destination/'SHA256SUMS').write_text(''.join(metadata.digest(p)+'  '+str(p.relative_to(destination))+'\n' for p in members))
    return intake(destination,metadata.digest(destination/'SHA256SUMS'))


def compose(base, preparation, owner, work, destination, command, result, context_provider=False):
    port = base/'port'
    selected = owner['service']
    cc = recipe(preparation,'zpl-mutation.o');cc = cc[:cc.index('-c')]
    (work/'namespace-launch-label.inc').write_text(labels((metadata.VOLUME/'namespace-label.inc').read_text()))
    label = metadata.replace((metadata.VOLUME/'pool-label.c').read_text(),
                             '#include "namespace-label.inc"','#include "namespace-launch-label.inc"')
    (work/'pool-launch-label.c').write_text(label)
    label_cc = recipe(preparation,'pool-label.o');label_cc = label_cc[:label_cc.index('-c')]
    command(label_cc+['-I'+str(work),'-fstack-usage','-c',work/'pool-launch-label.c',
                      '-o',work/'pool-launch-label.o'],work/'label.log')
    command(cc+['-c',metadata.VOLUME/('zpl-context.c' if context_provider else 'zpl-metadata.c'),'-o',work/'metadata-provider.o'],work/'provider.log')
    includes = ['-I'+str(metadata.SERVICE),'-I'+str(Path(selected['root'])/'source'),'-I'+str(metadata.VOLUME)]
    command(label_cc+includes+['-fstack-usage','-c',metadata.VOLUME/'filesystem-import.c',
                              '-o',work/'filesystem-import.o'],work/'import.log')
    startup = recipe(preparation,'engine-startup.o')
    command(startup[:startup.index('-c')]+includes+['-fstack-usage','-c',metadata.SERVICE/'filesystem-engine.c',
                                                 '-o',work/'filesystem-engine.o'],work/'startup.log')
    command([owner['tools']['rustc']['path'],'--edition=2021','--target=x86_64-unknown-none','--crate-type=lib',
        '--emit=obj','-Copt-level=2','-Cpanic=abort','-Crelocation-model=static','-Cno-redzone=yes','-Ccodegen-units=1',
        '-Dwarnings','-Dunsafe_op_in_unsafe_fn',owner['source'],'-o',work/'rebuilt-owner.o'],work/'owner.log')
    if metadata.digest(work/'rebuilt-owner.o')!=OWNER_OBJECT:
        raise ValueError('AF07 launch rebuilt owner differs from sealed Rustc object')
    shutil.copyfile(owner['object'],work/'launch-metadata-owner.o')
    partial = recipe(preparation,'selected-libzpool.o')
    replacements = {preparation['old_service']['object']:selected['object'],
        str(port/'zpl-mutation.o'):str(work/'metadata-provider.o'),str(port/'pool-label.o'):str(work/'pool-launch-label.o')}
    if any(partial.count(name)!=1 for name in replacements):raise ValueError('AF07 launch exact partial input replacement')
    partial = [replacements.get(p,'-Map='+str(work/'partial.map') if p.startswith('-Map=') else p) for p in partial]
    partial[-1]=str(work/'launch-libzpool.o');command(partial,work/'partial.log')
    result['partial_origins']=origins((work/'partial.map').read_text(),
        {'aether_fs_metadata_run':'filesystem-metadata.o','aether_zpl_getattr':'metadata-provider.o',
         'aether_pool_label_config':'pool-launch-label.o'})
    engine = recipe(preparation,'selected-engine.o')
    engine = [str(work/'launch-libzpool.o') if p==str(port/'selected-libzpool.o') else p for p in engine]
    engine[-1]=str(work/'launch-engine.o');command(engine,work/'engine.log')
    link = recipe(preparation,'engine.elf')
    for p in link:
        if p.endswith(('.a','.o')) and not Path(p).is_relative_to(base):result['inputs'][p]=metadata.digest(Path(p))
    if link.count(str(port/'engine-startup.o'))!=1 or link.count(str(port/'selected-engine.o'))!=1:
        raise ValueError('AF07 launch exact startup/engine replacement')
    final=[]
    for arg in link:
        if arg==str(port/'engine-startup.o'):
            final.extend(map(str,(work/'launch-metadata-owner.o',work/'filesystem-engine.o',work/'filesystem-import.o')))
        else:final.append(str(work/'launch-engine.o') if arg==str(port/'selected-engine.o') else
                          '-Map='+str(work/'launch.map') if arg.startswith('-Map=') else arg)
    final[-1]=str(destination/'filesystem.elf');command(final,work/'link.log')
    result['origins']=origins((work/'launch.map').read_text(),REQUIRED)
    llvm = Path(result['tools']['clang']['path']).parent
    elf = destination/'filesystem.elf'
    symbols=command([llvm/'llvm-nm','--defined-only',elf],work/'symbols.log');strong_symbols(symbols)
    imports=command([llvm/'llvm-nm','-u',elf],work/'imports.log')
    if any(line.split()[-1]!='_DYNAMIC' for line in imports.splitlines() if line.strip()):
        raise ValueError('AF07 launch unresolved import')
    reloc=command([llvm/'llvm-readelf','-rW',elf],work/'relocations.log')
    if reloc.strip()!='There are no relocations in this file.':raise ValueError('AF07 launch runtime relocations')
    result['segments']=command([llvm/'llvm-readelf','-lW',elf],work/'segments.log')
    shutil.copyfile(elf,work/'filesystem.elf')
    (work/'image-check.zig').write_text(metadata.replace((port/'image-check.zig').read_text(),
        '@embedFile("engine.elf")','@embedFile("filesystem.elf")'))
    result['structural_loader']=command(['zig','run','--cache-dir',ROOT/'.zig-cache','--global-cache-dir',ROOT/'.zig-cache/global',
        '-O','ReleaseSafe','--dep','native_elf','-Mroot='+str(work/'image-check.zig'),
        '-Mnative_elf='+str(ROOT/'kernel/native_elf.zig')],work/'loader.log').strip()
    result['local_frames']={p.name:p.read_text() for p in work.glob('*.su')}
    check_frames(result['local_frames'])
    result['map_sha256']=metadata.digest(work/'launch.map')
    upstream=ROOT/'.deps/native-current/baseline/source/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1'
    for directory in (Path(selected['root'])/'notices',Path(owner['root'])/'notices'):
        for path in directory.rglob('*'):
            if path.is_file():
                target=destination/'notices'/path.relative_to(directory);target.parent.mkdir(parents=True,exist_ok=True)
                if target.exists() and metadata.digest(target)!=metadata.digest(path):raise ValueError('AF07 launch notice collision')
                shutil.copyfile(path,target)
    notices=[(upstream/n,Path('openzfs')/n) for n in ('LICENSE','COPYRIGHT','NOTICE')]
    notices += [(p,Path('openzfs')/p.relative_to(upstream)) for p in sorted(upstream.glob('module/**/THIRDPARTYLICENSE*'))]
    notices += [(ROOT/'.deps/native-current/sdk/COPYRIGHT.musl',Path('COPYRIGHT.musl')),(ROOT/'LICENSE',Path('LICENSE'))]
    for path,name in notices:
        result['inputs'][str(path)]=metadata.digest(path)
        target=destination/'notices'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
    (destination/'SOURCE.md').write_text('# Separate AF07 filesystem launch candidate\n\n'
        'First-party BSD-2-Clause; OpenZFS remains CDDL with original mixed notices.\n'
        'Musl/Rust/compiler payloads keep their own terms. No whole-image relicensing.\n'
        'Pinned OpenZFS:71a9f9578616a90c3c14bb59629fb4d31bfd68d1.\n'
        'Original C engine/import/provider and scoped label adapter: Aether user/storage;\n'
        'sealed Rust owner/service: Aether-userland delivery hashes in build.json.\n'
        'Rebuild via scripts/fs_metadata_launch.py with pinned offline SDK inputs.\n'
        'This local dependency is not public distribution approval; matching modified\n'
        'CDDL source must accompany an actual public release. No native acceptance.\n')
    (destination/'preparation.json').write_text(json.dumps(dict(executed=False,case=preparation['case'],
        commands=len(preparation['commands']),summary='Verified unexecuted AF06 object preparation; explicit AF07 replacements recorded in build.json'),indent=2)+'\n')


if __name__=='__main__':
    class Parser(argparse.ArgumentParser):
        def error(self,message):
            print('[ERROR] '+ascii(message)[1:-1],file=sys.stderr);raise SystemExit(64)
    parser=Parser(description=__doc__)
    parser.add_argument('--version',action='version',version='aether-fs-metadata-launch 1')
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    try:print(json.dumps(build(args.output)))
    except (ValueError,OSError,RuntimeError,subprocess.SubprocessError) as error:
        print('[ERROR] '+ascii(str(error))[1:-1],file=sys.stderr);raise SystemExit(1)
