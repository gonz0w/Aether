# SPDX-License-Identifier: BSD-2-Clause
import copy
import json
import unittest
import test_harness_native_audit as fixtures


audit = fixtures.audit


class ProducerSourcesTests(unittest.TestCase):
    def test_retained_and_scoped_omissions(self):
        available=omitted=0
        for entry in json.loads((fixtures.ROOT/'docs/native-coverage.json').read_text())['bundles']:
            if entry['schema']!='sys-init-native-init-v1':continue
            d=fixtures.ROOT/entry['directory']/'producer'
            summary=json.loads((d/'summary.json').read_text())
            producer=json.loads((d/'init/results.json').read_text())
            audit.check_producer_sources(summary,producer,entry)
            available+=len(set(producer['sources'])&set(summary['inputs']))
            missing=set(producer['sources'])-set(summary['inputs']);omitted+=len(missing)
            if missing:
                with self.assertRaisesRegex(ValueError,'source missing'):
                    audit.check_producer_sources(summary,producer,dict(entry,manifest_sha256='0'*64))
                changed=copy.deepcopy(summary);changed.pop('schema')
                with self.assertRaisesRegex(ValueError,'source missing'):
                    audit.check_producer_sources(changed,producer,entry)
                for name in missing:
                    changed=copy.deepcopy(producer);changed['sources'][name]='0'*64
                    with self.assertRaisesRegex(ValueError,'source missing'):
                        audit.check_producer_sources(summary,changed,entry)
                    changed=copy.deepcopy(summary);changed['inputs'][name]='0'*64
                    with self.assertRaisesRegex(ValueError,'source digest mismatch'):
                        audit.check_producer_sources(changed,producer,entry)
            changed=copy.deepcopy(producer);changed['sources']['unknown.rs']='0'*64
            with self.assertRaisesRegex(ValueError,'source missing'):
                audit.check_producer_sources(summary,changed,entry)
            name=next(n for n in producer['sources'] if n in summary['inputs'])
            changed=copy.deepcopy(producer);changed['sources'][name]='0'*64
            with self.assertRaisesRegex(ValueError,'source digest mismatch'):
                audit.check_producer_sources(summary,changed,entry)
        self.assertEqual((available,omitted),(3420,10))
