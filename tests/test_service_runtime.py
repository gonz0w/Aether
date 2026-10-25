# SPDX-License-Identifier: BSD-2-Clause
"""Intake rejects corrupted authority inputs and false lifecycle evidence."""
import hashlib
import json
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import shutil
import ast

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from service_runtime_smoke import sealed, check_trace, check_callers, check_engine_bindings, check_engine_trace, check_open_probe_trace, suite, display
from openzfs_elapsed import adapt_runtime
import service_runtime_smoke as runtime


class ServiceRuntime(unittest.TestCase):
    def test_actual_pool_region_expression_attenuates_import_to_read(self):
        tree = ast.parse(Path(runtime.__file__).read_text())
        suite_node = next(node for node in tree.body
                          if isinstance(node, ast.FunctionDef) and node.name == 'suite')
        regions = [node.value for node in ast.walk(suite_node) if isinstance(node, ast.Constant)
                   and isinstance(node.value, str) and node.value.startswith('let region = [8u64, if cfg!(physical_small)')]
        self.assertEqual(len(regions), 1)
        with tempfile.TemporaryDirectory(prefix='aether-pool-region-') as directory:
            output = Path(directory)
            source = output / 'region.rs'
            source.write_text('fn main() { ' + regions[0] +
                              ' let n: u64=std::env::args().nth(1).unwrap().parse().unwrap(); assert_eq!(region,[8,131072,n]); }')
            for label, flags, rights in (
                ('create', ['--cfg', 'pool_create'], 7),
                ('import', ['--cfg', 'pool_create', '--cfg', 'pool_import'], 1)):
                result = subprocess.run(['rustc', '+1.98.0', '--edition=2024', '-Dwarnings',
                                         '-C', 'opt-level=2', *flags, str(source), '-o', str(output/label)],
                                        capture_output=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(subprocess.run([str(output/label), str(rights)], timeout=5).returncode, 0)

    def test_pool_pair_keeps_default_scope_and_readonly_import(self):
        self.assertEqual(runtime.pool_cases(None), ('pool-create',))
        self.assertEqual(runtime.pool_cases('pool-create'), ('pool-create',))
        self.assertEqual(runtime.pool_cases('pool-import'), ('pool-create', 'pool-import'))
        self.assertTrue(runtime.volume_readonly('pool-import'))
        self.assertFalse(runtime.volume_readonly('pool-create'))
        with self.assertRaises(ValueError):
            runtime.pool_cases('unknown')
        with self.assertRaisesRegex(ValueError, 'pool creation requires'):
            runtime.suite(Path('/absent'), case='pool-import')

    def test_pool_import_trace_rejects_missing_mos_export_retirement_and_identity(self):
        phases = b'BIUVWLP????????OAMDJFR'
        records = [(0, 1, i * 8, byte) for i, byte in enumerate(phases)]
        records += [(0, g, i * 8, byte) for g in (2, 3) for i, byte in enumerate(b'BNR')]
        def render(rows):
            return ''.join(f'NATIVE observation slot={s} generation={g} offset={o} byte={b}\n'
                           for s, g, o, b in rows)
        result = runtime.check_pool_import_trace(render(records))
        self.assertTrue(result['readonly_MOS_creation_version_readback'])
        self.assertTrue(result['readonly_pool_retired'])
        self.assertFalse(result['clean_export_observed'])
        for index in (0, 5, 15, 16, 17, 18, 19, 20, 21, 23):
            with self.subTest(index=index):
                missing = records[:index] + records[index + 1:]
                with self.assertRaises(ValueError):
                    runtime.check_pool_import_trace(render(missing))
                wrong = records.copy()
                slot, gen, offset, byte = wrong[index]
                wrong[index] = slot, gen, offset, byte ^ 1
                with self.assertRaises(ValueError):
                    runtime.check_pool_import_trace(render(wrong))
        wrong = records.copy()
        wrong[7] = (0, 2, 56, 0)
        with self.assertRaises(ValueError):
            runtime.check_pool_import_trace(render(wrong))

    def test_pool_data_exact_trace_targets_and_missing_phases(self):
        def render(phases):
            rows = [(0, 1, i * 8, byte) for i, byte in enumerate(phases)]
            rows += [(0, g, i * 8, byte) for g in (2, 3) for i, byte in enumerate(b'BNR')]
            return ''.join(f'NATIVE observation slot={s} generation={g} offset={o} byte={b}\n'
                           for s, g, o, b in rows)
        target = (17).to_bytes(8, 'little')
        create = b'BIUVWP????????CAT' + target + b'SDJFR'
        imported = b'BIUVWLP????????OAMT' + target + b'SDJFR'
        c = runtime.check_pool_create_trace(render(create), True)
        i = runtime.check_pool_import_trace(render(imported), True)
        self.assertEqual(runtime.check_pool_data_pair(c, i)['original_assigned_target_txg'], 17)
        self.assertTrue(c['ordered_provider_witness'])
        self.assertTrue(i['readonly_data_readback'])
        self.assertFalse(i['clean_export_observed'])
        for phases, checker, indices in ((create, runtime.check_pool_create_trace, (14, 15, 16, 25, 26, 27, 28, 29)),
                                        (imported, runtime.check_pool_import_trace, (15, 16, 17, 18, 27, 28, 29, 30, 31))):
            for index in indices:
                with self.subTest(phases=phases[:6], index=index):
                    corrupt = bytearray(phases); corrupt[index] ^= 1
                    with self.assertRaises(ValueError):
                        checker(render(corrupt), True)
                    with self.assertRaises(ValueError):
                        checker(render(phases[:index] + phases[index + 1:]), True)
            with self.assertRaises(ValueError):
                checker(render(phases), False)
        for key in ('assigned_DMU_transaction', 'ordered_provider_witness', 'assigned_target_txg'):
            bad = dict(c); bad[key] = 0
            with self.assertRaises(ValueError): runtime.check_pool_data_pair(bad, i)
        for value in (0, 18):
            bad = dict(i, recovered_target_txg=value)
            with self.assertRaises(ValueError): runtime.check_pool_data_pair(c, bad)
        with self.assertRaises(ValueError):
            runtime.check_pool_data_pair(c, dict(i, readonly_data_readback=False))
        with self.assertRaises(ValueError):
            runtime.check_pool_create_trace(render(b'BIUVWP????????CAT' + bytes(8) + b'SDJFR'), True)
        with self.assertRaises(ValueError):
            runtime.check_pool_import_trace(render(b'BIUVWLP????????OAMT' + bytes(8) + b'SDJFR'), True)

    def test_pool_data_requires_explicit_diagnostic_pool_selector(self):
        for kwargs in ({}, {'pool_create': True}, {'pool_create': True, 'pool_diagnose': 'build'}):
            with self.subTest(kwargs=kwargs), self.assertRaisesRegex(ValueError, 'pool data requires'):
                runtime.suite(Path('/absent'), pool_data=True, **kwargs)

    def test_pool_import_finally_captures_shared_media_without_case_fallback(self):
        node = next(n for n in ast.parse(Path(runtime.__file__).read_text()).body
                    if isinstance(n, ast.FunctionDef) and n.name == 'suite')
        final = next(n for n in node.body if isinstance(n, ast.Try)).finalbody
        media = next(n for n in final if isinstance(n, ast.If)
                     and isinstance(n.test, ast.Name) and n.test.id == 'pool_create')
        code = compile(ast.Module(body=[media], type_ignores=[]), '<paired pool finally>', 'exec')
        with tempfile.TemporaryDirectory(prefix='aether-pool-import-finally-') as directory:
            out = Path(directory)
            shared = out / 'disposable.raw'
            shared.write_bytes(b'actual paired media')
            unused = out / 'pool-create/disposable.raw'
            unused.parent.mkdir()
            unused.write_bytes(b'unattached case media')
            record = {}
            scope = dict(pool_namespace=False, pool_create=True, case='pool-import', out=out, record=record,
                         pool_attached_media=runtime.pool_attached_media,
                         pool_media_snapshot=runtime.pool_media_snapshot, Path=Path)
            exec(code, scope)
            self.assertEqual(record['pool_media_path'], str(shared))
            self.assertEqual(record['final_pool_media']['sha256'], runtime.sha(shared))
            shared.unlink()
            exec(code, scope)
            self.assertEqual(record['final_pool_media'], {'status': 'unavailable'})

    def test_pool_import_guard_requires_successful_create_teardown_and_exact_bytes(self):
        node = next(n for n in ast.walk(ast.parse(Path(runtime.__file__).read_text()))
                    if isinstance(n, ast.If) and ast.unparse(n.test) ==
                    "name == 'pool-import' and pool_diagnose != 'build' and (not pool_namespace)")
        code = compile(ast.Module(body=[node], type_ignores=[]), '<fresh import guard>', 'exec')
        with tempfile.TemporaryDirectory(prefix='aether-pool-import-prior-') as directory:
            disk = Path(directory) / 'disposable.raw'
            disk.write_bytes(b'exported media')
            prior = dict(name='pool-create', status='pass', vm_run_returned=True,
                         disk_sha256=runtime.sha(disk))
            scope = dict(name='pool-import', pool_diagnose='run', pool_corrupt_labels=False, record={'cases':[prior,{}]},
                         sha=runtime.sha, block_disk=disk, pool_interrupt=False, pool_uncommitted=False, pool_recovery_check=None, pool_namespace=False,
                         check_pool_import_media=runtime.check_pool_import_media)
            exec(code, scope)
            for key, value in (('name','foreign'),('status','running'),
                               ('vm_run_returned',False),('disk_sha256','stale')):
                with self.subTest(key=key):
                    changed = prior | {key:value}
                    scope['record'] = {'cases':[changed,{}]}
                    with self.assertRaisesRegex(ValueError, 'completed create/VM teardown'):
                        exec(code, scope)

    def test_pool_finally_captures_attached_case_not_root_seed(self):
        # Execute the actual finally branch with two different files. This
        # catches the former wrong-path result without building a guest.
        suite_node = next(n for n in ast.parse(Path(runtime.__file__).read_text()).body
                          if isinstance(n, ast.FunctionDef) and n.name == 'suite')
        final = next(n for n in suite_node.body if isinstance(n, ast.Try)).finalbody
        media = next(n for n in final if isinstance(n, ast.If)
                     and isinstance(n.test, ast.Name) and n.test.id == 'pool_create')
        code = compile(ast.Module(body=[media], type_ignores=[]), '<pool finally>', 'exec')
        with tempfile.TemporaryDirectory(prefix='aether-pool-finally-') as directory:
            out = Path(directory)
            seed = out / 'disposable.raw'
            seed.write_bytes(b'unexecuted seed')
            disk = out / 'pool-create/disposable.raw'
            disk.parent.mkdir()
            disk.write_bytes(b'guest changed case media')
            record = {'disk_seed_sha256': runtime.sha(seed)}
            scope = dict(pool_namespace=False, pool_create=True, case=None, out=out, record=record,
                         pool_attached_media=runtime.pool_attached_media,
                         pool_media_snapshot=runtime.pool_media_snapshot, Path=Path)
            exec(code, scope)
            self.assertEqual(record['pool_media_path'], str(disk))
            self.assertEqual(record['final_pool_media']['sha256'], runtime.sha(disk))
            self.assertFalse(record['final_pool_media']['whole_disk_matches_seed'])
            disk.unlink()
            exec(code, scope)
            self.assertEqual(record['final_pool_media'], {'status': 'unavailable'})

    def test_pool_diagnostic_selection_rejects_before_intake(self):
        for flags in (['--pool-diagnose', 'build'],
                      ['--pool-diagnose', 'run', '--pool-create'],
                      ['--pool-diagnose', 'build', '--pool-create', '--engine-utc', '--case', 'normal']):
            result = subprocess.run([sys.executable, str(runtime.ROOT/'scripts/service_runtime_smoke.py'),
                                     '--delivery', '/missing', *flags], capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 64)
            self.assertNotIn(b'[RUNNING]', result.stderr)
            self.assertFalse(result.stdout)
        with patch.object(runtime, 'intake', side_effect=AssertionError('unexpected intake')):
            for mode in ('build', 'run', 'invalid'):
                with self.assertRaises(ValueError):
                    suite(Path('/missing'), pool_diagnose=mode)

    def test_pool_media_capture_before_disposal(self):
        with tempfile.TemporaryDirectory(prefix='aether-pool-media-') as directory:
            disk = Path(directory) / 'disposable.raw'
            self.assertEqual(runtime.pool_media_snapshot(disk), {'status': 'unavailable'})
            disk.write_bytes(b'abcd')
            captured = runtime.pool_media_snapshot(disk)
            self.assertEqual(captured['sha256'], runtime.sha(disk))
            self.assertEqual(captured['bytes'], 4)
            self.assertFalse(captured['outside_region_canaries_match'])
            alias = Path(directory) / 'alias.raw'
            alias.symlink_to(disk)
            self.assertEqual(runtime.pool_media_snapshot(alias), {'status': 'unavailable'})
            with disk.open('wb') as stream:
                stream.write(bytes([165]) * 4096)
                stream.seek(64 * 1024 * 1024 + 4096)
                stream.write(bytes([165]) * 4096)
            captured = runtime.pool_media_snapshot(disk)
            self.assertTrue(captured['outside_region_canaries_match'])
            self.assertEqual(captured['sha256'], runtime.sha(disk))
            for offset in (0, 64 * 1024 * 1024 + 8191):
                with disk.open('r+b') as stream:
                    stream.seek(offset)
                    stream.write(b'!')
                self.assertFalse(runtime.pool_media_snapshot(disk)['outside_region_canaries_match'])
                with disk.open('r+b') as stream:
                    stream.seek(offset)
                    stream.write(bytes([165]))

    def test_open_probe_observations_require_real_complete_checkpoint(self):
        def trace(events):
            return ''.join(f'NATIVE observation slot=0 generation=1 offset={i * 8} byte={phase}\n'
                           for i, phase in enumerate(events)) + (
                'NATIVE terminal slot=0 generation=1 kind=1 detail=867\n'
                'NATIVE supervisor result=401 reclaimed=0\n')
        for middle in (b'LMLMLM', b'LLLMMM', b'LLMMLM'):
            result = check_open_probe_trace(trace(b'BIUVWAC' + middle + b'O'))
            self.assertEqual(result['open_probe_provider_reads'], 3)
            self.assertFalse(result['clean_lifetime'])
        valid = trace(b'BIUVWACLLLMMMO')
        for broken in (trace(b'BIUVWAC'), trace(b'BIUVWACMLLMMLO'),
                       trace(b'BIUVWACLLLLMMO'), trace(b'BIUVWACLLLMMYO'),
                       valid.replace('offset=56', 'offset=64'),
                       valid.replace('generation=1 offset=56', 'generation=2 offset=56'),
                       valid.replace('detail=867', 'detail=0'),
                       valid.replace('result=401', 'result=100'),
                       valid + 'NATIVE supervisor result=401 reclaimed=0\n',
                       'NATIVE terminal slot=0 generation=1 kind=1 detail=867\n' + valid.replace(
                           'NATIVE terminal slot=0 generation=1 kind=1 detail=867\n', ''),
                       'NATIVE supervisor result=401 reclaimed=0\n' + valid.replace(
                           'NATIVE supervisor result=401 reclaimed=0\n', '')):
            with self.subTest(broken=broken), self.assertRaises(ValueError):
                check_open_probe_trace(broken)

    def test_corrected_candidate_profile_rejects_unsupported_intake(self):
        runner = runtime.ROOT / 'scripts/service_runtime_smoke.py'
        for flags in (['--case', 'reaper-exhaustion'],
                      ['--fixed-reaper', '--openzfs-waits'],
                      ['--fixed-reaper', '--engine-volume-workers'],
                      ['--fixed-reaper', '--engine-native'], ['--spa-active'],
                      ['--spa-active', '--fixed-reaper', '--engine-utc', '--utc-delivery', '/missing', '--case', 'utc-spa']):
            result = subprocess.run([sys.executable, str(runner), '--delivery', '/missing', *flags],
                                    capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 64)
            self.assertFalse(result.stdout)
            self.assertNotIn(b'[RUNNING]', result.stderr)
        with patch.object(runtime, 'intake', side_effect=AssertionError('unexpected intake')):
            for profile in ('openzfs_waits', 'engine_native', 'engine_volume_workers'):
                with self.assertRaises(ValueError):
                    runtime.suite(Path('/missing'), fixed_reaper=True, **{profile: True})
            with self.assertRaises(ValueError):
                runtime.suite(Path('/missing'), runtime.EXHAUSTION_CASE)

    def test_spa_activation_rejects_wrong_revision_or_profile_before_intake(self):
        runner = runtime.ROOT / 'scripts/service_runtime_smoke.py'
        for name in runtime.ACTIVE_CASES:
            self.assertTrue(runtime.volume_readonly(name))
            with patch.object(runtime, 'intake', side_effect=AssertionError('unexpected intake')):
                for flags in ({}, {'engine_utc': True, 'utc_delivery': Path('/missing')},
                              {'fixed_reaper': True}):
                    with self.assertRaises(ValueError):
                        runtime.suite(Path('/missing'), name, **flags)
            result = subprocess.run([sys.executable, str(runner), '--delivery', '/missing',
                                     '--engine-utc', '--utc-delivery', '/missing', '--case', name],
                                    capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 64)
            self.assertFalse(result.stdout)
            self.assertNotIn(b'[RUNNING]', result.stderr)
            result = subprocess.run([sys.executable, str(runner), '--delivery', '/missing',
                                     '--fixed-reaper', '--engine-utc', '--utc-delivery', '/missing',
                                     '--case', name], capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 1)
            self.assertNotIn(b'invalid choice', result.stderr)
            self.assertNotIn(b'[RUNNING]', result.stderr)

    def test_physical_explicit_cases_are_never_silently_filtered(self):
        self.assertEqual(runtime.physical_cases(None), runtime.PHYSICAL_CORE_CASES)
        for name in runtime.PHYSICAL_CASES:
            if name == runtime.WRITE_CASES[1]:
                with self.assertRaises(ValueError):
                    runtime.physical_cases(name)
            else:
                self.assertEqual(runtime.physical_cases(name), (name,))
        for name in ('unknown', 'spa-active', 'utc-spa'):
            with self.assertRaises(ValueError):
                runtime.physical_cases(name)

    def test_physical_selection_requires_corrected_exclusive_utc(self):
        runner = runtime.ROOT / 'scripts/service_runtime_smoke.py'
        for name in runtime.PHYSICAL_CASES:
            self.assertEqual(runtime.volume_readonly(name), name not in runtime.WRITE_CASES or name == runtime.WRITE_CASES[1])
            with patch.object(runtime, 'intake', side_effect=AssertionError('unexpected intake')):
                for flags in ({}, {'engine_utc': True, 'utc_delivery': Path('/missing')},
                              {'fixed_reaper': True}, {'engine_utc': True, 'fixed_reaper': True,
                                                       'spa_active': True, 'utc_delivery': Path('/missing')}):
                    with self.assertRaises(ValueError):
                        runtime.suite(Path('/missing'), name, **flags)
            result = subprocess.run([sys.executable, str(runner), '--delivery', '/missing',
                                     '--fixed-reaper', '--engine-utc', '--utc-delivery', '/missing',
                                     '--case', name], capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 64 if name == runtime.WRITE_CASES[1] else 1)
            self.assertNotIn(b'invalid choice', result.stderr)
            self.assertNotIn(b'[RUNNING]', result.stderr)

        for flags in (['--spa-physical'], ['--spa-physical', '--engine-utc', '--utc-delivery', '/missing'],
                      ['--spa-physical', '--spa-active', '--fixed-reaper', '--engine-utc', '--utc-delivery', '/missing']):
            result = subprocess.run([sys.executable, str(runner), '--delivery', '/missing', *flags],
                                    capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 64)
            self.assertNotIn(b'[RUNNING]', result.stderr)

    def test_write_group_requires_fresh_verify_and_preserves_exact_media_scope(self):
        self.assertEqual(runtime.physical_cases(None, writable=True), runtime.WRITE_CASES)
        with self.assertRaises(ValueError):
            runtime.physical_cases('spa-physical', writable=True)
        before = bytes([165]) * (64 * 1024 * 1024 + 8192)
        after = runtime.physical_expected_disk(before, runtime.WRITE_CASES[0])
        offset = 4096 + 1048576
        self.assertEqual(after[:offset], before[:offset])
        self.assertEqual(after[offset + 512:], before[offset + 512:])
        self.assertEqual(after[offset:offset + 512], bytes((i * 17 + 91) & 255 for i in range(512)))
        self.assertEqual(runtime.physical_expected_disk(after, runtime.WRITE_CASES[1]), after)
        for flags in ({'spa_write': True}, {'spa_write': True, 'engine_utc': True},
                      {'spa_write': True, 'fixed_reaper': True, 'engine_utc': True,
                       'utc_delivery': Path('/missing'), 'spa_physical': True}):
            with patch.object(runtime, 'intake', side_effect=AssertionError('unexpected intake')):
                with self.assertRaises(ValueError):
                    runtime.suite(Path('/missing'), **flags)

    def test_write_flush_oracle_rejects_missing_duplicate_stale_and_false_success(self):
        tags = 'BIUVWACOqstkhgcfjipQSTKHPDJFR'
        good = ''.join(f'NATIVE observation slot=0 generation=1 offset={i * 8} byte={ord(t)}\n' for i, t in enumerate(tags))
        good += ''.join(f'NATIVE observation slot=0 generation={g} offset={i * 8} byte={ord(t)}\n' for g in (2, 3) for i, t in enumerate('BNR'))
        self.assertTrue(runtime.check_write_trace(good, runtime.WRITE_CASES[0])['actual_provider_flush_qualified'])
        for changed in (good.replace('byte=106', 'byte=101'), good + good,
                        good.replace('generation=1', 'generation=2', 1),
                        good.replace('offset=0 byte=66', 'offset=8 byte=66', 1)):
            with self.assertRaises(ValueError):
                runtime.check_write_trace(changed, runtime.WRITE_CASES[0])
        denied = ''.join(f'NATIVE observation slot=0 generation=1 offset={i * 8} byte={ord(t)}\n' for i, t in enumerate('BIUVWACOqstkhgi'))
        denied += 'NATIVE terminal slot=0 generation=1 kind=1 detail=868\nNATIVE supervisor result=401 reclaimed=0\n'
        self.assertFalse(runtime.check_write_trace(denied, 'spa-physical-no-flush')['actual_provider_flush_qualified'])
        for changed in (denied.replace('detail=868', 'detail=0'), denied.replace('reclaimed=0', 'reclaimed=1'),
                        denied.replace('kind=1', 'kind=2')):
            with self.assertRaises(ValueError):
                runtime.check_write_trace(changed, 'spa-physical-no-flush')

    def test_reaper_origins_require_unique_actual_text_addresses(self):
        mapping = ('100 100 20 16 /probe.o:(.text)\n'
                   '200 200 40 16 /libaether_runtime.a(backend.o):(.text)\n'
                   '300 300 20 16 /libaether_runtime.a(pthread.o):(.text)\n')
        symbols = ('100 T __wrap___unmapself\n110 T __wrap___tl_lock\n'
                   '200 t __unmapself\n220 t reap\n300 t __tl_lock\n')
        self.assertEqual(len(runtime.check_reaper_bindings(mapping, symbols)), 5)
        for changed_map, changed_symbols in (
                (mapping.replace('backend.o', 'substitute.o'), symbols),
                (mapping, symbols.replace('200 t', '240 t')),
                (mapping + mapping, symbols),
                (mapping, symbols + '200 t __unmapself\n'),
                (mapping, symbols.replace('220 t reap\n', ''))):
            with self.assertRaises(ValueError):
                runtime.check_reaper_bindings(changed_map, changed_symbols)

    def test_reaper_selection_rejects_other_profiles_before_intake(self):
        for name in runtime.REAPER_CASES:
            for profile in ('openzfs_waits', 'startup_config', 'engine_link',
                            'engine_native', 'rtc_source', 'block_region',
                            'engine_volume', 'engine_volume_workers',
                            'engine_spa_utc', 'engine_utc'):
                with self.subTest(name=name, profile=profile):
                    with patch.object(runtime, 'intake', side_effect=AssertionError('unexpected intake')) as intake:
                        with self.assertRaises(ValueError):
                            runtime.suite(Path('/missing'), name, **{profile: True})
                        intake.assert_not_called()

    def test_engine_replacement_rejects_wrong_owner_terminal_or_reclaim(self):
        serial = ''.join(f'NATIVE terminal slot=0 generation={g} kind=1 detail=0\n' for g in range(1, 4))
        serial += 'NATIVE supervisor result=100 reclaimed=3\nAETHER NATIVE SUPERVISION PASS\n'
        self.assertEqual(check_engine_trace('NATIVE observation slot=0 generation=1 offset=0 byte=66\n' + serial)['reclaimed'], 3)
        self.assertEqual(check_engine_trace(serial)['final_live_workers'], 0)
        for changed in (serial.replace('generation=2', 'generation=1'),
                        serial.replace('kind=1 detail=0', 'kind=1 detail=125', 1),
                        serial.replace('reclaimed=3', 'reclaimed=2'),
                        serial.replace('slot=0', 'slot=1', 1), serial + serial):
            with self.assertRaises(ValueError):
                check_engine_trace(changed)

    def test_engine_bindings_reject_substitution_omission_and_duplicates(self):
        origins = {
            'engine-startup.o': ['main'],
            'selected-engine.o': ['kernel_init', 'kernel_fini', 'cv_init', 'cv_timedwait_hires',
                                  'random_init', 'random_get_bytes', 'arc_all_memory',
                                  'arc_available_memory', 'aether_zfs_granted_pages',
                                  'aether_zfs_assigned_cpus'],
            'libaether_runtime.a(backend.o)': ['aether_runtime_init', 'aether_runtime_finish', '__aether_io']}
        mapping = '\n'.join('0 0 0 1 /private/' + owner + ':(.text)\n' +
                            '\n'.join('0 0 0 1 ' + symbol for symbol in symbols)
                            for owner, symbols in origins.items())
        self.assertEqual(len(check_engine_bindings(mapping)), 14)
        active_symbols = ('aether_spa_active_probe', 'aether_root_done', 'spa_activate', 'spa_deactivate',
                          'zio_root', 'zio_wait', 'metaslab_class_create', 'metaslab_class_destroy')
        active = mapping + '\n0 0 0 1 /private/selected-engine.o:(.text)\n' + '\n'.join(
            '0 0 0 1 ' + name for name in active_symbols)
        self.assertEqual(len(check_engine_bindings(active, spa_active=True)), 22)
        for name in active_symbols:
            with self.subTest(missing=name), self.assertRaises(ValueError):
                check_engine_bindings(active.replace('0 0 0 1 ' + name, ''), spa_active=True)

        physical_symbols = ('aether_spa_physical_probe', 'aether_physical_done', 'aether_physical_pread_original', 'spa_activate',
                            'spa_deactivate', 'vdev_alloc', 'vdev_open', 'vdev_free', 'zio_read_phys',
                            'zio_wait', 'vdev_file_io_start', 'vdev_file_io_strategy', 'zio_delay_interrupt',
                            'abd_get_from_buf', 'abd_free')
        physical = mapping + '\n0 0 0 1 /private/selected-engine.o:(.text)\n' + '\n'.join(
            '0 0 0 1 ' + name for name in physical_symbols)
        physical += '\n0 0 0 1 /private/engine-startup.o:(.text)\n0 0 0 1 aether_engine_utc_phase\n0 0 0 1 aether_physical_io_phase'
        self.assertEqual(len(check_engine_bindings(physical, spa_physical=True)), 31)
        for name in ('aether_engine_utc_phase', 'aether_physical_io_phase'):
            with self.subTest(missing=name), self.assertRaises(ValueError):
                check_engine_bindings(physical.replace('0 0 0 1 ' + name, ''), spa_physical=True)
        for name in physical_symbols:
            with self.subTest(missing=name), self.assertRaises(ValueError):
                check_engine_bindings(physical.replace('0 0 0 1 ' + name, ''), spa_physical=True)
        pool_symbols = ('system_taskq_init', 'system_taskq_fini',
                        'aether_pool_prepare', 'aether_spa_pool_probe', 'spa_create',
                        'spa_export', 'spa_open', 'spa_close', 'spa_feature_is_enabled',
                        'aether_pool_hooks_prepare', 'aether_pool_hooks_check',
                        'aether_pool_root_begin', 'aether_pool_root_end',
                        'aether_pool_zio_child', 'aether_pool_zio_retire',
                        'aether_pool_write_requested', 'aether_pool_flush_requested',
                        'aether_pool_txg_observe', 'aether_pool_sync_observe',
                        'aether_pool_io_begin', 'aether_pool_provider_done',
                        'aether_pool_leaf_done', 'nvlist_pack')
        pool = mapping + '\n0 0 0 1 /private/selected-engine.o:(.text)\n' + '\n'.join(
            '0 0 0 1 ' + name for name in pool_symbols)
        pool += '\n0 0 0 1 /private/engine-startup.o:(.text)\n0 0 0 1 aether_engine_utc_phase'
        self.assertEqual(len(check_engine_bindings(pool, pool=True)), 38)
        diagnostic = pool + '\n0 0 0 1 /private/selected-engine.o:(.text)\n'
        diagnostic += '\n'.join('0 0 0 1 ' + name for name in
                               ('aether_pool_failure_site', 'aether_pool_failure_allocation', 'aether_pool_failure_assertion',
                                'aether_pool_failure_pthread', 'aether_pool_failure_denial', 'aether_pool_failure_tid'))
        self.assertEqual(len(check_engine_bindings(diagnostic, pool=True, diagnostics=True)), 44)
        for bad in (diagnostic.replace('0 0 0 1 aether_pool_failure_tid', ''),
                    diagnostic+'\n0 0 0 1 /private/libaether_runtime.a(backend.o):(.text)\n0 0 0 1 aether_pool_failure_tid'):
            with self.assertRaises(ValueError): check_engine_bindings(bad, pool=True, diagnostics=True)
        for name in ('aether_pool_failure_site', 'aether_pool_failure_allocation', 'aether_pool_failure_assertion',
                                'aether_pool_failure_pthread', 'aether_pool_failure_denial', 'aether_pool_failure_tid'):
            with self.assertRaises(ValueError):
                check_engine_bindings(diagnostic.replace('0 0 0 1 '+name, ''), pool=True, diagnostics=True)
        for name in (*pool_symbols, 'aether_engine_utc_phase'):
            with self.subTest(missing=name), self.assertRaises(ValueError):
                check_engine_bindings(pool.replace('0 0 0 1 ' + name, ''), pool=True)
        with self.assertRaises(ValueError):
            check_engine_bindings(pool.replace('/private/selected-engine.o', '/private/substitute.o'), pool=True)

        for broken in (mapping.replace('selected-engine.o', 'old-engine.o'),
                       mapping.replace('libaether_runtime.a(backend.o)', 'libc.a(backend.o)'),
                       mapping.replace('0 0 0 1 kernel_init', ''),
                       mapping + '\n0 0 0 1 __aether_io',
                       mapping + '\n0 0 0 1 /private/engine/adapter.o:(.text)'):
            with self.subTest(broken=broken[-100:]), self.assertRaises(ValueError):
                check_engine_bindings(broken)

    def test_engine_selection_rejects_before_intake_or_native_execution(self):
        for case, waits in (('normal', False), (None, True)):
            with self.subTest(case=case, waits=waits), self.assertRaises(ValueError):
                suite(Path('/missing-delivery'), case, waits, True)
        for case in ('missing', 'version', 'cache', 'no-fini', 'no-finish', 'no-entropy'):
            with self.assertRaises(ValueError):
                suite(Path('/missing-delivery'), case)
        with self.assertRaises(ValueError):
            suite(Path('/missing-delivery'), 'normal', engine_native=True)
        with self.assertRaises(ValueError):
            suite(Path('/missing-delivery'), engine_link=True, engine_native=True)
        runner = runtime.ROOT / 'scripts/service_runtime_smoke.py'
        for flags in (['--engine-link', '--case', 'normal'], ['--engine-link', '--openzfs-waits'],
                      ['--engine-link', '--startup-config'], ['--case', 'missing'],
                      ['--engine-native', '--case', 'normal'], ['--engine-native', '--engine-link'],
                      ['--case', 'no-fini']):
            result = subprocess.run([sys.executable, str(runner), '--delivery', '/missing', *flags],
                                    capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 64)
            self.assertFalse(result.stdout)
            self.assertNotIn(b'[RUNNING]', result.stderr)

    def test_openzfs_adaptation_rejects_unreviewed_client(self):
        source = (runtime.SOURCE / 'probe.c').read_text()
        adapted, edits = adapt_runtime(source)
        self.assertEqual(len(edits), 5)
        self.assertIn('zfs_wait(&condition, &zfs_mutex, &deadline)', adapted)
        self.assertIn('pthread_mutex_trylock(&mutex)', adapted)
        self.assertIn('aether_runtime_finish()', adapted)
        for changed in (source.replace('pthread_mutex_lock(&mutex)', 'other_lock(&mutex)'),
                        source + '\npthread_cond_init(&condition, &attr)\n', adapted):
            with self.subTest(changed=changed[-80:]), self.assertRaises(RuntimeError):
                adapt_runtime(changed)

    def test_map_requires_actual_openzfs_objects(self):
        symbols = ('cv_init', 'cv_timedwait_hires', 'mutex_enter', 'mutex_exit')
        mapping = '\n'.join('/private/port/kernel.c-native.o:(.text.' + s + ')' for s in symbols)
        self.assertEqual(check_callers(mapping), list(symbols))
        for changed in (mapping.replace('kernel.c-native.o', 'fake.o'),
                        mapping.replace('.text.cv_init)', '.text.cv_init_other)'),
                        '\n'.join(mapping.splitlines()[:-1])):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                check_callers(changed)

    def test_seal_corruption_paths_types_and_count(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'payload').write_bytes(b'fixed')
            h = hashlib.sha256(b'fixed').hexdigest()

            def verify(text, count=1):
                (root / 'SHA256SUMS').write_text(text)
                pin = hashlib.sha256(text.encode()).hexdigest()
                return sealed(root, pin, count)

            self.assertEqual(verify(h + '  payload\n'), {'payload': h})
            for name in ('../outside', '/absolute', './payload', 'payload/../payload',
                         'payload\nforged', 'payload\t'):
                with self.subTest(name=name), self.assertRaises(ValueError):
                    verify(h + '  ' + name + '\n')
            with self.assertRaises(ValueError):
                verify((h + '  payload\n') * 2)
            with self.assertRaises(ValueError):
                verify(h + '  payload\n', count=2)
            with self.assertRaises(ValueError):
                sealed(root, '0' * 64, 1)
            (root / 'payload').write_bytes(b'changed')
            with self.assertRaises(ValueError):
                verify(h + '  payload\n')
            (root / 'payload').unlink()
            (root / 'real').write_bytes(b'fixed')
            (root / 'payload').symlink_to(root / 'real')
            with self.assertRaises(ValueError):
                verify(h + '  payload\n')
            (root / 'folder').symlink_to(root, target_is_directory=True)
            with self.assertRaises(ValueError):
                verify(h + '  folder/real\n')

    def test_owner_generation_and_exact_cleanup(self):
        serial = ('NATIVE terminal slot=0 generation=1 kind=1 detail=0\n'
                  'NATIVE terminal slot=1 generation=1 kind=1 detail=0\n'
                  'NATIVE terminal slot=0 generation=2 kind=1 detail=0\n'
                  'NATIVE supervisor result=100 reclaimed=3\n'
                  'AETHER NATIVE SUPERVISION PASS\n')
        self.assertEqual(check_trace(serial)['reclaimed'], 3)
        stopped = '\n'.join(serial.splitlines()[1:]) + '\n'
        check_trace(stopped, True)
        for broken in (serial.replace('reclaimed=3', 'reclaimed=2'),
                       serial.replace('generation=2', 'generation=1'),
                       serial.replace('slot=1', 'slot=2'),
                       serial.replace('detail=0', 'detail=802', 1),
                       serial + serial.splitlines()[0] + '\n',
                       serial.replace('SUPERVISION PASS', 'SUPERVISION CLOSED'),
                       serial + 'NATIVE supervisor result=100 reclaimed=3\n'):
            with self.subTest(broken=broken), self.assertRaises(ValueError):
                check_trace(broken)
        with self.assertRaises(ValueError):
            check_trace(serial, True)
        with self.assertRaises(ValueError):
            check_trace(stopped)

    def test_unknown_selection_rejects_before_intake(self):
        for case in ('', 'typo', 'normal,stop'):
            with self.subTest(case=case), self.assertRaises(ValueError):
                suite(Path('/missing-delivery'), case)

    def test_cli_streams_usage_and_terminal_controls(self):
        self.assertEqual(display('name\x1b\r\n'), 'name\\x1b\\x0d\\x0a')
        runner = Path(__file__).resolve().parents[1] / 'scripts/service_runtime_smoke.py'
        for arg in ('--help', '--version'):
            result = subprocess.run([sys.executable, str(runner), arg], capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 0)
            self.assertTrue(result.stdout)
            self.assertFalse(result.stderr)
        result = subprocess.run([sys.executable, str(runner), '--delivery', '/missing',
                                 '--case', 'bad\x1b\r\n'], capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 64)
        self.assertFalse(result.stdout)
        self.assertNotIn(b'\x1b', result.stderr)
        self.assertNotIn(b'\r', result.stderr)

    def test_copy_race_rejects_recipe_before_consumption(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            delivery = root / 'delivery'
            members = {}
            for n in ('runtime/libaether_runtime.a', 'source/experiments/build.py'):
                p = delivery / n
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(b'verified')
                members[n] = hashlib.sha256(p.read_bytes()).hexdigest()
            copy = shutil.copyfile

            def changed_copy(source, destination):
                result = copy(source, destination)
                if str(destination).endswith('build.py'):
                    Path(destination).write_bytes(b'changed after seal check')
                return result

            with patch.object(runtime, 'DEPENDENCY', root / 'retained'), \
                 patch.object(runtime, 'sealed', side_effect=[members, {}]), \
                 patch.object(runtime, 'ARCHIVE', members['runtime/libaether_runtime.a']), \
                 patch.object(runtime.shutil, 'copyfile', side_effect=changed_copy):
                with self.assertRaisesRegex(ValueError, 'retained dependency changed'):
                    runtime.intake(delivery)


class EngineStartup(unittest.TestCase):
    """Execute the actual C entry point with controlled surrounding functions."""
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-engine-lifecycle-')
        cls.addClassCleanup(cls.temp.cleanup)
        out = Path(cls.temp.name)
        driver = out / 'driver.c'
        driver.write_text('''#include <errno.h>
#include <stdlib.h>
#include "startup.h"
static int mode, stage, binding;
int aether_engine_main(void);
int aether_runtime_init(void) {
    if (stage != 0) _Exit(90);
    stage = 1; return mode == 1 ? EAGAIN : 0;
}
unsigned aether_runtime_live(void) {
    if (stage == 1) return mode == 2 ? 2 : 1;
    if (stage != 4) _Exit(91);
    return mode == 6 ? 1 : 0;
}
unsigned aether_runtime_admissions(void) {
    if (stage == 1) return mode == 3 ? 2 : 1;
    if (stage != 4) _Exit(92);
    return mode == 7 ? 0 : mode == 8 ? 513 : 84;
}
void kernel_init(int write_mode) {
    if (stage != 1 || write_mode != 1 || binding != 1) _Exit(93);
    stage = 2;
}
void kernel_fini(void) {
    if (stage != 2) _Exit(94);
    stage = 3;
}
int aether_runtime_finish(void) {
    if (stage != 3) _Exit(95);
    stage = 4; return mode == 4 ? EBUSY : mode == 5 ? EIO : 0;
}
int aether_zfs_startup_bind(const struct aether_zfs_startup *record) {
    if (stage != 1 || binding || !record || record->hostid != 0x41455448 ||
        record->cache_policy != AETHER_ZFS_EMPTY_CACHE) _Exit(98);
    ++binding; return mode == 9 ? EINVAL : 0;
}
int main(int argc, char **argv) {
    if (argc != 2) return 96;
    mode = atoi(argv[1]);
    int expected = mode == 9 ? 226 : mode == 0 ? 0 : mode <= 3 ? 222 : mode <= 5 ? 224 : 225;
    int result = aether_engine_main();
    if (result != expected || stage != ((mode >= 1 && mode <= 3) || mode == 9 ? 1 : 4)) return 97;
    if (mode >= 1 && mode <= 3 && binding) return 99;
    return 0;
}
''')
        sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        cc = ['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-std=c17', '-O2',
              '-Wall', '-Wextra', '-Werror', '-isysroot', sdk,
              '-I', str(runtime.ROOT / 'user/storage/openzfs-elapsed')]
        cls.binary = out / 'probe'
        for argv in (cc + ['-I', str(runtime.DEPENDENCY / 'runtime'), '-Dmain=aether_engine_main',
                           '-c', str(runtime.SOURCE / 'engine-startup.c'), '-o', str(out / 'startup.o')],
                     cc + [str(driver), str(out / 'startup.o'), '-o', str(cls.binary)]):
            result = subprocess.run(argv, capture_output=True, text=True, timeout=30)
            if result.returncode:
                raise RuntimeError(result.stderr)

    def test_serialized_success_and_init_failure_never_enters_engine(self):
        for mode in range(4):
            with self.subTest(mode=mode):
                self.assertEqual(subprocess.run([self.binary, str(mode)], timeout=5).returncode, 0)

    def test_busy_failed_finish_and_surviving_workers_reject(self):
        for mode in range(4, 9):
            with self.subTest(mode=mode):
                self.assertEqual(subprocess.run([self.binary, str(mode)], timeout=5).returncode, 0)

    def test_bad_startup_binding_never_enters_engine(self):
        self.assertEqual(subprocess.run([self.binary, '9'], timeout=5).returncode, 0)


class EngineRetirement(unittest.TestCase):
    """Actual admission hook must not turn unfinished teardown into success."""
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-engine-retirement-')
        cls.addClassCleanup(cls.temp.cleanup)
        out = Path(cls.temp.name)
        driver = out / 'driver.c'
        driver.write_text('''#include "runtime.h"
#include "engine-observe.inc"
#include <string.h>
static int mode, attempts, sleeps, reads, writes;
uint64_t aether_zfs_granted_pages(void) { return mode == 6 ? 128 : 8192; }
uint64_t aether_zfs_free_pages(void) { return 4096; }
unsigned aether_runtime_live(void) { return 1; }
unsigned aether_runtime_admissions(void) { return 1; }
int aether_runtime_finish(void) {
    ++attempts;
    return mode == 1 || mode == 4 || (mode == 0 && attempts <= 2) ? EBUSY : mode == 2 ? EIO : 0;
}
int clock_gettime(clockid_t id, struct timespec *out) {
    if (id != CLOCK_MONOTONIC) _Exit(90);
    if (mode == 3) return -1;
    *out = (struct timespec){reads / 2, (reads % 2) * 500000000}; ++reads; return 0;
}
int nanosleep(const struct timespec *pause, struct timespec *rem) {
    if (pause->tv_sec || pause->tv_nsec != 1000000 || rem) _Exit(91);
    ++sleeps; return mode == 4 ? -1 : 0;
}
ssize_t write(int fd, const void *buf, size_t bytes) {
    static const unsigned char expected[8] = {'B',1,1,0,0,16,0,32};
    if (fd != 1 || !bytes || bytes != 8 - (size_t)writes ||
        memcmp(buf, expected + writes, bytes)) _Exit(92);
    if (mode == 5) return 0;
    ++writes; return 1; /* Deliberately short writes must complete all eight bytes. */
}
int main(int argc, char **argv) {
    if (argc != 2) return 93;
    mode = atoi(argv[1]);
    engine_observe('B');
    int result = engine_finish();
    int expected = mode == 1 ? ETIMEDOUT : mode >= 2 && mode <= 4 ? EIO : 0;
    if (result != expected || writes != 8) return 94;
    if (mode == 0 && (attempts != 3 || sleeps != 2)) return 95;
    if (mode == 1 && (attempts != 4 || sleeps != 3)) return 96;
    return 0;
}
''')
        cls.binary = out / 'probe'
        sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        result = subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-std=c17',
            '-D_POSIX_C_SOURCE=200809L', '-O2', '-Wall', '-Wextra', '-Werror',
            '-isysroot', sdk, '-I', str(runtime.SOURCE), '-I', str(runtime.DEPENDENCY / 'runtime'),
            str(driver), '-o', str(cls.binary)], capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise RuntimeError(result.stderr)

    def test_busy_cleanup_can_settle_but_timeout_and_provider_errors_reject(self):
        for mode in range(5):
            with self.subTest(mode=mode):
                self.assertEqual(subprocess.run([self.binary, str(mode)], timeout=5).returncode, 0)

    def test_incomplete_output_and_wrong_grant_fail_closed(self):
        for mode in (5, 6):
            with self.subTest(mode=mode):
                self.assertEqual(subprocess.run([self.binary, str(mode)], timeout=5).returncode, 227)


class PoolDiagnosticDriver(unittest.TestCase):
    """Compiled actual diagnostic guard; host bytes, not native reclamation."""

    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix='aether-pool-driver-')
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.output = Path(cls.temporary.name)
        source = '''use std::cell::RefCell;
thread_local! { static ROW: RefCell<[u8;8]> = const { RefCell::new([0;8]) }; }
fn check(ok: bool) { if !ok { std::process::exit(90); } }
fn byte(_owner: u64, offset: u64) -> u8 { ROW.with(|r| r.borrow()[offset as usize]) }
fn main() {
    let args: Vec<String> = std::env::args().collect();
    let stage: usize = args[1].parse().unwrap();
    let stale: u64 = args[2].parse().unwrap();
    let dirty: usize = args[3].parse().unwrap();
    ROW.with(|r| { let mut row=r.borrow_mut(); row[0]=b'C';
        if dirty < 8 { row[dirty]=1; } });
    let owner=1;
    for stage in stage..stage+1 {
        let offset=0;
        let observed = byte(owner, offset);
        let _=observed;
            let live = byte(owner, offset + 1);
        let _=live;
        std::process::exit(91); // unchanged resource-check path must be reached
    }
}
'''
        selected = runtime.pool_diagnostic_driver(source)
        for name, text, enabled in (
                ('selected', selected, True), ('other-profile', selected, False),
                ('pool-import', selected, True),
                ('broken-padding', selected.replace(
                    'check(byte(owner, offset + n) == 0);',
                    'let _ = byte(owner, offset + n);', 1), True)):
            path = cls.output / (name + '.rs')
            path.write_text(text)
            command = ['rustc', '+1.98.0', '--edition=2024', '-Dwarnings',
                       '-C', 'opt-level=2', str(path), '-o', str(cls.output/name)]
            if enabled:
                command += ['--cfg', 'pool_create']
            if name == 'pool-import':
                command += ['--cfg', 'pool_import']
            result = subprocess.run(command, capture_output=True, timeout=30)
            if result.returncode:
                raise RuntimeError(result.stderr.decode())

    def run_guard(self, name='selected', stage=14, stale=0, dirty=8):
        return subprocess.run([str(self.output/name), str(stage), str(stale), str(dirty)],
                              capture_output=True, timeout=5).returncode

    def test_exact_raw_frame_and_all_corrupt_bytes(self):
        self.assertEqual(self.run_guard(), 0)
        for dirty in range(8):
            with self.subTest(dirty=dirty):
                self.assertEqual(self.run_guard(dirty=dirty), 90)

    def test_wrong_phase_owner_or_profile_retains_resource_path(self):
        for stage in (0, 6, 13, 15, 19):
            self.assertEqual(self.run_guard(stage=stage), 91)
        self.assertEqual(self.run_guard(stale=1), 91)
        self.assertEqual(self.run_guard(name='other-profile'), 91)

    def test_broken_padding_guard_cannot_reject_corrupt_frame(self):
        self.assertEqual(self.run_guard(name='broken-padding', dirty=7), 0)
        self.assertEqual(self.run_guard(dirty=7), 90)

    def test_import_fingerprint_stage_is_not_a_raw_creation_frame(self):
        self.assertEqual(self.run_guard(name='pool-import'), 91)
        self.assertEqual(self.run_guard(name='pool-import', dirty=7), 91)

    def test_context_drift_rejects_selection(self):
        for source in ('', '            let live = byte(owner, offset + 1);' * 2):
            with self.assertRaises(ValueError):
                runtime.pool_diagnostic_driver(source)


class PoolDataDriver(unittest.TestCase):
    "Compile the actual adapted phase/resource loop, including variable fields."

    recovery_check = None
    writer_rows = 30
    pool_data = True
    pool_namespace = False
    pool_zpl_write = False
    pool_zpl_recover = False
    pool_zpl_stages = False
    pool_zpl_write_stages = False
    pool_zpl_txg_stages = False
    pool_zpl_sync_stages = False

    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix='aether-pool-data-driver-')
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.output = Path(cls.temporary.name)
        tree = ast.parse(Path(runtime.__file__).read_text())
        suite_node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'suite')
        volume = next(n for n in ast.walk(suite_node) if isinstance(n, ast.If) and
                      isinstance(n.test, ast.Name) and n.test.id == 'engine_volume' and
                      n.body and isinstance(n.body[0], ast.Assign) and
                      ast.unparse(n.body[0].targets[0]) == 'driver_text')
        body = []
        for node in volume.body:
            if isinstance(node, ast.Assign) and ast.unparse(node.targets[0]) == 'driver_source':
                break
            body.append(node)
        scope = dict(_zpl_storage_lifetime=False, SOURCE=runtime.SOURCE, spa_physical=False, pool_create=True,
                     namespace_ipc=False, pool_zpl_write=cls.pool_zpl_write, pool_zpl_recover=cls.pool_zpl_recover,
                     _zpl_stages=cls.pool_zpl_stages,
                     _zpl_write_stages=cls.pool_zpl_write_stages,
                     _zpl_txg_stages=cls.pool_zpl_txg_stages,
                     _zpl_sync_stages=cls.pool_zpl_sync_stages,
                     engine_utc=True, pool_data=cls.pool_data, pool_diagnose='run', pool_recovery_check=cls.recovery_check, pool_namespace=cls.pool_namespace,
                     pool_diagnostic_driver=runtime.pool_diagnostic_driver,
                     namespace_driver=runtime.namespace_driver)
        exec(compile(ast.Module(body=body, type_ignores=[]), '<actual pool data adapter>', 'exec'), scope)
        adapted = scope['driver_text']
        cls.adapted = adapted
        start = adapted.index('        let tags =')
        end = adapted.index('        check(call(0x20003, owner, tags.len() as u64 * 8)', start)
        loop = adapted[start:end]
        source = '''use std::cell::RefCell;
thread_local! { static ROWS: RefCell<[[u8;8];32]> = const { RefCell::new([[0;8];32]) }; }
fn check(ok: bool) { if !ok { std::process::exit(90); } }
fn byte(_owner: u64, offset: u64) -> u8 {
    ROWS.with(|r| r.borrow()[offset as usize / 8][offset as usize % 8])
}
fn end(code: u64) -> ! { std::process::exit(code as i32); }
fn main() {
    let owner=1; let stale=0;
    let args: Vec<String> = std::env::args().collect();
    let dirty_row: usize=args[1].parse().unwrap();
    let dirty_byte: usize=args[2].parse().unwrap();
    let seed_tags=if cfg!(pool_import) { b"BIUVWLP????????OAMT????????SDJFR".as_slice() }
                  else { b"BIUVWP????????CAT????????SDJFR".as_slice() };
    check(seed_tags.len() <= 32);
    ROWS.with(|r| {
        let mut rows=r.borrow_mut();
        for (i,tag) in seed_tags.iter().enumerate() {
            rows[i]=[*tag, if i+1==seed_tags.len(){0}else{1}, if i==0{1}else{2},0,0,32,0,32];
            if !cfg!(pool_import) && i==14 { rows[i]=[b'C',0,0,0,0,0,0,0]; }
        }
        if dirty_row < seed_tags.len() { rows[dirty_row][dirty_byte] ^= 1; }
        if let Some(target) = args.get(3) {
            let bytes = target.parse::<u64>().unwrap().to_le_bytes();
            for i in 0..8 { rows[19 + i][0] = bytes[i]; }
        }
    });
''' + loop + '\n}\n'
        if cls.recovery_check == 'capacity':
            source = source.replace('b"BIUVWP????????CAT????????SDJFR"', r'b"BIUVWP????????CAT????????SQ\x1cDJFR"')
        if cls.pool_namespace and not (cls.pool_zpl_write or cls.pool_zpl_recover):
            source = source.replace('b"BIUVWLP????????OAMT????????SDJFR"', 'b"BIUVWLP????????OAMZDJFR"')
        if cls.pool_zpl_stages:
            source = source.replace('b"BIUVWLP????????OAMT????????SDJFR"', 'b"BIUVWLPOAMTbeicpvrw????????SDJFR"' if cls.pool_zpl_sync_stages else 'b"BIUVWLPOAMTbqsluodw????????SDJFR"' if cls.pool_zpl_txg_stages else 'b"BIUVWLPOAMTeabcdwsf????????SDJFR"' if cls.pool_zpl_write_stages else 'b"BIUVWLPOAMTorhc12vx????????SDJFR"')
        cls.host_source = source
        for label, flags in ((('reader', ['--cfg', 'pool_import']),) if cls.pool_namespace else
                             (('writer', []), ('reader', ['--cfg','pool_import']))):
            path=cls.output/(label+'.rs'); path.write_text(source)
            result=subprocess.run(['rustc','+1.98.0','--edition=2024','-Dwarnings','-C','opt-level=2',
                                   '--cfg','pool_create',*flags,str(path),'-o',str(cls.output/label)],
                                  capture_output=True,timeout=30)
            if result.returncode: raise RuntimeError(result.stderr.decode())

    def run_loop(self, label, row=32, byte=0):
        return subprocess.run([str(self.output/label),str(row),str(byte)],
                              capture_output=True,timeout=5).returncode

    def test_only_selected_fingerprint_and_target_bytes_vary(self):
        for label, count, variable in (
                ('writer',self.writer_rows,set(range(6,14))|set(range(17,25))),
                ('reader',32,set(range(7,15))|set(range(19,27)))):
            self.assertEqual(self.run_loop(label),0)
            for row in range(count):
                with self.subTest(label=label,row=row):
                    self.assertEqual(self.run_loop(label,row,0),0 if row in variable else 90)

    def test_resource_and_raw_padding_guards_survive_variable_fields(self):
        for label, count in (('writer',self.writer_rows),('reader',32)):
            for row in range(count):
                with self.subTest(label=label,row=row):
                    # Bad total pages must reject, even in a varying target row.
                    self.assertEqual(self.run_loop(label,row,6),90)
            self.assertEqual(self.run_loop(label,0,1),90)
            self.assertEqual(self.run_loop(label,count-1,1),90)
        for byte in range(1,8):
            self.assertEqual(self.run_loop('writer',14,byte),90)


class PoolCapacityDriver(PoolDataDriver):
    recovery_check = 'capacity'
    writer_rows = 32


class PoolNamespaceDriver(PoolDataDriver):
    pool_data = False
    pool_namespace = True

    def test_only_selected_fingerprint_and_target_bytes_vary(self):
        self.assertEqual(self.run_loop('reader'), 0)
        for row in range(23):
            self.assertEqual(self.run_loop('reader', row, 0), 0 if 7 <= row < 15 else 90)

    def test_resource_and_raw_padding_guards_survive_variable_fields(self):
        for row in range(23):
            self.assertEqual(self.run_loop('reader', row, 6), 90)
        self.assertEqual(self.run_loop('reader', 0, 1), 90)
        self.assertEqual(self.run_loop('reader', 22, 1), 90)


class PoolNamespaceWriteDriver(PoolNamespaceDriver):
    pool_zpl_write = True
    grant_rights = 7

    def test_only_selected_fingerprint_and_target_bytes_vary(self):
        self.assertEqual(self.run_loop('reader'), 0)
        for row in range(32):
            self.assertEqual(self.run_loop('reader', row, 0),
                             0 if row in {*range(7, 15), *range(19, 27)} else 90)

    def test_resource_and_raw_padding_guards_survive_variable_fields(self):
        for row in range(32):
            for byte in (1, 3, 6):
                expected = 90 if byte in (1, 6) or (byte == 3 and row == 0) else 0
                self.assertEqual(self.run_loop('reader', row, byte), expected)

    def test_zero_and_stale_assigned_targets_reject(self):
        for target in (0, 1, 781, 782, 783, 788, 0xffffffffffffffff):
            result = subprocess.run([str(self.output / 'reader'), '32', '0', str(target)],
                                    capture_output=True, timeout=5)
            self.assertEqual(result.returncode, 90 if target <= 782 else 0)

    def test_actual_delegation_record_and_context_drift(self):
        region = next(line.strip() for line in self.adapted.splitlines()
                      if 'let region = ' in line)
        source = 'fn main() { ' + region + f' assert_eq!(region, [8, 2097152, {self.grant_rights}]); }}'
        path = self.output / 'grant.rs'
        path.write_text(source)
        binary = self.output / 'grant'
        result = subprocess.run(['rustc', '+1.98.0', '--edition=2024', '-Dwarnings',
                                 '--cfg', 'pool_create', '--cfg', 'pool_import',
                                 str(path), '-o', str(binary)], capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(subprocess.run([str(binary)], capture_output=True, timeout=5).returncode, 0)
        with self.assertRaisesRegex(ValueError, 'context changed'):
            runtime.namespace_driver(self.adapted, writable=True)

    def test_compiling_missing_target_guard_accepts_forbidden_zero(self):
        self.assertEqual(self.host_source.count('check(target > 782);'), 1)
        path = self.output / 'missing-target.rs'
        path.write_text(self.host_source.replace('check(target > 782);', 'let _ = target;', 1))
        binary = self.output / 'missing-target'
        result = subprocess.run(['rustc', '+1.98.0', '--edition=2024', '-Dwarnings',
                                 '--cfg', 'pool_create', '--cfg', 'pool_import',
                                 str(path), '-o', str(binary)], capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(subprocess.run([str(binary), '32', '0', '0'],
                                       capture_output=True, timeout=5).returncode, 0)


class PoolNamespaceRecoverDriver(PoolNamespaceWriteDriver):
    pool_zpl_write = False
    pool_zpl_recover = True
    grant_rights = 1


class PoolCorruptLabels(unittest.TestCase):
    """Exact stopped-media mutation and pre-import negative native oracle."""

    @staticmethod
    def media():
        data = bytearray([165]) * (64 * 1024 * 1024 + 8192)
        for start in (0, 262144, 64 * 1024 * 1024 - 524288, 64 * 1024 * 1024 - 262144):
            data[4096 + start + 16384] = 1
        return bytes(data)

    def test_only_four_encoding_bytes_change_with_geometry_and_canaries(self):
        before = self.media()
        after, record = runtime.corrupt_pool_label_headers(before)
        previous = 0
        for change in record['changes']:
            offset = change['offset']
            self.assertEqual(before[previous:offset], after[previous:offset])
            self.assertEqual((before[offset], after[offset]), (1, 255))
            previous = offset + 1
        self.assertEqual(before[previous:], after[previous:])
        self.assertEqual(record['pre_corruption_sha256'], hashlib.sha256(before).hexdigest())
        self.assertEqual(record['post_corruption_sha256'], hashlib.sha256(after).hexdigest())
        for data in (before[:-1], after, bytes([0]) + before[1:], before[:-1] + bytes([0])):
            with self.assertRaises(ValueError): runtime.corrupt_pool_label_headers(data)

    def test_actual_import_guard_mutates_only_after_clean_stop_and_exact_media(self):
        node = next(n for n in ast.walk(ast.parse(Path(runtime.__file__).read_text()))
                    if isinstance(n, ast.If) and ast.unparse(n.test) ==
                    "name == 'pool-import' and pool_diagnose != 'build' and (not pool_namespace)")
        code = compile(ast.Module(body=[node], type_ignores=[]), '<corrupt stopped media guard>', 'exec')
        with tempfile.TemporaryDirectory(prefix='aether-label-corruption-') as directory:
            disk = Path(directory)/'disposable.raw'; before = self.media(); disk.write_bytes(before)
            prior = dict(name='pool-create', status='pass', vm_run_returned=True,
                         disk_sha256=runtime.sha(disk))
            scope = dict(name='pool-import', pool_diagnose='run', pool_corrupt_labels=True,
                         before_disk=before, record={'cases':[prior,{}]}, row={},
                         sha=runtime.sha, block_disk=disk,
                         corrupt_pool_label_headers=runtime.corrupt_pool_label_headers, pool_interrupt=False, pool_uncommitted=False, pool_recovery_check=None, pool_namespace=False,
                         check_pool_import_media=runtime.check_pool_import_media)
            for key, value in (('status','failed'),('vm_run_returned',False),('disk_sha256','foreign')):
                scope['record'] = {'cases':[prior|{key:value},{}]}
                with self.assertRaisesRegex(ValueError,'completed create/VM teardown'): exec(code,scope)
                self.assertEqual(runtime.sha(disk),prior['disk_sha256'])
            scope['record']={'cases':[prior,{}]}; exec(code,scope)
            mutation=scope['row']['label_corruption']
            self.assertEqual(mutation['pre_corruption_sha256'],prior['disk_sha256'])
            self.assertEqual(runtime.sha(disk),mutation['post_corruption_sha256'])
            self.assertEqual(disk.read_bytes(),scope['before_disk'])

    def test_exact_rejection_denies_wrong_phase_terminal_cleanup_or_order(self):
        rows = [f'NATIVE observation slot=0 generation=1 offset={i*8} byte={byte}'
                for i,byte in enumerate(b'BIUVWL')]
        rows += ['NATIVE terminal slot=0 generation=1 kind=1 detail=873',
                 'NATIVE CLEANUP v=1 slot=0 generation=1 phase=1 selected=0 pages=8192 reclaimed=0',
                 'NATIVE CLEANUP v=1 slot=0 generation=1 phase=2 selected=2 pages=8192 reclaimed=0',
                 'NATIVE supervisor result=401 reclaimed=0',
                 'AETHER PANIC: native C profile rejected']
        render=lambda lines:'\n'.join(lines)+'\n'
        result=runtime.check_pool_corrupt_label_trace(render(rows))
        self.assertFalse(result['pool_import_attempted']); self.assertFalse(result['guest_reclaim_qualified'])
        for index in range(len(rows)):
            with self.subTest(index=index):
                with self.assertRaises(ValueError):runtime.check_pool_corrupt_label_trace(render(rows[:index]+rows[index+1:]))
                with self.assertRaises(ValueError):runtime.check_pool_corrupt_label_trace(render(rows+rows[index:index+1]))
        for changed in (rows[:5]+[rows[5].replace('byte=76','byte=80')]+rows[6:],
                        rows[:6]+[rows[6].replace('detail=873','detail=0')]+rows[7:],
                        rows[:8]+[rows[8].replace('reclaimed=0','reclaimed=1')]+rows[9:],
                        rows[:6]+[rows[7],rows[6]]+rows[8:], rows+['AETHER NATIVE BLOCK PASS']):
            with self.assertRaises(ValueError):runtime.check_pool_corrupt_label_trace(render(changed))

    def test_explicit_selector_denies_before_artifact_intake(self):
        for kwargs in ({},dict(pool_data=True),dict(pool_data=True,pool_create=True,pool_diagnose='run',case='pool-create')):
            with self.assertRaisesRegex(ValueError,'corrupt labels requires'):
                runtime.suite(Path('/absent'),pool_corrupt_labels=True,**kwargs)
        result=subprocess.run([sys.executable,str(Path(runtime.__file__)), '--delivery','/absent',
                               '--pool-corrupt-labels'],capture_output=True,timeout=5)
        self.assertEqual(result.returncode,64)
        self.assertIn(b'--pool-corrupt-labels requires',result.stderr)


class PoolInterruptedRecovery(unittest.TestCase):
    @staticmethod
    def trace(target=6):
        tags = b'BIUVWP' + bytes(range(1, 9)) + b'CAT' + target.to_bytes(8, 'little') + b'SK'
        return ''.join(f'NATIVE observation slot=0 generation=1 offset={index * 8} byte={byte}\n'
                       for index, byte in enumerate(tags))

    def test_exact_checkpoint_denies_partial_foreign_zero_and_clean_results(self):
        serial = self.trace()
        result = runtime.check_pool_interrupted_trace(serial)
        self.assertEqual(result['assigned_target_txg'], 6)
        self.assertFalse(result['clean_export_observed'])
        self.assertFalse(result['guest_reclaim_qualified'])
        lines = serial.splitlines()
        for index in range(len(lines)):
            with self.subTest(index=index), self.assertRaises(ValueError):
                runtime.check_pool_interrupted_trace('\n'.join(lines[:index] + lines[index + 1:]))
        for bad in (self.trace(0), serial + lines[-1] + '\n',
                    serial.replace('generation=1', 'generation=2', 1),
                    serial.replace('byte=75', 'byte=68'),
                    serial.replace('offset=208', 'offset=216'),
                    serial.replace('byte=75', 'byte=256')):
            with self.assertRaises(ValueError):
                runtime.check_pool_interrupted_trace(bad)
        for suffix in ('NATIVE terminal slot=0 generation=1 kind=1 detail=0',
                       'NATIVE CLEANUP v=1 slot=0 generation=1 phase=1 selected=0 pages=8192 reclaimed=0',
                       'NATIVE supervisor result=100 reclaimed=3', 'AETHER NATIVE BLOCK PASS',
                       'AETHER PANIC: unexpected'):
            with self.assertRaises(ValueError):
                runtime.check_pool_interrupted_trace(serial + suffix + '\n')

    def test_stopped_media_and_matching_recovered_target_are_both_required(self):
        writer = runtime.check_pool_interrupted_trace(self.trace())
        reader = dict(readonly_data_readback=True, recovered_target_txg=6)
        with tempfile.TemporaryDirectory(prefix='aether-interrupted-media-') as directory:
            disk = Path(directory) / 'disposable.raw'
            disk.write_bytes(b'owned stopped media')
            writer.update(name='pool-create', status='pass', vm_run_returned=True,
                          disk_sha256=runtime.sha(disk))
            runtime.check_pool_import_media(writer, disk, interrupted=True)
            result = runtime.check_pool_data_pair(writer, reader, interrupted=True)
            self.assertTrue(result['interrupted_data_recovery_qualified'])
            self.assertNotIn('fresh_data_pair_qualified', result)
            for key, value in (('status', 'failed'), ('vm_run_returned', False),
                               ('disk_sha256', 'foreign'), ('writer_vm_interrupted', False),
                               ('ordered_provider_witness', False), ('assigned_target_txg', 0),
                               ('clean_export_observed', True), ('guest_reclaim_qualified', True)):
                with self.subTest(key=key), self.assertRaises(ValueError):
                    runtime.check_pool_import_media(writer | {key: value}, disk, interrupted=True)
            for key, value in (('vm_run_returned', False), ('writer_vm_interrupted', False),
                               ('checkpoint_after_sync', False), ('clean_export_observed', True),
                               ('guest_reclaim_qualified', True), ('ordered_provider_witness', False)):
                with self.subTest(key=key), self.assertRaises(ValueError):
                    runtime.check_pool_data_pair(writer | {key: value}, reader, interrupted=True)
            with self.assertRaises(ValueError):
                runtime.check_pool_data_pair(writer, reader | {'recovered_target_txg': 7}, interrupted=True)

    def test_selector_rejects_before_intake_and_cannot_mix_corruption(self):
        for kwargs in ({}, dict(pool_data=True),
                       dict(pool_data=True, pool_create=True, pool_diagnose='run', case='pool-create'),
                       dict(pool_data=True, pool_create=True, pool_diagnose='run', case='pool-import',
                            pool_corrupt_labels=True)):
            with self.assertRaisesRegex(ValueError, 'interruption requires'):
                runtime.suite(Path('/absent'), pool_interrupt=True, **kwargs)
        result = subprocess.run([sys.executable, runtime.__file__, '--delivery', '/absent',
                                 '--pool-interrupt'], capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 64)
        self.assertIn(b'--pool-interrupt requires', result.stderr)


class PoolUncommittedRecovery(unittest.TestCase):
    @staticmethod
    def trace(baseline=6, candidate=7):
        tags = b'BIUVWPCAT' + baseline.to_bytes(8, 'little') + b'SH' + candidate.to_bytes(8, 'little') + b'K'
        return ''.join(f'NATIVE observation slot=0 generation=1 offset={index * 8} byte={byte}\n'
                       for index, byte in enumerate(tags))

    def test_trace_requires_baseline_and_newer_held_candidate(self):
        serial = self.trace()
        result = runtime.check_pool_interrupted_trace(serial, uncommitted=True)
        self.assertEqual((result['assigned_target_txg'], result['uncommitted_candidate_txg']), (6, 7))
        self.assertTrue(result['checkpoint_before_commit'])
        self.assertFalse(result['checkpoint_after_sync'])
        self.assertFalse(result['candidate_committed'])
        lines = serial.splitlines()
        for index in range(len(lines)):
            with self.subTest(index=index), self.assertRaises(ValueError):
                runtime.check_pool_interrupted_trace('\n'.join(lines[:index] + lines[index + 1:]), True)
        for bad in (self.trace(0), self.trace(6, 0), self.trace(6, 6), self.trace(6, 5),
                    serial + lines[-1] + '\n', serial.replace('offset=216', 'offset=208'),
                    serial.replace('generation=1', 'generation=2', 1),
                    serial.replace('byte=75', 'byte=256'),
                    serial + 'NATIVE terminal slot=0 generation=1 kind=1 detail=0\n',
                    serial + 'NATIVE supervisor result=100 reclaimed=3\n',
                    serial + 'NATIVE CLEANUP v=1 slot=0 generation=1 phase=1 selected=0 pages=8192 reclaimed=0\n',
                    serial + 'AETHER NATIVE BLOCK PASS\n', serial + 'AETHER PANIC: unexpected\n'):
            with self.assertRaises(ValueError): runtime.check_pool_interrupted_trace(bad, True)
        with self.assertRaises(ValueError): runtime.check_pool_interrupted_trace(serial)
        with self.assertRaises(ValueError):
            runtime.check_pool_interrupted_trace(PoolInterruptedRecovery.trace(), True)

    def test_stopped_media_and_baseline_only_recovery_required(self):
        writer = runtime.check_pool_interrupted_trace(self.trace(), True)
        reader = dict(readonly_data_readback=True, recovered_target_txg=6)
        with tempfile.TemporaryDirectory(prefix='aether-uncommitted-media-') as directory:
            disk = Path(directory) / 'disposable.raw'; disk.write_bytes(b'owned stopped media')
            writer.update(name='pool-create', status='pass', vm_run_returned=True, disk_sha256=runtime.sha(disk))
            runtime.check_pool_import_media(writer, disk, True, True)
            result = runtime.check_pool_data_pair(writer, reader, True, True)
            self.assertTrue(result['uncommitted_recovery_qualified'])
            self.assertNotIn('interrupted_data_recovery_qualified', result)
            for key, value in (('status','failed'), ('vm_run_returned',False), ('disk_sha256','foreign'),
                               ('writer_vm_interrupted',False), ('checkpoint_before_commit',False),
                               ('baseline_synced',False), ('uncommitted_candidate_txg',6),
                               ('candidate_committed',True), ('ordered_provider_witness',False),
                               ('clean_export_observed',True), ('guest_reclaim_qualified',True)):
                with self.subTest(key=key), self.assertRaises(ValueError):
                    runtime.check_pool_import_media(writer | {key:value}, disk, True, True)
            for key, value in (('checkpoint_before_commit',False), ('baseline_synced',False),
                               ('uncommitted_candidate_txg',6), ('candidate_committed',True),
                               ('assigned_DMU_transaction',False)):
                with self.subTest(key=key), self.assertRaises(ValueError):
                    runtime.check_pool_data_pair(writer | {key:value}, reader, True, True)
            for target in (0,5,7):
                with self.assertRaises(ValueError):
                    runtime.check_pool_data_pair(writer, reader | {'recovered_target_txg':target}, True, True)
            with self.assertRaises(ValueError): runtime.check_pool_data_pair(writer, reader, True)

    def test_uncommitted_selector_requires_interrupted_pair_before_intake(self):
        from openzfs_elapsed import prepare
        from openzfs_volume import build
        with self.assertRaisesRegex(ValueError, 'uncommitted pool requires'):
            prepare(Path('/absent'), None, volume_pool_uncommitted=True)
        with self.assertRaisesRegex(ValueError, 'uncommitted pool requires'):
            build(Path('/absent'), [], None, pool_uncommitted=True)
        for kwargs in ({},dict(pool_data=True, pool_create=True, pool_diagnose='run',case='pool-import')):
            with self.assertRaisesRegex(ValueError,'uncommitted pool requires'):
                runtime.suite(Path('/absent'),pool_uncommitted=True,**kwargs)
        result=subprocess.run([sys.executable,runtime.__file__,'--delivery','/absent','--pool-uncommitted'],
                              capture_output=True,timeout=5)
        self.assertEqual(result.returncode,64)
        self.assertIn(b'--pool-uncommitted requires --pool-interrupt',result.stderr)


class PoolBuildFailureRetention(unittest.TestCase):
    def test_actual_finally_keeps_error_and_compacts_without_cases(self):
        tree=ast.parse(Path(runtime.__file__).read_text())
        suite=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='suite')
        final=next(n.finalbody for n in suite.body if isinstance(n,ast.Try) and n.finalbody)
        code=compile(ast.Module(body=final,type_ignores=[]),'<actual build failure retention>','exec')
        with tempfile.TemporaryDirectory(prefix='aether-empty-pool-cases-') as directory:
            out=Path(directory)
            for cases in (None,[],[dict(name='pool-import',status='failed')]):
                record=dict(status='failed',error='original compiler failure')
                if cases is not None:record['cases']=cases
                compacted=[]
                scope=dict(out=out,record=record,pool_diagnose='build',pool_create=False,_zpl_stage=None,
                           _fs_launch_output=None,
                           json=json,compact_run=lambda path,data:compacted.append((path,data.copy())))
                exec(code,scope)
                self.assertEqual(len(compacted),1)
                self.assertEqual(compacted[0][1]['error'],'original compiler failure')
                self.assertEqual(json.loads((out/'results.json').read_text())['status'],'failed')
