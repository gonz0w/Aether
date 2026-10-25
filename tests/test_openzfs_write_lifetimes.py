# SPDX-License-Identifier: BSD-2-Clause
"""Successful-TXG record reuse with actual graph/provider bodies and pinned borrows."""
from pathlib import Path
import subprocess
import unittest
import test_openzfs_pool_repeat as repeat
from openzfs_pool import lifetime_write_hooks
ROOT, OWNED=repeat.ROOT,repeat.OWNED

class WriteLifetimes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=repeat.RepeatedTransactions;cls.base.setUpClass();cls.addClassCleanup(cls.base.doClassCleanups)
        cls.hooks=lifetime_write_hooks((OWNED/'pool-vdev-hooks.inc').read_text())
        cls.flow=(OWNED/'pool-lifetime.inc').read_text()
        cls.binary=cls.compile(cls.flow,'lifetime')

    @classmethod
    def compile(cls,flow,name):
        out=cls.base.base.output
        (out/'repeat-flow-base.inc').write_text(cls.base.driver)
        prefix=(ROOT/'tests/fixtures/openzfs_pool_repeat.c').read_text().split('int main(int argc, char **argv)')[0]
        (out/'lifetime-flow-base.inc').write_text(prefix.replace('pool_repeat_records[0]','pool_record'))
        (out/'pool-bodies.inc').write_text(cls.base.file)
        (out/'pool-graph-bodies.inc').write_text(cls.base.base.graph)
        (out/'pool-vdev-hooks.inc').write_text(cls.hooks)
        (out/'pool-lifetime.inc').write_text(flow)
        sdk=subprocess.check_output(['xcrun','--show-sdk-path'],text=True).strip();binary=out/name
        p=subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang','-std=gnu11','-O2','-Wall','-Wextra','-Werror','-pthread','-isysroot',sdk,'-I'+str(out),'-I'+str(OWNED),'-I'+str(ROOT/'tests/fixtures'),str(OWNED/'pool-witness.c'),str(ROOT/'tests/fixtures/openzfs_pool_lifetime.c'),'-o',str(binary)],capture_output=True,text=True,timeout=30)
        if p.returncode:raise RuntimeError(p.stdout+p.stderr)
        return binary

    def run_mode(self,mode,binary=None,expected=0):
        p=subprocess.run([str(binary or self.binary),str(mode)],capture_output=True,text=True,timeout=10)
        self.assertEqual(p.returncode,expected,p.stdout+p.stderr)
        if expected:self.assertIn('pool hook rejection:',p.stderr)

    def test_reuse_eight_and64_transactions_with_constant_state_and_no_device_reset(self):
        self.run_mode(0);self.run_mode(75)

    def test_every_position_live_pins_graph_operations_requests_and_missing_wait_block_retirement(self):
        for mode in range(1,41):
            with self.subTest(mode=mode):self.run_mode(mode)

    def test_failed_disposition_stale_callbacks_identity_overflow_and_double_retirement_fail_closed(self):
        for mode in range(41,75):
            if mode==72:continue
            with self.subTest(mode=mode):self.run_mode(mode)

    def test_compiling_lifetime_guard_omissions_fail_semantically(self):
        variants=[('epoch','index != atomic_load(&pool_epoch)','((void)index,0)',57),
            ('graph','i < POOL_GRAPH_SLOTS; ++i)\n        if (atomic_load_explicit(&pool_nodes[i].address, memory_order_acquire))\n            error = EBUSY;', 'i < 0; ++i)\n        if (atomic_load_explicit(&pool_nodes[i].address, memory_order_acquire))\n            error = EBUSY;',17),
            ('error','operation_error || !target','!target',41),
            ('counter','atomic_fetch_add(&pool_completed, 1);','(void)0;',0)]
        for name,old,new,mode in variants:
            with self.subTest(name=name):
                self.assertEqual(self.flow.count(old),1)
                self.run_mode(mode,self.compile(self.flow.replace(old,new,1),name),1)

    def test_compiling_both_old_wait_guards_omitted_cannot_publish_new_success(self):
        self.assertEqual(self.flow.count('requested < target'),1)
        self.assertEqual(self.flow.count('target && requested >= target'),1)
        changed=self.flow.replace('requested < target','0',1).replace('target && requested >= target','target',1)
        self.run_mode(59,self.compile(changed,'old-wait-both'),1)

    def test_compiling_missing_retirement_exclusion_callback_pin_or_request_guard_fails(self):
        marker='int aether_pool_lifetime_retire('
        at=self.flow.index(marker);head,tail=self.flow[:at],self.flow[at:]
        old='if (!pool_exclusive())\n        return EBUSY;'
        self.assertEqual(tail.count(old),1)
        self.run_mode(1,self.compile(head+tail.replace(old,'if (0) return EBUSY;',1),'no-exclusive'),1)
        at=self.flow.index('void aether_pool_root_end(');stop=self.flow.index('void aether_pool_sync_observe(',at)
        target=self.flow[at:stop];old='if (!pool_enter())\n        return;'
        self.assertEqual(target.count(old),1)
        changed=self.flow[:at]+target.replace(old,'if (0) return;',1)+self.flow[stop:]
        self.run_mode(68,self.compile(changed,'no-callback-pin'),1)
        import re
        changed,n=re.subn(r'atomic_load_explicit\(&pool_requests\[i\]\.request,\s*memory_order_acquire\)', '0', self.flow)
        self.assertEqual(n,1)
        self.run_mode(33,self.compile(changed,'no-request-guard'),1)


import test_openzfs_eight_writes as eight

class LifetimesProbe(eight.EightProbe):
    @classmethod
    def compile(cls,body,reader,name):
        return cls.base.compile(body,3,reader,name,('-DSZ_EIGHT=1','-DSZ_LIFETIMES=1'))

    def test_busy_retirement_after_first_or_eighth_write_preserves_actual_progress(self):
        for mode in (31,32):self.base.run_mode(self,self.binaries[0],mode)

    def test_compiling_missing_retirement_context_close_or_failed_disposition_fails96(self):
        import re
        pattern=r'aether_pool_lifetime_retire\(\s*error,\s*result\.txg,\s*result\.bytes_staged,\s*result\.state\)'
        omitted,n=re.subn(pattern,'0',self.body);self.assertEqual(n,1)
        self.base.run_mode(self,self.compile(omitted,0,'no-retirement'),0,expected=96)
        changed,n=re.subn(r'error,\s*result\.txg,','0, result.txg,',self.body);self.assertEqual(n,1)
        self.base.run_mode(self,self.compile(changed,0,'failed-disposition'),16,expected=96)
        changed,n=re.subn(r'aether_zpl_close\(&view\);(\s+int retired =\s*aether_pool_lifetime_retire)',r'((void)view);\1',self.body)
        self.assertEqual(n,1)
        self.base.run_mode(self,self.compile(changed,0,'close-before-retire'),0,expected=96)




if __name__ == "__main__":
    unittest.main()
