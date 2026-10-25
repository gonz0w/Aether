# SPDX-License-Identifier: BSD-2-Clause
"""AF09 guarded dependency denials; synthetic bytes are parser inputs only."""
from contextlib import ExitStack
import copy
import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import fs_home_inputs as home


def record():
    return dict(format=home.SCHEMA, status='prepared', native_executed=False,
        profile=dict(home.PROFILE), bounds=dict(home.BOUNDS), engine={'directory':'.deps/fs-launch-af09-test',
        'seal':'1'*64,'elf_sha256':'2'*64}, producer_receipt={'path':'/receipt/producer','sha256':'3'*64},
        owner_receipt={'path':'/receipt/owner','sha256':'4'*64}, owner_reuse={'scope':'historical host coverage with explicit input impact'},
        measurement={'code_budget':49152,'code_bytes':47384,'code_fits':True,'resident_fits':True,
        'mapped_bytes':8192,'workspace_bytes':4096,'runtime_bytes':3688,'alignment':8,'native_executed':False,'stack':{'status':'pass','usable_stack_bytes':8184,'entry_stack_bytes':8160}},
        admission={'engine_pages':1400,'shell_pages':35,'helper_pages':30,'owner_bytes':47384},
        artifacts={n:{'sha256':'5'*64,'bytes':100} for n in home.ARTIFACTS},
        inputs={'/source':'6'*64}, tools={'zig':{'path':'/tool/zig','sha256':'7'*64}},
        commands=[{'status':'pass','process':{'complete':True,'cleanup':'complete','exit':0}}],
        kernel_build={'sha256':'8'*64,'native_executed':False,'flags':home.kernel_flags()}, final_input_verification='pass')


class GuardedHomeInputs(unittest.TestCase):
    def test_fixed_selection_bounds_and_actual_geometry(self):
        home.validate_record(record())
        for group in ('profile','bounds'):
            for key,value in record()[group].items():
                bad=record();bad[group][key]=not value if type(value) is bool else str(value)+'x'
                with self.subTest(group=group,key=key),self.assertRaises(ValueError):home.validate_record(bad)
        for key,value in [('engine_pages',1329),('engine_pages',1331),('shell_pages',33),('helper_pages',34)]:
            measured=record();measured['admission'][key]=value
            home.validate_record(measured)  # A coincident page count does not select an old profile.
            measured['format']='aether-guarded-af07-inputs-v1'
            with self.assertRaises(ValueError):home.validate_record(measured)
        for key,value in [('engine_pages',2049),('shell_pages',129),('helper_pages',129)]:
            bad=record();bad['admission'][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):home.validate_record(bad)

    def test_exact_record_fields_and_failed_processes(self):
        row=record()
        for key in row:
            bad=record();del bad[key]
            with self.subTest(missing=key),self.assertRaises(ValueError):home.validate_record(bad)
        for key,value in [('extra',1),('native_executed',True),('native_executed',0),('status','pass')]:
            bad=record();bad[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):home.validate_record(bad)
        for flags in ([],home.kernel_flags()[:-1],[*home.kernel_flags(),'native-fs-owner-data']):
            bad=record();bad['kernel_build']['flags']=flags
            with self.assertRaises(ValueError):home.validate_record(bad)
        bad=record();bad['kernel_build']['extra']=1
        with self.assertRaises(ValueError):home.validate_record(bad)
        for path,value in [('complete',False),('cleanup','failed'),('exit',1)]:
            bad=record();bad['commands'][0]['process'][path]=value
            with self.subTest(path=path),self.assertRaises(ValueError):home.validate_record(bad)

    def test_envelope_exact_bytes_and_no_old_wire(self):
        raw=home.envelope(b'engine',b'shell',b'helper',b'owner')
        self.assertEqual(raw[:8],b'AENFS005');self.assertEqual(raw[54:62],b'AENMX010')
        self.assertEqual(struct.unpack_from('<II',raw,8),(6,112+10+6+5))
        self.assertEqual(raw[54+112:],b'shellshellhelperowner')
        for args in [(b'',b's',b'h',b'o'),(b'e',b'',b'h',b'o'),(b'e',b's',b'h',b'o'*49153)]:
            with self.assertRaises(ValueError):home.envelope(*args)

    def test_member_closure_rejects_extra_missing_duplicate_escape_and_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'inputs.json').write_text('{}')
            for n in home.ARTIFACTS:(root/n).write_bytes(b'x')
            seal=lambda: (root/'SHA256SUMS').write_text(''.join(home.digest(root/n)+'  '+n+'\n' for n in sorted((*home.ARTIFACTS,'inputs.json'))))
            seal();home.checked_members(root,home.digest(root/'SHA256SUMS'))
            (root/'extra').write_bytes(b'x')
            with self.assertRaises(ValueError):home.checked_members(root,home.digest(root/'SHA256SUMS'))
            (root/'extra').unlink();(root/'owner.bin').unlink()
            with self.assertRaises(ValueError):home.checked_members(root,home.digest(root/'SHA256SUMS'))
            (root/'owner.bin').symlink_to(root/'owner.elf')
            with self.assertRaises(ValueError):home.checked_members(root,home.digest(root/'SHA256SUMS'))
            (root/'owner.bin').unlink();(root/'owner.bin').write_bytes(b'x');seal()
            for suffix in ['0'*64+'  ../escape\n','0'*64+'  inputs.json\n']:
                seal();p=root/'SHA256SUMS';p.write_text(p.read_text()+suffix)
                with self.assertRaises(ValueError):home.checked_members(root,home.digest(p))

    def test_duplicate_json_and_missing_source_never_admitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'data';p.write_text('{"a":1,"a":2}')
            with self.assertRaises(ValueError):home.read_json(p)
            with self.assertRaises(ValueError):home.verify_map({str(p.parent/'missing'):'1'*64},{})
            p.write_bytes(b'actual');home.verify_map({str(p):home.digest(p)},{})
            with self.assertRaises(ValueError):home.verify_map({str(p):'1'*64},{})

    def test_owned_cleanup_preserves_foreign_path_and_records_deletion_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'owned';path.mkdir();identity=home.directory_identity(path)
            errors=[]
            with patch.object(home.shutil,'rmtree',side_effect=OSError('deletion denied')):
                home.remove_owned(path,identity,errors,'work')
            self.assertTrue(path.is_dir());self.assertEqual(len(errors),1)
            self.assertIn('deletion denied',errors[0]['error'])
            errors=[];home.remove_owned(path,[identity[0],identity[1]+1],errors,'destination')
            self.assertTrue(path.is_dir());self.assertEqual(len(errors),1)
            errors=[];home.remove_owned(path,identity,errors,'work')
            self.assertFalse(path.exists());self.assertEqual(errors,[])
            detail={'status':'pass'};receipt=Path(tmp)/'attempt.json'
            errors=[{'label':'work','error':'deletion denied'}]
            with self.assertRaises(RuntimeError):home.finish_attempt(detail,receipt,errors,None)
            self.assertEqual(json.loads(receipt.read_text())['cleanup'],'failed')
            original=ValueError('original failure')
            home.finish_attempt({'status':'failed'},receipt,errors,original)
            self.assertTrue(original.__notes__)

    def test_standalone_intake_rejects_an_engine_from_another_producer(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);row=record()
            for name in home.ARTIFACTS:(root/name).write_bytes(b'x'*100)
            for name in home.ARTIFACTS:row['artifacts'][name]['sha256']=home.digest(root/name)
            producer=root/'producer.json';producer.write_text('{}')
            row['producer_receipt']['path']=str(producer);row['producer_receipt']['sha256']=home.digest(producer)
            (root/'inputs.json').write_text(json.dumps(row))
            real_read=home.read_json
            def read(path):
                if Path(path).name=='build.json':return dict(qualification_sha256='f'*64)
                return real_read(path)
            with patch.object(home,'checked_members',return_value={n:row['artifacts'][n]['sha256'] for n in home.ARTIFACTS}), \
                 patch.object(home,'read_json',side_effect=read), \
                 patch.object(home.launch,'intake',return_value=dict(elf_sha256='2'*64)), \
                 patch.object(home,'checked_producer',side_effect=RuntimeError('PAST_ASSOCIATION')) as later:
                with self.assertRaisesRegex(ValueError,'engine.*producer'):
                    home.intake(root,'0'*64)
                later.assert_not_called()

    def test_kernel_named_tools_are_fixed_and_rust_environment_is_private(self):
        with tempfile.TemporaryDirectory() as tmp:
            work=Path(tmp)
            tools=json.loads((ROOT/'.deps/native-current/sdk/tools.lock.json').read_text())['tools']
            tools.update(json.loads((ROOT/'userland/docs/evidence/filesystem-transport-2026-10-19/inputs.json').read_text())['tools'])
            report=dict(inputs={},commands=[])
            def query(label,args):
                return {'kernel-python-version':'Python 3.14.7\n',
                        'kernel-rust-version':'rustc 1.98.0 (test)\n',
                        'kernel-xorriso-version':'xorriso version   :  1.5.8.pl02\n'}[label]
            routing=home.kernel_environment(work,tools,report,query)
            self.assertNotIn('DYLD_LIBRARY_PATH',routing['environment'])
            self.assertEqual(routing['environment']['PATH'],str(work/'tool-bin')+':/usr/bin:/bin')
            body=Path(routing['rust_wrapper']['path']).read_text()
            self.assertIn('+1.98.0',body)
            self.assertIn('DYLD_LIBRARY_PATH=',body)
            self.assertEqual(home.digest(routing['rust_wrapper']['path']),routing['rust_wrapper']['sha256'])
            self.assertEqual(tools['qemu']['sha256'],home.digest(tools['qemu']['path']))
            home.verify_kernel_environment(routing)
            Path(routing['rust_wrapper']['path']).write_text(body+'# tampered\n')
            with self.assertRaises(ValueError):home.verify_kernel_environment(routing)

    def test_historical_owner_generated_closure_is_exact_and_current(self):
        report=home.read_json(ROOT/'sys-init/docs/evidence/home-owner-fit-2026-10-24/attempt-23.json')
        generated=home.owner_generated(report)
        self.assertEqual(len(generated),47)
        self.assertTrue(all(report['sources'][name]==sha for name,sha in generated.items()))
        bad=copy.deepcopy(report);bad['sources'][str(Path(report['work'])/'arbitrary.c')]='1'*64
        with self.assertRaises(ValueError):home.owner_generated(bad)
        bad=copy.deepcopy(report);name=next(iter(generated));bad['sources'][name]='1'*64
        with self.assertRaises(ValueError):home.owner_generated(bad)


class GuardedCleanup(unittest.TestCase):
    def test_build_retains_direct_imported_and_unknown_stop_outcomes(self):
        for mode in ('rows', 'commands', 'direct', 'raises'):
            for cleanup in ('unresolved', 'not-started'):
                with self.subTest(mode=mode, cleanup=cleanup):
                    self.model_build(mode, cleanup, True)

    def test_build_confirmed_stop_preserves_normal_failure_cleanup(self):
        self.model_build('rows', 'complete', False)
        self.model_build('direct', 'complete', False)

    def model_build(self, mode, cleanup, retained):
        with tempfile.TemporaryDirectory(prefix='af09-input-cleanup-model-') as folder:
            root=Path(folder); destination=root/'destination'; state={}
            primary=ValueError('original modeled guarded rejection')
            def run(*args, **kwargs):
                if mode=='raises':raise primary
                return SimpleNamespace(returncode=1,stdout=b'',stderr=b'modeled rejection',
                    record=dict(exit=1,complete=False,cleanup=cleanup))
            proc=SimpleNamespace(clean_env=lambda work:{},run=run)
            def build(destination_arg, *args):
                detail=args[-2]; work=root/'work';work.mkdir();destination.mkdir()
                state.update(detail=detail,work=work)
                detail.update(work=str(work),work_identity=home.directory_identity(work),
                    destination=str(destination),destination_created=True,
                    destination_identity=home.directory_identity(destination),rows=[],commands=[])
                (destination/'potentially-live-output').write_bytes(b'owned model')
                if mode in ('rows','commands'):
                    detail[mode].append(dict(process=dict(exit=1,complete=False,cleanup=cleanup)))
                    raise primary
                command=home.command_runner(work,proc,{},home.time.monotonic()+30,detail)
                command('modeled', ['/modeled/tool'])
            with patch.object(home,'ROOT',root),patch.object(home,'_build',side_effect=build):
                with self.assertRaises((ValueError,RuntimeError)) as caught:
                    home.build(destination,root/'engine','1'*64,root/'producer',root/'owner')
            if mode in ('rows','commands','raises'):self.assertIs(caught.exception,primary)
            self.assertEqual(state['work'].exists(),retained)
            self.assertEqual(destination.exists(),retained)
            if retained:
                detail=state['detail'];self.assertEqual(detail['cleanup'],'unresolved')
                self.assertEqual(detail['status'],'failed')
                self.assertIn(str(state['work']),detail['retained_paths'])
                self.assertIn(str(destination),detail['retained_paths'])
            else:self.assertEqual(state['detail']['cleanup'],'complete')

    def test_actual_guarded_build_tracks_imported_runner_before_row_return(self):
        with tempfile.TemporaryDirectory(prefix='af09-imported-cleanup-model-') as folder:
            root=Path(folder);(root/'userland/build').mkdir(parents=True)
            destination=root/'destination';engine=root/'engine';engine.mkdir()
            primary=KeyboardInterrupt('modeled interruption before child record return')
            proc=SimpleNamespace(clean_env=lambda work:{},run=lambda *args,**kwargs: (_ for _ in ()).throw(primary))
            tools={'zig':dict(path='/modeled/zig',sha256='1'*64)}
            def imported(system,work,runner,tools,deadline,detail):
                (destination/'potentially-live-output').write_bytes(b'owned model')
                runner.run(['/modeled/tool'])
            with ExitStack() as stack:
                stack.enter_context(patch.object(home,'ROOT',root))
                for name,kwargs in {
                    'output_path':dict(return_value=destination),
                    'checked_producer':dict(return_value=({'tools':tools},{})),
                    'owner_receipt':dict(return_value=({}, {},{})),
                    'read_json':dict(return_value=dict(qualification_sha256='1'*64,inputs={},tools=tools)),
                    'digest':dict(return_value='1'*64),'required_sources':dict(return_value=[]),
                    'verify_map':dict(),'owned_runner':dict(return_value=proc),
                }.items():stack.enter_context(patch.object(home,name,**kwargs))
                stack.enter_context(patch.object(home.launch,'intake',return_value={}))
                stack.enter_context(patch.object(home.launch,'closure',return_value=(engine,{})))
                stack.enter_context(patch.object(home.runpy,'run_path',return_value={'build':imported}))
                with self.assertRaises(KeyboardInterrupt) as caught:
                    home.build(destination,engine,'1'*64,root/'producer',root/'owner')
            self.assertIs(caught.exception,primary)
            self.assertTrue(destination.is_dir())
            self.assertTrue(list((root/'userland/build').glob('fs-home-inputs-*')))
            receipt=next((root/'userland/docs/evidence/filesystem-home-prep-2026-10-24/guarded-inputs/build').glob('attempt-*.json'))
            detail=json.loads(receipt.read_text())
            self.assertEqual(detail['cleanup'],'unresolved')
            self.assertFalse(detail['rows'])
            self.assertFalse((destination/'inputs.json').exists())

    def test_standalone_intake_and_nested_build_preserve_unknown_stop(self):
        for cleanup in ('unresolved','not-started','raises','complete'):
            for nested in (False,True):
                with self.subTest(cleanup=cleanup,nested=nested):self.model_intake(cleanup,nested)

    def model_intake(self, cleanup, nested):
        with tempfile.TemporaryDirectory(prefix='af09-intake-cleanup-model-') as folder:
            root=Path(folder);(root/'userland/build').mkdir(parents=True)
            candidate=root/'candidate';candidate.mkdir();row=record()
            row['owner_receipt']['sha256']='3'*64
            for name in home.ARTIFACTS:(candidate/name).write_bytes(b'x'*100)
            for name in home.ARTIFACTS:row['artifacts'][name]['sha256']=home.digest(candidate/name)
            (candidate/'inputs.json').write_text(json.dumps(row))
            primary=ValueError('modeled run raised before returning a record')
            state={};real_read=home.read_json
            def read(path):
                if Path(path).name=='build.json':return dict(qualification_sha256='3'*64)
                return real_read(path)
            def run(*args,**kwargs):
                if cleanup=='raises':raise primary
                return SimpleNamespace(returncode=1,stdout=b'',stderr=b'modeled rejection',
                    record=dict(exit=1,complete=False,cleanup=cleanup))
            proc=SimpleNamespace(clean_env=lambda work:{},run=run)
            def owner_pair(directory, measurement, command, tools):
                command('modeled', ['/modeled/tool'])
            def nested_build(destination,*args):
                detail=args[-2];work=root/'outer-work';work.mkdir()
                detail.update(work=str(work),work_identity=home.directory_identity(work),
                    destination=str(candidate),destination_created=True,
                    destination_identity=home.directory_identity(candidate))
                state['detail']=detail
                return home.intake(candidate,'0'*64)
            with ExitStack() as stack:
                stack.enter_context(patch.object(home,'ROOT',root))
                for name,kwargs in {
                    'checked_members':dict(return_value={n:row['artifacts'][n]['sha256'] for n in home.ARTIFACTS}),
                    'read_json':dict(side_effect=read),'digest':dict(return_value='3'*64),
                    'checked_producer':dict(return_value=({},{})),
                    'owner_receipt':dict(return_value=({}, {},row['owner_reuse'])),
                    'required_sources':dict(return_value=[]),'verify_map':dict(),
                    'routing_receipt':dict(),'envelope':dict(return_value=b'x'*100),
                    'owned_runner':dict(return_value=proc),'owner_pair':dict(side_effect=owner_pair),
                }.items():stack.enter_context(patch.object(home,name,**kwargs))
                stack.enter_context(patch.object(home.launch,'intake',return_value=dict(elf_sha256='2'*64,elf=str(candidate/'owner.elf'))))
                if nested:stack.enter_context(patch.object(home,'_build',side_effect=nested_build))
                with self.assertRaises((ValueError,RuntimeError)) as caught:
                    if nested:home.build(candidate,root/'engine','0'*64,root/'producer',root/'owner')
                    else:home.intake(candidate,'0'*64)
            if cleanup=='raises':self.assertIs(caught.exception,primary)
            receipt=next((root/'userland/docs/evidence/filesystem-home-prep-2026-10-24/guarded-inputs/intake').glob('attempt-*.json'))
            detail=json.loads(receipt.read_text());retained=cleanup!='complete'
            workdirs=list((root/'userland/build').glob('fs-home-intake-*'))
            self.assertEqual(bool(workdirs),retained)
            self.assertEqual(detail['cleanup'],'unresolved' if retained else 'complete')
            self.assertEqual(candidate.exists(),True if not nested else retained)
            if retained:
                self.assertIn(str(workdirs[0]),detail['retained_paths'])
                self.assertIn(str(candidate),detail['retained_paths'])
                if nested:
                    self.assertTrue((root/'outer-work').is_dir())
                    self.assertIn(str(workdirs[0]),state['detail']['retained_paths'])
                    self.assertEqual(state['detail']['cleanup'],'unresolved')

if __name__=='__main__':unittest.main()
