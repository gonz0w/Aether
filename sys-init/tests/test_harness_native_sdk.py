# SPDX-License-Identifier: BSD-2-Clause
import copy
import json
import unittest
from unittest.mock import patch
import test_harness_native_audit as fixtures


audit = fixtures.audit


class SDKReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = []
        cls.entries = json.loads((fixtures.ROOT/'docs/native-coverage.json').read_text())['bundles']
        for entry in cls.entries:
            for name in ('sdk-evidence.json','worker/inputs/sdk-evidence.json'):
                path = fixtures.ROOT/entry['directory']/name
                if path.exists(): cls.records.append((entry,name,path,json.loads(path.read_text())))

    def test_all_retained_variants(self):
        self.assertEqual(len(self.records),27)
        for _,name,path,value in self.records:
            with self.subTest(path=str(path)):
                audit.validate_sdk(value,direct=name.startswith('worker/'))

    def test_malformed_nested_fields(self):
        for derived in (False,True):
            value = next(r[3] for r in self.records if ('inputs' in r[3]) == derived)
            mutations = [lambda r:r.update(extra=1), lambda r:r.update(artifacts=[]),
                         lambda r:r['artifacts'].append(r['artifacts'][0]),
                         lambda r:r['artifacts'][0].update(sha256='A'*64),
                         lambda r:r.update(probe_variant='unknown')]
            if derived:
                mutations += [lambda r:r.update(inputs_unchanged=1),
                              lambda r:r['inputs'].pop('inputs/sdk-evidence.json'),
                              lambda r:r.update(commands=[[]]),
                              lambda r:r.update(tools_used=['clang','clang']),
                              lambda r:r['program_headers'][0].__setitem__(0,True)]
            else:
                mutations += [lambda r:r['libc_patches'][0].update(old='bad\x00'),
                              lambda r:r['libc_patches'][0].update(new='x'*65537),
                              lambda r:r['libc_patches'][0].update(path='../escape'),
                              lambda r:r['libc_patches'].append(r['libc_patches'][0]),
                              lambda r:r['artifacts'][0].update(bytes=True),
                              lambda r:r['artifacts'][0].update(static_syscall_instruction_sites=2**32),
                              lambda r:r['artifacts'][0]['program_headers'][0].__setitem__(2,2**64)]
            for i,mutate in enumerate(mutations):
                changed=copy.deepcopy(value);mutate(changed)
                with self.subTest(derived=derived,index=i), self.assertRaises(ValueError):audit.validate_sdk(changed)
        with self.assertRaisesRegex(ValueError,'direct SDK receipt required'):audit.validate_sdk(value,direct=True)

    def test_multiline_patch_bounds(self):
        value=copy.deepcopy(next(r[3] for r in self.records if 'inputs' not in r[3]))
        value['libc_patches'][0]['old']='a\t\r\n'+'x'*65532
        audit.validate_sdk(value,direct=True)
        for text in ('', 'x\x1b', 'x\x7f', False):
            value['libc_patches'][0]['old']=text
            with self.assertRaisesRegex(ValueError,'SDK patch text'):audit.validate_sdk(value,direct=True)

    def test_all_fixed_read_sites_validate(self):
        chosen=[self.records[0],next(r for r in self.records if 'inputs' in r[3]),
                next(r for r in self.records if r[0]['schema']!='sys-init-native-init-v1' and r[1].startswith('worker/')),
                next(r for r in self.records if r[0]['schema']=='sys-init-native-init-v1')]
        for entry,name,path,value in chosen:
            raw=path.read_bytes();original=audit.parse_receipt;reached=False
            def parse(data):
                nonlocal reached
                parsed=original(data)
                if data==raw:
                    reached=True;parsed['extra']=1
                return parsed
            with self.subTest(directory=entry['directory'],name=name), patch.object(audit,'parse_receipt',side_effect=parse):
                with self.assertRaisesRegex(ValueError,'invalid catalog fields'):audit.audit_bundle(fixtures.ROOT,entry)
                self.assertTrue(reached)
