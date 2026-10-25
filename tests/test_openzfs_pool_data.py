# SPDX-License-Identifier: BSD-2-Clause
"""Actual private DMU helper over synthetic ownership/assignment/media calls."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from openzfs_elapsed import CURRENT
from openzfs_pool import pool_transaction_body


class PoolDataProbe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-pool-data-host-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.out = Path(cls.temp.name)
        source = ROOT / 'user/storage/openzfs-volume/pool-data.c'
        cls.source = source.read_text()
        cls.body = '\n'.join(line for line in cls.source.splitlines()
                             if not line.startswith('#include')) + '\n'
        original = (CURRENT / 'baseline/source/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1/module/zfs/dmu_tx.c').read_text()
        getter = original.split('#include', 1)[0] + pool_transaction_body(original, 'dmu_tx_get_txg')
        (cls.out / 'original-getter.inc').write_text(getter)
        cls.binary = cls.compile(cls.body, 'probe')

    @classmethod
    def compile(cls, body, name):
        (cls.out / 'data-helper.inc').write_text(body)
        binary = cls.out / name
        result = subprocess.run(['/usr/bin/cc', '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                                 '-I', str(cls.out), str(ROOT / 'tests/fixtures/openzfs_pool_data.c'),
                                 '-o', str(binary)], capture_output=True, timeout=30)
        if result.returncode:
            raise RuntimeError(result.stderr.decode())
        return binary

    def check_modes(self, modes):
        for mode in modes:
            with self.subTest(mode=mode):
                r = subprocess.run([str(self.binary), str(mode)], capture_output=True, timeout=5)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_original_getter_before_commit_and_dataset_release(self):
        self.check_modes((0, 32))

    def test_create_claim_own_identity_and_authority_errors(self):
        self.check_modes((1, 2, 3, 4, 10, 11, 20, 27, 30, 31))

    def test_unassigned_abort_assigned_commit_wait_and_read_errors(self):
        self.check_modes((5, 6, 7, 8, 9))

    def test_read_object_geometry_and_target_denials(self):
        self.check_modes((21, 22, 23, 24, 25, 26, 28, 29))

    def test_every_record_byte_corruption_rejected(self):
        self.check_modes(range(100, 164))

    def test_named_compiling_omissions_fail_semantic_oracle(self):
        mutations = (
            ('foreign', 'dmu_objset_spa(os) != spa', '0', 4),
            ('geometry', 'info.doi_bonus_size', '0', 26),
            ('target', 'target > spa_last_synced_txg(spa)', '0', 29),
            ('payload', 'memcmp(record, expected, sizeof(record))', '0', 163),
            ('getter', 'uint64_t target = dmu_tx_get_txg(tx);', 'uint64_t target = dmu_tx_get_txg(tx) + 1;', 0),
        )
        for name, old, new, mode in mutations:
            with self.subTest(name=name):
                self.assertIn(old, self.body)
                body = self.body.replace(old, new)
                binary = self.compile(body, 'omit-' + name)
                result = subprocess.run([str(binary), str(mode)], capture_output=True, timeout=5)
                self.assertEqual(result.returncode, 92, result.stdout + result.stderr)
                self.assertIn(b'HOST DATA oracle92', result.stderr)
