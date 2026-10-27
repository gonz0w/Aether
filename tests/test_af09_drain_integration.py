# SPDX-License-Identifier: BSD-2-Clause
"""Hermetic host controls for explicit diagnostic integration; no target build."""
from contextlib import ExitStack
import copy
import json
import runpy
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import fs_home_launch as launch
import fs_home_inputs as inputs
from test_fs_home_prep import record
from test_fs_home_inputs import record as guarded_record

spec = importlib.util.spec_from_file_location('drain_qualifier', ROOT / 'sys-init/scripts/qualify-home-owner.py')
qualifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qualifier)
CASES = ('file_prefix', 'exec_prefix', 'fork_prefix', 'stream', 'no_ack',
         'partial_ack', 'exit_deadline', 'pending_fragment')


def setUpModule():
    global deny_spawn
    deny_spawn = patch.object(subprocess, 'Popen', side_effect=AssertionError('no real child in integration mocks'))
    deny_spawn.start()


def tearDownModule():
    deny_spawn.stop()


class DrainIntegration(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='af09-drain-integration-test-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        proof = self.root / 'proof.json'
        proof.write_text('{"synthetic":"host binding, not qualification"}')
        self.identity = dict(path=str(proof), sha256=launch.digest(proof))
        def selection(case):
            if not isinstance(case, str) or case not in ('none', *CASES):
                raise ValueError('invalid diagnostic selection')
            return 0 if case == 'none' else CASES.index(case) + 1
        def binding(identity, case):
            selection(case)
            if identity != self.identity or launch.digest(identity['path']) != identity['sha256']:
                raise ValueError('synthetic host binding identity')
            return dict(inputs={identity['path']: identity['sha256']})
        fake = SimpleNamespace(selection=selection, host_inputs=binding, CASES=CASES)
        guard = patch.dict(sys.modules, af09_drain_inputs=fake)
        guard.start()
        self.addCleanup(guard.stop)

    def test_exact_diagnostic_identity_and_closed_selection(self):
        self.assertEqual(launch.diagnostic_selection('none', None), (None, {}))
        for case_id, case in enumerate(CASES, 1):
            diagnostic, bound = launch.diagnostic_selection(case, self.identity)
            self.assertEqual(diagnostic, dict(case=case, case_id=case_id, host_inputs=self.identity))
            self.assertEqual(bound, {self.identity['path']: self.identity['sha256']})
        for case, identity in ((None, self.identity), ('unknown', self.identity), ('none', self.identity),
                               ('stream', None), ('stream', {})):
            with self.subTest(case=case), self.assertRaises(ValueError):
                launch.diagnostic_selection(case, identity)

    def test_proof_is_revalidated_not_merely_carried(self):
        launch.diagnostic_selection('stream', self.identity)
        Path(self.identity['path']).write_text('changed')
        with self.assertRaisesRegex(ValueError, 'binding identity'):
            launch.diagnostic_selection('stream', self.identity)

    def engine_record(self):
        row = record()
        leaf = runpy.run_path(str(launch.SOURCE/'home_engine_build.py'))
        profile = [*launch.PROFILE[:-1], 'fs_af09_drain']
        sources = {str(launch.SOURCE/n): launch.digest(launch.SOURCE/n)
                   for n in ('native-home.rs','launch-home-owner.rs','home_engine_build.py')}
        row['inputs'].update(sources)
        row['home_engine_rust'] = dict(profile=profile,drain_case='stream',drain_case_id=4,
            flags=[*leaf['BASE'],*[arg for n in profile for arg in ('--cfg',n)]],sources=sources,
            artifacts={'service': {'sha256': row['service_object_sha256']}})
        return row

    def test_selected_engine_schema_flags_counts_and_same_case(self):
        row = self.engine_record()
        row.update(schema='aether-fs-home-drain-launch-v1', flags=[*launch.PROFILE[:-1], 'fs_af09_drain'],
                   provider_attempts=2, service_requests=3,
                   diagnostic=dict(case='stream', case_id=4, host_inputs=self.identity))
        row['inputs'].update({self.identity['path']: self.identity['sha256']})
        launch.validate_record(row, drain_case='stream', diagnostic_host_inputs=self.identity)
        with self.assertRaises(ValueError):
            launch.validate_record(row)
        for change in ({'schema': launch.SCHEMA}, {'provider_attempts': 3}, {'flags': list(launch.PROFILE)},
                       {'service_requests': 4}, {'diagnostic': dict(case='file_prefix', case_id=1, host_inputs=self.identity)}):
            bad = copy.deepcopy(row)
            bad.update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                launch.validate_record(bad, drain_case='stream', diagnostic_host_inputs=self.identity)
        with self.assertRaises(ValueError):
            launch.validate_record(record(), drain_case='stream', diagnostic_host_inputs=self.identity)

    def application_record(self):
        row = guarded_record()
        leaf = runpy.run_path(str(inputs.S/'home_probe_build.py'))
        parent = [*leaf['UNITS'],'fd-home-probe-adapter','fd-home-drain']
        helper = [n for n in leaf['UNITS'] if n!='fd-shell-entry']+['fd-command-entry','fd-home-probe-adapter','fd-home-probe']
        sources={str(inputs.S/(n+'.c')):launch.digest(inputs.S/(n+'.c')) for n in {*parent,*helper}}
        flags=[*leaf['FLAGS'],'--target=x86_64-unknown-none','-ffreestanding','-fno-builtin',
               '-O2','-fstack-usage','-nostdinc','-isystem',str(ROOT/'userland/build/sdk-deliveries/native-service-runtime-2026-10-06-v2/sdk/stage/usr/include'),
               '-DAEFD_FORK_BINDINGS','-DAEFD_EXEC_BINDINGS','-I'+str(inputs.S)]
        selection=dict(drain_case='stream',drain_case_id=4,parent_sources=parent,helper_sources=helper,
            case_flags=['-DAEFD_HOME_DRAIN_CASE=4'],excluded_parent_objects=['/retained/dash'+str(i)+'.o' for i in range(32)],
            parent_objects=[str(self.root/(n+'.o')) for n in parent],
            helper_objects=[str(self.root/(n+'.o')) for n in helper])
        artifact={'sha256':'5'*64,'bytes':100}
        app=dict(sources=sources,flags=flags,profile=dict(selection='fs_af09_drain',provider_attempts=2,
            utc_min=1791290040,utc_max=1791290100,utc_half_open=True,rtc_base='2026-10-06T12:34:00'),
            selection=selection,artifacts={'shell':dict(artifact),'helper':dict(artifact)})
        diagnostic=dict(case='stream',case_id=4,host_inputs=self.identity)
        row.update(format=inputs.DRAIN_SCHEMA,profile=inputs.selected_profile(drain_case='stream'),
                   diagnostic=diagnostic,application=app)
        row['inputs'].update(sources)
        row['inputs'].update({self.identity['path']:self.identity['sha256']})
        row['tools']['clang']=dict(path='/synthetic/clang',sha256='7'*64)
        def command(label,argv):
            return dict(label=label,status='pass',process=dict(complete=True,cleanup='complete',exit=0,argv=argv))
        row['commands']=[
            command('home-target-fd-home-drain',['/synthetic/clang',*flags,*selection['case_flags'],
                '-c',str(inputs.S/'fd-home-drain.c'),'-o',str(self.root/'fd-home-drain.o')]),
            command('home-complete-shell-link',['/synthetic/lld',*selection['parent_objects'],'-o','shell.elf']),
            command('home-complete-helper-link',['/synthetic/lld',*selection['helper_objects'],'-o','helper.elf']),
            command('actual-kernel-build',['/tool/zig','build','-Dsmp=false',*inputs.kernel_arguments(drain_case='stream')])]
        row['kernel_build']['diagnostic_argument']='-Dnative-af09-drain=stream'
        return row

    def test_guarded_application_and_kernel_bind_actual_rows_and_case(self):
        row=self.application_record()
        inputs.validate_record(row,drain_case='stream',diagnostic_host_inputs=self.identity)
        for mutation in (
                lambda r:r['application']['selection'].update(drain_case_id=3),
                lambda r:r['application']['selection']['helper_objects'].append('/owned/fd-home-drain.o'),
                lambda r:r['application']['artifacts']['shell'].update(sha256='0'*64),
                lambda r:r['commands'][0]['process']['argv'].remove('-DAEFD_HOME_DRAIN_CASE=4'),
                lambda r:r['commands'][0]['process']['argv'].append('-DAEFD_HOME_DRAIN_CASE=1'),
                lambda r:r['commands'][1]['process']['argv'].append('/old/dash-main.o'),
                lambda r:r['commands'][-1]['process']['argv'].append('-Dnative-af09-drain=stream'),
                lambda r:r['commands'][-1]['process']['argv'].__setitem__(-1,'-Dnative-af09-drain=stream=true'),
                lambda r:r['inputs'].__setitem__(str(inputs.S/'fd-home-drain.c'),'0'*64)):
            bad=copy.deepcopy(row);mutation(bad)
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):
                inputs.validate_record(bad,drain_case='stream',diagnostic_host_inputs=self.identity)
        with self.assertRaises(ValueError):inputs.validate_record(row)

    def test_selected_actual_compile_cannot_drop_fork_binding(self):
        row=self.application_record()
        row['application']['flags'].remove('-DAEFD_FORK_BINDINGS')
        row['commands'][0]['process']['argv'].remove('-DAEFD_FORK_BINDINGS')
        with self.assertRaisesRegex(ValueError,'compiler flags'):
            inputs.validate_record(row,drain_case='stream',diagnostic_host_inputs=self.identity)

    def test_selected_actual_kernel_cannot_drop_required_boolean_flag(self):
        row=self.application_record()
        argv=row['commands'][-1]['process']['argv']
        argv.remove('-Dnative-fs-owner-stack=true')
        with self.assertRaisesRegex(ValueError,'kernel argument'):
            inputs.validate_record(row,drain_case='stream',diagnostic_host_inputs=self.identity)

    def test_selected_rust_record_rejects_mixed_flags_or_disconnected_object(self):
        row=self.engine_record()
        row.update(schema=launch.DRAIN_SCHEMA,flags=[*launch.PROFILE[:-1],'fs_af09_drain'],provider_attempts=2,
            service_requests=3,diagnostic=dict(case='stream',case_id=4,host_inputs=self.identity))
        row['inputs'][self.identity['path']]=self.identity['sha256']
        for mutation in (lambda r:r['home_engine_rust']['flags'].append('fs_home_probe_three'),
                lambda r:r['home_engine_rust']['artifacts']['service'].update(sha256='0'*64),
                lambda r:r['home_engine_rust']['sources'].clear()):
            bad=copy.deepcopy(row);mutation(bad)
            with self.assertRaises(ValueError):launch.validate_record(bad,drain_case='stream',diagnostic_host_inputs=self.identity)

    def test_none_forbids_diagnostic_metadata_without_changing_old_record(self):
        launch.validate_record(record())
        row = record()
        row['diagnostic'] = dict(case='stream', case_id=4, host_inputs=self.identity)
        with self.assertRaises(ValueError):
            launch.validate_record(row)

    def test_bad_selection_blocks_all_builds_before_output_effects(self):
        for module, arguments in ((launch, [self.root / 'engine', 'producer', 'probe']),
                (inputs, [self.root / 'inputs', 'engine', 'seal', 'producer', 'owner']),
                (qualifier, ['inputs', 'seal'])):
            function = module.prepare if module is qualifier else module.build
            for case, identity in (('none', self.identity), ('stream', None), (None, None)):
                with self.subTest(module=module.__name__, case=case), self.assertRaises(ValueError):
                    function(*arguments, drain_case=case, diagnostic_host_inputs=identity)
            self.assertEqual(sorted(p.name for p in self.root.iterdir()), ['proof.json'])

    def test_kernel_selection_is_one_nonboolean_argument(self):
        old = ['-D' + f + '=true' for f in inputs.kernel_flags()]
        self.assertEqual(inputs.kernel_arguments(), old)
        for case in CASES:
            actual = inputs.kernel_arguments(drain_case=case)
            self.assertEqual(actual, [*old, '-Dnative-af09-drain=' + case])
            self.assertEqual(sum(a.startswith('-Dnative-af09-drain=') for a in actual), 1)
            profile = inputs.selected_profile(drain_case=case)
            self.assertEqual(profile['selection'], 'fs_af09_drain')
            self.assertEqual(profile['provider_attempts'], 2)
            self.assertEqual((profile['envelope'], profile['nested'], profile['abi']), ('AENFS005', 'AENMX010', 31))
        self.assertEqual(inputs.selected_profile(), inputs.PROFILE)

    def test_qualifier_intake_forwards_exact_explicit_selection(self):
        diagnostic = dict(case='stream', case_id=4, host_inputs=self.identity)
        selected = dict(format='aether-guarded-af09-drain-inputs-v1',
            profile=inputs.selected_profile(drain_case='stream'), diagnostic=diagnostic,
            bounds=inputs.BOUNDS, admission=dict(engine_pages=1337,shell_pages=80,helper_pages=35,owner_bytes=47384))
        with patch.object(inputs, 'intake', return_value=dict(format=selected['format'])) as intake, \
                patch.object(inputs, 'read_json', return_value=selected), \
                patch.object(qualifier.time, 'monotonic', return_value=10):
            self.assertEqual(qualifier.input_record(Path('/sealed'), '1'*64, deadline=20,
                drain_case='stream', diagnostic_host_inputs=self.identity), selected)
            intake.assert_called_once_with(Path('/sealed'), '1'*64, deadline=20,
                drain_case='stream', diagnostic_host_inputs=self.identity)

    def test_selected_recovery_is_never_silently_old_reader(self):
        def old_reader(*args):
            raise AssertionError('old reader called')
        with patch.object(qualifier.home_reader, 'compose', old_reader), \
                patch.object(qualifier, 'input_record', side_effect=AssertionError('intake reached')):
            with self.assertRaisesRegex(ValueError, 'reader.*drain_case'):
                qualifier.prepare('/sealed', '1'*64, drain_case='stream', diagnostic_host_inputs=self.identity)

    def test_actual_engine_build_forwards_selected_case_to_leaf_before_composition(self):
        root=self.root/'engine-model';(root/'userland/build').mkdir(parents=True)
        helper=root/'userland/experiments/command-runner/process.py'
        helper.parent.mkdir(parents=True);helper.write_text('# inert model identity, never imported')
        producer=root/'producer';producer.write_text('{}')
        probe=root/'probe';probe.write_text('{}')
        tool=root/'tool';tool.write_text('synthetic identity, never executed')
        tools={n:dict(path=str(tool),sha256=launch.digest(tool)) for n in launch.EXECUTION_ROLES}
        destination=root/'fs-launch-af09-model'
        terminal=RuntimeError('SELECTED_LEAF_REACHED')
        observed={}
        def leaf(work,proc,selected,deadline,result,**kwargs):
            observed.update(kwargs=kwargs,diagnostic=result['diagnostic'],flags=result['flags'])
            raise terminal
        proc=SimpleNamespace(clean_env=lambda work:{},run=lambda *a,**k:self.fail('real target runner reached'))
        with ExitStack() as stack:
            for name,kwargs in {
                'ROOT':dict(new=root),'SOURCE':dict(new=root/'source'),
                'checked_receipt':dict(return_value=({},{})), 'generated_sources':dict(return_value={}),
                'current_dependency_inputs':dict(return_value=({},{})),
                'verify_inputs':dict(side_effect=lambda value:value),
                'read_json':dict(return_value=dict(tools=tools)),
            }.items():stack.enter_context(patch.object(launch,name,**kwargs))
            stack.enter_context(patch('deps.verify'))
            stack.enter_context(patch('fs_launch.validate_destination',return_value=destination))
            stack.enter_context(patch.object(launch.shutil,'which',return_value=str(tool)))
            stack.enter_context(patch('importlib.util.spec_from_file_location'))
            stack.enter_context(patch('importlib.util.module_from_spec',return_value=proc))
            stack.enter_context(patch.object(launch.runpy,'run_path',return_value={'build':leaf}))
            with self.assertRaises(RuntimeError) as error:
                launch.build(destination,producer,probe,drain_case='stream',diagnostic_host_inputs=self.identity)
        self.assertIs(error.exception,terminal)
        self.assertEqual(observed['kwargs'],dict(drain_case='stream'))
        self.assertEqual(observed['diagnostic']['case_id'],4)
        self.assertIn('fs_af09_drain',observed['flags'])
        self.assertNotIn('fs_home_probe_three',observed['flags'])
        self.assertFalse(destination.exists())
        self.assertFalse(list((root/'userland/build').iterdir()))

    def test_actual_guarded_build_rejects_wrong_returned_c_case_before_copy_or_kernel(self):
        root=self.root/'guarded-model';(root/'userland/build').mkdir(parents=True)
        engine=root/'engine';engine.mkdir()
        opaque=root/'opaque';opaque.write_bytes(b'opaque model, not a target artifact')
        tools={'zig':dict(path='/synthetic/zig',sha256='1'*64)}
        destination=root/'candidate';seen=[]
        def owner(*args):return dict(elf=opaque,raw=opaque,measurement={})
        def probe(*args,**kwargs):
            seen.append(kwargs)
            return dict(drain_case='file_prefix',drain_case_id=1,sources={})
        def imported(path):return {'build':owner if Path(path).name=='home_owner_build.py' else probe}
        proc=SimpleNamespace(clean_env=lambda work:{},run=lambda *a,**k:self.fail('real target runner reached'))
        with ExitStack() as stack:
            stack.enter_context(patch.object(inputs,'ROOT',root))
            for name,kwargs in {
                'output_path':dict(return_value=destination),
                'checked_producer':dict(return_value=({'tools':tools},{})),
                'owner_receipt':dict(return_value=({}, {}, {})),
                'read_json':dict(return_value=dict(qualification_sha256='1'*64,inputs={},tools=tools)),
                'digest':dict(return_value='1'*64),'required_sources':dict(return_value=[]),
                'verify_map':{},'owned_runner':dict(return_value=proc),
                'command_runner':dict(return_value=lambda *a,**k:self.fail('kernel command reached')),
                'merge_dependency_inputs':{},
            }.items():stack.enter_context(patch.object(inputs,name,**kwargs))
            consume=stack.enter_context(patch.object(launch,'intake',return_value=dict(elf=str(opaque),elf_sha256='1'*64)))
            stack.enter_context(patch.object(launch,'closure',return_value=(engine,{})))
            stack.enter_context(patch.object(inputs.runpy,'run_path',side_effect=imported))
            with self.assertRaisesRegex(ValueError,'returned C selection mismatch'):
                inputs.build(destination,engine,'1'*64,root/'producer',root/'owner',
                    drain_case='stream',diagnostic_host_inputs=self.identity)
        self.assertEqual(seen,[dict(drain_case='stream')])
        self.assertEqual(consume.call_args.kwargs,dict(drain_case='stream',diagnostic_host_inputs=self.identity))
        self.assertFalse(destination.exists())
        self.assertFalse(list((root/'userland/build').iterdir()))

    def test_actual_prepare_uses_autonomous_writer_and_only_permitted_readers(self):
        import deps
        from openzfs_namespace import FIXTURE_SHA256
        for case_id,case in enumerate(CASES,1):
            root=self.root/('prepare-'+case);(root/'zig-out').mkdir(parents=True)
            incoming=root/'sealed';incoming.mkdir()
            (incoming/'envelope.bin').write_bytes(b'opaque model envelope')
            tool=root/'tool';tool.write_text('synthetic tool, never executed')
            selected=dict(tools={n:dict(path=str(tool),sha256=launch.digest(tool)) for n in ('qemu','zig')},inputs={},
                artifacts={'envelope.bin':dict(sha256=launch.digest(incoming/'envelope.bin'))},
                profile=inputs.selected_profile(drain_case=case),bounds=inputs.BOUNDS,
                admission=dict(engine_pages=1300,shell_pages=50,helper_pages=40,owner_bytes=40000),
                measurement={},kernel_build={'flags':list(qualifier.WRITER_FLAGS)},
                diagnostic=dict(case=case,case_id=case_id,host_inputs=self.identity))
            receipt_path=root/'attempt.json';calls=[];readers=[]
            def run(argv,**kwargs):
                calls.append(list(argv))
                out=Path(argv[argv.index('-p')+1]);(out/'bin').mkdir()
                (out/'bin/aether').write_bytes(b'opaque kernel model')
                (out/'aether.iso').write_bytes(b'opaque iso model')
                return SimpleNamespace(returncode=0,stdout=b'',stderr=b'',record=dict(exit=0,complete=True,cleanup='complete'))
            proc=SimpleNamespace(clean_env=lambda work:{},run=run)
            def reader(stage,*args,**kwargs):
                readers.append((stage.name,kwargs))
                stage.mkdir();(stage/'kernel.elf').write_bytes(b'opaque reader model')
                (stage/'aether.iso').write_bytes(b'opaque iso model')
                return dict(engine_pages=1300)
            def available_reader(*args,drain_case='none'):pass
            digest=qualifier.digest
            def selected_digest(path):
                name=Path(path).name
                if name=='readback.rs':return qualifier.ORIGINAL_CONTROLLER_SHA256
                if not Path(path).is_file():return FIXTURE_SHA256
                return digest(path)
            with ExitStack() as stack:
                stack.enter_context(patch.object(qualifier,'ROOT',root))
                stack.enter_context(patch.object(qualifier.home_reader,'compose',available_reader))
                consume=stack.enter_context(patch.object(qualifier,'input_record',return_value=selected))
                for name,kwargs in {
                    'digest':dict(side_effect=selected_digest),'owned_process':dict(return_value=proc),
                    'reserve_evidence':dict(return_value=receipt_path),
                    'tool_environment':dict(return_value=(None,{})), 'child_environment':dict(return_value={}),
                    'verify_boundary':{},'verify_child':{},'build_controller':dict(return_value={'path':str(root/'opaque-controller'),'sha256':'1'*64}),
                    'build_reader':dict(side_effect=reader),
                    'writer_trace':dict(side_effect=AssertionError('legacy writer oracle reached')),
                    'qualify_sequence':dict(side_effect=AssertionError('legacy media oracle reached')),
                }.items():stack.enter_context(patch.object(qualifier,name,**kwargs))
                stack.enter_context(patch.object(launch,'verify_inputs',side_effect=lambda value:value))
                stack.enter_context(patch.object(deps,'verify'))
                stack.enter_context(patch.object(deps,'DEPS',root/'deps'))
                stack.enter_context(patch.object(inputs,'read_json',return_value={'files':{}}))
                result=qualifier.prepare(incoming,'1'*64,drain_case=case,diagnostic_host_inputs=self.identity)
            receipt=json.loads(receipt_path.read_text())
            roles=['pristine','writer','recovery'] if case_id<=4 else ['pristine','writer']
            self.assertEqual(receipt['schema'],qualifier.DRAIN_SCHEMA)
            self.assertEqual(receipt['script_hex'],'')
            self.assertEqual(receipt['prospective_sequence'],roles)
            self.assertEqual(list(receipt['artifacts']),roles)
            self.assertEqual([name for name,_ in readers],[n for n in roles if n!='writer'])
            self.assertTrue(all(kwargs==dict(drain_case=case) for _,kwargs in readers))
            self.assertEqual([a for a in calls[0] if str(a).startswith('-Dnative-af09-drain=')],['-Dnative-af09-drain='+case])
            self.assertEqual(receipt['cleanup']['kept_pending_images'],len(roles))
            self.assertEqual(consume.call_count,2)
            self.assertTrue(all(c.kwargs['drain_case']==case for c in consume.call_args_list))
            self.assertEqual(result['status'],'prepared')

    def test_paired_cli_selection_and_forwarding(self):
        specifications = [
            (launch, ['--checked','p','--probe-checked','q','--output','o'], launch.main, 'build'),
            (inputs, ['--engine','e','--engine-seal','s','--producer-receipt','p','--owner-receipt','r','--output','o'], inputs.main, 'build'),
            (qualifier, ['--inputs','e','--seal','s','--prepare'], qualifier.main, 'prepare')]
        for module, base, main, operation in specifications:
            for extra in (['--native-af09-drain','stream'], ['--diagnostic-host-inputs',self.identity['path']],
                          ['--diagnostic-host-inputs',self.identity['path'],'--diagnostic-host-inputs-sha256',self.identity['sha256']]):
                with self.subTest(module=module.__name__,extra=extra), \
                        patch.object(sys, 'argv', ['tool',*base,*extra]), patch.object(module, operation) as action, \
                        patch('sys.stderr', new_callable=io.StringIO), self.assertRaises(SystemExit) as error:
                    main()
                self.assertEqual(error.exception.code, 64)
                action.assert_not_called()
            extra = ['--native-af09-drain','stream','--diagnostic-host-inputs',self.identity['path'],
                     '--diagnostic-host-inputs-sha256',self.identity['sha256']]
            with patch.object(sys, 'argv', ['tool',*base,*extra]), \
                    patch.object(module, operation, return_value={}) as action, patch('sys.stdout', new_callable=io.StringIO):
                main()
            self.assertEqual(action.call_args.kwargs['drain_case'], 'stream')
            self.assertEqual(action.call_args.kwargs['diagnostic_host_inputs'], self.identity)


if __name__ == '__main__':
    unittest.main()
