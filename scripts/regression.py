"""Bounded M4 target regression; each run owns a fresh output directory."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from evidence import compact_run
from deps import ROOT
from emulator import run

CASES = (
    ("positive", None),
    ("skip-remote-unmap", b"remote stale mapping retained"),
    ("skip-remote-zero", b"remote code not cleared"),
    ("skip-remote-discard", b"remote transport not drained"),
    ("drop-remote-terminal", b"SMP supervisor fault; resources reserved"),
    ("skip-display-draw", None),
    ("bad-stream-generation", b"display service checks failed"),
)

TERMINAL_CONTEXT = (
    b"REMOTE: AP confirmed stopped, unmapped and zeroed backing",
    b"REMOTE: unsolicited AP user fault retained (#UD)",
)

STALE_RESULT_CONTEXT = (
    b"REMOTE: AP confirmed stopped, unmapped and zeroed backing",
    b"DISPLAY: second-generation result rejected after 20 acknowledgments",
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inputs():
    paths = [ROOT / "build.zig", ROOT / "rust-toolchain.toml", ROOT / "LICENSE"]
    for directory in ("kernel", "user", "scripts", "boot"):
        paths.extend(path for path in (ROOT / directory).rglob("*")
                     if path.is_file() and "__pycache__" not in path.parts)
    return {str(path.relative_to(ROOT)): digest(path) for path in sorted(paths)}


def regression():
    parent = ROOT / "zig-out"
    parent.mkdir(exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix="regression-", dir=parent))
    print("[RUNNING] Regression evidence:", output, file=sys.stderr, flush=True)
    record = {"format": "aether-m4-regression-v1", "status": "incomplete",
              "scope": "current working-tree build, two-core QEMU; not clean-checkout reproduction",
              "inputs": inputs(), "cases": []}
    try:
        for name, panic in CASES:
            destination = output / name
            destination.mkdir()
            command = ["zig", "build", "-p", str(destination),
                       "--cache-dir", str(ROOT / ".zig-cache"),
                       "--global-cache-dir", str(ROOT / ".zig-cache/global")]
            if name != "positive":
                command.append(f"-D{name}=true")
            case = {"name": name, "command": command, "status": "incomplete",
                    "expected_panic": panic.decode() if panic else None}
            context = TERMINAL_CONTEXT if name == "drop-remote-terminal" else ()
            if name == "bad-stream-generation":
                context = STALE_RESULT_CONTEXT
            pixel_failure = name == "skip-display-draw"
            case["panic_context"] = [line.decode() for line in context]
            case["expected_pixel_failure"] = pixel_failure
            record["cases"].append(case)
            print("[RUNNING]", name, file=sys.stderr, flush=True)
            with (destination / "build.log").open("wb") as log:
                subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                               check=True, timeout=180)
            image = destination / "aether.iso"
            case["image_sha256"] = digest(image)
            run("smoke", image, expected_panic=panic, panic_context=context,
                expected_pixel_failure=pixel_failure)
            case["serial_sha256"] = digest(destination / "serial.log")
            case["status"] = "pass"
        if inputs() != record["inputs"]:
            raise RuntimeError("build inputs changed during regression; rerun with stable sources")
        record["status"] = "pass"
    finally:
        (output / "results.json").write_text(json.dumps(record, indent=2) + "\n")
        compact_run(output, record)
    print(f"[PASS] All {len(CASES)} target cases passed. Evidence:", output)


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(64, f"[ERROR] {message}\n")


if __name__ == "__main__":
    parser = Parser(description=__doc__, epilog="Example: python3 scripts/regression.py. "
                    "Requires pinned build/QEMU tools and completed dependency setup. "
                    "Keeps logs in a fresh zig-out/regression-* directory; no physical disk is modified.")
    parser.add_argument("--version", action="version", version="aether-m4-regression 1")
    parser.parse_args()
    try:
        regression()
    except KeyboardInterrupt:
        sys.exit(130)
    except (OSError, RuntimeError, TimeoutError, subprocess.SubprocessError) as error:
        print(f"[FAIL] {error}", file=sys.stderr)
        sys.exit(1)
