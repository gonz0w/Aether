# SPDX-License-Identifier: BSD-2-Clause
"""Private descriptor facade with a deterministic host transport witness."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class ScratchClient(unittest.TestCase):
    def test_adapter(self):
        root = Path(__file__).resolve().parents[1]
        directory = Path(tempfile.mkdtemp(prefix='scratch-client-host-', dir=root / 'zig-out'))
        compiler = '/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang'
        binary = directory / 'adapter'
        commands = [
            [compiler, '-std=c11', '-D_DARWIN_C_SOURCE', '-Wall', '-Wextra',
             '-Werror', '-O2', str(root / 'tests/scratch_client.c'), '-o', str(binary)],
            [str(binary)],
        ]
        receipts = []
        for command in commands:
            result = subprocess.run(command, capture_output=True, text=True, timeout=180)
            receipts.append({'command': command, 'exit': result.returncode,
                             'stdout': result.stdout, 'stderr': result.stderr})
            (directory / 'checks.json').write_text(json.dumps(receipts, indent=2))
            self.assertEqual(result.returncode, 0, f'Retained {directory}: {result.stderr}')
            if command[0] == str(binary):
                self.assertIn('scratch adapter checks passed', result.stdout)
        shutil.rmtree(directory)
