# SPDX-License-Identifier: BSD-2-Clause
"""Run the Rust descriptor preparation tests through the existing host suite."""
from pathlib import Path
import subprocess
import tempfile
import unittest


class ExecDescriptors(unittest.TestCase):
    def test_preparation(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(prefix='aether-exec-fds-') as directory:
            binary = str(Path(directory) / 'exec-fds')
            compile_result = subprocess.run(
                ['rustc', '+1.98.0', '--edition=2024', '--test',
                 str(root / 'user/native-connections/exec_fds.rs'), '-o', binary],
                capture_output=True, text=True, timeout=180)
            self.assertEqual(compile_result.returncode, 0, compile_result.stderr)
            result = subprocess.run([binary], capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
