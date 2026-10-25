# SPDX-License-Identifier: BSD-2-Clause
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import test_harness_native_audit as fixtures


audit = fixtures.audit


class NativeCatalogTests(unittest.TestCase):
    def test_invalid_top_level_rejects_before_bundle_access(self):
        for catalog in ({'schema': 'wrong', 'bundles': [{}]},
                        {'schema': 'sys-init-native-coverage-v1', 'bundles': []},
                        {'schema': 'sys-init-native-coverage-v1', 'bundles': [{'directory': 'same'}, {'directory': 'same'}]}):
            with self.subTest(catalog=catalog), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / 'docs').mkdir()
                (root / 'docs/native-coverage.json').write_text(json.dumps(catalog))
                with patch.object(audit, 'ROOT', root), patch.object(audit.sys, 'argv', ['check']), patch.object(audit, 'audit_bundle') as bundle:
                    with self.assertRaises(ValueError):
                        audit.main()
                bundle.assert_not_called()

    def test_existing_but_unlisted_results_reject(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = root / 'bundle'
            bundle.mkdir()
            (bundle / 'note').write_text('inert')
            (bundle / 'results.json').write_text('{}')
            manifest = bundle / 'SHA256SUMS.json'
            manifest.write_text(json.dumps({'note': audit.sha(bundle / 'note')}))
            entry = {'directory': 'bundle', 'manifest_sha256': audit.sha(manifest)}
            with self.assertRaisesRegex(ValueError, 'bundle file inventory differs from manifest'):
                audit.audit_bundle(root, entry)

    def test_manifest_rejects_matching_pin_empty_map(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / 'SHA256SUMS.json'
            manifest.write_text('{}')
            with self.assertRaisesRegex(ValueError, 'empty manifest'):
                audit.verify_manifest(root, audit.sha(manifest))
