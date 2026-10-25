#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Host compiler ownership controls; Python 3.10+."""
import json
import os
from pathlib import Path
import runpy
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
MODULE = runpy.run_path(str(ROOT / 'experiments/dash-reference/host-build.py'))


class HostBuildTests(unittest.TestCase):
    def execute(self, code, *, fails=False, timeout=3, limit=1048576,
                executable=None):
        work = Path(tempfile.mkdtemp(prefix='dash-host-test-',
                                     dir=ROOT / 'build'))
        (work / 'control.py').write_text(code)
        argv = [executable or sys.executable, '-B', str(work / 'control.py')]
        print(f'retained: {work}', file=sys.stderr)
        with patch.dict(os.environ, {'AETHER_TEST_POISON': 'present'}):
            if fails:
                with self.assertRaises(RuntimeError):
                    MODULE['compile_helper'](argv, work, timeout=timeout,
                                             file_limit=limit)
            else:
                MODULE['compile_helper'](argv, work, timeout=timeout,
                                         file_limit=limit)
        receipt = json.loads((work / 'helper-build.process.json').read_text())
        if 'process_group' in receipt:
            self.assertFalse(MODULE['PROCESS']['alive'](
                receipt['process_group']))
            self.assertEqual(receipt['cleanup'], 'complete')
        return work, receipt

    def test_streams_environment_and_cwd(self):
        work, receipt = self.execute(
            'import os,pathlib\n'
            'assert pathlib.Path.cwd() == pathlib.Path(__file__).parent\n'
            'assert "AETHER_TEST_POISON" not in os.environ\n'
            'assert os.environ["TMPDIR"] == os.getcwd()\n'
            'assert os.environ["PATH"] == "/usr/bin:/bin"\n'
            'os.write(1,b"out\\0"); os.write(2,b"err\\0")')
        self.assertTrue(receipt['complete'])
        self.assertEqual((work / 'helper-build.stdout').read_bytes(), b'out\0')
        self.assertEqual((work / 'helper-build.trace').read_bytes(), b'err\0')

    def test_failure_cleanup(self):
        cases = [
            ('nonzero', 'raise SystemExit(7)', 3, 1048576),
            ('timeout', 'import os,time\nos.fork()\ntime.sleep(30)',
             0.3, 1048576),
            ('descendant-after-exit',
             'import os,time\nif os.fork(): os._exit(0)\ntime.sleep(30)',
             3, 1048576),
            ('output', 'import os\nwhile True: os.write(1,b"x"*4096)',
             3, 8192),
        ]
        for name, code, timeout, limit in cases:
            with self.subTest(name=name):
                work, receipt = self.execute(code, fails=True,
                                             timeout=timeout, limit=limit)
                if name in ('timeout', 'descendant-after-exit'):
                    self.assertEqual(receipt['failure'], name)
                else:
                    self.assertNotEqual(receipt['exit'], 0)
                self.assertLessEqual((work / 'helper-build.stdout')
                                     .stat().st_size, limit)

    def test_missing_executable(self):
        _, receipt = self.execute('', fails=True,
                                  executable='/nonexistent/aether-test-cc')
        self.assertFalse(receipt['complete'])
        self.assertEqual(receipt['cleanup'], 'not-started')


if __name__ == '__main__':
    unittest.main()
