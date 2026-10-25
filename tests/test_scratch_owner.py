# SPDX-License-Identifier: BSD-2-Clause
"""Exercise the scratch open-description owner independently of its native transport."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class ScratchOwner(unittest.TestCase):
    def test_owner(self):
        root = Path(__file__).resolve().parents[1]
        directory = Path(tempfile.mkdtemp(prefix='scratch-owner-host-', dir=root / 'zig-out'))
        source = root / 'user/native-connections/scratch_owner.rs'
        wrapper = directory / 'core.rs'
        wrapper.write_text('#![no_std]\n#[path = ' + json.dumps(str(source)) + ']\npub mod scratch_owner;\n')
        binary = directory / 'tests'
        commands = [
            ['rustc', '+1.98.0', '--edition=2024', '--test', str(source), '-o', str(binary)],
            [str(binary), '--nocapture'],
            ['rustc', '+1.98.0', '--edition=2024', '--crate-type=lib',
             '--target=x86_64-unknown-none', '--cfg=shell_files', '-Cpanic=abort', '--emit=obj',
             str(wrapper), '-o', str(directory / 'scratch-owner.o')],
        ]
        receipts = []
        for command in commands:
            result = subprocess.run(command, capture_output=True, text=True, timeout=180)
            receipts.append({'command': command, 'returncode': result.returncode,
                             'stdout': result.stdout, 'stderr': result.stderr})
            (directory / 'checks.json').write_text(json.dumps(receipts, indent=2))
            self.assertEqual(result.returncode, 0, f'Retained {directory}: {result.stderr}')
            if command[0] == str(binary):
                self.assertIn('33 passed; 0 failed', result.stdout, f'Retained {directory}')
        shutil.rmtree(directory)
