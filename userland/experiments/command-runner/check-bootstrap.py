#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Host bootstrap controls on the actual adapter; Python 3.10+."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys
import tempfile

from process import clean_env, run

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CASES = ([f"valid-{role}-{gen}" for role in ("parent", "child")
          for gen in ("gen1", "gen2")]
         + [f"bad-word-{i}" for i in range(8)]
         + ["bad-generation", "missing-input", "missing-output",
            "missing-both", "equal-channels"]
         + [f"prefix-{n}" for n in (0, 1, 4, 16, 31)])

STARTUP_CASES = (["valid-simple", "valid-wide", "bad-carrier",
                  "legacy-on-carrier", "null-output", "missing-aux"]
                 + [f"prefix-{n}" for n in range(256)]
                 + [f"binding-{n}" for n in range(8)])

TRANSFER_CASES = (
    ["short", "short-eagain", "error-1", "error-4095"]
    + [f"{direction}-{failure}" for direction in ("tx", "rx")
       for failure in ("zero", "error", "overlong", "eagain")]
    + ["rx-partial", "result-overlong", "result-negative-range"]
    + [f"metadata-{offset}" for offset in range(4, 16)]
    + [f"padding-{offset}" for offset in range(18, 32)]
    + ["close-lost", "close-negative", "close-positive", "close-padding",
       "close-valid", "write-padding", "write-valid"]
    + [f"size-{size}" for size in (0, 1, 31, 33, 383)]
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mutations", action="store_true")
    parser.add_argument("--suite", choices=("bootstrap", "transfer", "startup"),
                        default="bootstrap")
    parser.add_argument("--sanitizer", choices=("address,undefined", "undefined"),
                        default="address,undefined")
    args = parser.parse_args()
    cases = {"bootstrap": CASES, "transfer": TRANSFER_CASES,
             "startup": STARTUP_CASES}[args.suite]
    control_source = HERE / (args.suite + "-controls.c")
    marker = ("PASS: " + args.suite + " boundary\n").encode()
    work = Path(tempfile.mkdtemp(prefix="command-bootstrap-", dir=ROOT / "build"))
    print(work, flush=True)
    pin = ROOT / "docs/evidence/native-stdio-files-2026-09-05/libc/evidence.json"
    compiler = json.loads(pin.read_text())["tools"]["clang"]
    if sha(Path(compiler["path"])) != compiler["sha256"]:
        raise RuntimeError("compiler pin mismatch")
    env = clean_env(work)
    env["ASAN_OPTIONS"] = "detect_leaks=0:abort_on_error=1"
    env["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=1"
    inputs = [HERE / n for n in ("native-io.c", "native-io.h",
              "check-bootstrap.py", "process.py")]
    inputs += [HERE.parent / "native-channel/channel.h", HERE / "BOUNDARY-PLAN.md"]
    inputs.append(control_source)
    if args.suite == "startup":
        inputs += [HERE / "runner-parse.c", HERE / "runner-parse.h",
                   ROOT / "docs/evidence/runner-startup-2026-09-06/change-review.md"]
    sources = {str(p): sha(p) for p in inputs}
    report = {"scope": "host " + args.suite + " adapter; no native boundary acceptance",
              "status": "incomplete", "cases": [], "commands": [],
              "sources": sources, "compiler": compiler,
              "compiler_pin_sha256": sha(pin), "python": sys.version,
              "platform": platform.platform(), "inventory": cases,
              "leak_detection": "disabled; not claimed",
              "sanitizer_selection": args.sanitizer}

    def save():
        (work / "summary.json").write_text(json.dumps(report, indent=2) + "\n")

    def command(label, argv):
        result = run(argv, cwd=work, env=env, work=work, label=label, timeout=30)
        report["commands"].append({"label": label, "process": result.record})
        save()
        if not result.record["complete"]:
            raise RuntimeError(label + ": incomplete process cleanup/execution")
        return result

    def checked(label, argv):
        result = command(label, argv)
        if result.returncode:
            raise RuntimeError(label + ": failed; see retained logs")
        return result.stdout

    save()
    try:
        sdk = checked("host-sdk", ["/usr/bin/xcrun", "--show-sdk-path"]).decode().strip()
        cc = [compiler["path"], "--no-default-config"]
        resource = Path(checked("resource-dir", cc + ["-print-resource-dir"]).decode().strip())
        runtime_name = "asan" if "address" in args.sanitizer else "ubsan"
        runtime = resource / ("lib/darwin/libclang_rt." + runtime_name
                              + "_osx_dynamic.dylib")
        report["sanitizer_runtime"] = {"path": str(runtime), "sha256": sha(runtime)}
        include = work / "include/sys"
        include.mkdir(parents=True)
        (include / "auxv.h").write_text(
            "/* SPDX-License-Identifier: BSD-2-Clause */\n"
            "unsigned long getauxval(unsigned long);\n")
        report["host_auxv_declaration_sha256"] = sha(include / "auxv.h")
        flags = ["-std=c17", "-D_POSIX_C_SOURCE=200809L", "-O1", "-g",
                 "-Wall", "-Wextra", "-Werror", "-fno-omit-frame-pointer",
                 "-fsanitize=" + args.sanitizer, "-fno-sanitize-recover=all",
                 "-isysroot", sdk, "-I", str(work / "include"), "-I", str(HERE)]

        if args.suite == "startup":
            flags += ["-DNATIVE_RUNNER_STARTUP"]

        def build(label, source):
            binary = work / label
            checked(label + "-compile", cc + flags + [str(source),
                    str(control_source),
                    *([str(HERE / "runner-parse.c")] if args.suite == "startup" else []),
                    "-o", str(binary)])
            checked(label + "-libraries", ["/usr/bin/otool", "-L", str(binary)])
            return binary

        if args.suite == "startup":
            checked("startup-strict-source", cc + flags + [
                "-Wpedantic", "-Wconversion", "-Wsign-conversion", "-Wshadow",
                "-Wstrict-prototypes", "-Wmissing-prototypes", "-fsyntax-only",
                str(control_source)])
        binary = build("controls", HERE / "native-io.c")
        for case in cases:
            result = command(case, [str(binary), case])
            ok = result.returncode == 0 and result.stdout == marker and not result.stderr
            report["cases"].append({"case": case, "pass": ok,
                                    "exit": result.returncode})
            save()
        if args.mutations:
            original = (HERE / "native-io.c").read_text()
            anchor = "    /* Validate the complete pair before publishing either binding. */"
            if original.count(anchor) != 1:
                raise RuntimeError("early-publication mutation anchor changed")
            early = original.replace(anchor,
                "    refs[0] = native_word(r + 4);\n"
                "    fds[0] = native_word(r + 8);\n"
                "    rights[0] = native_word(r + 12);\n"
                "    live[0] = 1;\n" + anchor)
            guard = "    if (poisoned)\n        return 0;"
            if original.count(guard) != 1:
                raise RuntimeError("poison mutation anchor changed")
            unguarded = original.replace(guard, "    /* test-only disabled guard */")
            mutations = [
                ("early-publication", early, "bad-word-4", "no-published-references"),
                ("disabled-poison", unguarded, "bad-word-0", "failed-startup-exchange-traffic"),
            ]
            if args.suite == "transfer":
                validation = "    if (bad || (op == 3 && result)) {"
                if original.count(validation) != 1:
                    raise RuntimeError("reply mutation anchor changed")
                unchecked = original.replace(validation,
                    "    if ((bad || (op == 3 && result)) && 0) {")
                mutations = [
                    ("disabled-poison", unguarded, "rx-zero", "no-replay-traffic"),
                    ("disabled-validation", unchecked, "metadata-4", "reply-result"),
                ]
            if args.suite == "startup":
                admission = "    unsigned char r[32];\n    if (!input"
                if original.count(admission) != 1:
                    raise RuntimeError("carrier publication anchor changed")
                early_args = original.replace(admission,
                    "    if (carrier)\n        *startup = candidate;\n" + admission)
                retry = "if (bootstrap_attempted)"
                if original.count(retry) != 1:
                    raise RuntimeError("carrier retry anchor changed")
                mutations = [
                    ("early-arguments", early_args, "binding-7", "no-mid-read-arguments"),
                    ("disabled-reentry", original.replace(retry,
                     "if (bootstrap_attempted && 0)"), "missing-aux", "reentry-traffic"),
                ]
            for label, source, case, oracle in mutations:
                path = work / (label + ".c")
                path.write_text(source)
                mutant = build(label, path)
                result = command(label, [str(mutant), case])
                ok = (result.returncode == 90 and not result.stdout
                      and result.stderr == ("ORACLE: " + oracle + "\n").encode())
                report["cases"].append({"case": label, "pass": ok,
                    "expected_oracle": oracle, "exit": result.returncode,
                    "mutant_sha256": sha(path)})
                save()
        for name, digest in sources.items():
            if sha(Path(name)) != digest:
                raise RuntimeError("source changed: " + name)
        if sha(runtime) != report["sanitizer_runtime"]["sha256"]:
            raise RuntimeError("sanitizer runtime changed")
        report["status"] = "pass" if all(c["pass"] for c in report["cases"]) else "fail"
    finally:
        save()
    print(report["status"].upper() + ": " + str(len(report["cases"])) + " " + args.suite + " controls")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
