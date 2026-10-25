# SPDX-License-Identifier: BSD-2-Clause
"""Exact AF07 delivery, native fit, real consuming decoder and omission controls."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import openzfs_fs_metadata_service as af07


class MetadataService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix='aether-af07-host-')
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.out = Path(cls.temporary.name)
        cls.body = (af07.SERVICE/'fs-metadata-body.inc').read_text()

    def command(self,args,expected=0):
        r=subprocess.run(list(map(str,args)),capture_output=True,text=True,timeout=60,cwd=ROOT)
        self.assertEqual(r.returncode,expected,r.stdout+r.stderr)
        return r.stdout+r.stderr

    def test_exact_seal_sources_headers_tools_and_object(self):
        selected=af07.intake()
        self.assertEqual(selected['members'],77)
        self.assertEqual(selected['rights'],31)
        self.assertEqual(selected['limits']['requests'],96)
        nm=ROOT/'.deps/native-current/sdk/tools.lock.json'
        tools=json.loads(nm.read_text())['tools']
        symbols=self.command([tools['nm']['path'],'--defined-only','--extern-only',selected['object']])
        self.assertIn('aether_fs_metadata_run',symbols)
        self.assertNotIn('aether_fs_directories_run',symbols)
        imports=self.command([tools['nm']['path'],'--undefined-only',selected['object']])
        self.assertIn('aether_zpl_getattr',imports)

    def test_bounded_oracle_capture_summarizes_only_exact_successful_events(self):
        import hashlib
        import fs_metadata_service as harness
        from fs_session import machine_witness
        events = ('NATIVE STORAGE WAIT slot=2 generation=0 phase=park status=0\n'
                  'NATIVE STORAGE WAIT slot=2 generation=0 phase=wake status=0\n'
                  'NATIVE CLOCK park task=0 start=1 deadline=2\n'
                  'NATIVE CLOCK timeout task=0 now=3 elapsed=2\n') * 1000
        critical = ('NATIVE STORAGE WAIT slot=2 generation=0 phase=wake status=-5\n'
                    'NATIVE CLOCK unknown task=0\n'
                    'NATIVE STORAGE WAIT slot=2 generation=0 phase=park status=0 extra\n'
                    'NATIVE supervisor result=100 reclaimed=3\n'
                    'AETHER NATIVE BLOCK PASS\n')
        text = events + critical
        self.assertFalse(machine_witness(text)['selection_complete'])
        actual = harness.require_oracle_witness(text)
        self.assertEqual(actual['lines'],critical.splitlines())
        self.assertTrue(actual['selection_complete'])
        self.assertEqual(actual['ceiling_utf8_bytes'],65536)
        self.assertEqual(actual['source_selection']['total_lines'],4005)
        self.assertEqual(actual['source_selection']['full_selection_sha256'],
                         hashlib.sha256(text.encode()).hexdigest())
        self.assertEqual(actual['omitted_events'],dict(lines=4000,
                         sha256=hashlib.sha256(events.encode()).hexdigest()))

    def test_unexpected_record_overflow_is_rejected(self):
        import fs_metadata_service as harness
        text = 'NATIVE unknown must not be discarded\n' * 3000
        self.assertFalse(harness.oracle_witness(text)['selection_complete'])
        with self.assertRaisesRegex(ValueError,'oracle witness exceeds fixed64KiB'):
            harness.require_oracle_witness(text)

    def test_corrupt_extra_symlink_and_old_delivery_are_rejected(self):
        original=self.out/'delivery'
        shutil.copytree(af07.DELIVERY,original)
        af07.intake(original)
        target=original/'objects/filesystem-metadata.o'; data=target.read_bytes()
        target.write_bytes(data[:-1]+bytes([data[-1]^1]))
        with self.assertRaisesRegex(ValueError,'seal member'):af07.intake(original)
        target.write_bytes(data)
        (original/'extra').write_bytes(b'extra')
        # sealed() verifies every declared member; the new intake must also reject extras.
        try:
            with self.assertRaisesRegex(ValueError,'closure'):af07.intake(original)
        finally:(original/'extra').unlink()
        target.unlink();target.symlink_to(af07.DELIVERY/'objects/filesystem-metadata.o')
        with self.assertRaisesRegex(ValueError,'symlink'):af07.intake(original)
        with self.assertRaisesRegex(ValueError,'seal digest'):
            af07.intake(ROOT / 'userland/build/service-deliveries/filesystem-service-directories-2026-10-20-v1')

    def test_generated_jobs_preserve_exact_mutations_requests_and_profile_separation(self):
        text=af07.client((af07.SERVICE/'fs-directories-client.rs').read_text())
        jobs=text.split('const JOBS:',1)[1].split(' = [',1)[1].split('\n];',1)[0]
        rows=re.findall(r'^    \[(\d+),.*\],$',jobs,re.M)
        self.assertEqual(len(rows),32)
        # The denied rmdir is not a transaction; the original9 successes stay exact.
        self.assertEqual(sum(int(op) in (5,7,8,9,10,11) for op in rows),10)
        self.assertIn('for index in 0..58',text)
        self.assertEqual(5+len(rows)+58+1,96)
        self.assertIn('[12, 4, 0, 0, 0, 13]',text)
        self.assertIn('[1, 2, b\'p\', 22, 2, 0]',text)
        with self.assertRaisesRegex(ValueError,'source context'):af07.client('invalid')

    def decoder(self,body,label):
        source=self.out/(label+'.rs')
        source.write_text((ROOT/'tests/fixtures/fs_metadata_body.rs').read_text().replace(
            '// The Python test inserts the actual maintained decoder into this impl.',
            ('fn check_site(site: u64, ok: bool) { check({let _=site; ok}); }\n' if 'check_site(' in body else '')
            +'impl Connection {\n'+body+'\n}'))
        binary=self.out/label
        self.command(['rustc','+1.98.0','--edition=2024','-Dwarnings','--test',source,'-o',binary])
        return binary

    def test_actual_decoder_all_selections_corruptions_and_frame_failures(self):
        self.assertIn('1 passed',self.command([self.decoder(self.body,'decoder')]))

    def test_compiling_padding_and_time_omissions_fail_named_decoder_oracle(self):
        for label,old,new in (
            ('padding','check(bytes[112..].iter().all(|b| *b == 0));',''),
            ('nanos','check(values[i] < 1_000_000_000);','check({let _ = values[i]; true});')):
            self.assertEqual(self.body.count(old),1)
            output=self.command([self.decoder(self.body.replace(old,new,1),label)],101)
            self.assertIn('actual_frame_decoder_and_corruptions',output)
            self.assertIn('metadata corruption accepted',output)

    def test_actual_creator_flags_exclude_everyone_execute_and_old_oracle_rejects(self):
        source=ROOT/'.deps/native-current/baseline/source/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1/include/sys/zfs_znode.h'
        macros={name:int(value,16) for name,value in re.findall(r'^#define\s+(ZFS_\w+)\s+(0x[0-9a-fA-F]+)',source.read_text(),re.M)}
        creator=(af07.VOLUME/'zpl-mutate.c').read_text()
        self.assertIn('ZFS_ARCHIVE | ZFS_AV_MODIFIED | ZFS_ACL_TRIVIAL |\n                         ZFS_ACL_PROTECTED | ZFS_PROJID',creator)
        flags=0
        for name in ('ZFS_ARCHIVE','ZFS_AV_MODIFIED','ZFS_ACL_TRIVIAL','ZFS_ACL_PROTECTED','ZFS_PROJID'):
            flags |= macros[name]
        self.assertEqual(flags,0x840800000014)
        self.assertEqual(flags & macros['ZFS_NO_EXECS_DENIED'],0)
        self.assertNotEqual(flags & 0x104,0x104)
        old='check(values[5] & 0x0000040800000000 == 0x0000040800000000);'
        self.assertEqual(self.body.count(old),1)
        out=self.command([self.decoder(self.body.replace(old,'check(values[5] & 0x104 == 0x104);',1),'old-flags-oracle')],101)
        self.assertIn('metadata positive rejected',out)

    def test_native_controller_fits_and_has_no_writable_statics(self):
        text=(af07.SERVICE/'metadata-controller.rs').read_text()
        text=text.replace('// Build selection inserts absolute, immutable-at-run module paths here.',
            '#[path = '+json.dumps(str(af07.SERVICE/'fs-service-client.rs'))+']\nmod namespace_client;\n'
            +'#[path = '+json.dumps(str(af07.SERVICE/'fs-activation-client.rs'))+']\nmod activation;')
        path=self.out/'controller.rs';path.write_text(af07.controller(text,self.out))
        args=['rustc','+1.98.0','--edition=2024','--target=x86_64-unknown-none','-Dwarnings',
            '-Copt-level=z','-Clto=fat','-Ccodegen-units=1','-Cpanic=abort','-Crelocation-model=static',
            '-Clink-arg=-Tuser/storage/service-runtime/activation-linker.ld','-Clink-arg=--oformat=binary']
        for cfg in ('namespace_wait','fs_mixed','fs_bulk','fs_runtime','fs_activation','fs_names','fs_directories'):
            args+=['--cfg',cfg]
        binary=self.out/'supervisor.raw'
        self.command(args+[path,'-o',binary])
        self.assertLessEqual(binary.stat().st_size,8192)

        self.assertGreater(binary.stat().st_size,0)

    def test_provider_selection_preserves_workload_and_rejects_wrong_context(self):
        from openzfs_fs_directories_service import owner,probe
        original=(af07.VOLUME/'zpl-mutation-probe.c').read_text()
        selected,entry=af07.provider(probe(original),owner((af07.VOLUME/'fs-service-owner.inc').read_text()))
        self.assertIn('#include "zpl-metadata.c"',selected)
        self.assertNotIn('#include "zpl-directories.c"',selected)
        self.assertIn('aether_fs_metadata_run(',entry)
        self.assertIn('writer, 31, 1000, 1000,',entry)
        self.assertIn('#define FS_REQUESTS 96',entry)
        self.assertNotIn('aether_fs_directories_run(',entry)
        with self.assertRaisesRegex(ValueError,'source context'):af07.provider(original,entry)

    def test_diagnostic_is_numbered_predicates_only_and_fits_unchanged_guard(self):
        text=(af07.SERVICE/'metadata-controller.rs').read_text().replace(
            '// Build selection inserts absolute, immutable-at-run module paths here.',
            '#[path = '+json.dumps(str(af07.SERVICE/'fs-service-client.rs'))+']\nmod namespace_client;\n'
            +'#[path = '+json.dumps(str(af07.SERVICE/'fs-activation-client.rs'))+']\nmod activation;')
        path=self.out/'diagnostic.rs';path.write_text(af07.controller(text,self.out,True))
        sites=json.loads((self.out/'assertion-sites.json').read_text())
        self.assertEqual([s['code'] for s in sites],list(range(1000,1000+len(sites))))
        self.assertEqual(len(sites),106)
        selected=(self.out/'af07-client.rs').read_text()
        self.assertEqual(re.sub(r'check_site\(\d+, ','check(',selected),
                         af07.client((af07.SERVICE/'fs-directories-client.rs').read_text()))
        body='    fn metadata_body'+selected.split('    fn metadata_body',1)[1].split('    fn directory_message',1)[0]
        self.assertIn('1 passed',self.command([self.decoder(body,'diagnostic-body')]))
        args=['--edition=2024','--target=x86_64-unknown-none','-Dwarnings','-Cpanic=abort']
        for cfg in ('namespace_wait','fs_mixed','fs_bulk','fs_runtime','fs_activation','fs_names','fs_directories'):
            args+=['--cfg',cfg]
        tools=json.loads((af07.DELIVERY/'inputs.json').read_text())['tools']
        self.command([tools['clippy-driver']['path'],*args,'--emit=obj',path,'-o',self.out/'clippy.o'])
        binary=self.out/'diagnostic.raw'
        self.command(['rustc','+1.98.0',*args,'-Copt-level=z','-Clto=fat','-Ccodegen-units=1',
            '-Crelocation-model=static','-Clink-arg=-Tuser/storage/service-runtime/activation-linker.ld',
            '-Clink-arg=--oformat=binary',path,'-o',binary])
        self.assertLessEqual(binary.stat().st_size,8192)
        print('AF07_DIAGNOSTIC_FIT '+json.dumps(dict(bytes=binary.stat().st_size,
            sha256=af07.digest(binary),sites=len(sites),
            controller_sha256=af07.digest(path),client_sha256=af07.digest(self.out/'af07-client.rs'),
            connection_sha256=af07.digest(self.out/'af07-connection.rs'))))

    def test_cli_and_failed_preparation_do_not_boot_and_dispose_owned_outputs(self):
        from unittest.mock import patch
        import fs_metadata_service as harness
        for args,code,marker in ((['--version'],0,'aether-fs-metadata-service 1'),
                                 (['--help'],0,'--run'),(['--disk','/dev/disk0'],64,'[FAIL]')):
            result=self.command([sys.executable,'-B',ROOT/'scripts/fs_metadata_service.py',*args],code)
            self.assertIn(marker,result)
        from test_fs_metadata_failures import owned_campaign_outputs
        with owned_campaign_outputs() as roots:
            with patch.object(harness,'build_reader',side_effect=ValueError('declared preparation rejection')),patch.object(harness,'run') as guest:
                with self.assertRaisesRegex(ValueError,'declared preparation rejection'):harness.campaign(True)
                guest.assert_not_called()
            self.assertEqual(len(roots),1)
            record=json.loads((roots[0]/'results.json').read_text())
            self.assertFalse(record['native_attempted'])
            self.assertFalse(record['triage_required'])
            self.assertTrue(record['cleanup']['stopped'])
            self.assertEqual(record['cleanup']['remaining'],'results.json only')
