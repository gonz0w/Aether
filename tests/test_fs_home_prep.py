# SPDX-License-Identifier: BSD-2-Clause
"""Private AF09 association guards; synthetic records are not engine evidence."""
from contextlib import ExitStack
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import fs_home_launch as home


def record():
    return dict(schema='aether-fs-home-launch-v1', status='pass', executed=False,
        native_acceptance=False, protocol='AFSRPC09', service_result_bytes=320,
        launch_state_bytes=384, root_rights=3, home_rights=15, source_rights=15,
        provider_attempts=3, utc_min=1791290040, utc_max_exclusive=1791290100,
        rtc='2026-10-06T12:34:00,clock=vm', flags=list(home.PROFILE),
        limits=dict(mutations=9, requests=96, engine_pages=8192,
            writer_seconds=60, writer_ticks=6000, reader_seconds=30, reader_ticks=3000),
        origins={name: str(Path('/owned') / origin) for name, origin in home.REQUIRED.items()},
        partial_origins={name: str(Path('/owned') / origin) for name, origin in home.PARTIAL.items()},
        structural_loader='ELF structural pages=1334', inputs={'/retained/input':'1'*64},
        commands=[dict(status='pass',exit_code=0), *[dict(status='pass',exit_code=1,
            expected_rejection=marker,rejection_verified=True) for marker in sorted(home.LINK_DENIALS)]], qualification_sha256='1'*64,
        probe_qualification_sha256='2'*64, service_object_sha256='3'*64,
        elf_sha256='4'*64, elf_bytes=123456)


class HomePreparation(unittest.TestCase):
    def test_exact_expected_linker_denials_are_checked_not_successful_links(self):
        row=record()
        marker='undefined symbol: aether_volume_bind'
        home.validate_record(row)
        for change in ({'exit_code':0},{'exit_code':-9},{'rejection_verified':False},
                       {'expected_rejection':'unrelated failure'}):
            bad=copy.deepcopy(row)
            selected=next(command for command in bad['commands'] if command.get('expected_rejection')==marker)
            selected.update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):
                home.validate_record(bad)
        for commands in (row['commands'][:-1],row['commands']+[row['commands'][-1]]):
            bad=copy.deepcopy(row);bad['commands']=commands
            with self.assertRaises(ValueError):home.validate_record(bad)

    def test_pinned_recipe_tools_never_use_path_or_another_rust(self):
        with tempfile.TemporaryDirectory(prefix='home-recipe-tools-') as folder:
            tools = {}
            for name in home.EXECUTION_ROLES:
                path = Path(folder) / name
                path.write_text('synthetic tool identity: ' + name)
                tools[name] = dict(path=str(path), sha256=home.digest(path))
            self.assertEqual(
                home.command_arguments(['rustc', '+1.98.0', '--version'], tools),
                [tools['rustc']['path'], '--version'])
            self.assertEqual(
                home.command_arguments(['zig', 'run', 'check.zig'], tools),
                [tools['zig']['path'], 'run', 'check.zig'])
            for command in ([], ['rustc', '+nightly'],
                            ['rustc', '+1.99.0'], ['clang', 'a.c']):
                with self.subTest(command=command), self.assertRaises(ValueError):
                    home.command_arguments(command, tools)

    def test_runtime_inputs_stay_partitioned_and_rechecked_until_link(self):
        with tempfile.TemporaryDirectory(prefix='home-runtime-lifetime-') as directory:
            root=Path(directory);work=root/'owned';work.mkdir()
            original=root/'retained.h';original.write_bytes(b'original')
            header=work/'selected.h';header.write_bytes(b'selected')
            hashes={str(p):home.digest(p) for p in (original,header)}
            retained,generated={},{}
            home.bind_runtime({'inputs':hashes},work,retained,generated)
            self.assertEqual(set(retained),{str(original)})
            self.assertEqual(set(generated),{str(header)})
            header.write_bytes(b'changed after constructor returned')
            with self.assertRaisesRegex(ValueError,'input changed'):
                home.verify_inputs(generated)
            with self.assertRaisesRegex(ValueError,'conflicting'):
                home.bind_runtime({'inputs':hashes},work,{str(original):'0'*64},{})

    def test_runtime_constructor_artifact_identities_are_not_blessed_late(self):
        with tempfile.TemporaryDirectory(prefix='home-runtime-artifact-') as directory:
            work=Path(directory);base=work/'diagnostic';build=base/'failure-runtime-build'
            build.mkdir(parents=True);(base/'failure-runtime').mkdir()
            header=work/'header.h';header.write_bytes(b'header')
            paths=[build/'original-backend.o',build/'backend.o',base/'failure-runtime/libaether_runtime.a']
            for index,path in enumerate(paths):path.write_bytes(bytes([index]))
            backend=dict(inputs={str(header):home.digest(header)},original_backend_sha256=home.digest(paths[0]),
                selected_backend_sha256=home.digest(paths[1]),archive_sha256=home.digest(paths[2]))
            retained,generated={},{}
            home.bind_runtime(backend,work,retained,generated,artifact_root=base)
            self.assertEqual(generated[str(paths[2])],backend['archive_sha256'])
            paths[2].write_bytes(b'changed before consumer link')
            with self.assertRaisesRegex(ValueError,'input changed'):
                home.bind_runtime(backend,work,{}, {},artifact_root=base)

    def test_recipe_replacement_requires_exact_single_inputs(self):
        row=['ld','old.o','-Map=old.map','-o','old.elf']
        self.assertEqual(home.relink(row, {'old.o':['new.o','extra.o']}, Path('/owned/new.elf'),
                                   Path('/owned/new.map')),
                         ['ld','new.o','extra.o','-Map=/owned/new.map','-o','/owned/new.elf'])
        for broken in (['ld','-o','old.elf'], ['ld','old.o','old.o','-o','old.elf'],
                       ['ld','old.o','old.elf'], ['ld','old.o','-o','old.elf','tail']):
            with self.subTest(recipe=broken), self.assertRaises(ValueError):
                home.relink(broken, {'old.o':['new.o']}, Path('/owned/new.elf'), Path('/owned/new.map'))

    def test_frame_checks_require_the_four_actual_c_units(self):
        frames={name: 'source.c:1:run\t48\tstatic\n' for name in
                ('pool-home-label.su','home-provider.su','home-engine.su','home-import.su')}
        home.check_frames(frames)
        for bad in ({}, dict(frames, **{'old.su':'x\t8\tstatic\n'}),
                    dict(frames, **{'home-engine.su':'x\t8193\tstatic\n'}),
                    dict(frames, **{'home-import.su':'x\t64\tdynamic\n'})):
            with self.subTest(frames=bad), self.assertRaises(ValueError):
                home.check_frames(bad)

    def test_engine_shape_claims_only_preparation(self):
        row=record()
        home.validate_record(row)
        for key,value in [('executed',True),('executed',0),('native_acceptance',True),
                          ('status','incomplete'),('protocol','AFSRPC08'),
                          ('service_result_bytes',72),('launch_state_bytes',136)]:
            bad=copy.deepcopy(row); bad[key]=value
            with self.subTest(key=key,value=value), self.assertRaises(ValueError):
                home.validate_record(bad)

    def test_authority_clock_flags_and_bounds_cannot_drift(self):
        row=record()
        changes=[('root_rights',15),('home_rights',31),('source_rights',31),
                 ('provider_attempts',2),('utc_min',1791290039),
                 ('utc_max_exclusive',1791290101),('rtc','host'),
                 ('flags',[x for x in home.PROFILE if x!='fs_home_probe_three'])]
        for key,value in changes:
            bad=copy.deepcopy(row);bad[key]=value
            with self.subTest(key=key), self.assertRaises(ValueError):
                home.validate_record(bad)
        for key in row['limits']:
            bad=copy.deepcopy(row);bad['limits'][key]+=1
            with self.subTest(limit=key), self.assertRaises(ValueError):
                home.validate_record(bad)

    def test_exact_object_origins_and_all_commands_required(self):
        for key in ('origins','partial_origins'):
            row=record(); name=next(iter(row[key]))
            for label,alter in [('missing',lambda d:d[key].pop(name)),
                                ('foreign',lambda d:d[key].__setitem__(name,'old-service.o')),
                                ('extra',lambda d:d[key].__setitem__('aether_fs_metadata_run','old.o'))]:
                bad=copy.deepcopy(row);alter(bad)
                with self.subTest(group=key,label=label), self.assertRaises(ValueError):
                    home.validate_record(bad)
        for command in ([],[dict(status='failed',exit_code=1)],
                        [dict(status='pass',exit_code=1)]):
            row=record();row['commands']=command
            with self.subTest(command=command), self.assertRaises(ValueError):
                home.validate_record(row)

    def test_strong_new_symbols_reject_old_weak_missing_and_duplicate(self):
        names=list(home.REQUIRED)
        good='\n'.join('0000000000200000 T '+name for name in names)+'\n'
        home.strong_symbols(good)
        alternatives=[good.replace(' T '+names[0],' W '+names[0],1),
                      good.split('\n',1)[1], good+good.splitlines()[0]+'\n',
                      good+'0000000000200010 T aether_fs_metadata_run\n',
                      good+'0000000000200020 T aether_fs_engine_run\n']
        for symbols in alternatives:
            with self.subTest(symbols=symbols[-80:]), self.assertRaises(ValueError):
                home.strong_symbols(symbols)

    def test_live_input_identity_is_rechecked(self):
        with tempfile.TemporaryDirectory(prefix='home-input-identity-') as folder:
            source=Path(folder)/'source.c';source.write_text('original')
            inputs={str(source):hashlib.sha256(source.read_bytes()).hexdigest()}
            home.verify_inputs(inputs)
            source.write_text('changed')
            with self.assertRaisesRegex(ValueError,'input changed'):
                home.verify_inputs(inputs)
            with self.assertRaises(ValueError):
                home.verify_inputs({'relative.c':'0'*64})

    def test_disposed_generated_sources_need_exact_pinned_recipes(self):
        # Only the known home generator's two output identities may be absent.
        with tempfile.TemporaryDirectory(prefix='home-disposed-input-') as folder:
            path=Path(folder)/'arbitrary.c'
            with self.assertRaisesRegex(ValueError,'unavailable|generated'):
                home.verify_inputs({str(path):'0'*64})
        with self.assertRaises(ValueError):
            home.verify_inputs({})

    def test_retained_input_preflight_stops_before_generated_source_context(self):
        source=ROOT/'userland/docs/evidence/filesystem-home-native-2026-10-24/attempt-13.json'
        report=home.read_json(source)
        with tempfile.TemporaryDirectory(prefix='home-retained-preflight-') as directory:
            live=Path(directory)/'retained.rs';live.write_bytes(b'checked input')
            report['sources']={str(live):home.digest(live)}
            with patch.object(home,'read_json',return_value=report), patch.object(
                    home,'generated_sources',side_effect=AssertionError('GENERATOR_REACHED')) as generate:
                with self.assertRaisesRegex(AssertionError,'GENERATOR_REACHED'):
                    home.checked_receipt(source,'producer')
                generate.assert_called_once_with(report)
                generate.reset_mock();live.write_bytes(b'changed input')
                with self.assertRaisesRegex(ValueError,r'^AF09 input changed:'):
                    home.checked_receipt(source,'producer')
                generate.assert_not_called()

    def test_real_old_producer_receipt_is_stale_after_fixed_probe_change(self):
        source=ROOT/'userland/docs/evidence/filesystem-home-native-2026-10-24/attempt-13.json'
        self.assertTrue(source.is_file(), 'required retained producer receipt is unavailable')
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),
            'ebee88f7d60b33847e326c875f4998658268515732e423012449b8f6a41550f0')
        with self.assertRaisesRegex(ValueError, r'^AF09 input changed:'):
            home.checked_receipt(source,'producer')


class EngineExecutionInputs(unittest.TestCase):
    """Synthetic tools and capsules exercise routing, never compile code."""
    ROLES = ('clang', 'ar', 'lld', 'nm', 'readelf', 'rustc',
             'clippy-driver', 'zig')

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='af09-engine-input-')
        self.addCleanup(temporary.cleanup)
        self.out = Path(temporary.name).resolve()
        self.tools = {}
        for role in self.ROLES:
            path = self.out / role
            path.write_text('opaque synthetic tool: ' + role)
            self.tools[role] = dict(path=str(path), sha256=home.digest(path))
        self.public = self.out / 'public'
        self.retained = self.out / 'retained'
        self.current = self.retained / '.deps/native-current'
        self.current.mkdir(parents=True)
        self.logical = self.public / '.deps/native-current'
        self.logical.mkdir(parents=True)
        self.member = self.current / 'baseline/header.h'
        self.member.parent.mkdir()
        self.member.write_text('sealed synthetic header')
        (self.logical / 'baseline').symlink_to(self.member.parent,
                                               target_is_directory=True)
        self.manifest = self.current / 'current-inputs.json'
        (self.logical / self.manifest.name).symlink_to(self.manifest)
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        import fs_host_dependencies
        import source_paths
        self.stack.enter_context(patch.object(home, 'ROOT', self.public))
        self.stack.enter_context(
            patch.object(source_paths, 'ROOT', self.public))
        self.stack.enter_context(patch.object(fs_host_dependencies, 'ROOT',
                                              self.public))
        self.stack.enter_context(patch.dict(os.environ, {
            fs_host_dependencies.ENV: str(self.retained)}))
        self.manifest_pin = self.stack.enter_context(patch.object(
            home, 'CURRENT_INPUTS_SHA256', '', create=True))
        self.write_manifest({'baseline/header.h': home.digest(self.member)})

    def write_manifest(self, files):
        self.manifest.write_text(json.dumps({'files': files}))
        home.CURRENT_INPUTS_SHA256 = home.digest(self.manifest)

    def test_unknown_absolute_executables_and_make_never_run(self):
        for command in (['/foreign/compiler', '--version'],
                        ['/usr/bin/make'], ['make'], ['clang']):
            with self.subTest(command=command), self.assertRaises(ValueError):
                home.command_arguments(command, self.tools)

    def test_owner_qualifier_accepts_its_explicit_selected_host_tools(self):
        tools = dict(self.tools)
        for name in ('python3', 'xorriso'):
            path = self.out / name
            path.write_text('opaque selected owner tool: ' + name)
            tools[name] = dict(path=str(path), sha256=home.digest(path))
        for name, flag in (('python3', '--version'), ('xorriso', '-version')):
            argv = [tools[name]['path'], flag]
            with self.subTest(name=name):
                self.assertEqual(home.command_arguments(argv, tools), argv)
        for executable in ('/foreign/host-tool', '/usr/bin/make'):
            with self.subTest(executable=executable):
                with self.assertRaises(ValueError):
                    home.command_arguments([executable], tools)

    def test_actual_selected_tool_bytes_are_checked_for_every_command(self):
        path = Path(self.tools['clang']['path'])
        home.command_arguments([path, '-c', 'fixture.c'], self.tools)
        path.write_text('changed selected compiler')
        with self.assertRaisesRegex(ValueError, 'changed'):
            home.command_arguments([path, '-c', 'fixture.c'], self.tools)

    def test_exact_execution_closure_excludes_unused_provenance_tools(self):
        sdk = {name: self.tools[name] for name in
               ('clang', 'ar', 'lld', 'nm', 'readelf')}
        sdk['make'] = dict(path='/unavailable/old/make', sha256='0' * 64)
        rust = {name: self.tools[name] for name in
                ('clang', 'lld', 'nm', 'readelf', 'rustc', 'clippy-driver')}
        selected = home.execution_tools(sdk, rust, self.tools['zig'])
        self.assertEqual(set(selected), set(self.ROLES))
        self.assertNotIn('make', selected)
        self.assertEqual(sdk['make']['path'], '/unavailable/old/make')
        for mode in ('missing', 'conflict', 'drift'):
            altered = copy.deepcopy(rust)
            if mode == 'missing':
                altered.pop('rustc')
            elif mode == 'conflict':
                altered['clang']['sha256'] = '0' * 64
            else:
                Path(altered['rustc']['path']).write_text('changed compiler')
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                home.execution_tools(sdk, altered, self.tools['zig'])

    def test_current_manifest_routes_actual_members_and_pins_aliases(self):
        inputs, binding = home.current_dependency_inputs()
        self.assertEqual(inputs[str(self.member)], home.digest(self.member))
        self.assertNotIn(str(self.logical / 'baseline/header.h'), inputs)
        self.assertEqual(binding['members']['baseline/header.h'],
                         str(self.member))
        home.verify_dependency_bindings(binding)
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                home.current_dependency_inputs()
        foreign = self.out / 'foreign'
        foreign.mkdir()
        (foreign / 'header.h').write_bytes(self.member.read_bytes())
        alias = self.logical / 'baseline'
        alias.unlink()
        alias.symlink_to(foreign, target_is_directory=True)
        with self.assertRaises(ValueError):
            home.verify_dependency_bindings(binding)

    def test_declared_root_routes_absent_public_manifest_and_members(self):
        (self.logical / self.manifest.name).unlink()
        (self.logical / 'baseline').unlink()
        self.assertFalse((self.logical / self.manifest.name).exists())
        self.assertFalse((self.logical / 'baseline/header.h').exists())
        inputs, binding = home.current_dependency_inputs()
        self.assertEqual(inputs[str(self.member)], home.digest(self.member))
        self.assertEqual(binding['manifest']['path'], str(self.manifest))
        self.assertEqual(binding['members']['baseline/header.h'],
                         str(self.member))
        self.assertEqual(binding['dependency_root'], str(self.retained))
        home.verify_dependency_bindings(binding)

    def test_manifest_rejects_noncanonical_names_and_duplicate_members(self):
        for name in ('', '.', '..', '/absolute', 'baseline/../header.h',
                     'baseline/./header.h', 'baseline//header.h',
                     'baseline\\header.h'):
            self.write_manifest({name: home.digest(self.member)})
            with self.subTest(name=name), self.assertRaises(ValueError):
                home.current_dependency_inputs()
        digest = home.digest(self.member)
        self.manifest.write_text('{"files":{"baseline/header.h":"' + digest +
                                 '","baseline/header.h":"' + digest + '"}}')
        home.CURRENT_INPUTS_SHA256 = home.digest(self.manifest)
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            home.current_dependency_inputs()

    def test_member_manifest_and_alias_drift_during_read_reject(self):
        inputs, binding = home.current_dependency_inputs()
        self.member.write_text('changed header')
        with self.assertRaisesRegex(ValueError, 'changed'):
            home.verify_dependency_bindings(binding)
        self.member.unlink()
        with self.assertRaises(ValueError):
            home.verify_dependency_bindings(binding)
        self.member.write_text('sealed synthetic header')
        read_json = home.read_json

        def changed(path):
            result = read_json(path)
            if Path(path) == self.manifest:
                self.manifest.write_text(self.manifest.read_text() + '\n')
            return result

        with patch.object(home, 'read_json', side_effect=changed):
            with self.assertRaises(ValueError):
                home.current_dependency_inputs()
        self.write_manifest({'baseline/header.h': home.digest(self.member)})
        foreign = self.out / 'during-read'
        foreign.mkdir()
        (foreign / 'header.h').write_bytes(self.member.read_bytes())
        digest = home.digest

        def retarget(path):
            actual = digest(path)
            if Path(path) == self.member:
                alias = self.logical / 'baseline'
                alias.unlink()
                alias.symlink_to(foreign, target_is_directory=True)
            return actual

        with patch.object(home, 'digest', side_effect=retarget):
            with self.assertRaises(ValueError):
                home.current_dependency_inputs()

    def test_imported_tool_drift_preserves_the_actual_stop_record(self):
        stopped = dict(exit=0, complete=True, cleanup='complete')

        def run(*args, **kwargs):
            Path(self.tools['clang']['path']).write_text('changed during run')
            return SimpleNamespace(record=stopped)

        result = {}
        tracked = home.CleanupTrackedProcess(
            SimpleNamespace(run=run), result, tools=self.tools)
        with self.assertRaisesRegex(ValueError, 'changed'):
            tracked.run([self.tools['clang']['path'], '-c', 'fixture.c'])
        self.assertEqual(result['tool_validation_failures'][0]['process'],
                         stopped)
        self.assertFalse(home.process_cleanup_unresolved(result))

    def test_imported_process_uses_the_same_tool_gate(self):
        proc = SimpleNamespace(run=lambda *a, **k: self.fail('runner reached'))
        result = {}
        tracked = home.CleanupTrackedProcess(proc, result, tools=self.tools)
        with self.assertRaises(ValueError):
            tracked.run(['/usr/bin/make'])
        self.assertNotIn('process_cleanup_unresolved', result)
        extra = dict(self.tools, make=self.tools['clang'])
        tracked = home.CleanupTrackedProcess(proc, result, tools=extra)
        with self.assertRaisesRegex(ValueError, 'exact engine'):
            tracked.run([self.tools['clang']['path']])


class EngineCleanup(unittest.TestCase):
    def test_unconfirmed_direct_and_imported_children_retain_owned_outputs(self):
        # Only the host orchestration runs: no compiler, guest or orphan exists.
        for mode in ('rows', 'commands', 'direct', 'raises'):
            for cleanup in ('unresolved', 'not-started'):
                with self.subTest(mode=mode, cleanup=cleanup):
                    self.model_failure(mode, cleanup, retained=True)

    def test_confirmed_stopped_failure_removes_owned_outputs(self):
        self.model_failure('rows', 'complete', retained=False)
        self.model_failure('direct', 'complete', retained=False)

    def test_engine_acceptance_rejects_unconfirmed_imported_outcomes(self):
        for key in ('rows', 'commands'):
            for cleanup in ('unresolved', 'not-started'):
                row = record()
                row.setdefault(key, []).append(dict(status='pass', exit_code=0,
                    process=dict(exit=0, complete=True, cleanup=cleanup)))
                with self.subTest(key=key, cleanup=cleanup), self.assertRaises(ValueError):
                    home.validate_record(row)

    def test_present_imported_process_requires_completion_and_expected_exit(self):
        row=record()
        row['rows']=[dict(expected_exit=1,process=dict(exit=1,complete=True,cleanup='complete'))]
        home.validate_record(row)  # Expected, stopped nonzero controls stay valid.
        for changes in ({'complete':False},{'exit':0},{'exit':-9}):
            bad=copy.deepcopy(row);bad['rows'][0]['process'].update(changes)
            with self.subTest(changes=changes),self.assertRaises(ValueError):home.validate_record(bad)
        summary=record();summary['rows']=[dict(label='historical summary, no process')]
        home.validate_record(summary)

    def test_unconfirmed_cleanup_survives_failure_receipt_write_error(self):
        self.model_failure('rows', 'unresolved', retained=True, receipt_error=True)

    def model_failure(self, mode, cleanup, retained, receipt_error=False):
        with tempfile.TemporaryDirectory(prefix='af09-engine-cleanup-model-') as folder:
            root = Path(folder); (root/'userland/build').mkdir(parents=True)
            destination = root/'fs-launch-af09-test'
            primary = ValueError('original modeled build rejection')
            state = {}
            process = dict(exit=1, complete=False, cleanup=cleanup)
            def run(*args, **kwargs):
                if mode == 'raises': raise primary
                return SimpleNamespace(returncode=1, stdout=b'', stderr=b'modeled rejection', record=process)
            proc = SimpleNamespace(clean_env=lambda work: {}, run=run)
            def imported(work, runner, tools, deadline, result):
                state.update(work=work.parent, result=result)
                (destination/'potentially-live-output').write_bytes(b'owned model')
                if mode in ('rows', 'commands'):
                    result[mode].append(dict(process=process))
                    raise primary
                if mode == 'raises': runner.run(['/modeled/tool'])
                return dict(service=work/'modeled.o')
            def prepare(stage, command, tools, **kwargs):
                command(['/modeled/tool'], stage.parent/'child.log')
                raise AssertionError('nonzero child was accepted')
            def read(path):
                if Path(path).name == 'current-inputs.json': return dict(files={})
                return dict(tools={name: dict(path='/modeled/tool', sha256='1'*64)
                                  for name in home.EXECUTION_ROLES})
            real_write = Path.write_text
            def write(path, body, *args, **kwargs):
                if receipt_error and path.parent.name == 'engine':
                    raise OSError('modeled receipt publication failure')
                return real_write(path, body, *args, **kwargs)
            with ExitStack() as stack:
                for obj, name, value in ((home, 'ROOT', root), (home, 'SOURCE', root/'source')):
                    stack.enter_context(patch.object(obj, name, value))
                for name, kwargs in {
                    'checked_receipt': dict(return_value=({}, {})),
                    'generated_sources': dict(return_value={}),
                    'current_dependency_inputs': dict(return_value=({}, {})),
                    'verify_inputs': dict(side_effect=lambda data: data),
                    'digest': dict(return_value='1'*64), 'read_json': dict(side_effect=read),
                    'prepare_base': dict(side_effect=prepare),
                }.items(): stack.enter_context(patch.object(home, name, **kwargs))
                stack.enter_context(patch('deps.verify'))
                stack.enter_context(patch('fs_launch.validate_destination', return_value=destination))
                stack.enter_context(patch.object(home.shutil, 'which', return_value='/modeled/tool'))
                stack.enter_context(patch('importlib.util.spec_from_file_location'))
                stack.enter_context(patch('importlib.util.module_from_spec', return_value=proc))
                stack.enter_context(patch.object(home.runpy, 'run_path', return_value={'build': imported}))
                stack.enter_context(patch.object(Path, 'write_text', write))
                with self.assertRaises((ValueError, RuntimeError)) as caught:
                    home.build(destination, root/'producer', root/'probe')
            if mode in ('rows', 'commands', 'raises'): self.assertIs(caught.exception, primary)
            self.assertEqual(state['work'].exists(), retained)
            self.assertEqual(destination.exists(), retained)
            if retained:
                self.assertEqual(state['result']['status'], 'failed')
                self.assertEqual(state['result']['cleanup']['status'], 'unresolved')
                self.assertIn(str(state['work']), state['result']['cleanup']['retained_paths'])
                self.assertIn(str(destination), state['result']['cleanup']['retained_paths'])
                self.assertFalse((destination/'SHA256SUMS').exists())
            else:
                self.assertEqual(state['result']['cleanup']['owned_work'], 'removed')
