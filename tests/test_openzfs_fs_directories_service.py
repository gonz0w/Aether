# SPDX-License-Identifier: BSD-2-Clause
"""Exact delegated directory intake, owned origins, independent oracle and flags."""
import ast
import copy
from pathlib import Path
import unittest
from unittest.mock import patch

import test_openzfs_fs_names_service as prior
import openzfs_fs_directories_service as dirs
from openzfs_fs_service import intake,recheck
import service_runtime_smoke as runtime
import zpl_pair as pair

ROOT,SOURCE=prior.ROOT,prior.SOURCE
DELIVERY=prior.DELIVERY.with_name('filesystem-service-directories-2026-10-20-v1')


class Directories(unittest.TestCase):
    def fixture(self,case):
        helper=prior.Names();f=helper.fixture(case);self.addCleanup(helper.doCleanups)
        selected=intake(DELIVERY,mixed=True,waiting=True,bulk=True,runtime=True,activation=True,names=True,directories=True)
        b=f.builds['writer'];b['fs_service']=selected
        b['commands'][1]['argv'][1:1]=['--cfg','fs_directories']
        b['port']['volume']['namespace_objects'].update({'fs-service-consumer':prior.prior.mixed.sha(selected['object']),
            'mixed-owner-source':prior.prior.prior.sha(dirs.owner((SOURCE/'fs-service-owner.inc').read_text()))})
        origins=b['port']['fs_service_origins'];origins.pop('aether_fs_names_run');origins['aether_fs_directories_run']='/delivery/filesystem-directories.o'
        for n in ('aether_zpl_directory','aether_zpl_mkdir','aether_zpl_rmdir'):origins[n]='/private/zpl-mutation.o'
        for role in ('writer','reader'):
            f.builds[role]['fs_service_directories']=True
            f.builds[role]['port']['volume']['namespace_objects']['mixed-probe-source']=prior.prior.prior.sha(dirs.probe(
                (SOURCE/'zpl-mutation-probe.c').read_text(),role=='reader',case in ('lost-reply','partial-request'),case))
        return f

    def verify(self,f,case,**changes):
        options=dict(writer_ticks_6000=True,writer_60s=True,recovery_diagnostic=True,
            filesystem_service=DELIVERY,filesystem_service_case=case,filesystem_service_mixed=True,
            filesystem_service_wait=True,filesystem_service_bulk=True,filesystem_service_runtime=True,
            filesystem_service_activation=True,filesystem_service_names=True,filesystem_service_directories=True)
        options.update(changes)
        with patch.object(runtime,'sealed'):pair.verify_prepared(f.output,f.builds,**options)

    def test_exact67_intake_and_role_substitutions_fail_closed(self):
        selected=intake(DELIVERY,mixed=True,waiting=True,bulk=True,runtime=True,activation=True,names=True,directories=True);recheck(selected)
        self.assertEqual(selected['manifest_sha256'],'e01e269a91a96bac3a428fb1197dc862032838dcb94602c0c6042ef9e8e5c4fa')
        for d,flag in [(DELIVERY,False),(prior.DELIVERY,True)]:
            with self.assertRaises(ValueError):intake(d,mixed=True,waiting=True,bulk=True,runtime=True,activation=True,names=True,directories=flag)
        for key,value in [('directories',False),('names',False),('object',str(prior.DELIVERY/'objects/filesystem-names.o'))]:
            bad=copy.deepcopy(selected);bad[key]=value
            with self.assertRaises(ValueError):recheck(bad)
        for options in [(True,False,False,selected),(True,True,False,None),(False,True,False,selected),(True,True,True,selected)]:
            with self.assertRaises(ValueError):dirs.validate_profile(*options)

    def test_all_roles_require_actual_entry_cfg_directory_origins_and_independent_source(self):
        for case in ('normal','lost-reply','partial-request','close-failure'):
            f=self.fixture(case);self.verify(f,case);original=copy.deepcopy(f.builds)
            for change in ('cfg','reader-cfg','reader-source','writer-source','owner','entry','mkdir','rmdir','refresh','record','baseline'):
                f.builds=copy.deepcopy(original);b=f.builds['writer']
                if change=='cfg':b['commands'][1]['argv'].remove('fs_directories')
                elif change=='reader-cfg':f.builds['reader']['commands'][1]['argv']+=['--cfg','fs_directories']
                elif change=='reader-source':f.builds['reader']['port']['volume']['namespace_objects']['mixed-probe-source']='drift'
                elif change=='writer-source':b['port']['volume']['namespace_objects']['mixed-probe-source']='drift'
                elif change=='owner':b['port']['volume']['namespace_objects']['mixed-owner-source']='drift'
                elif change in ('entry','mkdir','rmdir','refresh'):
                    name={'entry':'aether_fs_directories_run','mkdir':'aether_zpl_mkdir','rmdir':'aether_zpl_rmdir','refresh':'aether_zpl_directory'}[change]
                    b['port']['fs_service_origins'][name]='/forged/wrong.o'
                elif change=='record':b['fs_service_directories']=False
                else:f.builds['baseline']['fs_service_directories']=True
                with self.subTest(case=case,change=change),self.assertRaises(ValueError):self.verify(f,case)
            f.builds=original
            mapping='\n'.join('0 0 10 1 '+owner+':(.text)\n0 0 10 1 '+name for name,owner in original['writer']['port']['fs_service_origins'].items())
            if case!='close-failure':self.assertEqual(prior.prior.mixed.partial_origins(mapping,waiting=True,bulk=True,runtime=True,activation=True,names=True,directories=True),original['writer']['port']['fs_service_origins'])

    def test_actual_engine_binding_requirements_distinguish_writer_from_reader(self):
        import inspect
        node=ast.parse(inspect.getsource(runtime.check_engine_bindings)).body[0]
        stop=next(i for i,n in enumerate(node.body) if isinstance(n,ast.Assign)
            and any(isinstance(t,ast.Name) and t.id=='seen' for t in n.targets))
        symbols=('aether_zpl_directory','aether_zpl_mkdir','aether_zpl_rmdir')
        for reader in (False,True):
            options=dict(pool=True,pool_namespace=True,pool_import=True,pool_zpl_write=not reader,
                pool_zpl_recover=reader,fs_service=not reader,fs_service_mixed=True,fs_service_wait=not reader,
                fs_service_bulk=True,fs_service_runtime=True,fs_service_activation=not reader,
                fs_service_names=True,fs_service_directories=True)
            scope={n:p.default for n,p in inspect.signature(runtime.check_engine_bindings).parameters.items() if n!='mapping'}
            scope.update(options)
            exec(compile(ast.Module(body=node.body[:stop],type_ignores=[]),'<actual directory requirements>','exec'),scope)
            required=scope['required']
            for name in symbols:self.assertEqual(required.get(name),None if reader else 'selected-engine.o')
            self.assertEqual(required.get('aether_fs_directories_run'),None if reader else 'selected-engine.o')
            mapping='\n'.join('0 0 10 1 /private/'+owner+':(.text)\n0 0 10 1 '+name for name,owner in required.items())
            runtime.check_engine_bindings(mapping,**options)
            if not reader:
                for name in symbols:
                    bad='\n'.join(line for line in mapping.splitlines() if line.split()[-1:]!=[name])
                    with self.assertRaises(ValueError):runtime.check_engine_bindings(bad,**options)
        with self.assertRaises(ValueError):
            runtime.check_engine_bindings('',fs_service_directories=True,fs_service_names=True)

    def test_emitted_cfg_and_early_guards_preserve_old_profiles(self):
        node=next(n for n in ast.walk(ast.parse(Path(runtime.__file__).read_text())) if isinstance(n,ast.Expr)
            and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='command'
            and 'link-arg=--oformat=binary' in ast.unparse(n))
        f=self.fixture('normal');emitted=[]
        scope={n.id:False for n in ast.walk(node) if isinstance(n,ast.Name) and isinstance(n.ctx,ast.Load)}
        scope.update(command=lambda argv,log:emitted.append(list(map(str,argv))),str=str,volume_readonly=runtime.volume_readonly,
            SOURCE=runtime.SOURCE,name='pool-import',namespace_ipc=True,namespace_wait=True,service_case=0,volume=True,
            engine_native=True,service={'activation':True,'names':True,'directories':True},_zpl_fs_namespace=None,
            _zpl_fs_runtime=True,_zpl_fs_activation=True,_zpl_fs_names=True,_zpl_fs_directories=True,_zpl_fs_bulk=True,_zpl_fs_mixed=True,
            pool_create=True,pool_zpl_write=True,WRITE_CASES=runtime.WRITE_CASES,driver_source=f.output/'writer/supervisor.rs',dest=f.output/'writer')
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual directory compiler command>','exec'),scope)
        f.builds['writer']['commands'][1]={'argv':emitted[0]};self.verify(f,'normal')
        with self.assertRaisesRegex(ValueError,'directories require'):runtime.suite(None,_zpl_fs_directories=True)
        with self.assertRaisesRegex(ValueError,'directories require'):pair.pair(None,None,filesystem_service_directories=True)
        import subprocess,sys
        result=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/zpl_pair.py'),'--delivery','/missing',
            '--utc-delivery','/missing','--filesystem-service-directories'],capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,64);self.assertIn('directories require',result.stderr);self.assertNotIn('[RUNNING]',result.stderr)


if __name__=='__main__':unittest.main()
