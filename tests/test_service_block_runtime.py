# SPDX-License-Identifier: BSD-2-Clause
"""Volume composition must never select an external disk or fabricated reboot."""
from pathlib import Path
import subprocess
import sys
import unittest
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import native_smoke
from service_runtime_smoke import check_trace, suite


class ServiceBlockRuntime(unittest.TestCase):
    def test_profiles_and_standalone_verify_reject_before_intake(self):
        for case, profile in (('block-write', False), ('block-verify', True),
                              ('normal', True), ('block-readonly', False)):
            with self.subTest(case=case), self.assertRaises(ValueError):
                suite(Path('/missing'), case, block_region=profile)
        with self.assertRaises(ValueError):
            suite(Path('/missing'), block_region=True, rtc_source=True)
        for flags in (['--block-region', '--case', 'block-verify'],
                      ['--case', 'block-write'], ['--block-region', '--rtc-source'],
                      ['--block-region', '--disk', '/dev/disk0']):
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/service_runtime_smoke.py'),
                                     '--delivery', '/missing', *flags], capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 64)
            self.assertNotIn(b'[RUNNING]', result.stderr)

    def test_unowned_disk_is_rejected_before_emulator(self):
        with patch.object(native_smoke, 'verify', side_effect=AssertionError('must not launch')):
            for disk in ('/dev/disk0', '/tmp/disposable.raw', '/missing/user.raw'):
                with self.subTest(disk=disk), self.assertRaises(ValueError):
                    native_smoke.run('/missing/profile/aether.iso', block_disk=disk)

    def test_large_disposable_selection_preserves_exact_default_and_ownership(self):
        with tempfile.TemporaryDirectory(prefix='thread-suite-service-runtime-guard-', dir=ROOT / 'zig-out') as directory:
            owner = Path(directory)
            case = owner / 'case'
            case.mkdir()
            image = case / 'aether.iso'
            disk = case / 'disposable.raw'
            for size, large, accepted in ((16 * 1024 * 1024, False, True),
                                          (16 * 1024 * 1024, True, False),
                                          (64 * 1024 * 1024 + 8192, False, False),
                                          (64 * 1024 * 1024 + 8192, True, True),
                                          (64 * 1024 * 1024, True, False)):
                with disk.open('wb') as stream:
                    stream.truncate(size)
                with patch.object(native_smoke, 'verify', side_effect=RuntimeError('guard accepted')) as verify:
                    with self.assertRaisesRegex(RuntimeError if accepted else ValueError,
                                                'guard accepted' if accepted else 'selected exact size'):
                        native_smoke.run(image, block_disk=disk, block_large=large)
                    self.assertEqual(verify.call_count, int(accepted))
            disk.unlink()
            (owner / 'real.raw').write_bytes(b'private')
            disk.symlink_to(owner / 'real.raw')
            with patch.object(native_smoke, 'verify', side_effect=AssertionError('must not launch')):
                with self.assertRaises(ValueError):
                    native_smoke.run(image, block_disk=disk, block_large=True)
                with self.assertRaises(ValueError):
                    native_smoke.run(image, block_large=True)

    def test_block_trace_retains_generation_and_marker_boundaries(self):
        serial = ''.join(f'NATIVE terminal slot={slot} generation={gen} kind=1 detail=0\n'
                         for slot, gen in ((0, 1), (1, 1), (0, 2)))
        serial += 'NATIVE supervisor result=100 reclaimed=3\nAETHER NATIVE BLOCK PASS\n'
        self.assertEqual(check_trace(serial, marker='AETHER NATIVE BLOCK PASS')['reclaimed'], 3)
        for changed in (serial.replace('reclaimed=3', 'reclaimed=2'),
                        serial.replace('generation=2', 'generation=1'),
                        serial.replace('AETHER NATIVE BLOCK PASS', 'AETHER NATIVE SUPERVISION PASS')):
            with self.assertRaises(ValueError):
                check_trace(changed, marker='AETHER NATIVE BLOCK PASS')
        with self.assertRaises(ValueError):
            check_trace(serial)


if __name__ == '__main__':
    unittest.main()
