# SPDX-License-Identifier: BSD-2-Clause
"""Separate native baseline admission and actual generated transaction probe."""
import copy
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

import test_openzfs_zpl_repeat as repeated
import test_zpl_pair as controls
from openzfs_pool import transaction_write_probe
import zpl_pair as pair
import service_runtime_smoke as runtime

ROOT = repeated.ROOT


class TransactionProbe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        repeated.RepeatedProbe.setUpClass()
        cls.addClassCleanup(repeated.RepeatedProbe.doClassCleanups)
        cls.out = repeated.RepeatedProbe.out
        cls.sdk = repeated.RepeatedProbe.sdk
        cls.body = '\n'.join(line for line in transaction_write_probe(
            (ROOT / 'user/storage/openzfs-volume/zpl-write-probe.c').read_text()).splitlines()
                             if not line.startswith('#include')) + '\n'
        cls.driver = repeated.RepeatedProbe.driver
        expected = bytes.fromhex('9ae4ab7a896f9d760334d1f322996043e1e132f4b131ccc3f2b7b2c577d2afb0')
        literal = ', '.join('0x%02x' % b for b in expected)
        changes = (
            ('out[0] ^= 1;', '{ static const unsigned char expected[32] = {' + literal + '}; memcpy(out, expected, 32); }'),
            ('mode == 3 || mode == 4 || mode == 7 ? 4', 'mode == 3 || mode == 4 || mode == 7 ? 9'),
            ('stage = call <= 3     ? call\n                    : call <= 195 ? 4\n                    : call == 196 ? 5\n                    : (call == 197 || call == 198) ? 6\n                    : call == 199 ? 8\n                                  : 9;',
             'stage = call <= 3 ? call : call == 4 ? 5 : call <= 6 ? 6 : call == 7 ? 8 : 9;'),
            ('reads == 382 && clock_calls == 1 && calls == 391', 'reads == 191 && clock_calls == 1 && calls == 199'),
            (' || mode == 297', ''),
            ('reads == 191 && writes == 1', 'reads == 0 && writes == 1'),
        )
        for old, new in changes:
            if cls.driver.count(old) != 1:
                raise RuntimeError('transaction fixture context changed: ' + old)
            cls.driver = cls.driver.replace(old, new, 1)
        cls.binary = cls.compile(cls.body, 'transaction-probe')

    @classmethod
    def compile(cls, body, name):
        return repeated.RepeatedProbe.compile.__func__(cls, body, name)

    def test_two_writes_complete_file_eof_metadata_and_all_199_api_failures(self):
        for mode in [0, *range(1, 8), *range(9, 20), *range(101, 300)]:
            with self.subTest(mode=mode):
                r = subprocess.run([str(self.binary), str(mode)], capture_output=True, text=True, timeout=5)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_compiling_fixed_oracle_readback_metadata_sync_and_second_write_omissions_fail96(self):
        for name, old, new, mode in (
            ('fixed-hash', '0x9a, 0xe4', '0x9b, 0xe4', 0),
            ('untouched-byte', 'memcmp(actual, predicted, sizeof(actual))', '((void)predicted,0)', 18),
            ('metadata', 'file.generation != 47', '0', 17),
            ('sync', 'result.state != AETHER_ZPL_SYNCED', '0', 16),
            ('second-write', 'part < 2 && !error', 'part < 1 && !error', 0),
            ('advance', 'result.txg <= previous', '((void)previous,0)', 19),
            ('eof', 'return error ? error : count ? EIO : 0;', 'return error;', 7),
        ):
            # Metadata and state occur in both preflight/final checks.
            body = self.body.replace(old, new)
            self.assertNotEqual(body, self.body)
            binary = self.compile(body, name)
            r = subprocess.run([str(binary), str(mode)], capture_output=True, text=True, timeout=5)
            self.assertEqual(r.returncode, 96, r.stdout + r.stderr)
            self.assertIn('HOST ZPL PROBE oracle96', r.stderr)

    def test_baseline_derivation_drift_and_duplicate_reject(self):
        source = (ROOT / 'user/storage/openzfs-volume/zpl-write-probe.c').read_text()
        for bad in (source + source, source.replace('memcmp(original, pristine,', 'memcmp(predicted, pristine,')):
            with self.assertRaises(ValueError):
                transaction_write_probe(bad)
        self.assertNotIn('stream_hash(view, original', self.body)
        self.assertIn('stream_hash(view, actual, NULL)', self.body)


class BaselineAdmission(controls.PairControls):
    def test_worker_profile_requires_exact_baseline_image_sources_and_readonly_role(self):
        self.builds['writer'].update(pool_zpl_repeat=True, pool_zpl_stages=True, pool_zpl_txg_stages=True)
        with patch.object(runtime, 'sealed'):
            with self.assertRaisesRegex(ValueError, 'all prepared'):
                pair.verify_prepared(self.output, self.builds, True, True, False, True)
            baseline = copy.deepcopy(self.builds['reader'])
            baseline['pool_zpl_recover'] = False
            self.builds['baseline'] = baseline
            (self.output / 'baseline').mkdir()
            for name in ('aether.iso', 'engine.elf'):
                (self.output / 'baseline' / name).write_bytes((self.output / 'reader' / name).read_bytes())
            pair.verify_prepared(self.output, self.builds, True, True, False, True)
            for key, value in (('pool_zpl_write', True), ('pool_zpl_recover', True), ('pool_zpl_txg_stages', True), ('sources', {})):
                present = key in baseline
                old = baseline.get(key)
                baseline[key] = value
                with self.subTest(key=key), self.assertRaises(ValueError):
                    pair.verify_prepared(self.output, self.builds, True, True, False, True)
                if present:
                    baseline[key] = old
                else:
                    baseline.pop(key, None)
            (self.output / 'baseline/aether.iso').write_bytes(b'drift')
            with self.assertRaisesRegex(ValueError, 'artifact drift'):
                pair.verify_prepared(self.output, self.builds, True, True, False, True)

    def test_invalid_baseline_full_file_marker_terminal_cleanup_stops_before_writer(self):
        text = controls.baseline_serial()
        for bad in (text.replace('byte=90', 'byte=88', 1), text.replace('detail=0', 'detail=873', 1), text.replace('phase=7', 'phase=6', 1)):
            with self.subTest(bad=bad[-80:]), self.assertRaises(ValueError):
                self.execute(txg_worker_diagnostic=True, baseline_text=bad)
            self.assertEqual(self.launched, ['baseline'])
            self.assertNotIn('separate_baseline_qualified', self.record)

    def test_changed_baseline_media_and_writer_intake_drift_stop(self):
        # Actual native_media_snapshot rejects all region drift and guards;
        # here emulate identity changes between independently captured snapshots.
        for snapshots in ([{'sha256': 'a'}] * 2 + [{'sha256': 'b'}],
                          [{'sha256': 'a'}] * 3 + [{'sha256': 'b'}]):
            f = controls.PairControls(); f.setUp(); self.addCleanup(f.doCleanups)
            (f.output / 'baseline').mkdir()
            record = {'cases': [], 'txg_worker_diagnostic': True}
            def launch(image, **kwargs):
                (image.parent / 'native-serial.log').write_text(controls.baseline_serial())
            with patch.object(pair, 'verify_prepared'), patch.object(pair, 'prepare_native_fixture'), \
                 patch.object(pair, 'native_media_snapshot', side_effect=snapshots), \
                 patch.object(pair, 'run', side_effect=launch) as run:
                with self.assertRaisesRegex(ValueError, 'media changed|media drift'):
                    pair.execute_pair(f.output, {}, record)
                self.assertEqual(run.call_count, 1)
                self.assertNotIn('fresh_vm_readback_qualified', record)

    def test_fixed_baseline_staging_rejects_wrong_role_and_keeps_controller_readonly(self):
        with patch.object(runtime, 'intake', side_effect=AssertionError('intake')):
            for flags in ({'pool_zpl_write': True}, {'pool_zpl_recover': True}, {'namespace_ipc': True}):
                with self.assertRaisesRegex(ValueError, 'ZPL staging'):
                    runtime.suite(Path('/absent'), pool_namespace=True, pool_diagnose='build', _zpl_stage=self.output / 'baseline', **flags)
        import test_service_runtime as checked
        checked.PoolNamespaceDriver.setUpClass()
        self.addCleanup(checked.PoolNamespaceDriver.doClassCleanups)
        derived = checked.PoolNamespaceDriver.adapted
        self.assertNotIn('let region = [8u64, 2097152, 7];', derived)
        self.assertIn('BIUVWLP????????OAMZDJFR', derived)
