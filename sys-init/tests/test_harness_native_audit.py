# SPDX-License-Identifier: BSD-2-Clause
"""Mutation checks for historical evidence completeness and semantic oracles."""
import copy
import hashlib
import struct
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('native_audit', ROOT/'scripts/check-native-evidence.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

class NativeAuditTests(unittest.TestCase):
    def setUp(self):
        self.entry = json.loads((ROOT/'docs/native-coverage.json').read_text())['bundles'][4]
        self.report = json.loads((ROOT/self.entry['directory']/'results.json').read_text())

    def test_complete_metadata(self):
        self.assertEqual(len(audit.check_cases(self.report,self.entry)),4)

    def test_missing_duplicate_wrong_and_forged_cases(self):
        for change in ('missing','duplicate','wrong_exit','boolean_exit','false_pass'):
            r = copy.deepcopy(self.report)
            if change == 'missing': r['cases'].pop()
            if change == 'duplicate': r['cases'][1] = r['cases'][0]
            if change == 'wrong_exit': r['cases'][0]['smoke_exit'] = 1
            if change == 'boolean_exit': r['cases'][0]['smoke_exit'] = False
            if change == 'false_pass': r['result'] = 'running'
            with self.subTest(change=change), self.assertRaises(ValueError): audit.check_cases(r,self.entry)

    def test_timeout_missing_command_and_failed_build(self):
        for change in ('timeout','missing','failed'):
            r = copy.deepcopy(self.report)
            if change == 'timeout': r['commands'][0]['outcome'] = 'timeout'
            if change == 'missing': r['commands'].pop()
            if change == 'failed': r['commands'][0]['exit'] = 1
            with self.subTest(change=change), self.assertRaises(ValueError): audit.check_cases(r,self.entry)

    def test_manifest_pin_content_and_escape_reject(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'payload').write_text('inert')
            (root/'SHA256SUMS.json').write_text(json.dumps({'payload':audit.sha(root/'payload')}))
            pin = audit.sha(root/'SHA256SUMS.json')
            audit.verify_manifest(root,pin)
            with self.assertRaises(ValueError): audit.verify_manifest(root,'0'*64)
            (root/'payload').write_text('changed')
            with self.assertRaises(ValueError): audit.verify_manifest(root,pin)
            for name in ('../outside','/outside','a/../payload'):
                with self.assertRaises(ValueError): audit.inside(root,name)

    def test_pinned_but_wrong_semantic_serial_rejects(self):
        # Re-pin a minimal inert bundle to prove digests alone do not pass a control.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); bundle = root/'bundle'; (bundle/'clients/control').mkdir(parents=True)
            sdk_entry = json.loads((ROOT/'docs/native-coverage.json').read_text())['bundles'][0]
            (bundle/'sdk-evidence.json').write_bytes((ROOT/sdk_entry['directory']/'sdk-evidence.json').read_bytes())
            native = b'AENATC01' + bytes(32) + b'inert-image'
            native_hash = hashlib.sha256(native).hexdigest()
            envelope = struct.pack('<8sII', b'AENFD001', 11, 16) + native[8:] + b'inert-supervisor'
            (bundle/'clients/control/supervised.bin').write_bytes(envelope)
            envelope_hash = audit.sha(bundle/'clients/control/supervised.bin')
            (bundle/'control-serial.log').write_text('AETHER PANIC: native C profile rejected\n')
            (bundle/'clients/control/supervisor.raw').write_bytes(b'inert-supervisor')
            build = dict(native_sha256=native_hash,envelope_sha256=envelope_hash,
                         supervisor_sha256=audit.sha(bundle/'clients/control/supervisor.raw'),
                         variant='fixture',command=['fixture'])
            (bundle/'clients/control/build.json').write_text(json.dumps(build))
            case = dict(image_sha256=envelope_hash,case='control',result='pass',smoke_exit=1,marker='AETHER PANIC: native C profile rejected',
                        serial_sha256=audit.sha(bundle/'control-serial.log'),envelope_sha256=envelope_hash)
            report = dict(schema='fixture',result='pass',sources_unchanged=True,native_memory=False,smp=False,
                          native_sha256=native_hash,sdk_receipt_sha256=audit.sha(bundle/'sdk-evidence.json'),
                          cases=[case],commands=[dict(argv=['fixture'],exit=c) for c in (0,0,1)])
            (bundle/'results.json').write_text(json.dumps(report))
            manifest = {str(p.relative_to(bundle)):audit.sha(p) for p in bundle.rglob('*') if p.is_file()}
            (bundle/'SHA256SUMS.json').write_text(json.dumps(manifest))
            entry = dict(directory='bundle',schema='fixture',manifest_sha256=audit.sha(bundle/'SHA256SUMS.json'),
                         cases=[dict(name='control',smoke_exit=1,marker=case['marker'],assertion='expected assertion')])
            with self.assertRaisesRegex(ValueError,'assertion missing'): audit.audit_bundle(root,entry)

class NativeInitAuditTests(unittest.TestCase):
    def setUp(self):
        self.entry = next(e for e in json.loads((ROOT/'docs/native-coverage.json').read_text())['bundles']
                          if e['schema'] == 'sys-init-native-init-v1')
        self.directory = ROOT/self.entry['directory']
        self.report = json.loads((self.directory/'results.json').read_text())

    def test_complete_metadata(self):
        self.assertEqual(len(audit.check_init_cases(self.report, self.entry)), 7)

    def test_missing_duplicate_forged_and_interrupted(self):
        for change in ('missing', 'duplicate', 'marker', 'panic', 'command', 'timeout', 'boolean'):
            r = copy.deepcopy(self.report)
            if change == 'missing': r['cases'].pop()
            if change == 'duplicate': r['cases'][1] = r['cases'][0]
            if change == 'marker': r['cases'][0]['marker'] = 'AETHER NATIVE INIT CLOSED'
            if change == 'panic': r['cases'][1]['expected_panic'] = None
            if change == 'command': r['commands'].pop()
            if change == 'timeout': r['commands'][0]['outcome'] = 'timeout'
            if change == 'boolean': r['commands'][0]['exit'] = False
            with self.subTest(change=change), self.assertRaises(ValueError):
                audit.check_init_cases(r, self.entry)

    def test_exact_serial_outcomes_and_order(self):
        for wanted in self.entry['cases']:
            lines = (self.directory/'cases'/wanted['name']/'native-serial.log').read_text().splitlines()
            audit.check_init_serial(lines, wanted)
            for changed in ([s for s in lines if s != wanted['assertion']],
                            lines + ['AETHER NATIVE INIT PASS'],
                            list(reversed(lines)),
                            [s.replace('reclaimed=3', 'reclaimed=2').replace('queued=2', 'queued=0')
                             .replace('result=821', 'result=803').replace('result=822', 'result=803')
                             for s in lines]):
                with self.subTest(case=wanted['name']), self.assertRaises(ValueError):
                    audit.check_init_serial(changed, wanted)

    def test_envelope_bounds(self):
        import struct
        raw = (self.directory/'cases/policy/native-c.bin').read_bytes()
        for changed in (raw[:55], raw+b'x', b'WRONG001'+raw[8:],
                        raw[:20]+struct.pack('<I', 1)+raw[24:]):
            with self.assertRaises(ValueError): audit.init_envelope(changed)

    def test_repinned_artifact_correspondence(self):
        import shutil
        # Re-pin mutations to exercise semantic checks beyond manifest integrity.
        for change, message in (('helper', 'ELF correspondence'),
                                ('consumer', 'consumer envelope correspondence'),
                                ('archive', 'producer receipt'),
                                ('serial', 'assertion')):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp); bundle = root/'bundle'
                shutil.copytree(self.directory, bundle)
                report = copy.deepcopy(self.report)
                if change == 'helper':
                    p = bundle/'producer/init/helper1.elf'; p.write_bytes(p.read_bytes()+b'x')
                if change == 'consumer':
                    p = bundle/'cases/policy/native-c.bin'; raw = bytearray(p.read_bytes()); raw[56] ^= 1
                    p.write_bytes(raw); report['cases'][0]['envelope_sha256'] = audit.sha(p)
                if change == 'archive':
                    p = bundle/'producer/producer-sources.tar.gz'; p.write_bytes(b'inert')
                if change == 'serial':
                    p = bundle/'cases/policy/native-serial.log'
                    p.write_text(p.read_text().replace('reclaimed=3', 'reclaimed=2'))
                    report['cases'][0]['serial_sha256'] = audit.sha(p)
                (bundle/'results.json').write_text(json.dumps(report))
                manifest = json.loads((bundle/'SHA256SUMS.json').read_text())
                manifest = {name:audit.sha(bundle/name) for name in manifest}
                (bundle/'SHA256SUMS.json').write_text(json.dumps(manifest))
                entry = dict(self.entry, directory='bundle', manifest_sha256=audit.sha(bundle/'SHA256SUMS.json'))
                with self.assertRaisesRegex(ValueError, message): audit.audit_bundle(root, entry)

class NativeLargeProfileAuditTests(unittest.TestCase):
    def test_explicit_profile_bounds_and_mixed_markers(self):
        import struct
        for profile,limit in [('AENIN001',4096),('AENIN002',8192)]:
            for size in (0,4096,4097,8192,8193):
                raw=struct.pack('<8sIIII',profile.encode(),1,1,size,0)+bytes(32)+b'ab'+bytes(size)
                with self.subTest(profile=profile,size=size):
                    if 0<size<=limit:self.assertEqual(len(audit.init_envelope(raw,profile)[3]),size)
                    else:
                        with self.assertRaises(ValueError):audit.init_envelope(raw,profile)
                    with self.assertRaises(ValueError):audit.init_envelope(raw,'AENIN002' if profile=='AENIN001' else 'AENIN001')
        wanted=dict(expected_panic=None,marker='AETHER NATIVE INIT LARGE PASS',assertion='NATIVE supervisor result=100 reclaimed=3')
        lines=[wanted['assertion'],wanted['marker']]
        audit.check_init_serial(lines,wanted)
        with self.assertRaises(ValueError):audit.check_init_serial(lines+['AETHER NATIVE INIT PASS'],wanted)

    def test_catalog_profile_is_explicit_and_closed(self):
        entry=next(e for e in json.loads((ROOT/'docs/native-coverage.json').read_text())['bundles'] if e['schema']=='sys-init-native-init-v1')
        report=json.loads((ROOT/entry['directory']/'results.json').read_text())
        report['native_profile']='AENIN002'
        with self.assertRaises(ValueError):audit.check_init_cases(report,entry)
        entry['native_profile']='AENIN002';audit.check_init_cases(report,entry)
        entry['native_profile']='unknown';report['native_profile']='unknown'
        with self.assertRaises(ValueError):audit.check_init_cases(report,entry)
