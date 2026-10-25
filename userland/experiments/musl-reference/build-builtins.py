#!/usr/bin/env python3
"""Build the LLVM 21.1.8 x86-64 builtins archive in this workspace."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import zipfile
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sources = ROOT / "build/compiler-rt-inputs"
tools = json.loads((HERE / "tools.lock.json").read_text())["tools"]
for name, item in tools.items():
    assert hashlib.sha256(Path(item["path"]).read_bytes()).hexdigest() == item["sha256"], name
cc = tools["clang"]["path"]
reference = Path(json.loads((HERE / "evidence.json").read_text())["output"])
out = Path(tempfile.mkdtemp(prefix="compiler-rt-", dir=ROOT / "build"))
# Source archives and the host CMake wheel must match the recorded input lock.
lock = json.loads((HERE / "builtins-inputs.json").read_text())
for item in lock["inputs"]:
    assert hashlib.sha256((sources / item["name"]).read_bytes()).hexdigest() == item["sha256"]
wheel = next(item for item in lock["inputs"] if item["name"].endswith(".whl"))
with zipfile.ZipFile(sources / wheel["name"]) as z:
    z.extractall(out / "host-cmake")
cmake = out / "host-cmake/cmake/data/bin/cmake"
cmake.chmod(0o755)
# Always consume fresh source extraction rather than trusting previous build trees.
import tarfile
for name in ("compiler-rt", "cmake"):
    with tarfile.open(sources / (name + "-21.1.8.src.tar.xz")) as tf:
        tf.extractall(out, filter="data")
(out / "cmake").symlink_to("cmake-21.1.8.src", target_is_directory=True)
(out / "tmp").mkdir()
env = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "TMPDIR": str(out / "tmp")}
flags = "--no-default-config --sysroot=" + str(reference / "stage") + " -isystem " + str(reference / "stage/usr/include")
args = [str(cmake), "-S", str(out / "compiler-rt-21.1.8.src/lib/builtins"),
        "-B", str(out / "obj"), "-G", "Unix Makefiles",
        "-DCMAKE_SYSTEM_NAME=Linux", "-DCMAKE_BUILD_TYPE=Release",
        "-DCMAKE_C_COMPILER=" + cc, "-DCMAKE_CXX_COMPILER=" + str(Path(cc).with_name("clang++")),
        "-DCMAKE_ASM_COMPILER=" + cc,
        "-DCMAKE_C_COMPILER_TARGET=x86_64-linux-musl", "-DCMAKE_CXX_COMPILER_TARGET=x86_64-linux-musl",
        "-DCMAKE_ASM_COMPILER_TARGET=x86_64-linux-musl",
        "-DCMAKE_C_FLAGS=" + flags, "-DCMAKE_CXX_FLAGS=--no-default-config", "-DCMAKE_ASM_FLAGS=--no-default-config",
        "-DCMAKE_AR=" + tools["ar"]["path"], "-DCMAKE_RANLIB=" + tools["ranlib"]["path"],
        "-DCOMPILER_RT_DEFAULT_TARGET_ONLY=ON",
        "-DLLVM_RUNTIMES_BUILD=ON", "-DCOMPILER_RT_INCLUDE_TESTS=OFF"]
commands = [args, [str(cmake), "--build", str(out / "obj"), "--parallel", "8"]]
print("Output: " + str(out), flush=True)
for label, command in zip(("configure", "build"), commands):
    with (out / (label + ".log")).open("wb") as log:
        result = subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(label + " failed; see " + str(out))
(out / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
archives = list((out / "obj").rglob("libclang_rt.builtins-x86_64.a"))
assert len(archives) == 1, archives
archive = archives[0]
headers = subprocess.run([tools["readelf"]["path"], "-h", str(archive)], capture_output=True, check=True, text=True).stdout
(out / "archive-headers.log").write_text(headers)
machines = re.findall(r"Machine:\s+(.+)", headers)
assert machines and all(m == "Advanced Micro Devices X86-64" for m in machines)
e = {"output": str(out), "archive": str(archive), "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
     "bytes": archive.stat().st_size, "scope": "builtins archive built; arithmetic witness still required",
     "members": len(machines), "input_lock_sha256": hashlib.sha256((HERE / "builtins-inputs.json").read_bytes()).hexdigest(),
     "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(out / "evidence.json").write_text(json.dumps(e, indent=2) + "\n")
print("PASS: " + str(archive), flush=True)
