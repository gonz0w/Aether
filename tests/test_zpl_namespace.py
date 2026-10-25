# SPDX-License-Identifier: BSD-2-Clause
"""Namespace batch admission/ordering; host doubles never qualify native storage."""
import ast
import copy
import hashlib
import inspect
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

import test_zpl_pair as controls
import native_smoke as native
import openzfs_elapsed as elapsed
import openzfs_mutation as mutation
import openzfs_namespace as media
import openzfs_volume as volume
import service_runtime_smoke as runtime
import zpl_namespace as batch
import zpl_pair as pair

ROOT = pair.ROOT


class NamespaceControls(unittest.TestCase):
    def test_profiles_and_fixed_sources_reject_ambiguous_intake(self):
        for operation in (True, 1, '', 'mkdir', 'CREATE'):
            for function, args, option in ((volume.build, (None, None, None), 'pool_namespace_mutation'),
                    (elapsed.prepare, (None, None), 'volume_namespace_mutation'),
                    (runtime.suite, (None,), '_zpl_namespace_mutation')):
                with self.subTest(operation=operation), self.assertRaises(ValueError):
                    function(*args, **{option: operation})
        for operation in mutation.OPERATIONS:
            for function, args, option in ((volume.build, (None, None, None), 'pool_namespace_mutation'),
                    (elapsed.prepare, (None, None), 'volume_namespace_mutation'),
                    (runtime.suite, (None,), '_zpl_namespace_mutation')):
                with self.assertRaisesRegex(ValueError, 'namespace mutation'):
                    function(*args, **{option: operation})
            self.assertNotEqual(mutation.source_sha(operation, False), mutation.source_sha(operation, True))
            self.assertIn('MNS_KIND ' + str(mutation.OPERATIONS.index(operation) + 1), mutation.source(operation, False))
        for operation, reader in ((None, False), ('create', 1), ('create', None)):
            with self.assertRaises(ValueError): mutation.source(operation, reader)

    def test_prepared_operation_role_source_and_real_kernel_budget_are_required(self):
        f = controls.PairControls(); f.setUp(); self.addCleanup(f.doCleanups)
        shutil.copytree(f.output / 'reader', f.output / 'baseline')
        f.builds['baseline'] = copy.deepcopy(f.builds['reader'])
        f.builds['baseline']['pool_zpl_recover'] = False
        f.builds['writer'].update(pool_zpl_writer_budget=True,
            commands=[{'argv': ['zig', 'build', '-Dnative-service-zpl-budget=true']}])
        f.builds['reader'].update(pool_recovery_writer_60s=True, pool_recovery_diagnostic=True)
        options = dict(writer_ticks_6000=True, recovery_diagnostic=True, writer_60s=True)
        with patch.object(runtime, 'sealed'):
            for operation in mutation.OPERATIONS:
                for role in ('writer', 'reader'):
                    f.builds[role]['namespace_mutation'] = operation
                    label = (ROOT / 'user/storage/openzfs-volume/namespace-label.inc').read_text()
                    if role == 'reader' or operation in ('rename', 'remove'):
                        label = media.recovery_label_source(label)
                    f.builds[role]['port'] = {'volume': {'namespace_objects': {
                        'mutation-selected-source': mutation.source_sha(operation, role == 'reader'),
                        'mutation-label-source': hashlib.sha256(label.encode()).hexdigest()}}}
                pair.verify_prepared(f.output, f.builds, namespace_mutation=operation, **options)
                for role in ('baseline', 'writer', 'reader'):
                    changed = copy.deepcopy(f.builds)
                    changed[role]['namespace_mutation'] = 'remove' if operation != 'remove' else 'create'
                    with self.assertRaises(ValueError):
                        pair.verify_prepared(f.output, changed, namespace_mutation=operation, **options)
                changed = copy.deepcopy(f.builds)
                changed['reader']['port']['volume']['namespace_objects']['mutation-selected-source'] = mutation.source_sha(operation, False)
                with self.assertRaisesRegex(ValueError, 'selected source'):
                    pair.verify_prepared(f.output, changed, namespace_mutation=operation, **options)
                changed = copy.deepcopy(f.builds)
                changed['writer']['port']['volume']['namespace_objects']['mutation-label-source'] = 'drift'
                with self.assertRaisesRegex(ValueError, 'label source'):
                    pair.verify_prepared(f.output, changed, namespace_mutation=operation, **options)
                for key in options:
                    with self.assertRaises(ValueError):
                        pair.verify_prepared(f.output, f.builds, namespace_mutation=operation, **(options | {key: False}))

    def test_actual_pool_builder_routes_seeded_writers_to_newer_exported_labels(self):
        tree = ast.parse(inspect.getsource(volume.build))
        call, = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and
                 isinstance(n.func, ast.Name) and n.func.id == 'build_pool_objects']
        selection, = [k.value for k in call.keywords if k.arg == 'namespace_recovery']
        for operation in (None, *mutation.OPERATIONS):
            for reader in (False, True):
                actual = eval(compile(ast.Expression(selection), '<actual label selection>', 'eval'),
                              {'pool_zpl_recover': reader, 'pool_namespace_mutation': operation})
                self.assertIs(actual, reader or operation in ('rename', 'remove'))

    def test_newer_label798_reproduces_old_pristine_guard_rejection(self):
        from test_openzfs_native_namespace import NamespaceRecoveryLabels
        fixture = NamespaceRecoveryLabels
        fixture.setUpClass(); self.addCleanup(fixture.doClassCleanups)
        driver = fixture.out / 'driver.c'
        text = driver.read_text()
        self.assertEqual(text.count('                         788,'), 1)
        driver.write_text(text.replace('                         788,', '                         798,', 1))
        selected = fixture.compile(fixture.body, 'newer798')
        pristine = fixture.compile(fixture.body.replace('txg <= 782 ||', 'txg != 782 ||', 1), 'pristine798')
        self.assertEqual(subprocess.run([str(selected), '0'], capture_output=True, timeout=5).returncode, 0)
        denied = subprocess.run([str(pristine), '0'], capture_output=True, timeout=5)
        self.assertEqual(denied.returncode, 95)
        self.assertIn(b'HOST NAMESPACE LABEL oracle95', denied.stderr)

    def test_original_namespace_origins_cannot_be_missing_substituted_or_duplicate(self):
        node = ast.parse(inspect.getsource(runtime.check_engine_bindings)).body[0]
        stop = next(i for i, item in enumerate(node.body) if isinstance(item, ast.Assign) and
                    any(isinstance(t, ast.Name) and t.id == 'seen' for t in item.targets))
        for operation, names in (
                ('create', ('aether_zpl_create', 'dmu_object_alloc', 'dmu_tx_hold_sa_create', 'sa_replace_all_by_template', 'zap_add')),
                ('rename', ('aether_zpl_rename', 'zap_add', 'zap_remove')),
                ('remove', ('aether_zpl_remove', 'dmu_object_free', 'dmu_tx_hold_free', 'dmu_tx_mark_netfree', 'sa_update', 'zap_remove'))):
            options = dict(pool=True, pool_zpl_write=True, pool_namespace=True, pool_import=True, namespace_mutation=operation)
            scope = {name: parameter.default for name, parameter in inspect.signature(runtime.check_engine_bindings).parameters.items() if name != 'mapping'}
            scope.update(options)
            exec(compile(ast.Module(body=node.body[:stop], type_ignores=[]), '<actual origin requirements>', 'exec'), scope)
            required = scope['required']
            for name in (*names, 'dmu_object_next', 'zap_count'):
                self.assertEqual(required[name], 'selected-engine.o')
            self.assertNotIn('aether_zpl_write', required)
            mapping = '\n'.join('0 0 0 1 /private/' + owner + ':(.text)\n0 0 0 1 ' + name for name, owner in required.items())
            runtime.check_engine_bindings(mapping, **options)
            for name in names:
                for changed in (mapping.replace('0 0 0 1 ' + name + '\n', ''),
                        mapping.replace('/private/selected-engine.o:(.text)\n0 0 0 1 ' + name, '/private/forged.o:(.text)\n0 0 0 1 ' + name),
                        mapping + '\n0 0 0 1 /private/selected-engine.o:(.text)\n0 0 0 1 ' + name):
                    # Exact whole-line deletion also works for final symbols.
                    if changed == mapping:
                        changed = '\n'.join(line for line in mapping.splitlines() if line != '0 0 0 1 ' + name)
                    with self.subTest(operation=operation, name=name), self.assertRaises(ValueError):
                        runtime.check_engine_bindings(changed, **options)

    def test_seeded_writer_requires_exact_owned_role_and_retains_fixed60(self):
        with tempfile.TemporaryDirectory(prefix=pair.PREFIX, dir=ROOT / 'zig-out') as directory:
            root = Path(directory); (root / 'writer').mkdir()
            disk = root / 'native-namespace.raw'
            with disk.open('wb') as stream: stream.truncate(1073750016)
            options = dict(_pair_stop=True, _zpl_writer_60s=True, _zpl_mutation_seed=True,
                zpl_writer={'status': 'pass'}, block_namespace=True, block_large=True,
                block_disk=disk, marker=pair.MARKER.encode())
            image = root / 'writer/aether.iso'
            with patch.object(native, 'verify', side_effect=AssertionError('intake')):
                for changed in ({'_zpl_mutation_seed': 1}, {'zpl_writer': None}, {'_zpl_writer_60s': False},
                        {'_pair_stop': False}, {'marker': b'wrong'}, {'expected_panic': b'x'}):
                    with self.assertRaises(ValueError): native.run(image, **(options | changed))
                with self.assertRaises(ValueError): native.run(root / 'reader/aether.iso', **options)
            process = Mock(); process.poll.return_value = 0
            with patch.object(native, 'verify'), patch.object(native.subprocess, 'check_output', return_value='QEMU emulator version ' + native.LOCK['qemu']), \
                 patch.object(native.subprocess, 'Popen', return_value=process), patch.object(native.shutil, 'copyfile'), \
                 patch.object(runtime, 'check_zpl_recovery_media') as admit, patch.object(native, 'wait_for_boot') as wait:
                native.run(image, **options)
            admit.assert_called_once_with(options['zpl_writer'], disk)
            self.assertEqual(wait.call_args.args[2], 60)

    def test_cli_has_no_user_media_resume_retry_or_budget_override(self):
        for flags in (['--disk', '/dev/disk0'], ['--resume'], ['--writer-60s'], ['--operation', 'rename']):
            result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/zpl_namespace.py'),
                '--delivery', '/absent', '--utc-delivery', '/absent', *flags], capture_output=True, timeout=5)
            self.assertEqual(result.returncode, 64)
            self.assertNotIn(b'[RUNNING]', result.stderr)


class SeedAdmission(unittest.TestCase):
    def setUp(self):
        self.previous = Path(tempfile.mkdtemp(prefix=pair.PREFIX, dir=ROOT / 'zig-out'))
        self.output = Path(tempfile.mkdtemp(prefix=pair.PREFIX, dir=ROOT / 'zig-out'))
        self.addCleanup(shutil.rmtree, self.previous); self.addCleanup(shutil.rmtree, self.output)
        self.sources = {'host-test': 'frozen'}
        self.snapshot = {'sha256': hashlib.sha256(b'owned media').hexdigest(), 'outside_region_canaries_match': True}
        (self.previous / 'native-namespace.raw').write_bytes(b'owned media')
        cases = []
        for role, txg in (('writer', 788), ('reader', 798)):
            (self.previous / role).mkdir()
            path = self.previous / role / 'native-serial.log'; path.write_text(controls.serial(txg))
            row = dict(role=role, status='pass', vm_run_returned=True, serial_sha256=runtime.sha(path), disk_sha256=self.snapshot['sha256'])
            row.update(runtime.check_engine_trace(path.read_text(), pair.MARKER))
            row.update(runtime.check_pool_cleanup_trace(path.read_text()))
            row.update(runtime.check_zpl_write_trace(path.read_text()) if role == 'writer' else runtime.check_zpl_recovery_trace(path.read_text()))
            cases.append(row)
        self.record = dict(status='pass', namespace_mutation='create', vm_stop_confirmed=True,
            fresh_vm_readback_qualified=True, reader_media_unchanged=True, cases=cases,
            sources_manifest_sha256=batch.digest(self.sources))
        self.receipt = self.previous / 'results.json'
        self.save()

    def save(self): self.receipt.write_text(json.dumps(self.record))

    def admit(self, **changes):
        with patch.object(runtime, 'check_zpl_recovery_media', return_value=self.snapshot), \
             patch.object(media, 'written_native_media_snapshot', return_value=self.snapshot):
            return mutation.admit_seed(**(dict(output=self.output, operation='rename', previous=self.previous, sources=self.sources) | changes))

    def test_exact_clean_trace_qualified_pair_is_copied_exclusively(self):
        result = self.admit()
        self.assertEqual(result['previous_operation'], 'create')
        self.assertEqual((self.output / 'native-namespace.raw').read_bytes(), b'owned media')
        with self.assertRaises(FileExistsError): self.admit()

    def test_missing_qualification_drift_and_unowned_paths_never_copy(self):
        original = copy.deepcopy(self.record)
        for field, value in (('status', 'failed'), ('namespace_mutation', 'rename'), ('vm_stop_confirmed', False),
                ('reader_media_unchanged', False), ('fresh_vm_readback_qualified', False), ('sources_manifest_sha256', 'drift')):
            self.record = original | {field: value}; self.save()
            with self.subTest(field=field), self.assertRaises(ValueError): self.admit()
            self.assertFalse((self.output / 'native-namespace.raw').exists())
        self.record = original; self.save()
        for changes in ({'operation': 'create'}, {'previous': self.output}, {'output': Path('/tmp')}, {'sources': {}}):
            with self.assertRaises(ValueError): self.admit(**changes)
        log = self.previous / 'reader/native-serial.log'
        log.write_text(log.read_text().replace('phase=7', 'phase=6', 1))
        with self.assertRaises(ValueError): self.admit()
        self.record['cases'][-1]['serial_sha256'] = runtime.sha(log); self.save()
        with self.assertRaises(ValueError): self.admit()

    def test_predecessor_media_recheck_detects_copy_drift(self):
        with patch.object(runtime, 'check_zpl_recovery_media', side_effect=[self.snapshot, self.snapshot | {'sha256': 'drift'}]), \
             patch.object(media, 'written_native_media_snapshot', return_value=self.snapshot):
            with self.assertRaisesRegex(ValueError, 'copy drift'):
                mutation.admit_seed(self.output, 'rename', self.previous, self.sources)


class BatchOrdering(unittest.TestCase):
    def exercise(self, failure=None, file_sizes=False, eight_writes=False, write_lifetimes=False):
        operations = mutation.LIFETIME_OPERATIONS if write_lifetimes else mutation.EIGHT_OPERATIONS if eight_writes else mutation.SIZE_OPERATIONS if file_sizes else mutation.OPERATIONS
        roots = []; order = []
        before = set((ROOT / 'zig-out').glob('thread-suite-service-runtime-namespace-batch-*'))
        def prepare(*args, **options):
            dest = options['_zpl_stage']; dest.mkdir()
            operation = options['_zpl_namespace_mutation'] or operations[0]
            self.assertIs(options['_zpl_repeat'], operation in ('repeat', 'eight', 'lifetimes') and dest.name == 'writer')
            order.append((operation, dest.name))
            root = Path(tempfile.mkdtemp(prefix='thread-suite-service-runtime-test-', dir=ROOT / 'zig-out')); roots.append(root)
            for name in ('aether.iso', 'engine.elf'): (dest / name).write_bytes(name.encode())
            (dest.parent / (dest.name + '-build.json')).write_text(json.dumps({'output': str(root), 'report': {'status': 'pass', 'sources': {}}}))
        def execute(output, builds, record):
            operation = record['namespace_mutation']
            self.assertEqual(len([item for item in order if item[1] != 'execute']), 7)
            self.assertEqual(record.get('namespace_seed') is None, operation == operations[0])
            if operation != operations[0]:
                previous = json.loads((Path(record['namespace_seed']) / 'results.json').read_text())
                self.assertEqual(previous['namespace_mutation'], operations[operations.index(operation) - 1])
                self.assertEqual(previous['status'], 'pass')
            order.append((operation, 'execute'))
            record['native_attempted'] = True
            (output / 'writer/native-qemu-command.json').write_text(json.dumps({'argv': ['qemu-host-double', operation]}))
            if operation == failure: raise ValueError('controlled failure')
        try:
            with patch.object(runtime, 'suite', side_effect=prepare), patch.object(pair, 'verify_prepared'), \
                 patch.object(pair, 'execute_pair', side_effect=execute):
                if failure:
                    with self.assertRaisesRegex(ValueError, 'controlled failure'): batch.batch(None, None, file_sizes, eight_writes, write_lifetimes)
                else: batch.batch(None, None, file_sizes, eight_writes, write_lifetimes)
            output, = set((ROOT / 'zig-out').glob('thread-suite-service-runtime-namespace-batch-*')) - before
            result = json.loads((output / 'results.json').read_text())
            self.assertEqual(result['status'], 'failed' if failure else 'pass')
            self.assertEqual(result['human_disposition_required'], bool(failure))
            self.assertTrue(result['owned_outputs_disposed'])
            self.assertTrue(all(not root.exists() for root in roots))
            for operation, role in order:
                if role == 'execute':
                    command = result['phases'][operation]['vm_commands']['writer']
                    self.assertEqual(command['argv'], ['qemu-host-double', operation])
                    self.assertEqual(len(command['sha256']), 64)
            return order
        finally:
            for output in set((ROOT / 'zig-out').glob('thread-suite-service-runtime-namespace-batch-*')) - before:
                shutil.rmtree(output)

    def test_seven_preparations_before_create_rename_remove_and_no_retry(self):
        order = self.exercise()
        self.assertEqual(order[-3:], [(operation, 'execute') for operation in mutation.OPERATIONS])
        for operation in mutation.OPERATIONS:
            order = self.exercise(operation)
            self.assertEqual([name for name, role in order if role == 'execute'],
                list(mutation.OPERATIONS[:mutation.OPERATIONS.index(operation) + 1]))




class FileSizeControls(unittest.TestCase):
    def test_size_batch_uses_existing_two_record_witness_only_for_repeat_writer(self):
        f = BatchOrdering(); f.setUp(); self.addCleanup(f.doCleanups)
        order = f.exercise(file_sizes=True)
        self.assertEqual(order[-3:], [(op, 'execute') for op in mutation.SIZE_OPERATIONS])
        for op in mutation.SIZE_OPERATIONS: f.exercise(op, file_sizes=True)
        with self.assertRaises(ValueError): batch.batch(None, None, 1)

    def test_prepared_fixed_size_source_label_and_repeat_selection_are_required(self):
        f = controls.PairControls(); f.setUp(); self.addCleanup(f.doCleanups)
        shutil.copytree(f.output / 'reader', f.output / 'baseline')
        f.builds['baseline'] = copy.deepcopy(f.builds['reader']); f.builds['baseline']['pool_zpl_recover'] = False
        f.builds['writer'].update(pool_zpl_writer_budget=True, commands=[{'argv': ['zig', 'build', '-Dnative-service-zpl-budget=true']}])
        f.builds['reader'].update(pool_recovery_writer_60s=True, pool_recovery_diagnostic=True)
        label = (ROOT / 'user/storage/openzfs-volume/namespace-label.inc').read_text()
        with patch.object(runtime, 'sealed'):
            for op in mutation.SIZE_OPERATIONS + ('eight','lifetimes'):
                options = dict(writer_ticks_6000=True, writer_60s=True, recovery_diagnostic=True,
                               namespace_mutation=op, repeated_writes=op in ('repeat', 'eight', 'lifetimes'))
                for role in ('writer', 'reader'):
                    text = media.recovery_label_source(label) if role == 'reader' or op != 'shrink' else label
                    f.builds[role].update(namespace_mutation=op, pool_zpl_repeat=op in ('repeat', 'eight', 'lifetimes') and role == 'writer',
                        port={'volume': {'namespace_objects': {'mutation-selected-source': mutation.source_sha(op, role == 'reader'),
                                                               'mutation-label-source': hashlib.sha256(text.encode()).hexdigest()}}})
                if op in ('eight','lifetimes'):
                    from openzfs_pool import eight_write_hooks, lifetime_write_hooks
                    hooks = (lifetime_write_hooks if op == 'lifetimes' else eight_write_hooks)((ROOT/'user/storage/openzfs-volume/pool-vdev-hooks.inc').read_text())
                    objects = f.builds['writer']['port']['volume']['namespace_objects']
                    objects['vdev-write-hooks-source'] = hashlib.sha256(hooks.encode()).hexdigest()
                    changed = copy.deepcopy(f.builds)
                    changed['writer']['port']['volume']['namespace_objects']['vdev-write-hooks-source'] = '0'*64
                    with self.assertRaisesRegex(ValueError, 'observer source/count/budget'):
                        pair.verify_prepared(f.output, changed, **options)
                pair.verify_prepared(f.output, f.builds, **options)
                for role in ('writer', 'reader'):
                    changed = copy.deepcopy(f.builds); changed[role]['pool_zpl_repeat'] = not changed[role]['pool_zpl_repeat']
                    with self.assertRaises(ValueError): pair.verify_prepared(f.output, changed, **options)
                with self.assertRaises(ValueError): pair.verify_prepared(f.output, f.builds, **(options | {'repeated_writes': op not in ('repeat', 'eight', 'lifetimes')}))

    def test_actual_label_builder_and_ffi_link_requirements_match_all_size_roles(self):
        tree = ast.parse(inspect.getsource(volume.build))
        call, = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'build_pool_objects']
        expr, = [k.value for k in call.keywords if k.arg == 'namespace_recovery']
        node = ast.parse(inspect.getsource(runtime.check_engine_bindings)).body[0]
        stop = next(i for i,n in enumerate(node.body) if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'seen' for t in n.targets))
        for op in mutation.SIZE_OPERATIONS + ('eight','lifetimes'):
            for reader in (False, True):
                self.assertIs(eval(compile(ast.Expression(expr), '<actual label selection>', 'eval'),
                    dict(pool_zpl_recover=reader, pool_namespace_mutation=op)), reader or op != 'shrink')
            options = dict(pool=True, pool_namespace=True, pool_import=True, pool_zpl_write=True, namespace_mutation=op)
            scope = {n:p.default for n,p in inspect.signature(runtime.check_engine_bindings).parameters.items() if n != 'mapping'}; scope.update(options)
            exec(compile(ast.Module(body=node.body[:stop], type_ignores=[]), '<actual requirements>', 'exec'), scope)
            required = scope['required']
            primitive = 'aether_zpl_write' if op in ('repeat', 'eight', 'lifetimes') else 'aether_zpl_' + op
            names = (primitive, 'dmu_tx_hold_free', 'dmu_free_range') if op == 'shrink' else (primitive, 'dmu_tx_hold_write', 'dmu_write')
            if op == 'lifetimes': names += ('aether_pool_lifetime_retire',)
            for name in names: self.assertEqual(required[name], 'selected-engine.o')
            mapping = '\n'.join('0 0 0 1 /private/' + owner + ':(.text)\n0 0 0 1 ' + name for name, owner in required.items())
            runtime.check_engine_bindings(mapping, **options)
            for name in names:
                changed = '\n'.join(line for line in mapping.splitlines() if line != '0 0 0 1 ' + name)
                with self.assertRaises(ValueError): runtime.check_engine_bindings(changed, **options)

    def test_size_aware_seed_rejects_the_legacy_file_length(self):
        f = SeedAdmission(); f.setUp(); self.addCleanup(f.doCleanups)
        f.record['namespace_mutation'] = 'shrink'
        f.record['cases'][-1]['namespace_bytes_verified'] = 65539; f.save()
        result = f.admit(operation='extend'); self.assertEqual(result['previous_operation'], 'shrink')
        (f.output / 'native-namespace.raw').unlink()
        f.record['cases'][-1]['namespace_bytes_verified'] = 780248; f.save()
        with self.assertRaises(ValueError): f.admit(operation='extend')

    def test_pair_reports_actual_qualified_file_length_and_fixed_writer_dispatch(self):
        for op in mutation.SIZE_OPERATIONS + ('eight','lifetimes'):
            f = controls.PairControls(); f.setUp(); self.addCleanup(f.doCleanups)
            (f.output / 'baseline').mkdir()
            record = dict(cases=[], namespace_mutation=op, writer_ticks_6000=True,
                writer_60s_diagnostic=True, recovery_diagnostic=True, repeated_writes=op in ('repeat', 'eight', 'lifetimes'))
            snapshot = {'sha256': 'b' * 64}; pristine = {'sha256': 'a' * 64}
            seed = {'qualified_writer': {'status': 'pass'}, 'media': snapshot}
            if op != 'shrink': record['namespace_seed'] = '/not-read-by-double'
            launched = []
            def run(image, **kw):
                role = image.parent.name; launched.append((role, kw))
                (image.parent / 'native-serial.log').write_text(controls.baseline_serial() if role == 'baseline' else controls.serial(788 if role == 'writer' else 798))
            with patch.object(pair, 'verify_prepared'), patch.object(pair, 'prepare_native_fixture'), \
                 patch.object(pair, 'native_media_snapshot', return_value=pristine), patch.object(pair, 'written_native_media_snapshot', return_value=snapshot), \
                 patch.object(runtime, 'check_zpl_recovery_media', return_value=snapshot), patch.object(mutation, 'admit_seed', return_value=seed), patch.object(pair, 'run', side_effect=run):
                pair.execute_pair(f.output, f.builds, record)
            self.assertTrue(record['fresh_vm_readback_qualified'])
            self.assertEqual([c['namespace_bytes_verified'] for c in record['cases'][-2:]], [mutation.FILE_BYTES[op]] * 2)
            writer = next(kw for role,kw in launched if role == 'writer')
            self.assertTrue(writer['_zpl_writer_60s'])
            self.assertEqual(writer.get('_zpl_mutation_seed', False), op != 'shrink')


class EightControls(unittest.TestCase):
    def test_eight_batch_all_prepared_stop_ordering_and_exclusive_fixed_flags(self):
        f=BatchOrdering();f.setUp();self.addCleanup(f.doCleanups)
        order=f.exercise(eight_writes=True)
        self.assertEqual(order[-3:],[(op,'execute') for op in mutation.EIGHT_OPERATIONS])
        for op in mutation.EIGHT_OPERATIONS:f.exercise(op,eight_writes=True)
        for args in ((True,True),(False,1),(1,False)):
            with self.assertRaises(ValueError):batch.batch(None,None,*args)
        p=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/zpl_namespace.py'),'--file-sizes','--eight-writes',
            '--delivery','/missing','--utc-delivery','/missing'],capture_output=True,text=True,timeout=5)
        self.assertEqual(p.returncode,64)

    def test_eight_seed_requires_recovered_extension_length_and_no_repeat_predecessor(self):
        f=SeedAdmission();f.setUp();self.addCleanup(f.doCleanups)
        f.record['namespace_mutation']='extend'
        f.record['cases'][-1]['namespace_bytes_verified']=69635;f.save()
        self.assertEqual(f.admit(operation='eight')['previous_operation'],'extend')
        (f.output/'native-namespace.raw').unlink()
        f.record['namespace_mutation']='repeat';f.save()
        with self.assertRaises(ValueError):f.admit(operation='eight')


class LifetimeControls(unittest.TestCase):
    def test_lifetime_batch_fixed_eight_workload_and_failure_stop_with_exclusive_flags(self):
        f=BatchOrdering();f.setUp();self.addCleanup(f.doCleanups)
        order=f.exercise(write_lifetimes=True)
        self.assertEqual(order[-3:],[(op,'execute') for op in mutation.LIFETIME_OPERATIONS])
        for op in mutation.LIFETIME_OPERATIONS:f.exercise(op,write_lifetimes=True)
        for opts in ({'file_sizes':True,'write_lifetimes':True},{'eight_writes':True,'write_lifetimes':True},{'write_lifetimes':1}):
            with self.assertRaises(ValueError):batch.batch(None,None,**opts)

    def test_lifetime_seed_admits_only_the_recovered_extension(self):
        f=SeedAdmission();f.setUp();self.addCleanup(f.doCleanups)
        f.record['namespace_mutation']='extend';f.record['cases'][-1]['namespace_bytes_verified']=69635;f.save()
        self.assertEqual(f.admit(operation='lifetimes')['previous_operation'],'extend')
        (f.output/'native-namespace.raw').unlink();f.record['namespace_mutation']='eight';f.save()
        with self.assertRaises(ValueError):f.admit(operation='lifetimes')

    def test_retirement_error_projection_is_strictly_profile_scoped(self):
        values=b'BIUVWLPabcdefghOAMTE'+bytes([10])+bytes([16,0,0,0])
        lines=[f'NATIVE observation slot=0 generation=1 offset={i*8} byte={v}' for i,v in enumerate(values)]
        text='\n'.join(lines+['NATIVE terminal slot=0 generation=1 kind=1 detail=873',
            'NATIVE CLEANUP v=1 slot=0 generation=1 phase=1 selected=0 pages=8192 reclaimed=0',
            'NATIVE CLEANUP v=1 slot=0 generation=1 phase=2 selected=2 pages=8192 reclaimed=0',
            'NATIVE supervisor result=401 reclaimed=0',''])
        result=pair.decode_zpl_error(text,write_lifetimes=True)
        self.assertEqual((result['stage'],result['operation'],result['errno']),(10,'record-retirement',16))
        self.assertNotIn('fresh_vm_readback_qualified',result)
        self.assertEqual(pair.decode_zpl_error(text,recovery=True)['operation'],'metadata-size')
        for opts in ({},{'recovery':True,'write_lifetimes':True},{'write_lifetimes':1}):
            with self.assertRaises(ValueError):pair.decode_zpl_error(text,**opts)


if __name__ == '__main__':
    unittest.main()
