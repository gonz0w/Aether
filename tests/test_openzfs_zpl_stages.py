# SPDX-License-Identifier: BSD-2-Clause
"""Same-capacity stage observations; no prefix can qualify persistence."""
import copy
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import test_openzfs_zpl_repeat as repeat
import test_openzfs_zpl_complete as complete
import test_service_runtime as runtime_tests
import test_zpl_pair as controls
from openzfs_pool import staged_write_probe, staged_import_probe
import openzfs_elapsed as elapsed
import openzfs_volume as volume
import zpl_pair as pair

ROOT, runtime = repeat.ROOT, complete.runtime


def observations(data, generation=1):
    return '\n'.join(f'NATIVE observation slot=0 generation={generation} offset={i*8} byte={value}'
                     for i, value in enumerate(data)) + '\n'


def success():
    original = controls.serial()
    old = observations(b'BIUVWLPabcdefghOAMT' + (788).to_bytes(8, 'little') + b'SDJFR')
    new = observations(b'BIUVWLPOAMTorhc12vx' + (788).to_bytes(8, 'little') + b'SDJFR')
    assert original.count(old) == 1
    return original.replace(old, new, 1)


class StagedProbe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base = repeat.RepeatedProbe
        base.setUpClass()
        cls.addClassCleanup(base.doClassCleanups)
        cls.base = base
        cls.out = base.out
        cls.original_driver = base.driver
        cls.body = '\n'.join(line for line in staged_write_probe(
            (ROOT / 'user/storage/openzfs-volume/zpl-write-probe.c').read_text()).splitlines()
                             if not line.startswith('#include')) + '\n'
        start = base.driver.index('void aether_engine_utc_phase(')
        end = base.driver.index('static uint64_t cursor;', start)
        callback = '''static unsigned observed_stages;
void aether_engine_utc_phase(unsigned char value)
{
    if (value == 'E' || diagnostic_count) {
        CHECK(!owned && diagnostic_count < sizeof(diagnostic));
        diagnostic[diagnostic_count++] = value;
        return;
    }
    static const unsigned char stages[] = "orhc12vx";
    static const int expected_calls[] = {0,1,3,195,196,197,198,391};
    CHECK(observed_stages < 8 && value == stages[observed_stages]);
    CHECK(calls == expected_calls[observed_stages]);
    CHECK(owned == (observed_stages != 0 && observed_stages != 7));
    CHECK(writes == (observed_stages < 5 ? 0 : observed_stages == 5 ? 1 : 2));
    ++observed_stages;
}
'''
        base.driver = base.driver[:start] + callback + base.driver[end:]
        base.driver = base.driver.replace('CHECK(writes == 2 && reads == 382',
                                          'CHECK(observed_stages == 8); CHECK(writes == 2 && reads == 382', 1)
        cls.addClassCleanup(setattr, base, 'driver', cls.original_driver)
        cls.binary = base.compile(cls.body, 'stages')

    def test_all_391_api_failures_and_contract_denials_preserve_error_close_and_marker_order(self):
        for mode in [0, *range(1, 8), *range(9, 20), *range(101, 492)]:
            with self.subTest(mode=mode):
                r = subprocess.run([str(self.binary), str(mode)], capture_output=True, text=True, timeout=5)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_compiling_missing_reordered_or_late_stage_markers_fail96(self):
        for name, old, new in (
            ('missing-open', "    aether_engine_utc_phase('o');", "    if (0) aether_engine_utc_phase('o');"),
            ('wrong-first', "part ? '2' : '1'", "part ? '1' : '2'"),
            ('early-close', "    aether_zpl_close(&view);", "    aether_engine_utc_phase('x');\n    aether_zpl_close(&view);"),
        ):
            with self.subTest(omission=name):
                self.assertEqual(self.body.count(old), 1)
                binary = self.base.compile(self.body.replace(old, new, 1), name)
                r = subprocess.run([str(binary), '0'], capture_output=True, text=True, timeout=5)
                self.assertEqual(r.returncode, 96, r.stdout + r.stderr)
                self.assertIn('HOST ZPL PROBE oracle96', r.stderr)

    def test_generated_sources_reject_duplicate_or_changed_context(self):
        probe = (ROOT / 'user/storage/openzfs-volume/zpl-write-probe.c').read_text()
        imported = (ROOT / 'user/storage/openzfs-volume/spa-zpl-write.inc').read_text()
        for f, source, changed in ((staged_write_probe, probe, probe.replace('unsigned char stage = 2;', 'unsigned char stage = 1;')),
                                   (staged_import_probe, imported, imported.replace('hash >> (8 * i)', 'hash >> i'))):
            for bad in (source + source, changed):
                with self.assertRaises(ValueError):
                    f(bad)


class StageImport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base = complete.ZplImportFlow
        base.setUpClass()
        cls.addClassCleanup(base.doClassCleanups)
        cls.base = base
        cls.body = '\n'.join(line for line in staged_import_probe(
            (ROOT / 'user/storage/openzfs-volume/spa-zpl-write.inc').read_text()).splitlines()
                             if not line.startswith('#include')) + '\n'
        driver = (ROOT / 'tests/fixtures/openzfs_zpl_import.c').read_text()
        driver = driver.replace('    *out = mode == 26 ? 0 : 788;',
                                '    for (unsigned i=0;i<8;++i) aether_engine_utc_phase("orhc12vx"[i]);\n    *out = mode == 26 ? 0 : 788;', 1)
        driver = driver.replace(r'LP\x2a\0\0\0\0\0\0\0OAMT', r'LPOAMTorhc12vx', 1)
        cls.driver = base.out / 'stage-import.c'
        cls.driver.write_text(driver)
        cls.binary = cls.compile(cls.body, 'staged-import')

    @classmethod
    def compile(cls, body, name):
        (cls.base.out / 'zpl-import.inc').write_text(body)
        binary = cls.base.out / name
        r = subprocess.run([cls.base.compiler, '-isysroot', cls.base.sdk, '-std=gnu11', '-O2',
                            '-Wall', '-Wextra', '-Werror', '-I' + str(cls.base.out),
                            str(cls.driver), '-o', str(binary)], capture_output=True, text=True, timeout=30)
        if r.returncode:
            raise RuntimeError(r.stdout + r.stderr)
        return binary

    def test_actual_import_error_close_drain_order_and_32_row_capacity(self):
        for mode in [0, 1, *range(20, 31), *range(101, 113)]:
            r = subprocess.run([str(self.binary), str(mode)], capture_output=True, text=True, timeout=5)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_restored_fingerprint_overflows_quota_and_missing_validation_rejects97(self):
        ordinary = self.base.body
        for name, body in (('old-hash', ordinary), ('no-config-hash', self.body.replace(
                'error = aether_pool_config_hash(config, &hash);', 'if (0) error = aether_pool_config_hash(config, &hash);', 1))):
            binary = self.compile(body, name)
            r = subprocess.run([str(binary), '0'], capture_output=True, text=True, timeout=5)
            self.assertEqual(r.returncode, 97, r.stdout + r.stderr)
            self.assertIn('HOST ZPL IMPORT oracle97', r.stderr)


class StageController(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        class Candidate(runtime_tests.PoolNamespaceWriteDriver):
            pool_zpl_stages = True
        Candidate.setUpClass()
        cls.addClassCleanup(Candidate.doClassCleanups)
        cls.candidate = Candidate

    def test_actual_rust_checks_all_fixed_stage_bytes_and_padding(self):
        binary = self.candidate.output / 'reader'
        for row in range(33):
            for byte in (0, 1, 6):
                r = subprocess.run([str(binary), str(row), str(byte), '788'], capture_output=True, timeout=5)
                expected = 0 if row == 32 or (byte == 0 and 19 <= row < 27) else 90
                self.assertEqual(r.returncode, expected, (row, byte, r.stderr))


    def test_compiling_old_wildcard_regression_fails_named_stage_oracle(self):
        source = self.candidate.host_source
        old = '(19..27).contains(&stage)'
        self.assertEqual(source.count(old), 1)
        bad = source.replace(old, '(7..15).contains(&stage) || ' + old, 1)
        path = self.candidate.output / 'old-wildcards.rs'
        path.write_text(bad)
        binary = path.with_suffix('')
        r = subprocess.run(['rustc','+1.98.0','--edition=2024','-Dwarnings','-C','opt-level=2',
                            '--cfg','pool_create','--cfg','pool_import',str(path),'-o',str(binary)],
                           capture_output=True,text=True,timeout=30)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        def reject_corruption(executable):
            result = subprocess.run([str(executable),'11','0','788'],capture_output=True,timeout=5)
            if result.returncode != 90:
                raise ValueError('stage marker corruption accepted')
        reject_corruption(self.candidate.output/'reader')
        with self.assertRaisesRegex(ValueError,'stage marker corruption accepted'):
            reject_corruption(binary)


class StageDecoding(unittest.TestCase):
    def test_every_valid_prefix_is_diagnostic_only(self):
        trace = b'BIUVWLPOAMTorhc12vx' + (788).to_bytes(8, 'little') + b'SDJFR'
        for length in range(1, len(trace) + 1):
            r = pair.decode_zpl_stages(observations(trace[:length]))
            self.assertFalse(r['qualification'])
            self.assertEqual(r['primary_rows'], length)
            self.assertEqual(len(r['observed_boundaries']), max(0, min(length - 11, 8)))
            self.assertNotIn('assigned_target_txg', r)

    def test_malformed_foreign_extra_reordered_or_wrong_markers_reject(self):
        good = observations(b'BIUVWLPOAMTorhc12vx')
        for bad in ('', good.replace('slot=0', 'slot=1', 1), good.replace('generation=1','generation=2',1),
                    good.replace('offset=8 ', 'offset=9 ', 1), good.replace('byte=111','byte=256',1),
                    good.replace('byte=114','byte=113',1), good + good,
                    good + 'NATIVE observation invalid\n'):
            with self.subTest(bad=bad[-100:]), self.assertRaises(ValueError):
                pair.decode_zpl_stages(bad)

    def test_error_projection_is_separate_and_cannot_qualify_completion(self):
        for prefix,stage in ((b'BIUVWLPOAMTo',1), (b'BIUVWLPOAMTorhc1',6),
                              (b'BIUVWLPOAMTorhc12',6), (b'BIUVWLPOAMTorhc12v',9)):
            r = pair.decode_zpl_stages(observations(prefix + b'E' + bytes([stage,5,0,0,0])))
            self.assertEqual(r['error_projection'], {'stage':stage,'errno':5})
            self.assertFalse(r['qualification'])
        with self.assertRaises(ValueError):
            pair.decode_zpl_stages(observations(b'BIUVWLPOAMToE' + bytes([9,5,0,0,0])))
        with self.assertRaises(ValueError):
            pair.decode_zpl_stages(observations(b'BIUVWLPOAMToE\0\0\0\0\0'))

    def test_full_oracle_has_no_fabricated_config_hash_and_checks_each_marker(self):
        text = success()
        result = runtime.check_zpl_write_trace(text, True)
        self.assertEqual(result['assigned_target_txg'],788)
        self.assertNotIn('input_xdr_fnv1a64',result)
        for i in range(19):
            lines=text.splitlines();lines[i]=lines[i].rsplit('byte=',1)[0]+'byte=0'
            with self.assertRaises(ValueError):runtime.check_zpl_write_trace('\n'.join(lines),True)
        with self.assertRaises(ValueError):runtime.check_zpl_write_trace(text)

    def test_profile_and_cli_reject_unsupported_stage_selection_before_intake(self):
        with patch.object(runtime,'intake',side_effect=AssertionError('intake')):
            with self.assertRaisesRegex(ValueError,'paired repeated writer'):
                runtime.suite(Path('/absent'),_zpl_stages=True)
        with self.assertRaises(ValueError):elapsed.prepare(Path('/absent'),None,volume_pool_zpl_stages=True)
        with self.assertRaises(ValueError):volume.build(Path('/absent'),None,None,pool_zpl_stages=True)
        r=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/zpl_pair.py'),'--stage-diagnostic','--delivery','/absent','--utc-delivery','/absent'],capture_output=True,text=True,timeout=5)
        self.assertEqual(r.returncode,64)
        self.assertIn('stage diagnostic requires repeated writes',r.stderr)


class StagePair(unittest.TestCase):
    def setUp(self):
        self.fixture = controls.PairControls()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def test_real_staged_oracles_allow_reader_only_after_all_writer_checks(self):
        r = self.fixture.execute(writer_text=success(),stage_diagnostic=True)
        self.assertEqual(self.fixture.launched,['writer','reader'])
        self.assertTrue(r['fresh_vm_readback_qualified'])
        self.assertEqual(r['assigned_target_txg'],788)
        for bad in (success().replace('byte=111','byte=110',1),
                    success().replace('phase=7','phase=6',1),
                    observations(b'BIUVWLPOAMTo')):
            with self.assertRaises(ValueError):
                self.fixture.execute(writer_text=bad,stage_diagnostic=True)
            self.assertEqual(self.fixture.launched,['writer'])
            self.assertNotIn('fresh_vm_readback_qualified',self.fixture.record)

    def test_stage_profile_downgrade_and_reader_selection_reject(self):
        b=self.fixture.builds
        b['writer']['pool_zpl_repeat']=True
        with patch.object(runtime,'sealed'):
            with self.assertRaisesRegex(ValueError,'profile or seal'):
                pair.verify_prepared(self.fixture.output,b,True,True)
            b['writer']['pool_zpl_stages']=True
            pair.verify_prepared(self.fixture.output,b,True,True)
            with self.assertRaisesRegex(ValueError,'profile or seal'):
                pair.verify_prepared(self.fixture.output,b,True)
            b['reader']['pool_zpl_stages']=True
            with self.assertRaisesRegex(ValueError,'profile or seal'):
                pair.verify_prepared(self.fixture.output,b,True,True)
