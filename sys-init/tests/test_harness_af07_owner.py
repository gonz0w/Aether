# SPDX-License-Identifier: BSD-2-Clause
"""Fresh guarded-input consumption, fixed shell outcome and failure oracles."""
import copy
import importlib.util
import itertools
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location('af07_owner',ROOT/'sys-init/scripts/qualify-af07-owner.py')
owner=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(owner)
INPUTS=ROOT/'.deps/fs-owner-af07-2026-10-23-v9'
SEAL='b42605bdfa6496c84d8366a853489c1507d74369f25865192786c4cc31ea5169'


def trace(case='exec-wait'):
    status={'exec-wait':7,'parent-close':7,'exec-missing':127,'exec-denied':126}[case]
    lines=['NATIVE MEMORY admitted slot=0 generation=1 used=1329 remaining=6863','NATIVE MEMORY admitted slot=1 generation=1 used=80 remaining=48','AF07-BEGIN']
    if case in ('exec-wait','parent-close'):lines+=['NATIVE MEMORY admitted slot=2 generation=1 used=33 remaining=95']
    lines+=[f'NATIVE terminal slot=2 generation=1 kind=1 detail={status}']
    for slot,pages,prior in ((2,128,0),(1,128,1),(0,8192,2)):
        if slot==1:
            lines+=[f'AF07-STATUS:{status}']
            if case!='exec-wait':lines+=['AF07-PARENT:ok']
            lines+=['NATIVE terminal slot=1 generation=1 kind=1 detail=0']
        if slot==0:lines+=['NATIVE terminal slot=0 generation=1 kind=1 detail=0']
        lines += [f'NATIVE CLEANUP v=1 slot={slot} generation=1 phase={phase} selected={slot if phase==1 else 6} pages={pages} reclaimed={prior+(phase==7)}' for phase in range(1,8)]
    lines += [f'NATIVE STORAGE WAIT slot={slot} generation={generation} phase={phase} status=0' for slot,generation in ((0,1),(1,1),(2,1),(6,0)) for phase in ('park','wake')]
    lines += ['NATIVE init halted ticks=2400 idle=100 reclaimed=3','AETHER NATIVE BLOCK PASS']
    return '\n'.join(lines)+'\n'


class AF07Owner(unittest.TestCase):
    def test_current_complete_input_chain_and_real_parser(self):
        selected=owner.intake(INPUTS,SEAL)
        self.assertEqual(selected['measurement']['stack']['entry_stack_bytes'],7992)
        self.assertEqual(selected['profile'],owner.PROFILE)
        self.assertEqual(selected['file_wire'],'AEFP0002')
        self.assertTrue(selected['dup2_wire'] and selected['path_probe'])
        self.assertFalse(selected['native_executed'])

    def test_resealed_wrong_profile_closure_bounds_and_raw_correspondence_reject(self):
        with tempfile.TemporaryDirectory(prefix='aether-af07-owner-denials-') as folder:
            root=Path(folder).resolve()/'inputs';shutil.copytree(INPUTS,root)
            original=json.loads((root/'inputs.json').read_text())
            for key,value in [('profile','AENFS004'),('inputs',{}),('native_executed',True),
                ('path_probe',1),('dup2_wire',1),('dup2_wire',False),('file_wire','AEFD0001'),('file_wire','AEFP0001'),('file_wire','other'),
                ('measurement',{**original['measurement'],'code_budget':65536}),
                ('measurement',{**original['measurement'],'stack':{'status':'pass','usable_stack_bytes':65536,'entry_stack_bytes':8000}})]:
                record=copy.deepcopy(original);record[key]=value
                (root/'inputs.json').write_text(json.dumps(record));seal=self.seal(root)
                with self.subTest(key=key),self.assertRaises(ValueError):owner.intake(root,seal)
            (root/'inputs.json').write_text(json.dumps(original));self.seal(root)
            raw=(root/'owner.bin').read_bytes();(root/'owner.bin').write_bytes(raw+b'bad')
            seal=self.seal(root)
            with self.assertRaises(ValueError):owner.intake(root,seal)

    def seal(self,root):
        (root/'SHA256SUMS').write_text(''.join(owner.digest(p)+'  '+p.name+'\n' for p in sorted(root.iterdir()) if p.name!='SHA256SUMS'))
        return owner.digest(root/'SHA256SUMS')

    def test_read_probe_requires_exact_marker_and_order_without_promoting_default(self):
        good=trace().replace('NATIVE terminal slot=2','AF07-READ:ok\nNATIVE terminal slot=2',1)
        self.assertTrue(owner.writer_trace(good,path_probe=True)['persistent_path_read_probe'])
        for raw in (trace(),good+'AF07-READ:ok\n',good.replace('AF07-READ:ok','AF07-READ:no'),
            good.replace('AF07-READ:ok\n','').replace('AF07-BEGIN','AF07-READ:ok\nAF07-BEGIN')):
            with self.subTest(raw=raw),self.assertRaises(ValueError):owner.writer_trace(raw,path_probe=True)
        with self.assertRaises(ValueError):owner.writer_trace(good)
        with self.assertRaises(ValueError):owner.writer_trace(good,case='parent-close',path_probe=True)
        with self.assertRaises(ValueError):owner.writer_trace(good,path_probe=1)

    def test_dup2_probe_requires_bound_path_variant_and_complete_success(self):
        good=trace().replace('NATIVE terminal slot=2','AF07-READ:ok\nNATIVE terminal slot=2',1)
        self.assertTrue(owner.writer_trace(good,path_probe=True,dup2_probe=True)['persistent_dup2_probe'])
        self.assertFalse(owner.writer_trace(good,path_probe=True)['persistent_dup2_probe'])
        for options in [dict(dup2_probe=True),dict(path_probe=True,dup2_probe=1)]:
            with self.subTest(options=options),self.assertRaises(ValueError):owner.writer_trace(good,**options)
        with self.assertRaises(ValueError):owner.writer_trace(trace(),path_probe=True,dup2_probe=True)

    def test_cwd_probe_requires_explicit_matching_read_and_dup2_selection(self):
        good=trace().replace('used=1329 remaining=6863','used=1331 remaining=6861').replace(
            'used=33 remaining=95','used=34 remaining=94').replace('NATIVE terminal slot=2','AF07-READ:ok\nNATIVE terminal slot=2',1)
        self.assertTrue(owner.writer_trace(good,path_probe=True,dup2_probe=True,cwd_probe=True)['persistent_cwd_probe'])
        for options in [dict(cwd_probe=True),dict(path_probe=True,cwd_probe=True),dict(path_probe=True,dup2_probe=True,cwd_probe=1)]:
            with self.subTest(options=options),self.assertRaises(ValueError):owner.writer_trace(good,**options)
        with self.assertRaises(ValueError):owner.writer_trace(trace(),path_probe=True,dup2_probe=True,cwd_probe=True)

    def test_cwd_loader_geometry_is_exact_and_separate_from_af07(self):
        old=trace().replace('NATIVE terminal slot=2','AF07-READ:ok\nNATIVE terminal slot=2',1)
        good=old.replace('used=1329 remaining=6863','used=1331 remaining=6861').replace(
            'used=33 remaining=95','used=34 remaining=94')
        options=dict(path_probe=True,dup2_probe=True,cwd_probe=True)
        with self.assertRaisesRegex(ValueError,'exact loader identities/geometry'):
            owner.writer_trace(old,**options)
        with self.assertRaisesRegex(ValueError,'exact loader identities/geometry'):
            owner.writer_trace(good,path_probe=True,dup2_probe=True)
        for before,after in [('1331 remaining=6861','1330 remaining=6862'),
                ('1331 remaining=6861','1332 remaining=6860'),
                ('34 remaining=94','33 remaining=95'),('34 remaining=94','35 remaining=93'),
                ('remaining=6861','remaining=6862'),('remaining=94','remaining=95'),
                ('admitted slot=0 generation=1','admitted slot=0 generation=2'),
                ('admitted slot=2 generation=1','admitted slot=3 generation=1')]:
            with self.subTest(change=before),self.assertRaisesRegex(ValueError,'exact loader identities/geometry'):
                owner.writer_trace(good.replace(before,after),**options)
        # The selected geometry must not bypass the rest of the strict oracle.
        for line in good.splitlines():
            with self.subTest(removed=line),self.assertRaises(ValueError):
                owner.writer_trace(good.replace(line+'\n','',1),**options)
            with self.subTest(duplicated=line),self.assertRaises(ValueError):
                owner.writer_trace(good+line+'\n',**options)
        for before,after in [('AF07-STATUS:7','AF07-STATUS:0'),('ticks=2400','ticks=6001'),
                ('phase=park status=0','phase=park status=9'),('reclaimed=3','reclaimed=2')]:
            with self.subTest(change=before),self.assertRaises(ValueError):
                owner.writer_trace(good.replace(before,after),**options)
        with self.assertRaisesRegex(ValueError,'ordering'):
            owner.writer_trace(good.replace('AF07-BEGIN','SWAP').replace(
                'NATIVE MEMORY admitted slot=2 generation=1 used=34 remaining=94','AF07-BEGIN').replace(
                'SWAP','NATIVE MEMORY admitted slot=2 generation=1 used=34 remaining=94'),**options)

    def test_exact_output_wait_cleanup_and_halt_required(self):
        good=trace();self.assertTrue(owner.writer_trace(good)['shell_exec_wait'])
        for line in good.splitlines():
            with self.subTest(line=line),self.assertRaises(ValueError):owner.writer_trace(good.replace(line+'\n','',1))
            with self.subTest(duplicate=line),self.assertRaises(ValueError):owner.writer_trace(good+line+'\n')
        for old,new in [('AF07-STATUS:7','AF07-STATUS:0'),('ticks=2400','ticks=6001'),('phase=park status=0','phase=park status=9'),('reclaimed=3','reclaimed=2'),
            ('slot=2 generation=1 kind=1 detail=7','slot=2 generation=2 kind=1 detail=7')]:
            with self.subTest(change=old),self.assertRaises(ValueError):owner.writer_trace(good.replace(old,new))
        with self.assertRaises(ValueError):owner.writer_trace(good+'AETHER PANIC: fail\n')
        for before,after in [('NATIVE terminal slot=2 generation=1 kind=1 detail=7','NATIVE CLEANUP v=1 slot=2 generation=1 phase=1 selected=2 pages=128 reclaimed=0'),('AF07-BEGIN','NATIVE MEMORY admitted slot=2 generation=1 used=33 remaining=95')]:
            with self.assertRaises(ValueError):owner.writer_trace(good.replace(before,'SWAP').replace(after,before).replace('SWAP',after))
        with self.assertRaises(ValueError):owner.writer_trace(good.replace('AF07-BEGIN','NATIVE observation slot=6 generation=0 offset=0 byte=0\nAF07-BEGIN'))

    def test_sequence_stops_before_next_guest_and_removes_owned_outputs(self):
        from contextlib import ExitStack,redirect_stdout
        import io
        from unittest.mock import patch
        import openzfs_namespace,fs_session,service_runtime_smoke
        from native_smoke import NativeStopError
        for case,failed_role in itertools.product(owner.SCRIPTS,('baseline','writer','recovery','unknown-stop','symbolizer-failure',None)):
            with self.subTest(case=case,failed_role=failed_role),tempfile.TemporaryDirectory(prefix=owner.PREFIX,dir=ROOT/'zig-out') as folder:
                work=Path(folder)
                for role in ('writer','reader'):
                    (work/role).mkdir();(work/role/'aether.iso').write_bytes(b'host flow fixture')
                (work/'writer/kernel.elf').write_bytes(b'host flow kernel')
                receipt=dict(kernel_elf_sha256=owner.digest(work/'writer/kernel.elf'),symbolizer=dict(path=str(Path(owner.__file__)),sha256=owner.digest(Path(owner.__file__))),status='prepared',profile=owner.PROFILE,case=case,script_hex=owner.case_script(case).hex(),
                    artifacts={role:owner.digest(work/role/'aether.iso') for role in ('writer','reader')},
                    reader={'read_grant_only':True},harness_sha256=owner.digest(Path(owner.__file__)),
                    inputs_directory='host-flow-only',inputs_seal='unused',freeze={str(Path(owner.__file__)):owner.digest(Path(owner.__file__))},emulator=str(Path(owner.__file__)),reader_dependencies={})
                if case=='exec-wait':receipt.pop('case') # Retained default receipts predate the selector.
                path=work/'results.json';path.write_text(json.dumps(receipt));seal=owner.digest(path)
                called=[]
                def guest(output,role,qemu,selected):
                    self.assertEqual(selected,case)
                    called.append(role)
                    if failed_role=='unknown-stop' and role=='writer':raise NativeStopError('injected unknown stop')
                    if failed_role=='symbolizer-failure' and role=='writer':
                        (work/'writer-guest.json').write_text(json.dumps(dict(role='writer',vm_stop_confirmed=True,transcript=owner.transcript_witness('NATIVE PANIC pc=1\n'))))
                        raise ValueError('injected flow failure')
                    if role==failed_role:raise ValueError('injected flow failure')
                    return trace(case),dict(role=role,vm_stop_confirmed=True,serial_sha256=owner.hashlib.sha256(trace(case).encode()).hexdigest())
                with ExitStack() as stack:
                    stack.enter_context(patch.object(owner,'intake',return_value={group:{} for group in ('inputs','tools','rust_native_libraries')}))
                    stack.enter_context(patch.object(owner,'reader_dependencies',return_value={}))
                    stack.enter_context(patch.object(owner,'guest',side_effect=guest))
                    setup=stack.enter_context(patch.object(openzfs_namespace,'prepare_native_fixture',side_effect=lambda out:(out/'native-namespace.raw').write_bytes(b'host flow media')))
                    for name in ('native_media_snapshot','_native_media_snapshot'):
                        stack.enter_context(patch.object(openzfs_namespace,name,return_value={'sha256':'host fixture'}))
                    stack.enter_context(patch.object(fs_session,'metadata_oracle_witness',return_value={}))
                    stack.enter_context(patch.object(fs_session,'metadata_oracle_text',return_value=''))
                    for name in ('check_engine_trace','check_pool_cleanup_trace','check_namespace_trace'):
                        stack.enter_context(patch.object(service_runtime_smoke,name,return_value={}))
                    with self.assertRaisesRegex(ValueError,'receipt identity'):
                        owner.execute(work,'0'*64)
                    setup.assert_not_called()
                    with redirect_stdout(io.StringIO()):
                        if failed_role:
                            kind=NativeStopError if failed_role=='unknown-stop' else ValueError
                            with self.assertRaises(kind):owner.execute(work,seal)
                        else:owner.execute(work,seal)
                expected=['baseline','writer','recovery']
                if failed_role:expected=expected[:expected.index('writer' if failed_role in ('unknown-stop','symbolizer-failure') else failed_role)+1]
                self.assertEqual(called,expected)
                result=json.loads(path.read_text());self.assertEqual(result['status'],'failed' if failed_role else 'pass')
                self.assertEqual(result.get('original_file_recovered',False),failed_role is None)
                if failed_role=='symbolizer-failure':
                    self.assertIn('failure_diagnostic_error',result);self.assertEqual(result['error'],'injected flow failure')
                if failed_role and failed_role!='unknown-stop':self.assertEqual(result['failed_stopped_media'],{'sha256':'host fixture'})
                if failed_role=='unknown-stop':
                    self.assertFalse(result['vm_stop_confirmed']);self.assertTrue((work/'writer/aether.iso').is_file())
                else:self.assertEqual(list(work.iterdir()),[path])

    def test_fixed_case_oracles_reject_confusion_missing_reordered_and_extra_records(self):
        for case,expected in [('exec-wait',7),('parent-close',7),('exec-missing',127),('exec-denied',126)]:
            good=trace(case);result=owner.writer_trace(good,case)
            self.assertEqual(result['child_status'],expected)
            self.assertEqual(result['exec_replaced'],case in ('exec-wait','parent-close'))
            for line in good.splitlines():
                with self.subTest(case=case,removed=line),self.assertRaises(ValueError):owner.writer_trace(good.replace(line+'\n','',1),case)
                with self.subTest(case=case,duplicate=line),self.assertRaises(ValueError):owner.writer_trace(good+line+'\n',case)
            for other in owner.SCRIPTS:
                if other!=case:
                    with self.subTest(case=case,other=other),self.assertRaises(ValueError):owner.writer_trace(good,other)
            wrong=good.replace(f'AF07-STATUS:{expected}',f'AF07-STATUS:{expected+1}')
            with self.assertRaises(ValueError):owner.writer_trace(wrong,case)
            if case!='exec-wait':
                wrong=good.replace('AF07-PARENT:ok\n','').replace(f'AF07-STATUS:{expected}\n','AF07-PARENT:ok\n'+f'AF07-STATUS:{expected}\n')
                with self.assertRaises(ValueError):owner.writer_trace(wrong,case)

    def test_receipt_case_and_script_mismatch_reject_before_native_effects(self):
        from unittest.mock import patch
        for case in (None,[],{},1,'other','exec-wait','exec-missing','exec-denied','parent-close'):
            with self.subTest(case=case),tempfile.TemporaryDirectory(prefix=owner.PREFIX,dir=ROOT/'zig-out') as folder:
                work=Path(folder);p=work/'results.json'
                p.write_text(json.dumps(dict(status='prepared',profile=owner.PROFILE,case=case,script_hex=b'not a fixed script'.hex())))
                with patch.object(owner,'guest') as launch,patch.object(owner,'intake') as intake:
                    with self.assertRaises(ValueError):owner.execute(work,owner.digest(p))
                    launch.assert_not_called();intake.assert_not_called()
        for case in (None,[],{},1,'other'):
            with self.subTest(case=case),self.assertRaises(ValueError):owner.writer_trace(trace(),case)

    def test_fixed_script_output_records_fit_one_console_transfer(self):
        import re
        for case,status in [('exec-wait',7),('parent-close',7),('exec-missing',127),('exec-denied',126)]:
            formats=re.findall(rb"printf '([^']*)'",owner.case_script(case))
            records=[value.replace(b'%s',str(status).encode()).replace(b'\\n',b'\n') for value in formats]
            expected=[b'AF07-BEGIN\n',b'AF07-STATUS:'+str(status).encode()+b'\n']
            if case!='exec-wait':expected.append(b'AF07-PARENT:ok\n')
            self.assertEqual(records,expected)
            for record in records:
                with self.subTest(case=case,record=record):self.assertLessEqual(len(record),16)
        self.assertGreater(len(b'AF07-PARENT:alive\n'),16)

    def test_real_split_parent_marker_failure_remains_failed(self):
        attempt=json.loads((ROOT/'docs/evidence/af07-process-cases-2026-10-23/attempt1.json').read_text())
        text=owner.transcript_text(attempt['writer']['transcript'])
        self.assertEqual(attempt['writer']['transcript']['raw_sha256'],attempt['writer']['serial_sha256'])
        self.assertIn('AF07-STATUS:127\n',text)
        self.assertIn('AF07-PARENT:aliv\nNATIVE STORAGE WAIT ',text)
        self.assertNotIn('AF07-PARENT:alive\n',text)
        with self.assertRaisesRegex(ValueError,'actual shell/exec/wait output'):owner.writer_trace(text,'exec-missing')
        self.assertFalse(attempt['recovery_started']);self.assertFalse(attempt['acceptance'])

    def test_serial_fragments_fault_eof_and_watchdog_reap_real_host_child(self):
        from contextlib import ExitStack
        import subprocess,sys,time
        from unittest.mock import patch
        import deps
        real_popen=subprocess.Popen;clock=time.monotonic
        scripts={
            'serial':"import sys\nprint('NATIVE MEMORY admitted slot=1 generation=1 used=80 remaining=48',flush=True)\nsys.stdin.buffer.read("+str(len(owner.SCRIPT))+")\nprint('AETHER NATIVE BLOCK PASS',flush=True)\n",
            'panic':"print('AETHER PANIC: host fixture',flush=True)",
            'eof':"print('host premature EOF',flush=True)",
            'timeout':"import time;time.sleep(10)",
        }
        trials=[('exec-wait',mode,source) for mode,source in scripts.items()]
        trials += [(case,'serial',scripts['serial'].replace(str(len(owner.SCRIPT)),str(len(script))))
                   for case,script in owner.SCRIPTS.items() if case!='exec-wait']
        for case,mode,source in trials:
            with self.subTest(mode=mode),tempfile.TemporaryDirectory(prefix='aether-af07-host-child-') as folder:
                work=Path(folder);(work/'writer').mkdir();child_script=work/'child.py';child_script.write_text(source)
                children=[]
                def launch(*args,**kwargs):
                    child=real_popen([sys.executable,'-B',str(child_script)],**kwargs);children.append(child);return child
                calls=0
                def fast_clock():
                    nonlocal calls
                    calls+=1;return clock()+calls*35
                with ExitStack() as stack:
                    stack.enter_context(patch.object(deps,'verify'))
                    stack.enter_context(patch.object(owner.subprocess,'check_output',return_value='QEMU emulator version '+deps.LOCK['qemu']+'\n'))
                    stack.enter_context(patch.object(owner.subprocess,'Popen',side_effect=launch))
                    if mode=='timeout':stack.enter_context(patch.object(owner.time,'monotonic',side_effect=fast_clock))
                    if mode=='serial':
                        text,row=owner.guest(work,'writer','host-fixture-qemu',case);self.assertIn('AETHER NATIVE BLOCK PASS',text)
                        chunks=row['input_writes'];self.assertTrue(all(0<r['accepted']<=7 for r in chunks))
                        self.assertEqual(b''.join(bytes.fromhex(r['requested_hex'])[:r['accepted']] for r in chunks),owner.case_script(case))
                    else:
                        with self.assertRaises((ValueError,TimeoutError)):owner.guest(work,'writer','host-fixture-qemu')
                self.assertEqual(len(children),1);self.assertIsNotNone(children[0].poll())
                row=json.loads((work/'writer-guest.json').read_text());self.assertTrue(row['vm_stop_confirmed'])
                captured=owner.transcript_text(row['transcript']);self.assertEqual(row['transcript']['raw_sha256'],row['serial_sha256'])
                if mode=='panic':self.assertIn('AETHER PANIC: host fixture',captured)
                if mode=='eof':self.assertIn('host premature EOF',captured)

    def test_cli_help_version_and_invalid_selections_do_not_prepare(self):
        import subprocess,sys
        for args,status in [(['--help'],0),(['--version'],0),([],64),(['--run'],64),
            (['--inputs','bad','--seal','bad','--run'],64),
            (['--inputs','bad','--seal','bad','--case','exec-missing'],64),
            (['--inputs','bad','--seal','bad','--prepare','--case','other'],64),
            (['--run','--prepared','bad','--prepared-sha256','bad','--case','exec-missing'],64)]:
            with self.subTest(args=args):
                run=subprocess.run([sys.executable,'-B',owner.__file__,*args],capture_output=True,timeout=10)
                self.assertEqual(run.returncode,status)
                self.assertNotIn(b'"status": "prepared"',run.stdout)
                if args==['--help']:self.assertIn(b'Only --run executes guests',run.stdout)

    def test_transcript_preserves_stdout_prompts_unknowns_and_partial_records(self):
        clocks='NATIVE CLOCK park task=1 start=2 deadline=3\nNATIVE CLOCK timeout task=1 now=3 elapsed=1\n'
        content='boot\r\n# NATIVE STORAGE WAIT slot=1 generation=1 phase=wake status=0\nAF07-BEGIN\nNATIVE CLOCK unknown x=1\nNATIVE CLOCK park task=١ start=2 deadline=3\npartial'
        text=clocks+content;row=owner.transcript_witness(text)
        self.assertEqual(owner.transcript_text(row),content)
        self.assertEqual(row['raw_sha256'],owner.hashlib.sha256(text.encode()).hexdigest())
        self.assertEqual(row['clocks'],dict(lines=2,sha256=owner.hashlib.sha256(clocks.encode()).hexdigest()))
        self.assertEqual(owner.transcript_text(owner.transcript_witness('é'*32768)),'é'*32768)
        with self.assertRaises(ValueError):owner.transcript_text(owner.transcript_witness('é'*32769))
        for key,value in [('complete',False),('text',content+'bad'),('retained_utf8_bytes',0),('raw_sha256','bad'),
            ('retained_sha256','0'*64),('source_lines',True),('source_lines',999),('retained_lines',999),
            ('ceiling_utf8_bytes',131072),('extra','bad'),('clocks',dict(lines=0,sha256='0'*64))]:
            bad=copy.deepcopy(row);bad[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):owner.transcript_text(bad)
        partial='NATIVE CLOCK park task=1 start=2 deadline=3'
        self.assertEqual(owner.transcript_text(owner.transcript_witness(partial)),partial)

    def test_process_wait_identity_is_exact_and_prior_unpaired_capture_still_rejects(self):
        good=trace();self.assertTrue(owner.writer_trace(good)['shell_exec_wait'])
        for old,new in [('slot=1 generation=1 phase=park','slot=3 generation=1 phase=park'),
            ('slot=2 generation=1 phase=wake','slot=2 generation=2 phase=wake'),
            ('slot=1 generation=1 phase=park','slot=1 generation=1 phase=wake')]:
            with self.subTest(change=new),self.assertRaises(ValueError):owner.writer_trace(good.replace(old,new))
        from fs_session import metadata_oracle_text
        attempt=json.loads((ROOT/'docs/evidence/af07-owner-native-2026-10-23/attempt1.json').read_text())
        selected=metadata_oracle_text(attempt['cases'][1]['machine_witness'])
        # Synthetic insertion restores markers absent from the old witness only
        # to reach strict wait validation. This is never native acceptance.
        selected=selected.replace('NATIVE MEMORY admitted slot=2','AF07-BEGIN\nNATIVE MEMORY admitted slot=2',1)
        selected=selected.replace('NATIVE terminal slot=1','AF07-STATUS:7\nNATIVE terminal slot=1',1)
        with self.assertRaisesRegex(ValueError,'duplicate park'):owner.writer_trace(selected)

    def test_full_native_capture_accounts_for_all_eight_prefixed_wakes(self):
        attempt=json.loads((ROOT/'docs/evidence/af07-owner-native-2026-10-23/attempt2.json').read_text())
        row=attempt['cases'][1];text=owner.transcript_text(row['transcript'])
        self.assertEqual(row['transcript']['raw_sha256'],row['serial_sha256'])
        with self.assertRaisesRegex(ValueError,'duplicate park'):owner.writer_trace(text)
        import re
        prefixed=[match.groups() for match in re.finditer(r'(?m)^(.+)(NATIVE STORAGE WAIT slot=1 generation=1 phase=wake status=0)$',text)]
        self.assertEqual([prefix for prefix,_ in prefixed],['sh: 0: ','getcwd() failed:',' Function not im','plemented','$ ','$ ','$ ','$ '])
        # Diagnostic projection of the new producer's unconditional line break.
        # The production oracle never promotes a user-output suffix to a record.
        projected=text.replace('NATIVE STORAGE WAIT ','\nNATIVE STORAGE WAIT ')
        result=owner.writer_trace(projected)
        self.assertEqual(result['primary_channel_waits'],220)
        self.assertEqual(result['primary_channel_wakes'],220)
        self.assertFalse(attempt['acceptance']);self.assertFalse(attempt['recovery_started'])

    def test_panic_symbolization_exact_elf_and_pc_denials(self):
        import struct,subprocess,sys
        with tempfile.TemporaryDirectory(prefix='aether-af07-symbols-') as folder:
            work=Path(folder);(work/'writer').mkdir();source=work/'site.zig'
            source.write_text('export fn entry() noreturn { while(true) asm volatile ("nop"); }\n')
            kernel=work/'writer/kernel.elf'
            subprocess.run(['zig','build-exe','-target','x86_64-freestanding-none','-ODebug','-fno-strip','-fentry=entry',
                str(source),'-femit-bin='+str(kernel),'--cache-dir',str(work/'cache'),'--global-cache-dir',str(work/'global')],
                check=True,capture_output=True,timeout=60)
            pc=struct.unpack_from('<Q',kernel.read_bytes(),24)[0]+1
            tool=Path('/opt/homebrew/Cellar/llvm@21/21.1.8/bin/llvm-symbolizer')
            receipt=dict(kernel_elf_sha256=owner.digest(kernel),symbolizer=dict(path=str(tool),sha256=owner.digest(tool)))
            def row(text):return dict(transcript=owner.transcript_witness(text))
            result=owner.symbolize_panic(work,receipt,row(f'NATIVE PANIC pc={pc:x}\nAETHER PANIC: host fixture\n'))
            self.assertIn(result['status'],('symbolized','symbolized-with-warnings'));self.assertIn('site.zig',result['output'])
            self.assertEqual(result['call_site'],hex(pc-1))
            self.assertEqual(owner.symbolize_panic(work,receipt,row('AETHER PANIC: no site\n'))['status'],'missing-site')
            for text in ('NATIVE PANIC pc=bad!\n','NATIVE PANIC pc=0\n','NATIVE PANIC pc=ffffffffffffffff\n',
                f'NATIVE PANIC pc={pc:x}\nNATIVE PANIC pc={pc:x}\n'):
                with self.subTest(text=text),self.assertRaises(ValueError):owner.symbolize_panic(work,receipt,row(text))
            for change in ('elf','tool'):
                bad=copy.deepcopy(receipt)
                if change=='elf':bad['kernel_elf_sha256']='0'*64
                else:bad['symbolizer']['sha256']='0'*64
                with self.subTest(change=change),self.assertRaises(ValueError):owner.symbolize_panic(work,bad,row(f'NATIVE PANIC pc={pc:x}\n'))

    def test_unconfirmed_stop_is_preserved_even_if_report_write_fails(self):
        from contextlib import ExitStack
        from unittest.mock import patch
        import deps,os,subprocess
        from native_smoke import NativeStopError
        for fail_report in (False,True):
            with self.subTest(fail_report=fail_report),tempfile.TemporaryDirectory(prefix='aether-af07-stop-report-') as folder:
                work=Path(folder);(work/'writer').mkdir()
                streams=[]
                def pipe(data):
                    reader,writer=os.pipe();os.write(writer,data);os.close(writer)
                    stream=os.fdopen(reader,'rb');streams.append(stream);return stream
                reader,writer=os.pipe();os.close(reader);stdin=os.fdopen(writer,'wb');streams.append(stdin)
                class Child:
                    pid=123456789
                    def poll(self):return None
                    def wait(self,timeout):raise subprocess.TimeoutExpired('host unconfirmed-stop fixture',timeout)
                child=Child();child.stdin=stdin;child.stdout=pipe(b'AETHER PANIC: stop fixture\n');child.stderr=pipe(b'')
                try:
                    with ExitStack() as stack:
                        stack.enter_context(patch.object(deps,'verify'))
                        stack.enter_context(patch.object(owner.subprocess,'check_output',return_value='QEMU emulator version '+deps.LOCK['qemu']+'\n'))
                        stack.enter_context(patch.object(owner.subprocess,'Popen',return_value=child))
                        signals=stack.enter_context(patch.object(owner.os,'killpg'))
                        if fail_report:stack.enter_context(patch.object(Path,'write_text',side_effect=OSError('host report write failure')))
                        with self.assertRaises(NativeStopError):owner.guest(work,'writer','host fixture')
                        self.assertEqual(signals.call_count,2)
                    if not fail_report:
                        record=json.loads((work/'writer-guest.json').read_text());self.assertFalse(record['vm_stop_confirmed'])
                        self.assertIn('AETHER PANIC: stop fixture',owner.transcript_text(record['transcript']))
                finally:
                    for stream in streams:stream.close()
