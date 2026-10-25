# SPDX-License-Identifier: BSD-2-Clause
"""Actual AF07 failure controllers/owner checks and batch fail-stop ordering."""
from contextlib import ExitStack, contextmanager
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import fs_metadata_service as harness
import openzfs_fs_metadata_service as af07
from openzfs_fs_directories_service import owner, probe


@contextmanager
def owned_campaign_outputs():
    """Track this invocation's actual allocations, never global-prefix scans."""
    roots=[]
    real=harness.tempfile.mkdtemp
    def create(*args,**kwargs):
        result=real(*args,**kwargs)
        if kwargs.get('prefix')=='thread-suite-service-runtime-zpl-pair-af07-':
            roots.append(Path(result))
        return result
    try:
        with patch.object(harness.tempfile,'mkdtemp',side_effect=create):
            yield roots
    finally:
        import shutil
        for root in roots:
            receipt=root/'results.json'
            if receipt.is_file():
                record=json.loads(receipt.read_text())
                for name in record.get('owned_output_roots',[]):
                    peer=Path(name)
                    if (peer!=root and peer.parent==root.parent and
                            peer.name.startswith(root.name+'-') and peer.is_dir()):
                        shutil.rmtree(peer)
            if root.is_dir():shutil.rmtree(root)


class MetadataFailures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix='aether-af07-failures-')
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.out = Path(cls.temporary.name)

    def command(self, args, expected=0):
        result = subprocess.run(list(map(str,args)),cwd=ROOT,capture_output=True,
                                text=True,timeout=60)
        self.assertEqual(result.returncode,expected,result.stdout+result.stderr)
        return result.stdout+result.stderr

    def driver(self):
        return (af07.SERVICE/'metadata-controller.rs').read_text().replace(
            '// Build selection inserts absolute, immutable-at-run module paths here.',
            '#[path = '+json.dumps(str(af07.SERVICE/'fs-service-client.rs'))+']\nmod namespace_client;\n'
            +'#[path = '+json.dumps(str(af07.SERVICE/'fs-activation-client.rs'))+']\nmod activation;')

    def test_all_numbered_controllers_fit_and_positive_payload_stays_exact(self):
        for case in af07.CASES:
            stage=self.out/case;stage.mkdir()
            source=stage/'controller.rs'
            source.write_text(af07.controller(self.driver(),stage,True,case))
            def command(args, log):
                Path(log).write_text(self.command(args))
            harness.rust(stage,source,command,True,case)
            binary=stage/'supervisor.raw'
            self.assertLessEqual(binary.stat().st_size,8192)
            if case=='normal':
                self.assertEqual(af07.digest(binary),
                    '294050a02a00160b09f63ea288d6b6dc1b4eed32e7394b9117e1c07c2947ef29')
            print('AF07_FAILURE_FIT',case,binary.stat().st_size,af07.digest(binary))
        for case in ('retry','',None,True):
            with self.assertRaisesRegex(ValueError,'fixed failure case'):
                af07.controller(self.driver(),self.out,False,case)

    def test_actual_partial_and_lost_clients_with_fragmented_host_transcripts(self):
        selected=self.out/'af07-host-client.rs'
        selected.write_text(af07.client((af07.SERVICE/'fs-directories-client.rs').read_text()))
        source=self.out/'transcript.rs'
        source.write_text((ROOT/'tests/fixtures/fs_directory_client.rs').read_text()
                          .replace('CONTROLLER',str(selected)).replace('AFSRPC06','AFSRPC07'))
        for case,cfg in (('lost','fs_lost_reply'),('partial','fs_partial_request')):
            binary=self.out/('transcript-'+case)
            self.command(['rustc','+1.98.0','--edition=2024','-Dwarnings',
                          '-Dunsafe_op_in_unsafe_fn','--test','--cfg',cfg,source,'-o',binary])
            self.assertIn('1 passed; 0 failed',self.command([binary,'--test-threads=1']))

    def test_actual_owner_rejects_wrong_completion_and_close_order_omissions(self):
        tools=json.loads((af07.DELIVERY/'inputs.json').read_text())['tools']
        sdk=subprocess.check_output(['xcrun','--show-sdk-path'],text=True).strip()
        aux=self.out/'sys';aux.mkdir(exist_ok=True)
        (aux/'auxv.h').write_text('unsigned long getauxval(unsigned long);\n')
        body=owner((af07.VOLUME/'fs-service-owner.inc').read_text())
        _,body=af07.provider(probe((af07.VOLUME/'zpl-mutation-probe.c').read_text()),body)
        (self.out/'owner.inc').write_text(body)
        source=self.out/'owner.c'
        fixture=(ROOT/'tests/fixtures/fs_metadata_owner.c').read_text()
        source.write_text(fixture.replace('"OWNER"','"owner.inc"'))
        prefix=[tools['clang']['path'],'-isysroot',sdk,'-std=c11','-Wall','-Wextra','-Werror',
                '-I'+str(self.out),'-I'+str(af07.DELIVERY/'source')]
        for case in range(4):
            binary=self.out/('owner-'+str(case))
            self.command(prefix+['-DAETHER_FS_SERVICE_CASE='+str(case),source,'-o',binary])
            for mode in range(8 if case==3 else 7):
                self.command([binary,str(mode)])
        for label,old,new in (
            ('early','if (fs_injected < 9)','if (fs_injected < 8)'),
            ('missing-consume','    __real_aether_zpl_close(view);','    (void)view;')):
            self.assertEqual(body.count(old),1)
            (self.out/'owner.inc').write_text(body.replace(old,new,1))
            binary=self.out/('owner-'+label)
            self.command(prefix+['-DAETHER_FS_SERVICE_CASE=3',source,'-o',binary])
            self.assertIn('AF07_OWNER_ORACLE96',self.command([binary,'0'],96))

    def model_campaign(self, fail=False, group=True):
        """Test runner ordering/retention with explicit build/VM/oracle doubles."""
        images=[]
        calls=[]
        media=dict(sha256='host-model-only')
        def baseline(stage, *args):
            stage.mkdir()
            for name in ('aether.iso','engine.elf','supervisor.raw'):
                (stage/name).write_bytes(b'baseline')
            images.append(stage)
            return {}
        def engine(stage, *args, **kwargs):
            stage.mkdir();(stage/'port').mkdir()
            (stage/'port/engine.elf').write_bytes(b'engine')
            return dict(commands=[],old_service=None)
        def recompose(stage,*args,**kwargs):
            (stage/'engine.elf').write_bytes(b'engine')
            return {}
        def rust(stage,*args): (stage/'supervisor.raw').write_bytes(b'controller')
        def image(stage,*args):
            (stage/'aether.iso').write_bytes(b'guest');images.append(stage)
            return {}
        def fixture(stage):
            with (stage/'native-namespace.raw').open('wb') as stream:
                stream.truncate(1024*1024*1024+8192)
            return {}
        def guest(*args,**kwargs):
            self.assertEqual(len(images),5 if group=='replies' else 6)
            self.assertTrue(all((stage/'aether.iso').is_file() for stage in images))
            stage=Path(args[0]).parent
            self.assertFalse((stage/'native-serial.log').exists())
            # Execute the real runner's path/ownership/geometry preflight, then
            # stop at its dependency boundary. No QEMU process can be created.
            import native_smoke
            with patch.object(native_smoke,'verify',side_effect=RuntimeError('native preflight reached')), \
                 patch.object(native_smoke.subprocess,'Popen',side_effect=AssertionError('host model forbids VM spawn')):
                with self.assertRaisesRegex(RuntimeError,'native preflight reached'):
                    native_smoke.run(*args,**kwargs)
            if fail is True:raise ValueError('declared host guest rejection')
            calls.append(stage)
            (stage/'native-serial.log').write_text('NATIVE HOST-TEST call='+str(len(calls))+'\n')
            (stage/'native-qemu-command.json').write_text('{"host_model_only": true}\n')
            if fail=='after-output':raise ValueError('declared host guest rejection')
        with owned_campaign_outputs() as roots:
            with ExitStack() as stack:
                for name,value in (('build_reader',baseline),('rust',rust),('image',image),
                                   ('prepare_native_fixture',fixture),('native_media_snapshot',lambda p:media),
                                   ('written_native_media_snapshot',lambda p:media),
                                   ('run',guest)):
                    stack.enter_context(patch.object(harness,name,side_effect=value))
                stack.enter_context(patch.object(af07,'prepare_engine',side_effect=engine))
                stack.enter_context(patch.object(af07,'recompose',side_effect=recompose))
                real_digest=af07.digest
                # Media contents are already an explicit double in this runner
                # model. Keep real sparse size/path preflight without hashing
                # tens of GiB of zeros unrelated to ordering/retention.
                stack.enter_context(patch.object(af07,'digest',side_effect=lambda p:
                    '0'*64 if Path(p).name=='native-namespace.raw' else real_digest(p)))
                for name in ('check_engine_trace','check_pool_cleanup_trace','check_namespace_trace',
                             'check_zpl_write_trace','check_zpl_recovery_trace','check_zpl_recovery_pair'):
                    stack.enter_context(patch.object(harness.runtime,name,return_value={}))
                stack.enter_context(patch.object(harness.runtime,'check_zpl_recovery_media',return_value=media))
                stack.enter_context(patch('openzfs_namespace.native_media_snapshot',return_value=media))
                stack.enter_context(patch('openzfs_namespace._native_media_snapshot',return_value=media))
                if fail:
                    with self.assertRaisesRegex(ValueError,'declared host guest rejection'):
                        harness.campaign(True,False,group)
                else:
                    harness.campaign(True,False,group)
            self.assertEqual(len(roots),1)
            record=json.loads((roots[0]/'results.json').read_text())
            self.assertTrue(record['cleanup']['stopped'])
            self.assertEqual(record['cleanup']['remaining'],'results.json only')
            self.assertTrue(all(not Path(p).exists() for p in record['owned_output_roots'] if Path(p)!=roots[0]))
            return record

    def test_all_images_prepare_before_guest_and_failure_never_advances(self):
        record=self.model_campaign(fail=True)
        self.assertEqual(len(record['cases']),1)
        self.assertEqual(record['cases'][0]['profile'],'lost-reply')
        self.assertEqual(record['cases'][0]['role'],'baseline')
        self.assertEqual(record['status'],'failed')

    def test_shared_reader_logs_capture_each_guest_before_reuse(self):
        record=self.model_campaign()
        self.assertEqual(record['status'],'pass')
        expected=[case+'/'+role for case in af07.CASES[1:]
                  for role in ('baseline','writer','reader')]
        self.assertEqual(list(record['serial']),expected)
        for index,key in enumerate(expected,1):
            self.assertEqual(record['serial'][key]['machine_witness']['lines'],
                             ['NATIVE HOST-TEST call='+str(index)])

    def test_failed_guest_retains_its_own_command_and_serial_before_cleanup(self):
        record=self.model_campaign(fail='after-output')
        self.assertEqual(len(record['cases']),1)
        self.assertEqual(record['status'],'failed')
        self.assertEqual(record['cases'][0]['qemu'],dict(host_model_only=True))
        self.assertNotIn('vm_run_returned',record['cases'][0])
        self.assertEqual(record['serial']['lost-reply/baseline']['machine_witness']['lines'],
                         ['NATIVE HOST-TEST call=1'])

    def test_cleanup_preserves_another_campaign_created_during_the_test(self):
        import shutil
        real=harness.tempfile.mkdtemp
        foreign=None
        try:
            with owned_campaign_outputs() as roots:
                ours=Path(harness.tempfile.mkdtemp(
                    prefix='thread-suite-service-runtime-zpl-pair-af07-',dir=ROOT/'zig-out'))
                # Bypass this invocation's spy, as a separate process would.
                foreign=Path(real(prefix='thread-suite-service-runtime-zpl-pair-af07-',dir=ROOT/'zig-out'))
                (foreign/'unrelated').write_text('preserve')
                self.assertEqual(roots,[ours])
            self.assertFalse(ours.exists())
            self.assertEqual((foreign/'unrelated').read_text(),'preserve')
        finally:
            if foreign is not None and foreign.is_dir():shutil.rmtree(foreign)
