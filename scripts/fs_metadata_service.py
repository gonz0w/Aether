#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Prepare/qualify the separate fixed AF07 metadata service; never repin AF06."""
import argparse
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

from deps import ROOT, verify
from fs_init_checks import build_reader
from fs_launch_intake import intake as launch_intake
from fs_session import ENGINE, machine_witness
from native_smoke import NativeStopError, run
from openzfs_namespace import prepare_native_fixture, native_media_snapshot, written_native_media_snapshot
import openzfs_fs_metadata_service as af07
import service_runtime_smoke as runtime

FLAGS = '''native-memory native-memory-large native-image-large native-backing
native-service-memory native-threads native-thread-pair native-thread-reuse
native-thread-origin native-service-workers native-clock native-entropy native-rtc
native-service-block native-service-cleanup-trace'''.split()
CFG = ('namespace_wait','fs_mixed','fs_bulk','fs_runtime','fs_activation','fs_names','fs_directories')


def oracle_witness(text):
    """Keep bounded oracle rows; hash only exact repetitive event omissions.

    Live qualification always checks the unfiltered log. Unknown or error rows
    remain selected, and overflow must stop the campaign before the next guest.
    This is not a complete UART or scheduler/wait-history witness.
    """
    source = machine_witness(text)
    repetitive = re.compile(
        r'NATIVE STORAGE WAIT slot=\d+ generation=\d+ phase=(?:park|wake) status=0'
        r'|NATIVE CLOCK park task=\d+ start=\d+ deadline=\d+'
        r'|NATIVE CLOCK timeout task=\d+ now=\d+ elapsed=\d+'
    )
    kept = []
    omitted = hashlib.sha256()
    count = 0
    for line in text.splitlines():
        if repetitive.fullmatch(line):
            omitted.update((line+'\n').encode('utf-8'))
            count += 1
        else:
            kept.append(line)
    witness = machine_witness('\n'.join(kept))
    witness.update(format='aether-af07-oracle-selection-v1',
        scope='Bounded oracle rows; exact successful wait/timer events summarized, not full UART or scheduling history',
        source_selection=dict(total_lines=source['total_lines'],
            full_selection_sha256=source['full_selection_sha256']),
        omitted_events=dict(lines=count,sha256=omitted.hexdigest()))
    return witness


def require_oracle_witness(text):
    witness = oracle_witness(text)
    if not witness['selection_complete']:
        raise ValueError('AF07 oracle witness exceeds fixed64KiB ceiling')
    return witness


def image(stage, command, writer=False):
    engine=(stage/'engine.elf').read_bytes();owner=(stage/'supervisor.raw').read_bytes()
    if not 0<len(owner)<=(8192 if writer else 4096):
        raise ValueError('AF07 controller size bound')
    (stage/'native-c.bin').write_bytes(struct.pack('<8sII',b'AENBD004' if writer else b'AENBD002',
        len(engine),len(owner))+bytes([107])*32+engine+owner)
    flags=FLAGS+('native-service-channel native-service-channel-wait native-service-activation native-service-zpl-budget'.split() if writer else [])
    command(['zig','build','-p',stage,'--cache-dir',ROOT/'.zig-cache','--global-cache-dir',ROOT/'.zig-cache/global',
        '-Dsmp=false','-Dnative-c-image='+str(stage/'native-c.bin'),*['-D'+f+'=true' for f in flags]],stage/'kernel.log')
    return dict(controller_bytes=len(owner),engine_sha256=af07.digest(stage/'engine.elf'),
                controller_sha256=af07.digest(stage/'supervisor.raw'),flags=flags)


def rust(stage, source, command, writer=False, case='normal'):
    af07.validate_case(case)
    args=['rustc','+1.98.0','--edition=2024','--target=x86_64-unknown-none','-Dwarnings',
        '-Copt-level=z' if writer else '-Copt-level=2','-Cpanic=abort','-Crelocation-model=static',
        '-Clink-arg=-Tuser/storage/service-runtime/activation-linker.ld' if writer else '-Clink-arg=-Tuser/protection/linker.ld',
        '-Clink-arg=--oformat=binary']
    if writer:
        args+=['-Clto=fat','-Ccodegen-units=1']
        for cfg in CFG:args+=['--cfg',cfg]
        if case in ('lost-reply','partial-request'):
            args+=['--cfg','fs_lost_reply' if case=='lost-reply' else 'fs_partial_request']
        elif case in af07.METADATA_REPLIES:
            args+=['--cfg','fs_metadata_loss']
    command(args+[source,'-o',stage/'supervisor.raw'],stage/'controller.log')


def campaign(execute=False, diagnostic=False, failures=False):
    if failures is True:group='inherited'
    elif failures is False or failures is None:group=None
    elif type(failures) is str and failures in af07.FAILURE_GROUPS:group=failures
    else:raise ValueError('AF07 requires a fixed failure group')
    if group=='retirement' and not diagnostic:
        raise ValueError('AF07 retirement selection requires numbered diagnostics')
    failures=group is not None
    out=Path(tempfile.mkdtemp(prefix='thread-suite-service-runtime-zpl-pair-af07-',dir=ROOT/'zig-out'))
    record=dict(format='aether-af07-native-v1',status='preparing',output=str(out),
        start_utc=datetime.now(timezone.utc).isoformat(),commands=[],cases=[],artifacts={},
        native_attempted=False,limits=dict(mutations=9,requests=96,writer_seconds=60,writer_ticks=6000,
            reader_seconds=30,reader_ticks=3000,controller_bytes=8192,observer_bytes=8192,
            stack_bytes=4096,engine_pages=8192),
        scope='Separate normal AF07 source-bound metadata service/9 mutations/96 requests; no operational launch/sys-init/Zsh/ISO or general failure recovery acceptance')
    record['diagnostic']=diagnostic
    record['failure_paths']=failures
    record['failure_group']=group
    if group=='retirement':
        record['relocated_observations']=dict(S='before eviction wait',D='after eviction wait/before export',
            J='after export and namespace/order checks',F='after engine/provider/UTC finish',R='after runtime finish')
    profiles=af07.FAILURE_GROUPS[group] if failures else ('normal',)
    prepared=[]
    owned=[out]
    record['owned_output_roots']=[str(out)]
    baseline=None
    readers={}
    metadata_base=None
    if failures:
        record['profiles']={}
        record['scope']='Separate fixed AF07 '+group+' failure controls only; other groups and operational/R1 acceptance remain separate'
    stopped=True
    def artifact_key(path):
        return str(path) if failures else str(path.relative_to(out))
    def save(): (out/'results.json').write_text(json.dumps(record,indent=2)+'\n')
    def command(argv, log, rejection=None):
        args=list(map(str,argv))
        try:
            with Path(log).open('w') as stream:
                r=subprocess.run(args,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,timeout=180)
        except subprocess.TimeoutExpired:
            record['commands'].append(dict(argv=args,status='timeout',seconds=180,
                log_sha256=af07.digest(Path(log)),tail=Path(log).read_text(errors='replace')[-3000:]));save();raise
        text=Path(log).read_text(errors='replace')
        bad=(r.returncode==0 or rejection not in text) if rejection else r.returncode!=0
        record['commands'].append(dict(argv=args,exit_code=r.returncode,expected_rejection=rejection,
            log_sha256=af07.digest(Path(log)),tail=text[-3000:] if bad else text[-160:]));save()
        if bad:raise RuntimeError('AF07 build/check failed: '+str(log))
        return text
    def freeze():
        launch_intake(ENGINE)
        if af07.intake()!=record['delivery']:raise ValueError('AF07 selected delivery drift')
        for name,checksum in record['inputs'].items():
            if af07.digest(Path(name))!=checksum:raise ValueError('AF07 input drift: '+name)
        for name,checksum in manifest['files'].items():
            if af07.digest(current/name)!=checksum:raise ValueError('AF07 native dependency drift: '+name)
        for name,checksum in record['artifacts'].items():
            if af07.digest(Path(name) if failures else out/name)!=checksum:raise ValueError('AF07 artifact drift: '+name)
    print('[RUNNING] AF07 preparation: '+str(out),file=sys.stderr,flush=True)
    try:
        verify();record['delivery']=af07.intake();current=ROOT/'.deps/native-current'
        manifest=json.loads((current/'current-inputs.json').read_text())
        tools=json.loads((current/'sdk/tools.lock.json').read_text())['tools'];record['tools']=tools
        record['dependency']=dict(manifest_sha256=af07.digest(current/'current-inputs.json'),members=len(manifest['files']))
        sources=[ROOT/'build.zig',ROOT/'boot/dependencies.json',current/'current-inputs.json']
        sources += [p for d in ('user','kernel','scripts') for p in (ROOT/d).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='.DS_Store']
        sources += [Path(shutil.which(n)).resolve() for n in ('zig','qemu-system-x86_64','xorriso')]
        record['inputs']={str(p):af07.digest(p) for p in sources}|record['delivery']['inputs']
        freeze()
        # Build/admit the entire selected matrix before touching any guest media.
        for case in profiles:
            # Native media ownership requires a direct, private zig-out child.
            # Keep that guard intact rather than admitting nested owners.
            root=out.with_name(out.name+'-'+case) if failures else out
            if failures:
                root.mkdir();owned.append(root)
                record['owned_output_roots'].append(str(root))
            detail={} if failures else record
            if failures:record['profiles'][case]=detail
            stages=dict(baseline=root/'baseline',writer=root/'writer',reader=root/'reader')
            prepared.append((case,root,detail,stages))
            print('[RUNNING] AF07 prepare '+case,file=sys.stderr,flush=True)
            if baseline is None:baseline=build_reader(out/'baseline',command,tools)
            detail['baseline']=baseline
            if failures:
                stages['baseline'].mkdir()
                for name in ('aether.iso','engine.elf','supervisor.raw'):
                    shutil.copyfile(out/'baseline'/name,stages['baseline']/name)
                    if af07.digest(out/'baseline'/name)!=af07.digest(stages['baseline']/name):
                        raise ValueError('AF07 baseline copy drift')
            writer=root/'writer'
            if case in af07.METADATA_REPLIES+af07.METADATA_PROVIDERS:
                if metadata_base is None:
                    metadata_base=af07.prepare_engine(out/'metadata-base',command,tools)
                    record['metadata_preparation']={k:v for k,v in metadata_base.items() if k!='commands'}
                writer.mkdir()
                base=metadata_base
            else:base=af07.prepare_engine(writer,command,tools,case=case)
            detail['writer']=af07.recompose(writer,base,record['delivery'],command,tools,case=case,
                                            **({'retirement':True} if group=='retirement' else {}))
            text=(af07.SERVICE/'metadata-controller.rs').read_text().replace(
                '// Build selection inserts absolute, immutable-at-run module paths here.',
                '#[path = '+json.dumps(str(af07.SERVICE/'fs-service-client.rs'))+']\nmod namespace_client;\n'
                +'#[path = '+json.dumps(str(af07.SERVICE/'fs-activation-client.rs'))+']\nmod activation;')
            source=writer/'controller.rs';source.write_text(af07.controller(text,writer,diagnostic,case))
            if diagnostic:detail['assertion_sites']=json.loads((writer/'assertion-sites.json').read_text())
            rust(writer,source,command,True,case);detail['writer_image']=image(writer,command,True)
            empty=case in ('lost-reply','partial-request')
            if empty not in readers:
                reader=out/('reader-empty' if empty else 'reader-final') if failures else root/'reader'
                summary=af07.prepare_engine(reader,command,tools,True,empty=empty)
                # Commands are retained once, not copied into each recipe summary.
                summary.pop('commands');summary.pop('old_service')
                shutil.copyfile(reader/'port/engine.elf',reader/'engine.elf')
                text=(ROOT/'user/storage/session/readback.rs').read_text()
                text=af07.replace(text,'b"BIUVWLP????????OAMZDJFR"','b"BIUVWLP????????OAMT????????SDJFR"')
                text=af07.replace(text,'(7..15).contains(&stage)','((7..15).contains(&stage) || (19..27).contains(&stage))')
                source=reader/'controller.rs';source.write_text(text);rust(reader,source,command)
                readers[empty]=(reader,summary,image(reader,command))
            reader,detail['recovery'],detail['recovery_image']=readers[empty]
            if failures:
                stages['reader'].mkdir()
                for name in ('aether.iso','engine.elf','supervisor.raw'):
                    shutil.copyfile(reader/name,stages['reader']/name)
                    if af07.digest(reader/name)!=af07.digest(stages['reader']/name):
                        raise ValueError('AF07 recovery copy drift')
            if failures:detail['image_roots']={k:str(v) for k,v in stages.items()}
            detail['fixture']=prepare_native_fixture(root);disk=root/'native-namespace.raw'
            detail['pristine_media']=native_media_snapshot(disk)
        record['owned_output_roots']=list(map(str,owned))
        record['artifacts']={artifact_key(p):af07.digest(p) for root in owned for p in root.rglob('*') if p.is_file() and p.name!='results.json'}
        freeze();record['status']='prepared';save()
        if execute:
            for case,root,detail,stages in prepared:
                disk=root/'native-namespace.raw'
                for role in ('baseline','writer','reader'):
                    freeze()
                    before=native_media_snapshot(disk) if role!='reader' else runtime.check_zpl_recovery_media(writer_result,disk)
                    row=dict(role=role,name='pool-import',status='running',media_before=before,
                        start_utc=datetime.now(timezone.utc).isoformat())
                    if failures:row['profile']=case
                    record['cases'].append(row);record['native_attempted']=True;save()
                    print('[RUNNING] AF07 '+case+'/'+role,file=sys.stderr,flush=True)
                    stage=stages[role]
                    # Prior shared-image logs were captured before reuse. Remove
                    # only these generated logs so a preflight error cannot bind
                    # an older guest's records to this attempt.
                    for name in ('native-serial.log','native-qemu-command.json'):
                        (stage/name).unlink(missing_ok=True)
                    run(stage/'aether.iso',marker=b'AETHER NATIVE BLOCK PASS',entropy=True,
                        rtc_base='2026-10-06T12:34:00',block_disk=disk,block_large=True,block_namespace=True,
                        _pair_stop=True,**({'_zpl_writer_60s':True} if role=='writer' else {'zpl_writer':writer_result} if role=='reader' else {}))
                    row['vm_run_returned']=True
                    row['qemu']=json.loads((stage/'native-qemu-command.json').read_text())
                    row['media_after']=written_native_media_snapshot(disk) if role=='writer' else runtime.check_zpl_recovery_media(writer_result,disk) if role=='reader' else native_media_snapshot(disk)
                    serial=stage/'native-serial.log';text=serial.read_text()
                    key=case+'/'+role if failures else role
                    record.setdefault('serial',{})[key]=dict(sha256=af07.digest(serial),tail=text[-6000:],machine_witness=oracle_witness(text))
                    require_oracle_witness(text)
                    row.update(runtime.check_engine_trace(text,'AETHER NATIVE BLOCK PASS'))
                    row.update(runtime.check_pool_cleanup_trace(text))
                    row.update(runtime.check_namespace_trace(text) if role=='baseline' else runtime.check_zpl_write_trace(text) if role=='writer' else runtime.check_zpl_recovery_trace(text))
                    row.update(status='pass',disk_sha256=row['media_after']['sha256'],end_utc=datetime.now(timezone.utc).isoformat());save()
                    if role=='writer':writer_result=row
                    elif row['media_before']!=row['media_after']:raise ValueError('AF07 reader changed media')
                    # Rebind only after the stopped, qualified writer.
                    if role=='writer':record['artifacts'][artifact_key(disk)]=af07.digest(disk)
                detail['pair']=runtime.check_zpl_recovery_pair(writer_result,record['cases'][-1]);freeze()
            record['status']='pass'
        return out
    except BaseException as error:
        stopped=not isinstance(error,NativeStopError)
        record.update(status='failed',error=str(error),vm_stop_confirmed=stopped,triage_required=record['native_attempted'])
        if record['cases']:record['cases'][-1].update(status='failed',error=str(error))
        raise
    finally:
        # Record stopped disposable media even on an unqualified native error.
        # A hash/guard observation does not establish export/device quiescence.
        for case,root,detail,stages in prepared:
            disk=root/'native-namespace.raw'
            if stopped and disk.is_file():
                from openzfs_namespace import _native_media_snapshot
                try:detail['stopped_media']=_native_media_snapshot(disk)
                except (OSError,ValueError) as error:detail['stopped_media']=dict(status='unavailable',error=str(error))
            for role in ('baseline','writer','reader'):
                key=case+'/'+role if failures else role
                attempted=any(c['role']==role and c.get('profile','normal')==case for c in record['cases'])
                qemu=stages[role]/'native-qemu-command.json'
                if attempted and qemu.is_file():
                    row=next(c for c in record['cases'] if c['role']==role and c.get('profile','normal')==case)
                    if 'qemu' not in row:
                        try:row['qemu']=json.loads(qemu.read_text())
                        except (OSError,ValueError) as error:
                            row['qemu_capture_error']=str(error)
                serial=stages[role]/'native-serial.log'
                if attempted and key not in record.get('serial',{}) and serial.is_file():
                    text=serial.read_text(errors='replace')
                    record.setdefault('serial',{})[key]=dict(sha256=af07.digest(serial),tail=text[-6000:],machine_witness=oracle_witness(text))
        if stopped:
            count=sum(p.is_file() for root in owned for p in root.rglob('*'))
            for root in owned:
                if root!=out:shutil.rmtree(root)
                else:
                    for path in out.iterdir():
                        if path.is_dir():shutil.rmtree(path)
                        elif path.name!='results.json':path.unlink()
            record['cleanup']=dict(stopped=True,removed_generated_members=max(0,count-1),remaining='results.json only')
        else:record['cleanup']=dict(stopped=False,retained=list(map(str,owned)))
        record['end_utc']=datetime.now(timezone.utc).isoformat();save()
        print(('[PASS] ' if record['status'] in ('pass','prepared') else '[FAIL] ')+str(out/'results.json'),file=sys.stderr)


if __name__=='__main__':
    class Parser(argparse.ArgumentParser):
        def error(self,message):
            print('[FAIL] '+runtime.display(message),file=sys.stderr);raise SystemExit(64)
    parser=Parser(description=__doc__)
    parser.add_argument('--run',action='store_true',help='qualify one fresh baseline/writer/recovery batch; no retries')
    parser.add_argument('--version',action='version',version='aether-fs-metadata-service 1')
    parser.add_argument('--diagnostic',action='store_true',help='separate numbered-check controller; native use requires disposition after unexpected persistence failure')
    parser.add_argument('--failure-paths',nargs='?',const='inherited',choices=tuple(af07.FAILURE_GROUPS),
        help='fixed inherited, replies, providers or retirement batch; admit every distinct image before execution')
    args=parser.parse_args()
    try:campaign(args.run,args.diagnostic,args.failure_paths)
    except Exception as error:
        print('[FAIL] '+runtime.display(error),file=sys.stderr);raise SystemExit(1)
