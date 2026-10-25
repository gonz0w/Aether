#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Offline adoption integrity and documentation inventory checks (Python 3.10+)."""

import argparse
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / "docs/vendor/aether-approved-drafts/2026-09-05"


class Parser(argparse.ArgumentParser):
    """Use the shared usage-error status for this new contributor command."""

    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(64, f"FAILED: {message}\n")


def verify_snapshot(snapshot=None, pin=None):
    """Verify the local review snapshot before loading its validator."""
    snapshot = SNAPSHOT if snapshot is None else snapshot
    pin = ROOT / "docs/quality/drafts.sha256" if pin is None else pin
    manifest = snapshot / "SHA256SUMS"
    expected = pin.read_text().strip()
    if hashlib.sha256(manifest.read_bytes()).hexdigest() != expected:
        raise ValueError("review manifest pin mismatch")
    seen = set()
    for line in manifest.read_text().splitlines():
        digest, name = line.split("  ", 1)
        path = Path(name)
        if path.is_absolute() or ".." in path.parts or name in seen:
            raise ValueError("unsafe or duplicate snapshot path")
        target = snapshot / path
        if any(p.is_symlink() for p in [target, *target.parents]):
            raise ValueError("symlink snapshot path")
        if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise ValueError("snapshot content mismatch: " + name)
        seen.add(name)
    actual = set()
    for path in snapshot.rglob("*"):
        if path.is_symlink():
            raise ValueError("symlink in snapshot")
        if path.is_file() and path != manifest:
            actual.add(path.relative_to(snapshot).as_posix())
    if not seen or actual != seen:
        raise ValueError("snapshot inventory mismatch")


def main():
    parser = Parser(description=__doc__)
    parser.add_argument("--version", action="version", version="quality 0.1.0")
    parser.add_argument(
        "--release", action="store_true",
        help="require complete documentation inventory; not release approval",
    )
    args = parser.parse_args()
    verify_snapshot()
    verify_snapshot(
        ROOT / "docs/vendor/aether-review-snapshots/2026-09-07/coding-v0.2.0",
        ROOT / "docs/quality/simplicity.sha256",
    )
    run_checked = runpy.run_path(str(
        ROOT / "docs/quality/processes.py"
    ))["run_checked"]
    run_checked(
        [sys.executable, "-B", str(ROOT / "docs/quality/test-check.py")], 30,
    )
    for name in ("standards", "distribution", "experience"):
        # Each wrapper owns its reference process; do not nest session owners.
        runpy.run_path(str(ROOT / "docs" / f"check-{name}.py"))["main"]()
    validator = runpy.run_path(str(
        SNAPSHOT / "drafts/documentation-v0.1.0/conformance/check.py"
    ))["validate_inventory"]
    inventory = json.loads((ROOT / "docs/quality/coverage.json").read_text())
    validator(inventory, ROOT, release=args.release)
    print("PASS: pinned standards and documentation inventory structure")
    print("NOT RUN: runtime, full source audit, reader and publication gates")


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print(f"FAILED: {error}", file=sys.stderr)
        sys.exit(1)
