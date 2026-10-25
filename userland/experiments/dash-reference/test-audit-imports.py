#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Host controls for import inspection; Python 3.10+."""
import hashlib
import json
import os
from pathlib import Path
import runpy
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
MODULE = runpy.run_path(str(ROOT / 'experiments/dash-reference/audit-imports.py'))


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.build = Path(tempfile.mkdtemp(prefix='dash-audit-test-',
                                           dir=ROOT / 'build'))
        self.objects = self.build / 'obj/src'
        self.objects.mkdir(parents=True)
        (self.objects / 'one.o').write_bytes(b'fixture')
        print(f'retained fixture: {self.build}', file=sys.stderr)

    def tool(self, code):
        path = self.build / 'fake-nm'
        path.write_text('#!' + sys.executable + '\n' + code + '\n')
        path.chmod(0o700)
        return {'path': str(path),
                'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

    def test_symbols_and_environment(self):
        tool = self.tool(
            'import os\n'
            'assert os.getcwd() == ' + repr(str(self.build)) + '\n'
            'assert "AETHER_TEST_POISON" not in os.environ\n'
            'assert os.environ["PATH"] == "/usr/bin:/bin"\n'
            'print(" U external\\n U own\\n0000 T own")')
        with patch.dict(os.environ, {'AETHER_TEST_POISON': 'present'}):
            work = MODULE['audit'](self.build, tool)
        report = json.loads((self.build / 'libc-imports.json').read_text())
        self.assertEqual(report['symbols'], ['external'])
        self.assertEqual(set(report),
                         {'scope', 'script_sha256', 'objects', 'symbols'})
        receipt = json.loads((work / 'nm-0.process.json').read_text())
        self.assertTrue(receipt['complete'])
        self.assertFalse(MODULE['PROCESS']['alive'](receipt['process_group']))
        print(f'retained execution: {work}', file=sys.stderr)

    def test_pin_denial_before_execution(self):
        marker = self.build / 'executed'
        tool = self.tool('open(' + repr(str(marker)) + ', "w").close()')
        tool['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'pin mismatch'):
            MODULE['audit'](self.build, tool)
        self.assertFalse(marker.exists())
        self.assertFalse((self.build / 'libc-imports.json').exists())

    def test_empty_objects(self):
        (self.objects / 'one.o').unlink()
        with self.assertRaisesRegex(ValueError, 'no dash objects'):
            MODULE['audit'](self.build, self.tool('raise SystemExit(99)'))

    def test_execution_failures(self):
        for name, code, timeout, limit in [
            ('nonzero', 'raise SystemExit(7)', 3, 1048576),
            ('timeout-descendant',
             'import os,time\nos.fork()\ntime.sleep(30)', 0.3, 1048576),
            ('output-limit',
             'import os\nwhile True: os.write(1, b"x" * 4096)', 3, 8192),
        ]:
            with self.subTest(name=name):
                report = self.build / 'libc-imports.json'
                report.write_bytes(b'prior report: not evidence of this attempt')
                with self.assertRaises(ValueError) as caught:
                    MODULE['audit'](self.build, self.tool(code),
                                    timeout=timeout, file_limit=limit)
                work = Path(str(caught.exception).split('evidence: ')[1])
                print(f'retained execution: {work}', file=sys.stderr)
                receipt = json.loads((work / 'nm-0.process.json').read_text())
                self.assertEqual(receipt['cleanup'], 'complete')
                self.assertFalse(MODULE['PROCESS']['alive'](
                    receipt['process_group']))
                self.assertEqual(report.read_bytes(),
                                 b'prior report: not evidence of this attempt')
                if name == 'timeout-descendant':
                    self.assertEqual(receipt['failure'], 'timeout')
                else:
                    self.assertNotEqual(receipt['exit'], 0)
                self.assertLessEqual((work / 'nm-0.stdout').stat().st_size,
                                     limit)


if __name__ == '__main__':
    unittest.main()
