# SPDX-License-Identifier: BSD-2-Clause
"""AF09 guarded dependency denials; synthetic bytes are parser inputs only."""
from contextlib import ExitStack
import copy
import hashlib
import json
import os
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
        for work in ('/foreign/userland/build/'+Path(report['work']).name,
                     str(Path(report['work']).parent/'..'/'build'/Path(report['work']).name)):
            bad=copy.deepcopy(report);bad['work']=work
            with self.assertRaisesRegex(ValueError,'historical work identity'):home.owner_generated(bad)
        bad=copy.deepcopy(report);current=ROOT/'sys-init/scripts/owner_compare.py'
        original=next(name for name in report['sources'] if name.endswith('/sys-init/scripts/owner_compare.py'))
        bad['sources'][str(current)]=bad['sources'][original]
        if str(current)!=original:
            with self.assertRaisesRegex(ValueError,'historical recipe changed'):home.owner_generated(bad)
        bad=copy.deepcopy(report);bad['sources'][str(Path(report['work'])/'arbitrary.c')]='1'*64
        with self.assertRaises(ValueError):home.owner_generated(bad)
        bad=copy.deepcopy(report);name=next(iter(generated));bad['sources'][name]='1'*64
        with self.assertRaises(ValueError):home.owner_generated(bad)



def owner_component_fixture():
    """Bind explicitly selected test data; full qualification stays in reader."""
    path = os.environ.get('AETHER_AF09_OWNER_COMPONENT_PROOF')
    digest = os.environ.get('AETHER_AF09_OWNER_COMPONENT_PROOF_SHA256')
    home.component_require(bool(path) and bool(digest),
                           'fixture requires paired proof environment')
    selected = home.component_selector({'path': path, 'sha256': digest})
    proof = home.read_json(selected['path'])
    home.component_require(
        isinstance(proof, dict) and
        set(proof) == {'format', 'receipt', 'role_metadata'} and
        proof['format'] == home.COMPONENT_SELECTION and
        isinstance(proof['role_metadata'], dict), 'fixture wrapper format')
    receipt = proof['receipt']
    home.component_require(
        isinstance(receipt, dict) and set(receipt) == {'path', 'sha256'} and
        isinstance(receipt['path'], str) and home.sha_string(receipt['sha256']),
        'fixture receipt identity')
    target = Path(receipt['path'])
    home.component_require(
        target.is_absolute() and '..' not in target.parts and
        target == target.resolve() and not target.is_symlink() and
        target.is_file() and home.digest(target) == receipt['sha256'],
        'fixture receipt path/hash')
    report = home.read_json(target)
    home.component_require(isinstance(report, dict), 'fixture report object')
    home.component_selector(selected)
    home.component_require(
        target == target.resolve() and not target.is_symlink() and
        target.is_file() and home.digest(target) == receipt['sha256'],
        'fixture receipt changed during read')
    return target, report, proof


class OwnerComponentFixtureConfiguration(unittest.TestCase):
    """Configuration bindings only; synthetic bytes are not qualifications."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='af64-fixture-config-')
        self.addCleanup(temporary.cleanup)
        self.out = Path(temporary.name).resolve()
        self.receipt = self.out / 'component.json'
        self.report = {'fixture': 'synthetic, not qualified'}
        self.receipt.write_text(json.dumps(self.report))
        self.proof = {'format': home.COMPONENT_SELECTION,
                      'receipt': {'path': str(self.receipt),
                                  'sha256': home.digest(self.receipt)},
                      'role_metadata': {}}
        self.wrapper = self.out / 'proof.json'
        self.wrapper.write_text(json.dumps(self.proof))
        self.environment = {
            'AETHER_AF09_OWNER_COMPONENT_PROOF': str(self.wrapper),
            'AETHER_AF09_OWNER_COMPONENT_PROOF_SHA256': home.digest(self.wrapper)}

    def test_actual_setup_requires_explicit_selection(self):
        case = CurrentOwnerComponent()
        try:
            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaises(ValueError):
                    case.setUp()
        finally:
            case.doCleanups()

    def test_actual_setup_rejects_partial_selection(self):
        for key, value in self.environment.items():
            case = CurrentOwnerComponent()
            try:
                with self.subTest(key=key):
                    with patch.dict(os.environ, {key: value}, clear=True):
                        with self.assertRaises(ValueError):
                            case.setUp()
            finally:
                case.doCleanups()

    def test_actual_setup_uses_only_the_explicit_wrapper_binding(self):
        case = CurrentOwnerComponent()
        try:
            with patch.dict(os.environ, self.environment, clear=True):
                case.setUp()
            self.assertEqual(case.receipt, self.receipt)
            self.assertEqual(case.report, self.report)
            self.assertEqual(case.proof, self.proof)
        finally:
            case.doCleanups()

    def test_malformed_wrapper_and_receipt_bindings_reject(self):
        for mode in ('format', 'extra', 'receipt-type', 'receipt-fields',
                     'receipt-hash', 'receipt-path', 'report-type'):
            proof = copy.deepcopy(self.proof)
            if mode == 'format':
                proof['format'] = 'unknown'
            elif mode == 'extra':
                proof['extra'] = True
            elif mode == 'receipt-type':
                proof['receipt'] = []
            elif mode == 'receipt-fields':
                proof['receipt']['extra'] = True
            elif mode == 'receipt-hash':
                proof['receipt']['sha256'] = '0' * 64
            elif mode == 'receipt-path':
                proof['receipt']['path'] = 'relative.json'
            else:
                self.receipt.write_text('[]')
                proof['receipt']['sha256'] = home.digest(self.receipt)
            self.wrapper.write_text(json.dumps(proof))
            environment = dict(self.environment)
            environment['AETHER_AF09_OWNER_COMPONENT_PROOF_SHA256'] = (
                home.digest(self.wrapper))
            with self.subTest(mode=mode):
                with patch.dict(os.environ, environment, clear=True):
                    with self.assertRaises(ValueError):
                        owner_component_fixture()

    def test_stale_wrapper_and_receipt_bytes_reject(self):
        for target in (self.wrapper, self.receipt):
            old = target.read_bytes()
            target.write_bytes(old + b'\n')
            try:
                with self.subTest(target=target.name):
                    with patch.dict(os.environ, self.environment, clear=True):
                        with self.assertRaises(ValueError):
                            owner_component_fixture()
            finally:
                target.write_bytes(old)

    def test_fixture_identity_is_rechecked_after_json_reads(self):
        read_json = home.read_json
        for target in (self.wrapper, self.receipt):
            original = target.read_bytes()

            def changed(path):
                value = read_json(path)
                if Path(path) == target:
                    target.write_bytes(original + b'\n')
                return value

            try:
                with self.subTest(target=target.name):
                    with patch.dict(os.environ, self.environment, clear=True):
                        with patch.object(home, 'read_json', side_effect=changed):
                            with self.assertRaises(ValueError):
                                owner_component_fixture()
            finally:
                target.write_bytes(original)

    def test_invalid_selector_and_receipt_alias_reject(self):
        for path, digest in (('', ''), (str(self.wrapper), 'bad'),
                             ('relative.json', home.digest(self.wrapper))):
            environment = {'AETHER_AF09_OWNER_COMPONENT_PROOF': path,
                           'AETHER_AF09_OWNER_COMPONENT_PROOF_SHA256': digest}
            with self.subTest(path=path, digest=digest):
                with patch.dict(os.environ, environment, clear=True):
                    with self.assertRaises(ValueError):
                        owner_component_fixture()
        alias = self.out / 'receipt-alias.json'
        alias.symlink_to(self.receipt)
        self.proof['receipt']['path'] = str(alias)
        self.wrapper.write_text(json.dumps(self.proof))
        environment = dict(self.environment)
        environment['AETHER_AF09_OWNER_COMPONENT_PROOF_SHA256'] = (
            home.digest(self.wrapper))
        with patch.dict(os.environ, environment, clear=True):
            with self.assertRaises(ValueError):
                owner_component_fixture()


class HistoricalOwnerComponent(unittest.TestCase):
    def test_known_component_is_stale_after_current_header_routing_change(self):
        fixture = ROOT / ('sys-init/docs/evidence/'
                          'filesystem-drain-deadline-2026-10-25/'
                          'component-01.json')
        self.assertTrue(fixture.is_file(), 'known stale fixture unavailable')
        receipt = fixture.resolve()
        self.assertEqual(
            home.digest(receipt),
            '25934d905cad20a6c3250e6dbedf55cb1c5e27a9519bfd831221fcb013adc568')
        report = home.read_json(receipt)
        roles = ROOT / 'kernel/arch/x86_64/native_fs_roles.zig'
        reader = ROOT / 'sys-init/scripts/owner_measure.py'
        proof = {'format': home.COMPONENT_SELECTION,
                 'receipt': {'path': str(receipt),
                             'sha256': home.digest(receipt)},
                 'role_metadata': {
                     'path': str(roles),
                     'before_sha256': report['sources'][str(roles)],
                     'current_sha256': home.digest(roles), 'code_limit': 49152,
                     'reader': {'path': str(reader),
                                'sha256': home.digest(reader)}}}
        with tempfile.TemporaryDirectory(prefix='af64-stale-owner-') as folder:
            wrapper = Path(folder).resolve() / 'proof.json'
            wrapper.write_text(json.dumps(proof))
            selected = {'path': str(wrapper), 'sha256': home.digest(wrapper)}
            with self.assertRaisesRegex(ValueError,
                                        r'/home_native_c_checks\.py$'):
                home.current_owner_receipt(receipt, selected)


class CurrentOwnerComponent(unittest.TestCase):
    """Retained observations only; fixture mutation never executes the harness."""
    def setUp(self):
        self.receipt, self.report, self.proof = owner_component_fixture()
        temporary = tempfile.TemporaryDirectory(prefix='af64-owner-reader-',
                                                dir='/private/tmp')
        self.addCleanup(temporary.cleanup)
        self.out = Path(temporary.name).resolve()

    def select(self,report=None,proof=None):
        proof=copy.deepcopy(self.proof if proof is None else proof)
        target=self.receipt
        if report is not None:
            target=self.out/'component.json';target.write_text(json.dumps(report))
            proof['receipt']={'path':str(target),'sha256':home.digest(target)}
        path=self.out/'selection.json';path.write_text(json.dumps(proof))
        return target,{'path':str(path),'sha256':home.digest(path)}

    def test_default_stays_historical_and_explicit_current_record_is_retained_only(self):
        with self.assertRaisesRegex(ValueError,'historical owner'):home.owner_receipt(self.receipt,{})
        target,selected=self.select()
        with patch.object(home.runpy,'run_path',wraps=home.runpy.run_path) as run:
            report,inputs,impact=home.owner_receipt(target,{},component=selected)
        self.assertEqual(report['rows'],self.report['rows']);self.assertEqual(impact['children'],911)
        self.assertFalse(impact['fresh_host_qualification']);self.assertEqual(len(impact['reconstructed_generated']),47)
        self.assertEqual(impact['selection'],selected)
        self.assertEqual(inputs[str(self.receipt)],home.digest(self.receipt));self.assertEqual(inputs[selected['path']],selected['sha256'])
        self.assertFalse(any('af61-component.py' in str(call.args[0]) for call in run.call_args_list))
        self.assertEqual(impact['role_metadata']['code_limit'],49152)

    def test_current_component_rejects_process_control_harness_and_input_tampering(self):
        for mode in ('actual','exit','cleanup','control-missing','control-duplicate','marker','control-source',
                     'typed','transport','implementation','tool','native-library','harness','missing','work','role-compiler','command','cwd','positive-marker','removed-source'):
            report=copy.deepcopy(self.report)
            if mode=='actual':report['actual_processes'][0]['exit']=1
            elif mode=='exit':report['rows'][0]['expected_exit']=1
            elif mode=='cleanup':report['rows'][0]['process']['cleanup']='unresolved';report['actual_processes'][0]=report['rows'][0]['process']
            elif mode=='control-missing':report['home_owner_controls'].pop()
            elif mode=='control-duplicate':report['home_owner_controls'][-1]=report['home_owner_controls'][0]
            elif mode=='marker':report['home_owner_controls'][0]['marker']='UNPROVED_MARKER'
            elif mode=='control-source':report['home_owner_controls'][0]['sha256']='0'*64
            elif mode=='typed':report['native_deadline_controls'][0]['marker']='OTHER'
            elif mode=='transport':report['transport_configuration_denials'][0]['sha256']='0'*64
            elif mode=='implementation':report['frozen_implementation'][next(iter(report['frozen_implementation']))]='0'*64
            elif mode=='tool':report['tools']['rustc']['sha256']='0'*64
            elif mode=='native-library':report['sources'][next(n for n in report['sources'] if '/rustlib/x86_64-unknown-none/lib/' in n)]='0'*64
            elif mode=='harness':report['harness_source']+='\n# tampered\n'
            elif mode=='missing':report['sources'][str(Path(report['work'])/'unproved.c')]='0'*64
            elif mode=='work':report['work']='/foreign/'+Path(report['work']).name
            elif mode=='command':report['rows'][0]['process']['argv'][0]='/foreign/compiler';report['actual_processes'][0]=report['rows'][0]['process']
            elif mode=='cwd':report['rows'][0]['process']['cwd']='/foreign';report['actual_processes'][0]=report['rows'][0]['process']
            elif mode=='positive-marker':next(r for r in report['rows'] if r['label']=='home-owner-tests')['stdout']='unproved pass'
            elif mode=='removed-source':report['sources'].pop(str(ROOT/'docs/native-fs-owner-stack-v1.json'))
            else:
                roles=str(ROOT/'kernel/arch/x86_64/native_fs_roles.zig');report['rows'][0]['process']['argv'].append(roles);report['actual_processes'][0]=report['rows'][0]['process']
            target,selected=self.select(report)
            with self.subTest(mode=mode),self.assertRaises(ValueError):home.owner_receipt(target,{},component=selected)

    def test_current_selection_and_role_impact_are_explicit_and_exact(self):
        for mode in ('format','receipt','before','current','reader','limit','foreign','extra'):
            proof=copy.deepcopy(self.proof)
            if mode=='format':proof['format']='unknown'
            elif mode=='receipt':proof['receipt']['sha256']='0'*64
            elif mode=='before':proof['role_metadata']['before_sha256']='0'*64
            elif mode=='current':proof['role_metadata']['current_sha256']='0'*64
            elif mode=='reader':proof['role_metadata']['reader']['sha256']='0'*64
            elif mode=='limit':proof['role_metadata']['code_limit']=65536
            elif mode=='foreign':proof['role_metadata']['path']='/foreign/roles.zig'
            else:proof['extra']=True
            target,selected=self.select(proof=proof)
            with self.subTest(mode=mode),self.assertRaises(ValueError):home.owner_receipt(target,{},component=selected)
        for selected in ([],{}, {'path':'relative','sha256':'0'*64}, {'path':str(self.out/'selection.json'),'sha256':'bad'}):
            with self.subTest(selected=selected),self.assertRaises(ValueError):home.owner_receipt(self.receipt,{},component=selected)

    def test_component_wrapper_drift_during_read_is_not_returned_as_valid(self):
        target,selected=self.select()
        def changed(report):
            path=Path(selected['path']);path.write_text(path.read_text()+'\n')
        with patch.object(home,'component_control_rows',side_effect=changed),self.assertRaisesRegex(ValueError,'input changed'):
            home.owner_receipt(target,{},component=selected)

    def test_intake_revalidates_persisted_component_before_later_work(self):
        target,selection=self.select();_,owner_inputs,impact=home.owner_receipt(target,{},component=selection)
        candidate=self.out/'dependency';candidate.mkdir();producer=self.out/'producer.json';producer.write_text('{}')
        row=record();row['owner_receipt']={'path':str(target),'sha256':home.digest(target)}
        row['producer_receipt']={'path':str(producer),'sha256':home.digest(producer)}
        row['owner_reuse']=impact;row['inputs']=owner_inputs
        for name in home.ARTIFACTS:
            (candidate/name).write_bytes(b'x'*100);row['artifacts'][name]['sha256']=home.digest(candidate/name)
        original_read=home.read_json
        def read(path):
            if Path(path).name=='build.json':return {'qualification_sha256':home.digest(producer)}
            return original_read(path)
        for changed in (False,True):
            current=copy.deepcopy(row)
            if changed:current['owner_reuse']['children']=912
            (candidate/'inputs.json').write_text(json.dumps(current))
            with patch.object(home,'checked_members',return_value={n:v['sha256'] for n,v in row['artifacts'].items()}), \
                 patch.object(home,'read_json',side_effect=read), \
                 patch.object(home.launch,'intake',return_value={'elf_sha256':'2'*64}), \
                 patch.object(home,'checked_producer',return_value=({},{})), \
                 patch.object(home,'owner_receipt',wraps=home.owner_receipt) as consume, \
                 patch.object(home,'required_sources',side_effect=RuntimeError('AFTER_COMPONENT_REVALIDATION')) as later:
                if changed:
                    with self.assertRaisesRegex(ValueError,'reuse impact drift'):home.intake(candidate,'0'*64)
                    later.assert_not_called()
                else:
                    with self.assertRaisesRegex(RuntimeError,'AFTER_COMPONENT_REVALIDATION'):home.intake(candidate,'0'*64)
                    later.assert_called_once()
                self.assertEqual(consume.call_args.kwargs,{'component':selection})

    def test_current_owner_selection_cannot_bypass_stale_actual_producer(self):
        target,selection=self.select()
        with patch.object(home,'output_path',side_effect=lambda p:p), \
             patch.object(home.launch,'intake',return_value={}), \
             patch.object(home,'checked_producer',side_effect=ValueError('STALE_ACTUAL_PRODUCER')), \
             patch.object(home,'owner_receipt',side_effect=AssertionError('owner read before producer')) as owner:
            with self.assertRaisesRegex(ValueError,'STALE_ACTUAL_PRODUCER'):
                home._build(self.out/'new-output',self.out/'engine','0'*64,self.out/'producer',target,{},self.out/'attempt.json',owner_component=selection)
            owner.assert_not_called()
        self.assertFalse((self.out/'new-output').exists())

    def test_component_cli_flags_are_paired_and_reuse_selector_is_validated(self):
        import subprocess
        command=[sys.executable,'-B',str(ROOT/'scripts/fs_home_inputs.py')]
        help=subprocess.run(command+['--help'],capture_output=True,text=True,timeout=10)
        self.assertEqual(help.returncode,0);self.assertIn('--owner-component-proof',help.stdout);self.assertTrue(help.stdout.isascii())
        required=['--engine','/absent','--engine-seal','0'*64,'--producer-receipt','/absent','--owner-receipt','/absent','--output','/absent']
        for flag,value in [('--owner-component-proof',str(self.out/'proof.json')),('--owner-component-proof-sha256','0'*64)]:
            result=subprocess.run(command+required+[flag,value],capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,64);self.assertEqual(result.stdout,'');self.assertIn('paired',result.stderr)
        for reuse in (None,[],{'format':'unknown'}, {'format':'aether-af09-owner-component-reuse-v1'},
                      {'format':'aether-af09-owner-component-reuse-v1','selection':[]}):
            candidate=record();candidate['owner_reuse']=reuse
            with self.subTest(reuse=reuse),self.assertRaises(ValueError):home.validate_record(candidate)


class GuardedCleanup(unittest.TestCase):
    def test_actual_build_reselects_component_at_final_owner_validation(self):
        for selection in (None,{'path':'/modeled/current-proof.json','sha256':'1'*64}):
            with self.subTest(selection=selection),tempfile.TemporaryDirectory(prefix='af64-final-selection-') as folder:
                root=Path(folder);(root/'userland/build').mkdir(parents=True)
                destination=root/'destination';engine=root/'engine';engine.mkdir()
                opaque=root/'opaque-fixture';opaque.write_bytes(b'not a native artifact')
                tools={'zig':{'path':'/modeled/zig','sha256':'1'*64}}
                terminal=RuntimeError('FINAL_OWNER_VALIDATION_REACHED');seen=[]
                def consume(path,producer,**kwargs):
                    seen.append(kwargs)
                    self.assertEqual(kwargs,{} if selection is None else {'component':selection})
                    if len(seen)==2:raise terminal
                    return {},{}, {'scope':'modeled retained coverage'}
                def owner(*args):return {'elf':opaque,'raw':opaque,'measurement':{}}
                def probe(*args):return {'shell':opaque,'helper':opaque,'inputs':{}}
                def imported(path):return {'build':owner if Path(path).name=='home_owner_build.py' else probe}
                proc=SimpleNamespace(clean_env=lambda work:{},run=lambda *args,**kwargs:self.fail('real process selected'))
                with ExitStack() as stack:
                    stack.enter_context(patch.object(home,'ROOT',root))
                    for name,kwargs in {
                        'output_path':{'return_value':destination},
                        'checked_producer':{'return_value':({'tools':tools},{})},
                        'owner_receipt':{'side_effect':consume},
                        'read_json':{'return_value':{'qualification_sha256':'1'*64,'inputs':{},'tools':tools}},
                        'digest':{'return_value':'1'*64},'required_sources':{'return_value':[]},
                        'verify_map':{},'owned_runner':{'return_value':proc},
                        'command_runner':{'return_value':lambda *args,**kwargs:None},
                        'merge_dependency_inputs':{},'owner_pair':{},'admit':{'return_value':{}},
                        'envelope':{'return_value':b'opaque modeled envelope'},
                    }.items():stack.enter_context(patch.object(home,name,**kwargs))
                    stack.enter_context(patch.object(home.launch,'intake',return_value={'elf':str(opaque),'elf_sha256':'1'*64}))
                    stack.enter_context(patch.object(home.launch,'closure',return_value=(engine,{})))
                    stack.enter_context(patch.object(home.launch,'checked_receipt',return_value=({},{})))
                    stack.enter_context(patch.object(home.runpy,'run_path',side_effect=imported))
                    with self.assertRaises(RuntimeError) as caught:
                        home.build(destination,engine,'1'*64,root/'producer',root/'owner',**({'owner_component':selection} if selection is not None else {}))
                self.assertIs(caught.exception,terminal);self.assertEqual(len(seen),2)
                self.assertFalse(destination.exists())
                self.assertFalse(list((root/'userland/build').glob('fs-home-inputs-*')))

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
