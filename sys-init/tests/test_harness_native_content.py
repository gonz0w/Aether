# SPDX-License-Identifier: BSD-2-Clause
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import test_harness_native_audit as fixtures


audit = fixtures.audit


class NativeContentTests(unittest.TestCase):
    def test_text_decoding_and_newline_compatibility(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); path = root/'text'
            for raw in (b'', b'a\r\nb\rc\n', b'plain\x00text'):
                path.write_bytes(raw)
                self.assertEqual(audit.read_text(path, root), path.read_text())

    def test_late_semantic_input_changes_reject(self):
        entry = next(e for e in json.loads((fixtures.ROOT/'docs/native-coverage.json').read_text())['bundles'] if e['schema'] == 'sys-init-native-init-v1')
        for selected in ('results.json', 'producer/init/positive/native-c.bin', 'cases/policy/native-serial.log'):
            for kind in ('fifo', 'symlink', 'oversize'):
                with self.subTest(selected=selected, kind=kind), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory); bundle = root/'bundle'
                    shutil.copytree(fixtures.ROOT/entry['directory'], bundle)
                    original = audit.read_metadata
                    changed = False
                    def read(path, anchor=None):
                        nonlocal changed
                        self.assertEqual(anchor, root)
                        if path == bundle/selected and not changed:
                            changed = True
                            path.unlink()
                            if kind == 'fifo': os.mkfifo(path)
                            elif kind == 'symlink': path.symlink_to(bundle/'SHA256SUMS.json')
                            else:
                                with path.open('wb') as source: source.truncate(audit.MAX_CATALOG+1)
                        return original(path, anchor)
                    with patch.object(audit, 'read_metadata', side_effect=read), self.assertRaises(ValueError):
                        audit.audit_bundle(root, dict(entry, directory='bundle'))
                    self.assertTrue(changed, 'semantic reader was not reached')

    def test_text_read_error_closes_descriptor(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); path = root/'text'; path.write_bytes(b'hello')
            original = os.open; descriptors = []
            def open_file(name, flags):
                fd = original(name, flags); descriptors.append(fd); return fd
            with patch.object(audit.os, 'open', side_effect=open_file), patch.object(audit.os, 'read', side_effect=OSError('read failed')), self.assertRaises(OSError):
                audit.read_text(path, root)
            with self.assertRaises(OSError): os.fstat(descriptors[0])
