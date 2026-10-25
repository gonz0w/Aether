#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Offline static Linux-musl coreutils tr/stty build; Python 3.12+."""

import argparse
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--uapi", type=Path, required=True)
    args = parser.parse_args()
    uapi = args.uapi.resolve()
    uapi_receipt = json.loads((uapi / "evidence.json").read_text())
    export = Path(uapi_receipt["export"])
    files = {str(p.relative_to(export)): sha(p)
             for p in export.rglob("*") if p.is_file()}
    if (not files or files != uapi_receipt["files"]
            or "include/linux/version.h" not in files):
        raise RuntimeError("UAPI export changed or empty")
    if (not uapi_receipt.get("extracted_file_count")
            or sha(uapi / "extracted-files.json")
            != uapi_receipt.get("extracted_inventory_sha256")
            or not (uapi / "CaseProbe").exists()
            or (uapi / "caseprobe").exists()):
        raise RuntimeError("UAPI extraction provenance or filesystem invalid")
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
    lock = locks["coreutils"]
    if sha(ROOT / lock["archive"]) != lock["sha256"]:
        raise RuntimeError("source changed")
    tools = receipt["tools"]
    out = Path(tempfile.mkdtemp(prefix="coreutils-musl-", dir=ROOT / "build"))
    print(out, flush=True)
    (out / "builder.py").write_bytes(Path(__file__).read_bytes())
    (out / "PLAN.md").write_bytes((HERE / "PLAN.md").read_bytes())
    original_wrapper = wrapper
    wrapper = out / "cc.py"
    wrapper.write_text(
        "#!" + os.sys.executable + "\n"
        "# SPDX-License-Identifier: BSD-2-Clause\n"
        "import os, sys\n"
        "base = " + repr(str(original_wrapper)) + "\n"
        "os.execv(base, [base, '-isystem', "
        + repr(str(export / "include")) + "] + sys.argv[1:])\n")
    wrapper.chmod(0o755)
    with tarfile.open(ROOT / lock["archive"]) as source:
        source.extractall(out, filter="data")
    src = out / "coreutils-9.11"
    env = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "CC": str(wrapper),
           "AR": tools["ar"]["path"], "RANLIB": tools["ranlib"]["path"],
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

    run("configure", ["/bin/sh", "configure", "--build=aarch64-apple-darwin",
                      "--host=x86_64-linux-musl", "--disable-nls",
                      "--disable-threads",
                      "--disable-acl", "--disable-xattr", "--disable-libcap",
                      "--without-selinux", "--without-libsmack",
                      "--without-libgmp"], src)
    generated = out / "generated.mk"
    generated.write_text("userland-generated: $(BUILT_SOURCES)\n")
    run("generated", [tools["make"]["path"], "-j2", "-f", "Makefile",
                      "-f", str(generated), "userland-generated"], src)
    run("build", [tools["make"]["path"], "-j2", "src/tr", "src/stty"], src)
    binaries = {}
    for name in ("tr", "stty"):
        binary = src / "src" / name
        run(name + "-headers", [tools["readelf"]["path"], "-h", "-l",
                               str(binary)], src)
        run(name + "-undefined", [tools["nm"]["path"], "--extern-only",
                                 "--undefined-only", str(binary)], src)
        if (out / (name + "-undefined.stdout")).read_text().strip():
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
        if any(h[0] in (2, 3) or (h[0] == 1 and h[1] & 3 == 3)
               for h in headers):
            raise RuntimeError("dynamic or W+X ELF")
        if not any(h[0] == 0x6474e551 and not h[1] & 1 for h in headers):
            raise RuntimeError("missing NX stack")
        binaries[name] = {"path": str(binary), "sha256": sha(binary),
                          "bytes": len(data)}
    evidence = {"scope": "static Linux x86-64 musl; not Aether",
                "sources": {"coreutils": lock}, "tools": tools,
                "sdk_inputs": inventory, "environment": env,
                "uapi_receipt_sha256": sha(uapi / "evidence.json"),
                "uapi_files": files, "uapi_export": str(export),
                "commands": commands, "binaries": binaries,
                "config_sha256": sha(src / "lib/config.h"),
                "wrapper_sha256": sha(wrapper),
                "builder_sha256": sha(Path(__file__))}
    (out / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print("PASS: static musl build and ELF inspection")


if __name__ == "__main__":
    main()
