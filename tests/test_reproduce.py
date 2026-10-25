# SPDX-License-Identifier: BSD-2-Clause
"""Source additions must not disappear behind a check of original files only."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from reproduce import inventory, verify_sources, tool_identity, verify_tool


class SourceInventory(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.TemporaryDirectory()
        self.addCleanup(self.work.cleanup)
        self.root = Path(self.work.name)
        (self.root / "kernel").mkdir()
        self.file = self.root / "kernel/main.zig"
        self.file.write_text("original")
        self.expected = inventory(self.root)

    def test_unchanged_source_and_generated_outputs(self):
        for name in (".deps", ".zig-cache", "zig-out", "kernel/__pycache__"):
            folder = self.root / name
            folder.mkdir(parents=True)
            (folder / "generated").write_text("output")
        verify_sources(self.root, self.expected)

    def test_added_source_rejected(self):
        (self.root / "kernel/new.zig").write_text("added")
        with self.assertRaisesRegex(RuntimeError, r"added=.*kernel/new.zig"):
            verify_sources(self.root, self.expected)

    def test_added_root_file_rejected(self):
        (self.root / "build.zig").write_text("added")
        with self.assertRaisesRegex(RuntimeError, r"added=.*build.zig"):
            verify_sources(self.root, self.expected)

    def test_modified_source_rejected(self):
        self.file.write_text("modified")
        with self.assertRaisesRegex(RuntimeError, r"modified=.*kernel/main.zig"):
            verify_sources(self.root, self.expected)

    def test_removed_source_rejected(self):
        self.file.unlink()
        with self.assertRaisesRegex(RuntimeError, r"removed=.*kernel/main.zig"):
            verify_sources(self.root, self.expected)

    def test_same_bytes_symlink_rejected(self):
        other = self.root / "original"
        other.write_bytes(self.file.read_bytes())
        self.file.unlink()
        self.file.symlink_to(other)
        with self.assertRaisesRegex(RuntimeError, "must not be symlinks"):
            verify_sources(self.root, self.expected)

    def test_nested_output_name_is_not_excluded(self):
        folder = self.root / "kernel/zig-out"
        folder.mkdir()
        (folder / "new.zig").write_text("added")
        with self.assertRaisesRegex(RuntimeError, r"added=.*kernel/zig-out/new.zig"):
            verify_sources(self.root, self.expected)


class ToolIdentity(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.TemporaryDirectory()
        self.addCleanup(self.work.cleanup)
        self.root = Path(self.work.name)
        self.tool = self.root / "compiler"
        self.tool.write_bytes(b"first compiler bytes")
        self.tool.chmod(0o700)
        self.env = {"PATH": str(self.root)}

    def test_unchanged_executable(self):
        expected = tool_identity("compiler", self.env)
        self.assertEqual(expected["resolved_path"], str(self.tool.resolve()))
        self.assertEqual(len(expected["sha256"]), 64)
        verify_tool("compiler", expected, self.env)

    def test_changed_bytes_rejected(self):
        expected = tool_identity("compiler", self.env)
        self.tool.write_bytes(b"changed compiler bytes")
        with self.assertRaisesRegex(RuntimeError, "tool identity changed"):
            verify_tool("compiler", expected, self.env)

    def test_same_bytes_retarget_rejected(self):
        other = self.root / "other"
        other.write_bytes(self.tool.read_bytes())
        other.chmod(0o700)
        link = self.root / "launcher"
        link.symlink_to(self.tool)
        expected = tool_identity("launcher", self.env)
        link.unlink()
        link.symlink_to(other)
        with self.assertRaisesRegex(RuntimeError, "tool identity changed"):
            verify_tool("launcher", expected, self.env)

    def test_missing_executable_rejected(self):
        expected = tool_identity("compiler", self.env)
        self.tool.unlink()
        with self.assertRaises(FileNotFoundError):
            verify_tool("compiler", expected, self.env)

    def test_path_selection_change_rejected(self):
        expected = tool_identity("compiler", self.env)
        alternate = self.root / "alternate"
        alternate.mkdir()
        tool = alternate / "compiler"
        tool.write_bytes(self.tool.read_bytes())
        tool.chmod(0o700)
        with self.assertRaisesRegex(RuntimeError, "tool identity changed"):
            verify_tool("compiler", expected, {"PATH": str(alternate)})
