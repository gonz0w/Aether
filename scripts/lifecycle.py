"""Build or pack the explicitly versioned native lifecycle fixture client."""
from pathlib import Path
import struct
import subprocess
import sys
import tempfile


def pack(raw, output, abi=1):
    code = Path(raw).read_bytes()
    if not 0 < len(code) <= 4096:
        raise ValueError("lifecycle code must occupy 1..4096 bytes")
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(struct.pack("<8sIIQII", b"AELIFE01", abi, 1, 0x400000, len(code), 0) + code)


def build(output, bad_abi, fail_supervisor):
    if subprocess.check_output(["rustc", "--version"], text=True).split()[1] != "1.98.0":
        raise RuntimeError("Aether requires Rust 1.98.0")
    with tempfile.TemporaryDirectory(prefix="aether-lifecycle-") as directory:
        raw = Path(directory) / "client.bin"
        command = ["rustc", "--edition=2024", "--target=x86_64-unknown-none",
                   "-C", "opt-level=2", "-C", "panic=abort", "-C", "relocation-model=static",
                   "-C", "link-arg=-Tuser/protection/linker.ld", "-C", "link-arg=--oformat=binary",
                   "--check-cfg=cfg(fail_supervisor)", "user/lifecycle/main.rs", "-o", str(raw)]
        if fail_supervisor == "true":
            command += ["--cfg", "fail_supervisor"]
        subprocess.run(command, check=True)
        pack(raw, output, abi=2 if bad_abi == "true" else 1)


if __name__ == "__main__":
    if sys.argv[1] == "pack":
        pack(*sys.argv[2:])
    elif sys.argv[1] == "build":
        build(*sys.argv[2:])
    else:
        raise SystemExit("usage: lifecycle.py pack RAW OUTPUT | build OUTPUT BAD_ABI FAIL_SUPERVISOR")
