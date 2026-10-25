"""Failure and watchdog evidence for the provider-neutral development runner."""
import importlib.util
import io
import os
import signal
import time
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('all_check', Path(__file__).resolve().parents[1] / 'scripts/check-all.py')
all_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(all_check)


class RunnerTests(unittest.TestCase):
    def test_help_version_and_invalid_usage_contracts(self):
        for option, expected in [('--help', 0), ('--version', 0), ('--unknown', 64)]:
            with self.subTest(option=option):
                run = subprocess.run([sys.executable, all_check.__file__, option],
                                     capture_output=True, text=True, timeout=5)
                self.assertEqual(run.returncode, expected)
                self.assertTrue(run.stdout if expected == 0 else run.stderr)
                self.assertFalse(run.stderr if expected == 0 else run.stdout)

    def run_fixture(self, code, timeout=5, limit=4 * 1024 * 1024):
        with tempfile.TemporaryDirectory() as root:
            directory = Path(root)
            result = all_check.run_check('fixture', [sys.executable, '-c', code], directory, timeout, limit)
            return result, (directory / 'fixture.stdout').read_text(), (directory / 'fixture.stderr').read_text()

    def test_failure_preserves_exit_and_both_logs(self):
        result, stdout, stderr = self.run_fixture("import sys; print('out'); print('err', file=sys.stderr); sys.exit(7)")
        self.assertEqual(result['result'], 'fail')
        self.assertEqual(result['returncode'], 7)
        self.assertEqual((stdout, stderr), ('out\n', 'err\n'))

    def test_timeout_is_not_semantic_rejection(self):
        result, _, _ = self.run_fixture('import time; time.sleep(30)', timeout=0.1)
        self.assertEqual(result['result'], 'timeout')
        self.assertLess(result['returncode'], 0)

    def test_missing_command_is_not_a_test_failure(self):
        with tempfile.TemporaryDirectory() as root:
            result = all_check.run_check('missing', [str(Path(root) / 'absent')], Path(root))
        self.assertEqual(result['result'], 'error')
        self.assertNotIn('returncode', result)

    def test_success_preserves_log(self):
        result, stdout, _ = self.run_fixture("print('witness')")
        self.assertEqual(result['result'], 'pass')
        self.assertEqual(stdout, 'witness\n')

    def test_exact_combined_limit_preserves_both_streams(self):
        result, stdout, stderr = self.run_fixture(
            "import os; os.write(1, b'a' * 64); os.write(2, b'b' * 64)", limit=128)
        self.assertEqual((result['result'], result['output_limit_bytes']), ('pass', 128))
        self.assertEqual((stdout, stderr), ('a' * 64, 'b' * 64))

    def test_overflow_on_either_stream_retains_only_budget(self):
        for fd in (1, 2):
            with self.subTest(fd=fd):
                result, stdout, stderr = self.run_fixture(
                    f"import os; os.write({fd}, b'x' * 129)", limit=128)
                self.assertEqual(result['result'], 'output-limit')
                self.assertEqual((stdout, stderr), ('x' * 128, '') if fd == 1 else ('', 'x' * 128))

    def test_concurrent_pipe_flood_is_bounded_without_deadlock(self):
        result, stdout, stderr = self.run_fixture(
            "import os, threading; t=threading.Thread(target=lambda: os.write(2, b'e'*200000)); "
            "t.start(); os.write(1, b'o'*200000); t.join()", limit=4096)
        self.assertEqual(result['result'], 'output-limit')
        self.assertEqual(len(stdout) + len(stderr), 4096)
        self.assertEqual(set(stdout) - {'o'}, set())
        self.assertEqual(set(stderr) - {'e'}, set())

    def test_closed_pipes_do_not_bypass_deadline(self):
        result, _, _ = self.run_fixture(
            'import os,time; os.close(1); os.close(2); time.sleep(30)', timeout=0.1)
        self.assertEqual(result['result'], 'timeout')
        self.assertLess(result['returncode'], 0)

    def test_inherited_pipe_descendant_is_stopped_after_parent_exit(self):
        with tempfile.TemporaryDirectory() as root:
            directory = Path(root)
            marker = directory / 'escaped'
            child_code = ("import os,time; print(os.getpid(), flush=True); time.sleep(2); "
                          f"open({str(marker)!r}, 'w').write('escaped')")
            command = [sys.executable, '-c',
                       f"import subprocess,sys; subprocess.Popen([sys.executable, '-c', {child_code!r}])"]
            result = all_check.run_check('descendant', command, directory, timeout=0.5)
            pid = int((directory / 'descendant.stdout').read_text().strip())
            try:
                self.assertEqual(result['result'], 'timeout')
                time.sleep(2)
                self.assertFalse(marker.exists())
            finally:
                try:
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass

    def test_empty_and_skipped_suites_cannot_pass(self):
        empty = unittest.TestResult()
        with self.assertRaises(ValueError):
            all_check.require_complete(empty, 0)
        case = unittest.FunctionTestCase(lambda: self.skipTest('required case unavailable'))
        result = unittest.TextTestRunner(stream=io.StringIO()).run(case)
        self.assertTrue(result.wasSuccessful())
        with self.assertRaises(ValueError):
            all_check.require_complete(result, 1)

    def test_partial_execution_cannot_pass(self):
        case = unittest.FunctionTestCase(lambda: None)
        result = unittest.TextTestRunner(stream=io.StringIO()).run(case)
        all_check.require_complete(result, 1)
        with self.assertRaises(ValueError):
            all_check.require_complete(result, 2)


if __name__ == '__main__':
    unittest.main()
