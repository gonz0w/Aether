#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Pure runner parser host controls and native object inspection; Python 3.10+."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import re
import sys
import tempfile

from process import clean_env, run

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sdk", type=Path, required=True)
    args = parser.parse_args()
    sdk = args.sdk.resolve()
    work = Path(tempfile.mkdtemp(prefix="runner-parser-", dir=ROOT / "build"))
    print(work, flush=True)
    pin = ROOT / "docs/evidence/native-stdio-files-2026-09-05/libc/evidence.json"
    reference = json.loads(pin.read_text())
    tools = reference["tools"]
    sources = [HERE / name for name in ("runner-parse.c", "runner-parse.h",
               "parser-controls.c", "check-parser.py", "process.py")]
    sources += [ROOT / "docs/AETHER-RUN.md", ROOT / "docs/RUNNER-INTEGRATION.md",
                ROOT / "docs/evidence/runner-parser-2026-09-06/change-review.md"]
    report = {"status": "incomplete", "scope": "host UBSan parser; native object only",
              "sources": {str(p): sha(p) for p in sources}, "commands": [],
              "cases": [], "pin_sha256": sha(pin), "tools": tools,
              "python": sys.version, "platform": platform.platform()}
    env = clean_env(work)
    env["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=1"

    def save():
        (work / "summary.json").write_text(json.dumps(report, indent=2) + "\n")

    def command(label, argv, expected=0):
        result = run(argv, cwd=work, env=env, work=work, label=label, timeout=30)
        report["commands"].append({"label": label, "process": result.record})
        save()
        if not result.record["complete"] or result.returncode != expected:
            raise RuntimeError(label + ": unexpected execution; see retained logs")
        return result

    def verify_inputs():
        for name, tool in tools.items():
            if sha(Path(tool["path"])) != tool["sha256"]:
                raise RuntimeError("tool mismatch: " + name)
        if any(p.is_symlink() for p in (sdk / "stage").rglob("*")):
            raise RuntimeError("SDK symlink")
        inventory = {str(p.relative_to(sdk)): sha(p)
                     for p in (sdk / "stage").rglob("*") if p.is_file()}
        if (inventory != reference["sdk_inputs"] or
                sha(sdk / "evidence.json") != reference["libc_receipt_sha256"]):
            raise RuntimeError("SDK mismatch")
        for name, digest in report["sources"].items():
            if sha(Path(name)) != digest:
                raise RuntimeError("source changed: " + name)

    save()
    try:
        verify_inputs()
        snapshot = work / "sources"
        snapshot.mkdir()
        for p in sources:
            (snapshot / p.name).write_bytes(p.read_bytes())
        cc = [tools["clang"]["path"], "--no-default-config"]
        host_sdk = command(
            "host-sdk", ["/usr/bin/xcrun", "--show-sdk-path"]
        ).stdout.decode().strip()
        resource = Path(command(
            "resource-dir", cc + ["-print-resource-dir"]
        ).stdout.decode().strip())
        runtime = resource / "lib/darwin/libclang_rt.ubsan_osx_dynamic.dylib"
        report["sanitizer_runtime"] = {"path": str(runtime), "sha256": sha(runtime)}
        flags = ["-std=c17", "-Wall", "-Wextra", "-Werror", "-Wpedantic",
                 "-Wconversion", "-Wsign-conversion", "-Wshadow",
                 "-Wstrict-prototypes", "-Wmissing-prototypes", "-I", str(HERE)]
        host = flags + ["-O1", "-g", "-fno-omit-frame-pointer",
                        "-fsanitize=undefined", "-fno-sanitize-recover=all",
                        "-isysroot", host_sdk]
        original = (HERE / "runner-parse.c").read_text()
        anchor = '    if (startup->count == 2 && !strcmp(startup->args[1], "--help"))'
        if original.count(anchor) != 1 or original.count("if (record[i])") != 1:
            raise RuntimeError("mutation anchors changed")
        variants = [
            ("controls", original, 0, None),
            ("skip-reserved", original.replace("if (record[i])", "if (record[i] && 0)"),
             90, b"ORACLE: reserved\n"),
            ("child-help", original.replace(anchor,
             '    if (startup->count == 3 && !strcmp(startup->args[2], "--help"))\n'
             '        return AR_HELP;\n' + anchor), 90, b"ORACLE: selector-action\n"),
        ]
        for label, source, expected, oracle in variants:
            path = work / (label + ".c")
            path.write_text(source)
            binary = work / label
            command(label + "-compile", cc + host + [str(path),
                    str(HERE / "parser-controls.c"), "-o", str(binary)])
            command(label + "-libraries", ["/usr/bin/otool", "-L", str(binary)])
            result = command(label, [str(binary)], expected)
            ok = (result.stderr == oracle and not result.stdout) if oracle else (
                not result.stderr and re.fullmatch(
                    rb"PASS: parser checks=[1-9][0-9]*\n", result.stdout) is not None)
            report["cases"].append({"case": label, "pass": ok,
                                    "source_sha256": sha(path), "binary_sha256": sha(binary)})
            if not ok:
                raise RuntimeError(label + ": wrong oracle")
        obj = work / "runner-parse.o"
        command("native-object", cc + flags + ["--target=x86_64-linux-musl",
                "--sysroot=" + str(sdk / "empty-root"), "-nostdinc", "-isystem",
                str(sdk / "stage/usr/include"), "-O2", "-ffreestanding",
                "-fno-builtin", "-fstack-protector-strong", "-c",
                str(HERE / "runner-parse.c"), "-o", str(obj)])
        header = command("object-header", [tools["readelf"]["path"], "-h", str(obj)]).stdout
        if (b"REL (Relocatable file)" not in header or
                b"Advanced Micro Devices X86-64" not in header):
            raise RuntimeError("unexpected object kind")
        imports = command("object-imports", [tools["nm"]["path"],
                          "--undefined-only", str(obj)]).stdout
        names = {line.split()[-1].decode() for line in imports.splitlines()}
        if not names <= {"memcmp", "memcpy", "memset", "strcmp", "strchr", "__stack_chk_fail"}:
            raise RuntimeError("unexpected pure parser import")
        report["object"] = {"sha256": sha(obj), "imports": sorted(names)}
        verify_inputs()
        if sha(runtime) != report["sanitizer_runtime"]["sha256"]:
            raise RuntimeError("runtime changed")
        report["status"] = "pass"
    finally:
        save()
    print("PASS: parser host controls, two semantic mutations, native object")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
