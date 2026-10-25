# SPDX-License-Identifier: BSD-2-Clause
"""Pinned producer identity and envelope bounds; fixtures are intentionally inert."""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('init_consumer',ROOT/'tests/native-init.py')
consumer=importlib.util.module_from_spec(spec);spec.loader.exec_module(consumer)

class InitInputs(unittest.TestCase):
    def fixture(self,root,reserved=0):
        (root/'init/positive').mkdir(parents=True,exist_ok=True)
        (root/'producer-sources.tar.gz').write_bytes(b'inert-not-an-archive')
        raw=struct.pack('<8sIIII',b'AENIN001',1,1,1,reserved)+bytes(32)+b'abc'
        (root/'init/positive/native-c.bin').write_bytes(raw)
        (root/'init/helper1.elf').write_bytes(b'a');(root/'init/helper2.elf').write_bytes(b'b')
        report=dict(status='pass',profile='init',cases=[dict(name='positive',envelope_sha256=hashlib.sha256(raw).hexdigest())])
        (root/'init/results.json').write_text(json.dumps(report))
        summary=dict(source_archive_sha256=consumer.sha(root/'producer-sources.tar.gz'),
                     suites=dict(init=dict(report_sha256=consumer.sha(root/'init/results.json'))))
        (root/'summary.json').write_text(json.dumps(summary))
        return consumer.sha(root/'summary.json')

    def test_pin_and_producer_correspondence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);pin=self.fixture(root)
            self.assertEqual(consumer.validate(root,pin)[2:],(1,1))
            with self.assertRaisesRegex(ValueError,'pin mismatch'):consumer.validate(root,'0'*64)
            (root/'init/helper1.elf').write_bytes(b'wrong')
            with self.assertRaisesRegex(ValueError,'correspondence'):consumer.validate(root,pin)

    def test_archive_report_envelope_and_reserved_field_reject(self):
        for name in ('producer-sources.tar.gz','init/results.json','init/positive/native-c.bin','reserved'):
            with self.subTest(name=name),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);pin=self.fixture(root,reserved=1 if name=='reserved' else 0)
                if name!='reserved':(root/name).write_bytes((root/name).read_bytes()+b'changed')
                with self.assertRaises(ValueError):consumer.validate(root,pin)

    def test_retained_sampling_profile_preserves_runtime_bounds(self):
        flags = consumer.compiler_profile(Path('/private/tmp/fixture with spaces/native'))
        self.assertEqual(consumer.BUILD_PROFILE, 'retained-sampling-v1')
        self.assertEqual(flags, ['-C', 'opt-level=s', '-C', 'panic=abort',
                                '-C', 'relocation-model=static',
                                '--remap-path-prefix=/private/tmp/fixture with spaces/native=sys-init/prototypes/native-supervisor'])
        self.assertNotIn('opt-level=2', flags)

    def test_explicit_profile_and_size_boundaries(self):
        for magic,profile,large,composed,limit in ((b'AENIN001','init',False,False,4096),
                                          (b'AENIN002','init-large',True,False,8192),
                                          (b'AENIN003','init-composed',False,True,16384)):
            for length in (0,1,4096,4097,8192,8193,16384,16385):
                with self.subTest(magic=magic,length=length),tempfile.TemporaryDirectory() as tmp:
                    root=Path(tmp);self.fixture(root)
                    raw=struct.pack('<8sIIII',magic,1,1,length,0)+bytes(32)+b'ab'+bytes(length)
                    (root/'init/positive/native-c.bin').write_bytes(raw)
                    report=dict(status='pass',profile=profile,cases=[dict(name='positive',envelope_sha256=hashlib.sha256(raw).hexdigest())])
                    (root/'init/results.json').write_text(json.dumps(report))
                    summary=json.loads((root/'summary.json').read_text())
                    if composed:summary.update(schema='sys-init-init-composed-intake-v1',native_profile='AENIN003',abi=16,supervisor_limit=16384,stack_bytes=4096)
                    summary['suites']['init']['report_sha256']=consumer.sha(root/'init/results.json')
                    (root/'summary.json').write_text(json.dumps(summary));pin=consumer.sha(root/'summary.json')
                    if 0<length<=limit:
                        self.assertEqual(consumer.validate(root,pin,large,composed)[2:],(1,1))
                    else:
                        with self.assertRaisesRegex(ValueError,'bounded selected'):consumer.validate(root,pin,large,composed)
                    with self.assertRaisesRegex(ValueError,'incomplete producer'):consumer.validate(root,pin,not large)

    def test_profile_report_cannot_relabel_legacy_envelope(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.fixture(root)
            report=json.loads((root/'init/results.json').read_text());report['profile']='init-large'
            (root/'init/results.json').write_text(json.dumps(report))
            summary=json.loads((root/'summary.json').read_text())
            summary['suites']['init']['report_sha256']=consumer.sha(root/'init/results.json')
            (root/'summary.json').write_text(json.dumps(summary))
            with self.assertRaisesRegex(ValueError,'bounded selected'):
                consumer.validate(root,consumer.sha(root/'summary.json'),True)

    def test_composed_cannot_relabel_legacy_or_omit_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);pin=self.fixture(root)
            with self.assertRaisesRegex(ValueError,'invalid composed intake'):
                consumer.validate(root,pin,composed=True)
            with self.assertRaisesRegex(ValueError,'select one'):
                consumer.validate(root,pin,large=True,composed=True)
            summary=json.loads((root/'summary.json').read_text())
            summary.update(schema='sys-init-init-composed-intake-v1',native_profile='AENIN003',abi=16,supervisor_limit=16384,stack_bytes=4096)
            report=json.loads((root/'init/results.json').read_text());report['profile']='init-composed'
            (root/'init/results.json').write_text(json.dumps(report))
            summary['suites']['init']['report_sha256']=consumer.sha(root/'init/results.json')
            (root/'summary.json').write_text(json.dumps(summary))
            with self.assertRaisesRegex(ValueError,'bounded selected'):
                consumer.validate(root,consumer.sha(root/'summary.json'),composed=True)

    def test_cli_profiles_are_exclusive_before_input_access(self):
        result=subprocess.run([sys.executable,str(ROOT/'tests/native-init.py'),'--init-large','--init-composed',
                               '--producer','/missing','--summary-pin','0'*64,'--work','/missing'],capture_output=True,timeout=10)
        self.assertEqual(result.returncode,64)
        self.assertIn(b'not allowed with argument',result.stderr)
        self.assertEqual(result.stdout,b'')
