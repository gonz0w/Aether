# SPDX-License-Identifier: BSD-2-Clause
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import test_harness_native_audit as fixtures


audit = fixtures.audit


class NativeMetadataTests(unittest.TestCase):
    def test_catalog_and_manifest_special_files_reject_before_open(self):
        for selected in ('catalog', 'manifest'):
            for kind in ('fifo', 'symlink', 'parent-link'):
                with self.subTest(selected=selected, kind=kind), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory); (root/'docs').mkdir(); (root/'bundle').mkdir()
                    path = root/('docs/native-coverage.json' if selected == 'catalog' else 'bundle/SHA256SUMS.json')
                    saved = root/'saved'; saved.write_text('{}')
                    if kind == 'fifo': os.mkfifo(path)
                    elif kind == 'symlink': path.symlink_to(saved)
                    else:
                        parent = path.parent; moved = root/'moved'; parent.rename(moved); parent.symlink_to(moved)
                        path.write_text('{}')
                    with patch.object(audit.os, 'open') as opened:
                        with self.assertRaises(ValueError):
                            if selected == 'manifest': audit.verify_manifest(root/'bundle', '0'*64, root)
                            else:
                                with patch.object(audit, 'ROOT', root), patch.object(audit.sys, 'argv', ['check']): audit.main()
                    opened.assert_not_called()

    def test_bad_matching_pin_manifests_do_not_hash_payloads(self):
        values = [b'{}', b'[]', b'{"x":"0","x":"1"}', b'{"x":NaN}', b'\xff',
                  json.dumps({'../escape': '0'*64}).encode(),
                  json.dumps({'SHA256SUMS.json': '0'*64}).encode(),
                  json.dumps({'x': True}).encode(),
                  json.dumps({'x': 'G'*64}).encode(),
                  json.dumps({str(i): '0'*64 for i in range(10001)}).encode()]
        for index, raw in enumerate(values):
            with self.subTest(index=index), tempfile.TemporaryDirectory() as directory:
                root = Path(directory); (root/'SHA256SUMS.json').write_bytes(raw)
                with patch.object(audit, 'sha') as payload_hash, self.assertRaises(ValueError):
                    audit.verify_manifest(root, hashlib.sha256(raw).hexdigest())
                payload_hash.assert_not_called()

    def test_manifest_parser_receives_hashed_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root/'payload').write_bytes(b'inert')
            record = {'payload': audit.sha(root/'payload')}
            raw = json.dumps(record).encode(); path = root/'SHA256SUMS.json'; path.write_bytes(raw)
            original = audit.parse_catalog
            def parse(captured, kind):
                self.assertEqual(captured, raw)
                path.write_bytes(b'{}')
                return original(captured, kind)
            with patch.object(audit, 'parse_catalog', side_effect=parse), self.assertRaisesRegex(ValueError, 'manifest changed during verification'):
                audit.verify_manifest(root, hashlib.sha256(raw).hexdigest())

    def test_metadata_bounds_replacement_and_growth(self):
        for change in ('oversize', 'replace', 'grow'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as directory:
                root = Path(directory); path = root/'record'; path.write_bytes(b'{}')
                if change == 'oversize':
                    path.write_bytes(b' '*(audit.MAX_CATALOG+1))
                    with patch.object(audit.os, 'open') as opened, self.assertRaisesRegex(ValueError, '4 MiB'):
                        audit.read_metadata(path, root)
                    opened.assert_not_called()
                    continue
                original_open, original_read = os.open, os.read
                descriptors = []; changed = False
                def open_file(name, flags):
                    if change == 'replace':
                        replacement = root/'replacement'; replacement.write_bytes(b'{}'); replacement.replace(path)
                    fd = original_open(name, flags); descriptors.append(fd); return fd
                def read_file(fd, size):
                    nonlocal changed
                    raw = original_read(fd, size)
                    if change == 'grow' and not changed:
                        with path.open('ab') as target: target.write(b' ')
                        changed = True
                    return raw
                with patch.object(audit.os, 'open', side_effect=open_file), patch.object(audit.os, 'read', side_effect=read_file), self.assertRaisesRegex(ValueError, 'changed'):
                    audit.read_metadata(path, root)
                with self.assertRaises(OSError): os.fstat(descriptors[0])
