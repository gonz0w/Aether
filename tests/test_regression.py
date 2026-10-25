"""Pixel-negative acceptance must not hide capture or format failures."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from emulator import FramebufferMismatch, verify_framebuffer


class PixelNegative(unittest.TestCase):
    def test_complete_wrong_pixels_are_expected_only_when_requested(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "capture.ppm"
            path.write_bytes(b"P6\n800 600\n255\n" + bytes(800 * 600 * 3))
            verify_framebuffer(path, display=True, expected_failure=True)
            with self.assertRaises(FramebufferMismatch):
                verify_framebuffer(path, display=True)

    def test_missing_and_malformed_capture_never_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "capture.ppm"
            with self.assertRaises(FileNotFoundError):
                verify_framebuffer(path, expected_failure=True)
            for data in (b"", b"P6\n800 600\n255\nshort",
                         b"P6\n1 1\n255\n" + bytes(3)):
                path.write_bytes(data)
                with self.subTest(data=data):
                    with self.assertRaises((RuntimeError, ValueError)):
                        verify_framebuffer(path, expected_failure=True)

    def test_successful_pixel_check_cannot_satisfy_negative(self):
        with patch("emulator.check_framebuffer", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "unexpected correct framebuffer"):
                verify_framebuffer(Path("unused"), expected_failure=True)


if __name__ == "__main__":
    unittest.main()
