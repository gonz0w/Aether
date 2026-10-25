# SPDX-License-Identifier: BSD-2-Clause
"""Migration may preserve provenance without allowing arbitrary stale source reuse."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import source_paths as paths


class SourcePaths(unittest.TestCase):
    def test_exact_component_prefixes_and_unrelated_paths(self):
        self.assertEqual(paths.relocate(paths.LEGACY / 'Aether-userland/x'), paths.ROOT / 'userland/x')
        for name in ('sys-init', 'pkg-mgr'):
            self.assertEqual(paths.relocate(paths.LEGACY / name / 'x'), paths.ROOT / name / 'x')
        for name in ('Aether-standards', 'Aether-userland-other'):
            path = paths.LEGACY / name / 'x'
            self.assertEqual(paths.relocate(path), path)

    def test_only_exact_pinned_tooling_uses_frozen_provenance(self):
        pins = json.loads((paths.TOOLING / 'pins.json').read_text())
        for name, expected in pins.items():
            path = paths.ROOT / name
            frozen = paths.dependency_input(path, expected)
            self.assertEqual(hashlib.sha256(frozen.read_bytes()).hexdigest(), expected)
            self.assertEqual(paths.dependency_input(path, '0' * 64), path)
        runtime = paths.ROOT / 'kernel/native_fs_session.zig'
        self.assertEqual(paths.dependency_input(runtime, next(iter(pins.values()))), runtime)

    def test_catalog_and_frozen_tool_drift_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = (paths.TOOLING / 'pins.json').read_bytes()
            (root / 'pins.json').write_bytes(raw)
            name, expected = next(iter(json.loads(raw).items()))
            (root / Path(name).name).write_bytes(b'changed')
            with patch.object(paths, 'TOOLING', root):
                with self.assertRaisesRegex(ValueError, 'provenance changed'):
                    paths.dependency_input(paths.ROOT / name, expected)
                (root / 'pins.json').write_bytes(b'{}')
                with self.assertRaisesRegex(ValueError, 'catalog changed'):
                    paths.dependency_input(paths.ROOT / name, expected)
