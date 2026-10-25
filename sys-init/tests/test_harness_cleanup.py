# SPDX-License-Identifier: BSD-2-Clause
"""Owned disposable processes for cooperative aggregate cleanup regression."""
import importlib.util
import json
import os
from pathlib import Path
import signal
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('cleanup_aggregate', ROOT/'scripts/check-all.py')
aggregate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aggregate)


def nested_probe(runner, directory, timeout=1):
    ready, receipt = directory/'ready.json', directory/'cleanup.json'
    worker = ("import os,time,json; from pathlib import Path; "
              f"Path({str(ready)!r}).write_text(json.dumps(dict(pid=os.getpid()))); "
              "time.sleep(30)")
    wrapper = "\n".join([
        'import sys,json,subprocess', 'from pathlib import Path',
        f'sys.path.insert(0, {str(ROOT / "scripts")!r})',
        'import bounded_capture', 'children=[]', 'original=subprocess.Popen',
        'def start(*args, **kwargs):',
        '    child=original(*args, **kwargs)',
        '    children.append(child)', '    return child',
        'subprocess.Popen=start', 'try:',
        f'    bounded_capture.run_capture([sys.executable, "-c", {worker!r}], cwd={str(ROOT)!r})',
        'except KeyboardInterrupt:',
        f'    Path({str(receipt)!r}).write_text(json.dumps(dict(returncode=children[0].returncode, closed=children[0].stdout.closed and children[0].stderr.closed)))',
        '    raise',
    ])
    result = runner.run_check('nested', [sys.executable, '-c', wrapper], directory, timeout=timeout)
    if not ready.exists():
        raise AssertionError('nested worker never reached readiness')
    pid = json.loads(ready.read_text())['pid']
    try:
        cleanup = json.loads(receipt.read_text()) if receipt.exists() else None
        return result, cleanup
    finally:
        # The pre-fix control deliberately leaves this owned session alive.
        # Reaped success needs no further signal to a potentially recycled pid.
        if not receipt.exists():
            try:
                os.killpg(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass


class CleanupTests(unittest.TestCase):
    def test_nested_capture_reaps_worker_before_wrapper_exit(self):
        with tempfile.TemporaryDirectory() as root:
            result, cleanup = nested_probe(aggregate, Path(root))
            self.assertEqual(result['result'], 'timeout')
            self.assertIsNotNone(cleanup, 'wrapper was killed before nested cleanup')
            self.assertLess(cleanup['returncode'], 0)
            self.assertTrue(cleanup['closed'])

    def test_ignored_interrupt_has_bounded_forced_fallback(self):
        with tempfile.TemporaryDirectory() as root:
            directory = Path(root)
            command = [sys.executable, '-c',
                       'import signal,time;signal.signal(signal.SIGINT,signal.SIG_IGN);print("ready",flush=True);time.sleep(30)']
            started = time.monotonic()
            result = aggregate.run_check('ignored', command, directory, timeout=0.3)
            elapsed = time.monotonic() - started
            self.assertEqual(result['result'], 'timeout')
            self.assertEqual(result['returncode'], -signal.SIGKILL)
            self.assertEqual((directory/'ignored.stdout').read_text(), 'ready\n')
            self.assertLess(elapsed, 3)
