# SPDX-License-Identifier: BSD-2-Clause
import copy
import json
import unittest
from unittest.mock import patch
import test_harness_native_audit as fixtures


audit = fixtures.audit


class CorrespondenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = json.loads((fixtures.ROOT/'docs/native-coverage.json').read_text())['bundles']

    def test_worker_required_links(self):
        entry = next(e for e in self.entries if any(c.get('first_image') == 'service-worker' for c in e['cases']))
        value = json.loads((fixtures.ROOT/entry['directory']/'worker/evidence.json').read_text())
        audit.validate_worker(value)
        for key, name in (('sdk_receipt_sha256','inputs/sdk-evidence.json'),
                          ('tools_lock_sha256','inputs/tools.lock.json'),
                          ('libc_sha256','inputs/libc.a')):
            for mode in ('missing','map-mismatch','top-mismatch'):
                with self.subTest(key=key,mode=mode):
                    changed = copy.deepcopy(value)
                    if mode == 'missing': changed['inputs'].pop(name)
                    elif mode == 'map-mismatch': changed['inputs'][name] = '0'*64
                    else: changed[key] = '0'*64
                    with self.assertRaisesRegex(ValueError,'worker input identity mismatch'):
                        audit.validate_worker(changed)

    def test_io_supervisor_claim_is_checked(self):
        entry = self.entries[0]
        directory = fixtures.ROOT/entry['directory']
        raw = (directory/'clients'/entry['cases'][0]['name']/'build.json').read_bytes()
        original = audit.parse_receipt
        reached = False
        def parse(data):
            nonlocal reached
            value = original(data)
            if data == raw:
                reached = True
                value['supervisor_sha256'] = '0'*64
            return value
        with patch.object(audit,'parse_receipt',side_effect=parse):
            with self.assertRaisesRegex(ValueError,'I/O supervisor identity mismatch'):
                audit.audit_bundle(fixtures.ROOT,entry)
        self.assertTrue(reached)
