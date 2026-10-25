# SPDX-License-Identifier: BSD-2-Clause
"""Modified-file reader preparation; API doubles are not native recovery."""
import json
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


class RecoveryGate(unittest.TestCase):
    def test_invalid_api_cli_and_lower_builder_selection_reject_before_intake(self):
        for kwargs in ({}, {'pool_namespace': True, 'pool_diagnose': 'run'},
                       {'pool_namespace': True, 'pool_diagnose': 'build', 'namespace_ipc': True},
                       {'pool_namespace': True, 'pool_diagnose': 'build', 'pool_zpl_write': True}):
            with patch.object(runtime, 'intake', side_effect=AssertionError('no intake')):
                with self.assertRaisesRegex(ValueError, 'isolated build-only'):
                    runtime.suite(Path('/absent'), pool_zpl_recover=True, **kwargs)
        for flag in ('run', 'build'):
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/service_runtime_smoke.py'),
                                     '--pool-zpl-recover', '--pool-diagnose', flag,
                                     '--delivery', '/absent'], capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 64)
            self.assertIn('isolated build-only', result.stderr)
        with self.assertRaisesRegex(ValueError, 'isolated namespace'):
            elapsed.prepare(Path('/absent'), None, volume_pool_zpl_recover=True)
        with self.assertRaisesRegex(ValueError, 'isolated namespace'):
            volume.build(Path('/absent'), None, None, pool_zpl_recover=True)

    def test_exact_clean_writer_evidence_and_sealed_digest_are_required(self):
        writer = dict(name='pool-import', status='pass', generations=3, reclaimed=3,
                      final_live_workers=0, cleanup_trace_version=1,
                      cleanup_boundaries_per_generation=7, vm_run_returned=True,
                      assigned_DMU_transaction=True, ordered_provider_witness=True,
                      clean_export_observed=True, assigned_target_txg=788, disk_sha256='a' * 64)
        with patch('openzfs_namespace.written_native_media_snapshot', return_value={'sealed': True}) as snapshot:
            self.assertEqual(runtime.check_zpl_recovery_media(writer, Path('/owned')), {'sealed': True})
            snapshot.assert_called_once_with(Path('/owned'), 'a' * 64)
            snapshot.reset_mock()
            for field in writer:
                missing = writer.copy(); del missing[field]
                with self.subTest(field=field), self.assertRaises(ValueError):
                    runtime.check_zpl_recovery_media(missing, Path('/absent'))
            for target in (0, 782, True, '788', 1 << 64):
                with self.assertRaises(ValueError):
                    runtime.check_zpl_recovery_media({**writer, 'assigned_target_txg': target}, Path('/absent'))
            snapshot.assert_not_called()

    def test_reader_trace_retains_recovery_not_write_semantics(self):
        tags = b'BIUVWLPabcdefghOAMT' + (789).to_bytes(8, 'little') + b'SDJFR'
        rows = [f'NATIVE observation slot=0 generation=1 offset={i*8} byte={b}' for i, b in enumerate(tags)]
        rows += [f'NATIVE observation slot=0 generation={g} offset={i*8} byte={b}'
                 for g in (2, 3) for i, b in enumerate(b'BNR')]
        result = runtime.check_zpl_recovery_trace('\n'.join(rows))
        self.assertEqual(result['recovered_pool_txg'], 789)
        self.assertTrue(result['readonly_pool_retired'])
        self.assertFalse(result['clean_export_observed'])
        self.assertFalse(result['assigned_DMU_transaction'])
        self.assertNotIn('assigned_target_txg', result)

    def test_pair_requires_both_retirements_matching_media_and_newer_loaded_txg(self):
        common = dict(status='pass', vm_run_returned=True, generations=3, reclaimed=3,
                      final_live_workers=0, cleanup_trace_version=1,
                      cleanup_boundaries_per_generation=7, disk_sha256='a' * 64)
        writer = {**common, 'assigned_target_txg': 788, 'assigned_DMU_transaction': True,
                  'ordered_provider_witness': True, 'clean_export_observed': True}
        reader = {**common, 'recovered_pool_txg': 789, 'readonly_pool_retired': True,
                  'namespace_bytes_verified': 780248}
        self.assertTrue(runtime.check_zpl_recovery_pair(writer, reader)['reader_media_unchanged'])
        for side in ('writer', 'reader'):
            original = writer if side == 'writer' else reader
            for field in original:
                missing = original.copy(); del missing[field]
                with self.subTest(side=side, field=field), self.assertRaises(ValueError):
                    runtime.check_zpl_recovery_pair(missing if side == 'writer' else writer,
                                                    missing if side == 'reader' else reader)
        with self.assertRaises(ValueError):
            runtime.check_zpl_recovery_pair(writer, {**reader, 'recovered_pool_txg': 787})


class RecoveryReader(unittest.TestCase):
    source = 'zpl-recovery.c'
    fixture = 'openzfs_zpl_recovery.c'
    include = 'zpl-recovery.inc'

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-zpl-recovery-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.out = Path(cls.temp.name)
        cls.body = '\n'.join(line for line in (ROOT / 'user/storage/openzfs-volume' / cls.source).read_text().splitlines()
                             if not line.startswith('#include')) + '\n'
        oracle = json.loads((ROOT / 'docs/evidence/zpl-recovery-oracle-2026-10-18.json').read_text())
        assert oracle['status'] == 'pass-host-oracle-only'
        digest = oracle['oracle']['expected_sha256']
        cls.hash_bytes = ','.join('0x' + digest[i:i+2] for i in range(0, 64, 2))
        cls.sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        cls.binary = cls.compile(cls.body, 'normal')

    @classmethod
    def compile(cls, body, name):
        (cls.out / cls.include).write_text(body)
        binary = cls.out / name
        result = subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-isysroot', cls.sdk,
                                 '-std=gnu11', '-O2', '-Wall', '-Wextra', '-Werror',
                                 '-DEXPECTED_HASH_BYTES=' + cls.hash_bytes, '-I' + str(cls.out),
                                 '-I' + str(ROOT / 'user/storage/openzfs-volume'),
                                 str(ROOT / 'tests/fixtures' / cls.fixture), '-o', str(binary)],
                                capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        return binary

    def modes(self, values):
        for value in values:
            result = subprocess.run([str(self.binary), str(value)], capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 0, (value, result.stdout + result.stderr))

    def test_success_denials_and_api_failures_release_ownership(self):
        self.modes([*range(19), *range(101, 298)])

    def test_compiling_required_guard_and_cleanup_omissions_fail(self):
        for name, old, new, mode in (
            ('hash', 'memcmp(digest, expected, sizeof(expected))', '((void)expected, 0)', 11),
            ('clock', 'mtime[0] < UINT64_C(1791290040)', '0', 15),
            ('flags', '(flags & (ZFS_ARCHIVE | ZFS_AV_MODIFIED))', '(ZFS_ARCHIVE | ZFS_AV_MODIFIED)', 13),
            ('close', 'aether_zpl_close(&view);', 'if (0) aether_zpl_close(&view);', 0),
            ('handle', 'sa_handle_destroy(handle);', 'if (0) sa_handle_destroy(handle);', 0),
        ):
            self.assertEqual(self.body.count(old), 1)
            binary = self.compile(self.body.replace(old, new, 1), name)
            result = subprocess.run([str(binary), str(mode)], capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 98, result.stdout + result.stderr)
            self.assertIn('HOST ZPL RECOVERY oracle98', result.stderr)


class RecoveryImport(RecoveryReader):
    source = 'spa-zpl-recover.inc'
    fixture = 'openzfs_zpl_recovery_import.c'
    include = 'recovery-import.inc'

    def test_success_denials_and_api_failures_release_ownership(self):
        self.modes([0, 1, *range(20, 31), *range(101, 112)])

    def test_compiling_required_guard_and_cleanup_omissions_fail(self):
        for name, old, new, mode in (
            ('drain', 'dmu_buf_user_evict_wait();', 'if (0) dmu_buf_user_evict_wait();', 0),
            ('borrow', 'spa_close(spa, FTAG);', 'if (0) spa_close(spa, FTAG);', 0),
            ('txg', 'spa->spa_uberblock.ub_txg > 782', '1', 26),
            ('retire', 'spa_evict_all();', 'if (0) spa_evict_all();', 0),
        ):
            self.assertEqual(self.body.count(old), 1)
            binary = self.compile(self.body.replace(old, new, 1), name)
            result = subprocess.run([str(binary), str(mode)], capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 99, result.stdout + result.stderr)
            self.assertIn('HOST ZPL IMPORT oracle99', result.stderr)


if __name__ == '__main__':
    unittest.main()
