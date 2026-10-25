# SPDX-License-Identifier: BSD-2-Clause
"""Denials for the imported, native-only matched owner constructor."""
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import home_owner_build as owner


class OwnerBuildTests(unittest.TestCase):
    def test_exact_profile(self):
        flags = owner.profile_flags()
        owner.require_profile(flags)
        for name in ("home", "home_wire", "in_place", "home_in_place", "home_owner", "file_write_wire"):
            changed = flags.copy()
            index = changed.index("fs_" + name)
            del changed[index - 1:index + 1]
            with self.assertRaisesRegex(ValueError, "profile"):
                owner.require_profile(changed)

    def test_extra_profile_denied(self):
        for extra in ("fs_home_native", "fs_home_probe_three", "fs_cwd"):
            with self.assertRaisesRegex(ValueError, "profile"):
                owner.require_profile([*owner.profile_flags(), "--cfg", extra])

    def test_input_change_or_absence_denied(self):
        with tempfile.TemporaryDirectory() as name:
            path = Path(name) / "source.rs"
            path.write_bytes(b"authoritative source\n")
            frozen = {str(path): hashlib.sha256(path.read_bytes()).hexdigest()}
            owner.verify_inputs(frozen)
            path.write_bytes(b"changed source\n")
            with self.assertRaisesRegex(ValueError, "input"):
                owner.verify_inputs(frozen)
            path.unlink()
            with self.assertRaisesRegex(ValueError, "input"):
                owner.verify_inputs(frozen)

    def fixture(self):
        return dict(code_bytes=47384, code_budget=49152, code_fits=True,
                    runtime_bytes=3688, alignment=8, workspace_bytes=4096,
                    mapped_bytes=8192, resident_fits=True, native_executed=False,
                    stack=dict(status="pass", entry_stack_bytes=8160, usable_stack_bytes=8184))

    def test_real_fit_accepted(self):
        owner.validate_measurement(self.fixture())

    def test_forged_fit_booleans_do_not_hide_overflow(self):
        for field, value in (("code_bytes", 49153), ("runtime_bytes", 4097),
                             ("workspace_bytes", 4095), ("mapped_bytes", 12288),
                             ("code_budget", 65536), ("native_executed", True)):
            changed = self.fixture()
            changed[field] = value
            with self.assertRaisesRegex(ValueError, "measurement"):
                owner.validate_measurement(changed)

    def test_stack_limit_and_blocked_analysis_denied(self):
        for stack in (dict(status="pass", entry_stack_bytes=8185, usable_stack_bytes=8184),
                      dict(status="blocked"),
                      dict(status="pass", entry_stack_bytes=8160, usable_stack_bytes=8192)):
            changed = self.fixture()
            changed["stack"] = stack
            with self.assertRaisesRegex(ValueError, "measurement"):
                owner.validate_measurement(changed)


if __name__ == "__main__":
    unittest.main()
