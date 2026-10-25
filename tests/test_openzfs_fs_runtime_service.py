# SPDX-License-Identifier: BSD-2-Clause
"""Explicit checked lifetime intake and fixed nine/96 native admission."""
import copy
import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import test_openzfs_fs_bulk_service as prior
import openzfs_fs_mixed_service as mixed
import openzfs_fs_runtime_service as runtime_service
from openzfs_fs_service import intake,recheck

ROOT,SOURCE=prior.ROOT,prior.SOURCE
DELIVERY=prior.DELIVERY.with_name('filesystem-service-runtime-2026-10-20-v1')
sha=lambda text:hashlib.sha256(text.encode()).hexdigest()


class RuntimeService(unittest.TestCase):
    def fixture(self,case):
        helper=prior.BulkService();f=helper.fixture(case);self.addCleanup(helper.doCleanups)
        b=f.builds['writer'];b['fs_service']=intake(DELIVERY,mixed=True,waiting=True,bulk=True,runtime=True)
        argv=b['commands'][1]['argv'];at=argv.index('fs_bulk')-1;argv[at:at]=['--cfg','fs_runtime']
        for role in ('writer','reader'):
            f.builds[role]['fs_service_runtime']=True
            f.builds[role]['port']['volume']['namespace_objects']['mixed-probe-source']=sha(runtime_service.probe(
                (SOURCE/'zpl-mutation-probe.c').read_text(),role=='reader',case in ('lost-reply','partial-request'),case))
        b['port']['volume']['namespace_objects'].update({'fs-service-consumer':mixed.sha(b['fs_service']['object']),
            'mixed-owner-source':sha(runtime_service.owner((SOURCE/'fs-service-owner.inc').read_text()))})
        origins=b['port']['fs_service_origins'];origins.pop('aether_fs_bulk_run');origins['aether_fs_runtime_run']='/delivery/filesystem-runtime.o'
        return f

    def verify(self,f,case,**changes):
        import zpl_pair as pair
        import service_runtime_smoke as runtime
        options=dict(writer_ticks_6000=True,writer_60s=True,recovery_diagnostic=True,
            filesystem_service=DELIVERY,filesystem_service_case=case,filesystem_service_mixed=True,
            filesystem_service_wait=True,filesystem_service_bulk=True,filesystem_service_runtime=True);options.update(changes)
        with patch.object(runtime,'sealed'):pair.verify_prepared(f.output,f.builds,**options)

    def test_exact55_separate_entry_and_lifetime_scope_cannot_be_substituted(self):
        selected=intake(DELIVERY,mixed=True,waiting=True,bulk=True,runtime=True);recheck(selected)
        self.assertEqual(selected['manifest_sha256'],mixed.RUNTIME_SEAL)
        for old,kw in ((DELIVERY,dict(mixed=True,waiting=True,bulk=True)),(prior.DELIVERY,dict(mixed=True,waiting=True,bulk=True,runtime=True))):
            with self.assertRaises(ValueError):intake(old,**kw)
        for key,value in [('runtime',False),('bulk',False),('object',str(prior.DELIVERY/'objects/filesystem-bulk.o'))]:
            changed=copy.deepcopy(selected);changed[key]=value
            with self.assertRaises(ValueError):recheck(changed)
        for args in [(True,False,None),(False,True,selected)]:
            with self.assertRaises(ValueError):runtime_service.validate_profile(*args)

    def test_all_four_matched_roles_require_runtime_sources_cfg_and_original_origins(self):
        for case in ('normal','lost-reply','partial-request','close-failure'):
            f=self.fixture(case);self.verify(f,case);saved=copy.deepcopy(f.builds)
            for kw in ({'filesystem_service_runtime':False},{'filesystem_service_bulk':False}):
                with self.assertRaises(ValueError):self.verify(f,case,**kw)
            for role in ('writer','reader','baseline'):
                f.builds=copy.deepcopy(saved);f.builds[role]['fs_service_runtime']=role=='baseline'
                with self.assertRaises(ValueError):self.verify(f,case)
            for change in ('cfg','owner','probe','origin'):
                f.builds=copy.deepcopy(saved);b=f.builds['writer']
                if change=='cfg':b['commands'][1]['argv'].remove('fs_runtime')
                if change=='owner':b['port']['volume']['namespace_objects']['mixed-owner-source']='drift'
                if change=='probe':f.builds['reader']['port']['volume']['namespace_objects']['mixed-probe-source']='drift'
                if change=='origin':b['port']['fs_service_origins']['aether_fs_runtime_run']='/fake/filesystem-bulk.o'
                with self.assertRaises(ValueError):self.verify(f,case)
            mapping='\n'.join('0 0 10 1 '+owner+':(.text)\n0 0 10 1 '+name for name,owner in saved['writer']['port']['fs_service_origins'].items())
            if case!='close-failure':self.assertEqual(mixed.partial_origins(mapping,waiting=True,bulk=True,runtime=True),saved['writer']['port']['fs_service_origins'])

    def test_actual_emitted_driver_flags_and_early_layer_guards(self):
        import ast
        import service_runtime_smoke as runtime
        import openzfs_elapsed as elapsed
        import openzfs_volume as volume
        node=next(n for n in ast.walk(ast.parse(Path(runtime.__file__).read_text())) if isinstance(n,ast.Expr)
            and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='command' and 'link-arg=--oformat=binary' in ast.unparse(n))
        for case in ('normal','lost-reply','partial-request','close-failure'):
            f=self.fixture(case);emitted=[]
            scope={n.id:False for n in ast.walk(node) if isinstance(n,ast.Name) and isinstance(n.ctx,ast.Load)}
            scope.update(command=lambda argv,log:emitted.append(list(map(str,argv))),str=str,volume_readonly=runtime.volume_readonly,
                SOURCE=runtime.SOURCE,name='pool-import',namespace_ipc=True,namespace_wait=True,service_case={'normal':0,'lost-reply':1,'partial-request':2,'close-failure':3}[case],
                volume=True,engine_native=True,service={},_zpl_fs_namespace=None,_zpl_fs_runtime=True,_zpl_fs_bulk=True,_zpl_fs_mixed=True,
                pool_create=True,pool_zpl_write=True,WRITE_CASES=runtime.WRITE_CASES,driver_source=f.output/'writer/supervisor.rs',dest=f.output/'writer')
            exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual runtime driver>','exec'),scope)
            f.builds['writer']['commands'][1]={'argv':emitted[0]};self.verify(f,case)
        for function,args,key in ((runtime.suite,(None,),'_zpl_fs_runtime'),(volume.build,(None,None,None),'pool_fs_runtime'),(elapsed.prepare,(None,None),'volume_fs_runtime')):
            with self.assertRaisesRegex(ValueError,'runtime requires'):function(*args,**{key:True})

    def test_strict_original_c_four_writers_two_recovery_states_and_exact_close_arm(self):
        import json
        r=json.loads((ROOT/'docs/evidence/fs-service-namespace-2026-10-19.json').read_text())
        command=r['native_original_c_partial']['commands'][0]['argv'];prefix=command[:command.index('-c')]
        body=runtime_service.owner((SOURCE/'fs-service-owner.inc').read_text())
        self.assertIn('#define FS_REQUESTS 96',body);self.assertIn('#define FS_CLOSES 10',body);self.assertIn('if (fs_injected < 9)',body)
        with tempfile.TemporaryDirectory(prefix='aether-runtime-native-c-') as directory:
            out=Path(directory).resolve();(out/'fs-mixed-owner.inc').write_text(body)
            for reader,empty,case in [(False,c in ('lost-reply','partial-request'),c) for c in ('normal','lost-reply','partial-request','close-failure')]+[(True,e,'normal') for e in (False,True)]:
                p=out/'probe.c';p.write_text(runtime_service.probe((SOURCE/'zpl-mutation-probe.c').read_text(),reader,empty,case))
                result=subprocess.run([*prefix,'-I'+str(DELIVERY/'source'),'-c',str(p),'-o',str(out/'probe.o')],capture_output=True,text=True,timeout=30)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                self.assertIn('offset<8192',p.read_text())
                if not reader:self.assertIn('result.bytes_staged != (FS_MIXED_EMPTY ? 0 : 4096)',p.read_text())


class RuntimeReaderOracle(unittest.TestCase):
    compile=classmethod(prior.BulkReaderOracle.compile.__func__)
    run_mode=prior.BulkReaderOracle.run_mode
    test_every_reachable_reader_api_fault_closes_without_replay=prior.BulkReaderOracle.test_every_reachable_reader_api_fault_closes_without_replay
    test_full8192_empty_metadata_and_last_chunk_corruption=prior.BulkReaderOracle.test_full4096_and_empty_recovery_reject_original_metadata_and_last_chunk_corruption

    @classmethod
    def setUpClass(cls):
        prior.BulkReaderOracle.setUpClass.__func__(cls)
        fixture=(cls.out/'fixture.c').read_text().replace('FS_MIXED_EMPTY ? 0 : 4096','FS_MIXED_EMPTY ? 0 : 8192').replace('off < 4096','off < 8192').replace('off == 4080','off == 8176').replace('(unsigned char)(71+off+i)','(unsigned char)((off<4096 ? 71 : 91)+off+i)')
        (cls.out/'fixture.c').write_text(fixture)
        cls.body='\n'.join(line for line in runtime_service.probe((SOURCE/'zpl-mutation-probe.c').read_text(),True).splitlines() if not line.startswith('#include'))+'\n'
        cls.normal=cls.compile(cls.body,'runtime-normal');cls.empty=cls.compile(cls.body.replace('#define FS_MIXED_EMPTY 0','#define FS_MIXED_EMPTY 1',1),'runtime-empty')

    def test_compiling_missing_second_block_wrong_seed_and_short_read_omissions_fail95(self):
        for name,old,new,mode in (
            ('seed','data[i] != (unsigned char)((offset<4096 ? 71 : 91)+offset+i)','0',30),
            ('span','offset<8192','offset<4096',30),
            ('short-read','got != sizeof(data)','0',31)):
            self.assertEqual(self.body.count(old),1)
            with self.subTest(name=name):self.run_mode(self.compile(self.body.replace(old,new,1),name),mode,expected=95)


if __name__=='__main__':unittest.main()
