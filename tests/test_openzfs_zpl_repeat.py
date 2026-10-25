# SPDX-License-Identifier: BSD-2-Clause
"""Generated two-write probe, profile isolation and unchanged final reader oracle."""
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import test_openzfs_zpl_complete as complete
from openzfs_pool import repeated_write_probe
import openzfs_elapsed as elapsed
import openzfs_volume as volume
import zpl_pair

ROOT = complete.ROOT


class RepeatedProbe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-zpl-repeat-probe-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.out = Path(cls.temp.name)
        cls.body = '\n'.join(line for line in repeated_write_probe(
            (ROOT / 'user/storage/openzfs-volume/zpl-write-probe.c').read_text()).splitlines()
                             if not line.startswith('#include')) + '\n'
        driver = (ROOT / 'tests/fixtures/openzfs_zpl_write_probe.c').read_text()
        changes = (
            ('offset == 37 && length == 16 && !writes',
             'offset == 37 + (uint64_t)writes * 8 && length == 8 && writes < 2'),
            ('pattern(37 + i, 1)', 'pattern(offset + i, 2)'),
            ('{42, 16, AETHER_ZPL_COMMITTED}', '{40 + writes + 1, 8, AETHER_ZPL_COMMITTED}'),
            ('mode == 15 ? 0 : 42, mode == 14 ? 0 : 16,',
             'mode == 15 ? 0 : mode == 19 && writes == 2 ? 41 : 40 + writes, mode == 14 ? 0 : 8,'),
            ('offset < 53', 'offset < 37 + (uint64_t)patched * 8'),
            ('pattern(hash->count + i, hash->patch)', 'pattern(hash->count + i, hash->patch ? 2 : 0)'),
            ('mode == 13                          ? 6', 'mode == 13 || (mode >= 14 && mode <= 16) || mode == 19 ? 6'),
            ('call == 197 ? 6', '(call == 197 || call == 198) ? 6'),
            ('call == 198 ? 8', 'call == 199 ? 8'),
            ('writes == 1 && reads == 382 && clock_calls == 1 && calls == 390',
             'writes == 2 && reads == 382 && clock_calls == 1 && calls == 391'),
        )
        for old, new in changes:
            if driver.count(old) != 1:
                raise RuntimeError('repeated probe fixture context changed: ' + old)
            driver = driver.replace(old, new, 1)
        cls.driver = driver
        cls.sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        cls.binary = cls.compile(cls.body, 'probe')

    @classmethod
    def compile(cls, body, name):
        (cls.out / 'write-probe.inc').write_text(body)
        source = cls.out / 'repeat-probe.c'
        source.write_text(cls.driver)
        binary = cls.out / name
        r = subprocess.run([
            '/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-isysroot', cls.sdk,
            '-std=gnu11', '-O2', '-Wall', '-Wextra', '-Werror',
            '-I' + str(cls.out), '-I' + str(ROOT / 'user/storage/openzfs-volume'),
            str(source), '-o', str(binary),
        ], capture_output=True, text=True, timeout=30)
        if r.returncode:
            raise RuntimeError(r.stdout + r.stderr)
        return binary

    def test_two_chunks_and_every_reachable_api_failure_close_without_retry(self):
        for mode in [0, *range(1, 8), *range(9, 20), *range(101, 492)]:
            with self.subTest(mode=mode):
                r = subprocess.run([str(self.binary), str(mode)], capture_output=True, text=True, timeout=5)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_compiling_omissions_fail_for_skipped_write_or_nonadvancing_target(self):
        for name, old, new, mode in (
            ('one-chunk', 'part < 2 && !error', 'part < 1 && !error', 0),
            ('same-target', 'result.txg <= previous', '((void)previous,0)', 19),
        ):
            with self.subTest(omission=name):
                self.assertEqual(self.body.count(old), 1)
                binary = self.compile(self.body.replace(old, new, 1), name)
                r = subprocess.run([str(binary), str(mode)], capture_output=True, text=True, timeout=5)
                self.assertEqual(r.returncode, 96, r.stdout + r.stderr)
                self.assertIn('HOST ZPL PROBE oracle96', r.stderr)

    def test_probe_derivation_rejects_changed_or_duplicate_context(self):
        source = (ROOT / 'user/storage/openzfs-volume/zpl-write-probe.c').read_text()
        for changed in (source + source, source.replace('ZPL_PROBE_LENGTH ||', 'ZPL_PROBE_LENGTH + 1 ||')):
            with self.assertRaises(ValueError):
                repeated_write_probe(changed)

    def test_repeat_selection_rejects_before_intake_and_cannot_be_a_reader(self):
        with patch.object(complete.runtime, 'intake', side_effect=AssertionError('intake')):
            for options in ({}, {'pool_zpl_write': True}, {'pool_zpl_recover': True}):
                with self.assertRaisesRegex(ValueError, 'paired build-only writer'):
                    complete.runtime.suite(Path('/absent'), _zpl_repeat=True, **options)
        with self.assertRaisesRegex(ValueError, 'isolated writer preparation'):
            volume.build(Path('/absent'), None, None, pool_zpl_repeat=True)
        with self.assertRaisesRegex(ValueError, 'isolated writer preparation'):
            elapsed.prepare(Path('/absent'), None, volume_pool_zpl_repeat=True)

    def test_pair_rejects_repeat_profile_downgrade(self):
        # Use the existing hash/source/tool/reader preparation harness, with no
        # VM. Only the exact requested writer may select repeated observations.
        import test_zpl_pair as checks
        fixture = checks.PairControls()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        with patch.object(complete.runtime, 'sealed'):
            with self.assertRaisesRegex(ValueError, 'profile or seal'):
                zpl_pair.verify_prepared(fixture.output, fixture.builds, True)
            fixture.builds['writer']['pool_zpl_repeat'] = True
            zpl_pair.verify_prepared(fixture.output, fixture.builds, True)
            with self.assertRaisesRegex(ValueError, 'profile or seal'):
                zpl_pair.verify_prepared(fixture.output, fixture.builds)
            fixture.builds['reader']['pool_zpl_repeat'] = True
            with self.assertRaisesRegex(ValueError, 'profile or seal'):
                zpl_pair.verify_prepared(fixture.output, fixture.builds, True)
