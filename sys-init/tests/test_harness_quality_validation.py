# SPDX-License-Identifier: BSD-2-Clause
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import test_harness_quality_records as fixtures

quality = fixtures.quality


class QualityValidationTests(unittest.TestCase):
    def test_invalid_inventory_rejects_before_reference_traversal(self):
        original=json.loads((quality.ROOT/'docs/quality-inventory.json').read_text())
        mutations=[lambda x:x.pop('scope'),lambda x:x.update(extra=1),lambda x:x.update(process='x'),
                   lambda x:x['surfaces'][0].update(owner=True),lambda x:x['surfaces'][0].update(id=[]),
                   lambda x:x['surfaces'][0].update(tests=['a','a']),
                   lambda x:x['gaps'][0].update(milestone=1),lambda x:x['gaps'][0].update(reference='../escape'),
                   lambda x:x.update(snapshot_manifest_sha256='A'*64),lambda x:x.update(scope='\ud800'),
                   lambda x:x['surfaces'][0].update(status='conformant')]
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'docs').mkdir()
            for index,mutate in enumerate(mutations):
                record=copy.deepcopy(original);mutate(record)
                (root/'docs/quality-inventory.json').write_text(json.dumps(record))
                with self.subTest(index=index),patch.object(quality,'local_file') as resolve:
                    with self.assertRaises(ValueError):quality.check(root)
                    resolve.assert_not_called()

    def test_parser_bounds_duplicate_keys_and_quoted_brackets(self):
        invalid=[b'\xff',b'{',b'{"x":1,"x":2}',b'{"x":{"a":1,"a":2}}',b'{"x":NaN}',
                 b'{"x":Infinity}',b'['*33+b'0'+b']'*33,b' '*(quality.MAX_RECORD+1)]
        for raw in invalid:
            with self.subTest(length=len(raw)),self.assertRaises(ValueError):quality.parse_record(raw)
        quality.parse_record(b'['*32+b'0'+b']'*32)
        quality.parse_record(json.dumps({'text':'['*100+'"'+']'*100}).encode())

    def test_matching_manifest_pin_does_not_bypass_strict_manifest_validation(self):
        fixture=fixtures.QualityRecordTests()
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);record=fixture.fixture(root);manifest=root/'snapshot/SHA256SUMS.json'
            valid=quality.digest(root/'snapshot/source')
            cases=[json.dumps({'source':'bad'}),json.dumps({'../reference':valid}),
                   '{"source":"'+valid+'","source":"'+valid+'"}']
            for raw in cases:
                manifest.write_text(raw);record['snapshot_manifest_sha256']=quality.digest(manifest)
                fixture.write(root,record)
                with self.assertRaises(ValueError):quality.check(root)

    def test_optional_gap_references_are_validated_and_resolved(self):
        fixture=fixtures.QualityRecordTests()
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);record=fixture.fixture(root)
            record['gaps'][0].update(reference='reference',review_evidence='reference')
            fixture.write(root,record);self.assertEqual(quality.check(root)['result'],'pass')
            record['gaps'][0]['review_evidence']='missing';fixture.write(root,record)
            with self.assertRaisesRegex(ValueError,'missing or escaping'):quality.check(root)

    def test_cli_malformed_input_preserves_stderr_only_exit_one(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'scripts').mkdir();(root/'docs').mkdir()
            script=root/'scripts/check-quality-process.py';shutil.copy2(quality.__file__,script)
            (root/'docs/quality-inventory.json').write_text('{}')
            result=subprocess.run([sys.executable,str(script)],capture_output=True,timeout=5)
            self.assertEqual(result.returncode,1)
            self.assertEqual(result.stdout,b'')
            self.assertIn(b'quality process:',result.stderr)
            self.assertNotIn(b'Traceback',result.stderr)
