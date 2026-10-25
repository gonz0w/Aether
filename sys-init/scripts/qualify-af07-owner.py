#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Prepare or qualify the explicitly selected guarded AF07 boot diagnostic."""
import argparse
from contextlib import redirect_stdout
import hashlib
import json
import os
from pathlib import Path
import re
import selectors
import shutil
import signal
import struct
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from fs_metadata_launch import closure, intake as engine_intake
from fs_af07_inputs import digest
from bounded_tools import run_tool

SCRIPT=b"printf 'AF07-BEGIN\\n'\n/inputs/helper status\nprintf 'AF07-STATUS:%s\\n' \"$?\"\nexit\n"
SCRIPTS={
    'exec-wait':SCRIPT,
    'exec-missing':b"printf 'AF07-BEGIN\\n'\n/inputs/missing\nprintf 'AF07-STATUS:%s\\n' \"$?\"\nprintf 'AF07-PARENT:ok\\n'\nexit\n",
    'exec-denied':b"printf 'AF07-BEGIN\\n'\n/inputs/denied\nprintf 'AF07-STATUS:%s\\n' \"$?\"\nprintf 'AF07-PARENT:ok\\n'\nexit\n",
    'parent-close':b"printf 'AF07-BEGIN\\n'\n/inputs/helper status\nprintf 'AF07-STATUS:%s\\n' \"$?\"\nexec 2>&-\nprintf 'AF07-PARENT:ok\\n'\nexit\n",
}
PROFILE='AENFS005/AENMX010/ABI31'
PREFIX='thread-suite-service-runtime-zpl-pair-fs-session-owner31-'


def case_script(case):
    if not isinstance(case,str) or case not in SCRIPTS:raise ValueError('guarded unknown fixed case')
    return SCRIPTS[case]


def intake(directory,seal):
    root,members=closure(directory,seal)
    expected={'inputs.json','owner.elf','owner.bin','shell.elf','helper.elf','envelope.bin'}
    if set(members)!=expected:raise ValueError('guarded input member closure')
    record=json.loads((root/'inputs.json').read_text())
    cwd=record.get('cwd_wire',False)
    if type(cwd) is not bool:raise ValueError('guarded invalid CWD selection')
    if (record.get('format')!=('aether-guarded-af08-inputs-v1' if cwd else 'aether-guarded-af07-inputs-v1') or record.get('profile')!=PROFILE
            or record.get('status')!='prepared' or record.get('native_executed') is not False):
        raise ValueError('guarded input profile/coverage')
    if (type(record.get('path_probe',False)) is not bool or type(record.get('dup2_wire',False)) is not bool or
            (record.get('dup2_wire',False) and not record.get('path_probe',False)) or
            (cwd and not record.get('dup2_wire',False)) or
            record.get('file_wire','AEFD0001') != ('AEFP0003' if cwd else 'AEFP0002' if record.get('dup2_wire',False) else 'AEFP0001' if record.get('path_probe',False) else 'AEFD0001')):
        raise ValueError('guarded FILE variant/probe mismatch')
    for group in ('inputs','tools','rust_native_libraries'):
        if not record.get(group):raise ValueError('missing guarded live closure')
        for name,expected_hash in record[group].items():
            path=Path(name)
            if not path.is_absolute() or not path.is_file() or digest(path)!=expected_hash:
                raise ValueError('guarded live input drift: '+name)
    for name,row in record['artifacts'].items():
        if name not in expected-{'inputs.json'} or row!={'bytes':(root/name).stat().st_size,'sha256':members[name]}:
            raise ValueError('guarded artifact metadata')
    if set(record['artifacts'])!=expected-{'inputs.json'}:raise ValueError('guarded artifact set')
    m=record['measurement'];stack=m['stack']
    if (m['code_budget']!=49152 or not 0<m['code_bytes']<=49152 or not m['code_fits'] or
            not m['resident_fits'] or not 0<m['runtime_bytes']<=4096 or
            m['workspace_bytes']!=4096 or m['mapped_bytes']!=8192 or
            stack['status']!='pass' or stack['usable_stack_bytes']!=8184 or
            not 0<stack['entry_stack_bytes']<=8184 or m['native_executed'] is not False):
        raise ValueError('guarded fixed code/data/stack budget')
    raw=(root/'owner.bin').read_bytes();elf=(root/'owner.elf').read_bytes()
    if len(raw)!=m['code_bytes'] or digest(root/'owner.bin')!=m['raw_sha256'] or digest(root/'owner.elf')!=m['elf_sha256']:
        raise ValueError('guarded measured owner correspondence')
    if elf[:6]!=b'\x7fELF\x02\x01' or len(elf)<64 or struct.unpack_from('<Q',elf,24)[0]!=0x400000:
        raise ValueError('guarded owner entry')
    at=struct.unpack_from('<Q',elf,32)[0];stride,count=struct.unpack_from('<HH',elf,54)
    if stride!=56 or at+stride*count>len(elf):raise ValueError('guarded owner ELF bounds')
    loads=[struct.unpack_from('<IIQQQQQQ',elf,at+i*stride) for i in range(count)
           if struct.unpack_from('<I',elf,at+i*stride)[0]==1]
    if len(loads)!=1:raise ValueError('guarded owner LOAD count')
    _,flags,offset,address,_,size,memory,_=loads[0]
    if flags!=5 or address!=0x400000 or size!=len(raw) or memory!=size or elf[offset:offset+size]!=raw:
        raise ValueError('guarded owner RX/raw contract')
    engine=record['engine'];engine_path=Path(engine['directory'])
    if engine_path.is_absolute() or '..' in engine_path.parts:raise ValueError('guarded engine path')
    if cwd:
        from fs_context_launch import intake as context_intake
        selected=context_intake(ROOT/engine_path,engine['seal'])
    else:
        selected=engine_intake(ROOT/engine_path,engine['seal'])
    if selected['elf_sha256']!=engine['elf_sha256']:raise ValueError('guarded engine association')
    envelope=(root/'envelope.bin').read_bytes();engine_bytes=(ROOT/engine_path/'filesystem.elf').read_bytes()
    a=(root/'shell.elf').read_bytes();b=(root/'helper.elf').read_bytes()
    nested=struct.pack('<8sIIIIQ',b'AENMX010',len(a),len(a),len(b),len(raw),0)+bytes(range(80))+a+a+b+raw
    wanted=struct.pack('<8sII',b'AENFS005',len(engine_bytes),len(nested))+bytes(range(32))+engine_bytes+nested
    if envelope!=wanted:raise ValueError('guarded exact envelope association')
    # Execute the enforcing parser on these exact bytes, never the user code.
    # Temporary sources live outside frozen kernel/user/script inputs.
    with tempfile.TemporaryDirectory(prefix='aether-af07-admission-') as folder:
        work=Path(folder);(work/'envelope.bin').write_bytes(envelope)
        (work/'admit.zig').write_text('const c=@import("composition");test "guarded admission"{_=try c.parseOwnerStack(@embedFile("envelope.bin"));}')
        zig=next(name for name in record['tools'] if Path(name).name=='zig')
        try:
            run_tool([zig,'test','--cache-dir',str(ROOT/'.zig-cache'),'--global-cache-dir',str(ROOT/'.zig-cache/global'),
                '--dep','composition','-Mroot='+str(work/'admit.zig'),'-Mcomposition='+str(ROOT/'kernel/native_fs_session.zig')],
                dict(os.environ),work/'admit.log',timeout=60,cwd=ROOT)
        except subprocess.SubprocessError as error:
            raise ValueError('guarded structural loader rejected: '+(work/'admit.log').read_text(errors='replace')[-600:]) from error
    return record



def reader_dependencies():
    """Validate original object pins and bind the independent reader runtime."""
    current=ROOT/'.deps/native-current'
    manifest=current/'current-inputs.json'
    files=json.loads(manifest.read_text())['files']
    for name,expected in files.items():
        path=current/name
        if Path(name).is_absolute() or '..' in Path(name).parts or digest(path)!=expected:
            raise ValueError('guarded reader original input drift: '+name)
    runtime=ROOT/'.deps/native-utc-v3'
    rows={str(path.relative_to(runtime)):digest(path) for path in sorted(runtime.rglob('*'))
          if path.is_file() and '__pycache__' not in path.parts}
    return dict(original_manifest_sha256=digest(manifest),original_files=len(files),
                runtime_files=len(rows),runtime_sha256=hashlib.sha256(
                    json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest())



CLOCK=re.compile(r'NATIVE CLOCK park task=[0-9]+ start=[0-9]+ deadline=[0-9]+|NATIVE CLOCK timeout task=[0-9]+ now=[0-9]+ elapsed=[0-9]+')


def transcript_witness(text):
    """Keep all non-clock UART bytes, including stdout and partial lines."""
    kept=[];clocks=hashlib.sha256();count=0
    for line in text.splitlines(keepends=True):
        if line.endswith('\n') and CLOCK.fullmatch(line[:-1]):
            clocks.update(line.encode());count+=1
        else:kept.append(line)
    selected=''.join(kept);data=selected.encode();complete=len(data)<=65536
    return dict(format='aether-af07-owner-transcript-v1',complete=complete,ceiling_utf8_bytes=65536,
        text=selected if complete else '',retained_utf8_bytes=len(data) if complete else 0,
        retained_sha256=hashlib.sha256(data if complete else b'').hexdigest(),
        raw_sha256=hashlib.sha256(text.encode()).hexdigest(),source_lines=len(text.splitlines(keepends=True)),
        retained_lines=len(kept) if complete else 0,clocks=dict(lines=count,sha256=clocks.hexdigest()))


def transcript_text(row):
    fields={'format','complete','ceiling_utf8_bytes','text','retained_utf8_bytes','retained_sha256',
            'raw_sha256','source_lines','retained_lines','clocks'}
    if (not isinstance(row,dict) or set(row)!=fields or row.get('format')!='aether-af07-owner-transcript-v1'
            or row.get('complete') is not True or row.get('ceiling_utf8_bytes')!=65536
            or not isinstance(row.get('text'),str) or not isinstance(row.get('clocks'),dict)
            or set(row['clocks'])!={'lines','sha256'}):raise ValueError('guarded incomplete/invalid transcript')
    data=row['text'].encode();clock=row['clocks']
    if (any(type(row.get(name)) is not int or row[name]<0 for name in ('source_lines','retained_lines','retained_utf8_bytes'))
            or type(clock.get('lines')) is not int or clock['lines']<0
            or any(not isinstance(value,str) or re.fullmatch('[0-9a-f]{64}',value) is None
                   for value in (row['retained_sha256'],row['raw_sha256'],clock['sha256']))
            or len(data)>65536 or len(data)!=row['retained_utf8_bytes']
            or hashlib.sha256(data).hexdigest()!=row['retained_sha256']
            or len(row['text'].splitlines(keepends=True))!=row['retained_lines']
            or row['source_lines']!=row['retained_lines']+clock['lines']
            or (clock['lines']==0 and clock['sha256']!=hashlib.sha256(b'').hexdigest())
            or any(line.endswith('\n') and CLOCK.fullmatch(line[:-1]) for line in row['text'].splitlines(keepends=True))):
        raise ValueError('guarded transcript identity/count/bound')
    return row['text']


def writer_trace(text,case='exec-wait',path_probe=False,dup2_probe=False,cwd_probe=False):
    if type(cwd_probe) is not bool or (cwd_probe and not dup2_probe):raise ValueError('guarded unsupported CWD probe')
    case_script(case)
    if type(dup2_probe) is not bool or (dup2_probe and not path_probe):raise ValueError('guarded unsupported dup2 probe')
    if type(path_probe) is not bool or (path_probe and case!='exec-wait'):
        raise ValueError('guarded unsupported read-probe case')
    if (text.count('AF07-READ:ok\n')!=int(path_probe) or
            sum(line.startswith('AF07-READ:') for line in text.splitlines())!=int(path_probe)):
        raise ValueError('guarded actual persistent read marker')
    replaced=case in ('exec-wait','parent-close')
    status={'exec-missing':127,'exec-denied':126}.get(case,7)
    status_line=f'AF07-STATUS:{status}'
    if text.count('AETHER NATIVE BLOCK PASS')!=1 or any(s in text for s in ('PANIC','NATIVE fault ','NATIVE supervisor result=')):
        raise ValueError('guarded writer failed/completion')
    # Observe the actual child's collected status, never infer refusal from EOF.
    if (text.count('AF07-BEGIN\n')!=1 or text.count(status_line+'\n')!=1 or
            sum(line.startswith('AF07-STATUS:') for line in text.splitlines())!=1 or
            text.count('AF07-PARENT:ok\n')!=int(case!='exec-wait') or
            sum(line.startswith('AF07-PARENT:') for line in text.splitlines())!=int(case!='exec-wait')):
        raise ValueError('guarded actual shell/exec/wait output')
    admissions=re.findall(r'^NATIVE MEMORY admitted slot=(\d+) generation=(\d+) used=(\d+) remaining=(\d+)$',text,re.M)
    # AF08's physical-directory engine and public-CWD helper have distinct
    # measured page geometry. Select exact counts, never a loose budget range.
    engine_used,helper_used=(1331,34) if cwd_probe else (1329,33)
    expected_admissions=[('0','1',str(engine_used),str(8192-engine_used)),('1','1','80','48')]
    if replaced:expected_admissions.append(('2','1',str(helper_used),str(128-helper_used)))
    if (admissions!=expected_admissions or
            sum(s.startswith('NATIVE MEMORY admitted') for s in text.splitlines())!=len(expected_admissions)):
        raise ValueError('guarded exact loader identities/geometry')
    terminals=re.findall(r'^NATIVE terminal slot=(\d+) generation=(\d+) kind=(\d+) detail=(\d+)$',text,re.M)
    if (terminals!=[('2','1','1',str(status)),('1','1','1','0'),('0','1','1','0')] or
            sum(s.startswith('NATIVE terminal') for s in text.splitlines())!=3):
        raise ValueError('guarded exact terminal identities/order')
    rows=[line for line in text.splitlines() if line.startswith('NATIVE CLEANUP ')]
    wanted=[]
    for slot,pages,prior in ((2,128,0),(1,128,1),(0,8192,2)):
        wanted += [f'NATIVE CLEANUP v=1 slot={slot} generation=1 phase={phase} selected={slot if phase==1 else 6} pages={pages} reclaimed={prior+(phase==7)}' for phase in range(1,8)]
    if rows!=wanted:raise ValueError('guarded complete cleanup order')
    halts=re.findall(r'^NATIVE init halted ticks=(\d+) idle=(\d+) reclaimed=(\d+)$',text,re.M)
    if (len(halts)!=1 or sum(s.startswith('NATIVE init halted') for s in text.splitlines())!=1 or
            not 0<int(halts[0][0])<=6000 or int(halts[0][2])!=3 or
            not text.endswith('AETHER NATIVE BLOCK PASS\n')):
        raise ValueError('guarded halt/tick/reclaim bound')
    lines=text.splitlines()
    if any(line.startswith('NATIVE observation ') for line in lines):
        raise ValueError('guarded writer must not use conformance observations')
    order=[next(line for line in lines if line.startswith('NATIVE MEMORY admitted slot=0 ')),
           next(line for line in lines if line.startswith('NATIVE MEMORY admitted slot=1 ')),
           'AF07-BEGIN']
    if replaced:order.append(next(line for line in lines if line.startswith('NATIVE MEMORY admitted slot=2 ')))
    order += [f'NATIVE terminal slot=2 generation=1 kind=1 detail={status}',*wanted[:7],status_line]
    if case!='exec-wait':order.append('AF07-PARENT:ok')
    order += ['NATIVE terminal slot=1 generation=1 kind=1 detail=0',*wanted[7:14],
           'NATIVE terminal slot=0 generation=1 kind=1 detail=0',*wanted[14:],
           next(line for line in lines if line.startswith('NATIVE init halted ')),'AETHER NATIVE BLOCK PASS']
    if path_probe:
        if not lines.index('AF07-BEGIN') < lines.index('AF07-READ:ok') < lines.index('NATIVE terminal slot=2 generation=1 kind=1 detail=7'):
            raise ValueError('guarded read marker ordering')
    positions=[lines.index(line) for line in order]
    if positions!=sorted(positions):raise ValueError('guarded admission/terminal/cleanup/output ordering')
    pending=set();owners=set();waits=wakes=0
    for line in lines:
        if not line.startswith('NATIVE STORAGE WAIT '):continue
        match=re.fullmatch(r'NATIVE STORAGE WAIT slot=(\d+) generation=(\d+) phase=(park|wake) status=0',line)
        if match is None:raise ValueError('guarded wait syntax/status')
        slot,generation,phase=match.groups();key=int(slot),int(generation)
        if key not in ((0,1),(1,1),(2,1),(6,0)):raise ValueError('guarded wait identity')
        if phase=='park':
            if key in pending:raise ValueError('guarded duplicate park')
            pending.add(key);owners.add(key[0]);waits+=1
        else:
            if key not in pending:raise ValueError('guarded unmatched wake')
            pending.remove(key);wakes+=1
    if pending or owners!={0,1,2,6} or waits!=wakes:raise ValueError('guarded incomplete primary waits')
    return dict(profile=PROFILE,status='pass',read_only_activation=True,
                shell_exec_wait=True,persistent_path_read_probe=path_probe,persistent_dup2_probe=dup2_probe,persistent_cwd_probe=cwd_probe,process_case=case,child_status=status,exec_replaced=replaced,
                primary_channel_waits=waits,primary_channel_wakes=wakes,admitted_instances=3,reclaimed=3,engine_terminal_zero=True,
                source_bound_readiness_and_shutdown=True)


def guest(output,role,qemu,case='exec-wait'):
    """One fixed emulator; process-group teardown is separate from guest success."""
    script=case_script(case)
    from deps import DEPS,LOCK,verify
    from native_smoke import NativeStopError
    verify()
    if subprocess.check_output([qemu,'--version'],text=True).splitlines()[0]!='QEMU emulator version '+LOCK['qemu']:
        raise ValueError('guarded emulator version')
    stage=output/('writer' if role=='writer' else 'reader')
    variables=stage/'vars.fd';shutil.copyfile(DEPS/'firmware/vars.fd',variables)
    args=[qemu,'-machine','pc-q35-11.1','-accel','tcg','-cpu','qemu64','-smp','1','-m','256M',
        '-drive',f'if=pflash,format=raw,readonly=on,file={DEPS/"firmware/code.fd"}',
        '-drive',f'if=pflash,format=raw,file={variables}','-cdrom',str(stage/'aether.iso'),'-boot','d',
        '-nic','none','-vga','std','-display','none','-serial','stdio','-monitor','none','-no-reboot','-no-shutdown',
        '-object','rng-random,id=random,filename=/dev/urandom',
        '-device','virtio-rng-pci,rng=random,disable-modern=on,max-bytes=1048576,period=1000',
        '-rtc','base=2026-10-06T12:34:00,clock=vm',
        '-drive','if=none,id=work,format=raw,cache=writeback,file='+str(output/'native-namespace.raw'),
        '-device','virtio-blk-pci,drive=work,disable-modern=on']
    row=dict(role=role,argv=args,watchdog_seconds=60 if role=='writer' else 30,
             kernel_tick_limit=6000 if role=='writer' else 3000,input_writes=[],vm_stop_confirmed=False)
    raw,errors=bytearray(),bytearray();child=None
    try:
        child=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
        os.set_blocking(child.stdin.fileno(),False)
        deadline=time.monotonic()+row['watchdog_seconds']
        sent=0
        with selectors.DefaultSelector() as selector:
            selector.register(child.stdout,selectors.EVENT_READ,raw)
            selector.register(child.stderr,selectors.EVENT_READ,errors)
            while time.monotonic()<deadline:
                for key,_ in selector.select(0.02):
                    chunk=os.read(key.fd,4096)
                    if not chunk:selector.unregister(key.fileobj);continue
                    if len(key.data)+len(chunk)>1024*1024:raise ValueError('guarded host raw output bound')
                    key.data.extend(chunk)
                if b'AETHER PANIC:' in raw or b'NATIVE fault ' in raw:raise ValueError('guarded guest fault')
                if b'AETHER NATIVE BLOCK PASS\n' in raw:
                    if role=='writer' and sent!=len(script):raise ValueError('guarded incomplete serial input')
                    break
                if not selector.get_map():raise ValueError('guarded premature guest exit')
                # QEMU's UART supplies backpressure. Admission permits enqueueing
                # only this fixed test input; it is not application readiness.
                if role=='writer' and sent<len(script) and b'NATIVE MEMORY admitted slot=1 generation=1 ' in raw:
                    chunk=script[sent:sent+7]
                    try:accepted=os.write(child.stdin.fileno(),chunk)
                    except BlockingIOError:continue
                    if not 0<accepted<=len(chunk):raise ValueError('guarded serial input failed')
                    row['input_writes'].append(dict(offset=sent,requested_hex=chunk.hex(),accepted=accepted))
                    sent+=accepted
            else:raise TimeoutError('guarded fixed guest watchdog')
        row['vm_run_returned']=True
        return bytes(raw).decode(errors='strict'),row
    finally:
        stop_error=None
        if child is not None:
            try:
                if child.poll() is None:
                    try:os.killpg(child.pid,signal.SIGTERM)
                    except ProcessLookupError:pass
                try:child.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid,signal.SIGKILL);child.wait(timeout=3)
                row.update(vm_stop_confirmed=True,emulator_exit=child.returncode)
            except (OSError,subprocess.SubprocessError) as error:
                stop_error=NativeStopError('guarded VM stop unconfirmed; retain '+str(output))
                row['stop_error']=str(error)
            finally:
                for pipe in (child.stdin,child.stdout,child.stderr):
                    try:pipe.close()
                    except OSError as error:row['pipe_close_error']=str(error)
        row.update(serial_sha256=hashlib.sha256(raw).hexdigest(),stderr_sha256=hashlib.sha256(errors).hexdigest(),
                   serial_tail=bytes(raw[-6000:]).decode(errors='replace'),stderr_tail=bytes(errors[-1200:]).decode(errors='replace'))
        if role=='writer':
            try:row['transcript']=transcript_witness(bytes(raw).decode(errors='strict'))
            except UnicodeDecodeError as error:row['transcript_error']=str(error)
        try:(output/(role+'-guest.json')).write_text(json.dumps(row,indent=2)+'\n')
        finally:
            # A report I/O error must never mask an unconfirmed live VM.
            if stop_error is not None:raise stop_error


def symbolize_panic(output,receipt,row):
    """Attribute only a supplied kernel PC against the exact pending ELF."""
    text=transcript_text(row['transcript'])
    sites=re.findall(r'^NATIVE PANIC pc=([0-9a-f]{1,16})$',text,re.M)
    site_lines=sum(line.startswith('NATIVE PANIC ') for line in text.splitlines())
    if not site_lines:return dict(status='missing-site',reason='No complete caller address; original failure remains')
    if len(sites)!=1 or site_lines!=1:
        raise ValueError('guarded panic site count/format')
    pc=int(sites[0],16);kernel=Path(output)/'writer/kernel.elf'
    if digest(kernel)!=receipt['kernel_elf_sha256']:raise ValueError('guarded panic ELF identity')
    data=kernel.read_bytes()
    if len(data)<64 or data[:6]!=b'\x7fELF\x02\x01':raise ValueError('guarded panic ELF header')
    at=struct.unpack_from('<Q',data,32)[0];stride,count=struct.unpack_from('<HH',data,54)
    if stride!=56 or at+stride*count>len(data):raise ValueError('guarded panic ELF program bounds')
    ranges=[]
    for index in range(count):
        kind,flags,_,address,_,_,size,_=struct.unpack_from('<IIQQQQQQ',data,at+index*stride)
        if kind==1 and flags&1:ranges.append((address,size))
    if pc==0 or not any(address<=pc-1 and pc-1-address<size for address,size in ranges):
        raise ValueError('guarded panic PC outside executable kernel')
    tool=receipt['symbolizer']
    if digest(tool['path'])!=tool['sha256']:raise ValueError('guarded symbolizer identity')
    args=[tool['path'],'--obj='+str(kernel),'--inlining','--demangle','--no-debuginfod',hex(pc),hex(pc-1)]
    log=Path(output)/'panic-symbols.log'
    result=run_tool(args,dict(os.environ),log,timeout=10,limit=4*1024*1024,cwd=ROOT)
    decoded=result.decode(errors='strict')
    warnings=[line for line in decoded.splitlines(keepends=True) if line.startswith('warning:')]
    mapping=''.join(line for line in decoded.splitlines(keepends=True) if not line.startswith('warning:'))
    if len(mapping.encode())>4096:raise ValueError('guarded symbol mapping retained bound')
    status=('symbolized-with-warnings' if warnings else 'symbolized') if re.search(r':[1-9][0-9]*:[0-9]+',mapping) else 'unresolved'
    return dict(status=status,pc=hex(pc),call_site=hex(pc-1),kernel_elf_sha256=receipt['kernel_elf_sha256'],
                argv=args,timeout_seconds=10,output_limit=4*1024*1024,output_sha256=digest(log),output=mapping,
                warning_lines=len(warnings),warning_sha256=hashlib.sha256(''.join(warnings).encode()).hexdigest(),
                warning_prefix=''.join(warnings)[:1500],attribution='Candidate location only; warnings and source/instruction verification remain separate')


def execute(output,expected):
    """Fixed pristine/writer/recovery sequence. No retry or reader after failure."""
    from native_smoke import NativeStopError
    from openzfs_namespace import prepare_native_fixture,native_media_snapshot,_native_media_snapshot
    from fs_session import metadata_oracle_witness,metadata_oracle_text
    import service_runtime_smoke as runtime
    output=Path(output).absolute()
    if (output.parent!=ROOT/'zig-out' or output.resolve()!=output or not output.name.startswith(PREFIX)):
        raise ValueError('guarded prepared output ownership')
    if not re.fullmatch('[0-9a-f]{64}',expected) or digest(output/'results.json')!=expected:
        raise ValueError('guarded prepared receipt identity')
    receipt=json.loads((output/'results.json').read_text())
    case=receipt.get('case','exec-wait');script=case_script(case)
    if receipt['status']!='prepared' or receipt['profile']!=PROFILE or receipt['script_hex']!=script.hex():
        raise ValueError('guarded prepared selection')
    if set(receipt['artifacts'])!={'writer','reader'} or receipt['reader']['read_grant_only'] is not True:
        raise ValueError('guarded prepared roles/read authority')
    def freeze():
        if digest(Path(__file__))!=receipt['harness_sha256']:raise ValueError('guarded harness changed')
        if receipt.get('emulator') not in receipt['freeze']:raise ValueError('guarded emulator identity missing')
        if digest(output/'writer/kernel.elf')!=receipt['kernel_elf_sha256']:raise ValueError('guarded prepared kernel ELF changed')
        if receipt['freeze'].get(receipt['symbolizer']['path'])!=receipt['symbolizer']['sha256']:raise ValueError('guarded missing symbolizer pin')
        for name,expected in receipt['freeze'].items():
            if digest(name)!=expected:raise ValueError('guarded prepared input drift: '+name)
        for role,expected in receipt['artifacts'].items():
            if digest(output/role/'aether.iso')!=expected:raise ValueError('guarded prepared ISO changed')
        if reader_dependencies()!=receipt['reader_dependencies']:raise ValueError('guarded reader dependency drift')
        current=intake(receipt['inputs_directory'],receipt['inputs_seal'])
        if (type(receipt.get('path_probe',False)) is not bool or
                receipt.get('path_probe',False)!=current.get('path_probe',False) or
                type(receipt.get('dup2_wire',False)) is not bool or
                receipt.get('dup2_wire',False)!=current.get('dup2_wire',False) or
                type(receipt.get('cwd_wire',False)) is not bool or
                receipt.get('cwd_wire',False)!=current.get('cwd_wire',False) or
                (receipt.get('path_probe',False) and case!='exec-wait')):
            raise ValueError('guarded prepared read-probe selection')
        for group in ('inputs','tools','rust_native_libraries'):
            if any(receipt['freeze'].get(name)!=value for name,value in current[group].items()):
                raise ValueError('guarded incomplete prepared closure')
    freeze()
    receipt['cases']=[];stopped=True
    def save():(output/'results.json').write_text(json.dumps(receipt,indent=2)+'\n')
    try:
        prepare_native_fixture(output);disk=output/'native-namespace.raw'
        pristine=native_media_snapshot(disk);receipt['pristine_media']=pristine;save()
        for role in ('baseline','writer','recovery'):
            freeze()
            before=_native_media_snapshot(disk)
            if role in ('baseline','writer') and before!=pristine:raise ValueError('guarded pristine media changed')
            if role=='recovery' and before!=receipt['cases'][-1]['stopped_media']:raise ValueError('guarded stopped-media mismatch')
            receipt['native_attempted']=True;save()
            text,row=guest(output,role,receipt['emulator'],case)
            after=_native_media_snapshot(disk)
            row['stopped_media']=after
            receipt['cases'].append(row);save()
            if role=='writer':
                row['transcript']=transcript_witness(text);save()
                selected=transcript_text(row['transcript'])
                if row['transcript']['raw_sha256']!=row['serial_sha256']:raise ValueError('guarded transcript/raw association')
                row.update(writer_trace(selected,case,path_probe=receipt.get('path_probe',False),dup2_probe=receipt.get('dup2_wire',False),cwd_probe=receipt.get('cwd_wire',False)))
            else:
                witness=metadata_oracle_witness(text);metadata_oracle_text(witness)
                row['machine_witness']=witness
                row.update(runtime.check_engine_trace(text,'AETHER NATIVE BLOCK PASS'))
                row.update(runtime.check_pool_cleanup_trace(text));row.update(runtime.check_namespace_trace(text))
            if role!='writer' and after!=before:raise ValueError('guarded reader changed media')
            row.update(status='pass',stopped_media=after);save()
        freeze();receipt.update(status='pass',original_file_recovered=True);save()
    except BaseException as error:
        stopped=not isinstance(error,NativeStopError)
        receipt.update(status='failed',error=str(error),human_disposition_required=True,vm_stop_confirmed=stopped)
        raise
    finally:
        for path in output.glob('*-guest.json'):
            row=json.loads(path.read_text())
            if not any(item['role']==row['role'] for item in receipt['cases']):receipt['cases'].append(row)
        if stopped and receipt.get('status')=='failed':
            try:
                disk=output/'native-namespace.raw'
                if disk.exists():receipt['failed_stopped_media']=_native_media_snapshot(disk)
                writer=next((row for row in receipt['cases'] if row['role']=='writer'),None)
                if writer is not None and 'transcript' in writer:
                    receipt['panic_site']=symbolize_panic(output,receipt,writer)
            except (ValueError,OSError,RuntimeError,subprocess.SubprocessError) as error:
                receipt['failure_diagnostic_error']=str(error)
        save()
        if stopped:
            # Compact receipt survives every outcome; generated media/images do
            # not become an evidence archive. Unknown stop retains everything.
            for path in output.iterdir():
                if path.name=='results.json':continue
                if path.is_dir():shutil.rmtree(path)
                else:path.unlink()
        print(json.dumps(dict(status=receipt['status'],report=str(output/'results.json'))))


def prepare(directory,seal,case='exec-wait'):
    script=case_script(case)
    directory=Path(directory).absolute()
    record=intake(directory,seal)
    if record.get('path_probe',False) and case!='exec-wait':
        raise ValueError('guarded read probe requires fixed exec-wait script')
    reader_pins=reader_dependencies()
    from fs_init_checks import build_reader
    from fs_session import FLAGS
    output=Path(tempfile.mkdtemp(prefix=PREFIX,dir=ROOT/'zig-out'))
    receipt=dict(status='preparing',output=str(output),profile=PROFILE,inputs_directory=str(Path(directory).absolute()),
                 inputs_seal=seal,case=case,path_probe=record.get('path_probe',False),dup2_wire=record.get('dup2_wire',False),cwd_wire=record.get('cwd_wire',False),script_hex=script.hex(),native_attempted=False,commands=[],
                 harness_sha256=digest(Path(__file__)))
    def command(args,log,rejection=None):
        path=Path(log)
        if not path.is_absolute():path=output/path
        row=dict(argv=list(map(str,args)),timeout=180,output_limit=4*1024*1024)
        receipt['commands'].append(row)
        try:
            data=run_tool(row['argv'],dict(os.environ),path,timeout=180,cwd=ROOT)
            row['exit_code']=0
        except subprocess.CalledProcessError as error:
            row['exit_code']=error.returncode
            data=path.read_bytes()
            if rejection is None or rejection not in data.decode(errors='replace'):raise
        finally:
            if path.is_file():row.update(log_sha256=digest(path),tail=path.read_text(errors='replace')[-1200:])
        if rejection is not None and row['exit_code']==0:raise ValueError('missing expected build rejection')
        return data.decode()
    try:
        writer=output/'writer';writer.mkdir()
        shutil.copyfile(Path(directory)/'envelope.bin',writer/'envelope.bin')
        flags=[*FLAGS,'native-fs-session-init','native-fs-owner-data','native-fs-owner-stack']
        if record['flags']!=flags:raise ValueError('guarded selected flags')
        command(['zig','build','-p',writer,'--cache-dir',ROOT/'.zig-cache','--global-cache-dir',ROOT/'.zig-cache/global',
            '-Dsmp=false','-Dnative-c-image='+str(writer/'envelope.bin'),*['-D'+f+'=true' for f in flags]],'writer-build.log')
        reader=output/'reader'
        tools={k:dict(path=v['path'],sha256=v['sha256']) for k,v in json.loads((ROOT/'.deps/native-current/sdk/tools.lock.json').read_text())['tools'].items()}
        receipt['reader']=build_reader(reader,command,tools)
        shutil.copyfile(writer/'bin/aether',writer/'kernel.elf')
        receipt['kernel_elf_sha256']=digest(writer/'kernel.elf')
        receipt['artifacts']={name:digest(path) for name,path in [('writer',writer/'aether.iso'),('reader',reader/'aether.iso')]}
        receipt['freeze']={str(Path(directory)/'SHA256SUMS'):seal,str(Path(__file__)):digest(Path(__file__))}
        for group in ('inputs','tools','rust_native_libraries'):receipt['freeze'].update(record[group])
        # Original objects are checked against their immutable manifest; the
        # smaller independent runtime is hashed as one exact named closure.
        if reader_dependencies()!=reader_pins:raise ValueError('guarded reader inputs changed during build')
        receipt['reader_dependencies']=reader_pins
        symbolizer=Path(next(name for name in record['tools'] if Path(name).name=='llvm-objdump')).with_name('llvm-symbolizer')
        version=run_tool([str(symbolizer),'--version'],dict(os.environ),output/'symbolizer-version.log',timeout=10,limit=4096,cwd=ROOT).decode()
        if 'LLVM version 21.1.8' not in version:raise ValueError('guarded symbolizer version')
        receipt['symbolizer']=dict(path=str(symbolizer),sha256=digest(symbolizer),version=version.strip())
        receipt['freeze'][str(symbolizer)]=digest(symbolizer)
        from deps import DEPS
        receipt['emulator']=str(Path(shutil.which('qemu-system-x86_64')).resolve())
        for path in (Path(receipt['emulator']),DEPS/'firmware/code.fd',DEPS/'firmware/vars.fd'):
            receipt['freeze'][str(path)]=digest(path)
        if intake(directory,seal)!=record:raise ValueError('guarded inputs changed during preparation')
        receipt['status']='prepared'
        return output
    except BaseException as error:
        receipt.update(status='failed',error=str(error));raise
    finally:
        # Pending qualification keeps two ISOs and one exact kernel ELF for PC lookup.
        # Neither source copies, SDKs nor build intermediates are test evidence.
        for path in output.iterdir():
            if path.is_dir():
                for child in path.iterdir():
                    if receipt['status']=='prepared' and child.name in ('aether.iso','kernel.elf'):continue
                    if child.is_dir():shutil.rmtree(child)
                    else:child.unlink()
            elif path.name!='results.json':path.unlink()
        (output/'results.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps(dict(status=receipt['status'],report=str(output/'results.json'))))


def main():
    class Parser(argparse.ArgumentParser):
        def error(self,message):
            self.print_usage(sys.stderr);self.exit(64,'af07-owner: '+ascii(message)[1:-1]+'\n')
    parser=Parser(description=__doc__,epilog='Only --run executes guests. Existing bounds and fresh persistence disposition still apply; no retry.')
    parser.add_argument('--version',action='version',version='aether-af07-owner-qualification 1')
    parser.add_argument('--inputs',type=Path)
    parser.add_argument('--seal')
    parser.add_argument('--prepare',action='store_true',help='build both images for the fixed three-guest boot/exec diagnostic')
    parser.add_argument('--case',choices=tuple(SCRIPTS),help='fixed process case, valid only with --prepare (default: exec-wait)')
    parser.add_argument('--prepared',type=Path,help='owned prepared directory for the reviewed diagnostic')
    parser.add_argument('--prepared-sha256',help='reviewed results.json SHA256, mandatory with --run')
    parser.add_argument('--run',action='store_true',help='one pristine/serial-shell/readonly-recovery diagnostic; stop on first failure')
    args=parser.parse_args()
    if args.run:
        if not args.prepared or not args.prepared_sha256 or args.inputs or args.seal or args.prepare or args.case:
            parser.error('--run requires only --prepared and --prepared-sha256')
        execute(args.prepared,args.prepared_sha256)
    else:
        if not args.inputs or not args.seal or args.prepared or args.prepared_sha256:
            parser.error('inspection/preparation requires --inputs and --seal')
        if args.case and not args.prepare:parser.error('--case requires --prepare')
        if args.prepare:
            prepare(args.inputs,args.seal,args.case or 'exec-wait');return
        data=intake(args.inputs,args.seal)
        print(json.dumps(dict(status='pass',profile=data['profile'],native_executed=False)))


if __name__=='__main__':
    try:main()
    except (ValueError,OSError,RuntimeError,subprocess.SubprocessError) as error:
        print('[FAIL] '+ascii(str(error))[1:-1],file=sys.stderr);raise SystemExit(1)
