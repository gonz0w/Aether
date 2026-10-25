#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Exercise adoption integrity failures in a private temporary fixture."""

import hashlib
from pathlib import Path
import runpy
import tempfile
import unittest

CHECK = Path(__file__).with_name("check.py")


class IntegrityTests(unittest.TestCase):
    def test_integrity_boundaries(self):
        verify = runpy.run_path(str(CHECK))["verify_snapshot"]
        with tempfile.TemporaryDirectory(prefix="userland-quality-") as name:
            root = Path(name).resolve()
            snapshot = root / "snapshot"
            snapshot.mkdir()
            quality = root / "docs/quality"
            quality.mkdir(parents=True)
            source = snapshot / "input.txt"
            source.write_bytes(b"approved content\n")
            manifest = snapshot / "SHA256SUMS"
            manifest.write_text(
                hashlib.sha256(source.read_bytes()).hexdigest()
                + "  input.txt\n"
            )
            pin = quality / "drafts.sha256"
            pin.write_text(hashlib.sha256(manifest.read_bytes()).hexdigest())
            # The same validator checks additive snapshots with explicit paths.
            verify(snapshot, pin)
            source.write_bytes(b"changed content\n")
            with self.assertRaisesRegex(ValueError, "content mismatch"):
                verify(snapshot, pin)
            source.write_bytes(b"approved content\n")
            verify.__globals__["ROOT"] = root
            verify.__globals__["SNAPSHOT"] = snapshot
            verify()
            source.write_bytes(b"changed content\n")
            with self.assertRaisesRegex(ValueError, "content mismatch"):
                verify()
            source.write_bytes(b"approved content\n")
            extra = snapshot / "extra"
            extra.write_bytes(b"unapproved")
            with self.assertRaisesRegex(ValueError, "inventory mismatch"):
                verify()
            extra.unlink()
            extra.symlink_to(source)
            with self.assertRaisesRegex(ValueError, "symlink"):
                verify()
            extra.unlink()
            pin.write_text("0" * 64)
            with self.assertRaisesRegex(ValueError, "pin mismatch"):
                verify()


if __name__ == "__main__":
    unittest.main()
