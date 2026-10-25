#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Host static analysis, RSS metrics, concurrency and transport stress; Python 3.10+."""
import hashlib
import json
from pathlib import Path
import platform
import sys
import tempfile
import time

from process import clean_env, run

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PLAN = ROOT / "docs/evidence/extended-host-2026-09-07/PLAN.md"
TIDY_CHECKS = ("clang-analyzer-core.NullDereference,"
               "clang-analyzer-core.uninitialized.Assign,"
               "clang-analyzer-core.DivideZero,"
               "clang-analyzer-unix.Malloc")
NULL_MARK = b"Dereference of null pointer"
RSS_BUDGET = 32 * 1024 * 1024
RSS_GROW = 64 * 1024 * 1024


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if sys.argv[1:] == ["--help"]:
        print(__doc__)
        print("Usage: python3 -B experiments/command-runner/"
              "check-extended-host.py [--help|--version]")
        print("No arguments: run offline host extended checks; retain build/.")
        print("Executed C uses UBSan only; ASan is out of scope for this command.")
        print("Requires pinned macOS LLVM 21.1.8. See EXTENDED.md.")
        return 0
    if sys.argv[1:] == ["--version"]:
        print("aether-extended-host 0.1.0")
        return 0
    if sys.argv[1:]:
        print("[ERROR] Unexpected arguments; use --help.", file=sys.stderr)
        return 64
    work = Path(tempfile.mkdtemp(prefix="extended-host-", dir=ROOT / "build"))
    print("[INFO] Evidence: " + str(work), file=sys.stderr, flush=True)
    pin = ROOT / "docs/evidence/native-stdio-files-2026-09-05/libc/evidence.json"
    tool = json.loads(pin.read_text())["tools"]["clang"]
    tidy = Path(tool["path"]).with_name("clang-tidy")
    sources = [HERE / name for name in (
        "runner-parse.c", "runner-parse.h", "parser-extended.c",
        "parser-reduce-oracle.c", "parser-static-canary.c",
        "parser-resource.c", "parser-concurrency.c",
        "parser-transport-stress.c", "native-io.c", "native-io.h",
        "check-extended-host.py", "process.py")]
    sources += [HERE.parent / "native-channel/channel.h", PLAN]
    report = {"status": "incomplete",
              "scope": "macOS host UBSan, clang-tidy/analyze; ASan NOT RUN",
              "python": sys.version, "platform": platform.platform(),
              "compiler": tool, "clang_tidy": str(tidy),
              "clang_tidy_sha256": sha(tidy), "pin_sha256": sha(pin),
              "sources": {str(p): sha(p) for p in sources}, "commands": []}
    env = clean_env(work)
    env["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=0"

    def save():
        (work / "summary.json").write_text(json.dumps(report, indent=2) + "\n")

    def command(label, argv, expected=0, marker=None, absent=None, timeout=30,
                cwd=None):
        started = time.monotonic()
        result = run(argv, cwd=cwd or work, env=env, work=work, label=label,
                     timeout=timeout)
        report["commands"].append({"label": label, "process": result.record,
                                   "elapsed_seconds": time.monotonic() - started})
        save()
        combined = result.stderr + result.stdout
        if (not result.record["complete"] or result.returncode != expected or
                (marker is not None and marker not in combined) or
                (absent is not None and absent in combined)):
            raise RuntimeError(label + ": unexpected result; see evidence")
        return result

    def verify():
        if sha(Path(tool["path"])) != tool["sha256"]:
            raise RuntimeError("compiler pin mismatch")
        if sha(tidy) != report["clang_tidy_sha256"]:
            raise RuntimeError("clang-tidy changed")
        for path, digest in report["sources"].items():
            if sha(Path(path)) != digest:
                raise RuntimeError("source changed: " + path)
        for path, digest in report.get("runtime_inputs", {}).items():
            if sha(Path(path)) != digest:
                raise RuntimeError("runtime input changed: " + path)

    save()
    try:
        verify()
        snapshot = work / "sources"
        snapshot.mkdir()
        for p in sources:
            (snapshot / p.name).write_bytes(p.read_bytes())
        cc = [tool["path"], "--no-default-config"]
        sdk = Path(command("host-sdk", ["/usr/bin/xcrun", "--show-sdk-path"])
                   .stdout.decode().strip())
        resource = Path(command("resource", cc + ["-print-resource-dir"])
                        .stdout.decode().strip())
        runtime = resource / "lib/darwin/libclang_rt.ubsan_osx_dynamic.dylib"
        report["runtime_inputs"] = {str(sdk / "SDKSettings.json"): sha(sdk / "SDKSettings.json"),
                                    str(runtime): sha(runtime)}
        report["host_sdk"] = str(sdk)
        inc = ["-isysroot", str(sdk), "-I", str(HERE)]
        flags = ["-std=c17", "-Wall", "-Wextra", "-Werror", "-Wpedantic",
                 "-Wconversion", "-Wsign-conversion", "-Wshadow",
                 "-Wstrict-prototypes", "-Wmissing-prototypes", "-O1", "-g",
                 "-fno-omit-frame-pointer", "-fsanitize=undefined",
                 "-fno-sanitize-recover=all"] + inc
        analyze_flags = cc + ["--analyze", "-Xanalyzer", "-analyzer-output=text",
                              "-std=c17", "--no-default-config"] + inc
        tidy_args = ["-std=c17", "--no-default-config"] + inc
        tidy_base = [str(tidy), "--quiet", "--checks=-*," + TIDY_CHECKS]
        clean = ["runner-parse.c", "parser-extended.c", "parser-reduce-oracle.c"]
        for name in clean:
            command("analyze-" + Path(name).stem,
                    analyze_flags + [str(HERE / name),
                                     "-o", str(work / (name + ".plist"))],
                    absent=b"warning:")
            command("tidy-" + Path(name).stem,
                    tidy_base + [str(HERE / name), "--"] + tidy_args,
                    absent=b"warning:")
        canary = HERE / "parser-static-canary.c"
        command("analyze-canary",
                analyze_flags + [str(canary), "-o", str(work / "canary.plist")],
                marker=NULL_MARK)
        command("tidy-canary",
                tidy_base + [str(canary), "--"] + tidy_args, marker=NULL_MARK)
        for label, extra in (("metrics", []), ("grow", ["--grow"]),
                             ("reserve", ["--reserve"])):
            binary = work / ("resource-" + label)
            command("resource-" + label + "-compile",
                    cc + flags + [str(HERE / "runner-parse.c"),
                                  str(HERE / "parser-resource.c"),
                                  "-o", str(binary)])
            result = command("resource-" + label, [str(binary)] + extra)
            rss = json.loads(result.stdout)["ru_maxrss"]
            report["rss_" + label] = rss
            if label == "metrics" and not 0 < rss < RSS_BUDGET:
                raise RuntimeError("parser RSS outside observational budget")
            if label == "grow" and rss < RSS_GROW:
                raise RuntimeError("grow control did not raise RSS")
            if label == "reserve" and rss >= RSS_GROW:
                raise RuntimeError("undirtied mmap satisfied the grow oracle")
        conc = work / "concurrency"
        command("concurrency-compile",
                cc + flags + [str(HERE / "runner-parse.c"),
                              str(HERE / "parser-concurrency.c"),
                              "-o", str(conc)])
        result = command("concurrency", [str(conc)])
        if result.stdout != b"PASS: concurrency\n":
            raise RuntimeError("missing concurrency marker")
        started = time.monotonic()
        hang_result = run([str(conc), "--hang"], cwd=work, env=env, work=work,
                          label="hang", timeout=5)
        report["commands"].append({"label": "hang",
                                   "process": hang_result.record,
                                   "elapsed_seconds": time.monotonic() - started})
        save()
        if (hang_result.record.get("failure") != "timeout" or
                hang_result.record.get("cleanup") != "complete"):
            raise RuntimeError("hang watchdog did not clean up")
        include = work / "include/sys"
        include.mkdir(parents=True)
        (include / "auxv.h").write_text(
            "/* SPDX-License-Identifier: BSD-2-Clause */\n"
            "unsigned long getauxval(unsigned long);\n")
        transport_flags = [
            "-std=c17", "-D_POSIX_C_SOURCE=200809L", "-O1", "-g",
            "-Wall", "-Wextra", "-Werror", "-fno-omit-frame-pointer",
            "-fsanitize=undefined", "-fno-sanitize-recover=all",
            "-isysroot", str(sdk), "-I", str(work / "include"), "-I", str(HERE)]
        transport = work / "transport"
        command("transport-compile",
                cc + transport_flags + [str(HERE / "native-io.c"),
                                        str(HERE / "parser-transport-stress.c"),
                                        "-o", str(transport)])
        result = command("transport", [str(transport)])
        if result.stdout != b"PASS: transport stress\n" or result.stderr:
            raise RuntimeError("transport stress failed")
        verify()
        report["status"] = "pass"
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        report["error"] = str(error)
        print("[ERROR] " + json.dumps(str(error), ensure_ascii=True),
              file=sys.stderr)
        return 1
    finally:
        save()
    print("[PASS] Host static analysis, RSS metrics, concurrency and "
          "transport stress; ASan NOT RUN.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
