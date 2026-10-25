# SPDX-License-Identifier: BSD-2-Clause
import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import test_harness_native_audit as fixtures


audit = fixtures.audit


class NativeHashingTests(unittest.TestCase):
    def test_raw_digest_compatibility_and_chunk_budget(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); path = root/'payload'
            for raw in (b'', bytes(range(256))*1024):
                path.write_bytes(raw)
                with patch.object(audit.os, 'read', wraps=os.read) as read:
                    self.assertEqual(audit.sha(path, root), hashlib.sha256(raw).hexdigest())
                self.assertTrue(all(call.args[1] <= 65536 for call in read.call_args_list))
                if raw: self.assertGreater(len(read.call_args_list), 4)

    def test_special_and_oversized_files_reject_before_open(self):
        for kind in ('fifo', 'directory', 'symlink', 'parent-link', 'oversize'):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                root = Path(directory); path = root/'payload'
                if kind == 'fifo': os.mkfifo(path)
                elif kind == 'directory': path.mkdir()
                elif kind == 'symlink':
                    (root/'real').write_bytes(b'x'); path.symlink_to(root/'real')
                elif kind == 'parent-link':
                    (root/'real').mkdir(); (root/'real/source').write_bytes(b'x'); path.symlink_to(root/'real'); path /= 'source'
                else:
                    with path.open('wb') as source: source.truncate(audit.MAX_PAYLOAD+1)
                with patch.object(audit.os, 'open') as opened, self.assertRaises(ValueError): audit.sha(path, root)
                opened.assert_not_called()

    def test_changed_inputs_close_descriptor(self):
        for change in ('replace', 'grow'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as directory:
                root = Path(directory); path = root/'payload'; path.write_bytes(b'x'*100000)
                original_open, original_read = os.open, os.read
                descriptors = []; changed = False
                def open_file(name, flags):
                    if change == 'replace':
                        p = root/'replacement'; p.write_bytes(b'y'); p.replace(path)
                    fd = original_open(name, flags); descriptors.append(fd); return fd
                def read_file(fd, size):
                    nonlocal changed
                    raw = original_read(fd, size)
                    if change == 'grow' and not changed:
                        with path.open('ab') as source: source.write(b'changed')
                        changed = True
                    return raw
                with patch.object(audit.os, 'open', side_effect=open_file), patch.object(audit.os, 'read', side_effect=read_file), self.assertRaisesRegex(ValueError, 'changed'):
                    audit.sha(path, root)
                with self.assertRaises(OSError): os.fstat(descriptors[0])

    def test_limit_boundary_and_read_error_cleanup(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); path = root/'payload'; path.write_bytes(b'abcd')
            with patch.object(audit, 'MAX_PAYLOAD', 4): self.assertEqual(audit.sha(path, root), hashlib.sha256(b'abcd').hexdigest())
            original = os.open; descriptors = []
            def open_file(name, flags):
                fd = original(name, flags); descriptors.append(fd); return fd
            with patch.object(audit.os, 'open', side_effect=open_file), patch.object(audit.os, 'read', side_effect=OSError('injected read error')), self.assertRaises(OSError):
                audit.sha(path, root)
            with self.assertRaises(OSError): os.fstat(descriptors[0])
