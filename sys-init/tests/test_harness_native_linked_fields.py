# SPDX-License-Identifier: BSD-2-Clause
import copy
import json
import unittest
from unittest.mock import patch
import test_harness_native_audit as fixtures


audit = fixtures.audit


class LinkedFieldsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = []
        for entry in json.loads((fixtures.ROOT/'docs/native-coverage.json').read_text())['bundles']:
            directory = fixtures.ROOT/entry['directory']
            if entry['schema'] == 'sys-init-native-init-v1':
                paths = [('summary', directory/'producer/summary.json'),
                         ('producer', directory/'producer/init/results.json')]
                if any(c.get('first_image') == 'service-worker' for c in entry['cases']):
                    paths.append(('worker', directory/'worker/evidence.json'))
            else:
                paths = [('io_build', directory/'clients'/c['name']/'build.json') for c in entry['cases']]
            for kind, path in paths:
                cls.records.append((kind, path, entry, json.loads(path.read_text())))

    def test_all_retained_linked_variants(self):
        self.assertEqual(len(self.records), 130)
        for kind, path, _, value in self.records:
            with self.subTest(path=str(path)):
                getattr(audit, 'validate_'+kind)(value)

    def test_malformed_nested_fields(self):
        changes = {
            'summary': [lambda r: r['suites']['init'].update(report_sha256='x'),
                        lambda r: r.update(inputs={}),
                        lambda r: r['suites']['init'].update(cases=True),
                        lambda r: r.update(tools={}),
                        lambda r: r.update(scope='x\n')],
            'producer': [lambda r: r['cases'][0].update(status='fail'),
                         lambda r: r['cases'].append(r['cases'][0]),
                         lambda r: r.update(commands=[['x']*1001]),
                         lambda r: r.update(sources={'../escape':'0'*64}),
                         lambda r: next(iter(r['tools'].values())).update(sha256='A'*64)],
            'worker': [lambda r: r.update(inputs={}),
                       lambda r: r.update(inputs_unchanged=1),
                       lambda r: r['program_headers'][0].__setitem__(0, True),
                       lambda r: r['program_headers'][0].__setitem__(0, 2**32),
                       lambda r: r['program_headers'][0].__setitem__(2, 2**64),
                       lambda r: r.update(tools_used=['clang','clang']),
                       lambda r: r.update(commands=[None])],
            'io_build': [lambda r: r.update(command=[]),
                         lambda r: r.update(supervisor_sha256=None),
                         lambda r: r.update(variant=False)],
        }
        for kind, mutations in changes.items():
            value = next(v for k, _, _, v in self.records if k == kind)
            for index, mutate in enumerate(mutations + [lambda r: r.update(extra=1)]):
                with self.subTest(kind=kind,index=index):
                    invalid = copy.deepcopy(value); mutate(invalid)
                    with self.assertRaises(ValueError): getattr(audit, 'validate_'+kind)(invalid)

    def test_collection_and_integer_bounds(self):
        for value, kind, maximum in [([],list,1000),([0]*1001,list,1000),({},dict,64),
                                      ({str(i):0 for i in range(65)},dict,64)]:
            with self.assertRaises(ValueError): audit.receipt_collection(value,kind,maximum)
        for value in (True,-1,2**64):
            with self.assertRaises(ValueError): audit.receipt_integer(value,2**64-1)
        audit.receipt_integer(2**64-1,2**64-1)
        audit.receipt_argv(['','x'*4096])
        with self.assertRaises(ValueError): audit.receipt_argv(['x'*4097])

    def test_each_site_rejects_before_following_fields(self):
        for kind in ('summary','producer','worker','io_build'):
            _, path, entry, value = next(r for r in self.records if r[0] == kind)
            raw = path.read_bytes(); original = audit.parse_receipt
            invalid = copy.deepcopy(value); invalid['extra'] = 1
            reached = False
            def parse(data):
                nonlocal reached
                if data == raw:
                    reached = True
                    return invalid
                if reached:
                    self.fail('parsed a later receipt after invalid fields')
                return original(data)
            with self.subTest(kind=kind), patch.object(audit,'parse_receipt',side_effect=parse):
                with self.assertRaisesRegex(ValueError,'invalid catalog fields'):
                    audit.audit_bundle(fixtures.ROOT,entry)
                self.assertTrue(reached)
