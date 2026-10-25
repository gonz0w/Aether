"""Exercise actual process exit/timeout and serial failure handling."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from emulator import wait_for_boot, check_framebuffer


class SmokeFailures(unittest.TestCase):
    def exercise(self, content, timeout=0.15, exited=False, marker=None, expected_panic=None, panic_context=()):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "serial.log"
            log.write_bytes(content)
            process = subprocess.Popen([sys.executable, "-c", "pass" if exited else "import time; time.sleep(5)"])
            try:
                if exited:
                    process.wait()
                if marker is None:
                    wait_for_boot(process, log, timeout, expected_panic=expected_panic, panic_context=panic_context)
                else:
                    wait_for_boot(process, log, timeout, marker)
            finally:
                if process.poll() is None:
                    process.terminate()
                process.wait()

    def test_panic_requires_ordered_context_before_failure(self):
        context = (b"first cleanup", b"second generation fault")
        self.exercise(b"first cleanup\nsecond generation fault\nAETHER PANIC: expected\n",
                      expected_panic=b"expected", panic_context=context)
        for content in (
            b"AETHER PANIC: expected\n",
            b"second generation fault\nfirst cleanup\nAETHER PANIC: expected\n",
            b"first cleanup\nAETHER PANIC: expected\nsecond generation fault\n",
            b"echo first cleanup\nsecond generation fault\nAETHER PANIC: expected\n",
        ):
            with self.subTest(content=content):
                with self.assertRaisesRegex(RuntimeError, "ordered execution context"):
                    self.exercise(content, expected_panic=b"expected", panic_context=context)

    def test_exact_expected_panic_passes(self):
        self.exercise(b"AETHER PANIC: expected\n", expected_panic=b"expected")

    def test_negative_rejects_unrelated_panic(self):
        with self.assertRaisesRegex(RuntimeError, "unexpected kernel panic"):
            self.exercise(b"AETHER PANIC: other\n", expected_panic=b"expected")

    def test_negative_rejects_prefix_and_embedded_panic(self):
        for content in (b"AETHER PANIC: expected extra\n",
                        b"echo AETHER PANIC: expected\n"):
            with self.assertRaisesRegex(RuntimeError, "unexpected kernel panic"):
                self.exercise(content, expected_panic=b"expected")

    def test_negative_rejects_incomplete_line(self):
        with self.assertRaises(TimeoutError):
            self.exercise(b"AETHER PANIC: expected", expected_panic=b"expected")

    def test_negative_rejects_success_even_with_expected_panic(self):
        with self.assertRaisesRegex(RuntimeError, "unexpected boot success"):
            self.exercise(b"AETHER FAULT RECOVERY PASS\nAETHER PANIC: expected\n",
                          expected_panic=b"expected")

    def test_negative_rejects_exit(self):
        with self.assertRaisesRegex(RuntimeError, "exited"):
            self.exercise(b"AETHER PANIC: expected\n", exited=True,
                          expected_panic=b"expected")

    def test_negative_missing_panic_times_out(self):
        with self.assertRaises(TimeoutError):
            self.exercise(b"firmware only\n", expected_panic=b"expected")

    def test_missing_marker_times_out(self):
        with self.assertRaises(TimeoutError):
            self.exercise(b"firmware only\n")

    def test_lifecycle_v1_alone_does_not_pass_default(self):
        with self.assertRaises(TimeoutError):
            self.exercise(b"AETHER LIFECYCLE V1 PASS\n")

    def test_legacy_lifetime_marker_cannot_pass_v1(self):
        with self.assertRaises(TimeoutError):
            self.exercise(b"AETHER LIFETIME PASS\n", marker=b"AETHER LIFECYCLE V1 PASS")

    def test_versioned_lifecycle_marker_passes_one_core(self):
        self.exercise(b"AETHER LIFECYCLE V1 PASS\n", marker=b"AETHER LIFECYCLE V1 PASS")

    def test_static_display_alone_does_not_pass(self):
        with self.assertRaises(TimeoutError):
            self.exercise(b"AETHER DISPLAY PASS\n")

    def test_m3_alone_does_not_pass(self):
        with self.assertRaises(TimeoutError):
            self.exercise(b"AETHER M3 PASS\n")

    def test_cross_core_ipc_alone_does_not_pass(self):
        with self.assertRaises(TimeoutError):
            self.exercise(b"AETHER SMP IPC PASS\n")

    def test_user_smp_alone_does_not_pass(self):
        with self.assertRaises(TimeoutError):
            self.exercise(b"AETHER SMP USER PASS\n")

    def test_kernel_smp_alone_does_not_pass(self):
        with self.assertRaises(TimeoutError):
            self.exercise(b"AETHER SMP BRINGUP PASS\n")

    def test_one_core_alone_does_not_pass(self):
        with self.assertRaises(TimeoutError):
            self.exercise(b"AETHER LIFETIME PASS\n")

    def test_ipc_alone_does_not_pass(self):
        with self.assertRaises(TimeoutError):
            self.exercise(b"AETHER IPC PASS\n")

    def test_scheduler_alone_does_not_pass(self):
        with self.assertRaises(TimeoutError):
            self.exercise(b"AETHER SCHEDULER PASS\n")

    def test_protection_alone_does_not_pass(self):
        with self.assertRaises(TimeoutError):
            self.exercise(b"AETHER PROTECTION PASS\n")

    def test_boot_alone_does_not_pass(self):
        with self.assertRaises(TimeoutError):
            self.exercise(b"AETHER M1 PASS\n")

    def test_supervisor_alone_does_not_pass(self):
        with self.assertRaises(TimeoutError):
            self.exercise(b"AETHER SMP SUPERVISOR PASS\n")

    def test_remote_lifetime_alone_does_not_pass(self):
        with self.assertRaises(TimeoutError):
            self.exercise(b"AETHER REMOTE LIFETIME PASS\n")

    def test_live_display_alone_does_not_pass(self):
        with self.assertRaises(TimeoutError):
            self.exercise(b"AETHER LIVE DISPLAY PASS\n")

    def test_embedded_marker_does_not_pass(self):
        with self.assertRaises(TimeoutError):
            self.exercise(b"echo AETHER FAULT RECOVERY PASS from boot config\n")

    def test_panic_overrides_marker(self):
        with self.assertRaisesRegex(RuntimeError, "kernel panic"):
            self.exercise(b"AETHER FAULT RECOVERY PASS\nAETHER PANIC: broken\n")

    def test_early_exit_fails(self):
        with self.assertRaisesRegex(RuntimeError, "exited"):
            self.exercise(b"", exited=True)

    def test_exact_marker_passes(self):
        self.exercise(b"FB width=800\nAETHER FAULT RECOVERY PASS\n")

    def test_blank_framebuffer_does_not_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "framebuffer.ppm"
            path.write_bytes(b"P6\n800 600\n255\n" + bytes(800 * 600 * 3))
            with self.assertRaisesRegex(RuntimeError, "pixel mismatch"):
                check_framebuffer(path)

    def test_truncated_framebuffer_does_not_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "framebuffer.ppm"
            path.write_bytes(b"P6\n800 600\n255\n" + bytes(30))
            with self.assertRaisesRegex(RuntimeError, "truncated"):
                check_framebuffer(path)


if __name__ == "__main__":
    unittest.main()
