# SPDX-License-Identifier: BSD-2-Clause
"""Bounded writer pressure and inherited-helper evidence; not descendant containment."""
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
from prototypes.host_runtime.runtime import Command, HostRuntime
from prototypes.runtime_model.model import Service

PYTHON = str(Path(sys.executable).resolve())
PIN = hashlib.sha256(Path(PYTHON).read_bytes()).hexdigest()
PRELUDE = """import os,signal,time,json
from pathlib import Path
signal.signal(signal.SIGTERM,signal.SIG_IGN)
fd=int(os.environ['AETHER_READY_FD'])
def receipt(name,value):
    p=Path(name+'.tmp'); p.write_text(json.dumps(value)); p.replace(name)
def wait(name):
    end=time.monotonic()+5
    while not Path(name).exists():
        if time.monotonic()>=end: raise SystemExit(90)
        time.sleep(.001)
"""

class ReadinessWriters(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)

    def receipt(self,name):
        end = time.monotonic()+4
        while not (self.path/name).exists():
            if time.monotonic()>=end: self.fail('writer handshake watchdog: '+name)
            time.sleep(.001)
        return json.loads((self.path/name).read_text())

    def runtime(self,code):
        rt = HostRuntime([Service('main',milestone='notified-ready',startup=5000,stop=1000,cleanup=1000),
                          Service('consumer',requires=(('main','notified-ready'),),startup=5000)],
                         {'main':Command((PYTHON,'-c',code),PIN),
                          'consumer':Command((PYTHON,'-c','import time; time.sleep(30)'),PIN)},cwd=self.path)
        self.addCleanup(rt.close)
        return rt

    def test_second_notification_gets_epipe_without_relaunch(self):
        code = PRELUDE+r"""
os.write(fd,b'READY\n'); receipt('first',True); wait('again')
try: os.write(fd,b'READY\n'); receipt('second','unexpected-success')
except BrokenPipeError: receipt('second','epipe')
time.sleep(30)
"""
        rt = self.runtime(code); rt.start(['consumer']); self.receipt('first')
        rt.until(lambda: rt.model.active is None)
        self.assertTrue(rt.model.state['main'].ready)
        (self.path/'again').touch(); self.assertEqual(self.receipt('second'),'epipe')
        rt.pump()
        self.assertEqual([x for x in rt.log if x[0]=='launch'],[('launch','main',1),('launch','consumer',1)])
        self.assertFalse(rt.ready)

    def test_bounded_junk_pressure_closes_after_one_bounded_read(self):
        code = PRELUDE+"""
os.set_blocking(fd,False)
written=os.write(fd,b'X'*4096); receipt('first',written)
end=time.monotonic()+5; attempts=0; outcome='bound'
while time.monotonic()<end and written<1048576:
    attempts+=1
    try: written+=os.write(fd,b'X'*4096)
    except BlockingIOError: time.sleep(.001)
    except BrokenPipeError: outcome='epipe'; break
receipt('pressure',dict(outcome=outcome,written=written,attempts=attempts))
time.sleep(30)
"""
        rt = self.runtime(code); rt.start(['consumer']); self.assertGreater(self.receipt('first'),0)
        reader = rt.ready[('main',1)][0]; reads=[]; real_read=os.read
        def observe(fd,count):
            if fd==reader: reads.append(count)
            return real_read(fd,count)
        with patch('prototypes.host_runtime.runtime.os.read',side_effect=observe): rt.pump()
        self.assertEqual(reads,[6])
        self.assertIn(('invalid-ready','main',1),rt.log)
        self.assertFalse(rt.ready)
        self.assertEqual(rt.model.state['consumer'].generation,0)
        self.assertFalse(rt.model.state['main'].ready)
        pressure = self.receipt('pressure')
        self.assertEqual(pressure['outcome'],'epipe')
        self.assertLessEqual(pressure['written'],1048576)
        self.assertIsNone(rt.children[('main',1)].poll())

    def test_late_forked_helper_cannot_revive_exited_main(self):
        code = PRELUDE+"""
parent=os.getpid(); child=os.fork()
if child:
    wait('helper'); raise SystemExit(0)
end=time.monotonic()+10
receipt('helper',dict(pid=os.getpid(),parent=os.getppid(),main=parent))
sent=False; retried=False
try:
    while time.monotonic()<end:
        if Path('release').exists(): break
        if not sent and Path('send').exists():
            receipt('late-write',dict(bytes=os.write(fd,b'READY\\n'),parent=os.getppid()))
            sent=True
        if not retried and Path('retry').exists():
            try: os.write(fd,b'READY\\n'); receipt('retry-result','unexpected-success')
            except BrokenPipeError: receipt('retry-result','epipe')
            retried=True
        time.sleep(.001)
    else: receipt('expired',True)
finally:
    os.close(fd); receipt('released','writer-closed-exit-path-reached')
os._exit(0)
"""
        rt = self.runtime(code)
        # Registration precedes spawn so even a later assertion requests orphan release.
        def release():
            (self.path/'release').touch()
            if (self.path/'helper').exists(): self.receipt('released')
        self.addCleanup(release)
        rt.start(['consumer']); hello=self.receipt('helper')
        main=rt.children[('main',1)]
        self.assertEqual(hello['parent'],main.pid)
        self.assertEqual(main.wait(timeout=2),0)
        (self.path/'send').touch(); late=self.receipt('late-write')
        self.assertEqual(late['bytes'],6)
        self.assertNotEqual(late['parent'],main.pid)
        rt.pump()
        self.assertFalse(rt.model.state['main'].ready)
        self.assertEqual(rt.model.state['consumer'].generation,0)
        self.assertFalse(rt.ready)
        (self.path/'retry').touch(); self.assertEqual(self.receipt('retry-result'),'epipe')
        rt.until(lambda: not rt.children and not rt.pending)
        release()
        self.assertFalse((self.path/'expired').exists())
        print('LATE-HELPER-WITNESS '+json.dumps(dict(main_reaped=True,late_write=late,
              helper_release=self.receipt('released'),helper_reaping='unobserved')),file=sys.stderr)

if __name__ == '__main__': unittest.main()
