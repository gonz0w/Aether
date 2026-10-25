#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Imported SDK startup/adapter/helper link; no artifact execution."""
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "experiments/command-runner"))
from process import clean_env, run

HERE = ROOT / "experiments/sdk-consumer"
NATIVE = ROOT / "experiments/native-c"
OUT = ROOT / "docs/evidence/sdk-startup-link-2026-09-07"
PIN = ROOT / "docs/evidence/native-stdio-files-2026-09-05/libc/evidence.json"
LAYOUT = ROOT / "../pkg-mgr/docs/evidence/sdk-real-transport-2026-09-07/attempt-1/result.json"
BINDING = ROOT / "docs/evidence/sdk-imported-consumer-2026-09-07/verification.json"
MAX_RECEIPT_BYTES = 2 * 1024 * 1024
MAX_RECEIPT_DEPTH = 64


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_receipt(path):
    with path.open("rb") as stream:
        raw = stream.read(MAX_RECEIPT_BYTES + 1)
    if len(raw) > MAX_RECEIPT_BYTES:
        raise RuntimeError("receipt exceeds byte limit")
    # Count only structural ASCII bytes outside strings. The JSON decoder
    # still validates syntax; this scan enforces an interpreter-independent
    # container-depth limit before it allocates the decoded object graph.
    depth = 0
    quoted = False
    escaped = False
    for byte in raw:
        if quoted:
            if escaped:
                escaped = False
            elif byte == 92:
                escaped = True
            elif byte == 34:
                quoted = False
        elif byte == 34:
            quoted = True
        elif byte in (91, 123):
            depth += 1
            if depth > MAX_RECEIPT_DEPTH:
                raise RuntimeError("receipt exceeds nesting limit")
        elif byte in (93, 125):
            depth -= 1

    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise RuntimeError("duplicate receipt JSON key")
            result[key] = value
        return result

    def reject_constant(value):
        raise RuntimeError("nonfinite receipt JSON constant")

    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object,
                          parse_constant=reject_constant)
    except RecursionError as error:
        raise RuntimeError("receipt JSON nesting exceeds decoder limit") from error


def require_object(value, field):
    if not isinstance(value, dict):
        raise RuntimeError("invalid receipt field: " + field)
    return value


def require_digest(value, field):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise RuntimeError("invalid receipt field: " + field)


def require_absolute_path(value, field):
    if (not isinstance(value, str) or not value or "\x00" in value or
            not Path(value).is_absolute()):
        raise RuntimeError("invalid receipt field: " + field)


def validate_inputs(pin, layout, binding):
    require_object(pin, "pin")
    require_object(layout, "layout")
    require_object(binding, "binding")
    require_digest(pin.get("libc_receipt_sha256"), "pin.libc_receipt_sha256")
    require_absolute_path(layout.get("imported_root"), "layout.imported_root")
    for name, data in (("layout", layout), ("binding", binding)):
        require_digest(data.get("target_sha256"), name + ".target_sha256")
    tools = require_object(pin.get("tools"), "pin.tools")
    for name in ("clang", "lld", "readelf", "nm"):
        field = "pin.tools." + name
        tool = require_object(tools.get(name), field)
        require_absolute_path(tool.get("path"), field + ".path")
        require_digest(tool.get("sha256"), field + ".sha256")
    inputs = require_object(pin.get("sdk_inputs"), "pin.sdk_inputs")
    if not inputs:
        raise RuntimeError("invalid receipt field: pin.sdk_inputs")
    for name, digest in inputs.items():
        if (not isinstance(name, str) or not name.startswith("stage/usr/") or
                "\\" in name or "\x00" in name or
                any(part in ("", ".", "..") for part in name.split("/"))):
            raise RuntimeError("invalid receipt field: pin.sdk_inputs.path")
        require_digest(digest, "pin.sdk_inputs.digest")


def validate_libc_receipt(receipt):
    require_object(receipt, "libc")
    for name in ("probe_sha256", "io_adapter_sha256"):
        require_digest(receipt.get(name), "libc." + name)
    memory = require_object(receipt.get("memory_sources"), "libc.memory_sources")
    for name in ("native_memory.c", "memory_probe.c"):
        require_digest(memory.get(name), "libc.memory_sources." + name)


def run_startup():
    work = Path(tempfile.mkdtemp(prefix="sdk-startup-", dir=ROOT / "build"))
    print("[INFO] Evidence: " + str(work), file=sys.stderr, flush=True)
    adapters = [NATIVE / name for name in (
        "io_probe.c", "native_io.c", "native_memory.c", "memory_probe.c")]
    receipt_path = ROOT / "build/native-c-xhkdw6jv/evidence.json"
    report = {"status": "incomplete",
              "scope": "imported SDK startup/adapter ELF link; native NOT RUN",
              "work": str(work), "commands": []}

    def save():
        (work / "summary.json").write_text(json.dumps(report, indent=2) + "\n")

    def cmd(label, argv, marker=None, failure=False):
        result = run(argv, cwd=work, env=clean_env(work), work=work,
                     label=label, timeout=30)
        report["commands"].append(result.record)
        save()
        if (not result.record["complete"] or
                (result.returncode != 0) != failure or
                (marker and marker not in result.stderr + result.stdout)):
            raise RuntimeError(label + ": unexpected result")
        return result

    save()
    try:
        pin = load_receipt(PIN)
        layout = load_receipt(LAYOUT)
        binding = load_receipt(BINDING)
        validate_inputs(pin, layout, binding)
        source_sdk = (Path(layout["imported_root"]) /
                      "stage/aether-musl-sdk/usr/local/lib/aether-sdk/"
                      "musl-native-experimental")
        sources = [HERE / "check-startup.py", ROOT / "experiments/command-runner/process.py",
                   OUT / "PLAN.md", HERE / "STARTUP-PLAN.md",
                   HERE / "RECEIPT-FAILURE-PLAN.md",
                   HERE / "SCHEMA-PLAN.md",
                   HERE / "PREFLIGHT-PLAN.md",
                   PIN, LAYOUT, BINDING, receipt_path] + adapters
        report["sources"] = {str(p): sha(p) for p in sources}
        report["tools"] = {name: pin["tools"][name]
                           for name in ("clang", "lld", "readelf", "nm")}
        for tool in report["tools"].values():
            if sha(Path(tool["path"])) != tool["sha256"]:
                raise RuntimeError("tool drift")
        report["package_binding"] = binding
        if report["package_binding"]["target_sha256"] != layout["target_sha256"]:
            raise RuntimeError("imported target mismatch")
        if sha(receipt_path) != pin["libc_receipt_sha256"]:
            raise RuntimeError("libc receipt identity mismatch")
        receipt = load_receipt(receipt_path)
        validate_libc_receipt(receipt)
        expected_sources = {
            "io_probe.c": receipt["probe_sha256"],
            "native_io.c": receipt["io_adapter_sha256"],
            "native_memory.c": receipt["memory_sources"]["native_memory.c"],
            "memory_probe.c": receipt["memory_sources"]["memory_probe.c"],
        }
        if sha(NATIVE / "probe.c") == receipt["probe_sha256"]:
            raise RuntimeError("startup probe.c unexpectedly matches io pin")
        def require_source(path, digest, label):
            if sha(path) != digest:
                raise RuntimeError("adapter drift before build: " + label)

        for name, digest in expected_sources.items():
            require_source(NATIVE / name, digest, name)
        mutant = work / "mutant-io_probe.c"
        mutant.write_bytes((NATIVE / "io_probe.c").read_bytes() + b"\n")
        try:
            require_source(mutant, receipt["probe_sha256"], "io_probe.c")
        except RuntimeError as error:
            if "adapter drift before build: io_probe.c" not in str(error):
                raise
        else:
            raise RuntimeError("changed-source control passed")
        report["receipt_sources"] = expected_sources
        report["sdk_inputs"] = pin["sdk_inputs"]
        for name, digest in pin["sdk_inputs"].items():
            rel = name.removeprefix("stage/")
            path = source_sdk / rel
            if path.is_symlink() or not path.is_file() or sha(path) != digest:
                raise RuntimeError("SDK drift: " + rel)
            dest = work / "sdk" / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
            if sha(dest) != digest or (dest.stat().st_mode & 0o7777) != 0o644:
                raise RuntimeError("copy drift")
        for path in adapters:
            destination = work / path.name
            shutil.copy2(path, destination)
            require_source(destination, expected_sources[path.name], path.name)
        report["staged_sources"] = {
            path.name: sha(work / path.name) for path in adapters
        }
        save()
        (work / "empty").mkdir()
        clang = pin["tools"]["clang"]["path"]
        lld = pin["tools"]["lld"]["path"]
        include = str(work / "sdk/usr/include")
        lib = work / "sdk/usr/lib"
        cc = [clang, "--no-default-config", "--target=x86_64-linux-musl",
              "--sysroot=" + str(work / "empty")]
        compile_cc = cc + ["-std=c17", "-O2", "-Wall", "-Wextra", "-Werror"]
        cmd("compile-io", compile_cc + [
            "-ffreestanding", "-fno-stack-protector", "-c", "native_io.c",
            "-o", "native_io.o"])
        cmd("compile-memory", compile_cc + [
            "-nostdinc", "-isystem", include, "-fno-builtin",
            "-fstack-protector-strong", "-c", "native_memory.c",
            "-o", "native_memory.o"])
        cmd("compile-memory-probe", compile_cc + [
            "-nostdinc", "-isystem", include, "-fno-builtin",
            "-fstack-protector-strong", "-c", "memory_probe.c",
            "-o", "memory_probe.o"])
        cmd("compile-probe", compile_cc + [
            "-nostdinc", "-isystem", include, "-fno-builtin",
            "-fstack-protector-strong", "-DNATIVE_MEMORY", "-c", "io_probe.c",
            "-o", "io_probe.o"])
        cmd("missing-headers", compile_cc + [
            "-nostdinc", "-fno-builtin", "-c", "io_probe.c", "-o",
            "missing-header.o"], b"'errno.h' file not found", True)
        link = cc + ["-fuse-ld=" + lld, "-nostdlib", "-static",
                     "-Wl,-z,noexecstack", "-Wl,--no-undefined"]
        objects = [str(lib / "crt1.o"), str(lib / "crti.o"), "io_probe.o",
                   "native_io.o", "native_memory.o", "memory_probe.o",
                   str(lib / "libc.a"), str(lib / "crtn.o")]
        cmd("link", link + objects + ["-o", "startup.elf"])
        cmd("missing-crt1", link + ["-Wl,--fatal-warnings"] + objects[1:] +
            ["-o", "missing-crt1.elf"], b"_start", True)
        cmd("missing-io", link + [
            str(lib / "crt1.o"), str(lib / "crti.o"), "io_probe.o",
            "native_memory.o", "memory_probe.o", str(lib / "libc.a"),
            str(lib / "crtn.o"), "-o", "missing-io.elf"], b"__aether_io", True)
        cmd("missing-memory-path", link + [
            str(lib / "crt1.o"), str(lib / "crti.o"), "io_probe.o",
            "native_io.o", str(work / "absent_memory.o"),
            str(lib / "libc.a"), str(lib / "crtn.o"), "-o",
            "missing-memory.elf"], b"absent_memory.o", True)
        cmd("missing-libc", link + [
            str(lib / "crt1.o"), str(lib / "crti.o"), "io_probe.o",
            "native_io.o", "native_memory.o", "memory_probe.o",
            str(lib / "crtn.o"), "-o", "missing-libc.elf"], b"undefined", True)
        (work / "helper.c").write_text(
            "unsigned __int128 divide(unsigned __int128 a, "
            "unsigned __int128 b) { return a / b; }\n")
        cmd("missing-builtins", link + [
            "-Wl,-e,divide", "helper.c", "-o", "helper.elf"], b"__udivti3", True)
        for name in ("missing-header.o", "missing-crt1.elf", "missing-io.elf",
                     "missing-memory.elf", "missing-libc.elf", "helper.elf"):
            if (work / name).exists():
                raise RuntimeError("unexpected failed output: " + name)
        headers = cmd("headers", [pin["tools"]["readelf"]["path"], "-h", "-l",
                                  str(work / "startup.elf")]).stdout
        undefined = cmd("undefined", [pin["tools"]["nm"]["path"], "-u",
                                      str(work / "startup.elf")]).stdout
        extra = {line.split()[-1] for line in undefined.decode().splitlines()
                 if line.strip()} - {"_DYNAMIC"}
        text = headers.decode()
        if (b"ELF64" not in headers or b"X86-64" not in headers or
                "INTERP" in text or "\n  DYNAMIC " in text or extra):
            raise RuntimeError("ELF oracle")
        report["artifact_sha256"] = sha(work / "startup.elf")
        for path, digest in report["sources"].items():
            if sha(Path(path)) != digest:
                raise RuntimeError("source drift")
        report["status"] = "pass"
    except (OSError, ValueError, RuntimeError) as error:
        report["error"] = str(error)
        print("[ERROR] " + json.dumps(str(error), ensure_ascii=True),
              file=sys.stderr)
        save()
        return 1
    save()
    print("[PASS] Imported SDK startup/adapter/helper link; native NOT RUN.")
    return 0


def main():
    try:
        return run_startup()
    except OSError as error:
        print("[ERROR] Evidence storage unavailable: " +
              json.dumps(str(error), ensure_ascii=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
