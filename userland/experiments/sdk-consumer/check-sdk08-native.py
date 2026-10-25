#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Isolated SDK-08 producer snapshot and first native cases."""
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments/command-runner"))
from process import clean_env, run

CLOSURE = ROOT / "experiments/sdk-consumer/sdk-08-closure.json"
AETHER = ROOT.parent
SYSINIT = ROOT.parent / 'sys-init'
ZIG = Path("/opt/homebrew/bin/zig")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def copy_file(src, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def snapshot_tree(src, dest, dirs, files):
    inventory = {}
    for name in dirs:
        origin = src / name
        if not origin.is_dir():
            raise RuntimeError("missing producer dir: " + name)
        shutil.copytree(origin, dest / name, ignore=lambda d, n: {
            ".git", ".zig-cache", "zig-out", "__pycache__", ".DS_Store", ".jj"})
    for name in files:
        origin = src / name
        if not origin.is_file():
            raise RuntimeError("missing producer file: " + name)
        copy_file(origin, dest / name)
    for path in dest.rglob("*"):
        if path.is_file():
            rel = path.relative_to(dest).as_posix()
            inventory[rel] = sha(path)
    return inventory


def main():
    if sys.argv[1:] == ["--help"]:
        print(__doc__)
        print("Usage: python3 -B experiments/sdk-consumer/"
              "check-sdk08-native.py [--help|--version]")
        return 0
    if sys.argv[1:] == ["--version"]:
        print("aether-sdk08-native 0.1.0")
        return 0
    if sys.argv[1:]:
        print("[ERROR] Unexpected arguments; use --help.", file=sys.stderr)
        return 64
    work = Path(tempfile.mkdtemp(prefix="sdk08-native-", dir=ROOT / "build"))
    print("[INFO] Evidence: " + str(work), file=sys.stderr, flush=True)
    closure = json.loads(CLOSURE.read_text())
    report = {"status": "incomplete", "scope": "isolated snapshot plus first native cases",
              "work": str(work), "commands": []}

    def save():
        (work / "summary.json").write_text(json.dumps(report, indent=2) + "\n")

    def cmd(label, argv, cwd=None, timeout=120, env=None, failure=False, marker=None):
        result = run(argv, cwd=cwd or work, env=env or clean_env(work),
                     work=work, label=label, timeout=timeout)
        report["commands"].append({"label": label, "process": result.record})
        save()
        if not result.record["complete"]:
            raise RuntimeError(label + ": incomplete")
        if (result.returncode != 0) != failure:
            raise RuntimeError(label + ": unexpected exit")
        blob = result.stderr + result.stdout
        if marker and marker not in blob:
            raise RuntimeError(label + ": missing marker")
        return result

    save()
    try:
        consumer = closure["consumer"]
        elf = ROOT / consumer["startup_elf_path"]
        if sha(elf) != consumer["startup_elf_sha256"]:
            raise RuntimeError("consumer ELF drift")
        producer = work / "producer"
        aether = producer / "aether"
        aether.mkdir(parents=True)
        docs = aether / "docs"
        docs.mkdir()
        for path in (AETHER / "docs").glob("*.md"):
            copy_file(path, docs / path.name)
        aether_inv = snapshot_tree(
            AETHER, aether,
            ["kernel", "scripts", "user", "boot", "tests"],
            ["build.zig", "rust-toolchain.toml", "LICENSE", "README.md",
             "AGENTS.md"])
        for extra in ("docs/" + p.name for p in docs.glob("*.md")):
            aether_inv[extra] = sha(aether / extra)
        deps = aether / ".deps"
        copy_file(AETHER / ".deps/manifest.json", deps / "manifest.json")
        shutil.copytree(AETHER / ".deps/firmware", deps / "firmware")
        shutil.copytree(AETHER / ".deps/limine", deps / "limine")
        for path in deps.rglob("*"):
            if path.is_file():
                aether_inv[".deps/" + path.relative_to(deps).as_posix()] = sha(path)
        if "evidence" in aether_inv or any("target-attempts" in k for k in aether_inv):
            raise RuntimeError("evidence archive leaked into snapshot")
        sysinit = producer / "sys-init"
        sysinit.mkdir()
        shutil.copytree(SYSINIT / "scripts", sysinit / "scripts",
                        ignore=lambda d, n: {"__pycache__"})
        shutil.copytree(SYSINIT / "prototypes/native-supervisor",
                        sysinit / "prototypes/native-supervisor",
                        ignore=lambda d, n: {"__pycache__"})
        sys_inv = {}
        for path in sysinit.rglob("*"):
            if path.is_file():
                sys_inv[path.relative_to(sysinit).as_posix()] = sha(path)
        report["producer"] = {
            "aether_files": len(aether_inv),
            "aether_contract_sha256": sha(aether / "docs/NATIVE-C.md"),
            "sysinit_files": len(sys_inv),
            "historical_match": sha(aether / "docs/NATIVE-C.md") ==
            closure["producer"]["historical_kernel_contract_sha256"],
        }
        (work / "aether-inventory.json").write_text(
            json.dumps(aether_inv, indent=2, sort_keys=True) + "\n")
        (work / "sysinit-inventory.json").write_text(
            json.dumps(sys_inv, indent=2, sort_keys=True) + "\n")
        envelope = work / "native-c.bin"
        envelope.write_bytes(b"AENATC01" + os.urandom(32) + elf.read_bytes())
        report["envelope_sha256"] = sha(envelope)
        env = dict(clean_env(work))
        env["PATH"] = "/opt/homebrew/bin:/usr/bin:/bin:" + os.environ.get("HOME", "") + "/.cargo/bin"
        rustc = Path.home() / ".cargo/bin/rustc"
        if not rustc.is_file():
            raise RuntimeError("rustc missing")
        supervisor = work / "client-pass"
        cmd("supervisor-pass",
            [sys.executable, str(sysinit / "scripts/build-native-supervisor.py"),
             str(envelope), str(supervisor), "--variant", "io"],
            env=env, timeout=180)
        image = supervisor / "supervised.bin"
        if not image.is_file():
            raise RuntimeError("supervised.bin missing")
        zig = [str(ZIG), "build", "-Dsmp=false",
               "-Dnative-c-image=" + str(image),
               "-Dnative-memory=true", "-p", str(work / "zig-pass"),
               "--cache-dir", str(work / "zig-cache"),
               "--global-cache-dir", str(work / "zig-cache/global")]
        cmd("zig-pass", zig, cwd=aether, env=env, timeout=180)
        iso = work / "zig-pass/aether.iso"
        if not iso.is_file():
            iso = aether / "zig-pass/aether.iso"
        cmd("smoke-pass",
            [sys.executable, str(aether / "scripts/io_smoke.py"), str(iso)],
            cwd=aether, env=env, timeout=60)
        serial = iso.parent / "native-serial.log"
        text = serial.read_text() if serial.is_file() else ""
        if "AETHER NATIVE IO PASS" not in text.splitlines():
            raise RuntimeError("pass serial missing")
        report["pass_serial_sha256"] = sha(serial) if serial.is_file() else None
        deny = work / "client-deny"
        cmd("supervisor-deny",
            [sys.executable, str(sysinit / "scripts/build-native-supervisor.py"),
             str(envelope), str(deny), "--variant", "io"],
            env=env, timeout=180)
        zig_deny = [str(ZIG), "build", "-Dsmp=false",
                    "-Dnative-c-image=" + str(deny / "supervised.bin"),
                    "-Dnative-memory=true", "-Dnative-no-output=true",
                    "-p", str(work / "zig-deny"),
                    "--cache-dir", str(work / "zig-cache"),
                    "--global-cache-dir", str(work / "zig-cache/global")]
        cmd("zig-deny", zig_deny, cwd=aether, env=env, timeout=180)
        deny_iso = work / "zig-deny/aether.iso"
        if not deny_iso.is_file():
            deny_iso = aether / "zig-deny/aether.iso"
        cmd("smoke-deny",
            [sys.executable, str(aether / "scripts/io_smoke.py"), str(deny_iso)],
            cwd=aether, env=env, timeout=60, failure=True)
        deny_serial = deny_iso.parent / "native-serial.log"
        deny_text = deny_serial.read_text() if deny_serial.is_file() else ""
        if "AETHER NATIVE IO PASS" in deny_text:
            raise RuntimeError("denial produced pass marker")
        if "AETHER PANIC: native C profile rejected" not in deny_text and \
                "AETHER PANIC" not in deny_text:
            raise RuntimeError("denial serial missing panic")
        report["status"] = "pass"
    except (OSError, ValueError, RuntimeError) as error:
        report["error"] = str(error)
        print("[ERROR] " + json.dumps(str(error), ensure_ascii=True),
              file=sys.stderr)
        save()
        return 1
    save()
    print("[PASS] Isolated producer snapshot and first native pass/denial.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
