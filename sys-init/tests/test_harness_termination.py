# SPDX-License-Identifier: BSD-2-Clause
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

import test_harness_cleanup as fixture


def termination_probe(directory, runner_path=None):
    script = '\n'.join([
        'import sys,json,signal,os', 'from pathlib import Path',
        f'sys.path.insert(0, {str(fixture.ROOT / "tests")!r})',
        'import test_harness_cleanup as fixture',
        'import importlib.util',
        f'override={str(runner_path)!r}' if runner_path else 'override=None',
        'if override:',
        '    spec=importlib.util.spec_from_file_location("signal_runner", override)',
        '    fixture.aggregate=importlib.util.module_from_spec(spec)',
        '    spec.loader.exec_module(fixture.aggregate)',
        'previous=signal.SIG_DFL',
        'signal.signal(signal.SIGTERM, previous)',
        'original=fixture.aggregate.subprocess.Popen',
        'def start(*args, **kwargs):',
        '    child=original(*args, **kwargs)',
        f'    Path({str(directory / "gate-pid")!r}).write_text(str(child.pid))',
        '    return child',
        'fixture.aggregate.subprocess.Popen=start',
        f'result,cleanup=fixture.nested_probe(fixture.aggregate, Path({str(directory)!r}), timeout=10)',
        'restored=signal.getsignal(signal.SIGTERM) is previous',
        f'Path({str(directory / "outer.json")!r}).write_text(json.dumps(dict(result=result, cleanup=cleanup, restored=restored)))',
        'raise SystemExit(130 if result["result"] == "interrupted" else 1)',
    ])
    with (directory/'outer.stdout').open('wb') as stdout, (directory/'outer.stderr').open('wb') as stderr:
        outer = subprocess.Popen([sys.executable, '-c', script], stdout=stdout, stderr=stderr,
                                 start_new_session=True)
        try:
            deadline = time.monotonic() + 5
            while not (directory/'ready.json').exists():
                if outer.poll() is not None or time.monotonic() >= deadline:
                    raise AssertionError('nested worker did not become ready')
                time.sleep(0.02)
            outer.send_signal(signal.SIGTERM)
            code = outer.wait(timeout=5)
            record = json.loads((directory/'outer.json').read_text()) if (directory/'outer.json').exists() else None
            return code, record
        finally:
            if outer.poll() is None:
                os.killpg(outer.pid, signal.SIGKILL)
                outer.wait()
            # Failed pre-fix runs cannot perform their own nested cleanup.
            if not (directory/'outer.json').exists():
                for file, parse in [('gate-pid', int), ('ready.json', lambda text: json.loads(text)['pid'])]:
                    path = directory/file
                    if path.exists():
                        try:
                            os.killpg(parse(path.read_text()), signal.SIGKILL)
                        except ProcessLookupError:
                            pass


class TerminationTests(unittest.TestCase):
    def test_real_sigterm_unwinds_nested_capture_and_restores_handler(self):
        with tempfile.TemporaryDirectory() as root:
            code, record = termination_probe(Path(root))
            self.assertEqual(code, 130)
            self.assertIsNotNone(record)
            self.assertEqual(record['result']['result'], 'interrupted')
            self.assertTrue(record['restored'])
            self.assertLess(record['cleanup']['returncode'], 0)
            self.assertTrue(record['cleanup']['closed'])

    def test_normal_and_timeout_restore_handler(self):
        previous = signal.getsignal(signal.SIGTERM)
        try:
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            with tempfile.TemporaryDirectory() as root:
                for code, timeout in [('print("ok")', 5), ('import time;time.sleep(30)', 0.2)]:
                    fixture.aggregate.run_check('restore', [sys.executable, '-c', code], Path(root), timeout=timeout)
                    self.assertEqual(signal.getsignal(signal.SIGTERM), signal.SIG_IGN)
        finally:
            signal.signal(signal.SIGTERM, previous)

    def test_background_thread_preserves_process_signal_disposition(self):
        previous = signal.getsignal(signal.SIGTERM)
        with tempfile.TemporaryDirectory() as root, ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(fixture.aggregate.run_check, 'thread',
                                     [sys.executable, '-c', 'print("ok")'], Path(root))
            self.assertEqual(future.result(timeout=5)['result'], 'pass')
        self.assertEqual(signal.getsignal(signal.SIGTERM), previous)
