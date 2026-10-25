#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Private host make and Linux x86 header export; Python 3.12+."""

import argparse
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", type=Path, required=True)
    args = parser.parse_args()
    work = args.work_root.resolve()
    if not work.is_relative_to(ROOT / "build"):
        raise RuntimeError("work root must be below build")
    pins = json.loads((HERE / "source.lock.json").read_text())
    receipt = json.loads((ROOT / "build/toybox-reference-1safvmep/evidence.json")
                         .read_text())
    tools = dict(receipt["tools"])
    tools.update(json.loads((HERE / "host-tools.lock.json").read_text()))
    for row in tools.values():
        if sha(Path(row["path"])) != row["sha256"]:
            raise RuntimeError("tool changed")
    for row in pins.values():
        if sha(ROOT / row["archive"]) != row["sha256"]:
            raise RuntimeError("source changed")
    out = Path(tempfile.mkdtemp(prefix="linux-uapi-", dir=work))
    print(out, flush=True)
    (out / "CaseProbe").write_text("case-sensitive required")
    if (out / "caseprobe").exists():
        raise RuntimeError("case-insensitive work filesystem")
    for name in ("build.py", "PLAN.md", "source.lock.json", "host-tools.lock.json"):
        (out / name).write_bytes((HERE / name).read_bytes())
    sdk = subprocess.check_output(["/usr/bin/xcrun", "--show-sdk-path"],
                                  text=True, timeout=15).strip()
    compiler = tools["clang"]["path"]
    flags = "--no-default-config -isysroot " + sdk + " -O2"
    env = {"PATH": "/opt/homebrew/opt/gnu-sed/libexec/gnubin:/usr/bin:/bin",
           "LC_ALL": "C", "CC": compiler, "CFLAGS": flags,
           "TMPDIR": str(out)}
    commands = []

    def run(name, args, cwd):
        with (out / (name + ".stdout")).open("wb") as stdout:
            with (out / (name + ".stderr")).open("wb") as stderr:
                proc = subprocess.Popen(args, cwd=cwd, env=env, stdout=stdout,
                                        stderr=stderr, start_new_session=True)
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

    for row in pins.values():
        with tarfile.open(ROOT / row["archive"]) as archive:
            archive.extractall(out, filter="data")
    verified = {}
    for row in pins.values():
        with tarfile.open(ROOT / row["archive"]) as archive:
            for member in archive:
                if member.isfile():
                    with archive.extractfile(member) as stream:
                        digest = hashlib.sha256(stream.read()).hexdigest()
                    if sha(out / member.name) != digest:
                        raise RuntimeError("extraction changed " + member.name)
                    verified[member.name] = digest
    (out / "extracted-files.json").write_text(json.dumps(verified, indent=2))
    make_src = out / "make-4.4.1"
    run("make-configure", ["/bin/sh", "configure", "--disable-nls",
                           "--without-guile"], make_src)
    run("make-build", ["/usr/bin/make", "-j2"], make_src)
    make = make_src / "make"
    run("make-version", [str(make), "--version"], make_src)
    src = out / "linux-6.18.49"
    export = out / "export"
    run("headers", [str(make), "-j2", "ARCH=x86", "HOSTCC=" + compiler,
                    "HOSTCFLAGS=" + flags, "INSTALL_HDR_PATH=" + str(export),
                    "headers_install"], src)
    inventory = {str(p.relative_to(export)): sha(p)
                 for p in export.rglob("*") if p.is_file()}
    required = {"include/linux/version.h", "include/asm/unistd_64.h",
                "include/asm/termbits.h", "include/linux/types.h"}
    if not required <= inventory.keys():
        raise RuntimeError("incomplete header export")
    evidence = {"scope": "Linux 6.18.49 x86 UAPI export, not Aether",
                "sources": pins, "tools": tools, "host_sdk": sdk,
                "environment": env, "commands": commands,
                "extracted_inventory_sha256": sha(out / "extracted-files.json"),
                "extracted_file_count": len(verified),
                "make_sha256": sha(make), "export": str(export),
                "files": inventory, "builder_sha256": sha(Path(__file__))}
    (out / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print("PASS: exported", len(inventory), "headers")


if __name__ == "__main__":
    main()
