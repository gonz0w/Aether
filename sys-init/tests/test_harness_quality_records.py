# SPDX-License-Identifier: BSD-2-Clause
import copy
import json
from pathlib import Path
import tempfile
import unittest
import test_harness_quality_process as process

quality = process.QUALITY


class QualityRecordTests(unittest.TestCase):
    def fixture(self, root):
        (root/'docs').mkdir();(root/'snapshot').mkdir()
        (root/'reference').write_text('reference')
        (root/'snapshot/source').write_text('reviewed')
        manifest=root/'snapshot/SHA256SUMS.json'
        manifest.write_text(json.dumps({'source':quality.digest(root/'snapshot/source')}))
        return dict(schema='sys-init-quality-inventory-v1',scope='fixture',snapshot='snapshot',
                    snapshot_manifest_sha256=quality.digest(manifest),process=['reference'],
                    surfaces=[dict(id='Q1',owner='fixture',status='experimental',layer='host',
                                   reference='reference',tests=['reference'],oracle='fixture',
                                   evidence='reference',stage='local')],
                    gaps=[dict(id='G1',owner='fixture',status='open',topic='remaining',
                               milestone='later',backlog='reference')])

    def write(self,root,record):
        (root/'docs/quality-inventory.json').write_text(json.dumps(record))

    def test_matching_pin_does_not_make_empty_manifest_valid(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);record=self.fixture(root)
            manifest=root/'snapshot/SHA256SUMS.json';manifest.write_text('{}')
            record['snapshot_manifest_sha256']=quality.digest(manifest);self.write(root,record)
            with self.assertRaisesRegex(ValueError,'empty or oversized snapshot inventory'):quality.check(root)

    def test_snapshot_references_cannot_escape_even_with_matching_digest(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);record=self.fixture(root)
            (root/'snapshot/alias').symlink_to(root/'reference')
            for name in ['../reference','alias']:
                manifest=root/'snapshot/SHA256SUMS.json'
                manifest.write_text(json.dumps({name:quality.digest(root/'reference')}))
                record['snapshot_manifest_sha256']=quality.digest(manifest);self.write(root,record)
                with self.subTest(name=name),self.assertRaises(ValueError):quality.check(root)

    def test_layer_counts_and_missing_test_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);record=self.fixture(root)
            original=record['surfaces'][0]
            record['surfaces']=[dict(original,id='Q'+str(i),layer=layer)
                                for i,layer in enumerate(['model','host','target'])]
            self.write(root,record)
            self.assertEqual(quality.check(root),dict(schema='sys-init-quality-check-v1',result='pass',
                             scope='record structure and reviewed bytes only',surfaces=3,open_gaps=1))
            record['surfaces'][0]['layer']='production';self.write(root,record)
            with self.assertRaisesRegex(ValueError,'unsupported coverage claim'):quality.check(root)
            record['surfaces'][0]['layer']='model';record['surfaces'][0]['tests']=['absent']
            self.write(root,record)
            with self.assertRaisesRegex(ValueError,'missing or escaping local file'):quality.check(root)
