# SPDX-License-Identifier: BSD-2-Clause
"""Exported-file admission and actual failed-peer/oracle counterexamples."""
import copy
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import fs_init_checks as checks
import native_smoke
import fs_session
from fs_session import machine_witness
from fs_init_consumer import trace as activation_trace
from test_fs_init_consumer import trace as activation_text


def failure_text(selection):
    index = checks.FAILURES.index(selection)
    lines = ['NATIVE MEMORY admitted slot=0 generation=1 used=21 remaining=8171']
    if index >= 2:
        lines += ['NATIVE MEMORY admitted slot=1 generation=1 used=21 remaining=107',
                  'NATIVE terminal slot=1 generation=1 kind=1 detail=0']
        lines += [f'NATIVE CLEANUP v=1 slot=1 generation=1 phase={p} selected={1 if p==1 else 6} pages=128 reclaimed={int(p==7)}' for p in range(1, 8)]
    lines += [f'NATIVE observation slot=0 generation=1 offset=0 byte={checks.TAGS[index]}']
    if index in (0, 3):
        lines += [f'NATIVE terminal slot=0 generation=1 kind=1 detail={71 if index==0 else 72}']
        lines += [f'NATIVE CLEANUP v=1 slot=0 generation=1 phase={p} selected={0 if p==1 else 6} pages=8192 reclaimed={int(index==3)}' for p in (1,2)]
    return '\n'.join([*lines, 'NATIVE fault vector=6 rip=400018 error=0',
                      'AETHER PANIC: native supervisor terminated'])+'\n'


class Recovery(unittest.TestCase):
    def test_actual_campaign_cleanup_captures_early_records_and_broken_selection_rejects(self):
        text = activation_text()+('firmware chatter\n'*600)
        with tempfile.TemporaryDirectory(prefix=fs_session.PREFIX,dir=ROOT/'zig-out') as folder:
            output = Path(folder);(output/'baseline').mkdir()
            (output/'baseline/native-serial.log').write_text(text)
            with patch.object(fs_session.tempfile,'mkdtemp',return_value=folder), \
                 patch.object(fs_session,'intake',side_effect=ValueError('CONTROL_PREPARATION_STOP')), \
                 patch.object(fs_session,'run') as guest:
                with self.assertRaisesRegex(ValueError,'CONTROL_PREPARATION_STOP'):
                    fs_session.campaign()
                guest.assert_not_called()
            result = json.loads((output/'results.json').read_text())
            self.assertEqual(result['status'],'failed')
            self.assertFalse(result['native_attempted'])
            capture = result['serial']['baseline']
            self.assertEqual(capture['tail'],text[-6000:])
            self.assertEqual(capture['sha256'],hashlib.sha256(text.encode()).hexdigest())
            self.assertNotIn('NATIVE MEMORY',capture['tail'])
            self.assertTrue(capture['machine_witness']['selection_complete'])
            activation_trace('\n'.join(capture['machine_witness']['lines'])+'\n')
            self.assertEqual(list(p.name for p in output.iterdir()),['results.json'])
        source = inspect.getsource(machine_witness)
        self.assertEqual(source.count('selected.append(line)'),1)
        broken = source.replace('selected.append(line)',
            "selected.append(line) if not line.startswith('NATIVE MEMORY ') else None")
        scope = {'hashlib':hashlib}
        exec(compile(broken,'<omitted-admission-retention>','exec'),scope)
        witness = scope['machine_witness'](activation_text())
        with self.assertRaisesRegex(ValueError,'actual loader count'):
            activation_trace('\n'.join(witness['lines'])+'\n')

    def test_machine_selection_keeps_early_records_without_firmware_and_mem_chatter(self):
        rows = ['AETHER M1: entered x86_64 kernel', 'AETHER M1 PASS',
                *failure_text('startup-exit').splitlines()]
        text = '\x1b[2Jfirmware\nMEM base=0x0 length=0xa0000 type=0\n'+ '\n'.join(rows)+'\n'
        witness = machine_witness(text)
        self.assertEqual(witness['lines'],rows)
        self.assertTrue(witness['selection_complete'])
        selected = ('\n'.join(rows)+'\n').encode()
        self.assertEqual(witness['full_selection_sha256'],hashlib.sha256(selected).hexdigest())
        self.assertEqual(witness['retained_utf8_bytes'],len(selected))
        # Only these actual required predicates can interpret the records;
        # retaining them does not convert an expected panic to successful halt.
        checks.failure_trace('\n'.join(witness['lines'])+'\n','startup-exit',21)
        self.assertNotIn('status',witness)

    def test_machine_selection_fixed_utf8_bound_hashes_omitted_records_and_empty_is_not_pass(self):
        rows = ['NATIVE '+('x'*248)+'é']*300
        text = '\n'.join(rows)+'\n'
        witness = machine_witness(text)
        self.assertFalse(witness['selection_complete'])
        self.assertEqual(witness['total_lines'],300)
        self.assertLessEqual(witness['retained_utf8_bytes'],65536)
        self.assertEqual(witness['full_selection_sha256'],hashlib.sha256(text.encode()).hexdigest())
        self.assertEqual(witness['retained_utf8_bytes'],len(('\n'.join(witness['lines'])+'\n').encode()))
        self.assertTrue(machine_witness('NATIVE '+('x'*65528)+'\n')['selection_complete'])
        self.assertFalse(machine_witness('NATIVE '+('x'*65529)+'\n')['selection_complete'])
        empty = machine_witness('firmware\nMEM ignored\n')
        self.assertEqual(empty['lines'],[])
        self.assertEqual(empty['total_lines'],0)
        with self.assertRaises(ValueError): checks.failure_trace('\n'.join(empty['lines']),'startup-exit',21)

    def test_label_derivation_changes_only_exported_txg_guard_and_include(self):
        volume = ROOT/'user/storage/openzfs-volume'
        original = (volume/'namespace-label.inc').read_text()
        selected = checks.labels(original)
        self.assertEqual(selected.replace('txg < 782', 'txg != 782'), original)
        with self.assertRaises(ValueError): checks.labels(original.replace('txg != 782', 'txg != 783'))
        source = (volume/'pool-label.c').read_text()
        self.assertEqual(checks.label_source(source).replace('readonly-exported-label.inc', 'namespace-label.inc'), source)
        with self.assertRaises(ValueError): checks.label_source(source+source)

    def test_exact_clean_stopped_actual_activation_required_before_media_inspection(self):
        writer = dict(activation_trace(activation_text()), status='pass', vm_run_returned=True, disk_sha256='a'*64)
        with patch('openzfs_namespace._native_media_snapshot', return_value={'sha256':'a'*64}) as snapshot:
            self.assertEqual(checks.recovery_media(writer, Path('/unused')), {'sha256':'a'*64})
            snapshot.assert_called_once()
        for key in ('profile','status','admitted_instances','reclaimed','final_live_workers',
                    'cleanup_trace_version','cleanup_boundaries_per_instance','vm_run_returned',
                    'read_only_activation','engine_terminal_zero','selected_process_terminal_zero',
                    'source_bound_readiness_and_shutdown','disk_sha256'):
            row = copy.deepcopy(writer); row.pop(key)
            with self.subTest(key=key), patch('openzfs_namespace._native_media_snapshot') as snapshot:
                with self.assertRaisesRegex(ValueError, 'clean stopped'): checks.recovery_media(row, Path('/unused'))
                snapshot.assert_not_called()
        with patch('openzfs_namespace._native_media_snapshot', return_value={'sha256':'b'*64}):
            with self.assertRaisesRegex(ValueError, 'exact stopped media'): checks.recovery_media(writer, Path('/unused'))

    def test_reader_selector_rejects_conflicts_before_dependency_or_guest(self):
        image = ROOT/'zig-out/thread-suite-service-runtime-zpl-pair-fs-session-test/reader/aether.iso'
        options = dict(_fs_init_writer={}, _pair_stop=True, block_namespace=True, block_large=True,
                       block_disk=image.parent.parent/'native-namespace.raw', marker=b'AETHER NATIVE BLOCK PASS')
        changes = ({'_pair_stop':False},{'_fs_session_writer':{}},{'zpl_writer':{}},
                   {'_zpl_writer_60s':True},{'_zpl_mutation_seed':True},{'_monitor_diagnostic':True},
                   {'_storage_lifetime':True},{'expected_panic':b'x'},{'panic_context':('x',)},
                   {'block_large':False},{'block_namespace':False},{'block_disk':None},{'marker':b'other'})
        with patch.object(native_smoke, 'verify') as verify:
            for change in changes:
                with self.subTest(change=change), self.assertRaisesRegex(ValueError, 'init recovery'):
                    native_smoke.run(image, **(options|change))
            with self.assertRaisesRegex(ValueError, 'init recovery'):
                native_smoke.run(image.parent.parent/'writer/aether.iso', **options)
            verify.assert_not_called()

    def test_cli_separate_selector_and_error_streams(self):
        for other in ('--sys-init','--controller-16k'):
            result = subprocess.run([sys.executable,'-B',ROOT/'scripts/fs_session.py','--sys-init-checks',other], capture_output=True,text=True,timeout=5)
            self.assertEqual(result.returncode,64); self.assertEqual(result.stdout,'')
            self.assertNotIn('[RUNNING]',result.stderr)
        result = subprocess.run([sys.executable,'-B',ROOT/'scripts/fs_session.py','--help'],capture_output=True,text=True,timeout=5)
        self.assertEqual(result.returncode,0); self.assertEqual(result.stderr,'')
        self.assertIn('--sys-init-checks',result.stdout)

    def test_each_native_failure_needs_exact_roles_stage_stop_and_no_replay(self):
        for selection in checks.FAILURES:
            text = failure_text(selection)
            result = checks.failure_trace(text,selection,21)
            self.assertTrue(result['actual_owner_fail_stop'])
            self.assertFalse(result['engine_reclaimed'])
            for line in text.splitlines():
                for changed in (text.replace(line+'\n','',1),text+line+'\n'):
                    with self.subTest(selection=selection,line=line), self.assertRaises(ValueError):
                        checks.failure_trace(changed,selection,21)
            for extra in ('NATIVE init halted ticks=50 idle=0 reclaimed=2',
                          'AETHER NATIVE BLOCK PASS', 'NATIVE supervisor result=100 reclaimed=2'):
                with self.assertRaisesRegex(ValueError, 'successfully halt'):
                    checks.failure_trace(text+extra+'\n',selection,21)
            for old,new in (('vector=6','vector=14'),('rip=400018','rip=500018'),
                            ('used=21 remaining=8171','used=22 remaining=8170'),
                            ('offset=0 byte=','offset=8 byte=')):
                with self.assertRaises(ValueError): checks.failure_trace(text.replace(old,new),selection,21)
        text = failure_text('failed-exit')
        for old,new in (('detail=72','detail=0'),('kind=1 detail=72','kind=2 detail=72'),('pages=128','pages=8192')):
            with self.assertRaises(ValueError): checks.failure_trace(text.replace(old,new),'failed-exit',21)
        marker = 'NATIVE observation slot=0 generation=1 offset=0 byte=70\n'
        with self.assertRaisesRegex(ValueError,'order'):
            checks.failure_trace(marker+text.replace(marker,''),'failed-exit',21)

    def test_actual_startup_exit_regression_stops_contexts_without_reclaiming_engine(self):
        text = (ROOT/'tests/fixtures/fs-init-startup-exit.log').read_text()
        row = checks.failure_trace(text,'startup-exit',20)
        self.assertEqual(row['engine_terminal_stop_boundaries'],2)
        self.assertFalse(row['engine_reclaimed'])
        for phase in range(3,8):
            line = f'NATIVE CLEANUP v=1 slot=0 generation=1 phase={phase} selected=6 pages=8192 reclaimed={int(phase==7)}\n'
            with self.assertRaisesRegex(ValueError,'stop/reclaim'):
                checks.failure_trace(text.replace('NATIVE fault ',line+'NATIVE fault '),'startup-exit',20)
        # Completion and the kernel's two automatic stop phases are independently
        # required. A context-stop observation can never stand in for reclaim.
        with self.assertRaises(ValueError):
            checks.failure_trace(text.replace('phase=2 selected=6','phase=3 selected=6'),'startup-exit',20)

    def test_actual_readonly_controller_fits_original_one_page_linker(self):
        with tempfile.TemporaryDirectory(prefix='aether-init-readback-') as folder:
            raw = Path(folder)/'reader.raw'
            run = subprocess.run(['rustc','+1.98.0','--edition=2024','--target=x86_64-unknown-none',
                '-Dwarnings','-Copt-level=2','-Cpanic=abort','-Crelocation-model=static',
                '-Clink-arg=-Tuser/protection/linker.ld','-Clink-arg=--oformat=binary',
                ROOT/'user/storage/session/readback.rs','-o',raw],cwd=ROOT,capture_output=True,text=True,timeout=30)
            self.assertEqual(run.returncode,0,run.stderr)
            self.assertLessEqual(raw.stat().st_size,4096)

    def test_actual_peer_frames_with_partial_io_eagain_and_compiling_omission(self):
        source = (ROOT/'user/storage/session/failed-peer.c').read_text()
        start = source.index('static long trap('); end = source.index('static void witness(',start)
        # Only replace the hardware boundary and platform headers in the host
        # copy. The actual frame/lifetime/validation branches execute unchanged.
        source = source[:start]+source[end:]
        source = source.replace('#include <sys/auxv.h>','').replace('int main(void)','int peer_main(void)')
        harness = r'''
#include <assert.h>
#include <setjmp.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
static jmp_buf stopped;
static unsigned count, seen, sent, received, yielded, ready, closed;
static unsigned char frames[128];
static _Noreturn void stop(int code) { longjmp(stopped,code); }
#define _Exit stop
static unsigned long getauxval(unsigned long key) { return key==0xa004?11:key==0xa005?12:0; }
static long trap(long op,long a,long b,long c,long d) {
 assert(!d);
 if(op==0x10001) { assert(a==1 && c==8 && !seen); seen=*(uint64_t*)b; return 8; }
 if(op==0x20004) { assert(!a&&!b&&!c&&!ready); ready=1;return 0; }
 if(op==0x24003) { assert(a==12&&!b&&!c&&!closed); closed=1;return 0; }
 if(op==0x1fffe) {
   if(yielded) { yielded=0;return 0; }
   assert(seen && (FAILURE==1?sent==64:FAILURE==2?sent==128:FAILURE==4?closed:0));
   stop(200);
 }
 assert(op==0x24001 || op==0x24002);
 assert(ready && c>0 && c<=16);
 if(++count%3==0) { yielded=1;return -11; }
 unsigned n=c>7?7:c;
 if(op==0x24002) { assert(a==12 && sent+n<=128); memcpy(frames+sent,(void*)b,n);sent+=n; }
 else {
   uint64_t request[8]={0};memcpy(request,"AFSRPC06",8);request[1]=4;request[2]=11;
   assert(a==11 && received+n<=64);memcpy((void*)b,(unsigned char*)request+received,n);received+=n;
 }
 return n;
}
'''
        ending = r'''
int main(void) {
 int status=setjmp(stopped); if(!status) status=peer_main();
 assert(status==(FAILURE==0?71:FAILURE==3?72:200));
 assert(seen==(unsigned char)"SGDFL"[FAILURE]);
 assert(ready==(FAILURE!=0));
 if(FAILURE==0) { assert(!sent&&!received&&!closed);return 0; }
 uint64_t first[8];memcpy(first,frames,64);
 assert(!memcmp(first,FAILURE==1?"AFSRPC05":"AFSRPC06",8));
 assert(!first[1]&&first[2]==11&&first[3]==1&&first[4]==1&&!first[5]&&!first[6]&&!first[7]);
 assert(received==(FAILURE>=2?64:0));
 assert(sent==(FAILURE==2||FAILURE==3?128:64));
 assert(closed==(FAILURE==4));
 if(FAILURE==2||FAILURE==3) {
   uint64_t last[8];memcpy(last,frames+64,64);
   assert(!memcmp(last,"AFSRPC06",8)&&!last[1]&&last[2]==(FAILURE==2?12:11));
   for(unsigned i=3;i<8;i++)assert(!last[i]);
 }
 return 0;
}
'''
        with tempfile.TemporaryDirectory(prefix='aether-init-peer-') as folder:
            out = Path(folder)
            for mode in range(5):
                for omitted in (False,True) if mode==2 else (False,):
                    body = source.replace('reply[2] = reader + 1;','reply[2] = reader;') if omitted else source
                    c = out/'peer.c'; exe = out/'peer'
                    c.write_text(harness+body+ending)
                    run = subprocess.run(['clang','-std=c11','-O2','-Wall','-Wextra','-Werror','-DFAILURE='+str(mode),c,'-o',exe],capture_output=True,text=True,timeout=30)
                    self.assertEqual(run.returncode,0,run.stderr)
                    run = subprocess.run([exe],capture_output=True,text=True,timeout=5)
                    self.assertEqual(run.returncode==0,not omitted,run.stderr)


if __name__=='__main__': unittest.main()
