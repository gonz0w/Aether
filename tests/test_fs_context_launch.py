# SPDX-License-Identifier: BSD-2-Clause
"""AF08 input identity/profile rejection; no guest or disk operations."""
import copy
import json
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import fs_context_launch as c


class ContextIntake(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='aether-af08-intake-')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        (self.root/'filesystem.elf').write_bytes(b'not-an-ELF: closure/loader replaced only in this field-validation test')
        source=self.root/'input';source.write_bytes(b'frozen')
        self.members={name:'a'*64 for name in ['filesystem.elf','SOURCE.md','preparation.json',
            'notices/LICENSE','notices/openzfs/LICENSE','notices/openzfs/COPYRIGHT','notices/openzfs/NOTICE','notices/COPYRIGHT.musl']}
        self.record=dict(schema=c.SCHEMA,status='pass',executed=False,protocol='AFSRPC08',
            owner_manifest_sha256=c.launch.OWNER_SEAL,baseline_service_manifest_sha256=c.metadata.SEAL,
            elf_sha256='a'*64,elf_bytes=(self.root/'filesystem.elf').stat().st_size,
            origins={k:'/owned/'+v for k,v in c.REQUIRED.items()},structural_loader='ELF structural pages=1',
            limits=dict(mutations=9,requests=96,engine_pages=8192,writer_seconds=60,writer_ticks=6000,reader_seconds=30,reader_ticks=3000),
            local_frames={n:'context\t64\tstatic\n' for n in c.launch.FRAME_FILES},
            inputs={str(source):c.digest(source)},commands=[dict(status='pass')],qualification_sha256='b'*64,service_object_sha256='c'*64)
    def intake(self,record=None,members=None):
        (self.root/'build.json').write_text(json.dumps(self.record if record is None else record))
        with patch.object(c.launch,'closure',return_value=(self.root,self.members if members is None else members)):
            return c.intake(self.root,'d'*64)
    def test_explicit_af08_result_is_not_native_acceptance(self):
        result=self.intake();self.assertEqual(result['protocol'],'AFSRPC08');self.assertFalse(result['native_acceptance']);self.assertFalse(result['executed'])
    def test_old_version_execution_false_claims_and_raised_limits_reject(self):
        for key,value in [('schema',c.launch.SCHEMA),('protocol','AFSRPC07'),('executed',True),('status','failed'),('owner_manifest_sha256','f'*64),('service_object_sha256','bad')]:
            row=copy.deepcopy(self.record);row[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.intake(row)
        for key in self.record['limits']:
            row=copy.deepcopy(self.record);row['limits'][key]+=1
            with self.subTest(limit=key),self.assertRaises(ValueError):self.intake(row)
    def test_missing_c_origin_notices_and_failed_command_reject(self):
        for symbol in c.REQUIRED:
            row=copy.deepcopy(self.record);del row['origins'][symbol]
            with self.subTest(symbol=symbol),self.assertRaises(ValueError):self.intake(row)
        row=copy.deepcopy(self.record);row['commands'][0]['status']='timeout'
        with self.assertRaises(ValueError):self.intake(row)
        members=dict(self.members);del members['notices/openzfs/LICENSE']
        with self.assertRaises(ValueError):self.intake(members=members)
    def test_changed_source_and_dynamic_or_excessive_stack_reject(self):
        source=next(iter(self.record['inputs']));Path(source).write_bytes(b'changed')
        with self.assertRaises(ValueError):self.intake()
        Path(source).write_bytes(b'frozen')
        for frame in ['context\t8193\tstatic\n','context\t64\tdynamic\n','']:
            row=copy.deepcopy(self.record);row['local_frames']['metadata-provider.su']=frame
            with self.subTest(frame=frame),self.assertRaises(ValueError):self.intake(row)
    def test_private_cli_streams_versions_usage_and_escaped_paths(self):
        root=Path(__file__).resolve().parents[1]
        for script in ('scripts/fs_context_launch.py','scripts/fs_context_inputs.py','userland/experiments/filesystem-service/check-directory-contexts.py'):
            for args,code in [(['--help'],0),(['--version'],0),(['--unknown'],64)]:
                with self.subTest(script=script,args=args):
                    run=subprocess.run([sys.executable,'-B',root/script,*args],capture_output=True,timeout=15)
                    self.assertEqual(run.returncode,code,run.stderr)
                    self.assertTrue(run.stdout if code==0 else run.stderr)
                    self.assertNotIn(b'\x1b',run.stdout+run.stderr)
        run=subprocess.run([sys.executable,'-B',root/'scripts/fs_context_launch.py','--output','/tmp/wrong\nname','--checked','/tmp/wrong'],capture_output=True,timeout=15)
        self.assertEqual(run.returncode,2);self.assertIn(b'[BLOCKED]',run.stderr);self.assertNotIn(b'wrong\nname',run.stderr)


if __name__=='__main__':unittest.main()
