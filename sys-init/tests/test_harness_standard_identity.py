# SPDX-License-Identifier: BSD-2-Clause
"""Persistent mutation checks around a synthetic reference invocation."""
from pathlib import Path
import hashlib
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import test_harness_offline_locks as fixtures


class StandardIdentityTests(unittest.TestCase):
    def mutate(self, kind, lock, manifest, checker):
        path = {'lock': lock, 'manifest': manifest, 'payload': checker}.get(kind)
        if path is not None:
            path.write_bytes(path.read_bytes() + b'\n')
        elif kind == 'extra':
            (manifest.parent / 'extra').write_text('extra')
        elif kind == 'missing':
            checker.unlink()
        else:
            moved = checker.with_name('saved')
            checker.rename(moved)
            checker.symlink_to(moved)

    def test_late_verification_mutations_prevent_execution(self):
        for suffix in fixtures.FAMILIES:
            for kind in ('lock', 'manifest', 'payload', 'extra', 'missing', 'symlink'):
                with self.subTest(suffix=suffix, kind=kind), tempfile.TemporaryDirectory() as directory:
                    module, lock, manifest, checker = fixtures.OfflineLockTests().fixture(Path(directory).resolve(), suffix)
                    original = module.read_input
                    changed = False
                    def read(path, root):
                        nonlocal changed
                        raw = original(path, root)
                        if path == checker and not changed:
                            self.mutate(kind, lock, manifest, checker)
                            changed = True
                        return raw
                    with patch.object(module, 'read_input', side_effect=read), patch.object(module, 'run_reference') as run:
                        with self.assertRaises((ValueError, OSError)):
                            module.main()
                    run.assert_not_called()

    def test_child_mutations_prevent_success(self):
        for suffix in fixtures.FAMILIES:
            for kind in ('lock', 'manifest', 'payload', 'extra', 'missing', 'symlink'):
                with self.subTest(suffix=suffix, kind=kind), tempfile.TemporaryDirectory() as directory:
                    module, lock, manifest, checker = fixtures.OfflineLockTests().fixture(Path(directory).resolve(), suffix)
                    def child(*args, **kwargs):
                        self.mutate(kind, lock, manifest, checker)
                    with patch.object(module, 'run_reference', side_effect=child) as run:
                        with self.assertRaises((ValueError, OSError)):
                            module.main()
                    run.assert_called_once()

    def test_real_child_output_does_not_override_postcheck_failure(self):
        for suffix in fixtures.FAMILIES:
            with self.subTest(suffix=suffix), tempfile.TemporaryDirectory() as directory:
                module, lock, manifest, checker = fixtures.OfflineLockTests().fixture(Path(directory).resolve(), suffix)
                checker.write_text('print("child completed")\nwith open(__file__, "a") as source: source.write("\\n")\n')
                manifest.write_text(hashlib.sha256(checker.read_bytes()).hexdigest() + '  conformance/check.py\n')
                rows = lock.read_text().splitlines()
                rows = ['manifest_sha256=' + hashlib.sha256(manifest.read_bytes()).hexdigest() if row.startswith('manifest_sha256=') else row for row in rows]
                lock.write_text('\n'.join(rows) + '\n')
                Path(module.__file__).write_bytes((fixtures.ROOT / 'docs' / ('check-' + suffix + '.py')).read_bytes())
                result = subprocess.run([sys.executable, module.__file__], capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 1, result)
                self.assertEqual(result.stdout, 'child completed\n')
                self.assertIn('payload changed during check', result.stderr)
