# SPDX-License-Identifier: BSD-2-Clause
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import test_harness_native_audit as fixtures


audit = fixtures.audit


class VerifiedNativeContentTests(unittest.TestCase):
    def fixture(self, root):
        entry = next(e for e in json.loads((fixtures.ROOT/'docs/native-coverage.json').read_text())['bundles'] if e['schema'] == 'sys-init-native-init-v1')
        shutil.copytree(fixtures.ROOT/entry['directory'], root/'bundle')
        return dict(entry, directory='bundle')

    def test_late_content_changes_reject_before_semantic_parsing(self):
        for selected in ('results.json', 'producer/summary.json', 'producer/init/positive/native-c.bin', 'cases/policy/native-serial.log'):
            with self.subTest(selected=selected), tempfile.TemporaryDirectory() as directory:
                root = Path(directory); entry = self.fixture(root); target = root/'bundle'/selected
                original = audit.read_metadata; changed = False
                def read(path, anchor=None):
                    nonlocal changed
                    if path == target and not changed:
                        changed = True
                        path.write_bytes(b'{invalid json' if selected == 'results.json' else path.read_bytes()+b'\n')
                    return original(path, anchor)
                with patch.object(audit, 'read_metadata', side_effect=read), self.assertRaisesRegex(ValueError, 'semantic input differs from manifest'):
                    audit.audit_bundle(root, entry)
                self.assertTrue(changed)

    def test_post_capture_change_rejects_at_final_verification(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); entry = self.fixture(root); target = root/'bundle/results.json'
            original = audit.read_metadata; changed = False
            def read(path, anchor=None):
                nonlocal changed
                raw = original(path, anchor)
                if path == target and not changed:
                    path.write_bytes(b'not JSON'); changed = True
                return raw
            with patch.object(audit, 'read_metadata', side_effect=read), self.assertRaisesRegex(ValueError, 'evidence digest mismatch'):
                audit.audit_bundle(root, entry)
            self.assertTrue(changed)

    def test_receipt_digest_remains_bound_to_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); entry = self.fixture(root); target = root/'bundle/producer/summary.json'
            original = audit.sha; calls = 0
            def digest(path, anchor=None):
                nonlocal calls
                if path == target:
                    calls += 1
                    if calls == 2: path.write_bytes(path.read_bytes()+b'\n')
                return original(path, anchor)
            with patch.object(audit, 'sha', side_effect=digest), self.assertRaisesRegex(ValueError, 'retained digest changed during audit'):
                audit.audit_bundle(root, entry)
            self.assertEqual(calls, 2)
