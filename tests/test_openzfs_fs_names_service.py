# SPDX-License-Identifier: BSD-2-Clause
"""Matched AF05 owner, independently named recovery, actual flags and old intake."""
import ast
import copy
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
import test_openzfs_fs_activation_service as prior
import openzfs_fs_names_service as names
from openzfs_fs_service import intake,recheck
import service_runtime_smoke as runtime
import zpl_pair as pair

ROOT,SOURCE=prior.ROOT,prior.SOURCE
DELIVERY=prior.DELIVERY.with_name('filesystem-service-names-2026-10-20-v1')


class Names(unittest.TestCase):
    def fixture(self,case):
        helper=prior.Activation();f=helper.fixture(case);self.addCleanup(helper.doCleanups)
        selected=intake(DELIVERY,mixed=True,waiting=True,bulk=True,runtime=True,activation=True,names=True)
        b=f.builds['writer'];b['fs_service']=selected
        b['commands'][1]['argv'][1:1]=['--cfg','fs_names']
        b['port']['volume']['namespace_objects'].update({'fs-service-consumer':prior.mixed.sha(selected['object']),
            'mixed-owner-source':prior.prior.sha(names.owner((SOURCE/'fs-service-owner.inc').read_text()))})
        origins=b['port']['fs_service_origins'];origins.pop('aether_fs_activation_run');origins['aether_fs_names_run']='/delivery/filesystem-names.o'
        for role in ('writer','reader'):
            f.builds[role]['fs_service_names']=True
            f.builds[role]['port']['volume']['namespace_objects']['mixed-probe-source']=prior.prior.sha(names.probe(
                (SOURCE/'zpl-mutation-probe.c').read_text(),role=='reader',case in ('lost-reply','partial-request'),case))
        return f

    def verify(self,f,case,**changes):
        options=dict(writer_ticks_6000=True,writer_60s=True,recovery_diagnostic=True,
            filesystem_service=DELIVERY,filesystem_service_case=case,filesystem_service_mixed=True,
            filesystem_service_wait=True,filesystem_service_bulk=True,filesystem_service_runtime=True,
            filesystem_service_activation=True,filesystem_service_names=True);options.update(changes)
        with patch.object(runtime,'sealed'):pair.verify_prepared(f.output,f.builds,**options)

    def test_exact61_candidate_and_unselected_substitutions_fail_closed(self):
        selected=intake(DELIVERY,mixed=True,waiting=True,bulk=True,runtime=True,activation=True,names=True);recheck(selected)
        self.assertEqual(selected['manifest_sha256'],'99cb2e36ad13e108761ca513aed53cc4681ce9b8033aa4663c1faf0aec091e78')
        for d,n in [(DELIVERY,False),(prior.DELIVERY,True)]:
            with self.assertRaises(ValueError):intake(d,mixed=True,waiting=True,bulk=True,runtime=True,activation=True,names=n)
        for key,value in [('names',False),('activation',False),('object',str(prior.DELIVERY/'objects/filesystem-activation.o'))]:
            bad=copy.deepcopy(selected);bad[key]=value
            with self.assertRaises(ValueError):recheck(bad)
        for args in [(True,False,True,False,selected),(False,True,True,False,selected),(True,False,False,True,None)]:
            with self.assertRaises(ValueError):names.validate_profile(*args)

    def test_all_cases_require_names_owner_reader_source_origins_and_actual_cfg(self):
        for case in ('normal','lost-reply','partial-request','close-failure'):
            f=self.fixture(case);self.verify(f,case);original=copy.deepcopy(f.builds)
            for change in ('cfg','reader-cfg','reader-source','writer-source','owner','origin','record','baseline-record'):
                f.builds=copy.deepcopy(original);b=f.builds['writer']
                if change=='cfg':b['commands'][1]['argv'].remove('fs_names')
                if change=='reader-cfg':f.builds['reader']['commands'][1]['argv']+=['--cfg','fs_names']
                if change=='reader-source':f.builds['reader']['port']['volume']['namespace_objects']['mixed-probe-source']='drift'
                if change=='writer-source':b['port']['volume']['namespace_objects']['mixed-probe-source']='drift'
                if change=='owner':b['port']['volume']['namespace_objects']['mixed-owner-source']='drift'
                if change=='origin':b['port']['fs_service_origins']['aether_fs_names_run']='/fake/filesystem-activation.o'
                if change=='record':b['fs_service_names']=False
                if change=='baseline-record':f.builds['baseline']['fs_service_names']=True
                with self.subTest(case=case,change=change),self.assertRaises(ValueError):self.verify(f,case)
            f.builds=original
            with self.assertRaises(ValueError):self.verify(f,case,filesystem_service_names=False)
            mapping='\n'.join('0 0 10 1 '+owner+':(.text)\n0 0 10 1 '+name for name,owner in original['writer']['port']['fs_service_origins'].items())
            if case!='close-failure':self.assertEqual(prior.mixed.partial_origins(mapping,waiting=True,bulk=True,runtime=True,activation=True,names=True),original['writer']['port']['fs_service_origins'])

    def test_actual_emitted_cfg_and_cli_guard_precede_missing_intake(self):
        node=next(n for n in ast.walk(ast.parse(Path(runtime.__file__).read_text())) if isinstance(n,ast.Expr)
            and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='command'
            and 'link-arg=--oformat=binary' in ast.unparse(n))
        f=self.fixture('normal');emitted=[]
        scope={n.id:False for n in ast.walk(node) if isinstance(n,ast.Name) and isinstance(n.ctx,ast.Load)}
        scope.update(command=lambda argv,log:emitted.append(list(map(str,argv))),str=str,volume_readonly=runtime.volume_readonly,
            SOURCE=runtime.SOURCE,name='pool-import',namespace_ipc=True,namespace_wait=True,service_case=0,volume=True,
            engine_native=True,service={'activation':True,'names':True},_zpl_fs_namespace=None,_zpl_fs_runtime=True,
            _zpl_fs_activation=True,_zpl_fs_names=True,_zpl_fs_bulk=True,_zpl_fs_mixed=True,pool_create=True,pool_zpl_write=True,
            WRITE_CASES=runtime.WRITE_CASES,driver_source=f.output/'writer/supervisor.rs',dest=f.output/'writer')
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual names compiler command>','exec'),scope)
        f.builds['writer']['commands'][1]={'argv':emitted[0]};self.verify(f,'normal')
        with self.assertRaisesRegex(ValueError,'names require'):runtime.suite(None,_zpl_fs_names=True)
        with self.assertRaisesRegex(ValueError,'names require'):pair.pair(None,None,filesystem_service_names=True)
        result=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/zpl_pair.py'),'--delivery','/missing',
            '--utc-delivery','/missing','--filesystem-service-names'],capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,64);self.assertIn('names require',result.stderr);self.assertNotIn('[RUNNING]',result.stderr)


if __name__=='__main__':unittest.main()
