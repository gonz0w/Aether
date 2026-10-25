#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Prepare or qualify the private filesystem/SESSION composition; no retries."""
import argparse
from contextlib import redirect_stdout
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import tempfile

from deps import ROOT, DEPS
from fs_launch_intake import intake
from native_smoke import NativeStopError, run
from openzfs_namespace import native_media_snapshot, prepare_native_fixture, written_native_media_snapshot
import service_runtime_smoke as runtime

PREFIX = 'thread-suite-service-runtime-zpl-pair-fs-session-'
ENGINE = ROOT/'.deps/fs-launch-2026-10-20-v4'
FLAGS = '''native-memory native-memory-large native-image-large native-backing
native-service-memory native-threads native-thread-pair native-thread-reuse
native-thread-origin native-service-workers native-clock native-entropy native-rtc
native-service-block native-service-cleanup-trace native-service-channel
native-service-channel-wait native-service-activation native-service-zpl-budget
native-process-freeze native-process-copy native-process-exec native-signal-actions
native-signal-public native-copy-signals native-runner-local native-parent-identity
native-pipeline-capacity native-session-lifecycle native-fs-session'''.split()
CFG = ('namespace_wait','fs_mixed','fs_bulk','fs_runtime','fs_activation','fs_names','fs_directories')


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def machine_witness(text):
    """Bounded normalized record selection, not raw UART or a passing oracle."""
    markers = ('AETHER M1: entered x86_64 kernel', 'AETHER M1 PASS',
               'AETHER NATIVE BLOCK PASS')
    selected = []
    digest = hashlib.sha256()
    total = retained_bytes = 0
    complete = True
    for line in text.splitlines():
        if not (line.startswith(('NATIVE ', 'AETHER PANIC:')) or line in markers):
            continue
        chunk = (line+'\n').encode('utf-8')
        digest.update(chunk)
        total += 1
        if complete and retained_bytes+len(chunk) <= 65536:
            selected.append(line)
            retained_bytes += len(chunk)
        else:
            complete = False
    return dict(format='aether-native-machine-selection-v1', lines=selected,
                selection_complete=complete, total_lines=total,
                retained_utf8_bytes=retained_bytes, ceiling_utf8_bytes=65536,
                full_selection_sha256=digest.hexdigest(),
                scope='Normalized selected records only; not raw UART, full kernel span or qualification')


def adapt_clients(output, metadata_service=False):
    """Owned controller-only adaptations. Old source/sealed objects stay exact."""
    parent=ROOT/'user/storage/service-runtime'
    original=(parent/'fs-service-client.rs').read_text()
    selected=original.replace('0xd001','0xd002')
    anchor='check(call(0x20008, factory, 1, self.request, self.reply).0 == -12);'
    if selected.count(anchor)!=1:
        raise ValueError('combined admission controller context changed')
    selected=selected.replace(anchor,anchor.replace('-12','-13'))
    def absolute(match):
        return '#[path = '+json.dumps(str((parent/match[1]).resolve()))+']'
    selected=re.sub(r'#\[path = "([^"]+)"\]',absolute,selected)
    directory=(parent/'fs-directories-client.rs').read_text()
    if metadata_service:
        from openzfs_fs_metadata_service import client
        directory=client(directory)
    anchor='                check(token == '+('9' if metadata_service else '8')+' && txg > 790);'
    if directory.count(anchor)!=1:
        raise ValueError('combined transaction witness context changed')
    directory=directory.replace(anchor,anchor+'\n                super::super::witness(txg);')
    (output/'directories.rs').write_text(directory)
    selected=selected.replace(str(parent/'fs-directories-client.rs'),str(output/'directories.rs'))
    (output/'service-client.rs').write_text(selected)
    owner=(ROOT/'user/storage/session/owner.rs').read_text()
    owner=owner.replace('"../service-runtime/fs-activation-client.rs"',json.dumps(str(parent/'fs-activation-client.rs')))
    owner=owner.replace('"wide.rs"',json.dumps(str(ROOT/'user/storage/session/wide.rs')))
    if metadata_service:owner=owner.replace('Exact AF06 nine-mutation/96-request','Exact AF07 nine-mutation/96-request')
    (output/'owner.rs').write_text(owner)


# Fixed one-record-per-event dictionary; no event is generated or aggregated.
_WAIT_ENCODE = {f'NATIVE STORAGE WAIT slot={slot} generation={generation} phase={phase} status=0':
                f'NATIVE SW {slot}{letter}'
                for slot,generation in ((0,1),(6,0)) for phase,letter in (('park','P'),('wake','W'))}
_WAIT_DECODE = {value:key for key,value in _WAIT_ENCODE.items()}
_WAIT_ESCAPE = 'NATIVE RAW '


def metadata_oracle_witness(text):
    """Losslessly shorten four exact waits within the same64KiB UTF8 ceiling."""
    source=machine_witness(text)
    timer=re.compile(r'NATIVE CLOCK park task=\d+ start=\d+ deadline=\d+|NATIVE CLOCK timeout task=\d+ now=\d+ elapsed=\d+')
    kept=[];encoded=[];omitted=hashlib.sha256();count=0
    for line in text.splitlines():
        if timer.fullmatch(line):omitted.update((line+'\n').encode());count+=1;continue
        kept.append(line)
        if line in _WAIT_ENCODE:encoded.append(_WAIT_ENCODE[line])
        elif line in _WAIT_DECODE or line.startswith(_WAIT_ESCAPE):encoded.append(_WAIT_ESCAPE+line)
        else:encoded.append(line)
    decoded=machine_witness('\n'.join(kept))
    result=machine_witness('\n'.join(encoded))
    result.update(format='aether-af07-session-oracle-v2',source_selection=dict(total_lines=source['total_lines'],sha256=source['full_selection_sha256']),
                  decoded_selection=dict(total_lines=decoded['total_lines'],sha256=decoded['full_selection_sha256']),
                  omitted_clock_events=dict(lines=count,sha256=omitted.hexdigest()),
                  scope='Lossless four-record primary-wait dictionary within64KiB UTF8; exact clock events summarized, not raw UART/schedule replay')
    return result


def metadata_oracle_text(witness):
    """Reconstruct exact selected records; malformed/incomplete evidence rejects."""
    if (type(witness) is not dict or witness.get('format')!='aether-af07-session-oracle-v2' or witness.get('selection_complete') is not True
            or witness.get('ceiling_utf8_bytes')!=65536 or type(witness.get('decoded_selection')) is not dict
            or type(witness.get('source_selection')) is not dict or type(witness.get('omitted_clock_events')) is not dict
            or not isinstance(witness.get('lines'),list)):
        raise ValueError('AF07 SESSION incomplete/unsupported oracle')
    if (type(witness['omitted_clock_events'].get('lines')) is not int or witness['omitted_clock_events']['lines']<0
            or type(witness.get('total_lines')) is not int
            or type(witness['source_selection'].get('total_lines')) is not int
            or witness['source_selection']['total_lines']!=witness.get('total_lines',-1)+witness['omitted_clock_events']['lines']
            or any(not isinstance(value,str) or not re.fullmatch(r'[0-9a-f]{64}',value) for value in
                   (witness['source_selection'].get('sha256'),witness['omitted_clock_events'].get('sha256')))):
        raise ValueError('AF07 SESSION source/clock count/hash')
    lines=witness['lines']
    if len(lines)>65536 or any(type(line) is not str or '\n' in line or '\r' in line for line in lines):
        raise ValueError('AF07 SESSION oracle record shape')
    if sum(len(line.encode())+1 for line in lines)>65536:
        raise ValueError('AF07 SESSION encoded oracle count/hash/bound')
    raw=''.join(line+'\n' for line in lines)
    if (machine_witness(raw)['lines']!=lines
            or len(raw.encode())!=witness.get('retained_utf8_bytes') or len(lines)!=witness.get('total_lines')
            or hashlib.sha256(raw.encode()).hexdigest()!=witness.get('full_selection_sha256')):
        raise ValueError('AF07 SESSION encoded oracle count/hash/bound')
    restored=''.join((line[len(_WAIT_ESCAPE):] if line.startswith(_WAIT_ESCAPE) else _WAIT_DECODE.get(line,line))+'\n' for line in lines)
    selected=machine_witness(restored)
    if (len(restored.encode())>5*65536 or selected['total_lines']!=len(lines)
            or selected['total_lines']!=witness.get('decoded_selection',{}).get('total_lines')
            or selected['full_selection_sha256']!=witness.get('decoded_selection',{}).get('sha256')):
        raise ValueError('AF07 SESSION decoded oracle count/hash/bound')
    return restored


def writer_trace(text, controller_16k=False):
    """This writer has two admitted roles, not the old three engine generations."""
    if (text.count('AETHER NATIVE BLOCK PASS\n')!=1 or
            any(s in text for s in ('PANIC','NATIVE fault ','NATIVE supervisor result='))):
        raise ValueError('combined writer completion/fault')
    terminal=re.findall(r'^NATIVE terminal .*$',text,re.M)
    if terminal!=['NATIVE terminal slot=1 generation=1 kind=1 detail=0',
                  'NATIVE terminal slot=0 generation=1 kind=1 detail=0']:
        raise ValueError('combined process/engine terminal identities')
    cleanup=[line for line in text.splitlines() if line.startswith('NATIVE CLEANUP ')]
    expected=[]
    for slot,pages,prior in ((1,128,0),(0,8192,1)):
        expected += [f'NATIVE CLEANUP v=1 slot={slot} generation=1 phase={phase} selected={slot if phase==1 else 6} pages={pages} reclaimed={prior+(phase==7)}' for phase in range(1,8)]
    if cleanup!=expected:
        raise ValueError('combined per-role stop/reclaim/zero boundaries')
    halt=re.findall(r'^NATIVE init halted ticks=(\d+) idle=(\d+) reclaimed=(\d+)$',text,re.M)
    if len(halt)!=1 or not 0<int(halt[0][0])<=6000 or int(halt[0][2])!=2:
        raise ValueError('combined quiescent halt or tick budget')
    values=[];engine_rows=[]
    for line in text.splitlines():
        if not line.startswith('NATIVE observation '):
            continue
        m=re.fullmatch(r'NATIVE observation slot=(\d+) generation=(\d+) offset=(\d+) byte=(\d+)',line)
        if m is None:
            raise ValueError('combined observation syntax')
        slot,generation,offset,value=map(int,m.groups())
        target=values if (slot,generation)==(6,0) else engine_rows if (slot,generation)==(0,1) else None
        if target is None or offset!=8*len(target) or len(target)>=32 or not 0<=value<=255:
            raise ValueError('combined observation identity/offset/bound')
        target.append(value)
    base = 8 if controller_16k else 0
    if controller_16k:
        if len(values)!=13 or values[0]!=ord('W'):
            raise ValueError('four-page controller mapping witness')
        values=values[1:]
    if len(values)!=12 or bytes(values[:3])!=b'RPT' or values[-1]!=ord('C'):
        raise ValueError('combined ready/exec/transaction/cleanup transcript')
    memory=re.findall(r'^NATIVE MEMORY admitted slot=(\d+) generation=(\d+) used=(\d+) remaining=(\d+)$',text,re.M)
    if len(memory)!=3:
        raise ValueError('combined actual loader admission count')
    for row,slot,pages in zip(memory,(0,1,1),(8192,128,128),strict=True):
        observed,generation,used,remaining=map(int,row)
        if (observed,generation)!=(slot,1) or used<17 or used+remaining!=pages:
            raise ValueError('combined actual loader role quota')
    ordered=[
        'NATIVE MEMORY admitted slot=0 ',
        f'NATIVE observation slot=6 generation=0 offset={base} byte=82\n',
        'NATIVE MEMORY admitted slot=1 ',
        'NATIVE terminal slot=1 generation=1 kind=1 detail=0\n',
        'NATIVE CLEANUP v=1 slot=1 generation=1 phase=7 ',
        f'NATIVE observation slot=6 generation=0 offset={base+8} byte=80\n',
        f'NATIVE observation slot=6 generation=0 offset={base+80} ',
        'NATIVE terminal slot=0 generation=1 kind=1 detail=0\n',
        'NATIVE CLEANUP v=1 slot=0 generation=1 phase=7 ',
        f'NATIVE observation slot=6 generation=0 offset={base+88} byte=67\n',
        'NATIVE init halted ', 'AETHER NATIVE BLOCK PASS\n']
    positions=[text.index(anchor) for anchor in ordered]
    if positions!=sorted(positions):
        raise ValueError('combined ready/process/write/terminal/reclaim/halt ordering')
    target=int.from_bytes(bytes(values[3:11]),'little')
    if not 790<target<=0xffffffffffffffff:
        raise ValueError('combined transaction target')
    pending=set();counts={'park':0,'wake':0};owners=set()
    for line in text.splitlines():
        if not line.startswith('NATIVE STORAGE WAIT '):
            continue
        m=re.fullmatch(r'NATIVE STORAGE WAIT slot=(\d+) generation=(\d+) phase=(park|wake) status=(-?\d+)',line)
        if m is None:
            raise ValueError('combined wait syntax')
        slot,generation,phase,status=m.groups();key=int(slot),int(generation)
        if key not in ((0,1),(6,0)) or int(status)!=0:
            raise ValueError('combined primary wait identity/status')
        if phase=='park':
            if key in pending: raise ValueError('combined duplicate wait')
            pending.add(key);owners.add(key[0])
        else:
            if key not in pending: raise ValueError('combined foreign wake')
            pending.remove(key)
        counts[phase]+=1
    if pending or owners!={0,6} or counts['park']!=counts['wake']:
        raise ValueError('combined incomplete primary waits')
    return dict(profile='AENFS003/owner29/engine26' if controller_16k else 'AENFS002/owner28/engine26', admitted_instances=2,
                reclaimed=2, final_live_workers=0, cleanup_trace_version=1,
                cleanup_boundaries_per_instance=7, assigned_target_txg=target,
                engine_terminal_zero=True, process_exec_wait=True,
                full_service_transcript=True, primary_channel_waits=counts['park'],
                primary_channel_wakes=counts['wake'], engine_observation_bytes=engine_rows,
                shutdown_basis='exact sealed executable exit0 requires all8191 phases and clean service; not a new provider phase trace')


def check_writer(writer):
    required={'status':'pass',
              'admitted_instances':2,'reclaimed':2,'final_live_workers':0,
              'cleanup_trace_version':1,'cleanup_boundaries_per_instance':7}
    target=writer.get('assigned_target_txg')
    if (writer.get('profile') not in ('AENFS002/owner28/engine26','AENFS003/owner29/engine26') or
            any(writer.get(k)!=v for k,v in required.items()) or
            any(writer.get(k) is not True for k in ('vm_run_returned','engine_terminal_zero','process_exec_wait','full_service_transcript')) or
            type(target) is not int or not 790<target<=0xffffffffffffffff or
            re.fullmatch('[0-9a-f]{64}',writer.get('disk_sha256','')) is None):
        raise ValueError('combined recovery requires a qualified clean stopped writer')


def recovery_media(writer,disk):
    check_writer(writer)
    return written_native_media_snapshot(disk,writer['disk_sha256'])


def qualify_pair(writer,reader):
    check_writer(writer)
    if (reader.get('status')!='pass' or reader.get('vm_run_returned') is not True or
            reader.get('reclaimed')!=3 or reader.get('generations')!=3 or
            reader.get('final_live_workers')!=0 or reader.get('cleanup_trace_version')!=1 or
            reader.get('cleanup_boundaries_per_generation')!=7 or reader.get('readonly_pool_retired') is not True or
            reader.get('namespace_bytes_verified')!=780248 or
            type(reader.get('recovered_pool_txg')) is not int or
            not writer['assigned_target_txg']<=reader['recovered_pool_txg']<=0xffffffffffffffff or
            reader.get('disk_sha256')!=writer.get('disk_sha256')):
        raise ValueError('combined independent recovery/data/media/cleanup mismatch')
    return dict(fresh_vm_readback_qualified=True, reader_media_unchanged=True,
                assigned_target_txg=writer['assigned_target_txg'],recovered_pool_txg=reader['recovered_pool_txg'])


def campaign(execute=False, controller_16k=False, sys_init=False, sys_init_checks=False, metadata_candidate=None, metadata_sys_init_checks=False):
    engine_directory=ENGINE
    if metadata_sys_init_checks and (metadata_candidate is None or controller_16k or sys_init or sys_init_checks):
        raise ValueError('AF07 sys-init requires only the separate selector and explicit candidate/seal')
    if metadata_candidate is not None:
        if (type(metadata_candidate) is not tuple or len(metadata_candidate)!=2
                or controller_16k or sys_init or sys_init_checks
                or not isinstance(metadata_candidate[1],str) or not re.fullmatch(r'[0-9a-f]{64}',metadata_candidate[1])):
            raise ValueError('AF07 requires a fixed8KiB conformance profile and explicit candidate/seal')
        import fs_metadata_launch
        engine_directory=Path(metadata_candidate[0]).absolute()
        if engine_directory.parent!=ROOT/'.deps' or not engine_directory.name.startswith('fs-launch-af07-'):
            raise ValueError('AF07 requires a scoped .deps/fs-launch-af07-* candidate')
    if metadata_sys_init_checks:
        sys_init_checks = True
    def consumer_intake():
        if metadata_sys_init_checks:
            from fs_init_af07 import intake as af07_intake
            return af07_intake(engine_directory, metadata_candidate[1])
        from fs_init_consumer import intake as old_consumer_intake
        return old_consumer_intake()
    def selected_intake():
        return fs_metadata_launch.intake(engine_directory,metadata_candidate[1]) if metadata_candidate is not None else intake(engine_directory)
    if sys_init_checks:
        sys_init = True
    if sys_init:
        controller_16k = True
    output=Path(tempfile.mkdtemp(prefix=PREFIX,dir=ROOT/'zig-out'))
    record=dict(schema='aether-fs-session-v1',status='preparing',native_attempted=False,
                executed=execute,controller_16k=controller_16k,sys_init=sys_init,sys_init_checks=sys_init_checks,metadata_sys_init_checks=metadata_sys_init_checks,commands=[],cases=[],inputs={},builds={},
                scope='Two-role native composition only; no sys-init/Zsh/ISO acceptance')
    if metadata_candidate is not None:
        record.update(metadata_protocol='AFSRPC07',metadata_engine=str(engine_directory),metadata_seal=metadata_candidate[1],
                      scope='Separate AF07 operational owner/SESSION witness only; not sys-init or R1 acceptance')
    stopped=True
    def save(): (output/'results.json').write_text(json.dumps(record,indent=2)+'\n')
    def command(args,name,rejection=None):
        args=list(map(str,args));log=name if isinstance(name,Path) else output/(name+'.log')
        if not log.is_relative_to(output) or log.resolve()!=log:
            raise ValueError('combined command log must be owned')
        log.parent.mkdir(parents=True,exist_ok=True)
        with log.open('wb') as stream:
            r=subprocess.run(args,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,timeout=240)
        row={'argv':args,'exit_code':r.returncode,'log_sha256':sha(log)}
        if rejection: row['expected_rejection']=rejection
        record['commands'].append(row);save()
        failed = (r.returncode == 0 or rejection not in log.read_text(errors='replace')) if rejection else r.returncode != 0
        if failed:
            row['failure_tail']=log.read_text(errors='replace')[-6000:];save()
            raise RuntimeError('combined build/check failed: '+str(name))
        return log.read_text()
    def freeze():
        selected_intake()
        if sys_init:
            if consumer_intake() != record['sys_init_delivery']:
                raise ValueError('sys-init consumer delivery drift')
        current=ROOT/'.deps/native-current'
        if sha(current/'current-inputs.json')!=record['current_dependency']['manifest_sha256']:
            raise ValueError('combined current dependency manifest drift')
        manifest=json.loads((current/'current-inputs.json').read_text())
        if any(sha(current/name)!=digest for name,digest in manifest['files'].items()):
            raise ValueError('combined current dependency bytes drift')
        for path,digest in record['inputs'].items():
            if sha(path)!=digest: raise ValueError('combined frozen input drift: '+path)
        for role,artifacts in record['artifacts'].items():
            for name,digest in artifacts.items():
                if sha(output/role/name)!=digest: raise ValueError('combined artifact drift: '+role+'/'+name)
    print('[RUNNING] Filesystem/SESSION preparation: '+str(output),file=sys.stderr,flush=True)
    try:
        record['engine_intake']=selected_intake()
        if sys_init:
            record['sys_init_delivery']=consumer_intake()
            record['scope']='Actual sys-init read-only activation only; post-activation full file readback/failure matrix and Zsh/ISO remain open'
            if sys_init_checks:
                record['scope']='Actual sys-init activation plus independent original-file readback and fixed hostile-peer controls; not a shell/ISO or general failure recovery'
            if metadata_sys_init_checks:
                record['scope']='Separate exact AF07 sys-init activation/readback/five failed peers; not a shell/ISO or general failure recovery'
        current=ROOT/'.deps/native-current'
        manifest=json.loads((current/'current-inputs.json').read_text())
        if any(sha(current/name)!=digest for name,digest in manifest['files'].items()):
            raise ValueError('combined current dependency bytes drift')
        record['current_dependency']={'manifest_sha256':sha(current/'current-inputs.json'),
                                      'members':len(manifest['files'])}
        initial = [ROOT/'build.zig', *[p for d in ('kernel','user','scripts')
                   for p in (ROOT/d).rglob('*') if p.is_file()
                   and '__pycache__' not in p.parts and p.name!='.DS_Store']]
        initial += [p for p in (ROOT/'.deps/native-current/sdk/stage').rglob('*') if p.is_file()]
        initial += [Path(shutil.which(name)).resolve() for name in ('zig','qemu-system-x86_64','xorriso')]
        initial_inputs = {str(p):sha(p) for p in initial}
        writer=output/'writer';writer.mkdir()
        if not sys_init: adapt_clients(writer,metadata_service=metadata_candidate is not None)
        sdk=ROOT/'.deps/native-current/sdk';tools=json.loads((sdk/'tools.lock.json').read_text())['tools']
        for name in ('clang','lld','nm'):
            if sha(Path(tools[name]['path']).resolve())!=tools[name]['sha256']:
                raise ValueError('combined tool identity: '+name)
        if sha(sdk/'stage/usr/lib/libc.a')!=json.loads((sdk/'evidence.json').read_text())['libc_archive_sha256']:
            raise ValueError('combined libc identity')
        record['tools']=tools
        cc=[tools['clang']['path'],'--no-default-config','--target=x86_64-linux-musl','--sysroot='+str(sdk/'empty-root')]
        flags=['-std=c11','-D_GNU_SOURCE','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-fstack-protector-strong','-nostdinc','-isystem',str(sdk/'stage/usr/include')]
        command(cc+flags+['-c','user/native-memory/adapter.c','-o',writer/'adapter.o'],'adapter')
        lib=sdk/'stage/usr/lib'
        for name,extra in (('process',[]),('replacement',['-DREPLACEMENT'])):
            command(cc+flags+extra+['-c','user/storage/session/process.c','-o',writer/(name+'.o')],name)
            command(cc+['-fuse-ld='+tools['lld']['path'],'-nostdlib','-static','-Wl,-z,noexecstack','-Wl,--no-undefined',lib/'crt1.o',lib/'crti.o',writer/(name+'.o'),writer/'adapter.o',lib/'libc.a',lib/'crtn.o','-o',writer/(name+'.elf')],name+'-link')
        linker = 'user/storage/session/init-linker.ld' if controller_16k else 'user/storage/service-runtime/activation-linker.ld'
        cfgs = (*CFG, 'fs_owner_16k') if controller_16k else CFG
        rust = ['rustc','+1.98.0','--edition=2024','--target=x86_64-unknown-none','-C','opt-level=z','-C','panic=abort','-C','relocation-model=static','-C','lto=fat','-C','codegen-units=1','-C','link-arg=-T'+linker,*[a for cfg in cfgs for a in ('--cfg',cfg)],writer/'owner.rs']
        if controller_16k or metadata_candidate is not None: rust += ['-C','jump-tables=no']
        if sys_init:
            delivery=record['sys_init_delivery']
            shutil.copyfile(delivery['raw'],writer/'owner.raw')
            shutil.copyfile(delivery['elf'],writer/'owner.elf')
            if sha(writer/'replacement.elf') != delivery['selected_program_sha256']:
                raise ValueError('sys-init selected program bytes changed')
        else:
            command(rust+['-C','link-arg=--oformat=binary','-o',writer/'owner.raw'],'owner')
        if controller_16k or metadata_candidate is not None:
            if not sys_init: command(rust+['-o',writer/'owner.elf'],'owner-elf')
            from fs_init_intake import intake as owner_intake
            record['owner_intake']=owner_intake(writer/'owner.elf',writer/'owner.raw',
                                               sha(writer/'owner.elf'),sha(writer/'owner.raw'))
            record['owner_stack']=dict(record['owner_intake']['stack'])
            record['owner_stack'].update(matched_elf_sha256=sha(writer/'owner.elf'),matched_raw_sha256=sha(writer/'owner.raw'))

        engine_bytes=(engine_directory/'filesystem.elf').read_bytes();a=(writer/'process.elf').read_bytes();b=(writer/'replacement.elf').read_bytes();owner=(writer/'owner.raw').read_bytes()
        if not (0<len(owner)<=16384 if sys_init else 12288<len(owner)<=16384 if controller_16k else 0<len(owner)<=8192): raise ValueError('combined controller bound')
        nested=struct.pack('<8sIIIIQ',b'AENMX009',len(a),len(b),len(b),len(owner),0)+b''.join(bytes([i+1])*16 for i in range(5))+a+b+b+owner
        payload=struct.pack('<8sII',b'AENFS003' if controller_16k else b'AENFS002',len(engine_bytes),len(nested))+bytes([91])*32+engine_bytes+nested
        (writer/'envelope.bin').write_bytes(payload)
        (writer/'admit.zig').write_text('const std=@import("std");const c=@import("composition");pub fn main()!void{const b=try c.parse(@embedFile("envelope.bin"));std.debug.print("COMBINED admitted engine={d} owner={d}\\n",.{b.engine.len,b.session.supervisor.len});}')
        if controller_16k:
            text=(writer/'admit.zig').read_text().replace('c.parse(@embedFile("envelope.bin"))','c.parseProfile(@embedFile("envelope.bin"),true)')
            (writer/'admit.zig').write_text(text)
        record['admission']=command(['zig','run','--cache-dir',ROOT/'.zig-cache','--global-cache-dir',ROOT/'.zig-cache/global','--dep','composition','-Mroot='+str(writer/'admit.zig'),'-Mcomposition='+str(ROOT/'kernel/native_fs_session.zig')],'admit').strip()
        command(['zig','build','-p',writer,'--cache-dir',ROOT/'.zig-cache','--global-cache-dir',ROOT/'.zig-cache/global','-Dsmp=false','-Dnative-c-image='+str(writer/'envelope.bin'),*['-D'+f+'=true' for f in (*FLAGS, *(['native-fs-session-init'] if controller_16k else []))]],'kernel')
        llvm=Path(tools['clang']['path']).parent
        record['kernel_layout']=command([llvm/'llvm-size',writer/'bin/aether'],'kernel-size').strip()
        record['kernel_metadata']=command([llvm/'llvm-nm','-S',writer/'bin/aether'],'kernel-symbols')
        record['kernel_metadata']='\n'.join(line for line in record['kernel_metadata'].splitlines() if re.search(r'\.(states|small_records|service_records|service_children|channels|engine_bytes|service_bytes)$',line))
        record['controller_bytes']=len(owner)
        for role in (('baseline',) if sys_init else ('baseline','reader')):
            with redirect_stdout(sys.stderr):
                runtime.suite(ROOT/'.deps/native-utc-v3/base',case='pool-import',fixed_reaper=True,engine_utc=True,utc_delivery=ROOT/'.deps/native-utc-v3',pool_create=True,pool_namespace=True,pool_diagnose='build',pool_zpl_recover=role=='reader',_zpl_stage=output/role,_zpl_recovery_diagnostic=role=='reader',_zpl_recovery_writer_60s=role=='reader',_zpl_fs_mixed=role=='reader',_zpl_fs_bulk=role=='reader',_zpl_fs_runtime=role=='reader',_zpl_fs_names=role=='reader',_zpl_fs_directories=role=='reader')
            record['builds'][role]=json.loads((output/(role+'-build.json')).read_text())
        fault_roles=()
        if sys_init_checks:
            from fs_init_checks import build_reader, FAILURES
            record['independent_reader']=build_reader(output/'reader',command,tools)
            fault_roles=tuple('failure-'+name for name in FAILURES)
            record['failed_peers']={}
            original=(writer/'envelope.bin').read_bytes()
            old_engine_size=struct.unpack_from('<I',original,8)[0]
            nested=original[48+old_engine_size:]
            for number,role in enumerate(fault_roles):
                stage=output/role;stage.mkdir()
                peer_source=ROOT/'user/storage/session/failed-peer.c'
                if metadata_sys_init_checks:
                    from fs_init_af07 import failed_peer_source
                    selected=stage/'failed-peer.c'
                    selected.write_text(failed_peer_source(peer_source.read_text()))
                    peer_source=selected
                command(cc+flags+['-DFAILURE='+str(number),'-c',peer_source,'-o',stage/'peer.o'],stage/'compile.log')
                command(cc+['-fuse-ld='+tools['lld']['path'],'-nostdlib','-static','-Wl,-z,noexecstack','-Wl,--no-undefined',lib/'crt1.o',lib/'crti.o',stage/'peer.o',writer/'adapter.o',lib/'libc.a',lib/'crtn.o','-o',stage/'engine.elf'],stage/'link.log')
                engine=(stage/'engine.elf').read_bytes()
                (stage/'envelope.bin').write_bytes(struct.pack('<8sII',b'AENFS003',len(engine),len(nested))+bytes([91])*32+engine+nested)
                shutil.copyfile(writer/'owner.raw',stage/'owner.raw')
                source=(writer/'admit.zig').read_text()
                (stage/'admit.zig').write_text(source)
                command(['zig','run','--cache-dir',ROOT/'.zig-cache','--global-cache-dir',ROOT/'.zig-cache/global','--dep','composition','-Mroot='+str(stage/'admit.zig'),'-Mcomposition='+str(ROOT/'kernel/native_fs_session.zig')],stage/'admit.log')
                command(['zig','build','-p',stage,'--cache-dir',ROOT/'.zig-cache','--global-cache-dir',ROOT/'.zig-cache/global','-Dsmp=false','-Dnative-c-image='+str(stage/'envelope.bin'),*['-D'+f+'=true' for f in (*FLAGS,'native-fs-session-init')]],stage/'kernel.log')
                phoff=struct.unpack_from('<Q',engine,32)[0]
                phsize,phnum=struct.unpack_from('<HH',engine,54)
                pages=16+sum((p[3]%4096+p[6]+4095)//4096 for p in (struct.unpack_from('<IIQQQQQQ',engine,phoff+i*phsize) for i in range(phnum)) if p[0]==1)
                record['failed_peers'][role]={'selection':FAILURES[number],'engine_pages':pages,'elf_sha256':sha(stage/'engine.elf'),'owner_sha256':sha(stage/'owner.raw')}
        paths=[ROOT/'build.zig',*[(ROOT/d)/p.relative_to(ROOT/d) for d in ('kernel','user','scripts') for p in (ROOT/d).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='.DS_Store']]
        paths += [p for p in (sdk/'stage').rglob('*') if p.is_file()]
        paths += [sdk/'tools.lock.json',sdk/'evidence.json',engine_directory/'SHA256SUMS',*DEPS.joinpath('firmware').glob('*.fd')]
        paths += [Path(v['path']) for v in tools.values()]
        for binary in ('zig','qemu-system-x86_64','xorriso'): paths.append(Path(shutil.which(binary)).resolve())
        sysroot=Path(subprocess.check_output(['rustc','+1.98.0','--print','sysroot'],text=True).strip())
        paths += [sysroot/'bin/rustc',*[p for p in (sysroot/'lib/rustlib/x86_64-unknown-none/lib').glob('*') if p.is_file()]]
        for build in record['builds'].values():
            report=build['report']
            paths += [ROOT/name for name in report['sources']]
            paths += [Path(v['path']) for v in report['tools'].values()]
            paths += [ROOT/'.deps/native-service-runtime-v3'/name for name in report['dependency_files']]
        record['inputs']={str(p):sha(p) for p in sorted(set(paths))}
        if sys_init: record['inputs'].update(record['sys_init_delivery']['inputs'])
        if any(record['inputs'].get(p)!=digest for p,digest in initial_inputs.items()):
            raise ValueError('combined consumed source changed during preparation')
        for build in record['builds'].values():
            for name,digest in build['report']['sources'].items():
                if record['inputs'].get(str(ROOT/name))!=digest:
                    raise ValueError('combined reader consumed source drift: '+name)
        roles=('baseline','writer','reader',*fault_roles) if sys_init_checks else ('baseline','writer') if sys_init else ('baseline','writer','reader')
        record['artifacts']={role:{name:sha(output/role/name) for name in (('aether.iso','envelope.bin','owner.raw','process.elf','replacement.elf',*(['owner.elf'] if controller_16k else [])) if role=='writer' else ('aether.iso','engine.elf','envelope.bin','owner.raw') if role in fault_roles else ('aether.iso','engine.elf'))} for role in roles}
        freeze();record['status']='prepared';save()
        if not execute: return output
        prepare_native_fixture(output);disk=output/'native-namespace.raw';pristine=native_media_snapshot(disk)
        for role in fault_roles: prepare_native_fixture(output/role)
        record['pristine_media']=pristine
        qualified_writer=None
        for role in roles:
            freeze()
            if role in fault_roles:
                from fs_init_checks import failure_trace
                fault_disk=output/role/'native-namespace.raw'
                before=native_media_snapshot(fault_disk)
                row=dict(role=role,status='running',watchdog_seconds=30,kernel_tick_limit=6000,start_utc=datetime.now(timezone.utc).isoformat())
                record['cases'].append(row);record['native_attempted']=True;save()
                run(output/role/'aether.iso',expected_panic=b'native supervisor terminated',marker=b'AETHER NATIVE BLOCK PASS',entropy=True,rtc_base='2026-10-06T12:34:00',block_disk=fault_disk,block_large=True,block_namespace=True,_pair_stop=True)
                row['vm_run_returned']=True
                row['qemu']=json.loads((output/role/'native-qemu-command.json').read_text())
                text=(output/role/'native-serial.log').read_text();row['serial_sha256']=sha(output/role/'native-serial.log')
                after=native_media_snapshot(fault_disk)
                row['namespace_media']=after
                row['disk_sha256']=after['sha256']
                if after!=before: raise ValueError('failed peer changed pristine media')
                peer=record['failed_peers'][role]
                if metadata_sys_init_checks:
                    witness=metadata_oracle_witness(text)
                    record.setdefault('serial',{})[role]=dict(sha256=row['serial_sha256'],tail=text[-6000:],machine_witness=witness)
                    metadata_oracle_text(witness)
                row.update(failure_trace(text,peer['selection'],peer['engine_pages']))
                row.update(status='pass',namespace_media=before,end_utc=datetime.now(timezone.utc).isoformat());save()
                continue
            if role!='reader':
                if native_media_snapshot(disk)!=pristine: raise ValueError('combined pristine admission drift')
            else:
                if sys_init_checks:
                    from fs_init_checks import recovery_media as consumer_media
                    consumer_media(qualified_writer,disk)
                else: recovery_media(qualified_writer,disk)
            row={'role':role,'status':'running','watchdog_seconds':60 if role=='writer' else 30,'kernel_tick_limit':6000 if role=='writer' else 3000,'start_utc':datetime.now(timezone.utc).isoformat()}
            record['cases'].append(row);record['native_attempted']=True;save()
            run(output/role/'aether.iso',marker=b'AETHER NATIVE BLOCK PASS',entropy=True,rtc_base='2026-10-06T12:34:00',block_disk=disk,block_large=True,block_namespace=True,_pair_stop=True,**({'_zpl_writer_60s':True} if role=='writer' else {('_fs_init_writer' if sys_init_checks else '_fs_session_writer'):qualified_writer} if role=='reader' else {}))
            row['vm_run_returned']=True
            row['qemu']=json.loads((output/role/'native-qemu-command.json').read_text())
            text=(output/role/'native-serial.log').read_text();row['serial_sha256']=sha(output/role/'native-serial.log')
            if metadata_candidate is not None:
                witness=metadata_oracle_witness(text)
                record.setdefault('serial',{})[role]=dict(sha256=row['serial_sha256'],tail=text[-6000:],machine_witness=witness)
                if not witness['selection_complete']:raise ValueError('AF07 SESSION oracle exceeds fixed64KiB ceiling')
                metadata_oracle_text(witness)
            if role=='writer':
                if sys_init:
                    if metadata_sys_init_checks:
                        from fs_init_af07 import trace as consumer_trace
                    else:
                        from fs_init_consumer import trace as consumer_trace
                    row.update(consumer_trace(text))
                else: row.update(writer_trace(text,controller_16k))
            else:
                row.update(runtime.check_engine_trace(text,'AETHER NATIVE BLOCK PASS'))
                row.update(runtime.check_pool_cleanup_trace(text))
                row.update(runtime.check_namespace_trace(text) if role=='baseline' or sys_init_checks else runtime.check_zpl_recovery_trace(text))
            if role=='writer' and sys_init:
                # Writable import/export may change pool metadata despite no
                # filesystem mutation request. Inspect full guarded bytes after
                # confirmed stop; do not invent a TXG or readback witness.
                from openzfs_namespace import _native_media_snapshot
                row['namespace_media']=_native_media_snapshot(disk)
                row['whole_media_unchanged']=row['namespace_media']['sha256']==pristine['sha256']
            else:
                row['namespace_media']=native_media_snapshot(disk) if role=='baseline' else written_native_media_snapshot(disk) if role=='writer' else consumer_media(qualified_writer,disk) if sys_init_checks else recovery_media(qualified_writer,disk)
            if role=='baseline' and row['namespace_media']!=pristine: raise ValueError('baseline changed media')
            row.update(status='pass',disk_sha256=row['namespace_media']['sha256'],end_utc=datetime.now(timezone.utc).isoformat());save()
            if role=='writer': qualified_writer=row
            elif role=='reader':
                if sys_init_checks:
                    record.update(after_activation_file_readback=True,readback_media_unchanged=True)
                else: record.update(qualify_pair(qualified_writer,row))
        freeze();record['status']='pass';return output
    except BaseException as error:
        stopped=not isinstance(error,NativeStopError)
        record.update(status='failed',error=str(error),vm_stop_confirmed=stopped,human_disposition_required=record['native_attempted'])
        if record['cases']: record['cases'][-1].update(status='failed',error=str(error))
        raise
    finally:
        for role in ('baseline','writer','reader',*locals().get('fault_roles',())):
            path=output/role/'native-serial.log'
            if path.is_file() and role not in record.get('serial',{}):
                text=path.read_text();record.setdefault('serial',{})[role]={'sha256':sha(path),'tail':text[-6000:],'machine_witness':machine_witness(text)}
                if metadata_candidate is not None:record['serial'][role]['machine_witness']=metadata_oracle_witness(text)
            if metadata_candidate is not None:
                row=next((c for c in record['cases'] if c['role']==role),None)
                qemu=output/role/'native-qemu-command.json'
                if row is not None and 'qemu' not in row and qemu.is_file():
                    try:row['qemu']=json.loads(qemu.read_text())
                    except (OSError,ValueError) as error:row['qemu_capture_error']=str(error)
            location=output/(role+'-build.json')
            if location.is_file():
                build=json.loads(location.read_text());root=Path(build['output'])
                record['builds'][role]={'status':build['report']['status'],'report_sha256':sha(location),'commands':len(build['report']['commands'])}
                if stopped:
                    if root.parent!=ROOT/'zig-out' or root.is_symlink() or root.resolve()!=root or not root.name.startswith('thread-suite-service-runtime-') or root.name.startswith('thread-suite-service-runtime-zpl-pair-'):
                        raise ValueError('combined refuses unowned reader build disposal')
                    shutil.rmtree(root)
                if stopped: location.unlink()
        if metadata_candidate is not None and stopped and (output/'native-namespace.raw').is_file():
            from openzfs_namespace import _native_media_snapshot
            try:record['stopped_media']=_native_media_snapshot(output/'native-namespace.raw')
            except (OSError,ValueError) as error:record['stopped_media']=dict(status='unavailable',error=str(error))
        save()
        if stopped:
            from evidence import compact_run
            compact_run(output,record)
            # The receipt already has command identities and short failure/serial
            # tails. Do not retain successful per-build logs or source bundles.
            for path in output.rglob('*'):
                if path.is_file() and path != output/'results.json': path.unlink()
            for path in sorted(output.rglob('*'),reverse=True):
                if path.is_dir(): path.rmdir()
            record['artifact_retention']['remaining']='single compact results.json'
            save()
        else: record['retained_unconfirmed_stop']=str(output);save()
        print('[PASS] Compact filesystem/SESSION receipt: '+str(output/'results.json') if record['status'] in ('pass','prepared') else '[FAIL] Filesystem/SESSION receipt: '+str(output/'results.json'),file=sys.stderr)


if __name__=='__main__':
    class Parser(argparse.ArgumentParser):
        def error(self,message):
            print('[FAIL] '+runtime.display(message),file=sys.stderr);raise SystemExit(64)
    parser=Parser(description=__doc__)
    parser.add_argument('--run',action='store_true',help='one fresh baseline/writer/recovery campaign within approved30/60/30s bounds')
    parser.add_argument('--version',action='version',version='aether-fs-session 1')
    selection=parser.add_mutually_exclusive_group()
    selection.add_argument('--controller-16k',action='store_true',help='explicit separate AENFS003/owner29 four-page conformance profile')
    selection.add_argument('--sys-init',action='store_true',help='exact ABI29 sys-init read-only activation; baseline/activation only, not recovery or shell qualification')
    selection.add_argument('--sys-init-checks',action='store_true',help='exact ABI29 activation, independent exported-file readback and five fixed failed-peer controls')
    selection.add_argument('--metadata-sys-init-checks',action='store_true',help='separate exact AF07 sys-init activation, independent original-file readback and five failed peers; requires metadata engine/seal, not a shell')
    parser.add_argument('--metadata-engine',type=Path,help='explicit separately sealed AF07 executable;8KiB conformance unless --metadata-sys-init-checks selects actual init')
    parser.add_argument('--metadata-seal',help='reviewed AF07 executable manifest SHA256; never updates default selection')
    args=parser.parse_args()
    if args.metadata_sys_init_checks and not args.metadata_engine:
        parser.error('AF07 sys-init requires explicit metadata engine and seal')
    if bool(args.metadata_engine)!=bool(args.metadata_seal) or (args.metadata_engine and (args.controller_16k or args.sys_init or args.sys_init_checks or not re.fullmatch(r'[0-9a-f]{64}',args.metadata_seal or ''))):
        parser.error('AF07 requires both candidate and seal, without16KiB/sys-init selectors')
    try:
        result=campaign(args.run,args.controller_16k,args.sys_init,args.sys_init_checks,
                        (args.metadata_engine,args.metadata_seal) if args.metadata_engine else None,args.metadata_sys_init_checks)
        print('[PASS] '+str(result/'results.json'))
    except (OSError,ValueError,RuntimeError,subprocess.SubprocessError) as error:
        print('[FAIL] '+runtime.display(error),file=sys.stderr);raise SystemExit(1)
