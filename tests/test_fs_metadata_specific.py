# SPDX-License-Identifier: BSD-2-Clause
"""Actual metadata loss/wrapper fragments, original link maps and fixed groups."""
from pathlib import Path
import json
import subprocess
import tempfile
import unittest

import test_fs_metadata_failures as prior

ROOT,af07,harness=prior.ROOT,prior.af07,prior.harness


class MetadataSpecific(unittest.TestCase):
    command=prior.MetadataFailures.command
    driver=prior.MetadataFailures.driver
    model_campaign=prior.MetadataFailures.model_campaign

    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='aether-af07-specific-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.out=Path(cls.temp.name)
        cls.tools=json.loads((af07.DELIVERY/'inputs.json').read_text())['tools']
        cls.sdk=subprocess.check_output(['xcrun','--show-sdk-path'],text=True).strip()

    def c_prefix(self):
        return [self.tools['clang']['path'],'-isysroot',self.sdk,'-std=c11',
                '-Wall','-Wextra','-Werror','-I'+str(self.out),
                '-I'+str(af07.VOLUME),'-I'+str(af07.DELIVERY/'source')]

    def test_all_metadata_controllers_fit_and_pass_native_clippy(self):
        for case in af07.METADATA_REPLIES+af07.METADATA_PROVIDERS:
            stage=self.out/case;stage.mkdir()
            source=stage/'controller.rs';source.write_text(af07.controller(self.driver(),stage,True,case))
            def command(args,log):Path(log).write_text(self.command(args))
            harness.rust(stage,source,command,True,case)
            self.assertLessEqual((stage/'supervisor.raw').stat().st_size,8192)
            flags=['--edition=2024','--target=x86_64-unknown-none','-Dwarnings','-Cpanic=abort','--emit=obj']
            for cfg in harness.CFG:flags+=['--cfg',cfg]
            if case in af07.METADATA_REPLIES:flags+=['--cfg','fs_metadata_loss']
            self.command([self.tools['clippy-driver']['path'],*flags,source,'-o',stage/'clippy.o'])
            print('AF07_METADATA_FIT',case,(stage/'supervisor.raw').stat().st_size,
                  af07.digest(stage/'supervisor.raw'))

    def loss(self,body,label):
        source=self.out/(label+'.rs')
        source.write_text((ROOT/'tests/fixtures/fs_metadata_loss.rs').read_text().replace('// LOSS_METHODS',body))
        binary=self.out/label
        self.command(['rustc','+1.98.0','--edition=2024','-Dwarnings','-Dunsafe_op_in_unsafe_fn',
                      '--test',source,'-o',binary])
        return binary

    def test_actual_loss_methods_fragmentation_corruption_and_compiling_omissions(self):
        body=(af07.SERVICE/'fs-metadata-loss.inc').read_text()
        self.assertIn('3 passed; 0 failed',self.command([self.loss(body,'loss'), '--test-threads=1']))
        for label,old,new in (
            ('no-close','check(call(0x24003, self.receive, 0, 0, 0).0 == 0);',''),
            ('no-stage','check(stage <= 2);','')):
            self.assertIn(old,body)
            output=self.command([self.loss(body.replace(old,new,1),label),'--test-threads=1'],101)
            self.assertIn('AF07_METADATA_LOSS_ORACLE',output)

    def test_actual_settlement_requires_the_metadata_loss_cfg(self):
        stage=self.out/'finish';stage.mkdir()
        af07.controller(self.driver(),stage,False,'metadata-header-loss')
        text=(stage/'af07-connection.rs').read_text()
        method='    pub fn finish'+text.split('    pub fn finish',1)[1].split('\n}\n\npub fn stale',1)[0]
        source=stage/'test.rs';source.write_text((ROOT/'tests/fixtures/fs_metadata_finish.rs').read_text()
                                               .replace('// FINISH_METHOD',method))
        binary=stage/'finish'
        prefix=['rustc','+1.98.0','--edition=2024','-Dwarnings','-Dunsafe_op_in_unsafe_fn','--test']
        self.command(prefix+['--cfg','fs_metadata_loss',source,'-o',binary])
        self.assertIn('1 passed; 0 failed',self.command([binary]))
        self.command(prefix+[source,'-o',binary])
        self.assertIn('AF07_FINISH_ORACLE',self.command([binary],101))

    def test_actual_getter_faults_are_once_only_bounded_and_preserve_real_errors(self):
        body=(af07.VOLUME/'metadata-fault.inc').read_text()
        (self.out/'fault.inc').write_text(body)
        source=self.out/'getter.c';source.write_text((ROOT/'tests/fixtures/fs_metadata_getter_fault.c').read_text()
                                                       .replace('"FAULT"','"fault.inc"'))
        for fault in range(5):
            binary=self.out/('getter-'+str(fault))
            self.command(self.c_prefix()+['-DAF07_METADATA_FAULT='+str(fault),source,'-o',binary])
            self.command([binary]);self.command([binary,'1'])
        for label,old,new,fault in (
            ('early','af07_gets == 4','af07_gets == 3',1),
            ('negative','return -EIO;','return EIO;',4),
            ('bound','af07_gets >= 5','af07_gets >= 4',0)):
            self.assertEqual(body.count(old),1)
            (self.out/'fault.inc').write_text(body.replace(old,new,1))
            binary=self.out/('getter-'+label)
            self.command(self.c_prefix()+['-DAF07_METADATA_FAULT='+str(fault),source,'-o',binary])
            self.assertIn('AF07_GETTER_ORACLE96',self.command([binary],96))

    def test_actual_metadata_completion_guards_and_counter_omission(self):
        (self.out/'sys').mkdir(exist_ok=True)
        (self.out/'sys/auxv.h').write_text('unsigned long getauxval(unsigned long);\n')
        source=self.out/'owner.c'
        source.write_text((ROOT/'tests/fixtures/fs_metadata_owner.c').read_text().replace('"OWNER"','"owner.inc"'))
        original=prior.owner((af07.VOLUME/'fs-service-owner.inc').read_text())
        probe,owner=af07.provider(prior.probe((af07.VOLUME/'zpl-mutation-probe.c').read_text()),original)
        for case in af07.METADATA_REPLIES+af07.METADATA_PROVIDERS:
            _,selected=af07.metadata_provider(probe,owner,case)
            (self.out/'owner.inc').write_text(selected)
            result=1 if case in af07.METADATA_REPLIES else 3 if case=='metadata-errno' else 2
            binary=self.out/('owner-'+case)
            flags=['-DAETHER_FS_SERVICE_CASE=0','-DAF07_HOST_METADATA_RESULT='+str(result)]
            self.command(self.c_prefix()+flags+[source,'-o',binary])
            for mode in range(9):self.command([binary,str(mode)])
        old=' || af07_fault_error ||'
        self.assertEqual(selected.count(old),1)
        (self.out/'owner.inc').write_text(selected.replace(old,' ||',1))
        binary=self.out/'owner-omission'
        self.command(self.c_prefix()+flags+[source,'-o',binary])
        self.assertIn('AF07_OWNER_ORACLE96',self.command([binary,'8'],96))

    def test_wrapped_original_definition_uses_actual_partial_and_final_maps(self):
        source=self.out/'map.c'
        source.write_text('int __real_aether_zpl_getattr(int);\n'
            '__attribute__((noinline)) int aether_zpl_getattr(int value) { return value + 1; }\n'
            '__attribute__((noinline)) int __wrap_aether_zpl_getattr(int value) { return __real_aether_zpl_getattr(value); }\n'
            'int _start(void) { return __wrap_aether_zpl_getattr(1); }\n')
        obj=self.out/'map.o';partial=self.out/'partial.o';final=self.out/'map.elf'
        clang=self.tools['clang']['path'];lld=self.tools['lld']['path'];nm=Path(clang).parent/'llvm-nm'
        self.command([clang,'--target=x86_64-linux-musl','-ffreestanding','-fno-stack-protector',
                      '-ffunction-sections','-O2','-c',source,'-o',obj])
        self.command([lld,'-r','--wrap=aether_zpl_getattr','-Map='+str(self.out/'partial.map'),obj,'-o',partial])
        self.command([lld,'-static','--gc-sections','--no-undefined','-e','_start',
                      '-Map='+str(self.out/'final.map'),partial,'-o',final])
        for label,binary,owner in (('partial',partial,obj),('final',final,partial)):
            symbols=self.command([nm,'--print-size','--defined-only',binary])
            mapping=(self.out/(label+'.map')).read_text()
            self.assertEqual(af07.original_getter(mapping,symbols,owner),str(owner))
            with self.assertRaises(ValueError):af07.original_getter(mapping,symbols,self.out/'foreign.o')
            with self.assertRaises(ValueError):af07.original_getter(mapping,symbols+'\n'+symbols,owner)
            bad=symbols.replace(' T aether_zpl_getattr',' W aether_zpl_getattr')
            with self.assertRaises(ValueError):af07.original_getter(mapping,bad,owner)

    def test_both_metadata_groups_prepare_then_capture_before_any_image_reuse(self):
        for group,count in (('replies',9),('providers',12)):
            record=self.model_campaign(group=group)
            self.assertEqual(record['status'],'pass')
            self.assertEqual(len(record['cases']),count)
            self.assertEqual(len(record['serial']),count)
            self.assertTrue(all(s['machine_witness']['selection_complete'] for s in record['serial'].values()))
        self.assertIn('[FAIL]',self.command(['python3','-B',ROOT/'scripts/fs_metadata_service.py',
                                            '--failure-paths','unknown'],64))
        from unittest.mock import patch
        with patch.object(harness.tempfile,'mkdtemp') as create:
            with self.assertRaisesRegex(ValueError,'fixed failure group'):
                harness.campaign(False,False,'unknown')
            create.assert_not_called()

    def test_unselected_positive_c_sources_stay_exact(self):
        selected,owner=af07.provider(prior.probe((af07.VOLUME/'zpl-mutation-probe.c').read_text()),
                                    prior.owner((af07.VOLUME/'fs-service-owner.inc').read_text()))
        import hashlib
        receipt=json.loads((ROOT/'docs/evidence/fs-af07-capture-native-2026-10-21.json').read_text())['writer']
        self.assertEqual(hashlib.sha256(selected.encode()).hexdigest(),receipt['source_sha256'])
        self.assertEqual(hashlib.sha256(owner.encode()).hexdigest(),receipt['owner_sha256'])
        self.assertEqual(af07.metadata_provider(selected,owner,'normal'),(selected,owner))
