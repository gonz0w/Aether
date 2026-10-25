# SPDX-License-Identifier: BSD-2-Clause
"""Approved fixed writer tick budget: preparation and admission denials."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import test_zpl_pair as controls
import test_openzfs_zpl_sync_stages as sync
import service_runtime_smoke as runtime
import zpl_pair as pair

ROOT = pair.ROOT
FLAG = '-Dnative-service-zpl-budget=true'


class ZplTickBudget(unittest.TestCase):
    def fixture(self):
        f = controls.PairControls()
        f.setUp()
        self.addCleanup(f.doCleanups)
        f.builds['baseline'] = copy.deepcopy(f.builds['reader'])
        f.builds['baseline']['pool_zpl_recover'] = False
        (f.output / 'baseline').mkdir()
        for name in ('aether.iso', 'engine.elf'):
            (f.output / 'baseline' / name).write_bytes((f.output / 'reader' / name).read_bytes())
        f.builds['writer'].update(pool_zpl_repeat=True, pool_zpl_stages=True,
            pool_zpl_txg_stages=True, pool_zpl_sync_stages=True, pool_zpl_writer_budget=True)
        for role, b in f.builds.items():
            b['commands'] = [{'argv': ['zig', 'build'] + ([FLAG] if role == 'writer' else [])}]
        import openzfs_fs_bridge as bridge
        source = bridge.recovery_source((ROOT / 'user/storage/openzfs-volume/zpl-recovery.c').read_text(), True)
        f.builds['reader']['pool_recovery_writer_60s'] = True
        f.builds['reader']['port'] = {'volume': {'namespace_objects': {
            'recovery-selected-source': hashlib.sha256(source.encode()).hexdigest()}}}
        return f

    def verify(self, f):
        with patch.object(runtime, 'sealed'):
            pair.verify_prepared(f.output, f.builds, True, True, False, True, True, True, writer_60s=True)

    def test_build_selection_and_actual_option_are_both_required_only_for_writer(self):
        f = self.fixture()
        self.verify(f)
        original = copy.deepcopy(f.builds)
        for role in ('baseline', 'writer', 'reader'):
            for change in ('flag', 'missing-option', 'wrong-value', 'duplicate-option', 'foreign-option'):
                f.builds = copy.deepcopy(original)
                b = f.builds[role]
                if change == 'flag':
                    b['pool_zpl_writer_budget'] = role != 'writer'
                elif change == 'missing-option':
                    if role != 'writer':
                        continue
                    b['commands'] = []
                elif change == 'wrong-value':
                    b['commands'] = [{'argv': ['zig', 'build', FLAG.replace('true', 'false')]}]
                else:
                    b['commands'][0]['argv'] += [FLAG] * (2 if change == 'duplicate-option' else 1)
                    if change == 'foreign-option' and role == 'writer':
                        continue
                with self.subTest(role=role, change=change), self.assertRaises(ValueError):
                    self.verify(f)

    def test_defaults_cannot_silently_consume_extended_builds(self):
        f = self.fixture()
        with patch.object(runtime, 'sealed'), self.assertRaises(ValueError):
            pair.verify_prepared(f.output, f.builds, True, True, False, True, True, writer_60s=True)
        f.builds['writer']['pool_zpl_writer_budget'] = False
        with patch.object(runtime, 'sealed'), self.assertRaisesRegex(ValueError, 'kernel tick budget'):
            pair.verify_prepared(f.output, f.builds, True, True, False, True, True, writer_60s=True)

    def test_invalid_cli_pair_and_runtime_selection_reject_before_intake(self):
        for args in (['--writer-ticks-6000'], ['--writer-ticks-6000', '--sync-stages']):
            result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/zpl_pair.py'),
                *args, '--delivery', '/absent', '--utc-delivery', '/absent'],
                capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 64)
            self.assertIn('writer tick budget requires writer60', result.stderr)
        with patch.object(runtime, 'intake', side_effect=AssertionError('intake')):
            for kwargs in ({'_zpl_writer_budget': True}, {'_zpl_writer_budget': 6000},
                           {'_zpl_writer_budget': True, '_zpl_sync_stages': True,
                            '_zpl_txg_stages': True, '_zpl_stages': True, '_zpl_repeat': True}):
                with self.assertRaisesRegex(ValueError, 'writer tick budget'):
                    runtime.suite(Path('/absent'), **kwargs)
        for value in (True, 6000):
            with self.assertRaises(ValueError):
                pair.pair(Path('/absent'), Path('/absent'), writer_ticks_6000=value)

    def test_actual_runtime_option_emission_is_writer_only(self):
        tree = ast.parse(Path(runtime.__file__).read_text())
        suite = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'suite')
        nodes = [n for n in ast.walk(suite) if isinstance(n, ast.If) and
                 isinstance(n.test, ast.Name) and n.test.id == '_zpl_writer_budget']
        self.assertEqual(len(nodes), 1)
        for selected in (False, True):
            scope = {'_zpl_writer_budget': selected, 'options': []}
            exec(compile(ast.Module(body=nodes, type_ignores=[]), '<actual kernel option>', 'exec'), scope)
            self.assertEqual(scope['options'], [FLAG] if selected else [])

    def test_extended_dispatch_preserves_baseline_file_cleanup_and_recovery_gates(self):
        f = controls.PairControls(); f.setUp(); self.addCleanup(f.doCleanups)
        result = f.execute(writer_text=sync.success(), txg_worker_diagnostic=True,
            sync_stages=True, writer_60s=True, writer_ticks_6000=True)
        self.assertEqual([(c['role'], c['watchdog_seconds'], c['kernel_tick_limit'])
                          for c in result['cases']],
                         [('baseline', 30, 3000), ('writer', 60, 6000), ('reader', 30, 3000)])
        broken = sync.success().replace('phase=7', 'phase=6', 1)
        with self.assertRaises(ValueError):
            f.execute(writer_text=broken, txg_worker_diagnostic=True,
                sync_stages=True, writer_60s=True, writer_ticks_6000=True)
        self.assertEqual(f.launched, ['baseline', 'writer'])

    def test_actual_build_rejects_option_without_required_profile_before_build(self):
        release = ['-Drelease-artifact=true', '-Dsmp=false', '-Dnative-c-image=/absent',
            '-Dnative-memory=true', '-Dnative-memory-large=true', '-Dnative-image-large=true',
            '-Dnative-backing=true', '-Dnative-service-memory=true', '-Dnative-threads=true',
            '-Dnative-thread-pair=true', '-Dnative-thread-reuse=true', '-Dnative-thread-origin=true',
            '-Dnative-service-workers=true', '-Dnative-clock=true', '-Dnative-rtc=true',
            '-Dnative-entropy=true', '-Dnative-service-block=true', '-Dnative-service-cleanup-trace=true']
        for flags in ([], release):
            result = subprocess.run(['zig', 'build', '--help', FLAG, *flags,
                '--cache-dir', str(ROOT / '.zig-cache'), '--global-cache-dir',
                str(ROOT / '.zig-cache/global')], capture_output=True, text=True, timeout=180)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('ZPL tick budget requires the private BSP service writer diagnostic', result.stderr)
