# SPDX-License-Identifier: BSD-2-Clause
"""Bounded length retirement against original graph/observer fixture bodies."""
from pathlib import Path
import subprocess
import unittest

import test_openzfs_fs_mixed as prior
from openzfs_fs_bulk import bulk_lifetime_hooks, bulk_lifetime_record

ROOT, OWNED = prior.ROOT, prior.OWNED
PATTERN = '((n == 0 || n == 3 || n == 5 || n == 6) ? 0 : 4096)'


class BulkLifetime(prior.MixedLifetime):
    @classmethod
    def setUpClass(cls):
        cls.prior = prior.original.WriteLifetimes
        cls.prior.setUpClass(); cls.addClassCleanup(cls.prior.doClassCleanups)
        cls.hooks = bulk_lifetime_hooks((OWNED/'pool-vdev-hooks.inc').read_text())
        cls.flow = bulk_lifetime_record((OWNED/'pool-lifetime.inc').read_text())
        cls.binary = cls.compile(cls.flow, 'bulk')

    @classmethod
    def compile(cls, flow, name, stage=PATTERN, selection=PATTERN):
        out=cls.prior.base.base.output
        (out/'pool-vdev-hooks.inc').write_text(cls.hooks)
        (out/'pool-bulk-lifetime.inc').write_text(flow)
        fixture=(ROOT/'tests/fixtures/openzfs_pool_lifetime.c').read_text().replace('4096',str(stage))
        macro=('#define aether_pool_lifetime_retire(error,target,staged,state) '
               '(('+str(selection)+') == 0 ? aether_pool_namespace0_retire(error,target,staged,state) : '
               'aether_pool_service_bytes_retire(error,target,staged,state,('+str(selection)+')))\n')
        fixture=fixture.replace('int main(int argc, char **argv)',macro+'int main(int argc, char **argv)',1)
        source=out/'bulk-fixture.c';source.write_text(fixture)
        binary=out/name;sdk=subprocess.check_output(['xcrun','--show-sdk-path'],text=True).strip()
        result=subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang','-std=gnu11','-O2',
            '-Wall','-Wextra','-Werror','-pthread','-isysroot',sdk,'-I'+str(out),'-I'+str(OWNED),
            '-I'+str(ROOT/'tests/fixtures'),str(OWNED/'pool-witness.c'),str(source),'-o',str(binary)],
            capture_output=True,text=True,timeout=30)
        if result.returncode:raise RuntimeError(result.stdout+result.stderr)
        return binary

    def test_fixed_eight_mixed_and_host64_synthetic_reuse_same_observer(self):
        self.assertIn('observer bytes=7596 records=1 completed=8',self.run_mode(0).stdout)
        self.run_mode(75)
        self.run_mode(0,self.compile(self.flow,'namespace-only',0,0))
        for length in (1,16,63,64,65,4095,4096):
            with self.subTest(length=length):self.run_mode(0,self.compile(self.flow,'bytes'+str(length),length,length))

    def test_staging_class_and_old4096_cannot_be_substituted(self):
        for stage in (0,16,4095,4097):
            with self.subTest(stage=stage):self.run_mode(0,self.compile(self.flow,'bad-stage'+str(stage),stage),1)
        for length in (4097,2**32+1):
            with self.subTest(length=length):self.run_mode(0,self.compile(self.flow,'bad-length'+str(length),length,length),1)
        # Selecting the data entry with expected0 must reject, whereas the fixed
        # namespace entry above succeeds with0. This omission forces that entry.
        flow=self.flow.replace('return pool_bulk_retire(error, target, staged, state, 0);',
            'return aether_pool_service_bytes_retire(error, target, staged, state, 0);')
        self.run_mode(0,self.compile(flow,'zero-data',0,0),1)

    def test_exact_derivation_rejects_drift_duplicate_and_already_selected(self):
        seed=(OWNED/'pool-lifetime.inc').read_text()
        for bad in (seed+' ',seed+seed,self.flow):
            with self.assertRaisesRegex(ValueError,'source identity'):bulk_lifetime_record(bad)
        hooks=(OWNED/'pool-vdev-hooks.inc').read_text()
        for bad in (hooks+hooks,hooks.replace('#include "pool-flow.inc"','')):
            with self.assertRaises(ValueError):bulk_lifetime_hooks(bad)

    def test_compiling_failed_history_epoch_counter_and_staging_omissions_fail(self):
        for name,old,new,mode in (
            ('error','operation_error || !target','!target',41),
            ('epoch','index != atomic_load(&pool_epoch)','((void)index,0)',57),
            ('counter','atomic_fetch_add(&pool_completed, 1);','(void)0;',0),
            ('stage','staged != expected','((void)staged,0)',49),
            ('namespace-kind','return pool_bulk_retire(error, target, staged, state, 0);',
             'return pool_bulk_retire(error, target, staged, state, 16);',0)):
            self.assertEqual(self.flow.count(old),1)
            with self.subTest(name=name):self.run_mode(mode,self.compile(self.flow.replace(old,new,1),name),1)

    def test_exports_are_typed_and_legacy_contract_unmodified(self):
        symbols=subprocess.check_output(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/llvm-nm',
            '--defined-only','--extern-only',str(self.binary)],text=True)
        for name in ('aether_pool_namespace0_retire','aether_pool_service_bytes_retire'):self.assertIn(name,symbols)
        for name in ('pool_bulk_retire','aether_pool_lifetime_retire','aether_pool_service16_retire'):self.assertNotIn(name,symbols)
        self.assertIn('staged != 4096',(OWNED/'pool-lifetime.inc').read_text())
        self.assertIn('state, 16);',__import__('openzfs_fs_mixed').mixed_lifetime_record((OWNED/'pool-lifetime.inc').read_text()))


if __name__=='__main__':unittest.main()
