# SPDX-License-Identifier: BSD-2-Clause
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'worker_builder', ROOT / 'scripts/build-native-service-worker.py')
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


class WorkerBoundsTests(unittest.TestCase):
    builder = BUILDER
    def test_completion_and_nonzero_logs(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / 'tool.log'
            command = [sys.executable, '-c', 'print("tool result")']
            self.assertEqual(self.builder.run_tool(command, os.environ, log), b'tool result\n')
            with self.assertRaises(subprocess.CalledProcessError) as error:
                self.builder.run_tool([sys.executable, '-c', 'print("failure"); raise SystemExit(7)'],
                                 os.environ, log)
            self.assertEqual(error.exception.returncode, 7)
            self.assertEqual(log.read_bytes(), b'failure\n')

    def test_missing_tool_preserves_empty_attempt_log(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / 'tool.log'
            with self.assertRaises(OSError):
                self.builder.run_tool([str(Path(directory) / 'missing')], os.environ, log)
            self.assertEqual(log.read_bytes(), b'')

    def test_timeout_and_output_limit_are_distinct(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / 'tool.log'
            with self.assertRaises(subprocess.TimeoutExpired):
                self.builder.run_tool([sys.executable, '-c', 'import time; time.sleep(10)'],
                                 os.environ, log, timeout=0.1)
            with self.assertRaisesRegex(ValueError, 'output limit exceeded'):
                self.builder.run_tool([sys.executable, '-c', 'print("x" * 4096)'],
                                 os.environ, log, limit=128)
            self.assertEqual(log.stat().st_size, 128)


IO_SPEC = importlib.util.spec_from_file_location(
    'io_worker_builder', ROOT / 'scripts/build-native-io-worker.py')
IO_BUILDER = importlib.util.module_from_spec(IO_SPEC)
IO_SPEC.loader.exec_module(IO_BUILDER)


class IOWorkerBoundsTests(WorkerBoundsTests):
    builder = IO_BUILDER
