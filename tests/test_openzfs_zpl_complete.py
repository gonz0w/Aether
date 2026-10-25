# SPDX-License-Identifier: BSD-2-Clause
"""Complete writer build gate and actual one-write probe under faulting APIs."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import service_runtime_smoke as runtime
import openzfs_elapsed as elapsed
import openzfs_volume as volume


class ZplControllerTrace(unittest.TestCase):
    @staticmethod
    def trace(target=788):
        tags = b'BIUVWLPabcdefghOAMT' + target.to_bytes(8, 'little') + b'SDJFR'
        rows = [f'NATIVE observation slot=0 generation=1 offset={i * 8} byte={b}'
                for i, b in enumerate(tags)]
        rows += [f'NATIVE observation slot=0 generation={g} offset={i * 8} byte={b}'
                 for g in (2, 3) for i, b in enumerate(b'BNR')]
        return '\n'.join(rows)

    def test_writer_is_32_rows_and_has_no_readonly_or_recovery_claim(self):
        result = runtime.check_zpl_write_trace(self.trace())
        self.assertEqual(result['assigned_target_txg'], 788)
        self.assertEqual(result['namespace_primary_rows'] * 8, 256)
        self.assertTrue(result['clean_export_observed'])
        self.assertNotIn('recovered_target_txg', result)
        self.assertNotIn('readonly_pool_retired', result)
        for target in (0, 1, 782):
            with self.assertRaises(ValueError):
                runtime.check_zpl_write_trace(self.trace(target))

    def test_malformed_missing_extra_wrong_identity_and_phases_reject(self):
        text = self.trace()
        for changed in (text + '\nNATIVE observation malformed',
                        text + '\n' + text.splitlines()[0],
                        text.replace('offset=248', 'offset=256'),
                        text.replace('generation=3', 'generation=4'),
                        text.replace('byte=83', 'byte=90'),
                        '\n'.join(text.splitlines()[:31] + text.splitlines()[32:])):
            with self.subTest(changed=changed[-70:]), self.assertRaises(ValueError):
                runtime.check_zpl_write_trace(changed)


class ZplCompleteGate(unittest.TestCase):

    def test_cli_run_is_rejected_without_accessing_delivery(self):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/service_runtime_smoke.py'), '--pool-zpl-write', '--pool-namespace', '--pool-diagnose', 'run', '--delivery', '/absent'], capture_output=True, text=True, timeout=5)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('ZPL writer requires isolated build-only namespace profile', result.stderr)

    def test_run_and_ambiguous_selection_reject_before_dependency_intake(self):
        with patch.object(runtime, 'intake', side_effect=AssertionError('dependency intake')):
            for options in ({}, {'pool_namespace': True, 'pool_diagnose': 'run'}, {'pool_namespace': True, 'pool_diagnose': 'build', 'namespace_ipc': True}):
                with self.subTest(options=options):
                    with self.assertRaisesRegex(ValueError, 'isolated build-only'):
                        runtime.suite(Path('/absent'), pool_zpl_write=True, **options)
        with self.assertRaisesRegex(ValueError, 'isolated namespace'):
            elapsed.prepare(Path('/absent'), None, volume_pool_zpl_write=True)
        with self.assertRaisesRegex(ValueError, 'isolated namespace'):
            volume.build(Path('/absent'), None, None, pool_zpl_write=True)

class ZplWriteProbe(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-zpl-complete-probe-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.out = Path(cls.temp.name)
        cls.body = '\n'.join((l for l in (ROOT / 'user/storage/openzfs-volume/zpl-write-probe.c').read_text().splitlines() if not l.startswith('#include'))) + '\n'
        cls.compiler = '/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang'
        cls.sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        cls.binary = cls.compile(cls.body, 'probe')

    @classmethod
    def compile(cls, body, name):
        (cls.out / 'write-probe.inc').write_text(body)
        binary = cls.out / name
        result = subprocess.run([cls.compiler, '-isysroot', cls.sdk, '-std=gnu11', '-O2', '-Wall', '-Wextra', '-Werror', '-I' + str(cls.out), '-I' + str(ROOT / 'user/storage/openzfs-volume'), str(ROOT / 'tests/fixtures/openzfs_zpl_write_probe.c'), '-o', str(binary)], capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        return binary

    def test_success_and_every_selected_contract_denial(self):
        for mode in [0, *range(1, 8), *range(9, 19)]:
            with self.subTest(mode=mode):
                result = subprocess.run([str(self.binary), str(mode)], capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_all_390_reachable_api_failures_close_without_retry(self):
        for mode in range(101, 491):
            with self.subTest(mode=mode):
                result = subprocess.run([str(self.binary), str(mode)], capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_compiling_omissions_fail_semantic_oracles(self):
        for name, old, new, mode in (('baseline', 'memcmp(original, pristine, sizeof(original))', '((void)pristine,0)', 3), ('readback', 'memcmp(actual, predicted, sizeof(actual))', '0', 18), ('state', 'result.state != AETHER_ZPL_SYNCED', '0', 16), ('close', 'aether_zpl_close(&view);', 'if (0) aether_zpl_close(&view);', 0)):
            with self.subTest(name=name):
                self.assertEqual(self.body.count(old), 1)
                binary = self.compile(self.body.replace(old, new, 1), name)
                result = subprocess.run([str(binary), str(mode)], capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 96, result.stdout + result.stderr)
                self.assertIn('HOST ZPL PROBE oracle96', result.stderr)

    def test_missing_wrong_stage_or_errno_fails_diagnostic_oracle(self):
        for name, old, new in (
                ('stage', 'stage = 6;', 'stage = 5;'),
                ('errno', '((uint32_t)error >> (8 * i))', '((uint32_t)error >> (8 * i + 1))'),
                ('missing', "aether_engine_utc_phase('E');", "if (0) aether_engine_utc_phase('E');")):
            with self.subTest(name=name):
                self.assertEqual(self.body.count(old), 1)
                binary = self.compile(self.body.replace(old, new, 1), name)
                result = subprocess.run([str(binary), '13'], capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 96, result.stdout + result.stderr)
                self.assertIn('HOST ZPL PROBE oracle96', result.stderr)

class ZplImportFlow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-zpl-import-flow-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.out = Path(cls.temp.name)
        cls.body = '\n'.join((l for l in (ROOT / 'user/storage/openzfs-volume/spa-zpl-write.inc').read_text().splitlines() if not l.startswith('#include'))) + '\n'
        cls.compiler = '/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang'
        cls.sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        cls.binary = cls.compile(cls.body, 'import')

    @classmethod
    def compile(cls, body, name):
        (cls.out / 'zpl-import.inc').write_text(body)
        binary = cls.out / name
        result = subprocess.run([cls.compiler, '-isysroot', cls.sdk, '-std=gnu11', '-O2', '-Wall', '-Wextra', '-Werror', '-I' + str(cls.out), str(ROOT / 'tests/fixtures/openzfs_zpl_import.c'), '-o', str(binary)], capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        return binary

    def test_import_failures_close_and_export_follows_drain(self):
        for mode in [0, 1, *range(20, 31), *range(101, 113)]:
            with self.subTest(mode=mode):
                result = subprocess.run([str(self.binary), str(mode)], capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_compiling_drain_close_and_order_omissions_fail(self):
        for name, old, new, mode in (('drain', 'dmu_buf_user_evict_wait();', 'if (0) dmu_buf_user_evict_wait();', 0), ('borrow', 'spa_close(spa, FTAG);', 'if (0) spa_close(spa, FTAG);', 0), ('ordered', 'remaining || aether_pool_hooks_check_ordered()', 'remaining || (0 && aether_pool_hooks_check_ordered())', 29), ('quota', "aether_engine_utc_phase('S');", "aether_engine_utc_phase('S'); aether_engine_utc_phase('Z');", 0)):
            with self.subTest(name=name):
                self.assertEqual(self.body.count(old), 1)
                binary = self.compile(self.body.replace(old, new, 1), name)
                result = subprocess.run([str(binary), str(mode)], capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 97, result.stdout + result.stderr)
                self.assertIn('HOST ZPL IMPORT oracle97', result.stderr)
if __name__ == '__main__':
    unittest.main()
