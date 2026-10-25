# SPDX-License-Identifier: BSD-2-Clause
"""Real readiness pipes at controlled registration, time, stop and replacement cuts."""
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
from prototypes.host_runtime.runtime import Command, HostRuntime
from prototypes.runtime_model.model import Service

PYTHON = str(Path(sys.executable).resolve())
PIN = hashlib.sha256(Path(PYTHON).read_bytes()).hexdigest()
WAITING = """import os,signal,time
from pathlib import Path
signal.signal(signal.SIGTERM,signal.SIG_IGN)
Path('staged').touch()
while not Path('go').exists(): time.sleep(.001)
os.write(int(os.environ['AETHER_READY_FD']),b'READY\\n')
Path('written').touch()
time.sleep(30)
"""

class ReadinessOrdering(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)

    def wait_file(self, name):
        end = time.monotonic()+3
        while not (self.path/name).exists():
            if time.monotonic() >= end: self.fail('child handshake watchdog: '+name)
            time.sleep(.001)

    def runtime(self, code=WAITING, retries=0):
        services = [Service('provider',milestone='notified-ready',startup=1000,stop=1000,cleanup=1000,retries=retries,delay=1),
                    Service('consumer',requires=(('provider','notified-ready'),),startup=1000)]
        commands = {'provider':Command((PYTHON,'-c',code),PIN),
                    'consumer':Command((PYTHON,'-c','import time; time.sleep(30)'),PIN)}
        rt = HostRuntime(services,commands,cwd=self.path)
        self.addCleanup(rt.close)
        return rt

    def write_ready(self):
        (self.path/'go').touch()
        self.wait_file('written')

    def test_notification_before_launch_registration_is_preserved(self):
        rt = self.runtime()
        real_spawn = subprocess.Popen
        def spawn(*args, **kwargs):
            child = real_spawn(*args, **kwargs)
            # Return ownership on any handshake failure so test cleanup still works.
            try:
                self.wait_file('staged'); self.write_ready()
                self.assertFalse(rt.children)
                self.assertFalse(rt.ready)
            except BaseException:
                child.kill(); child.wait(timeout=2); raise
            return child
        with patch('prototypes.host_runtime.runtime.subprocess.Popen',side_effect=spawn):
            rt.start(['consumer'])
        rt.until(lambda: rt.model.active is None)
        self.assertTrue(rt.model.state['provider'].ready)
        self.assertEqual(rt.model.state['consumer'].generation,1)
        self.assertFalse(rt.ready)

    def test_ready_before_at_and_after_deadline(self):
        for offset,accepted in [(-1,True),(0,False),(1,False)]:
            with self.subTest(offset=offset):
                for name in ('staged','go','written'):
                    (self.path/name).unlink(missing_ok=True)
                rt = self.runtime()
                try:
                    with patch.object(rt,'now',return_value=0):
                        rt.start(['consumer']); rt.pump()
                    self.wait_file('staged'); self.write_ready()
                    deadline = rt.model.state['provider'].deadline
                    with patch.object(rt,'now',return_value=deadline+offset): rt.pump()
                    self.assertEqual(rt.model.state['provider'].ready,accepted)
                    self.assertEqual(rt.model.state['consumer'].generation,1 if accepted else 0)
                    if not accepted:
                        self.assertEqual(rt.model.state['provider'].reason,'startup-timeout')
                finally: rt.close()

    def test_notification_after_stop_cannot_admit_consumer(self):
        rt = self.runtime()
        rt.start(['consumer']); self.wait_file('staged')
        rt.stop(['provider','consumer'])
        self.write_ready(); rt.pump()
        self.assertFalse(rt.model.state['provider'].ready)
        self.assertFalse(rt.model.state['provider'].desired)
        self.assertEqual(rt.model.state['consumer'].generation,0)
        self.assertFalse(rt.ready)

    def test_old_writer_and_event_cannot_ready_replacement(self):
        code = """import os,time
from pathlib import Path
p=Path('generation'); n=int(p.read_text())+1 if p.exists() else 1; p.write_text(str(n))
if n == 1: raise SystemExit(9)
Path('staged').touch()
while not Path('go').exists(): time.sleep(.001)
os.write(int(os.environ['AETHER_READY_FD']),b'READY\\n')
Path('written').touch()
time.sleep(30)
"""
        rt = self.runtime(code,retries=1)
        real_spawn = subprocess.Popen
        old = []
        def spawn(*args, **kwargs):
            old.append(os.dup(kwargs['pass_fds'][0]))
            self.addCleanup(os.close,old[-1])
            return real_spawn(*args, **kwargs)
        with patch('prototypes.host_runtime.runtime.subprocess.Popen',side_effect=spawn):
            rt.start(['consumer'])
        rt.until(lambda: ('provider',2) in rt.children)
        self.wait_file('staged')
        with self.assertRaises(BrokenPipeError): os.write(old[0],b'READY\n')
        rt.event('ready','provider',1)  # Separate stale-observation injection.
        rt.pump()
        self.assertFalse(rt.model.state['provider'].ready)
        self.assertEqual(rt.model.state['consumer'].generation,0)
        self.write_ready(); rt.until(lambda: rt.model.active is None)
        self.assertTrue(rt.model.state['provider'].ready)
        self.assertEqual(rt.model.state['provider'].generation,2)
        self.assertEqual(rt.model.state['consumer'].generation,1)

if __name__ == '__main__': unittest.main()
