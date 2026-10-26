# SPDX-License-Identifier: BSD-2-Clause
"""Pair admission/ordering/failure controls; doubles cannot qualify a native run."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import native_smoke
import service_runtime_smoke as runtime
import zpl_pair as pair


def serial(txg=788):
    lines = []
    for generation in (1, 2, 3):
        phases = b'BIUVWLPabcdefghOAMT' + txg.to_bytes(8, 'little') + b'SDJFR' if generation == 1 else b'BNR'
        lines += [f'NATIVE observation slot=0 generation={generation} offset={i*8} byte={b}'
                  for i, b in enumerate(phases)]
        lines.append(f'NATIVE terminal slot=0 generation={generation} kind=1 detail=0')
        lines += [f'NATIVE CLEANUP v=1 slot=0 generation={generation} phase={phase} '
                  f'selected={0 if phase == 1 else 2} pages=8192 '
                  f'reclaimed={generation if phase == 7 else generation-1}' for phase in range(1, 8)]
    return '\n'.join(lines + ['NATIVE supervisor result=100 reclaimed=3', pair.MARKER, ''])


def baseline_serial():
    text = serial()
    lines = [line for line in text.splitlines() if not line.startswith('NATIVE observation slot=0 generation=1 ')]
    rows = [f'NATIVE observation slot=0 generation=1 offset={i*8} byte={b}'
            for i, b in enumerate(b'BIUVWLPabcdefghOAMZDJFR')]
    return '\n'.join(rows + lines) + '\n'


class PairControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=pair.PREFIX, dir=ROOT / 'zig-out')
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name)
        self.builds = {}
        for role in ('writer', 'reader'):
            directory = self.output / role
            directory.mkdir()
            for name in ('aether.iso', 'engine.elf'):
                (directory / name).write_bytes((role + name).encode())
            artifacts = {name: runtime.sha(directory / name) for name in ('aether.iso', 'engine.elf')}
            self.builds[role] = dict(status='pass', pool_diagnose='build', pool_namespace=True,
                namespace_ipc=False, pool_zpl_write=role == 'writer', pool_zpl_recover=role == 'reader',
                delivery_seal=runtime.FIXED_SEAL, utc_delivery_seal=runtime.FIXED_UTC_SEAL,
                sources={'scripts/zpl_pair.py': runtime.sha(ROOT / 'scripts/zpl_pair.py')},
                tools={'python': {'path': sys.executable, 'sha256': runtime.sha(sys.executable)}},
                dependency_files={'OWNER.md': runtime.sha(ROOT / '.deps/native-service-runtime-v3/OWNER.md')},
                cases=[dict(name='pool-import', status='build-only', engine_entry_executed=False,
                            kernel_profile='AENBD002/ABI14', staged_artifacts=artifacts,
                            iso_sha256=artifacts['aether.iso'], elf_sha256=artifacts['engine.elf'])])

    def test_both_profiles_actual_hashes_sources_tools_and_runtime_are_required(self):
        with patch.object(runtime, 'sealed') as seal:
            pair.verify_prepared(self.output, self.builds)
            self.assertEqual(seal.call_count, 2)
            for role in ('writer', 'reader'):
                for key, value in (('status', 'failed'), ('pool_zpl_write', None),
                                   ('pool_zpl_recover', None), ('namespace_ipc', True),
                                   ('delivery_seal', 'drift'), ('cases', []), ('sources', {}),
                                   ('tools', {}), ('dependency_files', {})):
                    changed = copy.deepcopy(self.builds)
                    changed[role][key] = value
                    with self.subTest(role=role, key=key), self.assertRaises(ValueError):
                        pair.verify_prepared(self.output, changed)
                for key in ('sources', 'tools', 'dependency_files'):
                    changed = copy.deepcopy(self.builds)
                    if key == 'tools':
                        changed[role][key]['python']['sha256'] = 'drift'
                    else:
                        field = next(iter(changed[role][key]))
                        changed[role][key][field] = 'drift'
                        if key == 'sources':
                            changed['reader' if role == 'writer' else 'writer'][key][field] = 'drift'
                    with self.subTest(role=role, key=key), self.assertRaises(ValueError):
                        pair.verify_prepared(self.output, changed)
            for role in ('writer', 'reader'):
                path = self.output / role / 'aether.iso'
                original = path.read_bytes()
                path.write_bytes(b'drift')
                with self.assertRaisesRegex(ValueError, 'artifact drift'):
                    pair.verify_prepared(self.output, self.builds)
                path.unlink(); path.symlink_to(self.output / role / 'engine.elf')
                with self.assertRaisesRegex(ValueError, 'artifact drift'):
                    pair.verify_prepared(self.output, self.builds)
                path.unlink(); path.write_bytes(original)
            with self.assertRaises(ValueError):
                pair.verify_prepared(self.output, {'writer': self.builds['writer']})

    def test_declared_runtime_root_preserves_default_alias_member_and_hash_guards(self):
        import os
        import fs_host_dependencies as dependencies
        # Synthetic dependency bytes exercise the actual complete pair reader;
        # only later sealed SDK checks are mocked, and no target is executed.
        canonical = self.output / '.deps/native-service-runtime-v3'
        original = self.output / 'retained'
        retained = original / '.deps/native-service-runtime-v3'
        retained.mkdir(parents=True);canonical.parent.mkdir()
        member = retained / 'OWNER.md';member.write_bytes(b'synthetic retained member\n')
        canonical.symlink_to(retained, target_is_directory=True)
        builds = copy.deepcopy(self.builds)
        for build in builds.values():
            build['sources'] = {str(ROOT / 'scripts/zpl_pair.py'): runtime.sha(ROOT / 'scripts/zpl_pair.py')}
            build['dependency_files'] = {'OWNER.md': runtime.sha(member)}
        with patch.object(pair, 'ROOT', self.output), patch.object(dependencies, 'ROOT', self.output), patch.object(runtime, 'sealed'):
            with patch.dict(os.environ, {}, clear=False):
                os.environ.pop(dependencies.ENV, None)
                with self.assertRaisesRegex(ValueError, 'runtime drift'):
                    pair.verify_prepared(self.output, builds)
            with patch.dict(os.environ, {dependencies.ENV: str(original)}):
                pair.verify_prepared(self.output, builds)
                resolve = Path.resolve
                def foreign(path, *args, **kwargs):
                    return original / 'foreign' if path == canonical else resolve(path, *args, **kwargs)
                with patch.object(Path, 'resolve', foreign), self.assertRaisesRegex(ValueError, 'alias target'):
                    pair.verify_prepared(self.output, builds)
                linked = retained / 'linked';linked.symlink_to(member)
                (retained / 'linked-directory').symlink_to(retained, target_is_directory=True)
                for name in ('linked', 'linked-directory/OWNER.md'):
                    changed = copy.deepcopy(builds);changed['writer']['dependency_files'] = {name: runtime.sha(member)}
                    with self.assertRaisesRegex(ValueError, 'runtime drift'):
                        pair.verify_prepared(self.output, changed)
                escaped = original / 'outside';escaped.write_bytes(member.read_bytes())
                (retained / 'escape-link').symlink_to(escaped)
                changed = copy.deepcopy(builds);changed['writer']['dependency_files'] = {'escape-link': runtime.sha(member)}
                with self.assertRaisesRegex(ValueError, 'runtime member path'):
                    pair.verify_prepared(self.output, changed)
                member.write_bytes(b'drift')
                with self.assertRaisesRegex(ValueError, 'runtime drift'):
                    pair.verify_prepared(self.output, builds)

    def test_runtime_member_names_cannot_escape_capsule(self):
        import os
        import fs_host_dependencies as dependencies
        dependency = self.output / '.deps/native-service-runtime-v3'
        dependency.mkdir(parents=True)
        member = dependency / 'OWNER.md';member.write_bytes(b'synthetic retained member\n')
        escaped = dependency.parent / 'escaped';escaped.write_bytes(member.read_bytes())
        builds = copy.deepcopy(self.builds)
        for build in builds.values():
            build['sources'] = {str(ROOT / 'scripts/zpl_pair.py'): runtime.sha(ROOT / 'scripts/zpl_pair.py')}
            build['dependency_files'] = {'OWNER.md': runtime.sha(member)}
        with patch.object(pair, 'ROOT', self.output), patch.object(dependencies, 'ROOT', self.output), patch.object(runtime, 'sealed'), patch.dict(os.environ, {}, clear=False):
            os.environ.pop(dependencies.ENV, None)
            pair.verify_prepared(self.output, builds)
            for name in ('../escaped', str(escaped), '', '.', None):
                changed = copy.deepcopy(builds);changed['writer']['dependency_files'] = {name: runtime.sha(member)}
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'runtime member path'):
                    pair.verify_prepared(self.output, changed)

    def execute(self, writer_text=None, reader_text=None, launch_error=None, drift=False, final_drift=False, stage_diagnostic=False, first_write_diagnostic=False, txg_worker_diagnostic=False, baseline_text=None, sync_stages=False, writer_60s=False, writer_ticks_6000=False, filesystem_bridge=None):
        if txg_worker_diagnostic or filesystem_bridge is not None:
            (self.output / "baseline").mkdir(exist_ok=True)
        record = {'cases': [], 'native_attempted': False, 'stage_diagnostic': stage_diagnostic or first_write_diagnostic or txg_worker_diagnostic,
                  'first_write_diagnostic': first_write_diagnostic, 'txg_worker_diagnostic': txg_worker_diagnostic, 'sync_stages': sync_stages, 'writer_60s_diagnostic': writer_60s, 'writer_ticks_6000': writer_ticks_6000,
                  'repeated_writes': stage_diagnostic or first_write_diagnostic or txg_worker_diagnostic,
                  'filesystem_bridge': filesystem_bridge}
        count = []
        pristine = {'sha256': 'a'*64, 'outside_region_canaries_match': True}
        written = {'sha256': 'b'*64, 'outside_region_canaries_match': True}
        def launch(image, **kwargs):
            role = image.parent.name
            count.append(role)
            if role == 'reader':
                self.assertTrue(kwargs['zpl_writer']['vm_run_returned'])
                self.assertEqual(kwargs['zpl_writer']['status'], 'pass')
            if launch_error:
                raise launch_error
            text = (writer_text if writer_text is not None else serial()) if role == 'writer' else (
                reader_text if reader_text is not None else serial(789))
            if role == 'baseline':
                text = baseline_text if baseline_text is not None else baseline_serial()
            (image.parent / 'native-serial.log').write_text(text)
        def admitted(writer, disk):
            if drift:
                raise ValueError('sealed hash mismatch')
            self.assertEqual(writer['disk_sha256'], written['sha256'])
            return written
        self.record, self.launched = record, count
        with patch.object(pair, 'verify_prepared', side_effect=[None] * (4 if txg_worker_diagnostic or filesystem_bridge is not None else 3) + [
                 ValueError('final source drift') if final_drift else None]), \
             patch.object(pair, 'prepare_native_fixture', return_value={}), \
             patch.object(pair, 'native_media_snapshot', return_value=pristine), \
             patch.object(pair, 'written_native_media_snapshot', return_value=written), \
             patch.object(runtime, 'check_zpl_recovery_media', side_effect=admitted), \
             patch.object(pair, 'run', side_effect=launch):
            pair.execute_pair(self.output, self.builds, record)
        return record

    def test_real_trace_oracles_require_two_clean_outcomes_and_matching_media(self):
        result = self.execute()
        self.assertEqual(self.launched, ['writer', 'reader'])
        self.assertTrue(result['fresh_vm_readback_qualified'])
        self.assertEqual(result['assigned_target_txg'], 788)
        self.assertEqual(result['recovered_pool_txg'], 789)
        self.assertTrue(result['reader_media_unchanged'])

    def test_writer_failures_never_launch_reader_or_accept_progress(self):
        for text in (serial().replace('detail=0', 'detail=873', 1),
                     serial().replace('phase=7', 'phase=6', 1),
                     serial().replace('offset=216 byte=83', 'offset=216 byte=90'),
                     serial().replace(pair.MARKER, ''), serial(782)):
            with self.subTest(text=text[-100:]), self.assertRaises(ValueError):
                self.execute(writer_text=text)
            self.assertEqual(self.launched, ['writer'])
            self.assertNotIn('fresh_vm_readback_qualified', self.record)
        with self.assertRaisesRegex(RuntimeError, 'guest timeout'):
            self.execute(launch_error=RuntimeError('guest timeout'))
        self.assertEqual(self.launched, ['writer'])

    def test_media_drift_prevents_reader_and_old_txg_prevents_pair_acceptance(self):
        with self.assertRaisesRegex(ValueError, 'sealed hash'):
            self.execute(drift=True)
        self.assertEqual(self.launched, ['writer'])
        with self.assertRaises(ValueError):
            self.execute(reader_text=serial(787))
        self.assertEqual(self.launched, ['writer', 'reader'])
        self.assertNotIn('fresh_vm_readback_qualified', self.record)

    def test_final_source_check_precedes_any_pair_qualification(self):
        with self.assertRaisesRegex(ValueError, 'final source drift'):
            self.execute(final_drift=True)
        self.assertEqual(self.launched, ['writer', 'reader'])
        self.assertNotIn('fresh_vm_readback_qualified', self.record)

    def test_staging_refuses_unowned_symlink_reused_or_wrong_profile_before_intake(self):
        with patch.object(runtime, 'intake', side_effect=AssertionError('no intake')):
            for stage, options in ((self.output / 'writer', {}),
                                   (Path('/tmp/writer'), {'pool_zpl_write': True}),
                                   (self.output / 'reader', {'pool_zpl_write': True})):
                with self.assertRaises(ValueError):
                    runtime.suite(Path('/absent'), pool_namespace=True, pool_diagnose='build',
                                  _zpl_stage=stage, **options)
        source = self.output / 'source'; source.mkdir()
        (source / 'aether.iso').write_bytes(b'iso')
        engine = source / 'engine'; engine.write_bytes(b'elf')
        row = dict(iso_sha256=runtime.sha(source / 'aether.iso'), elf_sha256=runtime.sha(engine))
        with self.assertRaises(ValueError):
            runtime.stage_zpl_image(self.output / 'writer', source, engine, row)
        shutil_target = self.output / 'writer'
        for p in shutil_target.iterdir(): p.unlink()
        shutil_target.rmdir()
        shutil_target.symlink_to(source, target_is_directory=True)
        with self.assertRaises(ValueError):
            runtime.stage_zpl_image(shutil_target, source, engine, row)
        shutil_target.unlink()
        staged = runtime.stage_zpl_image(shutil_target, source, engine, row)
        self.assertEqual(staged, {'aether.iso': row['iso_sha256'], 'engine.elf': row['elf_sha256']})

    def test_pair_build_failure_starts_no_vm_and_prepares_both_before_execution(self):
        order = []
        roots = []
        def build(*args, **kwargs):
            role = Path(kwargs['_zpl_stage']).name
            order.append(role)
            root = Path(tempfile.mkdtemp(prefix='thread-suite-service-runtime-test-', dir=ROOT/'zig-out'))
            roots.append(root)
            (root / 'build.log').write_text('compact build log\n')
            (Path(kwargs['_zpl_stage']).parent / (role + '-build.json')).write_text(json.dumps(
                {'output': str(root), 'report': {'status': 'pass'}}))
        def execute(*args):
            self.assertEqual(order, ['writer', 'reader'])
            order.append('execute')
        with patch.object(runtime, 'suite', side_effect=build), \
             patch.object(pair, 'execute_pair', side_effect=execute):
            output = pair.pair(Path('/not-read'), Path('/not-read'))
        try:
            self.assertEqual(order, ['writer', 'reader', 'execute'])
            self.assertTrue(all(not root.exists() for root in roots))
            self.assertEqual(json.loads((output/'results.json').read_text())['status'], 'pass')
            self.assertFalse(list(output.rglob('*.iso')))
        finally:
            import shutil
            shutil.rmtree(output)
        with patch.object(runtime, 'suite', side_effect=ValueError('build failed')), \
             patch.object(pair, 'execute_pair') as execute:
            before = set((ROOT/'zig-out').glob(pair.PREFIX+'*'))
            with self.assertRaisesRegex(ValueError, 'build failed'):
                pair.pair(Path('/not-read'), Path('/not-read'))
            execute.assert_not_called()
            for output in set((ROOT/'zig-out').glob(pair.PREFIX+'*')) - before:
                report = json.loads((output/'results.json').read_text())
                self.assertFalse(report['native_attempted'])
                import shutil
                shutil.rmtree(output)

    def test_cli_rejects_user_disk_and_partial_resume(self):
        for flags in (['--disk', '/dev/disk0'], ['--reader-only'], ['--retain-outputs']):
            result = subprocess.run([sys.executable, '-B', str(ROOT/'scripts/zpl_pair.py'),
                '--delivery', '/absent', '--utc-delivery', '/absent', *flags],
                capture_output=True, timeout=5)
            self.assertEqual(result.returncode, 64)
            self.assertNotIn(b'[RUNNING]', result.stderr)
        result = subprocess.run([sys.executable, '-B', str(ROOT/'scripts/zpl_pair.py'),
            '--delivery', '/absent', '--utc-delivery', '/absent', '--bad\x1b\rNAME'],
            capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 64)
        self.assertNotIn(b'\x1b', result.stderr)
        self.assertNotIn(b'\r', result.stderr)
        self.assertIn(b'\\x1b\\x0dNAME', result.stderr)

    def test_error_decoder_never_promotes_failed_progress_to_qualification(self):
        def trace(stage=6, error=5):
            values = b'BIUVWLPabcdefghOAMTE' + bytes([stage]) + error.to_bytes(4, 'little')
            lines = [f'NATIVE observation slot=0 generation=1 offset={i*8} byte={v}' for i,v in enumerate(values)]
            return '\n'.join(lines + ['NATIVE terminal slot=0 generation=1 kind=1 detail=873',
                'NATIVE CLEANUP v=1 slot=0 generation=1 phase=1 selected=0 pages=8192 reclaimed=0',
                'NATIVE CLEANUP v=1 slot=0 generation=1 phase=2 selected=2 pages=8192 reclaimed=0',
                'NATIVE supervisor result=401 reclaimed=0', 'AETHER PANIC: native C profile rejected', ''])
        for stage, operation in enumerate(pair.ERROR_STAGES, 1):
            result = pair.decode_zpl_error(trace(stage))
            self.assertEqual(result['operation'], operation)
            self.assertEqual(result['errno'], 5)
            self.assertNotIn('fresh_vm_readback_qualified', result)
        valid = trace()
        for changed in (trace(0), trace(10), trace(error=0), trace(error=4096),
                        valid.replace('byte=5', 'byte=256'),
                        valid.replace('offset=0', 'offset=8', 1),
                        valid.replace('detail=873', 'detail=0'),
                        valid.replace('phase=2', 'phase=3'),
                        valid.replace('generation=1', 'generation=2', 1),
                        valid + pair.MARKER, serial()):
            with self.subTest(changed=changed[-60:]), self.assertRaises(ValueError):
                pair.decode_zpl_error(changed)

    def test_guest_failure_cleans_only_after_confirmed_stop_and_keeps_diagnostics(self):
        import shutil
        for error, stopped in ((RuntimeError('guest timeout'), True),
                               (native_smoke.NativeStopError('unconfirmed'), False)):
            def failed(output, builds, record):
                record['native_attempted'] = True
                record['cases'].append({'role': 'writer', 'status': 'running'})
                (output / 'native-namespace.raw').write_bytes(b'owned model media')
                (output / 'model.iso').write_bytes(b'owned model image')
                raise error
            def build(*args, **kwargs):
                role = Path(kwargs['_zpl_stage']).name
                output = Path(kwargs['_zpl_stage']).parent
                root = Path(tempfile.mkdtemp(prefix='thread-suite-service-runtime-test-', dir=ROOT/'zig-out'))
                (root/'failed-build.log').write_text('short retained diagnostic\n')
                (output/(role+'-build.json')).write_text(json.dumps(
                    {'output': str(root), 'report': {'status': 'pass'}}))
            before = set((ROOT/'zig-out').glob(pair.PREFIX+'*'))
            with patch.object(runtime, 'suite', side_effect=build), \
                 patch.object(pair, 'execute_pair', side_effect=failed), patch.object(pair, 'diagnose'), \
                 patch('openzfs_namespace._native_media_snapshot', return_value={'model': True}):
                with self.assertRaises(type(error)):
                    pair.pair(Path('/not-read'), Path('/not-read'))
            for output in set((ROOT/'zig-out').glob(pair.PREFIX+'*')) - before:
                try:
                    report = json.loads((output/'results.json').read_text())
                    self.assertEqual(report['vm_stop_confirmed'], stopped)
                    self.assertTrue(report['human_disposition_required'])
                    self.assertFalse(report['fresh_vm_readback_qualified'])
                    self.assertEqual((output/'native-namespace.raw').exists(), not stopped)
                    self.assertEqual((output/'model.iso').exists(), not stopped)
                    self.assertTrue((output/'writer-build-logs/failed-build.log').is_file())
                finally:
                    shutil.rmtree(output)


class LauncherControls(unittest.TestCase):
    def test_changed_media_path_still_requires_ownership_and_qualified_writer(self):
        with tempfile.TemporaryDirectory(prefix=pair.PREFIX, dir=ROOT/'zig-out') as directory:
            output = Path(directory); (output/'reader').mkdir()
            disk = output/'native-namespace.raw'
            with disk.open('wb') as stream: stream.truncate(1073750016)
            with patch.object(native_smoke, 'verify', side_effect=RuntimeError('admitted')) as verify, \
                 patch.object(runtime, 'check_zpl_recovery_media', side_effect=ValueError('unclean')) as gate:
                with self.assertRaisesRegex(ValueError, 'unclean'):
                    native_smoke.run(output/'reader/aether.iso', block_disk=disk, block_large=True,
                                     block_namespace=True, zpl_writer={})
                verify.assert_not_called(); gate.assert_called_once()
            with patch.object(native_smoke, 'verify', side_effect=RuntimeError('admitted')), \
                 patch.object(runtime, 'check_zpl_recovery_media') as gate:
                with self.assertRaisesRegex(RuntimeError, 'admitted'):
                    native_smoke.run(output/'reader/aether.iso', block_disk=disk, block_large=True,
                                     block_namespace=True, zpl_writer={'sealed': 'host-double'})
                gate.assert_called_once()
                with self.assertRaises(ValueError):
                    native_smoke.run(output/'reader/aether.iso', zpl_writer={})

    def test_unconfirmed_stop_is_distinct_and_never_cleanup_permission(self):
        process = Mock()
        process.poll.return_value = None
        process.wait.side_effect = subprocess.TimeoutExpired('qemu', 3)
        with tempfile.TemporaryDirectory(prefix=pair.PREFIX, dir=ROOT/'zig-out') as directory:
            output = Path(directory); (output/'reader').mkdir()
            with patch.object(native_smoke, 'verify'), \
                 patch.object(native_smoke.subprocess, 'check_output', return_value='QEMU emulator version '+native_smoke.LOCK['qemu']), \
                 patch.object(native_smoke.subprocess, 'Popen', return_value=process), \
                 patch.object(native_smoke.shutil, 'copyfile'), patch.object(native_smoke, 'wait_for_boot'):
                with self.assertRaises(native_smoke.NativeStopError):
                    native_smoke.run(output/'reader/aether.iso', _pair_stop=True)
            process.terminate.assert_called_once(); process.kill.assert_called_once()
            self.assertEqual(process.wait.call_count, 2)

    def test_default_launcher_keeps_existing_termination_join(self):
        process = Mock()
        process.poll.return_value = None
        process.wait.side_effect = [subprocess.TimeoutExpired('qemu', 3), 0]
        with tempfile.TemporaryDirectory(prefix=pair.PREFIX, dir=ROOT/'zig-out') as directory:
            output = Path(directory); (output/'reader').mkdir()
            with patch.object(native_smoke, 'verify'), \
                 patch.object(native_smoke.subprocess, 'check_output', return_value='QEMU emulator version '+native_smoke.LOCK['qemu']), \
                 patch.object(native_smoke.subprocess, 'Popen', return_value=process), \
                 patch.object(native_smoke.shutil, 'copyfile'), patch.object(native_smoke, 'wait_for_boot'):
                native_smoke.run(output/'reader/aether.iso')
            self.assertEqual(process.wait.call_args_list[0].kwargs, {'timeout': 3})
            self.assertEqual(process.wait.call_args_list[1].kwargs, {})
