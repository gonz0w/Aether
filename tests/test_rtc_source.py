# SPDX-License-Identifier: BSD-2-Clause
"""Reject invalid source-profile selection before intake or emulator startup."""
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import native_smoke
from service_runtime_smoke import suite


class RTCSource(unittest.TestCase):
    def test_profile_selection_cannot_enter_unrequested_delivery(self):
        for name in ('rtc', 'rtc-leap', 'rtc-disabled'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                suite(Path('/missing'), name)
        with self.assertRaises(ValueError):
            suite(Path('/missing'), 'normal', rtc_source=True)
        with self.assertRaises(ValueError):
            suite(Path('/missing'), engine_native=True, rtc_source=True)
        for flags in (['--case', 'rtc'], ['--rtc-source', '--case', 'normal'],
                      ['--rtc-source', '--engine-native']):
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/service_runtime_smoke.py'),
                                     '--delivery', '/missing', *flags], capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 64)
            self.assertNotIn(b'[RUNNING]', result.stderr)

    def test_invalid_calendar_and_emulator_options_reject_before_launch(self):
        with patch.object(native_smoke, 'verify', side_effect=AssertionError('must not launch')):
            for value in ('2001-02-29T12:34:00', '2000-02-29T24:34:00',
                          '2026-10-06T12:34:00,clock=host', '2026-1-06T12:34:00', 0):
                with self.subTest(value=value), self.assertRaises(ValueError):
                    native_smoke.run('/missing.iso', rtc_base=value)


if __name__ == '__main__':
    unittest.main()
