# SPDX-License-Identifier: BSD-2-Clause
import copy
import json
import unittest
from unittest.mock import patch
import test_harness_native_audit as fixtures


audit = fixtures.audit


class ReportFieldsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = json.loads((fixtures.ROOT/'docs/native-coverage.json').read_text())['bundles']

    def report(self, entry):
        return json.loads((fixtures.ROOT/entry['directory']/'results.json').read_text())

    def test_all_retained_variants(self):
        for entry in self.entries:
            with self.subTest(directory=entry['directory']):
                audit.validate_report(self.report(entry), entry)

    def test_invalid_fields_and_bounds(self):
        for init in (False, True):
            entry = next(e for e in self.entries if (e['schema'] == 'sys-init-native-init-v1') == init)
            original = self.report(entry)
            mutations = [
                lambda r: r.update(extra=1),
                lambda r: r.pop('result'),
                lambda r: r.update(sources_unchanged=1),
                lambda r: r.update(cases=[]),
                lambda r: r.update(cases=r['cases'][:1]*1001),
                lambda r: r.update(commands=r['commands'][:1]*3005),
                lambda r: r['cases'][0].update(serial_sha256='A'*64),
                lambda r: r['cases'][0].update(marker='bad\nmarker'),
                lambda r: r['cases'][0].update(extra=1),
                lambda r: r['commands'][0].update(exit=True),
                lambda r: r['commands'][0].update(exit=256),
                lambda r: r['commands'][0].update(argv=[]),
                lambda r: r['commands'][0].update(argv=['x']*1001),
                lambda r: r['commands'][0].update(argv=['x'*4097]),
                lambda r: r['commands'][0].update(argv=[None]),
                lambda r: r['commands'][0].update(extra=1),
            ]
            if init:
                mutations += [lambda r: r.update(service_worker_sha256='0'*64),
                              lambda r: r.update(build_profile='unknown'),
                              lambda r: r['cases'][0].update(context=False)]
            else:
                mutations += [lambda r: r['cases'][0].update(smoke_exit=True),
                              lambda r: r['cases'][0].update(marker=None)]
            for index, mutate in enumerate(mutations):
                with self.subTest(init=init, mutation=index):
                    report = copy.deepcopy(original)
                    mutate(report)
                    with self.assertRaises(ValueError): audit.validate_report(report, entry)
            valid = copy.deepcopy(original)
            valid['commands'][0] = {'argv': ['', 'x'*4096], 'exit': -255}
            audit.validate_report(valid, entry)

    def test_service_worker_pins_required(self):
        entry = next(e for e in self.entries if any(c.get('first_image') == 'service-worker' for c in e['cases']))
        report = self.report(entry)
        for key in ('service_worker_sha256', 'service_worker_receipt_sha256'):
            report.pop(key)
        with self.assertRaisesRegex(ValueError, 'missing report worker pins'):
            audit.validate_report(report, entry)

    def test_invalid_consumer_rejects_before_linked_receipts(self):
        for entry in (self.entries[0], next(e for e in self.entries if e['schema'] == 'sys-init-native-init-v1')):
            report = self.report(entry)
            report['commands'][0]['exit'] = True
            # Manifest verification is real; inject only the parsed consumer object.
            with patch.object(audit, 'parse_receipt', return_value=report) as parser:
                with self.assertRaisesRegex(ValueError, 'invalid report command exit'):
                    audit.audit_bundle(fixtures.ROOT, entry)
                self.assertEqual(parser.call_count, 1)
