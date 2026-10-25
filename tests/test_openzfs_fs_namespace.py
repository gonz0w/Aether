# SPDX-License-Identifier: BSD-2-Clause
"""Separate namespace intake, original C adapter and actual prepared-image admission."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import openzfs_fs_namespace as ns
import openzfs_fs_service as service
import openzfs_namespace as media
import openzfs_volume as volume
import openzfs_elapsed as elapsed
import service_runtime_smoke as runtime
import zpl_pair as pair
import zpl_namespace as batch
import test_zpl_pair as controls

DELIVERY = ROOT / 'userland/build/service-deliveries/filesystem-service-namespace-2026-10-19-v1'
SOURCE = ROOT/'user/storage/openzfs-volume'


class NamespaceService(unittest.TestCase):
    def test_exact36_closure_separate_selection_and_recheck(self):
        selected = service.intake(DELIVERY, namespace=True)
        self.assertEqual(selected, ns.intake(DELIVERY))
        self.assertEqual(selected['manifest_sha256'], ns.SEAL)
        service.recheck(selected)
        for args in ({}, {'lifetimes':True}, {'lifetimes':True,'namespace':True}):
            with self.assertRaises(ValueError): service.intake(DELIVERY, **args)
        for key in ('object', 'inputs', 'namespace'):
            changed=copy.deepcopy(selected); changed[key] = {} if key=='inputs' else 'wrong'
            with self.assertRaises(ValueError): service.recheck(changed)
        with tempfile.TemporaryDirectory(prefix='aether-ns-intake-') as temp:
            root=Path(temp).resolve()/'delivery'; shutil.copytree(DELIVERY,root)
            member=root/'source/namespace-service.h'; saved=member.read_bytes()
            member.write_bytes(saved+b' ')
            with self.assertRaisesRegex(ValueError,'member identity'): ns.intake(root)
            member.write_bytes(saved); (root/'extra').write_text('x')
            with self.assertRaisesRegex(ValueError,'closure'): ns.intake(root)
            (root/'extra').unlink(); member.unlink(); member.symlink_to(DELIVERY/'source/namespace-service.h')
            with self.assertRaises(ValueError): ns.intake(root)
        original=ns.sha
        for target in (SOURCE/'zpl-mutate.c', Path('/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang')):
            with patch.object(ns,'sha',side_effect=lambda p: '0'*64 if Path(p)==target else original(p)):
                with self.assertRaisesRegex(ValueError,'drift'): ns.intake(DELIVERY)

    def test_invalid_role_mixed_delivery_and_unapproved_profiles_stop_before_build(self):
        for operation in (None, True, 1, '', 'mkdir', 'repeat', 'lifetimes'):
            with self.assertRaises(ValueError): ns.validate_profile(operation,'create',True,False,{'namespace':True})
        for kw in ({'mutation':'rename'}, {'reader':True}, {'writer':False}, {'service':None},
                {'service':{}}, {'lifetimes':True}, {'case':'partial-request'}):
            args=dict(operation='create',mutation='create',writer=True,reader=False,
                      service={'namespace':True},lifetimes=False,case='normal');args.update(kw)
            with self.assertRaises(ValueError): ns.validate_profile(**args)
        ns.validate_profile('create','create',True,False,{'namespace':True})
        ns.validate_profile('create','create',False,True,None)
        for function,args,key in ((volume.build,(None,None,None),'pool_fs_namespace'),
                (elapsed.prepare,(None,None),'volume_fs_namespace'),(runtime.suite,(None,),'_zpl_fs_namespace')):
            for value in (True, 'create', 'repeat'):
                with self.assertRaises(ValueError): function(*args, **{key:value})
        with patch.object(ns,'intake',side_effect=AssertionError('intake')):
            with self.assertRaises(ValueError): batch.batch(None,None,file_sizes=True,filesystem_service=DELIVERY)
        for flags in (['--file-sizes','--filesystem-service',str(DELIVERY)],
                ['--filesystem-service-case','lost-reply'], ['--filesystem-service-case','partial-request'],
                ['--writer-60s'],['--resume']):
            r=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/zpl_namespace.py'),
                '--delivery','/absent','--utc-delivery','/absent',*flags],capture_output=True,timeout=5)
            self.assertEqual(r.returncode,64,r.stderr)
            self.assertNotIn(b'[RUNNING]',r.stderr)

    def fixture(self,op,case):
        f=controls.PairControls();f.setUp();self.addCleanup(f.doCleanups)
        shutil.copytree(f.output/'reader',f.output/'baseline')
        f.builds['baseline']=copy.deepcopy(f.builds['reader']);f.builds['baseline']['pool_zpl_recover']=False
        b=f.builds['writer']; selected=ns.intake(DELIVERY)
        b.update(fs_service=selected,namespace_ipc=True,pool_zpl_writer_budget=True,fs_service_case=case)
        b['cases'][0]['kernel_profile']='AENBD003/ABI25'
        b['commands']=[{'argv':['zig','build','-Dnative-service-channel=true','-Dnative-service-zpl-budget=true']},
            {'argv':['rustc','-Clink-arg=--oformat=binary','--cfg','fs_namespace_'+op,*(['--cfg','fs_lost_reply'] if case=='lost-reply' else [])]},
            {'argv':['ld.lld','-r','-Map=/test/bridge-partial.map',*(['--wrap=aether_zpl_close'] if case=='close-failure' else [])]}]
        f.builds['reader'].update(pool_recovery_writer_60s=True,pool_recovery_diagnostic=True)
        for role in ('writer','reader'):
            build=f.builds[role];build.update(namespace_mutation=op,fs_namespace_operation=op)
            label=(SOURCE/'namespace-label.inc').read_text()
            if role=='reader' or op in ('rename','remove'):label=media.recovery_label_source(label)
            build['port']={'volume':{'namespace_objects':{
                'mutation-selected-source':hashlib.sha256(ns.probe((SOURCE/'zpl-mutation-probe.c').read_text(),op,role=='reader',case).encode()).hexdigest(),
                'mutation-label-source':hashlib.sha256(label.encode()).hexdigest()}}}
        b['port']['volume']['namespace_objects'].update({
            'fs-service-consumer':ns.sha(selected['object']),
            'fs-namespace-owner-source':hashlib.sha256(ns.owner((SOURCE/'fs-service-owner.inc').read_text()).encode()).hexdigest()})
        b['port']['fs_service_origins']={n:'/build/zpl-mutation.o' for n in ('aether_zpl_open_write','aether_zpl_close',
            'aether_zpl_root','aether_zpl_lookup','aether_zpl_read','aether_zpl_write','aether_zpl_create','aether_zpl_rename','aether_zpl_remove')}
        b['port']['fs_service_origins']['aether_fs_namespace_run']='/delivery/filesystem-namespace.o'
        if case=='close-failure':b['port']['fs_service_origins']['__wrap_aether_zpl_close']='/build/zpl-mutation.o'
        return f

    def verify(self,f,op,case,**kw):
        options=dict(writer_ticks_6000=True,writer_60s=True,recovery_diagnostic=True,namespace_mutation=op,
            filesystem_service=DELIVERY,filesystem_service_case=case,filesystem_service_namespace=True);options.update(kw)
        with patch.object(runtime,'sealed'):pair.verify_prepared(f.output,f.builds,**options)

    def test_all_operations_and_interruption_profiles_admit_exact_inputs_only(self):
        for op in ns.OPERATIONS:
            for case in ('normal','lost-reply','close-failure'):
                f=self.fixture(op,case);self.verify(f,op,case)
                for kw in ({'filesystem_service_namespace':False},{'filesystem_service_lifetimes':True},
                        {'filesystem_service_case':'partial-request'},{'writer_60s':False},{'writer_ticks_6000':False}):
                    with self.assertRaises(ValueError):self.verify(f,op,case,**kw)
                saved=copy.deepcopy(f.builds)
                changes=[('writer','fs_namespace_operation','rename' if op=='create' else 'create'),
                    ('baseline','fs_namespace_operation',op),('reader','fs_service',ns.intake(DELIVERY))]
                for role,key,value in changes:
                    f.builds=copy.deepcopy(saved);f.builds[role][key]=value
                    with self.assertRaises(ValueError):self.verify(f,op,case)
                for role,key in (('writer','fs-namespace-owner-source'),('reader','mutation-selected-source'),
                        ('writer','mutation-label-source'),('writer','fs-service-consumer')):
                    f.builds=copy.deepcopy(saved);f.builds[role]['port']['volume']['namespace_objects'][key]='drift'
                    with self.assertRaises(ValueError):self.verify(f,op,case)
                f.builds=copy.deepcopy(saved);f.builds['writer']['port']['fs_service_origins']['aether_zpl_create']='/fake/stub.o'
                with self.assertRaisesRegex(ValueError,'origin'):self.verify(f,op,case)

    def test_actual_driver_and_partial_link_expressions_match_all_namespace_admissions(self):
        tree=ast.parse(Path(runtime.__file__).read_text())
        driver=next(n for n in ast.walk(tree) if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call)
            and isinstance(n.value.func,ast.Name) and n.value.func.id=='command' and 'link-arg=--oformat=binary' in ast.unparse(n))
        tree=ast.parse(Path(elapsed.__file__).read_text())
        partial=next(n for n in ast.walk(tree) if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call)
            and isinstance(n.value.func,ast.Name) and n.value.func.id=='command' and 'bridge-partial.map' in ast.unparse(n))
        for op in ns.OPERATIONS:
            for case in ('normal','lost-reply','close-failure'):
                f=self.fixture(op,case); emitted=[]
                def command(argv,log):emitted.append(list(map(str,argv)))
                scope={n.id:False for n in ast.walk(driver) if isinstance(n,ast.Name) and isinstance(n.ctx,ast.Load)}
                scope.update(command=command,str=str,volume_readonly=runtime.volume_readonly,SOURCE=runtime.SOURCE,name='pool-import',
                    namespace_ipc=True,service_case=service.case_number(case),volume=True,engine_native=True,service={},
                    _zpl_fs_namespace=op,pool_create=True,pool_zpl_write=True,WRITE_CASES=runtime.WRITE_CASES,
                    driver_source=f.output/'writer/supervisor.rs',dest=f.output/'writer')
                exec(compile(ast.Module(body=[driver],type_ignores=[]),'<actual namespace driver>','exec'),scope)
                scope=dict(command=command,tool='ld.lld',service_case=service.case_number(case),volume_fs_bridge=None,
                    volume_fs_service={},output=f.output/'writer',base=[])
                exec(compile(ast.Module(body=[partial],type_ignores=[]),'<actual namespace partial>','exec'),scope)
                f.builds['writer']['commands']=f.builds['writer']['commands'][:1]+[{'argv':v} for v in emitted]
                self.verify(f,op,case)

    def test_partial_link_original_definitions_cannot_be_missing_foreign_or_duplicate(self):
        required={n:'zpl-mutation.o' for n in ('aether_zpl_open_write','aether_zpl_close','aether_zpl_root',
            'aether_zpl_lookup','aether_zpl_read','aether_zpl_write','aether_zpl_create','aether_zpl_rename','aether_zpl_remove')}
        required['aether_fs_namespace_run']='filesystem-namespace.o'
        text='\n'.join('0 0 10 1 /native/'+owner+':(.text)\n0 0 10 1 '+name for name,owner in required.items())
        self.assertEqual(len(ns.partial_origins(text)),10)
        for name,owner in required.items():
            for changed in (text.replace('0 0 10 1 '+name+'\n',''),text+'\n0 0 10 1 '+name,
                    text.replace('/native/'+owner+':(.text)\n0 0 10 1 '+name,'/native/fake.o:(.text)\n0 0 10 1 '+name)):
                if changed==text:changed='\n'.join(l for l in text.splitlines() if l!='0 0 10 1 '+name)
                with self.assertRaises(ValueError):ns.partial_origins(changed)
        wrapped=text.replace('0 0 10 1 aether_zpl_close\n','')+'\n0 0 10 1 /native/zpl-mutation.o:(.text.aether_zpl_close)\n0 0 10 1 __wrap_aether_zpl_close'
        nm='00000000 00000010 T aether_zpl_close'
        self.assertEqual(len(ns.partial_origins(wrapped,nm,True)),11)
        for bad in (None,'',nm+'\n'+nm,nm.replace(' T ',' W '),nm.replace('00000010','00000000')):
            with self.assertRaises(ValueError):ns.partial_origins(wrapped,bad,True)

    def test_actual_selected_c_compiles_all_roles_and_fixed_cases(self):
        # Original engine headers/ABI and strict compiler, not mocked C signatures.
        receipt=json.loads((ROOT/'docs/evidence/fs-service-namespace-2026-10-19.json').read_text())
        original=receipt['native_original_c_partial']['commands'][0]['argv']
        prefix=original[:original.index('-c')]
        with tempfile.TemporaryDirectory(prefix='aether-ns-adapter-') as temp:
            out=Path(temp).resolve();(out/'fs-namespace-owner.inc').write_text(ns.owner((SOURCE/'fs-service-owner.inc').read_text()))
            for op in ns.OPERATIONS:
                for reader,case in ((True,'normal'),(False,'normal'),(False,'lost-reply'),(False,'close-failure')):
                    source=out/'probe.c';obj=out/'probe.o'
                    source.write_text(ns.probe((SOURCE/'zpl-mutation-probe.c').read_text(),op,reader,case))
                    p=subprocess.run([*prefix,'-I'+str(DELIVERY/'source'),'-c',str(source),'-o',str(obj)],capture_output=True,text=True,timeout=30)
                    self.assertEqual(p.returncode,0,p.stdout+p.stderr)
            for fn,seed in ((ns.owner,(SOURCE/'fs-service-owner.inc').read_text()),
                    (lambda x:ns.probe(x,'create'),(SOURCE/'zpl-mutation-probe.c').read_text())):
                with self.assertRaisesRegex(ValueError,'drift'):fn(seed+' ')


if __name__=='__main__':unittest.main()
