# SPDX-License-Identifier: BSD-2-Clause
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import test_harness_quality_records as fixtures

quality=fixtures.quality


class SnapshotTests(unittest.TestCase):
    def fixture(self,root):
        helper=fixtures.QualityRecordTests();record=helper.fixture(root);helper.write(root,record)
        return record

    def test_unlisted_and_missing_files_reject(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);self.fixture(root)
            extra=root/'snapshot/extra';extra.write_text('unlisted')
            with self.assertRaisesRegex(ValueError,'file inventory'):quality.check(root)
            extra.unlink();(root/'snapshot/source').unlink()
            with self.assertRaisesRegex(ValueError,'file inventory'):quality.check(root)

    def test_symlink_and_fifo_entries_reject_without_reading(self):
        for kind in ['file-link','directory-link','fifo']:
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as directory:
                root=Path(directory);self.fixture(root);extra=root/'snapshot/extra'
                if kind=='fifo':os.mkfifo(extra)
                else:extra.symlink_to(root/'reference' if kind=='file-link' else root)
                with self.assertRaisesRegex(ValueError,'symlink or special'):quality.check(root)

    def test_snapshot_parent_alias_rejects(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);record=self.fixture(root);(root/'alias').symlink_to(root/'snapshot',target_is_directory=True)
            record['snapshot']='alias';fixtures.QualityRecordTests().write(root,record)
            with self.assertRaisesRegex(ValueError,'symlink component'):quality.check(root)

    def test_late_source_and_unlisted_file_changes_reject(self):
        for kind in ['source','extra']:
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as directory:
                root=Path(directory);self.fixture(root);original=quality.local_file;changed=False
                def resolve(base,name):
                    nonlocal changed
                    if base==root and name=='reference' and not changed:
                        (root/'snapshot'/kind).write_text('changed');changed=True
                    return original(base,name)
                with patch.object(quality,'local_file',side_effect=resolve),self.assertRaises(ValueError):quality.check(root)

    def test_late_record_whitespace_changes_reject(self):
        for name in ['docs/quality-inventory.json','snapshot/SHA256SUMS.json']:
            with self.subTest(name=name),tempfile.TemporaryDirectory() as directory:
                root=Path(directory);self.fixture(root);original=quality.local_file;changed=False
                def resolve(base,reference):
                    nonlocal changed
                    if base==root and reference=='reference' and not changed:
                        path=root/name;path.write_bytes(path.read_bytes()+b'\n');changed=True
                    return original(base,reference)
                with patch.object(quality,'local_file',side_effect=resolve),self.assertRaisesRegex(ValueError,'quality record changed'):quality.check(root)

    def test_tree_entry_budget_includes_directories(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for index in range(2001):(root/str(index)).mkdir()
            with self.assertRaisesRegex(ValueError,'2000 entries'):quality.snapshot_files(root,{})
