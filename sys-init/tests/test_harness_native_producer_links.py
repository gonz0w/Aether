# SPDX-License-Identifier: BSD-2-Clause
import copy
import json
import unittest
import test_harness_native_audit as fixtures


audit = fixtures.audit


class ProducerLinkTests(unittest.TestCase):
    def test_retained_links_and_mutations(self):
        counts = workers = normalized = 0
        for entry in json.loads((fixtures.ROOT/'docs/native-coverage.json').read_text())['bundles']:
            if entry['schema'] != 'sys-init-native-init-v1': continue
            directory = fixtures.ROOT/entry['directory']
            summary = json.loads((directory/'producer/summary.json').read_text())
            producer = json.loads((directory/'producer/init/results.json').read_text())
            audit.check_producer_links(summary,producer)
            if 'cases' in summary['suites']['init']:
                counts += 1;changed=copy.deepcopy(summary)
                changed['suites']['init']['cases']+=1
                with self.assertRaisesRegex(ValueError,'suite count mismatch'):
                    audit.check_producer_links(changed,producer)
            else: normalized += 1
            if any(c.get('first_image')=='service-worker' for c in entry['cases']):
                workers += 1
                worker=json.loads((directory/'worker/evidence.json').read_text())
                audit.check_producer_links(summary,producer,worker)
                for field in ('sdk_receipt_sha256','libc_sha256','tools_lock_sha256'):
                    changed=copy.deepcopy(worker);changed[field]='0'*64
                    with self.subTest(field=field),self.assertRaisesRegex(ValueError,'dependency mismatch'):
                        audit.check_producer_links(summary,producer,changed)
        self.assertEqual((counts,normalized,workers),(40,5,18))
