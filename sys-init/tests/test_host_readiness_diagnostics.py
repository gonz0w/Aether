# SPDX-License-Identifier: BSD-2-Clause
"""Readiness diagnostic identity and observation semantics with actual pipes."""
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
from prototypes.host_runtime.runtime import Command, HostRuntime, ReadinessDiagnostic
from prototypes.runtime_model.model import Service

PYTHON = str(Path(sys.executable).resolve())
PIN = hashlib.sha256(Path(PYTHON).read_bytes()).hexdigest()

class ReadinessDiagnostics(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)

    def runtime(self, code, retries=0):
        rt=HostRuntime([Service('main',milestone='notified-ready',startup=3000,stop=1000,cleanup=1000,retries=retries,delay=1),
                        Service('consumer',requires=(('main','notified-ready'),),startup=3000)],
                       {'main':Command((PYTHON,'-c',code),PIN),
                        'consumer':Command((PYTHON,'-c','import time; time.sleep(30)'),PIN)},cwd=self.path)
        self.addCleanup(rt.close)
        return rt

    def test_closed_incomplete_and_malformed_are_distinct_once(self):
        for payload,code in [(b'','SYSINIT-READY-CLOSED'),(b'REA','SYSINIT-READY-INCOMPLETE'),
                             (b'\x1b\nX','SYSINIT-READY-MALFORMED')]:
            with self.subTest(code=code):
                child=("import os,signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); "
                       "fd=int(os.environ['AETHER_READY_FD']); os.write(fd,"+repr(payload)+
                       "); os.close(fd); time.sleep(30)")
                rt=self.runtime(child)
                try:
                    rt.start(['consumer']); rt.until(lambda: bool(rt.diagnostics))
                    for _ in range(3): rt.pump()
                    self.assertEqual(list(rt.diagnostics),[ReadinessDiagnostic(code,'main',1,len(payload))])
                    self.assertEqual([x for x in rt.log if x[0]=='invalid-ready'],[('invalid-ready','main',1)])
                    self.assertFalse(rt.model.state['main'].ready)
                    self.assertEqual(rt.model.state['consumer'].generation,0)
                    self.assertIsNone(rt.children[('main',1)].poll())
                    self.assertNotEqual(rt.model.state['main'].phase,'terminal')
                finally: rt.close()

    def test_failures_remain_associated_with_each_generation(self):
        rt=self.runtime("import os,time; os.write(int(os.environ['AETHER_READY_FD']),b'X'); time.sleep(30)",retries=1)
        rt.start(['consumer']); rt.until(lambda: rt.model.active is None and not rt.children and not rt.pending)
        self.assertEqual([(d.code,d.service,d.generation,d.received_bytes) for d in rt.diagnostics],
                         [('SYSINIT-READY-MALFORMED','main',1,1),('SYSINIT-READY-MALFORMED','main',2,1)])
        self.assertEqual(rt.model.state['consumer'].generation,0)
        self.assertEqual(rt.diagnostics.maxlen,128)

    def test_valid_first_frame_with_trailing_data_has_no_diagnostic(self):
        rt=self.runtime("import os,time; os.write(int(os.environ['AETHER_READY_FD']),b'READY\\n\\x1bnoise'); time.sleep(30)")
        rt.start(['consumer']); rt.until(lambda: rt.model.active is None)
        self.assertTrue(rt.model.state['main'].ready)
        self.assertEqual(rt.model.state['consumer'].generation,1)
        self.assertFalse(rt.diagnostics)

if __name__ == '__main__': unittest.main()
