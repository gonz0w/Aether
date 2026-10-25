# SPDX-License-Identifier: BSD-2-Clause
"""First-helper scalar observations preserve original errors and ownership."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import test_openzfs_zpl_write as writer
import test_openzfs_zpl_repeat as repeat
import test_openzfs_zpl_stages as outer
import test_service_runtime as runtime_tests
import test_zpl_pair as controls
from openzfs_pool import first_write_provider, first_write_probe
import zpl_pair as pair

ROOT, runtime = outer.ROOT, outer.runtime


class FirstProvider(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = writer.ZplWriter
        cls.base.setUpClass()
        cls.addClassCleanup(cls.base.doClassCleanups)
        cls.out = cls.base.out
        cls.body = '\n'.join(line for line in first_write_provider(
            (writer.OWNED / 'zpl-write.c').read_text()).splitlines()
                             if not line.startswith('#include') and not line.startswith('#define AETHER_ZPL_WRITE_PROVIDER')) + '\n'
        fixture = (ROOT / 'tests/fixtures/openzfs_zpl_write.c').read_text()
        monitor = r'''
#define DCHECK(value) do { if (!(value)) { fprintf(stderr, "HOST FIRST WRITE oracle98 line%d\n", __LINE__); exit(98); } } while (0)
static unsigned diagnostic_count;
static unsigned char diagnostic_bytes[8];
void aether_engine_utc_phase(unsigned char value)
{
    DCHECK(diagnostic_count < 8 && owned);
    switch (value) {
    case 'e': DCHECK(!diagnostic_count && !handles && !tx_live && !order_length); break;
    case 'a': DCHECK(handles && tx_live && !transaction.assigned && order[order_length-1]=='S'); break;
    case 'b': DCHECK(handles && tx_live && order[order_length-1]=='A' && !aborts); break;
    case 'c': DCHECK(handles && tx_live && transaction.assigned && !commits); break;
    case 'd': DCHECK(handles && !tx_live && commits && !waits); break;
    case 'w': DCHECK(handles && !tx_live && commits && !waits && updates); break;
    case 's': DCHECK(handles && !tx_live && waits && !last_checks); break;
    case 'f': DCHECK(!handles && !tx_live); break;
    default: DCHECK(0);
    }
    diagnostic_bytes[diagnostic_count++] = value;
}
'''
        cls.fixture = fixture.replace('#include "zpl-adapter.inc"', monitor + '\n#include "zpl-adapter.inc"', 1)
        check = r'''
    unsigned char wanted[8]; unsigned n = 0;
    if (DIAGNOSTIC) {
        wanted[n++]='e';
        if (memchr(order, 'A', order_length)) { wanted[n++]='a'; wanted[n++]='b'; }
        if (commits) { wanted[n++]='c'; wanted[n++]='d'; }
        if (waits) { wanted[n++]='w'; wanted[n++]='s'; }
        wanted[n++]='f';
    }
    DCHECK(diagnostic_count == n && !memcmp(wanted, diagnostic_bytes, n));
'''
        cls.fixture = cls.fixture.replace('    CHECK(error == expected_error);\n    CHECK(!handles', check + '\n    CHECK(error == expected_error);\n    CHECK(!handles', 1)
        cls.binary = cls.compile(cls.body, 'first', True)
        cls.normal = cls.compile(cls.body, 'normal', False)

    @classmethod
    def compile(cls, body, name, diagnostic):
        (cls.out / 'zpl-adapter.inc').write_text('#define AETHER_ZPL_WRITE_PROVIDER 1\n' + cls.base.read_body + body)
        fixture = cls.fixture.replace('DIAGNOSTIC', str(int(diagnostic)))
        if diagnostic:
            fixture = fixture.replace('int error = aether_zpl_write(mode', 'int error = aether_zpl_write_diagnostic(mode', 1)
        source = cls.out / (name + '.c'); source.write_text(fixture)
        binary = cls.out / name
        r = subprocess.run([str(cls.base.clang), '-isysroot', cls.base.sdk, '-std=gnu11', '-O2',
                            '-Wall','-Wextra','-Werror','-DAETHER_ZPL_ORDERED_WRITE=1',
                            '-I'+str(cls.out),'-I'+str(writer.OWNED),str(source),'-o',str(binary)],
                           capture_output=True,text=True,timeout=30)
        if r.returncode:raise RuntimeError(r.stdout+r.stderr)
        return binary

    def test_all_existing_preflight_assignment_commit_wait_errors_and_normal_entry_silence(self):
        modes = [0,1,2,3,4,66,*range(10,35),*range(50,55),*range(60,66),68,69,70,*range(100,113),*range(120,147)]
        for binary in (self.binary, self.normal):
            for mode in modes:
                with self.subTest(binary=binary.name,mode=mode):
                    r=subprocess.run([str(binary),str(mode)],capture_output=True,text=True,timeout=5)
                    self.assertEqual(r.returncode,0,r.stdout+r.stderr)

    def test_compiling_missing_early_or_reordered_markers_fail98(self):
        for name,old,new in (
            ('missing', "if (diagnostic) aether_engine_utc_phase('a');", "if (0 && diagnostic) aether_engine_utc_phase('a');"),
            ('early-return', "    aether_engine_utc_phase('f');", "    aether_engine_utc_phase('s');"),
            ('early-commit', "if (diagnostic) aether_engine_utc_phase('c');", "if (diagnostic) aether_engine_utc_phase('d');"),
        ):
            self.assertEqual(self.body.count(old),1)
            binary=self.compile(self.body.replace(old,new,1),name,True)
            r=subprocess.run([str(binary),'0'],capture_output=True,text=True,timeout=5)
            self.assertEqual(r.returncode,98,r.stdout+r.stderr)
            self.assertIn('HOST FIRST WRITE oracle98',r.stderr)

    def test_native_selected_headers_imports_and_local_frames(self):
        output=self.out/'headers';writer.prepare_resource_headers(output)
        receipt=json.loads((writer.CURRENT/'build-attempt-5/results.json').read_text())
        recipe=next(c['argv'] for c in receipt['commands'] if c['name']=='input-176-checked')
        prefix=[writer.route(a) for a in recipe[:recipe.index('-c')]]
        llvm=Path(prefix[0]).parent
        prefix[1:1]=['-I'+str(output/'resources'),'-I'+str(output/'allocation'),'-I'+str(writer.OWNED)]
        prefix += ['-isystem',str(llvm.parent/'lib/clang/21/include')]
        source=self.out/'selected-first.c';source.write_text(first_write_provider((writer.OWNED/'zpl-write.c').read_text()))
        obj=source.with_suffix('.o')
        argv=prefix+['-DAETHER_ZPL_ORDERED_WRITE=1','-std=gnu11','-Wall','-Wextra','-Werror','-fstack-usage','-c',str(source),'-o',str(obj)]
        r=subprocess.run(argv,capture_output=True,text=True,timeout=180)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        symbols=subprocess.check_output([str(llvm/'llvm-nm'),'-u',str(obj)],text=True)
        self.assertIn('aether_engine_utc_phase',symbols);self.assertIn('aether_pool_hooks_bind_transaction',symbols)
        canonical=self.out/'canonical.o'
        ordinary=[str(writer.OWNED/'zpl-write.c') if a==str(source) else str(canonical) if a==str(obj) else a for a in argv]
        r=subprocess.run(ordinary,capture_output=True,text=True,timeout=180)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        baseline=subprocess.check_output([str(llvm/'llvm-nm'),'-u',str(canonical)],text=True)
        self.assertEqual({line.split()[-1] for line in symbols.splitlines()},
                         {line.split()[-1] for line in baseline.splitlines()} | {'aether_engine_utc_phase'})
        stack=obj.with_suffix('.su').read_text();self.assertNotIn('dynamic',stack)
        self.assertTrue(all(int(line.split('\t')[1]) <= 8192 for line in stack.splitlines()))
        print('FIRST WRITE NATIVE '+json.dumps({'argv':argv,'bytes':obj.stat().st_size,'sha256':hashlib.sha256(obj.read_bytes()).hexdigest(),'imports':symbols,'local_frames':stack,'scope':'unlinked native headers, not full-stack/peak or real-media completion'}))


class FirstProbe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base=repeat.RepeatedProbe;base.setUpClass();cls.addClassCleanup(base.doClassCleanups)
        cls.base=base;cls.old=base.driver;cls.addClassCleanup(setattr,base,'driver',cls.old)
        anchor='#include "write-probe.inc"'
        wrapper='''
static unsigned diagnostic_writes;
int aether_zpl_write_diagnostic(aether_zpl_view *v, uint64_t o, uint64_t g,
    uint64_t offset, const void *data, size_t length, uint64_t sec, uint64_t ns,
    aether_zpl_write_result *out)
{
    CHECK(!writes && !diagnostic_writes++);
    return aether_zpl_write(v,o,g,offset,data,length,sec,ns,out);
}
'''
        cls.body='\n'.join(line for line in first_write_probe((writer.OWNED/'zpl-write-probe.c').read_text()).splitlines() if not line.startswith('#include'))+'\n'
        cls.assert_anchor=base.driver.count(anchor)
        base.driver=base.driver.replace(anchor,wrapper+'\n'+anchor,1)
        base.driver=base.driver.replace('CHECK(writes == 2 && reads', 'CHECK(diagnostic_writes == 1); CHECK(writes == 2 && reads',1)
        cls.binary=base.compile(cls.body,'first-probe')

    def test_first_only_selection_and_all391_probe_failures_keep_original_outcomes(self):
        self.assertEqual(self.assert_anchor,1)
        for mode in [0,*range(1,8),*range(9,20),*range(101,492)]:
            r=subprocess.run([str(self.binary),str(mode)],capture_output=True,text=True,timeout=5)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)

    def test_compiling_wrong_first_only_selection_fails96(self):
        old='part ? aether_zpl_write : aether_zpl_write_diagnostic'
        self.assertEqual(self.body.count(old),1)
        binary=self.base.compile(self.body.replace(old,'part ? aether_zpl_write_diagnostic : aether_zpl_write',1),'wrong-selected-call')
        r=subprocess.run([str(binary),'0'],capture_output=True,text=True,timeout=5)
        self.assertEqual(r.returncode,96,r.stdout+r.stderr)
        self.assertIn('HOST ZPL PROBE oracle96',r.stderr)

    def test_derivation_drift_and_duplicate_sources_reject(self):
        for f,name in ((first_write_provider,'zpl-write.c'),(first_write_probe,'zpl-write-probe.c')):
            source=(writer.OWNED/name).read_text()
            for bad in (source+source,source.replace('aether_zpl_write(', 'changed_write(')):
                with self.assertRaises(ValueError):f(bad)


class FirstController(outer.StageController):
    @classmethod
    def setUpClass(cls):
        class Candidate(runtime_tests.PoolNamespaceWriteDriver):
            pool_zpl_stages=True
            pool_zpl_write_stages=True
        Candidate.setUpClass();cls.addClassCleanup(Candidate.doClassCleanups);cls.candidate=Candidate


def success():
    return outer.success().replace(outer.observations(b'BIUVWLPOAMTorhc12vx'+(788).to_bytes(8,'little')+b'SDJFR'),
                                   outer.observations(b'BIUVWLPOAMTeabcdwsf'+(788).to_bytes(8,'little')+b'SDJFR'),1)


def failed_lifetime():
    return ('NATIVE terminal slot=0 generation=1 kind=1 detail=873\n' +
            ''.join(f'NATIVE CLEANUP v=1 slot=0 generation=1 phase={phase} selected={0 if phase == 1 else 2} pages=8192 reclaimed=0\n' for phase in (1,2)) +
            'NATIVE supervisor result=401 reclaimed=0\n')


class FirstDecoding(unittest.TestCase):
    def test_every_success_prefix_and_legal_error_path_is_diagnostic_only(self):
        trace=b'BIUVWLPOAMTeabcdwsf'+(788).to_bytes(8,'little')+b'SDJFR'
        for length in range(1,33):
            r=pair.decode_zpl_stages(outer.observations(trace[:length]),True)
            self.assertFalse(r['qualification']);self.assertEqual(r['primary_rows'],length)
        for path in pair.FIRST_WRITE_PATHS:
            r=pair.decode_zpl_stages(outer.observations(b'BIUVWLPOAMT'+path+b'E'+bytes([6,5,0,0,0])) + failed_lifetime(),True)
            self.assertFalse(r['qualification']);self.assertEqual(r['error_projection'],{'stage':6,'errno':5})
            self.assertEqual(r['last_boundary'],'write-return-after-SA-cleanup')
        r=pair.decode_zpl_stages(outer.observations(b'BIUVWLPOAMTE'+bytes([1,5,0,0,0])),True)
        self.assertFalse(r['qualification'])

    def test_ambiguous_target_E_is_not_an_errno_without_exact_failed_lifetime(self):
        text=outer.observations(b'BIUVWLPOAMTeabcdwsfE'+bytes([6,5,0,0,0]))
        for suffix in ('',failed_lifetime().replace('detail=873','detail=872'),failed_lifetime().replace('phase=2','phase=1')):
            r=pair.decode_zpl_stages(text+suffix,True)
            self.assertIsNone(r['error_projection']);self.assertFalse(r['qualification'])

    def test_wrong_order_foreign_old_profile_and_impossible_error_boundaries_reject(self):
        for bad in (b'BIUVWLPOAMTorhc1', b'BIUVWLPOAMTeaabcd', b'BIUVWLPOAMTeabcdwf',
                    b'BIUVWLPOAMTeaE'+bytes([6,5,0,0,0]),b'BIUVWLPOAMTefE'+bytes([9,5,0,0,0])):
            with self.assertRaises(ValueError):pair.decode_zpl_stages(outer.observations(bad),True)
        with self.assertRaises(ValueError):pair.decode_zpl_stages(outer.observations(b'BIUVWLPOAMTe').replace('slot=0','slot=1'),True)

    def test_full_oracle_and_pair_guards_preserve_reader_admission(self):
        r=runtime.check_zpl_write_trace(success(),True,True)
        self.assertEqual(r['stage_boundaries_observed'],'eabcdwsf');self.assertNotIn('input_xdr_fnv1a64',r)
        fixture=controls.PairControls();fixture.setUp();self.addCleanup(fixture.doCleanups)
        fixture.execute(writer_text=success(),first_write_diagnostic=True)
        self.assertEqual(fixture.launched,['writer','reader'])
        for bad in (outer.observations(b'BIUVWLPOAMTeab'),success().replace('phase=7','phase=6',1),outer.success()):
            with self.assertRaises(ValueError):fixture.execute(writer_text=bad,first_write_diagnostic=True)
            self.assertEqual(fixture.launched,['writer'])
        b=fixture.builds;b['writer'].update(pool_zpl_repeat=True,pool_zpl_stages=True)
        with patch.object(runtime,'sealed'):
            with self.assertRaises(ValueError):pair.verify_prepared(fixture.output,b,True,True,True)
            b['writer']['pool_zpl_write_stages']=True
            pair.verify_prepared(fixture.output,b,True,True,True)
            with self.assertRaises(ValueError):pair.verify_prepared(fixture.output,b,True,True)

    def test_invalid_selection_rejects_before_intake(self):
        import openzfs_elapsed as elapsed
        import openzfs_volume as volume
        with self.assertRaises(ValueError):elapsed.prepare(Path('/absent'),None,volume_pool_zpl_write_stages=True)
        with self.assertRaises(ValueError):volume.build(Path('/absent'),None,None,pool_zpl_write_stages=True)
        with patch.object(runtime,'intake',side_effect=AssertionError('intake')):
            with self.assertRaises(ValueError):runtime.suite(Path('/absent'),_zpl_write_stages=True)
        for flags in (['--first-write-diagnostic'],['--repeated-writes','--stage-diagnostic','--first-write-diagnostic']):
            r=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/zpl_pair.py'),*flags,'--delivery','/absent','--utc-delivery','/absent'],capture_output=True,text=True,timeout=5)
            self.assertEqual(r.returncode,64)
