#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Offline, source-pinned host comparison build; Python 3.12+."""

import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    locks = json.loads((HERE / "source.lock.json").read_text())
    tools = json.loads((HERE / "tools.lock.json").read_text())
    for tool in tools.values():
        if sha(Path(tool["path"])) != tool["sha256"]:
            raise RuntimeError("host tool changed: " + tool["path"])
    for lock in locks.values():
        if sha(ROOT / lock["archive"]) != lock["sha256"]:
            raise RuntimeError("source changed")
    out = Path(tempfile.mkdtemp(prefix="awk-build-", dir=ROOT / "build"))
    print(out, flush=True)
    sdk = subprocess.check_output(
        ["/usr/bin/xcrun", "--show-sdk-path"], timeout=15, text=True,
        cwd=ROOT, env={"PATH": "/usr/bin:/bin"},
    ).strip()
    compiler = tools["clang"]["path"]
    flags = "--no-default-config -isysroot " + sdk + " -O2"
    env = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "CC": compiler,
           "CFLAGS": flags, "TMPDIR": str(out)}
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

    binaries = {}
    for name, lock in locks.items():
        target = out / name
        target.mkdir()
        with tarfile.open(ROOT / lock["archive"]) as source:
            source.extractall(target, filter="data")
        src = next(target.iterdir())
        if name == "onetrueawk":
            run(name + "-build", [tools["make"]["path"], "-j1",
                "CC=" + compiler, "HOSTCC=" + compiler + " " + flags,
                "CFLAGS=" + flags, "YACC=" + tools["bison"]["path"] + " -d"],
                src)
            binary = src / "a.out"
        else:
            options = []
            if name == "gawk":
                options = ["--disable-extensions", "--disable-mpfr",
                           "--disable-nls", "--without-readline"]
            run(name + "-configure", ["/bin/sh", "configure"] + options, src)
            if name == "gawk":
                run(name + "-support", [tools["make"]["path"], "-j2",
                    "-C", "support"], src)
            run(name + "-build", [tools["make"]["path"], "-j2", name], src)
            binary = src / name
        run(name + "-libraries", ["/usr/bin/otool", "-L", str(binary)], src)
        binaries[name] = {"path": str(binary), "sha256": sha(binary),
                          "bytes": binary.stat().st_size}
    evidence = {"scope": "macOS arm64 host; no musl/native claim",
                "sources": locks, "tools": tools, "host_sdk": sdk,
                "environment": env, "commands": commands,
                "binaries": binaries, "builder_sha256": sha(Path(__file__))}
    (out / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print("PASS: three host provider builds")


if __name__ == "__main__":
    main()
