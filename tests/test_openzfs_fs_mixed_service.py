# SPDX-License-Identifier: BSD-2-Clause
"""Exact mixed intake/original C composition and independent final-data oracle."""
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

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import openzfs_fs_mixed_service as mixed
DELIVERY=ROOT / 'userland/build/service-deliveries/filesystem-service-mixed-2026-10-19-v1'
WAIT_DELIVERY=DELIVERY.with_name('filesystem-service-mixed-wait-2026-10-20-v1')
SOURCE=ROOT/'user/storage/openzfs-volume'


class MixedIntake(unittest.TestCase):
    def test_exact41_closed_manifest_and_engine_retirement_tool_drift(self):
        s=mixed.intake(DELIVERY);self.assertTrue(s['mixed']);self.assertEqual(s['manifest_sha256'],mixed.SEAL)
        self.assertGreater(len(s['inputs']),360)
        with tempfile.TemporaryDirectory(prefix='aether-mixed-intake-') as directory:
            root=Path(directory).resolve()/'delivery';shutil.copytree(DELIVERY,root)
            p=root/'source/mixed-service.h';old=p.read_bytes();p.write_bytes(old+b' ')
            with self.assertRaisesRegex(ValueError,'member identity'):mixed.intake(root)
            p.write_bytes(old);(root/'extra').write_text('x')
            with self.assertRaisesRegex(ValueError,'closure'):mixed.intake(root)
            (root/'extra').unlink();p.unlink();p.symlink_to(DELIVERY/'source/mixed-service.h')
            with self.assertRaises(ValueError):mixed.intake(root)
        original=mixed.sha
        for target in (SOURCE/'pool-mixed-lifetime.h',SOURCE/'zpl-mutate.c',Path('/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang')):
            with patch.object(mixed,'sha',side_effect=lambda p:'0'*64 if Path(p)==target else original(p)):
                with self.assertRaisesRegex(ValueError,'drift'):mixed.intake(DELIVERY)

    def test_strict_original_c_compilation_every_writer_and_both_reader_profiles(self):
        r=json.loads((ROOT/'docs/evidence/fs-service-namespace-2026-10-19.json').read_text())
        command=r['native_original_c_partial']['commands'][0]['argv'];prefix=command[:command.index('-c')]
        with tempfile.TemporaryDirectory(prefix='aether-mixed-native-c-') as directory:
            out=Path(directory).resolve();(out/'fs-mixed-owner.inc').write_text(mixed.owner((SOURCE/'fs-service-owner.inc').read_text()))
            for reader,empty,case in [(False,c=='lost-reply',c) for c in ('normal','lost-reply','partial-request','close-failure')]+[(True,e,'normal') for e in (False,True)]:
                p=out/'probe.c';p.write_text(mixed.probe((SOURCE/'zpl-mutation-probe.c').read_text(),reader,empty,case))
                r=subprocess.run([*prefix,'-I'+str(DELIVERY/'source'),'-c',str(p),'-o',str(out/'probe.o')],capture_output=True,text=True,timeout=30)
                self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        for reader,empty,case in [(1,False,'normal'),(False,1,'normal'),(False,True,'normal'),(False,False,'lost-reply'),(False,False,'unknown')]:
            with self.assertRaises(ValueError):mixed.probe((SOURCE/'zpl-mutation-probe.c').read_text(),reader,empty,case)
        with self.assertRaisesRegex(ValueError,'drift'):mixed.owner((SOURCE/'fs-service-owner.inc').read_text()+' ')

    def test_all12_original_partial_origins_and_wrapped_consuming_close(self):
        required={n:'zpl-mutation.o' for n in ('aether_zpl_open_write','aether_zpl_close','aether_zpl_root',
            'aether_zpl_lookup','aether_zpl_read','aether_zpl_write','aether_zpl_create','aether_zpl_rename','aether_zpl_remove')}
        required.update(aether_fs_mixed_run='filesystem-mixed.o',aether_pool_namespace0_retire='vdev-selected.o',aether_pool_service16_retire='vdev-selected.o')
        text='\n'.join('0 0 10 1 /native/'+owner+':(.text)\n0 0 10 1 '+name for name,owner in required.items())
        self.assertEqual(len(mixed.partial_origins(text)),12)
        for name,owner in required.items():
            for bad in ('\n'.join(l for l in text.splitlines() if l!='0 0 10 1 '+name),text+'\n0 0 10 1 '+name,
                    text.replace('/native/'+owner+':(.text)\n0 0 10 1 '+name,'/native/fake.o:(.text)\n0 0 10 1 '+name)):
                with self.assertRaises(ValueError):mixed.partial_origins(bad)
        wrapped=text.replace('0 0 10 1 aether_zpl_close\n','')+'\n0 0 10 1 /native/zpl-mutation.o:(.text.aether_zpl_close)\n0 0 10 1 __wrap_aether_zpl_close'
        nm='00000000 00000010 T aether_zpl_close';self.assertEqual(len(mixed.partial_origins(wrapped,nm,True)),13)
        for bad in (None,'',nm+'\n'+nm,nm.replace(' T ',' W '),nm.replace('00000010','00000000')):
            with self.assertRaises(ValueError):mixed.partial_origins(wrapped,bad,True)


class MixedReaderOracle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='aether-mixed-oracle-');cls.addClassCleanup(cls.temp.cleanup)
        cls.out=Path(cls.temp.name);cls.sdk=subprocess.check_output(['xcrun','--show-sdk-path'],text=True).strip()
        cls.body='\n'.join(line for line in mixed.probe((SOURCE/'zpl-mutation-probe.c').read_text(),True).splitlines() if not line.startswith('#include'))+'\n'
        fixture=(ROOT/'tests/fixtures/openzfs_namespace_probe.c').read_text().replace('"aether-created"','"p"').replace('"aether-renamed"','"q"')
        old='*out = (aether_zpl_node){99, 788, 0, 0100600};';assert fixture.count(old)==2
        fixture=fixture.replace(old,'*out = (aether_zpl_node){99, 788, FS_MIXED_EMPTY ? 0 : 16, 0100600};')
        old='value = file ? 0 : phase == 1 || phase == 2 ? 4 : 3;';assert fixture.count(old)==1
        fixture=fixture.replace(old,'value = file ? (FS_MIXED_EMPTY ? 0 : 16) : phase == 1 || phase == 2 ? 4 : 3;',1)
        old='''        CHECK(gen == 788 && !off && length == 1);
        *count = mode == 10;
        return 0;'''
        new='''        CHECK(gen == 788);
        if (!FS_MIXED_EMPTY && off == 0 && length == 16) {
            *count = mode == 25 ? 15 : 16;
            for (unsigned i=0;i<16;++i) ((unsigned char*)buf)[i]=71+i;
            if (mode == 24) ((unsigned char*)buf)[0]^=1;
        } else { CHECK(off == (FS_MIXED_EMPTY ? 0 : 16) && length == 1); *count = mode == 10; }
        return 0;''';assert fixture.count(old)==1;fixture=fixture.replace(old,new,1)
        old='''            uint64_t time[2] = {1791290045, 123};'''
        new=old+'''
            if (file && !FS_MIXED_EMPTY && (a[i].attr == ZPL_MTIME || a[i].attr == ZPL_CTIME)) time[0]+=5;
            if (file && (a[i].attr == ZPL_CRTIME || a[i].attr == ZPL_ATIME)) {
                if (mode == 27) time[0]=1791290039;
                if (mode == 28) time[0]=1791290055;
            }
            if (file && mode == 29 && a[i].attr == ZPL_ATIME) ++time[0];'''
        assert fixture.count(old)==1;fixture=fixture.replace(old,new,1)
        (cls.out/'fixture.c').write_text(fixture)
        cls.normal=cls.compile(cls.body,'normal')
        cls.empty=cls.compile(cls.body.replace('#define FS_MIXED_EMPTY 0','#define FS_MIXED_EMPTY 1',1),'empty')

    @classmethod
    def compile(cls,body,name):
        (cls.out/'namespace-probe.inc').write_text(body);binary=cls.out/name
        empty='#define FS_MIXED_EMPTY 1' in body
        p=subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang','-isysroot',cls.sdk,'-std=gnu11','-O2','-Wall','-Wextra','-Werror',
            '-DMNS_READER=1','-DMNS_KIND=1','-DFS_MIXED_EMPTY='+str(int(empty)),'-I'+str(cls.out),'-I'+str(SOURCE),str(cls.out/'fixture.c'),'-o',str(binary)],capture_output=True,text=True,timeout=30)
        if p.returncode:raise RuntimeError(p.stdout+p.stderr)
        return binary

    def run_mode(self,binary,mode,fault=0,expected=0):
        p=subprocess.run([str(binary),str(mode),str(fault)],capture_output=True,text=True,timeout=5)
        self.assertEqual(p.returncode,expected,p.stdout+p.stderr)
        if expected:self.assertIn('HOST NAMESPACE oracle95',p.stderr)
        return p.stdout

    def test_full_final16_and_empty_lost_reply_oracles_reject_corrupt_inputs(self):
        for binary in (self.normal,self.empty):
            self.run_mode(binary,0)
            for mode in [*range(1,20),27,28,29]:self.run_mode(binary,mode)
        for mode in (24,25):self.run_mode(self.normal,mode)

    def test_every_reachable_reader_api_fault_closes_without_replay(self):
        import re
        for binary in (self.normal,self.empty):
            count=int(re.search(r'calls=(\d+)',self.run_mode(binary,0))[1])
            for fault in range(1,count+1):self.run_mode(binary,0,fault)

    def test_compiling_data_size_birth_order_atime_and_inventory_omissions_fail95(self):
        for name,old,new,mode in (
            ('content','data[i] != 71+i','0',24),
            ('short-read','got != sizeof(data)','0',25),
            ('birth-lower','crtime[0] < 1791290040','0',27),
            ('birth-order','mtime[0] < crtime[0] ||\n        (mtime[0] == crtime[0] && mtime[1] < crtime[1])','0',28),
            ('atime','memcmp(crtime, atime, 16)','0',29),
            ('inventory','return mask == 511 && added == !!extra ? 0 : EIO;','return ((void)mask,(void)added,0);',18)):
            self.assertEqual(self.body.count(old),1)
            with self.subTest(name=name):
                self.run_mode(self.compile(self.body.replace(old,new,1),name),mode,expected=95)


if __name__=='__main__':unittest.main()

class MixedPairAdmission(unittest.TestCase):
    def fixture(self,case,waiting=False):
        import test_openzfs_fs_service as old
        import openzfs_namespace as media
        from openzfs_fs_mixed import mixed_lifetime_hooks,mixed_lifetime_record
        helper=old.ServiceIntake();f=helper.fixture();self.addCleanup(helper.doCleanups)
        b=f.builds['writer'];selected=mixed.intake(WAIT_DELIVERY if waiting else DELIVERY,waiting)
        b.update(fs_service=selected,fs_service_case=case)
        cfg=['--cfg','fs_mixed']+(['--cfg','fs_lost_reply'] if case=='lost-reply' else ['--cfg','fs_partial_request'] if case=='partial-request' else [])
        b['commands'][1]['argv']+=cfg
        if case=='close-failure':b['commands'][2]['argv']+=['--wrap=aether_zpl_close']
        for role in ('writer','reader'):
            build=f.builds[role];empty=role=='reader' and case=='lost-reply'
            build.update(fs_service_mixed=True,fs_service_mixed_empty=empty)
            label=(SOURCE/'namespace-label.inc').read_text()
            if role=='reader':label=media.recovery_label_source(label)
            build['port']={'volume':{'namespace_objects':{
                'mixed-probe-source':hashlib.sha256(mixed.probe((SOURCE/'zpl-mutation-probe.c').read_text(),role=='reader',case=='lost-reply',case).encode()).hexdigest(),
                'mixed-label-source':hashlib.sha256(label.encode()).hexdigest()}}}
        b['port']['volume']['namespace_objects'].update({
            'fs-service-consumer':mixed.sha(selected['object']),
            'mixed-owner-source':hashlib.sha256(mixed.owner((SOURCE/'fs-service-owner.inc').read_text()).encode()).hexdigest(),
            'mixed-hooks-source':hashlib.sha256(mixed_lifetime_hooks((SOURCE/'pool-vdev-hooks.inc').read_text()).encode()).hexdigest(),
            'mixed-record-source':hashlib.sha256(mixed_lifetime_record((SOURCE/'pool-lifetime.inc').read_text()).encode()).hexdigest()})
        b['port']['fs_service_origins']={n:'/build/zpl-mutation.o' for n in ('aether_zpl_open_write','aether_zpl_close',
            'aether_zpl_root','aether_zpl_lookup','aether_zpl_read','aether_zpl_write','aether_zpl_create','aether_zpl_rename','aether_zpl_remove')}
        b['port']['fs_service_origins'].update(aether_fs_mixed_run='/delivery/filesystem-mixed.o',
            aether_pool_namespace0_retire='/build/vdev-selected.o',aether_pool_service16_retire='/build/vdev-selected.o')
        if case=='close-failure':b['port']['fs_service_origins']['__wrap_aether_zpl_close']='/build/zpl-mutation.o'
        if waiting:
            b['namespace_wait']=True
            b['commands'][0]['argv']+=['-Dnative-service-channel-wait=true']
            b['commands'][1]['argv']+=['--cfg','namespace_wait']
            b['cases'][0]['kernel_profile']='AENBD004/ABI26'
            b['port']['volume']['namespace_objects']['mixed-owner-source']=hashlib.sha256(mixed.owner((SOURCE/'fs-service-owner.inc').read_text(),True).encode()).hexdigest()
            b['port']['fs_service_origins'].pop('aether_fs_mixed_run')
            b['port']['fs_service_origins']['aether_fs_mixed_wait_run']='/delivery/filesystem-mixed-wait.o'
        return f

    def verify(self,f,case,**kw):
        import zpl_pair as pair
        import service_runtime_smoke as runtime
        options=dict(writer_ticks_6000=True,writer_60s=True,recovery_diagnostic=True,
            filesystem_service=DELIVERY,filesystem_service_case=case,filesystem_service_mixed=True);options.update(kw)
        with patch.object(runtime,'sealed'):pair.verify_prepared(f.output,f.builds,**options)

    def test_all_fixed_cases_reject_selector_source_origin_and_role_drift(self):
        for case in ('normal','lost-reply','partial-request','close-failure'):
            f=self.fixture(case);self.verify(f,case);saved=copy.deepcopy(f.builds)
            for kw in ({'filesystem_service_mixed':False},{'filesystem_service_lifetimes':True},
                    {'filesystem_service_namespace':True},{'namespace_mutation':'create'},
                    {'writer_60s':False},{'writer_ticks_6000':False}):
                with self.assertRaises(ValueError):self.verify(f,case,**kw)
            for role,key,value in [('writer','fs_service_mixed',False),('baseline','fs_service_mixed',True),
                    ('writer','fs_service_mixed_empty',True),('reader','fs_service_mixed_empty',case!='lost-reply')]:
                f.builds=copy.deepcopy(saved);f.builds[role][key]=value
                with self.assertRaises(ValueError):self.verify(f,case)
            for role,key in [('writer','mixed-record-source'),('writer','mixed-hooks-source'),('writer','mixed-owner-source'),
                    ('reader','mixed-probe-source'),('reader','mixed-label-source'),('writer','fs-service-consumer')]:
                f.builds=copy.deepcopy(saved);f.builds[role]['port']['volume']['namespace_objects'][key]='drift'
                with self.assertRaises(ValueError):self.verify(f,case)
            f.builds=copy.deepcopy(saved);f.builds['writer']['port']['fs_service_origins']['aether_pool_namespace0_retire']='/fake/old.o'
            with self.assertRaisesRegex(ValueError,'origin'):self.verify(f,case)

    def test_actual_driver_partial_link_expressions_match_every_case(self):
        import ast
        import service_runtime_smoke as runtime
        import openzfs_elapsed as elapsed
        import openzfs_fs_service as service
        def expression(module,marker):
            return next(n for n in ast.walk(ast.parse(Path(module.__file__).read_text())) if isinstance(n,ast.Expr)
                and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='command' and marker in ast.unparse(n))
        driver=expression(runtime,'link-arg=--oformat=binary');partial=expression(elapsed,'bridge-partial.map')
        for case in ('normal','lost-reply','partial-request','close-failure'):
            f=self.fixture(case);emitted=[]
            def command(argv,log):emitted.append(list(map(str,argv)))
            scope={n.id:False for n in ast.walk(driver) if isinstance(n,ast.Name) and isinstance(n.ctx,ast.Load)}
            scope.update(command=command,str=str,volume_readonly=runtime.volume_readonly,SOURCE=runtime.SOURCE,name='pool-import',
                namespace_ipc=True,service_case=service.case_number(case),volume=True,engine_native=True,service={},
                _zpl_fs_namespace=None,_zpl_fs_mixed=True,pool_create=True,pool_zpl_write=True,WRITE_CASES=runtime.WRITE_CASES,
                driver_source=f.output/'writer/supervisor.rs',dest=f.output/'writer')
            exec(compile(ast.Module(body=[driver],type_ignores=[]),'<actual mixed driver>','exec'),scope)
            scope=dict(command=command,tool='ld.lld',service_case=service.case_number(case),volume_fs_bridge=None,
                volume_fs_service={},output=f.output/'writer',base=[])
            exec(compile(ast.Module(body=[partial],type_ignores=[]),'<actual mixed partial>','exec'),scope)
            f.builds['writer']['commands']=f.builds['writer']['commands'][:1]+[{'argv':v} for v in emitted]
            self.verify(f,case)

    def test_invalid_cli_selectors_exit64_before_build_or_vm(self):
        for flags in (['--filesystem-service-mixed'],['--filesystem-service-mixed','--filesystem-service-lifetimes','--filesystem-service',str(DELIVERY)]):
            p=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/zpl_pair.py'),'--delivery','/absent','--utc-delivery','/absent',*flags],capture_output=True,timeout=5)
            self.assertEqual(p.returncode,64,p.stderr);self.assertNotIn(b'[RUNNING]',p.stderr)


class MixedWaitAdmission(unittest.TestCase):
    fixture=MixedPairAdmission.fixture
    verify=MixedPairAdmission.verify
    # Reuse the actual closed-preparation fixture, but do not rerun unchanged
    # original tests under an implicit new profile.
    def test_exact_wait_candidate_abi_options_sources_origins_and_role_admission(self):
        from openzfs_fs_service import intake,recheck
        from storage_channel_wait import validate
        selected=intake(WAIT_DELIVERY,mixed=True,waiting=True)
        recheck(selected)
        self.assertTrue(selected['waiting'])
        for delivery,waiting in [(WAIT_DELIVERY,False),(DELIVERY,True)]:
            with self.assertRaisesRegex(ValueError,'manifest identity'):intake(delivery,mixed=True,waiting=waiting)
        validate(True,True,True,True,False,selected,None,True)
        for opts in [(False,True,True,True,False,selected,None,True),
                     (True,True,True,True,False,selected,None,False),
                     (True,True,True,True,False,mixed.intake(DELIVERY),None,True),
                     (True,True,True,False,True,selected,None,True)]:
            with self.assertRaises(ValueError):validate(*opts)
        changed=copy.deepcopy(selected);changed['waiting']=False
        with self.assertRaises(ValueError):recheck(changed)
        for case in ('normal','lost-reply','partial-request','close-failure'):
            f=self.fixture(case,True)
            opts=dict(filesystem_service=WAIT_DELIVERY,filesystem_service_wait=True)
            self.verify(f,case,**opts)
            saved=copy.deepcopy(f.builds)
            for role,key,value in [('writer','namespace_wait',False),('reader','namespace_wait',True),('baseline','namespace_wait',True)]:
                f.builds=copy.deepcopy(saved);f.builds[role][key]=value
                with self.assertRaises(ValueError):self.verify(f,case,**opts)
            for change in ('wait-flag','wait-cfg','entry','owner','abi','reader-option'):
                f.builds=copy.deepcopy(saved);b=f.builds['writer']
                if change=='wait-flag':b['commands'][0]['argv'].remove('-Dnative-service-channel-wait=true')
                if change=='wait-cfg':b['commands'][1]['argv'][-1]='unknown_wait'
                if change=='entry':b['port']['fs_service_origins']['aether_fs_mixed_wait_run']='/fake/filesystem-mixed.o'
                if change=='owner':b['port']['volume']['namespace_objects']['mixed-owner-source']='drift'
                if change=='abi':b['cases'][0]['kernel_profile']='AENBD003/ABI25'
                if change=='reader-option':f.builds['reader'].setdefault('commands',[]).append({'argv':['zig','build','-Dnative-service-channel-wait=true']})
                with self.assertRaises(ValueError):self.verify(f,case,**opts)

    def test_wait_candidate_rejects_mutable_adapter_and_pointers(self):
        from openzfs_fs_service import recheck
        selected=mixed.intake(WAIT_DELIVERY,True)
        for field,value in [('object',str(DELIVERY/'objects/filesystem-mixed.o')),('header_directory','/other'),('manifest_sha256',mixed.SEAL)]:
            changed=copy.deepcopy(selected);changed[field]=value
            with self.assertRaises(ValueError):recheck(changed)
        original=mixed.sha
        target=ROOT/'user/storage/namespace-wait-channel.rs'
        with patch.object(mixed,'sha',side_effect=lambda p:'0'*64 if Path(p)==target else original(p)):
            with self.assertRaisesRegex(ValueError,'wait adapter drift'):mixed.intake(WAIT_DELIVERY,True)
        with tempfile.TemporaryDirectory(prefix='aether-wait-intake-') as folder:
            root=Path(folder).resolve()/'delivery';shutil.copytree(WAIT_DELIVERY,root)
            p=root/'source/channel.rs';p.write_bytes(p.read_bytes()+b' ')
            with self.assertRaisesRegex(ValueError,'member identity'):mixed.intake(root,True)

    def test_wait_original_c_owner_and_exact_partial_origins(self):
        report=json.loads((ROOT/'docs/evidence/fs-service-namespace-2026-10-19.json').read_text())
        command=report['native_original_c_partial']['commands'][0]['argv'];prefix=command[:command.index('-c')]
        with tempfile.TemporaryDirectory(prefix='aether-mixed-wait-native-c-') as directory:
            out=Path(directory).resolve()
            (out/'fs-mixed-owner.inc').write_text(mixed.owner((SOURCE/'fs-service-owner.inc').read_text(),True))
            for case in ('normal','lost-reply','partial-request','close-failure'):
                p=out/'probe.c';p.write_text(mixed.probe((SOURCE/'zpl-mutation-probe.c').read_text(),False,case=='lost-reply',case))
                done=subprocess.run([*prefix,'-I'+str(WAIT_DELIVERY/'source'),'-c',str(p),'-o',str(out/'probe.o')],capture_output=True,text=True,timeout=30)
                self.assertEqual(done.returncode,0,done.stdout+done.stderr)
        required={n:'zpl-mutation.o' for n in ('aether_zpl_open_write','aether_zpl_close','aether_zpl_root','aether_zpl_lookup','aether_zpl_read','aether_zpl_write','aether_zpl_create','aether_zpl_rename','aether_zpl_remove')}
        required.update(aether_fs_mixed_wait_run='filesystem-mixed-wait.o',aether_pool_namespace0_retire='vdev-selected.o',aether_pool_service16_retire='vdev-selected.o')
        text='\n'.join('0 0 10 1 /native/'+owner+':(.text)\n0 0 10 1 '+name for name,owner in required.items())
        self.assertEqual(len(mixed.partial_origins(text,waiting=True)),12)
        with self.assertRaises(ValueError):mixed.partial_origins(text)
        for name in required:
            with self.assertRaises(ValueError):mixed.partial_origins(text.replace('0 0 10 1 '+name+'\n','',1) if name!=list(required)[-1] else text.rsplit('\n',1)[0],waiting=True)
