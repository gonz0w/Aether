# SPDX-License-Identifier: BSD-2-Clause
"""Typed namespace0/service16 success-only retirement; host fixtures, not native."""
from pathlib import Path
import subprocess
import unittest

import test_openzfs_write_lifetimes as original
from openzfs_fs_mixed import mixed_lifetime_hooks, mixed_lifetime_record

ROOT, OWNED = original.ROOT, original.OWNED
PATTERN = '((n == 0 || n == 3 || n == 5 || n == 6) ? 0 : 16)'


class MixedLifetime(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prior = original.WriteLifetimes
        cls.prior.setUpClass(); cls.addClassCleanup(cls.prior.doClassCleanups)
        cls.hooks = mixed_lifetime_hooks((OWNED/'pool-vdev-hooks.inc').read_text())
        cls.flow = mixed_lifetime_record((OWNED/'pool-lifetime.inc').read_text())
        cls.binary = cls.compile(cls.flow, 'mixed')

    @classmethod
    def compile(cls, flow, name, stage=PATTERN, selection=PATTERN):
        out=cls.prior.base.base.output
        (out/'pool-vdev-hooks.inc').write_text(cls.hooks)
        (out/'pool-mixed-lifetime.inc').write_text(flow)
        fixture=(ROOT/'tests/fixtures/openzfs_pool_lifetime.c').read_text()
        # All4096 literals in this fixture are retirement arguments; original
        # media/graph/phase bodies in its separate includes remain unchanged.
        fixture=fixture.replace('4096',str(stage))
        marker='int main(int argc, char **argv)'
        macro='#define aether_pool_lifetime_retire(...) (('+str(selection)+') == 0 ? aether_pool_namespace0_retire(__VA_ARGS__) : aether_pool_service16_retire(__VA_ARGS__))\n'
        fixture=fixture.replace(marker,macro+marker,1)
        source=out/'mixed-fixture.c'; source.write_text(fixture)
        binary=out/name;sdk=subprocess.check_output(['xcrun','--show-sdk-path'],text=True).strip()
        result=subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang','-std=gnu11','-O2','-Wall','-Wextra','-Werror','-pthread',
            '-isysroot',sdk,'-I'+str(out),'-I'+str(OWNED),'-I'+str(ROOT/'tests/fixtures'),
            str(OWNED/'pool-witness.c'),str(source),'-o',str(binary)],capture_output=True,text=True,timeout=30)
        if result.returncode:raise RuntimeError(result.stdout+result.stderr)
        return binary

    def run_mode(self, mode, binary=None, expected=0):
        p=subprocess.run([str(binary or self.binary),str(mode)],capture_output=True,text=True,timeout=10)
        self.assertEqual(p.returncode,expected,p.stdout+p.stderr)
        if expected:self.assertIn('pool hook rejection:',p.stderr)
        return p

    def test_fixed_eight_mixed_and_host64_synthetic_reuse_same_observer(self):
        p=self.run_mode(0);self.assertIn('observer bytes=7596 records=1 completed=8',p.stdout)
        self.run_mode(75)  # Host exhaustion/epochs only; native remains exactly8.
        self.run_mode(0,self.compile(self.flow,'only0',0,0))
        self.run_mode(0,self.compile(self.flow,'only16',16,16))

    def test_original_pin_graph_request_wait_epoch_failure_overflow_cases(self):
        for mode in range(1,75):
            if mode==72:continue
            with self.subTest(mode=mode):self.run_mode(mode)

    def test_staging_class_and_old4096_cannot_be_substituted(self):
        for stage in (0,16,4096):
            with self.subTest(stage=stage):self.run_mode(0,self.compile(self.flow,'wrong-stage'+str(stage),stage),1)
        for selection in (0,16):
            with self.subTest(selection=selection):self.run_mode(0,self.compile(self.flow,'wrong-kind'+str(selection),selection=selection),1)

    def test_exact_derivation_rejects_drift_duplicate_and_already_selected(self):
        seed=(OWNED/'pool-lifetime.inc').read_text()
        for bad in (seed+' ',seed+seed,self.flow):
            with self.assertRaisesRegex(ValueError,'source identity'):mixed_lifetime_record(bad)
        hooks=(OWNED/'pool-vdev-hooks.inc').read_text()
        for bad in (hooks+hooks,hooks.replace('#include "pool-flow.inc"','')):
            with self.assertRaises(ValueError):mixed_lifetime_hooks(bad)

    def test_compiling_failed_history_epoch_counter_and_staging_omissions_fail(self):
        for name,old,new,mode in (
            ('error','operation_error || !target','!target',41),
            ('epoch','index != atomic_load(&pool_epoch)','((void)index,0)',57),
            ('counter','atomic_fetch_add(&pool_completed, 1);','(void)0;',0),
            ('stage','staged != expected','((void)staged,0)',49),
            ('namespace-kind','return pool_mixed_retire(error, target, staged, state, 0);','return pool_mixed_retire(error, target, staged, state, 16);',0)):
            self.assertEqual(self.flow.count(old),1)
            with self.subTest(name=name):self.run_mode(mode,self.compile(self.flow.replace(old,new,1),name),1)

    def test_exports_are_typed_and_legacy_contract_unmodified(self):
        symbols=subprocess.check_output(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/llvm-nm','--defined-only','--extern-only',str(self.binary)],text=True)
        for name in ('aether_pool_namespace0_retire','aether_pool_service16_retire'):self.assertIn(name,symbols)
        self.assertNotIn('pool_mixed_retire',symbols)
        self.assertNotIn('aether_pool_lifetime_retire',symbols)
        self.assertIn('staged != 4096',(OWNED/'pool-lifetime.inc').read_text())
        self.assertIn('staged != 16',__import__('openzfs_fs_lifetime').service_lifetime_record((OWNED/'pool-lifetime.inc').read_text()))


if __name__=='__main__':unittest.main()
