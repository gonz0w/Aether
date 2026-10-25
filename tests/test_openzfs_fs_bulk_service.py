# SPDX-License-Identifier: BSD-2-Clause
"""Closed AF04 intake, bounded composition, original native C and role guards."""
import copy
import hashlib
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import test_openzfs_fs_mixed_service as previous
import openzfs_fs_mixed_service as mixed
import openzfs_fs_bulk_service as bulk
from openzfs_fs_bulk import bulk_lifetime_hooks,bulk_lifetime_record
from openzfs_fs_service import intake,recheck

ROOT,SOURCE=previous.ROOT,previous.SOURCE
DELIVERY=previous.WAIT_DELIVERY.with_name('filesystem-service-bulk-2026-10-20-v1')
sha=lambda text:hashlib.sha256(text.encode()).hexdigest()


class BulkService(unittest.TestCase):
    def test_exact49_intake_abi_body_and_length_retirement_closure(self):
        selected=intake(DELIVERY,mixed=True,waiting=True,bulk=True);recheck(selected)
        self.assertTrue(selected['bulk']);self.assertEqual(selected['manifest_sha256'],mixed.BULK_SEAL)
        for options in ({},{'mixed':True},{'mixed':True,'waiting':True},{'bulk':True}):
            with self.assertRaises(ValueError):intake(DELIVERY,**options)
        for old,options in ((previous.DELIVERY,{'mixed':True}),
                            (previous.WAIT_DELIVERY,{'mixed':True,'waiting':True})):
            recheck(intake(old,**options))
            with self.assertRaises(ValueError):intake(old,mixed=True,waiting=True,bulk=True)
        for field,value in [('bulk',False),('waiting',False),('object',str(previous.WAIT_DELIVERY/'objects/filesystem-mixed-wait.o'))]:
            changed=copy.deepcopy(selected);changed[field]=value
            with self.assertRaises(ValueError):recheck(changed)
        with tempfile.TemporaryDirectory(prefix='aether-bulk-intake-') as directory:
            root=Path(directory).resolve()/'delivery';shutil.copytree(DELIVERY,root)
            p=root/'source/bulk-service.rs';data=p.read_bytes();p.write_bytes(data+b' ')
            with self.assertRaisesRegex(ValueError,'member identity'):intake(root,mixed=True,waiting=True,bulk=True)
            p.write_bytes(data);(root/'extra').write_text('x')
            with self.assertRaisesRegex(ValueError,'closure'):intake(root,mixed=True,waiting=True,bulk=True)

    def test_strict_original_c_all_four_writers_two_recovery_states(self):
        import json
        r=json.loads((ROOT/'docs/evidence/fs-service-namespace-2026-10-19.json').read_text())
        command=r['native_original_c_partial']['commands'][0]['argv'];prefix=command[:command.index('-c')]
        with tempfile.TemporaryDirectory(prefix='aether-bulk-native-c-') as directory:
            out=Path(directory).resolve();(out/'fs-mixed-owner.inc').write_text(bulk.owner((SOURCE/'fs-service-owner.inc').read_text()))
            for reader,empty,case in [(False,c in ('lost-reply','partial-request'),c) for c in ('normal','lost-reply','partial-request','close-failure')]+[(True,e,'normal') for e in (False,True)]:
                p=out/'probe.c';p.write_text(bulk.probe((SOURCE/'zpl-mutation-probe.c').read_text(),reader,empty,case))
                result=subprocess.run([*prefix,'-I'+str(DELIVERY/'source'),'-c',str(p),'-o',str(out/'probe.o')],capture_output=True,text=True,timeout=30)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                self.assertIn('offset<4096',p.read_text())
        with self.assertRaises(ValueError):bulk.owner((SOURCE/'fs-service-owner.inc').read_text(),False)
        with self.assertRaises(ValueError):bulk.probe((SOURCE/'zpl-mutation-probe.c').read_text(),False,False,'partial-request')

    def fixture(self,case):
        helper=previous.MixedPairAdmission();f=helper.fixture(case,True);self.addCleanup(helper.doCleanups)
        b=f.builds['writer'];b['fs_service']=intake(DELIVERY,mixed=True,waiting=True,bulk=True)
        argv=b['commands'][1]['argv'];at=argv.index('fs_mixed')-1;argv[at:at]=['--cfg','fs_bulk']
        for role in ('writer','reader'):
            build=f.builds[role];build['fs_service_bulk']=True
            build['fs_service_mixed_empty']=role=='reader' and case in ('lost-reply','partial-request')
            build['port']['volume']['namespace_objects']['mixed-probe-source']=sha(bulk.probe(
                (SOURCE/'zpl-mutation-probe.c').read_text(),role=='reader',case in ('lost-reply','partial-request'),case))
        b['port']['volume']['namespace_objects'].update({
            'fs-service-consumer':mixed.sha(b['fs_service']['object']),
            'mixed-owner-source':sha(bulk.owner((SOURCE/'fs-service-owner.inc').read_text())),
            'mixed-hooks-source':sha(bulk_lifetime_hooks((SOURCE/'pool-vdev-hooks.inc').read_text())),
            'mixed-record-source':sha(bulk_lifetime_record((SOURCE/'pool-lifetime.inc').read_text()))})
        origins=b['port']['fs_service_origins'];origins.pop('aether_fs_mixed_wait_run');origins.pop('aether_pool_service16_retire')
        origins.update(aether_fs_bulk_run='/delivery/filesystem-bulk.o',aether_pool_service_bytes_retire='/build/vdev-selected.o')
        return f

    def verify(self,f,case,**changes):
        import zpl_pair as pair
        import service_runtime_smoke as runtime
        options=dict(writer_ticks_6000=True,writer_60s=True,recovery_diagnostic=True,
            filesystem_service=DELIVERY,filesystem_service_case=case,filesystem_service_mixed=True,
            filesystem_service_wait=True,filesystem_service_bulk=True);options.update(changes)
        with patch.object(runtime,'sealed'):pair.verify_prepared(f.output,f.builds,**options)

    def test_all_roles_require_matching_bulk_cfg_object_original_c_and_independent_empty_reader(self):
        for case in ('normal','lost-reply','partial-request','close-failure'):
            f=self.fixture(case);self.verify(f,case);saved=copy.deepcopy(f.builds)
            for key in ('filesystem_service_bulk','filesystem_service_wait','filesystem_service_mixed'):
                with self.assertRaises(ValueError):self.verify(f,case,**{key:False})
            for change in ('writer','baseline','reader','cfg','origin','record','probe'):
                f.builds=copy.deepcopy(saved);b=f.builds['writer']
                if change in ('writer','baseline'):f.builds[change]['fs_service_bulk']=change=='baseline'
                if change=='reader':f.builds['reader']['fs_service_mixed_empty']=not saved['reader']['fs_service_mixed_empty']
                if change=='cfg':b['commands'][1]['argv'].remove('fs_bulk')
                if change=='origin':b['port']['fs_service_origins']['aether_pool_service_bytes_retire']='/fake.o'
                if change=='record':b['port']['volume']['namespace_objects']['mixed-record-source']='drift'
                if change=='probe':f.builds['reader']['port']['volume']['namespace_objects']['mixed-probe-source']='drift'
                with self.assertRaises(ValueError):self.verify(f,case)

    def test_exact_partial_origins_and_early_profile_rejections(self):
        f=self.fixture('normal');origins=f.builds['writer']['port']['fs_service_origins']
        mapping='\n'.join('0 0 10 1 '+owner+':(.text)\n0 0 10 1 '+name for name,owner in origins.items())
        self.assertEqual(mixed.partial_origins(mapping,waiting=True,bulk=True),origins)
        for name in origins:
            with self.assertRaises(ValueError):mixed.partial_origins(mapping.replace('1 '+name+'\n','1 missing\n') if not mapping.endswith('1 '+name) else mapping+'\n0 0 10 1 '+name,waiting=True,bulk=True)
        selected=intake(DELIVERY,mixed=True,waiting=True,bulk=True)
        for args in [(False,True,True,True,False,selected),(True,False,True,True,False,selected),
                     (True,True,False,True,False,selected),(True,True,True,False,True,selected)]:
            with self.assertRaises(ValueError):bulk.validate_profile(*args)


if __name__=='__main__':unittest.main()


class BulkReaderOracle(unittest.TestCase):
    compile=classmethod(previous.MixedReaderOracle.compile.__func__)
    run_mode=previous.MixedReaderOracle.run_mode
    test_every_reachable_reader_api_fault_closes_without_replay=previous.MixedReaderOracle.test_every_reachable_reader_api_fault_closes_without_replay

    @classmethod
    def setUpClass(cls):
        previous.MixedReaderOracle.setUpClass.__func__(cls)
        fixture=(cls.out/'fixture.c').read_text().replace('FS_MIXED_EMPTY ? 0 : 16','FS_MIXED_EMPTY ? 0 : 4096')
        old='        if (!FS_MIXED_EMPTY && off == 0 && length == 16) {\n            *count = mode == 25 ? 15 : 16;\n            for (unsigned i=0;i<16;++i) ((unsigned char*)buf)[i]=71+i;\n            if (mode == 24) ((unsigned char*)buf)[0]^=1;\n'
        new='        if (!FS_MIXED_EMPTY && off < 4096 && !(off % 16) && length == 16) {\n            *count = (mode == 25 || (mode == 31 && off == 4080)) ? 15 : 16;\n            for (unsigned i=0;i<16;++i) ((unsigned char*)buf)[i]=(unsigned char)(71+off+i);\n            if (mode == 24 || (mode == 30 && off == 4080)) ((unsigned char*)buf)[15]^=1;\n'
        assert fixture.count(old)==1;fixture=fixture.replace(old,new,1)
        (cls.out/'fixture.c').write_text(fixture)
        cls.body='\n'.join(line for line in bulk.probe((SOURCE/'zpl-mutation-probe.c').read_text(),True).splitlines() if not line.startswith('#include'))+'\n'
        cls.normal=cls.compile(cls.body,'bulk-normal')
        cls.empty=cls.compile(cls.body.replace('#define FS_MIXED_EMPTY 0','#define FS_MIXED_EMPTY 1',1),'bulk-empty')

    def test_full4096_and_empty_recovery_reject_original_metadata_and_last_chunk_corruption(self):
        for binary in (self.normal,self.empty):
            self.run_mode(binary,0)
            for mode in [*range(1,20),27,28,29]:self.run_mode(binary,mode)
        for mode in (24,25,30,31):self.run_mode(self.normal,mode)

    def test_compiling_content_full_span_and_short_read_omissions_fail95(self):
        for name,old,new,mode in (
            ('content','data[i] != (unsigned char)(71+offset+i)','0',30),
            ('span','offset<4096','offset<16',30),
            ('short-read','got != sizeof(data)','0',31)):
            self.assertEqual(self.body.count(old),1)
            with self.subTest(name=name):self.run_mode(self.compile(self.body.replace(old,new,1),name),mode,expected=95)

    def test_actual_namespace_origin_branch_retains_the_three_argument_legacy_abi(self):
        import ast
        import openzfs_elapsed as elapsed
        node=next(n for n in ast.walk(ast.parse(Path(elapsed.__file__).read_text())) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='namespace_origins')
        self.assertEqual(len(node.args),3)
        from openzfs_fs_namespace import partial_origins
        # Execute the actual emitted argument expression with the original typed
        # callable; no bulk/wait selector may leak into the legacy namespace ABI.
        with tempfile.TemporaryDirectory(prefix='aether-namespace-origin-') as directory:
            output=Path(directory);(output/'bridge-partial.map').write_text('')
            with self.assertRaises(ValueError):
                eval(compile(ast.Expression(node),'<actual namespace origins>','eval'),dict(namespace_origins=partial_origins,output=output,close_symbols=None,service_case=0))
