# SPDX-License-Identifier: BSD-2-Clause
import copy
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import test_harness_static_records as records

check = records.check


class StaticInputTests(unittest.TestCase):
    def test_regular_file_limit_and_parent_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'actual').mkdir();path=root/'actual/input'
            path.write_bytes(b'x'*check.MAX_FILE)
            self.assertEqual(len(check.read_input(path,root)),check.MAX_FILE)
            path.write_bytes(b'x'*(check.MAX_FILE+1))
            with self.assertRaisesRegex(ValueError,'1 MiB'):check.read_input(path,root)
            path.write_bytes(b'ok');(root/'alias').symlink_to(root/'actual',target_is_directory=True)
            with self.assertRaisesRegex(ValueError,'symlink'):check.read_input(root/'alias/input',root)
            with self.assertRaisesRegex(ValueError,'ordinary file'):check.read_input(root/'actual',root)

    def test_fifo_is_rejected_without_waiting_for_writer(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);fifo=root/'pipe';os.mkfifo(fifo)
            script=('import importlib.util,pathlib;'
                    f's=importlib.util.spec_from_file_location("probe",{check.__file__!r});'
                    'm=importlib.util.module_from_spec(s);s.loader.exec_module(m);'
                    f'm.read_input(pathlib.Path({str(fifo)!r}),pathlib.Path({str(root)!r}))')
            result=subprocess.run([check.sys.executable,'-c',script],capture_output=True,timeout=2)
            self.assertNotEqual(result.returncode,0)
            self.assertIn(b'input must be an ordinary file',result.stderr)

    def test_replacement_between_inspection_and_open_rejects(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);path=root/'input';path.write_bytes(b'before')
            replacement=root/'replacement';replacement.write_bytes(b'after')
            original=os.open
            def swap(*args,**kwargs):
                replacement.replace(path)
                return original(*args,**kwargs)
            with patch.object(check.os,'open',side_effect=swap):
                with self.assertRaisesRegex(ValueError,'changed before read'):check.read_input(path,root)

    def test_growth_during_read_rejects(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);path=root/'input';path.write_bytes(b'before')
            original=os.read;changed=False
            def grow(*args,**kwargs):
                nonlocal changed
                value=original(*args,**kwargs)
                if not changed:
                    with path.open('ab') as output:output.write(b'after')
                    changed=True
                return value
            with patch.object(check.os,'read',side_effect=grow):
                with self.assertRaisesRegex(ValueError,'changed during read'):check.read_input(path,root)

    def test_metadata_byte_changes_reject_even_with_valid_semantics(self):
        for name in ['native-boundaries.json','static-tools.json']:
            with self.subTest(name=name),tempfile.TemporaryDirectory() as directory:
                root=Path(directory);(root/'docs').mkdir()
                for file in ['native-boundaries.json','static-tools.json']:
                    (root/'docs'/file).write_bytes((check.ROOT/'docs'/file).read_bytes())
                tool=root/'tool';tool.write_bytes(b'fake tool');identity=check.digest(tool.read_bytes())
                def mutate(*args):
                    target=root/'docs'/name
                    target.write_bytes(target.read_bytes()+b'\n')
                    return {}
                # Tool execution is mocked; select the fixture's pinned platform too.
                with patch.object(check.platform,'system',return_value='Darwin'),patch.object(check.platform,'machine',return_value='arm64'),patch.object(check,'check_boundaries',return_value=13),patch.object(check,'sources',return_value={}),patch.object(check,'command',return_value=str(tool).encode()),patch.object(check,'identify_tool',return_value=identity),patch.object(check,'check_clippy',side_effect=mutate):
                    with self.assertRaisesRegex(ValueError,'static record changed'):check.run(root)
