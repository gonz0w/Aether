import hashlib
import os
from unittest.mock import patch
from pathlib import Path
import sys
import tempfile
import unittest
from prototypes.host_runtime.runtime import Command, HostRuntime
from prototypes.runtime_model.model import Service, Rejected

PYTHON = str(Path(sys.executable).resolve())
PIN = hashlib.sha256(Path(PYTHON).read_bytes()).hexdigest()
SLEEP = "import time; time.sleep(30)"
READY = "import os,time; os.write(int(os.environ['AETHER_READY_FD']),b'READY\\n'); time.sleep(30)"

class RealChildren(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
    def runtime(self, services, codes):
        rt = HostRuntime(services, {n:Command((PYTHON,'-c',code),PIN) for n,code in codes.items()},cwd=self.tmp.name)
        self.addCleanup(rt.close)
        return rt
    def settled(self,rt):
        rt.until(lambda: rt.model.active is None)
    def drained(self,rt):
        rt.until(lambda: not rt.children and not rt.pending)
    def test_oneshot_completion_and_reaping(self):
        rt=self.runtime([Service('job',kind='oneshot',milestone='completed',startup=1000,cleanup=1000)],{'job':'pass'})
        rt.start(['job']); self.settled(rt); self.drained(rt)
        self.assertTrue(rt.model.state['job'].completed)
        self.assertEqual(rt.model.operations[-1].status,'success')
    def test_ready_dependency_and_reverse_stop(self):
        rt=self.runtime([Service('provider',milestone='notified-ready',startup=1000,stop=1000,cleanup=1000),Service('consumer',requires=(('provider','notified-ready'),),startup=1000,stop=1000,cleanup=1000)],{'provider':READY,'consumer':SLEEP})
        rt.start(['consumer']); self.settled(rt)
        self.assertTrue(rt.model.state['provider'].ready)
        rt.stop(['provider','consumer'],shutdown=True); self.settled(rt); self.drained(rt)
        stops=[n for a,n,g in rt.log if a=='stop']
        self.assertEqual(stops,['consumer','provider'])
    def test_bounded_retry(self):
        rt=self.runtime([Service('fail',milestone='notified-ready',retries=2,delay=10,startup=1000,cleanup=1000)],{'fail':'raise SystemExit(7)'})
        rt.start(['fail']); self.settled(rt); self.drained(rt)
        self.assertEqual(rt.model.state['fail'].generation,3)
        self.assertEqual(rt.model.operations[-1].status,'failed')
    def test_invalid_readiness_never_opens_dependency(self):
        bad="import os,time; os.write(int(os.environ['AETHER_READY_FD']),b'BOGUS!'); time.sleep(30)"
        rt=self.runtime([Service('bad',milestone='notified-ready',startup=1000,cleanup=1000),Service('dependent',requires=(('bad','notified-ready'),),startup=1000)],{'bad':bad,'dependent':SLEEP})
        rt.start(['dependent']); self.settled(rt); self.drained(rt)
        self.assertEqual(rt.model.state['dependent'].generation,0)
        self.assertIn(('invalid-ready','bad',1),rt.log)
    def test_force_requires_observed_exit_and_cleanup(self):
        code="import signal,os,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); os.write(int(os.environ['AETHER_READY_FD']),b'READY\\n'); time.sleep(30)"
        rt=self.runtime([Service('stubborn',milestone='notified-ready',startup=1000,stop=30,cleanup=1000)],{'stubborn':code})
        rt.start(['stubborn']); self.settled(rt)
        rt.stop(['stubborn']); self.settled(rt); self.drained(rt)
        self.assertIn(('force','stubborn',1),rt.log)
        self.assertFalse(rt.model.state['stubborn'].owned)
        self.assertEqual(rt.model.state['stubborn'].cleanup,'complete')
        self.assertEqual(rt.model.operations[-1].status,'incomplete')
    def test_startup_timeout(self):
        rt=self.runtime([Service('quiet',milestone='notified-ready',startup=50,stop=1000,cleanup=1000)],{'quiet':SLEEP})
        rt.start(['quiet']); self.settled(rt); self.drained(rt)
        self.assertEqual(rt.model.state['quiet'].reason,'startup-timeout')
    def test_changed_pin_rejected_before_launch(self):
        with self.assertRaises(Rejected):
            HostRuntime([Service('bad')],{'bad':Command((PYTHON,'-c','pass'),'0'*64)},cwd=self.tmp.name)
    def test_fresh_pipe_and_generation_on_retry(self):
        code="import os,time; from pathlib import Path; p=Path('count'); n=int(p.read_text())+1 if p.exists() else 1; p.write_text(str(n)); os.write(int(os.environ['AETHER_READY_FD']),b'READY\\n') if n==2 else None; time.sleep(30) if n==2 else None; raise SystemExit(9)"
        rt=self.runtime([Service('retry',milestone='notified-ready',retries=1,delay=10,startup=1000,stop=1000,cleanup=1000)],{'retry':code})
        rt.start(['retry']); self.settled(rt)
        self.assertTrue(rt.model.state['retry'].ready)
        self.assertEqual(rt.model.state['retry'].generation,2)
        self.assertEqual(set(rt.children),{('retry',2)})
        rt.stop(['retry']); self.settled(rt); self.drained(rt)

    def test_readiness_fragmented_into_single_byte_reads(self):
        rt=self.runtime([Service('fragment',milestone='notified-ready',startup=1000,stop=1000,cleanup=1000)],{'fragment':READY})
        rt.start(['fragment'])
        real_read=os.read
        # Actual pipe bytes, forced small reads; no assumption about pipe write boundaries.
        with patch('prototypes.host_runtime.runtime.os.read', side_effect=lambda fd,n: real_read(fd,min(n,1))):
            self.settled(rt)
        self.assertTrue(rt.model.state['fragment'].ready)
        self.assertFalse(rt.ready)
        rt.stop(['fragment']); self.settled(rt); self.drained(rt)

    def test_coalesced_trailing_bytes_do_not_change_first_frame(self):
        code="import os,time; os.write(int(os.environ['AETHER_READY_FD']),b'READY\\nignored'); time.sleep(30)"
        rt=self.runtime([Service('frame',milestone='notified-ready',startup=1000,stop=1000,cleanup=1000)],{'frame':code})
        rt.start(['frame']); self.settled(rt)
        self.assertTrue(rt.model.state['frame'].ready)
        self.assertNotIn(('invalid-ready','frame',1),rt.log)
        self.assertFalse(rt.ready)
        rt.stop(['frame']); self.settled(rt); self.drained(rt)

    def test_partial_frame_eof_is_not_readiness(self):
        code="import os,time; fd=int(os.environ['AETHER_READY_FD']); os.write(fd,b'REA'); os.close(fd); time.sleep(30)"
        rt=self.runtime([Service('partial',milestone='notified-ready',startup=1000,stop=1000,cleanup=1000)],{'partial':code})
        rt.start(['partial']); self.settled(rt); self.drained(rt)
        self.assertFalse(rt.model.state['partial'].ready)
        self.assertIn(('invalid-ready','partial',1),rt.log)
        self.assertEqual(rt.model.operations[-1].status,'failed')
        self.assertFalse(rt.ready)

    def test_wrong_partial_prefix_rejects_without_waiting_for_eof(self):
        code="import os,time; os.write(int(os.environ['AETHER_READY_FD']),b'X'); time.sleep(30)"
        rt=self.runtime([Service('prefix',milestone='notified-ready',startup=1000,stop=1000,cleanup=1000)],{'prefix':code})
        rt.start(['prefix']); self.settled(rt); self.drained(rt)
        self.assertIn(('invalid-ready','prefix',1),rt.log)
        self.assertNotEqual(rt.model.state['prefix'].reason,'startup-timeout')

    def test_unrelated_inheritable_descriptor_is_closed(self):
        read,write=os.pipe()
        self.addCleanup(os.close,read); self.addCleanup(os.close,write)
        os.set_inheritable(write,True)
        code=("import os,errno; fd="+str(write)+"\n"
              "try: os.fstat(fd)\n"
              "except OSError as e: raise SystemExit(0 if e.errno==errno.EBADF else 2)\n"
              "raise SystemExit(3)\n")
        rt=self.runtime([Service('fdcheck',kind='oneshot',milestone='completed',startup=1000,cleanup=1000)],{'fdcheck':code})
        rt.start(['fdcheck']); self.settled(rt); self.drained(rt)
        self.assertTrue(rt.model.state['fdcheck'].completed)
        self.assertEqual(rt.model.state['fdcheck'].terminal_detail,0)

    def test_known_exit_discards_buffered_ready(self):
        code="import os; os.write(int(os.environ['AETHER_READY_FD']),b'READY\\n')"
        rt=self.runtime([Service('gone',milestone='notified-ready',startup=1000,cleanup=1000),Service('dependent',requires=(('gone','notified-ready'),),startup=1000)],{'gone':code,'dependent':SLEEP})
        rt.start(['dependent'])
        # Establish exit before the observation cut, rather than race a sleep.
        rt.children[('gone',1)].wait(timeout=2)
        self.settled(rt); self.drained(rt)
        self.assertFalse(rt.model.state['gone'].ready)
        self.assertEqual(rt.model.state['dependent'].generation,0)
        self.assertFalse(rt.ready)

    def test_start_after_idle_receives_fresh_budgets(self):
        rt=self.runtime([Service('idle',milestone='notified-ready',startup=1000)],{'idle':SLEEP})
        # Inject adapter time; pipes, process creation and reaping remain real.
        with patch.object(rt,'now',return_value=5000):
            rt.start(['idle'],budget=3000)
            self.assertEqual(rt.model.active.deadline,8000)
            self.assertEqual(rt.model.state['idle'].deadline,6000)
            rt.pump()
        self.assertNotIn(('stop','idle',1),rt.log)
        self.assertNotIn(('force','idle',1),rt.log)

    def test_stop_after_idle_receives_fresh_budgets(self):
        code="import signal,os,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); os.write(int(os.environ['AETHER_READY_FD']),b'READY\\n'); time.sleep(30)"
        rt=self.runtime([Service('idle',milestone='notified-ready',startup=1000,stop=1000)],{'idle':code})
        rt.start(['idle']); self.settled(rt)
        future=rt.model.now+5000
        with patch.object(rt,'now',return_value=future):
            first=rt.stop(['idle'],budget=3000)
            self.assertEqual(rt.model.active.deadline,future+3000)
            self.assertEqual(rt.model.state['idle'].deadline,future+1000)
            rt.pump()
        with patch.object(rt,'now',return_value=future+500):
            self.assertEqual(rt.stop(['idle'],budget=9000),first)
        self.assertEqual(rt.model.active.deadline,future+3000)
        self.assertEqual(rt.model.state['idle'].deadline,future+1000)
        self.assertNotIn(('force','idle',1),rt.log)

    def test_duplicate_start_does_not_refresh_deadline(self):
        rt=self.runtime([Service('quiet',milestone='notified-ready',startup=1000)],{'quiet':SLEEP})
        with patch.object(rt,'now',return_value=5000):
            first=rt.start(['quiet'],budget=3000)
        with patch.object(rt,'now',return_value=5500):
            self.assertEqual(rt.start(['quiet'],budget=9000),first)
        self.assertEqual(rt.model.active.deadline,8000)
        self.assertEqual(rt.model.state['quiet'].deadline,6000)
        self.assertEqual([a for a,n,g in rt.log if a=='launch'],['launch'])

    def test_request_sync_processes_existing_overdue_timer(self):
        rt=self.runtime([Service('quiet',milestone='notified-ready',startup=1000,stop=1000)],{'quiet':SLEEP})
        with patch.object(rt,'now',return_value=5000):
            rt.start(['quiet'],budget=3000)
        with patch.object(rt,'now',return_value=6500):
            # Synchronization precedes validation; the expired service is not revived.
            with self.assertRaises(Rejected):
                rt.start(['missing'])
        self.assertEqual(rt.model.state['quiet'].reason,'startup-timeout')
        self.assertEqual(rt.model.state['quiet'].deadline,7000)
        self.assertEqual(rt.model.state['quiet'].phase,'stopping')
        self.assertIn(('stop','quiet',1),rt.log)

if __name__=='__main__': unittest.main()
