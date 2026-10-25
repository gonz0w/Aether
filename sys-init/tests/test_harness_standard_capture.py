# SPDX-License-Identifier: BSD-2-Clause
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import test_harness_offline_locks as fixtures
import test_harness_standard_private as private_fixtures


class StandardCaptureTests(unittest.TestCase):
    def streams(self):
        output, errors = io.BytesIO(), io.BytesIO()
        return SimpleNamespace(executable=sys.executable, stdout=SimpleNamespace(buffer=output),
                               stderr=SimpleNamespace(buffer=errors)), output, errors

    def test_exact_raw_streams_and_nonzero(self):
        for suffix in fixtures.FAMILIES:
            for code in (0, 7):
                with self.subTest(suffix=suffix, code=code), tempfile.TemporaryDirectory() as directory:
                    module, _, _, _ = fixtures.OfflineLockTests().fixture(Path(directory).resolve(), suffix)
                    streams, output, errors = self.streams()
                    command = [sys.executable, '-I', '-S', '-B', '-c',
                               'import os;os.write(1,b"out\\r\\n\\xff");os.write(2,b"err\\x00");raise SystemExit(' + str(code) + ')']
                    with patch.object(module, 'sys', streams):
                        if code:
                            with self.assertRaises(subprocess.CalledProcessError) as caught:
                                module.run_reference(command)
                            self.assertEqual(caught.exception.returncode, code)
                        else:
                            module.run_reference(command)
                    self.assertEqual(output.getvalue(), b'out\r\n\xff')
                    self.assertEqual(errors.getvalue(), b'err\x00')

    def test_timeout_overflow_and_closed_pipes_reap_child(self):
        for suffix in fixtures.FAMILIES:
            for kind in ('timeout', 'overflow', 'closed-pipes'):
                with self.subTest(suffix=suffix, kind=kind), tempfile.TemporaryDirectory() as directory:
                    module, _, _, _ = fixtures.OfflineLockTests().fixture(Path(directory).resolve(), suffix)
                    streams, output, errors = self.streams()
                    code = {'timeout': 'import time;time.sleep(10)',
                            'overflow': 'import os,time;os.write(1,b"x"*8192);time.sleep(10)',
                            'closed-pipes': 'import os,time;os.close(1);os.close(2);time.sleep(10)'}[kind]
                    original = subprocess.Popen
                    children = []
                    def launch(*args, **kwargs):
                        child = original(*args, **kwargs)
                        children.append(child)
                        return child
                    expected = ValueError if kind == 'overflow' else subprocess.TimeoutExpired
                    with patch.object(module, 'sys', streams), patch.object(module, 'CHILD_TIMEOUT', 0.3), patch.object(module, 'CHILD_OUTPUT', 4096), patch.object(module.subprocess, 'Popen', side_effect=launch):
                        with self.assertRaises(expected):
                            module.run_reference([sys.executable, '-I', '-S', '-B', '-c', code])
                    self.assertIsNotNone(children[0].returncode)
                    self.assertTrue(children[0].stdout.closed and children[0].stderr.closed)
                    with self.assertRaises(ProcessLookupError):
                        os.kill(children[0].pid, 0)
                    self.assertEqual(len(output.getvalue()) + len(errors.getvalue()), 4096 if kind == 'overflow' else 0)

    def test_timeout_cleans_staged_tree(self):
        for suffix in fixtures.FAMILIES:
            with self.subTest(suffix=suffix), tempfile.TemporaryDirectory() as directory:
                module, lock, manifest, checker = fixtures.OfflineLockTests().fixture(Path(directory).resolve(), suffix)
                private_fixtures.PrivateStandardTests().reseal(lock, manifest, checker, 'import time;time.sleep(10)\n')
                streams, _, _ = self.streams()
                original = subprocess.Popen
                paths = []
                def launch(command, **kwargs):
                    paths.append(Path(command[-1]))
                    return original(command, **kwargs)
                with patch.object(module, 'sys', streams), patch.object(module, 'CHILD_TIMEOUT', 0.3), patch.object(module.subprocess, 'Popen', side_effect=launch):
                    with self.assertRaises(subprocess.TimeoutExpired):
                        module.main()
                self.assertFalse(paths[0].parents[2].exists())
