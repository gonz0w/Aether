# SPDX-License-Identifier: BSD-2-Clause
"""Reject incompatible service-volume selections before dependency/device work."""
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import block_smoke


class BlockProfile(unittest.TestCase):
    def test_service_backing_requires_native_regions_before_setup(self):
        with patch.object(block_smoke, 'verify') as verify:
            for native, regions in ((False, False), (True, False), (False, True)):
                with self.subTest(native=native, regions=regions), self.assertRaises(RuntimeError):
                    block_smoke.suite(native=native, regions=regions, service_memory=True)
            verify.assert_not_called()

    def test_cli_usage_rejects_incompatible_service_profile(self):
        runner = Path(block_smoke.__file__)
        for flags in (['--service-memory'], ['--service-memory', '--native'],
                      ['--service-memory', '--regions']):
            with self.subTest(flags=flags):
                result = subprocess.run([sys.executable, runner, *flags], capture_output=True, timeout=10)
                self.assertEqual(result.returncode, 64)
                self.assertFalse(result.stdout)
                self.assertNotIn(b'[RUNNING]', result.stderr)
