# SPDX-License-Identifier: BSD-2-Clause
"""Consume sealed AF07 owner sources; verify real code, object, origins and cleanup."""
from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import uuid

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import fs_metadata_launch as launch


class MetadataLaunch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='aether-af07-launch-host-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.out=Path(cls.temp.name)
        cls.owner=launch.owner_intake()

    def command(self,args,expected=0):
        row=subprocess.run(list(map(str,args)),capture_output=True,text=True,timeout=60)
        self.assertEqual(row.returncode,expected,row.stdout+row.stderr)
        return row.stdout+row.stderr

    def test_exact_owner_and_resealed_dependency_coverage_and_abi_rejections(self):
        self.assertEqual(self.owner['object_sha256'],launch.OWNER_OBJECT)
        self.assertFalse(self.owner['native_acceptance'])
        for label,alter in (
            ('extra',lambda p:(p/'extra').write_text('extra')),
            ('symlink',lambda p:((p/'OWNER.md').unlink(),(p/'OWNER.md').symlink_to(launch.OWNER/'OWNER.md'))),
            ('dependency',lambda p:(p/'dependency.json').write_text('{}')),
            ('coverage',lambda p:self.alter_json(p/'build.json',{'native_executed':True})),
            ('abi',lambda p:(p/'abi/filesystem-engine.h').write_text('wrong')),
            ('source',lambda p:(p/'source/launch-metadata-owner.rs').write_text('wrong')),
            ('engine',lambda p:self.alter_engine_hash(p)),
            ('tool',lambda p:self.alter_tool_hash(p))):
            root=self.out/label;shutil.copytree(launch.OWNER,root);alter(root)
            # Resealing intentionally permits semantic guards past member hashes.
            members=sorted(p for p in root.rglob('*') if p.is_file() and p.name!='SHA256SUMS')
            (root/'SHA256SUMS').write_text(''.join(launch.metadata.digest(p)+'  '+str(p.relative_to(root))+'\n' for p in members))
            with patch.object(launch,'OWNER_SEAL',launch.metadata.digest(root/'SHA256SUMS')):
                with self.assertRaises(ValueError):launch.owner_intake(root)

    def alter_json(self,path,fields):
        row=json.loads(path.read_text());row.update(fields);path.write_text(json.dumps(row))

    def alter_engine_hash(self,root):
        path=root/'inputs.json';row=json.loads(path.read_text())
        row['producer_and_before']['producer']['user/storage/service-runtime/filesystem-engine.c']='0'*64
        path.write_text(json.dumps(row))

    def alter_tool_hash(self,root):
        path=root/'inputs.json';row=json.loads(path.read_text());row['tools']['rustc']['sha256']='0'*64
        path.write_text(json.dumps(row))

    def test_actual_owner_tests_native_rustc_identity_and_semantic_omissions(self):
        source=Path(self.owner['source']);rust=self.owner['tools']['rustc']['path']
        self.command([self.owner['tools']['rustfmt']['path'],'--edition=2021','--check',source,source.with_name('launch-metadata-owner-tests.rs')])
        host=self.out/'owner-host'
        self.command([rust,'--edition=2021','-Dwarnings','-Dunsafe_op_in_unsafe_fn','--test',source,'-o',host])
        self.assertIn('8 passed; 0 failed',self.command([host,'--test-threads=1']))
        native=self.out/'native.o'
        prefix=[rust,'--edition=2021','--target=x86_64-unknown-none','--crate-type=lib','--emit=obj',
                '-Cpanic=abort','-Copt-level=2','-Crelocation-model=static','-Cno-redzone=yes','-Ccodegen-units=1',
                '-Dwarnings','-Dunsafe_op_in_unsafe_fn']
        self.command(prefix+[source,'-o',native])
        self.assertEqual(launch.metadata.digest(native),launch.OWNER_OBJECT)
        clippy=self.owner['tools']['clippy-driver']['path']
        self.command([clippy,*prefix[1:],source,'-o',self.out/'clippy.o'])
        text=source.read_text().replace('#[path = "launch-metadata-owner-tests.rs"]',
                '#[path = '+json.dumps(str(source.with_name('launch-metadata-owner-tests.rs')))+']')
        for old,new in (
            ('            31,','            15,'),
            ('|| !progress_valid','|| (!progress_valid && false)'),
            ('|| service.requests == 0','|| (service.requests == 0 && false)'),
            ('&& service_unobserved {','&& { let _ = service_unobserved; true } {'),
            ('service.writer_close != 0','(service.writer_close != 0 && false)')):
            self.assertEqual(text.count(old),1)
            mutant=self.out/'mutant.rs';mutant.write_text(text.replace(old,new,1))
            self.command([rust,'--edition=2021','-Dunsafe_op_in_unsafe_fn','--test',mutant,'-o',host])
            self.assertIn('test result: FAILED.',self.command([host,'--test-threads=1'],101))

    def test_real_partial_and_final_maps_strong_definitions_and_old_service_exclusion(self):
        tools=self.owner['tools'];clang=tools['clang']['path'];lld=tools['lld']['path'];nm=tools['nm']['path']
        for variant in ('strong','weak','old'):
            directory=self.out/variant;directory.mkdir()
            for obj in set(launch.REQUIRED.values()):
                names=[k for k,v in launch.REQUIRED.items() if v==obj]
                if obj=='launch-engine.o' and variant=='old':names+=['aether_fs_directories_run']
                text='\n'.join(('__attribute__((weak)) ' if variant=='weak' and name=='main' else '')
                               +'void '+name+'(void) {}' for name in names)
                source=directory/(obj+'.c');source.write_text(text)
                self.command([clang,'--target=x86_64-linux-musl','-ffreestanding','-c',source,'-o',directory/obj])
            objects=[directory/name for name in sorted(set(launch.REQUIRED.values()))]
            for partial in (True,False):
                binary=directory/('partial.o' if partial else 'image.elf');mapping=binary.with_suffix('.map')
                self.command([lld,*(['-r'] if partial else ['-static','-e','main']),*objects,'-Map='+str(mapping),'-o',binary])
                symbols=self.command([nm,'--defined-only',binary])
                if variant=='strong':
                    launch.strong_symbols(symbols)
                    self.assertEqual(set(launch.origins(mapping.read_text(),launch.REQUIRED)),set(launch.REQUIRED))
                    with self.assertRaises(ValueError):launch.origins(mapping.read_text().replace('launch-metadata-owner.o','foreign.o'),launch.REQUIRED)
                else:
                    with self.assertRaises(ValueError):launch.strong_symbols(symbols)

    def test_failed_preparation_cleans_only_owned_output_and_keeps_old_selection(self):
        destination=ROOT/'.deps'/('fs-launch-af07-host-'+uuid.uuid4().hex)
        before=launch.old_launch_intake(launch.CURRENT)
        owned=[];real=launch.tempfile.mkdtemp
        def created(*args,**kwargs):
            name=real(*args,**kwargs);owned.append(Path(name));return name
        try:
            with patch.object(launch.tempfile,'mkdtemp',side_effect=created), \
                 patch.object(launch.metadata,'prepare_engine',side_effect=ValueError('declared host preparation rejection')):
                with self.assertRaisesRegex(ValueError,'declared host preparation rejection'):launch.build(destination)
            self.assertTrue(owned);self.assertTrue(all(not p.exists() for p in owned))
            self.assertEqual([p.name for p in destination.iterdir()],['build.json'])
            row=json.loads((destination/'build.json').read_text())
            self.assertEqual(row['status'],'failed');self.assertFalse(row['cleanup']['native_attempted'])
            self.assertEqual(launch.old_launch_intake(launch.CURRENT),before)
        finally:
            if destination.exists():shutil.rmtree(destination)

    def test_cli_never_starts_preparation_for_help_version_usage_or_invalid_destination(self):
        script=ROOT/'scripts/fs_metadata_launch.py'
        for args,status in ((['--help'],0),(['--version'],0),([],64),(['--bad\x1bflag'],64),
                            (['--output',str(self.out/'unowned')],1),(['--output',str(launch.CURRENT)],1)):
            row=subprocess.run([sys.executable,'-B',str(script),*args],capture_output=True,text=True,timeout=10)
            self.assertEqual(row.returncode,status,row.stdout+row.stderr)
            self.assertNotIn('\x1b',row.stderr)
            self.assertNotIn('[RUNNING]',row.stderr)
        self.assertFalse((self.out/'unowned').exists())
