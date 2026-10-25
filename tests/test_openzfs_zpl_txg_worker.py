# SPDX-License-Identifier: BSD-2-Clause
"""Bounded original TXG worker/ordered-root observations, never durability."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import test_openzfs_pool_repeat as repeat
import test_openzfs_zpl_first_write as first
import test_openzfs_zpl_stages as outer
import test_service_runtime as runtime_tests
import test_zpl_pair as controls
from openzfs_pool import patch_worker_txg, worker_body, worker_flow, worker_write_provider, worker_publisher
from openzfs_elapsed import CURRENT
import zpl_pair as pair

ROOT, OWNED, runtime = repeat.ROOT, repeat.OWNED, outer.runtime


class Workers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='aether-txg-worker-');cls.addClassCleanup(cls.temp.cleanup)
        cls.out=Path(cls.temp.name)
        cls.original=(CURRENT/'baseline/source/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1/module/zfs/txg.c').read_text()
        cls.selected=patch_worker_txg(cls.original)
        cls.bodies='\n'.join(worker_body(cls.selected,n,False) for n in ('txg_sync_thread','txg_quiesce_thread'))
        cls.binary=cls.compile(cls.bodies,'workers')

    @classmethod
    def compile(cls,bodies,name):
        (cls.out/'worker-bodies.inc').write_text(bodies)
        sdk=subprocess.check_output(['xcrun','--show-sdk-path'],text=True).strip();binary=cls.out/name
        r=subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang','-isysroot',sdk,'-std=gnu11','-O2','-Wall','-Wextra','-Werror','-I'+str(cls.out),str(ROOT/'tests/fixtures/openzfs_txg_workers.c'),'-o',str(binary)],capture_output=True,text=True,timeout=30)
        if r.returncode:raise RuntimeError(r.stdout+r.stderr)
        return binary

    def test_actual_original_workers_emit_outside_lock_at_handoff_and_sync_boundaries(self):
        r=subprocess.run([str(self.binary)],capture_output=True,text=True,timeout=5);self.assertEqual(r.returncode,0,r.stdout+r.stderr)

    def test_compiling_omitted_and_moved_under_lock_markers_fail99(self):
        call="\t\taether_pool_worker_progress(dp, txg, 'q');"
        bads=[self.bodies.replace(call,'',1),self.bodies.replace(call,'',1).replace('\t\ttxg_quiesce(dp, txg);\n\t\tmutex_enter(&tx->tx_sync_lock);','\t\ttxg_quiesce(dp, txg);\n\t\tmutex_enter(&tx->tx_sync_lock);\n'+call,1),self.bodies.replace("txg, 'd'", "txg, 's'",1)]
        for n,bad in enumerate(bads):
            self.assertNotEqual(bad,self.bodies)
            binary=self.compile(bad,'bad'+str(n));r=subprocess.run([str(binary)],capture_output=True,text=True,timeout=5)
            self.assertEqual(r.returncode,99,r.stdout+r.stderr);self.assertIn('TXG WORKER oracle99',r.stderr)

    def test_actual_partial_link_coalescing_and_distinct_final_relay(self):
        flow=worker_flow((OWNED/'pool-repeat.inc').read_text())
        start=flow.index('extern void aether_pool_worker_phase')
        gate=flow[start:flow.index('static void pool_flow_prepare',start)]
        prelude="""#include <stdint.h>
#include <stdatomic.h>
enum { POOL_READY=2, POOL_TX_BOUND=2 };
static void *pool_observer=(void*)1, *pool_dp=(void*)1;
static _Atomic unsigned pool_publication=2, pool_transaction=2, pool_repeat_count=1;
static struct { _Atomic uint64_t txg; } pool_repeat_records[1]={{7}};
"""
        actual=worker_publisher((runtime.SOURCE/'engine-startup.c').read_text())
        begin=actual.index('void aether_engine_utc_phase(')
        end=actual.index('\n#ifdef ENGINE_SPA_PHYSICAL',begin)
        publisher='static volatile unsigned char observed;\nstatic void engine_observe(unsigned char e) { observed=e; }\n'+actual[begin:end]
        sources={'gate':prelude+gate,'bad-gate':prelude+gate.replace('aether_pool_worker_phase','aether_engine_utc_phase'),
                 'dead':"extern void aether_engine_utc_phase(unsigned char); void unused_probe(void) { aether_engine_utc_phase('x'); }",
                 'entry':"extern void aether_pool_worker_progress(const void*, unsigned long, unsigned char); void _start(void) { aether_pool_worker_progress((void*)1,7,'b'); }",'publisher':publisher}
        llvm=Path('/opt/homebrew/Cellar/llvm@21/21.1.8');lld='/opt/homebrew/Cellar/lld@21/21.1.8_1/bin/ld.lld'
        for name,text in sources.items():
            source=self.out/(name+'.c');source.write_text(text)
            r=subprocess.run([str(llvm/'bin/clang'),'--no-default-config','--target=x86_64-linux-musl','-ffreestanding','-fno-stack-protector','-ffunction-sections','-fdata-sections','-O2','-nostdinc','-isystem',str(llvm/'lib/clang/21/include'),'-c',str(source),'-o',str(self.out/(name+'.o'))],capture_output=True,text=True,timeout=30)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        for name in ('gate','bad-gate'):
            r=subprocess.run([lld,'-r',str(self.out/(name+'.o')),str(self.out/'dead.o'),'-o',str(self.out/(name+'-partial.o'))],capture_output=True,text=True,timeout=30);self.assertEqual(r.returncode,0,r.stderr)
            r=subprocess.run([lld,'-static','--gc-sections','-e','_start',str(self.out/'entry.o'),str(self.out/(name+'-partial.o')),'-o',str(self.out/(name+'.elf'))],capture_output=True,text=True,timeout=30)
            if name=='bad-gate':
                self.assertNotEqual(r.returncode,0);self.assertIn('undefined symbol: aether_engine_utc_phase',r.stderr)
            else:
                self.assertEqual(r.returncode,0,r.stderr)
                from openzfs_elapsed import check_intermediate_imports
                imports=subprocess.check_output([str(llvm/'bin/llvm-nm'),'--undefined-only',str(self.out/'gate.elf')],text=True)
                check_intermediate_imports(imports,worker_stages=True)
        r=subprocess.run([lld,'-static','--gc-sections','--no-undefined','--undefined=aether_engine_utc_phase','--undefined=aether_pool_worker_phase','-e','_start',str(self.out/'entry.o'),str(self.out/'gate-partial.o'),str(self.out/'publisher.o'),'-o',str(self.out/'final.elf')],capture_output=True,text=True,timeout=30);self.assertEqual(r.returncode,0,r.stderr)
        symbols=subprocess.check_output([str(llvm/'bin/llvm-nm'),str(self.out/'final.elf')],text=True)
        self.assertIn(' T aether_pool_worker_phase',symbols);self.assertIn(' T aether_engine_utc_phase',symbols)

    def test_pins_source_drift_duplicate_and_inverse_insertions(self):
        for bad in (self.original+self.original,self.original.replace('spa_sync(spa, txg);','spa_sync(spa, txg+1);',1)):
            with self.assertRaises((ValueError,RuntimeError)):patch_worker_txg(bad)
        for n in ('txg_sync_thread','txg_quiesce_thread'):
            restored='\n'.join(l for l in worker_body(self.selected,n,False).splitlines() if 'aether_pool_worker_progress(' not in l)
            self.assertEqual(restored,worker_body(self.original,n))


class Flow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b=repeat.RepeatedTransactions;b.setUpClass();cls.addClassCleanup(b.doClassCleanups);cls.base=b
        cls.flow=worker_flow(b.flow);cls.out=b.base.output
        driver=(ROOT/'tests/fixtures/openzfs_pool_repeat.c').read_text()
        callback='''static unsigned worker_events;
void aether_pool_worker_phase(unsigned char event) {
    static const char wanted[]="bqsluodw";
    if (!(worker_events < 8 && event == wanted[worker_events])) { fprintf(stderr,"pool hook rejection: worker event order\\n"); exit(1); }
    ++worker_events;
}
'''
        driver=driver.replace('static unsigned repeat_mode;',callback+'\nstatic unsigned repeat_mode;',1)
        driver=driver.replace('    REQUIRE(!repeat_phases(0, 7));', '''    aether_pool_worker_progress(&foreign_dp,7,'q');
    aether_pool_worker_progress(&dp,8,'q');
    aether_pool_worker_progress(&dp,7,'q');
    aether_pool_worker_progress(&dp,7,'s');
    REQUIRE(!repeat_phases(0, 7));
    aether_pool_worker_progress(&dp,7,'d');
    aether_pool_worker_progress(&dp,7,'w');''',1)
        driver=driver.replace('    REQUIRE(!aether_zfs_volume_bind(17));', "    aether_pool_worker_progress(&dp,7,'q');\n    REQUIRE(!aether_zfs_volume_bind(17));",1)
        driver=driver.replace('    vdev_file_close(&leaf);', "    vdev_file_close(&leaf);\n    if (atomic_load(&pool_publication) == POOL_CLOSED) aether_pool_worker_progress(&dp,7,'q');")
        cls.driver=driver
        cls.binary=cls.compile(cls.flow,'flow')

    @classmethod
    def compile(cls,flow,name):
        (cls.out/'repeat-flow-base.inc').write_text(cls.base.driver)
        (cls.out/'pool-bodies.inc').write_text(cls.base.file)
        (cls.out/'pool-graph-bodies.inc').write_text(cls.base.base.graph)
        (cls.out/'pool-vdev-hooks.inc').write_text(cls.base.hooks)
        (cls.out/'pool-repeat.inc').write_text(flow)
        source=cls.out/'worker-flow.c';source.write_text(cls.driver)
        binary=cls.out/name;sdk=subprocess.check_output(['xcrun','--show-sdk-path'],text=True).strip()
        r=subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang','-std=gnu11','-O2','-Wall','-Wextra','-Werror','-pthread','-isysroot',sdk,'-I'+str(cls.out),'-I'+str(OWNED),'-I'+str(ROOT/'tests/fixtures'),str(OWNED/'pool-witness.c'),str(source),'-o',str(binary)],capture_output=True,text=True,timeout=30)
        if r.returncode:raise RuntimeError(r.stdout+r.stderr)
        return binary

    def test_actual_graph_first_target_owner_filter_retirement_and_all_previous_denials(self):
        for mode in range(17):
            r=subprocess.run([str(self.binary),str(mode)],capture_output=True,text=True,timeout=10)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)

    def test_compiling_foreign_filter_and_phase_omissions_fail_semantically(self):
        for n,old,new in ((0,'dp != pool_dp ||','((void)dp,0) ||'),(1,"local == 1 ? 'l'", "local == 1 ? 'u'")):
            self.assertEqual(self.flow.count(old),1)
            binary=self.compile(self.flow.replace(old,new,1),'bad-flow'+str(n));r=subprocess.run([str(binary),'0'],capture_output=True,text=True,timeout=10)
            self.assertNotEqual(r.returncode,0);self.assertIn('pool hook rejection:',r.stderr)


class Provider(unittest.TestCase):
    compile = classmethod(first.FirstProvider.compile.__func__)
    @classmethod
    def setUpClass(cls):
        b=first.writer.ZplWriter;b.setUpClass();cls.addClassCleanup(b.doClassCleanups);cls.base=b;cls.out=b.out
        cls.body='\n'.join(l for l in worker_write_provider((OWNED/'zpl-write.c').read_text()).splitlines() if not l.startswith('#include') and not l.startswith('#define AETHER_ZPL_WRITE_PROVIDER'))+'\n'
        fixture=(ROOT/'tests/fixtures/openzfs_zpl_write.c').read_text()
        callback='''static unsigned events;
void aether_pool_worker_progress(const void *dp, uint64_t txg, unsigned char event) {
    CHECK(dp==&pool && txg==42 && event=='w' && waits==1 && !tx_live && handles && !last_checks && !events++);
}
'''
        cls.fixture=fixture.replace('#include "zpl-adapter.inc"',callback+'\n#include "zpl-adapter.inc"',1).replace('    CHECK(error == expected_error);\n    CHECK(!handles', '    CHECK(events == (unsigned)waits);\n    CHECK(error == expected_error);\n    CHECK(!handles',1)
        cls.binary=cls.compile(cls.body,'worker-provider',False)
        cls.normal=cls.binary

    def test_compiling_missing_wait_marker_fails93(self):
        call="        aether_pool_worker_progress(spa_get_dsl(spa), out->txg, 'w');"
        binary=self.compile(self.body.replace(call,'',1),'missing-wait',False)
        r=subprocess.run([str(binary),'0'],capture_output=True,text=True,timeout=5)
        self.assertEqual(r.returncode,93,r.stdout+r.stderr)

    def test_all_existing_provider_errors_preserve_progress_and_wait_return_order(self):
        modes=[0,1,2,3,4,66,*range(10,35),*range(50,55),*range(60,66),68,69,70,*range(100,113),*range(120,147)]
        for mode in modes:
            r=subprocess.run([str(self.binary),str(mode)],capture_output=True,text=True,timeout=5)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)


class Controller(outer.StageController):
    @classmethod
    def setUpClass(cls):
        class Candidate(runtime_tests.PoolNamespaceWriteDriver):
            pool_zpl_stages=True
            pool_zpl_txg_stages=True
        Candidate.setUpClass();cls.addClassCleanup(Candidate.doClassCleanups);cls.candidate=Candidate


def success():
    return outer.success().replace(outer.observations(b'BIUVWLPOAMTorhc12vx'+(788).to_bytes(8,'little')+b'SDJFR'),outer.observations(b'BIUVWLPOAMTbqsluodw'+(788).to_bytes(8,'little')+b'SDJFR'),1)


class Decoder(unittest.TestCase):
    def test_all_prefixes_early_wait_error_and_no_false_qualification(self):
        data=b'BIUVWLPOAMTbqsluodw'+(788).to_bytes(8,'little')+b'SDJFR'
        for n in range(1,33):
            r=pair.decode_zpl_stages(outer.observations(data[:n]),txg_worker=True);self.assertFalse(r['qualification'])
        for n in range(8):
            data=b'BIUVWLPOAMT'+b'bqsluod'[:n]+b'E'+bytes([6,5,0,0,0])
            r=pair.decode_zpl_stages(outer.observations(data),txg_worker=True);self.assertEqual(r['error_projection'],{'stage':6,'errno':5})
        for path in pair.TXG_WORKER_PATHS[1:]:
            r=pair.decode_zpl_stages(outer.observations(b'BIUVWLPOAMT'+path),txg_worker=True);self.assertEqual(r['last_boundary'],'wait-return');self.assertFalse(r['qualification'])

    def test_old_foreign_reordered_duplicate_and_ambiguous_error_reject_or_stay_unknown(self):
        for data in (b'BIUVWLPOAMTeabcdw',b'BIUVWLPOAMTbsq',b'BIUVWLPOAMTbb',b'BIUVWLPOAMTbqsluodd'):
            with self.assertRaises(ValueError):pair.decode_zpl_stages(outer.observations(data),txg_worker=True)
        text=outer.observations(b'BIUVWLPOAMTbqsluodwE'+bytes([6,5,0,0,0]))
        self.assertIsNone(pair.decode_zpl_stages(text,txg_worker=True)['error_projection'])
        self.assertEqual(pair.decode_zpl_stages(text+first.failed_lifetime(),txg_worker=True)['error_projection'],{'stage':6,'errno':5})

    def test_success_guards_and_prepared_profile_rejection(self):
        r=runtime.check_zpl_write_trace(success(),True,False,True);self.assertEqual(r['stage_boundaries_observed'],'bqsluodw');self.assertNotIn('input_xdr_fnv1a64',r)
        f=controls.PairControls();f.setUp();self.addCleanup(f.doCleanups)
        f.execute(writer_text=success(),txg_worker_diagnostic=True);self.assertEqual(f.launched,['baseline','writer','reader'])
        for text in (outer.observations(b'BIUVWLPOAMTbq'),success().replace('phase=7','phase=6',1),outer.success()):
            with self.assertRaises(ValueError):f.execute(writer_text=text,txg_worker_diagnostic=True)
            self.assertEqual(f.launched,['baseline','writer'])
        b=f.builds;b['writer'].update(pool_zpl_repeat=True,pool_zpl_stages=True)
        with patch.object(runtime,'sealed'):
            with self.assertRaises(ValueError):pair.verify_prepared(f.output,b,True,True,False,True)
            b['writer']['pool_zpl_txg_stages']=True
            import copy
            b['baseline']=copy.deepcopy(b['reader']);b['baseline']['pool_zpl_recover']=False
            (f.output/'baseline').mkdir(exist_ok=True)
            for name in ('aether.iso','engine.elf'):
                (f.output/'baseline'/name).write_bytes((f.output/'reader'/name).read_bytes())
            pair.verify_prepared(f.output,b,True,True,False,True)
            with self.assertRaises(ValueError):pair.verify_prepared(f.output,b,True,True)

    def test_intermediate_phase_is_weak_and_scoped_to_worker_profile(self):
        from openzfs_elapsed import check_intermediate_imports
        weak=' U _DYNAMIC\n w aether_pool_worker_phase\n'
        check_intermediate_imports(weak,worker_stages=True)
        for text,selected in ((weak,False),(weak.replace('w aether','U aether'),True),(weak.replace('worker_phase','other'),True)):
            with self.assertRaises(RuntimeError):check_intermediate_imports(text,worker_stages=selected)

    def test_final_relay_origin_is_mandatory_and_cannot_be_substituted(self):
        owners={'engine-startup.o':['main','aether_pool_worker_phase'],
                'selected-engine.o':['kernel_init','kernel_fini','cv_init','cv_timedwait_hires','random_init','random_get_bytes','arc_all_memory','arc_available_memory','aether_zfs_granted_pages','aether_zfs_assigned_cpus'],
                'libaether_runtime.a(backend.o)':['aether_runtime_init','aether_runtime_finish','__aether_io']}
        mapping='\n'.join('0 0 0 1 /private/'+owner+':(.text)\n'+'\n'.join('0 0 0 1 '+symbol for symbol in names) for owner,names in owners.items())
        self.assertEqual(runtime.check_engine_bindings(mapping,txg_worker=True)['aether_pool_worker_phase'],'/private/engine-startup.o')
        for bad in (mapping.replace('0 0 0 1 aether_pool_worker_phase',''),mapping.replace('0 0 0 1 aether_pool_worker_phase','0 0 0 1 /private/selected-engine.o:(.text)\n0 0 0 1 aether_pool_worker_phase')):
            with self.assertRaisesRegex(ValueError,'aether_pool_worker_phase'):runtime.check_engine_bindings(bad,txg_worker=True)

    def test_invalid_selection_fails_before_intake(self):
        for flags in (['--txg-worker-diagnostic'],['--repeated-writes','--first-write-diagnostic','--txg-worker-diagnostic']):
            r=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/zpl_pair.py'),*flags,'--delivery','/absent','--utc-delivery','/absent'],capture_output=True,text=True,timeout=5);self.assertEqual(r.returncode,64)
        with patch.object(runtime,'intake',side_effect=AssertionError('intake')):
            with self.assertRaises(ValueError):runtime.suite(Path('/absent'),_zpl_txg_stages=True)
