"""Direct-child emergency lifetime, including injected cleanup failures."""
import errno
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from prototypes.host_runtime.runtime import Command, HostRuntime
from prototypes.runtime_model.model import Rejected, Service

PYTHON = str(Path(sys.executable).resolve())
PIN = hashlib.sha256(Path(PYTHON).read_bytes()).hexdigest()


class EmergencyCleanup(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def runtime(self, names=('child',)):
        rt = HostRuntime([Service(n, milestone='notified-ready', startup=1000) for n in names],
                         {n: Command((PYTHON, '-c', 'import time; time.sleep(30)'), PIN)
                          for n in names}, cwd=self.tmp.name)
        self.addCleanup(rt.close)
        rt.start(list(names))
        return rt

    def test_caller_exception_finally_reaps_and_closes_pipe(self):
        rt = self.runtime()
        child = rt.children[('child', 1)]
        reader = rt.ready[('child', 1)][0]
        with self.assertRaisesRegex(RuntimeError, 'caller failure'):
            try:
                raise RuntimeError('caller failure')
            finally:
                rt.close()
        self.assertIsNotNone(child.returncode)
        self.assertFalse(rt.children)
        self.assertFalse(rt.ready)
        with self.assertRaises(OSError) as caught:
            os.fstat(reader)
        self.assertEqual(caught.exception.errno, errno.EBADF)
        # Emergency cleanup cannot fabricate orderly operation completion.
        self.assertEqual(rt.model.operations[-1].status, 'pending')

    def test_close_permanently_rejects_lifecycle_and_late_events(self):
        rt = self.runtime()
        rt.close()
        for operation in (lambda: rt.start(['child']), lambda: rt.stop(['child']),
                          rt.pump, lambda: rt.event('ready', 'child', 1),
                          lambda: rt.dispatch([('launch', 'child', 2)])):
            with self.subTest(operation=operation), self.assertRaisesRegex(Rejected, 'closed'):
                operation()
        self.assertTrue(rt.closed)
        self.assertFalse(rt.pending)
        self.assertFalse(rt.children)

    def test_successful_close_is_repeatable_without_process_calls(self):
        rt = self.runtime()
        child = rt.children[('child', 1)]
        rt.close()
        with patch.object(child, 'kill', side_effect=AssertionError('already reclaimed')), \
             patch.object(child, 'wait', side_effect=AssertionError('already reclaimed')):
            rt.close()
        self.assertTrue(rt.closed)

    def test_wait_timeout_retains_ownership_and_allows_cleanup_retry(self):
        rt = self.runtime()
        child = rt.children[('child', 1)]
        reader = rt.ready[('child', 1)][0]
        with patch.object(child, 'wait', side_effect=subprocess.TimeoutExpired(child.args, 2)):
            with self.assertRaisesRegex(RuntimeError, 'owned-child cleanup failed'):
                rt.close()
        self.assertTrue(rt.closed)
        self.assertIs(rt.children[('child', 1)], child)
        os.fstat(reader)
        with self.assertRaises(Rejected):
            rt.start(['child'])
        rt.close()
        self.assertFalse(rt.children)
        self.assertFalse(rt.ready)
        self.assertIsNotNone(child.returncode)

    def test_kill_failure_does_not_abandon_other_children(self):
        rt = self.runtime(('first', 'second'))
        first, second = rt.children[('first', 1)], rt.children[('second', 1)]
        with patch.object(first, 'kill', side_effect=PermissionError('injected denial')):
            with self.assertRaisesRegex(RuntimeError, 'injected denial'):
                rt.close()
        self.assertEqual(set(rt.children), {('first', 1)})
        self.assertEqual(set(rt.ready), {('first', 1)})
        self.assertIsNone(first.poll())
        self.assertIsNotNone(second.returncode)
        rt.close()
        self.assertFalse(rt.children)

    def test_unrelated_child_is_not_signalled_or_reaped(self):
        unrelated = subprocess.Popen([PYTHON, '-c', 'import time; time.sleep(30)'],
                                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
        def reap_unrelated():
            if unrelated.poll() is None:
                unrelated.kill()
            unrelated.wait(timeout=2)
        self.addCleanup(reap_unrelated)
        rt = self.runtime()
        rt.close()
        self.assertIsNone(unrelated.poll())


if __name__ == '__main__':
    unittest.main()
