#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Prepare three fixed AF09 images and offline prospective oracles; execute no guest."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import struct
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import fs_home_inputs as inputs
import fs_home_launch as launch
import home_reader
from fs_session import FLAGS

SCHEMA='aether-home-owner-prepared-v1'
PREFIX='af09-home-owner-pending-'
RTC='2026-10-06T12:34:00,clock=vm'
SCRIPT=b"printf 'AF09-BEGIN\\n'\n/inputs/helper status\nprintf 'AF09-STATUS:%s\\n' \"$?\"\nexit\n"
ORIGINAL_CONTROLLER_SHA256='1e6dcce43abcf3aa321ec9931518b7560b5417e95374dbf5e12a094e8a990532'
CONTROLLER=ROOT/'user/storage/session/home-readback.rs'
WRITER_FLAGS=(*FLAGS,'native-fs-session-init','native-fs-owner-data','native-fs-owner-stack')
READER_FLAGS=tuple('''native-memory native-memory-large native-image-large native-backing
native-service-memory native-threads native-thread-pair native-thread-reuse
native-thread-origin native-service-workers native-clock native-entropy native-rtc
native-service-block native-service-cleanup-trace'''.split())
PROCESS=ROOT/'userland/experiments/command-runner/process.py'
PROCESS_SHA256='9f0c0464c10fa23bfc7c3c91fe26b04e5ab063ca058eeb6d41542d98c6186e4e'
DIAGNOSTIC_LIMIT=4*1024*1024


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def geometry(admission):
    wanted={'engine_pages','shell_pages','helper_pages','owner_bytes'}
    if not isinstance(admission,dict) or set(admission)!=wanted or any(type(admission[k]) is not int for k in wanted):
        raise ValueError('AF09 exact measured geometry missing')
    if (not 16<admission['engine_pages']<=2048 or not 16<admission['shell_pages']<=128
            or not 16<admission['helper_pages']<=128 or not 0<admission['owner_bytes']<=49152):
        raise ValueError('AF09 measured geometry/budget or old profile rejected')
    return admission['engine_pages'],admission['shell_pages'],admission['helper_pages']


def transcript(text):
    if not isinstance(text,str) or len(text.encode())>65536 or not text.endswith('AETHER NATIVE BLOCK PASS\n'):
        raise ValueError('AF09 exact complete bounded transcript required')
    if any(token in text for token in ('PANIC','NATIVE fault ','\x00')):
        raise ValueError('AF09 transcript contains failed/malformed execution')
    lines=text.split('\n')[:-1]
    if lines.count('AETHER NATIVE BLOCK PASS')!=1:
        raise ValueError('AF09 completion count')
    return lines


def exact_rows(lines,prefix,pattern):
    selected=[line for line in lines if line.startswith(prefix)]
    result=[]
    for line in selected:
        match=re.fullmatch(pattern,line)
        if match is None:raise ValueError('AF09 malformed '+prefix)
        result.append(tuple(map(int,match.groups())))
    return result


def reader_trace(text,engine_pages):
    """Validate controlled or supplied records; no media or execution is inferred."""
    if type(engine_pages) is not int or not 16<engine_pages<=2048:
        raise ValueError('AF09 reader exact measured pages required')
    lines=transcript(text)
    rows=exact_rows(lines,'NATIVE observation',r'NATIVE observation slot=(\d+) generation=(\d+) offset=(\d+) byte=(\d+)')
    expected=[(0,g,i*8) for g,count in ((1,32),(2,3),(3,3)) for i in range(count)]
    if [row[:3] for row in rows]!=expected or any(not 0<=row[3]<=255 for row in rows):
        raise ValueError('AF09 full32-byte digest/guard observation order or extent')
    if bytes(row[3] for row in rows[32:])!=b'BNRBNR':
        raise ValueError('AF09 denied generations BNR missing')
    admitted=exact_rows(lines,'NATIVE MEMORY admitted',r'NATIVE MEMORY admitted slot=(\d+) generation=(\d+) used=(\d+) remaining=(\d+)')
    if admitted!=[(0,g,engine_pages,8192-engine_pages) for g in (1,2,3)]:
        raise ValueError('AF09 reader exact measured admission/reuse')
    terminals=exact_rows(lines,'NATIVE terminal',r'NATIVE terminal slot=(\d+) generation=(\d+) kind=(\d+) detail=(\d+)')
    if terminals!=[(0,g,1,0) for g in (1,2,3)]:
        raise ValueError('AF09 reader terminal identities/status')
    cleanup=exact_rows(lines,'NATIVE CLEANUP',r'NATIVE CLEANUP v=1 slot=(\d+) generation=(\d+) phase=(\d+) selected=(\d+) pages=(\d+) reclaimed=(\d+)')
    wanted=[(0,g,p,0 if p==1 else 2,8192,g if p==7 else g-1) for g in (1,2,3) for p in range(1,8)]
    if cleanup!=wanted:raise ValueError('AF09 reader full stop/reclaim sequence')
    if [line for line in lines if line.startswith('NATIVE supervisor')]!=['NATIVE supervisor result=100 reclaimed=3']:
        raise ValueError('AF09 reader controller/reclaim result')
    if any(line.startswith(('NATIVE init halted','NATIVE STORAGE WAIT')) for line in lines):
        raise ValueError('AF09 reader unexpected writer lifecycle rows')
    order=[]
    for g,count in ((1,32),(2,3),(3,3)):
        order += [f'NATIVE MEMORY admitted slot=0 generation={g} used={engine_pages} remaining={8192-engine_pages}']
        order += [f'NATIVE observation slot=0 generation={row[1]} offset={row[2]} byte={row[3]}' for row in rows if row[1]==g]
        order += [f'NATIVE terminal slot=0 generation={g} kind=1 detail=0']
        order += [f'NATIVE CLEANUP v=1 slot=0 generation={g} phase={p} selected={0 if p==1 else 2} pages=8192 reclaimed={g if p==7 else g-1}' for p in range(1,8)]
    order += ['NATIVE supervisor result=100 reclaimed=3','AETHER NATIVE BLOCK PASS']
    if [lines.index(line) for line in order]!=sorted(lines.index(line) for line in order):
        raise ValueError('AF09 reader admission/late-output/terminal/cleanup ordering')
    return dict(format='aether-af09-reader-transcript-v1',status='pass',metadata_sha256=bytes(row[3] for row in rows[:32]).hex(),generations=3,reclaimed=3,
        final_live_workers=0,cleanup_trace_version=1,cleanup_boundaries_per_generation=7,
        read_grant_only=True,readonly_pool_retired=True,clean_export_observed=False,
        native_executed=False,scope='Transcript parser only; row padding/resources checked by exact sealed controller')


def writer_trace(text,admission):
    """Fixed AF09 adaptation of the AF07 guarded terminal/cleanup/wait oracle."""
    engine_used,shell_used,helper_used=geometry(admission)
    lines=transcript(text)
    for marker in ('AF09-BEGIN','AF09-HOME-WR','AF09-STATUS:7'):
        if lines.count(marker)!=1:raise ValueError('AF09 exact shell/helper marker/status')
    if any(line.startswith(('AF07-','AF09-STATUS:','AF09-HOME-','AF09-BEGIN')) and line not in
        ('AF09-BEGIN','AF09-HOME-WR','AF09-STATUS:7') for line in lines):
        raise ValueError('AF09 extra/old workload output')
    admissions=exact_rows(lines,'NATIVE MEMORY admitted',r'NATIVE MEMORY admitted slot=(\d+) generation=(\d+) used=(\d+) remaining=(\d+)')
    if admissions!=[(0,1,engine_used,8192-engine_used),(1,1,shell_used,128-shell_used),(2,1,helper_used,128-helper_used)]:
        raise ValueError('AF09 exact loader identities/geometry')
    terminals=exact_rows(lines,'NATIVE terminal',r'NATIVE terminal slot=(\d+) generation=(\d+) kind=(\d+) detail=(\d+)')
    if terminals!=[(2,1,1,7),(1,1,1,0),(0,1,1,0)]:
        raise ValueError('AF09 exact helper/parent/engine terminal identities/order')
    wanted=[]
    for slot,pages,prior in ((2,128,0),(1,128,1),(0,8192,2)):
        wanted += [f'NATIVE CLEANUP v=1 slot={slot} generation=1 phase={phase} selected={slot if phase==1 else 6} pages={pages} reclaimed={prior+int(phase==7)}' for phase in range(1,8)]
    if [line for line in lines if line.startswith('NATIVE CLEANUP')]!=wanted:
        raise ValueError('AF09 complete cleanup order')
    halts=exact_rows(lines,'NATIVE init halted',r'NATIVE init halted ticks=(\d+) idle=(\d+) reclaimed=(\d+)')
    if len(halts)!=1 or not 0<halts[0][0]<=6000 or halts[0][2]!=3:
        raise ValueError('AF09 halt/tick/reclaim bound')
    if any(line.startswith(('NATIVE observation','NATIVE supervisor')) for line in lines):
        raise ValueError('AF09 writer unexpected conformance/controller observations')
    order=[next(line for line in lines if line.startswith(f'NATIVE MEMORY admitted slot={slot} ')) for slot in (0,1)]
    order += ['AF09-BEGIN',next(line for line in lines if line.startswith('NATIVE MEMORY admitted slot=2 ')),
        'AF09-HOME-WR','NATIVE terminal slot=2 generation=1 kind=1 detail=7',*wanted[:7],
        'AF09-STATUS:7','NATIVE terminal slot=1 generation=1 kind=1 detail=0',*wanted[7:14],
        'NATIVE terminal slot=0 generation=1 kind=1 detail=0',*wanted[14:],
        next(line for line in lines if line.startswith('NATIVE init halted ')),'AETHER NATIVE BLOCK PASS']
    if [lines.index(line) for line in order]!=sorted(lines.index(line) for line in order):
        raise ValueError('AF09 admission/workload/terminal/cleanup/output ordering')
    pending=set();owners=set();waits=wakes=0
    for line in lines:
        if not line.startswith('NATIVE STORAGE WAIT'):continue
        match=re.fullmatch(r'NATIVE STORAGE WAIT slot=(\d+) generation=(\d+) phase=(park|wake) status=0',line)
        if match is None:raise ValueError('AF09 wait syntax/status')
        slot,generation,phase=match.groups();key=int(slot),int(generation)
        if key not in ((0,1),(1,1),(2,1),(6,0)):raise ValueError('AF09 wait identity')
        if phase=='park':
            if key in pending:raise ValueError('AF09 duplicate park')
            pending.add(key);owners.add(key[0]);waits+=1
        else:
            if key not in pending:raise ValueError('AF09 unmatched wake')
            pending.remove(key);wakes+=1
    if pending or owners!={0,1,2,6} or waits!=wakes:
        raise ValueError('AF09 incomplete primary waits')
    return dict(format='aether-af09-writer-transcript-v1',status='pass',child_status=7,primary_channel_waits=waits,primary_channel_wakes=wakes,
        admitted_instances=3,reclaimed=3,engine_terminal_zero=True,helper_marker='AF09-HOME-WR',
        provider_attempts=3,provider_attempts_source='sealed fs_home_probe_three success predicate',
        native_executed=False,scope='Transcript parser only; mutation-attempt enforcement belongs to the sealed engine')


def media_snapshot(row):
    from openzfs_namespace import FIXTURE_BYTES
    if (not isinstance(row,dict) or row.get('status')!='captured' or row.get('bytes')!=FIXTURE_BYTES+8192
            or row.get('outside_region_canaries_match') is not True
            or any(not isinstance(row.get(name),str) or re.fullmatch('[0-9a-f]{64}',row[name]) is None
                   for name in ('sha256','region_sha256'))):
        raise ValueError('AF09 full owned stopped-media snapshot/canaries required')
    return row


def qualify_sequence(pristine,writer,recovery,media):
    """Prospective offline comparison; caller must supply actual stopped records."""
    from openzfs_namespace import FIXTURE_IMAGE_SHA256
    if (len(media)!=3 or [row.get('role') for row in media]!=['pristine','writer','recovery']
            or any(row.get('vm_stop_confirmed') is not True or row.get('vm_run_returned') is not True for row in media)):
        raise ValueError('AF09 exact stopped pristine/writer/recovery sequence required')
    for row in media:media_snapshot(row.get('before'));media_snapshot(row.get('after'))
    if (media[0]['before']!=media[0]['after'] or media[0]['before']['region_sha256']!=FIXTURE_IMAGE_SHA256
            or media[1]['before']!=media[0]['after'] or media[1]['after']==media[1]['before']
            or media[1]['after']['region_sha256']==FIXTURE_IMAGE_SHA256
            or media[2]['before']!=media[1]['after'] or media[2]['after']!=media[2]['before']):
        raise ValueError('AF09 pristine/changed/readonly media identity chain')
    required_reader=dict(format='aether-af09-reader-transcript-v1',status='pass',generations=3,reclaimed=3,final_live_workers=0,
        cleanup_trace_version=1,cleanup_boundaries_per_generation=7,read_grant_only=True,readonly_pool_retired=True)
    if any(any(type(row.get(key)) is not type(value) or row.get(key)!=value for key,value in required_reader.items()) for row in (pristine,recovery)):
        raise ValueError('AF09 complete independent reader outcomes required')
    required_writer=dict(format='aether-af09-writer-transcript-v1',status='pass',child_status=7,admitted_instances=3,reclaimed=3,engine_terminal_zero=True,
        helper_marker='AF09-HOME-WR',provider_attempts=3)
    if (any(type(writer.get(key)) is not type(value) or writer.get(key)!=value for key,value in required_writer.items())
            or type(writer.get('primary_channel_waits')) is not int or writer['primary_channel_waits']<=0
            or writer.get('primary_channel_wakes')!=writer['primary_channel_waits']):
        raise ValueError('AF09 complete actual writer outcomes required')
    a=pristine.get('metadata_sha256');b=recovery.get('metadata_sha256')
    if not isinstance(a,str) or re.fullmatch('[0-9a-f]{64}',a) is None or a!=b:
        raise ValueError('AF09 full preserved metadata SHA256 mismatch')
    return dict(status='pass',metadata_sha256=a,reader_media_unchanged=True,
        exact_stopped_writer_media=True,native_executed=False,
        scope='Supplied transcript/media validation only; no execution or durability claim')


def owned_process():
    if digest(PROCESS)!=PROCESS_SHA256:raise ValueError('AF09 owned process helper changed')
    spec=importlib.util.spec_from_file_location('af09_qualifier_owned_process',PROCESS)
    proc=importlib.util.module_from_spec(spec);spec.loader.exec_module(proc)
    return proc


def reserve_evidence():
    directory=ROOT/'userland/docs/evidence/filesystem-home-prep-2026-10-24/qualifier'
    directory.mkdir(parents=True,exist_ok=True)
    for number in range(1,10000):
        path=directory/('prepare-%02d.json'%number)
        try:path.touch(exist_ok=False);return path
        except FileExistsError:pass
    raise ValueError('AF09 evidence name bound')


def check_budget(deadline):
    remaining=deadline-time.monotonic()
    if remaining<=0:raise RuntimeError('AF09 image preparation total deadline')
    return remaining


def input_record(directory,seal,*,deadline):
    check_budget(deadline)
    result=inputs.intake(directory,seal,deadline=deadline)
    check_budget(deadline)
    record=inputs.read_json(Path(directory)/'inputs.json')
    if (result.get('format')!=inputs.SCHEMA or record.get('format')!=inputs.SCHEMA
            or record.get('profile')!=inputs.PROFILE or record.get('bounds')!=inputs.BOUNDS):
        raise ValueError('AF09 exact guarded selection required')
    geometry(record['admission'])
    check_budget(deadline)
    return record


def explicit_linker(args):
    values=[arg.removeprefix('linker=') for arg in args if arg.startswith('linker=')]
    values += [arg.removeprefix('-Clinker=') for arg in args if arg.startswith('-Clinker=')]
    if len(values)>1:raise ValueError('AF09 ambiguous explicit Rust linker')
    return values[0] if values else None


def verify_child(args,tools,generated):
    """Every executed tool and live generated runtime input stays byte-exact."""
    selected={row['path']:row['sha256'] for row in tools.values()}
    paths=[args[0]]
    linker=explicit_linker(args)
    if linker is not None:paths.append(linker)
    for path in paths:
        if path not in selected:raise ValueError('AF09 unselected child tool: '+path)
        launch.verify_inputs({path:selected[path]})
    if generated:launch.verify_inputs(generated)


def verify_boundary(retained,generated,record,label):
    """Full hashes at consumer boundaries; no mtime/size cache or source thaw."""
    row=dict(label=label,status='checking',retained_files=len(retained),generated_files=len(generated),
        retained_map_sha256=hashlib.sha256(json.dumps(retained,sort_keys=True).encode()).hexdigest(),
        generated_map_sha256=hashlib.sha256(json.dumps(generated,sort_keys=True).encode()).hexdigest())
    record.setdefault('input_boundaries',[]).append(row)
    try:
        launch.verify_inputs(retained)
        if generated:launch.verify_inputs(generated)
    except BaseException as error:
        row.update(status='failed',error=type(error).__name__+': '+str(error));raise
    row['status']='pass'


def controller_bytes(selected):
    path=Path(selected['path'])
    if (not 0<selected['bytes']<=4096 or path.stat().st_size!=selected['bytes']
            or digest(path)!=selected['sha256'] or digest(CONTROLLER)!=selected['source_sha256']):
        raise ValueError('AF09 shared controller artifact/source changed')
    return path.read_bytes()


def build_controller(stage,command,tools):
    """Fail fast once, before expensive SPA reconstruction; reuse exact bytes."""
    stage.mkdir()
    command([tools['rustfmt']['path'],'--edition=2024','--check',CONTROLLER],stage/'controller-format.log')
    command([tools['clippy-driver']['path'],'--edition=2024','--target=x86_64-unknown-none',
        '--emit=obj','-Dwarnings','-Dunsafe_op_in_unsafe_fn',CONTROLLER,'-o',stage/'controller.o'],stage/'controller-clippy.log')
    raw=stage/'supervisor.raw'
    command([tools['rustc']['path'],'--edition=2024','--target=x86_64-unknown-none','-Dwarnings',
        '-C','linker='+tools['lld']['path'],'-C','opt-level=2','-C','panic=abort','-C','relocation-model=static',
        '-C','link-arg=-Tuser/protection/linker.ld','-C','link-arg=--oformat=binary',CONTROLLER,'-o',raw],stage/'controller.log')
    selected=dict(path=str(raw),sha256=digest(raw),bytes=raw.stat().st_size,source_sha256=digest(CONTROLLER))
    controller_bytes(selected)
    return selected


def build_reader(stage,command,tools,record,retained,generated,recovered,controller):
    stage.mkdir()
    base=stage/'base';work=stage/'compose';work.mkdir();delivery=stage/'delivery';delivery.mkdir()
    def backend(backend,diagnostic,copied=None):
        launch.bind_runtime(backend,stage,retained,generated,artifact_root=diagnostic,copied=copied)
    label='recovery' if recovered else 'pristine'
    verify_boundary(retained,generated,record,'before-'+label+'-base')
    prepared=launch.prepare_base(base,command,tools,recovered=True,on_backend=backend)
    verify_boundary(retained,generated,record,'after-'+label+'-base')
    verify_boundary(retained,generated,record,'before-'+label+'-reader-composition')
    selected=home_reader.compose(base,prepared,work,delivery,command,tools,record,recovered)
    verify_boundary(retained,generated,record,'after-'+label+'-reader-composition')
    generated[selected['elf']]=selected['elf_sha256']
    engine=Path(selected['elf']).read_bytes();raw_controller=controller_bytes(controller)
    (stage/'native-c.bin').write_bytes(struct.pack('<8sII',b'AENBD002',len(engine),len(raw_controller))+bytes([91])*32+engine+raw_controller)
    generated[str(stage/'native-c.bin')]=digest(stage/'native-c.bin')
    verify_boundary(retained,generated,record,'before-'+label+'-kernel-envelope')
    command([tools['zig']['path'],'build','-p',stage,'--cache-dir',stage/'zig-cache','--global-cache-dir',ROOT/'.zig-cache/global',
        '-Dsmp=false','-Dnative-c-image='+str(stage/'native-c.bin'),*['-D'+flag+'=true' for flag in READER_FLAGS]],stage/'kernel.log')
    shutil.copyfile(stage/'bin/aether',stage/'kernel.elf')
    verify_boundary(retained,generated,record,'after-'+label+'-kernel-envelope')
    found=re.fullmatch(r'ELF structural pages=(\d+) segments=\d+ entry=[0-9a-f]+',selected['structural_loader'])
    if found is None:raise ValueError('AF09 reader actual loader geometry missing')
    return dict(selected,engine_pages=int(found[1]),controller_bytes=controller['bytes'],controller_sha256=controller['sha256'],
        controller_source_sha256=digest(CONTROLLER),original_controller_sha256=ORIGINAL_CONTROLLER_SHA256,
        flags=list(READER_FLAGS),read_grant_only=True,kernel_tick_limit=3000)


def tool_environment(work,tools,record,command):
    """Reuse the frozen guarded-input recipe and its Rust-only private LLVM."""
    def query(label,args):return command(args,Path(work)/(label+'.log'))
    routing=inputs.kernel_environment(work,tools,record,query)
    return Path(routing['rust_wrapper']['path']).parent,routing


def command_accepted(code,text,process,rejection=None):
    if (process.get('complete') is not True or process.get('cleanup')!='complete'
            or process.get('exit')!=code):
        return False
    if rejection is None:return code==0
    return isinstance(rejection,str) and rejection in launch.LINK_DENIALS and code==1 and rejection in text


def child_environment(proc,work,tools,args,routing=None):
    env=proc.clean_env(work)
    if routing is not None:
        inputs.verify_kernel_environment(routing)
        env.update(routing['environment'])
    if args[0] in [tools[name]['path'] for name in ('rustc','clippy-driver','rustfmt')]:
        linker=explicit_linker(args)
        bundled=tools.get('rust-lld',{}).get('path')
        if linker is not None and linker not in (tools['lld']['path'],bundled):
            raise ValueError('AF09 unselected explicit Rust linker')
        if linker==tools['lld']['path']:return env
        env['DYLD_LIBRARY_PATH']=str(Path(tools['rustc']['path']).parent.parent/'lib')
    return env


def prepare(directory,seal):
    """Prepare only; keep three pending ISOs/exact kernel ELFs and frozen receipt."""
    deadline=time.monotonic()+1800
    directory=Path(directory).absolute()
    selected=input_record(directory,seal,deadline=deadline)
    tools=selected['tools']
    if digest(ROOT/'user/storage/session/readback.rs')!=ORIGINAL_CONTROLLER_SHA256:
        raise ValueError('AF09 original readback controller drift')
    from deps import verify,DEPS,LOCK
    verify()
    frozen=dict(selected['inputs'])
    boot_manifest=inputs.read_json(ROOT/'.deps/manifest.json')
    frozen[str(ROOT/'.deps/manifest.json')]=digest(ROOT/'.deps/manifest.json')
    for name,expected in boot_manifest['files'].items():
        path=DEPS/name
        if Path(name).is_absolute() or '..' in Path(name).parts or digest(path)!=expected:
            raise ValueError('AF09 pinned boot input drift')
        frozen[str(path)]=expected
    for path in (ROOT/'LICENSE',*(p for p in (ROOT/'boot').rglob('*') if p.is_file())):
        frozen[str(path)]=digest(path)
    frozen.update({str(directory/'SHA256SUMS'):seal,str(directory/'inputs.json'):digest(directory/'inputs.json'),
        str(Path(__file__).resolve()):digest(__file__),str(CONTROLLER):digest(CONTROLLER),str(PROCESS):PROCESS_SHA256,
        str(ROOT/'sys-init/tests/home_owner_qualifier_tests.py'):digest(ROOT/'sys-init/tests/home_owner_qualifier_tests.py')})
    frozen.update({str(directory/name):row['sha256'] for name,row in selected['artifacts'].items()})
    for name,row in tools.items():frozen[row['path']]=row['sha256']
    for name in ('firmware/code.fd','firmware/vars.fd'):
        frozen[str(DEPS/name)]=digest(DEPS/name)
    from openzfs_namespace import FIXTURE,FIXTURE_SHA256,FIXTURE_IMAGE_SHA256,FIXTURE_BYTES
    if digest(FIXTURE)!=FIXTURE_SHA256:raise ValueError('AF09 exact original fixture source changed')
    frozen[str(FIXTURE)]=FIXTURE_SHA256
    launch.verify_inputs(frozen)
    proc=owned_process()
    output=Path(tempfile.mkdtemp(prefix=PREFIX,dir=ROOT/'zig-out'))
    receipt_path=reserve_evidence()
    receipt=dict(schema=SCHEMA,status='preparing',native_attempted=False,native_executed=False,output=str(output),
        input_directory=str(directory),input_seal=seal,profile=selected['profile'],bounds=selected['bounds'],
        admission=selected['admission'],measurement=selected['measurement'],rtc=RTC,script_hex=SCRIPT.hex(),
        prospective_sequence=['pristine','writer','recovery'],stop_on_first_failure=True,retry=False,
        no_guest_entrypoint=True,commands=[],inputs=frozen,generated_inputs={},tools=tools,
        input_verification='Full source hashes at start, consumer/role boundaries and publication; each child checks actual tool, explicit linker and live generated runtime inputs; all sources remain frozen',
        expected_media=dict(region_sha256=FIXTURE_IMAGE_SHA256,region_bytes=FIXTURE_BYTES,guard_bytes=4096,
            guard_value=165,full_media_bytes=FIXTURE_BYTES+8192,recovery='exact confirmed stopped-writer whole-media identity'),
        controller_derivation=dict(original=str(ROOT/'user/storage/session/readback.rs'),original_sha256=ORIGINAL_CONTROLLER_SHA256,
            selected=str(CONTROLLER),selected_sha256=digest(CONTROLLER)),
        limits=dict(child_seconds=180,total_seconds=1800,capture_bytes=65536,diagnostic_stream_bytes=DIAGNOSTIC_LIMIT,
            compiler_file_limit_bytes=16*1024*1024),
        scope='Offline prepared candidates/prospective oracles only; fresh disposition required before any guest')
    work=output/'work'
    generated={}
    tool_bin=None;tool_routing=None
    def command(argv,log,rejection=None):
        args=launch.command_arguments(argv,tools)
        verify_child(args,tools,generated)
        remaining=check_budget(deadline)
        env=child_environment(proc,work,tools,args,tool_routing)
        label='prepare-%04d'%len(receipt['commands'])
        expected_exit=1 if rejection is not None else 0
        try:
            child=proc.run(args,cwd=ROOT,env=env,work=work,label=label,timeout=min(180,remaining))
        except BaseException as error:
            path=work/(label+'.process.json')
            state=inputs.read_json(path) if path.is_file() else dict(failure='runner did not return')
            receipt['commands'].append(dict(process=state,expected_exit=expected_exit,expected_rejection=rejection,rejection_verified=False,error=type(error).__name__+': '+str(error)))
            if state.get('process_group') and state.get('cleanup')!='complete':
                receipt['process_cleanup_unresolved']=True
            raise
        if child.record.get('process_group') and child.record.get('cleanup')!='complete':
            receipt['process_cleanup_unresolved']=True
        text=(child.stdout+child.stderr).decode(errors='replace')
        row=dict(process=child.record,expected_exit=expected_exit,expected_rejection=rejection,rejection_verified=False,stdout_bytes=len(child.stdout),stderr_bytes=len(child.stderr),stdout_tail=child.stdout.decode(errors='replace')[-1200:],
            stderr_tail=child.stderr.decode(errors='replace')[-3000:])
        receipt['commands'].append(row)
        if len(child.stdout)>DIAGNOSTIC_LIMIT or len(child.stderr)>DIAGNOSTIC_LIMIT:
            row['diagnostic_overflow']=True
            raise RuntimeError('AF09 compiler diagnostic stream exceeds4MiB')
        path=Path(log)
        if not path.is_absolute():path=work/path
        if not path.resolve().is_relative_to(output):raise ValueError('AF09 command log outside owned output')
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
        row['log_sha256']=digest(path)
        verify_child(args,tools,generated)
        valid=command_accepted(child.returncode,text,child.record,rejection)
        row['rejection_verified']=rejection is not None and valid
        if not valid:
            raise RuntimeError('AF09 preparation command failed: '+str(path))
        return text
    try:
        work.mkdir()
        tool_bin,tool_routing=tool_environment(work,tools,receipt,command)
        receipt['named_build_tools']=tool_routing
        qemu=tools.get('qemu',{}).get('path') or shutil.which('qemu-system-x86_64')
        if not qemu:raise ValueError('AF09 prospective QEMU input unavailable')
        qemu=Path(qemu).resolve();frozen[str(qemu)]=digest(qemu)
        receipt['prospective_emulator']=dict(path=str(qemu),sha256=digest(qemu),expected_version=LOCK['qemu'],
            machine='pc-q35-11.1',accel='tcg',cpu='qemu64',smp=1,memory='256M',network=False,executed=False)
        verify_boundary(frozen,generated,receipt,'before-controller')
        controller=build_controller(work/'controller',command,tools)
        generated[controller['path']]=controller['sha256']
        receipt['shared_controller']=controller
        verify_boundary(frozen,generated,receipt,'after-controller')
        verify_boundary(frozen,generated,receipt,'before-writer-role')
        writer=output/'writer';writer.mkdir()
        shutil.copyfile(directory/'envelope.bin',writer/'envelope.bin')
        generated[str(writer/'envelope.bin')]=selected['artifacts']['envelope.bin']['sha256']
        if selected['kernel_build']['flags']!=list(WRITER_FLAGS):raise ValueError('AF09 exact writer kernel flags')
        command([tools['zig']['path'],'build','-p',writer,'--cache-dir',work/'zig-cache','--global-cache-dir',ROOT/'.zig-cache/global',
            '-Dsmp=false','-Dnative-c-image='+str(writer/'envelope.bin'),*['-D'+flag+'=true' for flag in WRITER_FLAGS]],writer/'kernel.log')
        shutil.copyfile(writer/'bin/aether',writer/'kernel.elf')
        verify_boundary(frozen,generated,receipt,'after-writer-role')
        receipt['readers']={}
        for role,recovered in (('pristine',False),('recovery',True)):
            stage=output/role
            verify_boundary(frozen,generated,receipt,'before-'+role+'-role')
            role_record={}
            receipt['readers'][role]=build_reader(stage,command,tools,role_record,frozen,generated,recovered,controller)
            receipt.setdefault('reader_composition_boundaries',{})[role]=role_record.get('input_boundaries',[])
            verify_boundary(frozen,generated,receipt,'after-'+role+'-role')
        verify_boundary(frozen,generated,receipt,'final-consumers')
        if input_record(directory,seal,deadline=deadline)!=selected:raise ValueError('AF09 guarded input changed during image preparation')
        receipt['generated_inputs']=dict(generated)
        receipt['artifacts']={role:{name:dict(bytes=(output/role/name).stat().st_size,sha256=digest(output/role/name))
            for name in ('aether.iso','kernel.elf')} for role in ('pristine','writer','recovery')}
        receipt['expected_reader_metadata']='Compare all32 opaque returned metadata SHA256 bytes for pristine and recovery; no prefix/changed-zstd oracle'
        check_budget(deadline)
        receipt.update(status='prepared',final_input_verification='pass')
    except BaseException as error:
        receipt.update(status='failed',error=type(error).__name__+': '+str(error));raise
    finally:
        removed=0
        if not receipt.get('process_cleanup_unresolved'):
            for path in output.iterdir():
                if path.is_dir():
                    for child in path.iterdir():
                        if receipt['status']=='prepared' and path.name in ('writer','pristine','recovery') and child.name in ('aether.iso','kernel.elf'):continue
                        if child.is_dir():removed+=sum(p.is_file() for p in child.rglob('*'));shutil.rmtree(child)
                        else:removed+=1;child.unlink()
                    if not any(path.iterdir()):path.rmdir()
                elif path.name!='results.json':removed+=1;path.unlink()
            receipt['cleanup']=dict(status='complete',removed_generated_files=removed,
                kept_pending_images=3 if receipt['status']=='prepared' else 0)
        else:
            receipt['cleanup']=dict(status='unresolved',owned_outputs_retained=True)
        data=json.dumps(receipt,indent=2)+'\n'
        expired=None
        if receipt['status']=='prepared':
            try:
                publication=dict(frozen)
                for role,artifacts in receipt['artifacts'].items():
                    publication.update({str(output/role/name):row['sha256'] for name,row in artifacts.items()})
                verify_boundary(publication,{},receipt,'publication')
                check_budget(deadline)
                data=json.dumps(receipt,indent=2)+'\n'
            except (ValueError,RuntimeError,OSError) as error:
                # Cleanup/serialization count toward the same total budget.
                # Never publish expired candidates as prepared or keep their
                # images as pending evidence after this rejecting boundary.
                expired=error
                receipt.update(status='failed',error=str(error))
                for role in ('pristine','writer','recovery'):
                    folder=output/role
                    for name in ('aether.iso','kernel.elf'):
                        path=folder/name
                        if path.is_file():
                            path.unlink();receipt['cleanup']['removed_generated_files']+=1
                    if folder.is_dir() and not any(folder.iterdir()):folder.rmdir()
                receipt['cleanup']['kept_pending_images']=0
                data=json.dumps(receipt,indent=2)+'\n'
        (output/'results.json').write_text(data);receipt_path.write_text(data)
        if expired is not None:raise expired
    return dict(status='prepared',native_executed=False,output=str(output),receipt=str(output/'results.json'),receipt_sha256=digest(output/'results.json'))


def main(argv=None):
    class Parser(argparse.ArgumentParser):
        def error(self,message):
            self.print_usage(sys.stderr);self.exit(64,'home-owner: '+ascii(message)[1:-1]+'\n')
    parser=Parser(description=__doc__,epilog='Offline preparation only. Keep the prepared receipt for review; no guest execution is available. Fix blocked inputs before a new preparation.')
    parser.add_argument('--version',action='version',version='aether-home-owner-qualification 1')
    parser.add_argument('--inputs',type=Path,required=True,help='sealed exact AF09 guarded input directory')
    parser.add_argument('--seal',required=True,help='SHA256 of the guarded SHA256SUMS file')
    parser.add_argument('--prepare',action='store_true',required=True,help='prepare pristine/writer/recovery images; execute no guest')
    args=parser.parse_args(argv)
    try:result=prepare(args.inputs,args.seal)
    except (ValueError,FileNotFoundError) as error:
        print('[BLOCKED] '+ascii(str(error))[1:-1],file=sys.stderr);return 2
    except (OSError,RuntimeError) as error:
        print('[ERROR] '+ascii(str(error))[1:-1],file=sys.stderr);return 1
    print(json.dumps(result));return 0


if __name__=='__main__':raise SystemExit(main())
