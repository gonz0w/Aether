# SPDX-License-Identifier: BSD-2-Clause
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import test_harness_offline_locks as fixtures


class PrivateStandardTests(unittest.TestCase):
    def reseal(self, lock, manifest, checker, code):
        checker.write_text(code)
        manifest.write_text(hashlib.sha256(checker.read_bytes()).hexdigest() + '  conformance/check.py\n')
        lock.write_text('\n'.join('manifest_sha256=' + hashlib.sha256(manifest.read_bytes()).hexdigest() if line.startswith('manifest_sha256=') else line for line in lock.read_text().splitlines()) + '\n')

    def test_dispatch_uses_verified_copy_with_python_isolation(self):
        for suffix in fixtures.FAMILIES:
            with self.subTest(suffix=suffix), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                module, lock, manifest, checker = fixtures.OfflineLockTests().fixture(root, suffix)
                marker = root / 'executed'
                self.reseal(lock, manifest, checker,
                            'import os,sys\nfrom pathlib import Path\n'
                            'assert sys.flags.isolated and sys.flags.no_site\n'
                            'assert sys.flags.optimize == 0 and sys.dont_write_bytecode\n'
                            'Path(os.environ["PRIVATE_TEST_MARKER"]).write_text(__file__)\n')
                (root / 'sitecustomize.py').write_text('raise RuntimeError("site injection")\n')
                original_run = subprocess.run
                paths = []
                def dispatch(command, **kwargs):
                    paths.append(Path(command[-1]))
                    self.assertNotEqual(paths[-1], checker)
                    checker.write_text('raise RuntimeError("original replacement executed")\n')
                    return original_run(command, **kwargs, capture_output=True, timeout=10)
                with patch.dict(os.environ, PYTHONPATH=str(root), PYTHONOPTIMIZE='2', PRIVATE_TEST_MARKER=str(marker)), patch.object(module, 'run_reference', side_effect=dispatch):
                    with self.assertRaisesRegex(ValueError, 'payload changed'):
                        module.main()
                self.assertEqual(Path(marker.read_text()), paths[0])
                self.assertFalse(paths[0].exists(), 'temporary release leaked')

    def test_cleanup_after_child_failure(self):
        for suffix in fixtures.FAMILIES:
            with self.subTest(suffix=suffix), tempfile.TemporaryDirectory() as directory:
                module, _, _, _ = fixtures.OfflineLockTests().fixture(Path(directory).resolve(), suffix)
                paths = []
                def fail(command, **kwargs):
                    paths.append(Path(command[-1]))
                    self.assertTrue(paths[-1].is_file())
                    raise subprocess.CalledProcessError(7, command)
                with patch.object(module, 'run_reference', side_effect=fail), self.assertRaises(subprocess.CalledProcessError):
                    module.main()
                self.assertFalse(paths[0].exists())

    def test_staging_budget_prevents_execution(self):
        for suffix in fixtures.FAMILIES:
            with self.subTest(suffix=suffix), tempfile.TemporaryDirectory() as directory:
                module, _, _, _ = fixtures.OfflineLockTests().fixture(Path(directory).resolve(), suffix)
                with patch.object(module, 'MAX_STAGE', 1), patch.object(module, 'run_reference') as run:
                    with self.assertRaisesRegex(ValueError, '64 MiB'):
                        module.main()
                run.assert_not_called()
