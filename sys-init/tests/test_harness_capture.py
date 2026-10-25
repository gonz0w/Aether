# SPDX-License-Identifier: BSD-2-Clause
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import bounded_capture as capture


class CaptureTests(unittest.TestCase):
    def run_child(self, code, **bounds):
        return capture.run_capture([sys.executable, '-c', code], cwd=ROOT, **bounds)

    def test_exact_limit_nonzero_and_text_newlines(self):
        result = self.run_child('import os;os.write(1,bytes([97,13,10,98,13]));os.write(2,b"err");exit(7)', limit=8)
        self.assertEqual((result.returncode, result.stdout, result.stderr), (7, 'a\nb\n', 'err'))

    def test_overflow_preserves_each_stream_prefix(self):
        for fd in (1, 2):
            with self.subTest(fd=fd), self.assertRaises(capture.OutputLimitError) as caught:
                self.run_child(f'import os;os.write({fd},b"x"*129)', limit=128)
            error = caught.exception
            self.assertEqual((error.output, error.stderr), (b'x'*128, b'') if fd == 1 else (b'', b'x'*128))

    def test_concurrent_output_cannot_deadlock_or_exceed_budget(self):
        with self.assertRaises(capture.OutputLimitError) as caught:
            self.run_child('import os,threading;t=threading.Thread(target=lambda:os.write(2,b"e"*200000));'
                           't.start();os.write(1,b"o"*200000);t.join()', limit=4096)
        self.assertEqual(len(caught.exception.output) + len(caught.exception.stderr), 4096)

    def test_timeout_preserves_prefix_even_after_pipe_closure(self):
        with self.assertRaises(subprocess.TimeoutExpired) as caught:
            self.run_child('import os,time;os.write(1,b"out");os.write(2,b"err");'
                           'os.close(1);os.close(2);time.sleep(30)', timeout=0.2)
        self.assertEqual((caught.exception.output, caught.exception.stderr), (b'out', b'err'))

    def test_missing_tool_raises_infrastructure_error(self):
        with tempfile.TemporaryDirectory() as root, self.assertRaises(FileNotFoundError):
            capture.run_capture([str(Path(root)/'missing')], cwd=ROOT)

    def test_interruption_reaps_child_and_closes_pipes(self):
        children = []
        real_popen = subprocess.Popen
        def start(*args, **kwargs):
            child = real_popen(*args, **kwargs)
            children.append(child)
            return child
        with mock.patch.object(capture.subprocess, 'Popen', side_effect=start), \
             mock.patch.object(capture.selectors.DefaultSelector, 'select', side_effect=KeyboardInterrupt), \
             self.assertRaises(KeyboardInterrupt):
            self.run_child('import time;time.sleep(30)')
        self.assertEqual(len(children), 1)
        self.assertLess(children[0].returncode, 0)
        self.assertTrue(children[0].stdout.closed and children[0].stderr.closed)

    def test_host_overflow_emits_no_success_stdout(self):
        spec = importlib.util.spec_from_file_location('host_capture_check', ROOT/'scripts/check-host-runtime.py')
        host = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(host)
        stdout, stderr = io.StringIO(), io.StringIO()
        def overflowing_worker(*args, **kwargs):
            return self.run_child('import os;os.write(2,b"diagnostic"*100)', limit=32)
        with mock.patch.object(host, 'run_capture', side_effect=overflowing_worker), \
             contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            self.assertEqual(host.main(), 1)
        self.assertEqual(stdout.getvalue(), '')
        self.assertIn('output limit exceeded', stderr.getvalue())
        self.assertTrue(stderr.getvalue().startswith('diagnostic'))

    def test_model_overflow_writes_failure_shape_and_prefixes(self):
        with tempfile.TemporaryDirectory() as root:
            output = Path(root)/'results.json'
            error = capture.OutputLimitError(8, b'partial', b'e')
            with mock.patch.object(sys, 'argv', ['check-runtime-model.py', '--output', str(output)]), \
                 mock.patch.object(capture, 'run_capture', side_effect=error), \
                 self.assertRaises(capture.OutputLimitError):
                runpy.run_path(str(ROOT/'scripts/check-runtime-model.py'), run_name='__main__')
            result = json.loads(output.read_text())
            self.assertEqual(set(result), {'passed', 'error'})
            self.assertIs(result['passed'], False)
            self.assertIn('stdout prefix:\npartial', result['error'])
            self.assertIn('stderr prefix:\ne', result['error'])
