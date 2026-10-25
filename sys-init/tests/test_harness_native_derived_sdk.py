# SPDX-License-Identifier: BSD-2-Clause
import copy
import hashlib
import unittest
import test_harness_native_audit as fixtures


audit = fixtures.audit


class DerivedSDKTests(unittest.TestCase):
    def fixture(self):
        files={'worker/inputs/a':b'input','worker/worker.elf':b'inert-elf'}
        files['worker/native-c.bin']=b'AENATC01'+bytes(32)+files['worker/worker.elf']
        digest=lambda p:hashlib.sha256(files[p]).hexdigest()
        sdk={'inputs':{'inputs/a':digest('worker/inputs/a')},
             'artifacts':[{'name':'startup','sha256':digest('worker/worker.elf')}],
             'envelope_sha256':digest('worker/native-c.bin')}
        report={'native_sha256':sdk['envelope_sha256']}
        return files,digest,sdk,report

    def test_contradictory_claims(self):
        files,digest,sdk,report=self.fixture()
        def check(value): audit.audit_derived_sdk(value,report,lambda p:p,files.__getitem__,digest)
        check(sdk)
        for mutate,message in [(lambda s:s['inputs'].update({'inputs/a':'0'*64}),'build input'),
                               (lambda s:s['artifacts'][0].update(name='other'),'artifact set'),
                               (lambda s:s['artifacts'][0].update(sha256='0'*64),'worker identity'),
                               (lambda s:s.update(envelope_sha256='0'*64),'envelope identity')]:
            value=copy.deepcopy(sdk);mutate(value)
            with self.subTest(message=message),self.assertRaisesRegex(ValueError,message):check(value)
        report['native_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'envelope identity'):check(sdk)

    def test_matching_hashes_do_not_hide_wrong_payload(self):
        files,digest,sdk,report=self.fixture()
        files['worker/native-c.bin']=b'AENATC01'+bytes(32)+b'other-elf'
        sdk['envelope_sha256']=report['native_sha256']=digest('worker/native-c.bin')
        with self.assertRaisesRegex(ValueError,'ELF correspondence'):
            audit.audit_derived_sdk(sdk,report,lambda p:p,files.__getitem__,digest)

    def test_bad_envelope_with_matching_hashes(self):
        for raw in (b'AENATC01'+bytes(32),b'BADMAGIC'+bytes(32)+b'x',b'AENATC01'+bytes(1048576+33)):
            files,digest,sdk,report=self.fixture();files['worker/native-c.bin']=raw
            sdk['envelope_sha256']=report['native_sha256']=digest('worker/native-c.bin')
            with self.assertRaisesRegex(ValueError,'invalid derived SDK envelope'):
                audit.audit_derived_sdk(sdk,report,lambda p:p,files.__getitem__,digest)
