# SPDX-License-Identifier: BSD-2-Clause
"""Pure selected reader composition tests; no compiler, artifact or guest.

From userland: python3 -B experiments/filesystem-service/home_reader_drain_tests.py
"""
from pathlib import Path
import hashlib
import importlib.util
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location('home_reader_drain', ROOT/'scripts/home_reader.py')
reader = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reader)
POSITIVE = ('file_prefix', 'exec_prefix', 'fork_prefix', 'stream')
NEGATIVE = ('no_ack', 'partial_ack', 'exit_deadline', 'pending_fragment')


class ReaderDrainTests(unittest.TestCase):
    def test_existing_default_sources_remain_exact(self):
        startup = (reader.SERVICE/'engine-startup.c').read_text()
        importer = (reader.VOLUME/'spa-zpl-recover.inc').read_text()
        expected = {
            False: ('ca720544f5f9d1df79dcebed0f2fd993c1c62af0758624751a247944ab719470',
                    '73ec401f84ddfc31872ae1355da889e7e2ec65a8dc3e0f57bd6613911aa4b635'),
            True: ('a31f531ee11aa06ed8d618e1b000b999ecc47af49bd56b038a36db553c0bde76',
                   '018c0a74ef16ff2f4a68d41a6e21708b114d7734cc6c079fb6a3f4dc81c1303a'),
        }
        for recovered, digests in expected.items():
            self.assertEqual(reader.role(recovered), int(recovered))
            values = (reader.render_startup(startup, recovered),
                      reader.render_importer(importer, recovered))
            self.assertEqual(tuple(hashlib.sha256(v.encode()).hexdigest() for v in values), digests)

    def test_four_success_cases_use_recovered_empty_and_pristine_absence(self):
        importer = (reader.VOLUME/'spa-zpl-recover.inc').read_text()
        startup = (reader.SERVICE/'engine-startup.c').read_text()
        for case in POSITIVE:
            self.assertEqual(reader.role(True, drain_case=case), 2)
            self.assertEqual(reader.role(False, drain_case=case), 0)
            recovered = reader.render_importer(importer, True, drain_case=case)
            pristine = reader.render_importer(importer, False, drain_case=case)
            self.assertIn('aether_home_readback(spa, 2,', recovered)
            self.assertIn('spa->spa_uberblock.ub_txg > 782', recovered)
            self.assertIn('aether_home_readback(spa, 0,', pristine)
            self.assertIn('spa->spa_uberblock.ub_txg == 782', pristine)
            self.assertIn('const int recovered = 2;', reader.render_startup(startup, True, drain_case=case))

    def test_four_deadline_cases_never_prepare_recovery(self):
        for case in NEGATIVE:
            self.assertEqual(reader.role(False, drain_case=case), 0)
            for render in (reader.render_startup, reader.render_importer):
                with self.assertRaises(ValueError):
                    render('unused', True, drain_case=case)
            with self.assertRaises(ValueError):
                reader.compose(None, None, None, None, None, None, {}, True, drain_case=case)

    def test_unknown_cases_and_nonboolean_roles_reject_before_effects(self):
        record = {}
        for case in ('', 'unknown', 1, None, False, []):
            with self.assertRaises(ValueError):
                reader.compose(None, None, None, None, None, None, record, True, drain_case=case)
            for render in (reader.render_startup, reader.render_importer):
                with self.assertRaises(ValueError):
                    render('unused', True, drain_case=case)
        for recovered in (0, 1, 2, None, 'recovery'):
            with self.assertRaises(ValueError):
                reader.role(recovered, drain_case='file_prefix')
        self.assertEqual(record, {})

    def test_compose_forwards_case_into_actual_generated_sources_before_commands(self):
        class StopBeforeCommand(Exception):
            pass
        for recovered, expectation in ((False, 0), (True, 2)):
            with tempfile.TemporaryDirectory(prefix='af09-reader-compose-') as directory:
                work = Path(directory)
                spa = work/'input-spa.c'
                spa.write_text('#include "spa-import.inc"')
                calls = []

                def command(*args):
                    calls.append(args)
                    raise StopBeforeCommand
                with mock.patch.object(reader, '_recipe', return_value=['cc', '-c', str(spa)]):
                    with self.assertRaises(StopBeforeCommand):
                        reader.compose(work, {'old_service': None, 'recovery_empty': False},
                                       work, work, command, {}, {}, recovered, drain_case='stream')
                self.assertEqual(len(calls), 1)
                self.assertIn('aether_home_readback(spa, '+str(expectation)+',',
                              (work/'home-reader-spa.c').read_text())
                self.assertIn('const int recovered = '+str(expectation)+';',
                              (work/'home-reader-startup.c').read_text())
                # The callback stops before any tool is invoked.
                self.assertFalse((work/'reader.elf').exists())


if __name__ == '__main__':
    unittest.main()
