# SPDX-License-Identifier: BSD-2-Clause
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

spec = importlib.util.spec_from_file_location(
    'bounded', Path(__file__).resolve().parents[1] / 'scripts/bounded_tools.py')
bounded = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bounded)


class RecordedToolTests(unittest.TestCase):
    def exercise(self, args, expected, exception=None, **limits):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / 'compiler.log'
            if exception:
                with self.assertRaises(exception):
                    bounded.run_recorded(args, log, __file__, **limits)
            else:
                self.assertEqual(bounded.run_recorded(args, log, __file__, **limits), b'ok\n')
            record = json.loads(log.with_suffix('.log.json').read_text())
            self.assertEqual(record['result'], expected)
            self.assertEqual(record['command'], args)
            self.assertEqual(len(record['sources']), 2)
            return record, log.read_bytes()

    def test_success_and_nonzero_preserve_outcome_and_log(self):
        self.exercise([sys.executable, '-c', 'print("ok")'], 'pass')
        record, raw = self.exercise([sys.executable, '-c', 'print("bad"); raise SystemExit(7)'],
                                    'fail', subprocess.CalledProcessError)
        self.assertEqual((record['returncode'], raw), (7, b'bad\n'))

    def test_timeout_and_overflow_remain_distinct(self):
        self.exercise([sys.executable, '-c', 'import time; time.sleep(30)'],
                      'timeout', subprocess.TimeoutExpired, timeout=0.1)
        _, raw = self.exercise([sys.executable, '-c', 'print("x" * 4096)'],
                               'output-limit', ValueError, limit=128)
        self.assertEqual(len(raw), 128)

    def test_missing_tool_is_infrastructure_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            self.exercise([str(Path(directory) / 'missing')], 'infra-error', OSError)


class CompletedToolTests(unittest.TestCase):
    def test_cwd_and_nonzero_are_preserved_for_semantic_oracle(self):
        original = Path.cwd()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            log = root / 'tool.log'
            command = [sys.executable, '-c',
                       'from pathlib import Path; print(Path.cwd()); raise SystemExit(7)']
            result = bounded.run_completed(command, log, __file__, cwd=root)
            self.assertEqual(result.returncode, 7)
            self.assertEqual(result.stdout, (str(root) + '\n').encode())
            record = json.loads(log.with_suffix('.log.json').read_text())
            self.assertEqual((record['result'], record['returncode'], record['cwd']),
                             ('fail', 7, str(root)))
            self.assertEqual(Path.cwd(), original)

    def test_timeout_overflow_and_missing_tool_are_not_semantic_exits(self):
        cases = [([sys.executable, '-c', 'import time; time.sleep(20)'],
                  subprocess.TimeoutExpired, {'timeout': 0.1}, 'timeout'),
                 ([sys.executable, '-c', 'print("x" * 4096)'],
                  ValueError, {'limit': 128}, 'output-limit')]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cases.append(([str(root / 'missing')], OSError, {}, 'infra-error'))
            for command, error, options, outcome in cases:
                with self.subTest(outcome=outcome):
                    log = root / (outcome + '.log')
                    with self.assertRaises(error):
                        bounded.run_completed(command, log, __file__, cwd=root, **options)
                    self.assertEqual(json.loads(log.with_suffix('.log.json').read_text())['result'], outcome)
                    if outcome == 'output-limit':
                        self.assertEqual(len(log.read_bytes()), 128)

    def test_success_returns_completed_output_and_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / 'success.log'
            result = bounded.run_completed([sys.executable, '-c', 'print("success")'],
                                           log, __file__, cwd=directory)
            self.assertEqual((result.returncode, result.stdout), (0, b'success\n'))
            self.assertEqual(json.loads(log.with_suffix('.log.json').read_text())['result'], 'pass')
