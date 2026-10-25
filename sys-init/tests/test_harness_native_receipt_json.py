# SPDX-License-Identifier: BSD-2-Clause
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import test_harness_native_audit as fixtures


audit = fixtures.audit


class ReceiptJSONTests(unittest.TestCase):
    def test_invalid_json_and_roots_reject(self):
        for raw in (b'{"x":1,"x":2}', b'{"x":{"a":1,"a":2}}', b'{"x":NaN}',
                    b'{"x":Infinity}', b'{"x":1e9999}', b'{"x":-1e9999}', b'\xff',
                    b'[]', b'null', b'"text"', b'['*33+b'0'+b']'*33,
                    b' '*(audit.MAX_CATALOG+1)):
            with self.subTest(prefix=raw[:24]), self.assertRaises(ValueError): audit.parse_receipt(raw)

    def test_finite_values_and_quoted_brackets_preserved(self):
        raw = '{"float":1.25,"integer":42,"boolean":true,"null":null,"text":"é[[["}'.encode()
        self.assertEqual(audit.parse_receipt(raw), json.loads(raw))

    def test_all_receipt_sites_use_strict_parser(self):
        catalog = json.loads((fixtures.ROOT/'docs/native-coverage.json').read_text())
        io_entry = catalog['bundles'][0]
        init = next(e for e in catalog['bundles'] if e['schema'] == 'sys-init-native-init-v1')
        service = next(e for e in catalog['bundles'] if any(c.get('first_image') == 'service-worker' for c in e['cases']))
        for entry, name in ((init, 'results.json'), (init, 'producer/summary.json'),
                            (init, 'producer/init/results.json'), (service, 'worker/evidence.json'),
                            (io_entry, 'clients/stop/build.json')):
            with self.subTest(name=name):
                expected = (fixtures.ROOT/entry['directory']/name).read_bytes()
                original = audit.parse_receipt; reached = False
                def parse(raw):
                    nonlocal reached
                    if raw == expected:
                        reached = True
                        return original(b'{"duplicate":1,"duplicate":2}')
                    return original(raw)
                with patch.object(audit, 'parse_receipt', side_effect=parse), self.assertRaisesRegex(ValueError, 'duplicate receipt JSON key'):
                    audit.audit_bundle(fixtures.ROOT, entry)
                self.assertTrue(reached)
