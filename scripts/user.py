"""Build the fixed-format Rust protection fixture without registry dependencies."""
from pathlib import Path
import subprocess
import sys


def build(output, bad, bad_ipc, bad_smp_ipc, bad_display_message, bad_stream_generation):
    version = subprocess.check_output(["rustc", "--version"], text=True)
    if version.split()[1] != "1.98.0":
        raise RuntimeError("Aether requires Rust 1.98.0 (rust-toolchain.toml)")
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    command = ["rustc", "--edition=2024", "--target=x86_64-unknown-none",
               "-C", "opt-level=2", "-C", "panic=abort", "-C", "relocation-model=static",
               "-C", "link-arg=-Tuser/protection/linker.ld", "-C", "link-arg=--oformat=binary",
               "--check-cfg=cfg(bad_fixture,bad_ipc,bad_smp_ipc,bad_display_message,bad_stream_generation)", "user/protection/main.rs", "-o", str(output)]
    if bad == "true":
        command += ["--cfg", "bad_fixture"]
    if bad_ipc == "true":
        command += ["--cfg", "bad_ipc"]
    if bad_smp_ipc == "true":
        command += ["--cfg", "bad_smp_ipc"]
    if bad_display_message == "true":
        command += ["--cfg", "bad_display_message"]
    if bad_stream_generation == "true":
        command += ["--cfg", "bad_stream_generation"]
    subprocess.run(command, check=True)
    if not 0 < output.stat().st_size <= 4096:
        raise RuntimeError("invalid protection image size")


if __name__ == "__main__":
    build(*sys.argv[1:])
