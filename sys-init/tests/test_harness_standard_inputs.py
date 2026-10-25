# SPDX-License-Identifier: BSD-2-Clause
"""Bounded standard inputs, using synthetic private release trees."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import test_harness_offline_locks as fixtures


class StandardInputTests(unittest.TestCase):
    def test_special_inputs_reject_before_open_and_execution(self):
        for suffix in fixtures.FAMILIES:
            for selected in ('lock', 'manifest', 'payload'):
                for kind in ('fifo', 'symlink'):
                    with self.subTest(suffix=suffix, selected=selected, kind=kind), tempfile.TemporaryDirectory() as directory:
                        module, lock, manifest, checker = fixtures.OfflineLockTests().fixture(Path(directory).resolve(), suffix)
                        path = {'lock': lock, 'manifest': manifest, 'payload': checker}[selected]
                        saved = Path(directory) / 'saved'
                        path.rename(saved)
                        if kind == 'fifo':
                            os.mkfifo(path)
                        else:
                            path.symlink_to(saved)
                        with patch.object(module, 'run_reference') as run, patch.object(module.os, 'open', wraps=os.open) as opened:
                            with self.assertRaises(ValueError):
                                module.main()
                        run.assert_not_called()
                        self.assertNotIn(path, [c.args[0] for c in opened.call_args_list])

    def test_oversized_inputs_prevent_execution(self):
        for suffix in fixtures.FAMILIES:
            for selected in ('lock', 'manifest', 'payload'):
                with self.subTest(suffix=suffix, selected=selected), tempfile.TemporaryDirectory() as directory:
                    module, lock, manifest, checker = fixtures.OfflineLockTests().fixture(Path(directory).resolve(), suffix)
                    path = {'lock': lock, 'manifest': manifest, 'payload': checker}[selected]
                    path.write_bytes(b'x' * (module.MAX_INPUT + 1))
                    with patch.object(module, 'run_reference') as run, self.assertRaisesRegex(ValueError, '1 MiB'):
                        module.main()
                    run.assert_not_called()

    def test_tree_entry_limit_and_exact_read_limit(self):
        for suffix in fixtures.FAMILIES:
            with self.subTest(suffix=suffix), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                module, _, _, checker = fixtures.OfflineLockTests().fixture(root, suffix)
                checker.write_bytes(b'x' * module.MAX_INPUT)
                self.assertEqual(len(module.read_input(checker, root)), module.MAX_INPUT)
                tree = root / 'tree'
                tree.mkdir()
                for index in range(2000):
                    (tree / str(index)).mkdir()
                self.assertEqual(module.release_files(tree), [])
                (tree / 'overflow').mkdir()
                with self.assertRaisesRegex(ValueError, '2000 entries'):
                    module.release_files(tree)

    def test_replacement_and_growth_reject_and_close_descriptor(self):
        for suffix in fixtures.FAMILIES:
            for change in ('replace', 'grow'):
                with self.subTest(suffix=suffix, change=change), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    module, _, _, checker = fixtures.OfflineLockTests().fixture(root, suffix)
                    original_open, original_read = os.open, os.read
                    descriptors = []
                    grown = False
                    def open_file(path, flags):
                        if change == 'replace':
                            replacement = root / 'replacement'
                            replacement.write_bytes(b'replaced')
                            replacement.replace(checker)
                        fd = original_open(path, flags)
                        descriptors.append(fd)
                        return fd
                    def read_file(fd, size):
                        nonlocal grown
                        chunk = original_read(fd, size)
                        if change == 'grow' and chunk and not grown:
                            grown = True
                            with checker.open('ab') as target:
                                target.write(b'extra')
                        return chunk
                    with patch.object(module.os, 'open', side_effect=open_file), patch.object(module.os, 'read', side_effect=read_file):
                        with self.assertRaisesRegex(ValueError, 'changed'):
                            module.read_input(checker, root)
                    self.assertEqual(len(descriptors), 1)
                    with self.assertRaises(OSError):
                        os.fstat(descriptors[0])
