"""Exclusive wait loss and explicitly delegated readiness in trusted fixtures."""
import hashlib
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from prototypes.host_runtime.runtime import Command, HostRuntime
from prototypes.runtime_model.model import Service

PYTHON = str(Path(sys.executable).resolve())
PIN = hashlib.sha256(Path(PYTHON).read_bytes()).hexdigest()


class WaitOwnership(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def runtime(self, service, code):
        return HostRuntime([service], {service.name: Command((PYTHON, '-c', code), PIN)},
                           cwd=self.tmp.name)

    def test_stolen_exit_status_is_unknown_not_success(self):
        rt = self.runtime(Service('job', kind='oneshot', milestone='completed',
                                  startup=1000, cleanup=1000), 'raise SystemExit(23)')
        try:
            rt.start(['job'])
            child = rt.children[('job', 1)]
            # Deliberately violate exclusive wait without populating Popen's cache.
            pid, status = os.waitpid(child.pid, 0)
            self.assertEqual(pid, child.pid)
            self.assertEqual(os.waitstatus_to_exitcode(status), 23)
            with patch('prototypes.host_runtime.runtime.os.kill',
                       side_effect=AssertionError('lost identity must not be signalled')):
                rt.pump()
                rt.pump()
                state = rt.model.state['job']
                self.assertFalse(state.completed)
                self.assertEqual(state.phase, 'unknown')
                self.assertEqual(state.reason, 'observation-lost')
                self.assertEqual(rt.model.operations[-1].status, 'incomplete')
                self.assertIsNone(child.returncode)
                self.assertIn(child, rt.lost_children)
                with self.assertRaisesRegex(RuntimeError, 'cleanup failed'):
                    rt.close()
                self.assertTrue(rt.closed)
                self.assertIn(('job', 1), rt.children)
        finally:
            # The test knows it already reaped this child; the adapter must not guess.
            if rt.lost_children:
                with self.assertRaises(RuntimeError): rt.close()
                # Only the test holds the real status; silence Popen destruction's
                # false running warning after checking adapter behavior above.
                child.returncode = os.waitstatus_to_exitcode(status)
            else:
                rt.close()

    def test_independent_helper_cannot_wait_for_owners_child(self):
        child = subprocess.Popen([PYTHON, '-c', 'import time; time.sleep(30)'])
        try:
            code = ("import os;\ntry: os.waitpid(" + str(child.pid) + ",os.WNOHANG)\n"
                    "except ChildProcessError: raise SystemExit(0)\nraise SystemExit(9)")
            helper = subprocess.run([PYTHON, '-c', code], timeout=2)
            self.assertEqual(helper.returncode, 0)
            self.assertIsNone(child.poll())
        finally:
            if child.poll() is None: child.kill()
            self.assertEqual(child.wait(timeout=2), -signal.SIGKILL)

    def test_explicitly_inherited_writer_allows_helper_readiness(self):
        helper = "import os; os.write(int(os.environ['AETHER_READY_FD']),b'READY\\n')"
        code = ("import os,subprocess,time; from pathlib import Path; "
                "fd=int(os.environ['AETHER_READY_FD']); "
                "p=subprocess.run([" + repr(PYTHON) + ",'-c'," + repr(helper) +
                "],pass_fds=(fd,),check=True); Path('helper-reaped').write_text(str(p.returncode)); "
                "os.close(fd); time.sleep(30)")
        rt = self.runtime(Service('main', milestone='notified-ready', startup=1000,
                                  stop=1000, cleanup=1000), code)
        try:
            rt.start(['main'])
            rt.until(lambda: rt.model.active is None and (Path(self.tmp.name) / 'helper-reaped').exists())
            self.assertTrue(rt.model.state['main'].ready)
            self.assertEqual((Path(self.tmp.name) / 'helper-reaped').read_text(), '0')
            self.assertEqual(len(rt.children), 1)
            rt.stop(['main'])
            rt.until(lambda: rt.model.active is None and not rt.children and not rt.pending)
        finally:
            rt.close()


if __name__ == '__main__':
    unittest.main()
