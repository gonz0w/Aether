"""Build the separate single-page Rust SMP supervisor with pinned tools."""
from pathlib import Path
import subprocess
import sys


def build(output, fail_supervisor):
    if subprocess.check_output(["rustc", "--version"], text=True).split()[1] != "1.98.0":
        raise RuntimeError("Aether requires Rust 1.98.0")
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    command = ["rustc", "--edition=2024", "--target=x86_64-unknown-none",
               "-C", "opt-level=s", "-C", "panic=abort", "-C", "relocation-model=static",
               "-C", "link-arg=-Tuser/protection/linker.ld", "-C", "link-arg=--oformat=binary",
               "--check-cfg=cfg(fail_supervisor)", "user/smp_supervisor/main.rs", "-o", str(path)]
    if fail_supervisor == "true":
        command += ["--cfg", "fail_supervisor"]
    subprocess.run(command, check=True)
    if not 0 < path.stat().st_size <= 4096:
        raise RuntimeError("SMP supervisor image exceeds one page")


if __name__ == "__main__":
    build(*sys.argv[1:])
