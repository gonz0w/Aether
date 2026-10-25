# SPDX-License-Identifier: BSD-2-Clause
"""Private corruption/trace/selector oracles; synthetic geometry is not a ZFS pool."""
from pathlib import Path
import ast
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import service_runtime_smoke as runtime


class RecoveryChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data=bytearray([165])*(67108864+8192)
        cls.offsets=[]
        for start in (0,262144,67108864-524288,67108864-262144):
            for slot in (2,3):
                base=4096+start+131072+slot*1024
                struct.pack_into('<QQQ',data,base,0xBAB10C,5000,slot+4)
                struct.pack_into('<Q',data,base+984,0x210DA7AB10C7A11)
                cls.offsets.append(base+1023)
        cls.seed=bytes(data)

    @staticmethod
    def trace(tags):
        return ''.join(f'NATIVE observation slot=0 generation=1 offset={i*8} byte={byte}\n'
                       for i,byte in enumerate(tags))

    @classmethod
    def rejected(cls):
        return cls.trace(b'BIUVWLP'+bytes(range(1,9))+b'OE\x06\0\0\0')+(
            'NATIVE terminal slot=0 generation=1 kind=1 detail=873\n'
            'NATIVE CLEANUP v=1 slot=0 generation=1 phase=1 selected=0 pages=8192 reclaimed=0\n'
            'NATIVE CLEANUP v=1 slot=0 generation=1 phase=2 selected=2 pages=8192 reclaimed=0\n'
            'NATIVE supervisor result=401 reclaimed=0\nAETHER PANIC: native C profile rejected\n')

    def test_only_populated_checksum_bytes_change(self):
        changed,record=runtime.corrupt_pool_uberblocks(self.seed)
        expected=bytearray(self.seed)
        for offset in self.offsets:expected[offset]^=1
        self.assertEqual(changed,bytes(expected))
        self.assertEqual([row['offset'] for row in record['changes']],self.offsets)
        self.assertEqual([row['txg'] for row in record['changes']],[6,7]*4)
        self.assertEqual({row['label'] for row in record['changes']},{0,1,2,3})
        self.assertNotEqual(record['pre_corruption_sha256'],record['post_corruption_sha256'])

    def test_actual_media_guard_requires_success_stop_and_exact_hash(self):
        node=next(n for n in ast.walk(ast.parse(Path(runtime.__file__).read_text()))
                  if isinstance(n,ast.If) and ast.unparse(n.test)=="name == 'pool-import' and pool_diagnose != 'build' and (not pool_namespace)")
        code=compile(ast.Module(body=[node],type_ignores=[]),'<actual uberblock media guard>','exec')
        with tempfile.TemporaryDirectory(prefix='aether-uberblock-guard-') as directory:
            disk=Path(directory)/'disposable.raw';disk.write_bytes(self.seed)
            prior=dict(name='pool-create',status='pass',vm_run_returned=True,disk_sha256=runtime.sha(disk))
            scope=dict(name='pool-import',pool_diagnose='run',pool_corrupt_labels=False,pool_namespace=False,
                       pool_recovery_check='uberblock-checksum',pool_interrupt=False,pool_uncommitted=False,
                       before_disk=self.seed,block_disk=disk,row={},record={'cases':[prior,{}]},
                       check_pool_import_media=runtime.check_pool_import_media,
                       corrupt_pool_uberblocks=runtime.corrupt_pool_uberblocks)
            for key,value in (('status','failed'),('vm_run_returned',False),('disk_sha256','foreign')):
                scope['record']={'cases':[prior|{key:value},{}]}
                with self.assertRaisesRegex(ValueError,'completed create/VM teardown'):exec(code,scope)
                self.assertEqual(disk.read_bytes(),self.seed)
            scope['record']={'cases':[prior,{}]};exec(code,scope)
            self.assertEqual(runtime.sha(disk),scope['row']['uberblock_corruption']['post_corruption_sha256'])
            self.assertEqual(disk.read_bytes(),scope['before_disk'])

    def test_wrong_geometry_canaries_and_slot_fields_deny_mutation(self):
        for offset,value in ((0,0),(-1,0),(self.offsets[0]-1015,9999),
                             (self.offsets[0]-1007,0),(self.offsets[0]-39,0)):
            data=bytearray(self.seed)
            if offset in (0,-1):data[offset]=value
            else:struct.pack_into('<Q',data,offset,value)
            with self.subTest(offset=offset),self.assertRaises(ValueError):runtime.corrupt_pool_uberblocks(bytes(data))
        with self.assertRaises(ValueError):runtime.corrupt_pool_uberblocks(self.seed[:-1])
        data=bytearray(self.seed)
        for offset in self.offsets[:2]:struct.pack_into('<Q',data,offset-1023,0)
        with self.assertRaises(ValueError):runtime.corrupt_pool_uberblocks(bytes(data))

    def test_original_import_errno_and_partial_cleanup_exact(self):
        serial=self.rejected();result=runtime.check_pool_corrupt_label_trace(serial,True)
        self.assertTrue(result['pool_import_attempted']);self.assertEqual(result['original_import_errno'],6)
        self.assertFalse(result['guest_reclaim_qualified']);self.assertFalse(result['readonly_pool_retired'])
        lines=serial.splitlines()
        for index in range(len(lines)):
            with self.subTest(index=index),self.assertRaises(ValueError):
                runtime.check_pool_corrupt_label_trace('\n'.join(lines[:index]+lines[index+1:]),True)
        for bad in (serial+lines[-1]+'\n',serial.replace('offset=136 byte=6','offset=136 byte=5'),
                    serial.replace('generation=1','generation=2',1),serial.replace('detail=873','detail=0'),
                    serial.replace('reclaimed=0','reclaimed=1',1),serial+'AETHER NATIVE BLOCK PASS\n',
                    serial.replace('offset=160 byte=0','offset=160 byte=256'),serial.replace('phase=2','phase=3')):
            with self.assertRaises(ValueError):runtime.check_pool_corrupt_label_trace(bad,True)
        with self.assertRaises(ValueError):runtime.check_pool_corrupt_label_trace(serial)

    def test_capacity_trace_requires_real_denial_phases(self):
        tags=b'BIUVWP'+bytes(range(1,9))+b'CAT'+(6).to_bytes(8,'little')+b'SQ\x1cDJFR'
        serial=self.trace(tags)+''.join(f'NATIVE observation slot=0 generation={g} offset={i*8} byte={byte}\n'
                                      for g in (2,3) for i,byte in enumerate(b'BNR'))
        result=runtime.check_pool_create_trace(serial,True,True)
        self.assertTrue(result['capacity_denial_baseline_validated']);self.assertEqual(result['original_reservation_errno'],28)
        for bad in (serial.replace('offset=208 byte=81\n',''),
                    serial.replace('offset=216 byte=28','offset=216 byte=5'),serial.replace('byte=81','byte=0')):
            with self.assertRaises(ValueError):runtime.check_pool_create_trace(bad,True,True)
        with self.assertRaises(ValueError):runtime.check_pool_create_trace(serial,True)
        with self.assertRaises(ValueError):runtime.check_pool_create_trace(serial,False,True)

    def test_selectors_fail_before_dependency_intake(self):
        from openzfs_elapsed import prepare
        from openzfs_volume import build
        for selected in ('capacity','uberblock-checksum','unknown'):
            with self.assertRaisesRegex(ValueError,'pool recovery check requires'):
                prepare(Path('/absent'),None,volume_pool_recovery_check=selected)
            with self.assertRaisesRegex(ValueError,'pool recovery check requires'):
                build(Path('/absent'),[],None,pool_recovery_check=selected)
            for extra in ({},dict(pool_data=True,pool_create=True,pool_diagnose='run',case='pool-import',pool_interrupt=True),
                          dict(pool_data=True,pool_create=True,pool_diagnose='run',case='pool-import',pool_corrupt_labels=True)):
                with self.assertRaisesRegex(ValueError,'pool recovery check requires'):
                    runtime.suite(Path('/absent'),pool_recovery_check=selected,**extra)
        r=subprocess.run([sys.executable,runtime.__file__,'--delivery','/absent','--pool-recovery-check','capacity'],capture_output=True,timeout=5)
        self.assertEqual(r.returncode,64);self.assertIn(b'--pool-recovery-check requires',r.stderr)

    def test_actual_original_errno_observer_never_translates(self):
        text=(ROOT/'user/storage/openzfs-volume/spa-import.inc').read_text()
        start=text.index('    if (error) {\n#ifdef AETHER_POOL_BAD_UBERBLOCKS')
        end=text.index("    aether_engine_utc_phase('A');",start)
        body=text[start:end]
        scaffold=r'''
#include <stdint.h>
#include <stdlib.h>
static unsigned count;static unsigned char bytes[5];
void aether_engine_utc_phase(unsigned char byte) { if (count>=5) exit(94);bytes[count++]=byte; }
static int exercise(int error) {
'''
        main=r'''
return 0; }
int main(void) {
    if (exercise(6)!=873 || count!=5 || bytes[0]!='E' || bytes[1]!=6 || bytes[2] || bytes[3] || bytes[4]) return 94;
    count=0;if (exercise(-1)!=873 || count!=5) return 94;
    for (int i=1;i<5;i++) if (bytes[i]!=255) return 94;
    count=0;return exercise(0) || count ? 94:0;
}
'''
        with tempfile.TemporaryDirectory(prefix='aether-import-errno-') as directory:
            source=Path(directory)/'probe.c';binary=Path(directory)/'probe'
            source.write_text('#define AETHER_POOL_BAD_UBERBLOCKS 1\n'+scaffold+body+main)
            r=subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang','-std=c11','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(binary)],capture_output=True,timeout=30)
            self.assertEqual(r.returncode,0,r.stderr)
            r=subprocess.run([str(binary)],capture_output=True,timeout=5)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
