# SPDX-License-Identifier: BSD-2-Clause
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import test_harness_quality_records as fixtures

quality = fixtures.quality


class QualityInputTests(unittest.TestCase):
    def test_record_and_reference_special_files(self):
        for name in ('docs/quality-inventory.json', 'reference'):
            for kind in ('fifo', 'link', 'directory'):
                with self.subTest(name=name, kind=kind), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    helper = fixtures.QualityRecordTests()
                    helper.write(root, helper.fixture(root))
                    path = root / name
                    path.unlink()
                    if kind == 'fifo':
                        os.mkfifo(path)
                    elif kind == 'link':
                        path.symlink_to(root / 'snapshot/source')
                    else:
                        path.mkdir()
                    with patch.object(quality.os, 'open', wraps=os.open) as opened:
                        with self.assertRaises(ValueError):
                            quality.check(root)
                        self.assertNotIn(path, [call.args[0] for call in opened.call_args_list])

    def test_reference_parent_link_and_large_ordinary_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'real').mkdir()
            path = root / 'real/source'
            path.write_bytes(b'x' * (quality.MAX_RECORD + 1))
            self.assertEqual(quality.local_file(root, 'real/source'), path)
            (root / 'alias').symlink_to(root / 'real')
            with self.assertRaises(ValueError):
                quality.local_file(root, 'alias/source')
            with patch.object(quality.os, 'open') as opened, self.assertRaisesRegex(ValueError, '1 MiB'):
                quality.digest(path, root)
            opened.assert_not_called()

    def test_replacement_between_stat_and_open(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / 'source'
            path.write_bytes(b'original')
            replacement = root / 'replacement'
            replacement.write_bytes(b'replaced')
            original = os.open
            def replace(name, flags):
                replacement.replace(path)
                return original(name, flags)
            with patch.object(quality.os, 'open', side_effect=replace), self.assertRaisesRegex(ValueError, 'before read'):
                quality.read_record(path, root)

    def test_growth_during_read_and_exact_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / 'source'
            path.write_bytes(b'x' * quality.MAX_RECORD)
            self.assertEqual(len(quality.read_record(path, root)), quality.MAX_RECORD)
            original = os.read
            changed = False
            def grow(fd, size):
                nonlocal changed
                chunk = original(fd, size)
                if not changed:
                    with path.open('ab') as target:
                        target.write(b'extra')
                    changed = True
                return chunk
            with patch.object(quality.os, 'read', side_effect=grow), self.assertRaisesRegex(ValueError, 'during read'):
                quality.read_record(path, root)
