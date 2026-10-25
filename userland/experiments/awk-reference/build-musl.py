#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Offline static Linux-musl mawk build; Python 3.12+."""

import hashlib
import json
import os
from pathlib import Path
import signal
import struct
import subprocess
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    locks = json.loads((HERE / "source.lock.json").read_text())
    prior = ROOT / "build/toybox-reference-1safvmep"
    receipt = json.loads((prior / "evidence.json").read_text())
    wrapper = prior / "cc.py"
    if sha(wrapper) != receipt["files"][str(wrapper)]:
        raise RuntimeError("compiler wrapper changed")
    for tool in receipt["tools"].values():
        if sha(Path(tool["path"])) != tool["sha256"]:
            raise RuntimeError("tool changed")
    sdk = ROOT / "build/musl-reference-q39nl2io"
    inventory = {str(p.relative_to(sdk)): sha(p)
                 for p in (sdk / "stage").rglob("*") if p.is_file()}
    if inventory != receipt["sdk_inputs"]:
        raise RuntimeError("SDK changed")
    lock = locks["mawk"]
    if sha(ROOT / lock["archive"]) != lock["sha256"]:
        raise RuntimeError("source changed")
    tools = receipt["tools"]
    out = Path(tempfile.mkdtemp(prefix="mawk-musl-", dir=ROOT / "build"))
    print(out, flush=True)
    with tarfile.open(ROOT / lock["archive"]) as source:
        source.extractall(out, filter="data")
    src = out / "mawk-1.3.4-20260302"
    env = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "CC": str(wrapper),
           "CFLAGS": "-O2 -fstack-protector-strong", "TMPDIR": str(out),
           "LDFLAGS": "-L" + str(sdk / "stage/usr/lib")
                        + " -Wl,-z,noexecstack -Wl,--no-undefined"}
    commands = []

    def run(name, args, cwd):
        with (out / (name + ".stdout")).open("wb") as stdout:
            with (out / (name + ".stderr")).open("wb") as stderr:
                proc = subprocess.Popen(
                    args, cwd=cwd, env=env, stdout=stdout, stderr=stderr,
                    start_new_session=True,
                )
                try:
                    status = proc.wait(timeout=240)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait()
                    status = "timeout"
        commands.append({"name": name, "argv": args, "cwd": str(cwd),
                         "status": status})
        (out / "commands.json").write_text(json.dumps(commands, indent=2))
        if status != 0:
            raise RuntimeError(name + " failed; see " + str(out))

    run("math-probe", [str(wrapper), "-std=c17", "-Wall", "-Wextra",
                       "-Werror", str(HERE / "math-probe.c"),
                       "-o", str(out / "math-probe")], src)
    env.update(ac_cv_func_isnan="yes", ac_cv_func_isinf="yes")
    run("configure", ["/bin/sh", "configure", "--build=aarch64-apple-darwin",
                      "--host=x86_64-linux-musl"], src)
    run("build", [tools["make"]["path"], "-j2", "mawk"], src)
    binary = src / "mawk"
    run("headers", [tools["readelf"]["path"], "-h", "-l", str(binary)], src)
    run("undefined", [tools["nm"]["path"], "--extern-only",
                      "--undefined-only", str(binary)], src)
    if (out / "undefined.stdout").read_text().strip():
        raise RuntimeError("undefined external symbol")
    data = binary.read_bytes()
    if data[:6] != b"\x7fELF\x02\x01":
        raise RuntimeError("ELF encoding")
    if struct.unpack_from("<HH", data, 16) != (2, 62):
        raise RuntimeError("ELF target")
    offset = struct.unpack_from("<Q", data, 32)[0]
    size, count = struct.unpack_from("<HH", data, 54)
    headers = [struct.unpack_from("<IIQQQQQQ", data, offset + i * size)
               for i in range(count)]
    if any(h[0] in (2, 3) or (h[0] == 1 and h[1] & 3 == 3) for h in headers):
        raise RuntimeError("dynamic or W+X ELF")
    if not any(h[0] == 0x6474e551 and not h[1] & 1 for h in headers):
        raise RuntimeError("missing NX stack")
    run("imports", [tools["nm"]["path"], "--undefined-only"]
        + [str(p) for p in sorted(src.glob("*.o"))], src)
    evidence = {"scope": "static Linux x86-64 musl; not Aether",
                "sources": {"mawk": lock}, "tools": tools,
                "sdk_inputs": inventory, "environment": env,
                "commands": commands, "binaries": {"mawk": {
                    "path": str(binary), "sha256": sha(binary),
                    "bytes": len(data)}},
                "test_inputs": {str(p.relative_to(src)): sha(p)
                                for p in (src / "test").rglob("*")
                                if p.is_file()},
                "config_sha256": sha(src / "config.h"),
                "math_probe_sha256": sha(out / "math-probe"),
                "math_probe_source_sha256": sha(HERE / "math-probe.c"),
                "wrapper_sha256": sha(wrapper),
                "builder_sha256": sha(Path(__file__))}
    (out / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print("PASS: static musl build and ELF inspection")


if __name__ == "__main__":
    main()
