# SPDX-License-Identifier: BSD-2-Clause
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import test_harness_native_audit as fixtures


audit = fixtures.audit


class NativeConsistencyTests(unittest.TestCase):
    def seal(self, root):
        (root/'payload').write_bytes(b'inert')
        manifest = root/'SHA256SUMS.json'
        manifest.write_text(json.dumps({'payload': audit.sha(root/'payload')}))
        return audit.sha(manifest)

    def test_unlisted_special_files_and_late_inventory(self):
        for kind in ('extra', 'fifo', 'symlink', 'late-extra'):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                root = Path(directory); pin = self.seal(root); extra = root/'extra'
                if kind == 'extra': extra.write_text('extra')
                elif kind == 'fifo': os.mkfifo(extra)
                elif kind == 'symlink': extra.symlink_to(root/'payload')
                original = audit.sha
                def digest(path, anchor=None):
                    result = original(path, anchor)
                    if kind == 'late-extra': extra.write_text('late')
                    return result
                with patch.object(audit, 'sha', side_effect=digest), self.assertRaises(ValueError):
                    audit.verify_manifest(root, pin)

    def test_tree_budget_counts_empty_directories(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for i in range(20001): (root/str(i)).mkdir()
            with self.assertRaisesRegex(ValueError, '20000 entries'): audit.bundle_files(root, root)

    def test_final_pass_rechecks_earlier_bundles(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root/'docs').mkdir()
            bundles = []
            for name in ('first', 'second'):
                path = root/name; path.mkdir(); pin = self.seal(path)
                bundles.append(dict(directory=name, manifest_sha256=pin, schema='sys-init-native-io-stop-v1', cases=[dict(name='case', marker='marker', assertion=None, smoke_exit=0)]))
            (root/'docs/native-coverage.json').write_text(json.dumps(dict(schema='sys-init-native-coverage-v1',scope='fixture',bundles=bundles)))
            def bundle(base, entry):
                if entry['directory'] == 'second': (root/'first/payload').write_text('changed')
                return dict(directory=entry['directory'],cases=1,files=1,result='pass')
            output = io.StringIO()
            with patch.object(audit, 'ROOT', root), patch.object(audit.sys, 'argv', ['check']), patch.object(audit, 'audit_bundle', side_effect=bundle), contextlib.redirect_stdout(output):
                with self.assertRaisesRegex(ValueError, 'evidence digest mismatch'): audit.main()
            self.assertEqual(output.getvalue(), '')
