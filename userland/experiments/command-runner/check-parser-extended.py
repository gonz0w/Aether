#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Run the fixed host parser mutation, replay and reduction controls; Python 3.10+."""
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import sys
import tempfile
import time

from process import clean_env, run

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PLAN = ROOT / "docs/evidence/parser-replay-2026-09-07/PLAN.md"
ORACLE_BUDGET = 1024
ORACLE_GAP = 180
MAX_INPUT = 225


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exclusive_write(path, data):
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    with os.fdopen(fd, "wb") as handle:
        if handle.write(data) != len(data):
            raise RuntimeError("short exclusive write: " + str(path))


class ReduceError(RuntimeError):
    pass


def reduction_outcome(result, directory, candidate, must_accept, oracle):
    """Classify complete replay evidence; infrastructure errors are not negatives."""
    if not result.record["complete"]:
        raise ReduceError("incomplete replay process")
    paths = [directory / "failure.bin", directory / "failure.json"]
    if result.returncode == 0:
        if (result.stdout != b"PASS: replay\n" or result.stderr or
                any(p.exists() for p in paths)):
            raise ReduceError("invalid passing replay evidence")
        return False
    if result.returncode != 90:
        raise ReduceError("unexpected replay exit")
    pattern = (rb"ORACLE: " + re.escape(oracle.encode("ascii")) +
               rb" seed=[0-9]+ offset=[0-9]+ value=[0-9]+\n")
    if result.stdout or re.fullmatch(pattern, result.stderr) is None:
        raise ReduceError("unexpected replay diagnostics")
    try:
        with paths[0].open("rb") as handle:
            payload = handle.read(MAX_INPUT + 1)
        with paths[1].open("rb") as handle:
            encoded = handle.read(1025)
        if len(encoded) > 1024:
            raise ReduceError("oversized replay metadata")
        meta = json.loads(encoded)
    except (OSError, ValueError) as error:
        raise ReduceError("unreadable replay evidence") from error
    if (len(payload) > MAX_INPUT or payload != candidate or
            not isinstance(meta, dict) or
            set(meta) != {"oracle", "size", "must_accept"} or
            meta["oracle"] != oracle or type(meta["size"]) is not int or
            meta["size"] != len(candidate) or
            type(meta["must_accept"]) is not int or
            meta["must_accept"] != must_accept):
        raise ReduceError("mismatched replay evidence")
    return True


def main():
    if sys.argv[1:] == ["--help"]:
        print(__doc__)
        print("Usage: python3 -B experiments/command-runner/"
              "check-parser-extended.py [--help|--version|--ubsan-only]")
        print("No arguments: run offline checks; retain results under build/.")
        print("--ubsan-only explicitly omits ASan; default requires both.")
        print("Requires the pinned macOS LLVM toolchain. See EXTENDED.md.")
        return 0
    if sys.argv[1:] == ["--version"]:
        print("aether-parser-extended 0.1.0")
        return 0
    ubsan_only = sys.argv[1:] == ["--ubsan-only"]
    if sys.argv[1:] and not ubsan_only:
        print("[ERROR] Unexpected arguments; use --help.", file=sys.stderr)
        return 64
    work = Path(tempfile.mkdtemp(prefix="parser-extended-", dir=ROOT / "build"))
    print("[INFO] Evidence: " + str(work), file=sys.stderr, flush=True)
    pin = ROOT / "docs/evidence/native-stdio-files-2026-09-05/libc/evidence.json"
    tool = json.loads(pin.read_text())["tools"]["clang"]
    sources = [HERE / name for name in (
        "runner-parse.c", "runner-parse.h", "parser-controls.c",
        "parser-extended.c", "parser-reduce-oracle.c",
        "check-parser-extended.py", "test-parser-reduction.py", "process.py")]
    sources.append(PLAN)
    sources.append(ROOT / "docs/evidence/parser-reducer-review-2026-09-07/PLAN.md")
    report = {"status": "incomplete", "scope": ("macOS host UBSan only; ASan NOT RUN" if ubsan_only
                        else "macOS host ASan/UBSan only"),
              "python": sys.version, "platform": platform.platform(),
              "compiler": tool, "pin_sha256": sha(pin),
              "sources": {str(p): sha(p) for p in sources}, "commands": []}
    env = clean_env(work)
    env.update(ASAN_OPTIONS="halt_on_error=1:detect_leaks=0:symbolize=0",
               UBSAN_OPTIONS="halt_on_error=1:print_stacktrace=0")

    def save():
        (work / "summary.json").write_text(json.dumps(report, indent=2) + "\n")

    def command(label, argv, expected=0, marker=None, cwd=None, absent=None):
        started = time.monotonic()
        result = run(argv, cwd=cwd or work, env=env, work=work, label=label,
                     timeout=30)
        report["commands"].append({"label": label, "process": result.record,
                                   "elapsed_seconds": time.monotonic() - started})
        save()
        if expected == "any":
            exit_ok = True
        elif expected is None:
            exit_ok = result.returncode != 0
        else:
            exit_ok = result.returncode == expected
        if (not result.record["complete"] or not exit_ok or
                (marker is not None and marker not in result.stderr) or
                (absent is not None and absent in result.stderr)):
            raise RuntimeError(label + ": unexpected result; see evidence")
        return result

    def verify():
        if sha(Path(tool["path"])) != tool["sha256"]:
            raise RuntimeError("compiler pin mismatch")
        for path, digest in report["sources"].items():
            if sha(Path(path)) != digest:
                raise RuntimeError("source changed: " + path)
        for path, digest in report.get("runtime_inputs", {}).items():
            if sha(Path(path)) != digest:
                raise RuntimeError("runtime input changed: " + path)

    def read_failure(directory):
        meta = json.loads((directory / "failure.json").read_text())
        payload = (directory / "failure.bin").read_bytes()
        if (meta.get("oracle") in (None, "") or
                meta.get("size") != len(payload) or
                meta.get("must_accept") not in (0, 1) or
                len(payload) > MAX_INPUT):
            raise RuntimeError("invalid retained failure in " + str(directory))
        return payload, meta

    def replay(label, binary, data, must_accept, expected, oracle=None,
               extra=None):
        cwd = work / label
        cwd.mkdir()
        exclusive_write(cwd / "input.bin", data)
        exclusive_write(cwd / "expected.json", json.dumps({
            "must_accept": must_accept, "size": len(data),
            "oracle": oracle, "expected_exit": expected,
        }).encode() + b"\n")
        argv = [str(binary), "--replay", "input.bin",
                "1" if must_accept else "0"]
        if extra:
            argv.extend(extra)
        marker = None if oracle is None else (
            "ORACLE: " + oracle + " ").encode()
        absent = b"ORACLE:" if expected == 91 else None
        result = command(label, argv, expected, marker, cwd, absent)
        if expected == 90:
            payload, meta = read_failure(cwd)
            if payload != data or meta["oracle"] != oracle:
                raise RuntimeError(label + ": retained failure mismatch")
            if meta["must_accept"] != must_accept:
                raise RuntimeError(label + ": must_accept mismatch")
        elif (cwd / "failure.bin").exists() or (cwd / "failure.json").exists():
            raise RuntimeError(label + ": unexpected retained failure")
        if expected == 0 and result.stdout != b"PASS: replay\n":
            raise RuntimeError(label + ": missing replay marker")
        return result

    def reduce_input(prefix, binary, original, must_accept, oracle, extra,
                     budget=ORACLE_BUDGET):
        root = work / prefix
        root.mkdir()
        exclusive_write(root / "original.bin", original)
        current = original
        trace = []
        calls = 0
        deadline = time.monotonic()

        def oracle_call(candidate, op, index):
            nonlocal calls, deadline
            now = time.monotonic()
            if now - deadline > ORACLE_GAP:
                raise ReduceError("reduction deadline")
            if calls >= budget:
                raise ReduceError("reduction budget")
            if len(candidate) > MAX_INPUT:
                raise ReduceError("candidate too large")
            calls += 1
            label = prefix + "-" + f"{calls:04d}"
            cwd = work / label
            cwd.mkdir()
            exclusive_write(cwd / "input.bin", candidate)
            argv = [str(binary), "--replay", "input.bin",
                    "1" if must_accept else "0"]
            if extra:
                argv.extend(extra)
            result = command(label, argv, expected="any", cwd=cwd)
            status = None
            reproduced = False
            try:
                reproduced = reduction_outcome(
                    result, cwd, candidate, must_accept, oracle)
            except ReduceError as error:
                status = str(error)
            entry = {"label": label, "op": op, "index": index,
                     "size": len(candidate), "reproduced": reproduced,
                     "exit": result.returncode, "status": status}
            trace.append(entry)
            (root / "trace.json").write_bytes(
                json.dumps(trace, indent=2).encode() + b"\n")
            deadline = time.monotonic()
            if status is not None:
                raise ReduceError(label + ": " + status)
            return reproduced

        if not oracle_call(current, "original", None):
            raise ReduceError("non-reproducing input")
        changed = True
        while changed:
            changed = False
            for i in range(len(current) - 1, -1, -1):
                if current[i] == 0:
                    continue
                candidate = current[:i] + b"\x00" + current[i + 1:]
                if oracle_call(candidate, "zero", i):
                    current = candidate
                    changed = True
                    break
            if changed:
                continue
            for i in range(len(current)):
                candidate = current[:i] + current[i + 1:]
                if oracle_call(candidate, "delete", i):
                    current = candidate
                    changed = True
                    break
        for i in range(len(current)):
            if oracle_call(current[:i] + current[i + 1:], "final-delete", i):
                raise ReduceError("reduction not locally minimal")
        for i in range(len(current) - 1, -1, -1):
            if current[i] == 0:
                continue
            if oracle_call(current[:i] + b"\x00" + current[i + 1:],
                           "final-zero", i):
                raise ReduceError("reduction not locally minimal")
        exclusive_write(root / "reduced.bin", current)
        exclusive_write(root / "reduced.json", json.dumps({
            "oracle": oracle, "must_accept": must_accept,
            "original_size": len(original), "reduced_size": len(current),
            "calls": calls, "local_minimum": True,
        }).encode() + b"\n")
        replay(prefix + "-confirm", binary, current, must_accept, 90, oracle,
               extra)
        return current, calls, trace

    save()
    try:
        verify()
        snapshot = work / "sources"
        snapshot.mkdir()
        for p in sources:
            (snapshot / p.name).write_bytes(p.read_bytes())
        command("reduction-unittests",
                [sys.executable, "-B", str(HERE / "test-parser-reduction.py")])
        cc = [tool["path"], "--no-default-config"]
        sdk = Path(command("host-sdk", ["/usr/bin/xcrun", "--show-sdk-path"])
                   .stdout.decode().strip())
        resource = Path(command("resource", cc + ["-print-resource-dir"])
                        .stdout.decode().strip())
        inputs = [sdk / "SDKSettings.json"] + list(
            (resource / "lib/darwin").glob("libclang_rt.*san_osx_dynamic.dylib"))
        if not any(p.name == "libclang_rt.asan_osx_dynamic.dylib" for p in inputs):
            raise RuntimeError("ASan runtime unavailable")
        report["runtime_inputs"] = {str(p): sha(p) for p in inputs}
        report["host_sdk"] = str(sdk)
        flags = ["-std=c17", "-Wall", "-Wextra", "-Werror", "-Wpedantic",
                 "-Wconversion", "-Wsign-conversion", "-Wshadow",
                 "-Wstrict-prototypes", "-Wmissing-prototypes", "-O1", "-g",
                 "-fno-omit-frame-pointer",
                 "-fsanitize=" + ("undefined" if ubsan_only else "address,undefined"),
                 "-fno-sanitize-recover=all", "-isysroot", str(sdk),
                 "-I", str(snapshot)]
        parser = snapshot / "runner-parse.c"
        original = parser.read_text()
        if original.count("if (record[i])") != 1:
            raise RuntimeError("mutation anchor changed")
        mutant = work / "skip-reserved.c"
        mutant.write_text(original.replace("if (record[i])",
                                           "if (record[i] && 0)"))
        binaries = {}
        for label, implementation, fixture, expected, marker in (
            ("controls", parser, "parser-controls.c", 0, None),
            ("sweep", parser, "parser-extended.c", 0, None),
            ("mutation", mutant, "parser-extended.c", 90,
             b"ORACLE: canonical-carrier seed=0 offset=12 value=1\n"),
        ):
            binary = work / label
            command(label + "-compile", cc + flags + [str(implementation),
                    str(snapshot / fixture), "-o", str(binary)])
            command(label + "-libraries", ["/usr/bin/otool", "-L", str(binary)])
            result = command(label, [str(binary)], expected, marker)
            report[label + "_binary_sha256"] = sha(binary)
            binaries[label] = binary
            if expected == 0 and result.stderr:
                raise RuntimeError(label + ": unexpected diagnostics")
            if label == "controls" and not result.stdout.startswith(
                    b"PASS: parser checks="):
                raise RuntimeError("missing controls marker")
            if label == "sweep":
                report["workload"] = json.loads(result.stdout)
                if report["workload"]["checks"] != 172038:
                    raise RuntimeError("incorrect workload count")
        payload, meta = read_failure(work)
        if (meta["oracle"] != "canonical-carrier" or meta["must_accept"] != 0 or
                meta["size"] != 224 or len(payload) != 224 or payload[12] != 1):
            raise RuntimeError("mutation did not retain the reserved-byte case")
        replay("replay-mutant", binaries["mutation"], payload, 0, 90,
               "canonical-carrier")
        replay("replay-original", binaries["sweep"], payload, 0, 0)
        reduced, calls, _trace = reduce_input(
            "reduce-reserved", binaries["mutation"], payload, 0,
            "canonical-carrier", None)
        if (len(reduced) != 224 or reduced[12] != 1 or
                reduced[:8] != b"AERUN001"):
            raise RuntimeError("reserved-byte reduction lost the defect")
        replay("replay-reduced-original", binaries["sweep"], reduced, 0, 0)
        report["reserved_reduction"] = {
            "calls": calls, "original_size": 224, "reduced_size": len(reduced),
            "zeroed_bytes": sum(1 for a, b in zip(payload, reduced) if a != b),
            "local_minimum": True,
        }
        replay("replay-empty", binaries["sweep"], b"", 0, 0)
        replay("replay-max", binaries["sweep"], bytes(MAX_INPUT), 0, 0)
        replay("replay-oversize", binaries["sweep"], bytes(MAX_INPUT + 1), 0, 91)
        expect_dir = work / "replay-expect"
        expect_dir.mkdir()
        exclusive_write(expect_dir / "input.bin", payload)
        command("replay-expect",
                [str(binaries["sweep"]), "--replay", "input.bin", "2"],
                91, cwd=expect_dir, absent=b"ORACLE:")
        missing = work / "replay-missing"
        missing.mkdir()
        command("replay-missing",
                [str(binaries["sweep"]), "--replay", "missing.bin", "0"],
                91, cwd=missing, absent=b"ORACLE:")
        sentinel = b"sentinel-bytes"
        collision = work / "collision-bin"
        collision.mkdir()
        exclusive_write(collision / "failure.bin", sentinel)
        command("collision-bin", [str(binaries["mutation"])], 91, cwd=collision,
                marker=b"ORACLE: canonical-carrier seed=0 offset=12 value=1\n")
        if (collision / "failure.bin").read_bytes() != sentinel:
            raise RuntimeError("failure.bin was replaced")
        if (collision / "failure.json").exists():
            raise RuntimeError("json written after bin collision")
        collision_json = work / "collision-json"
        collision_json.mkdir()
        exclusive_write(collision_json / "failure.json", sentinel)
        command("collision-json", [str(binaries["mutation"])], 91,
                cwd=collision_json,
                marker=b"ORACLE: canonical-carrier seed=0 offset=12 value=1\n")
        if (collision_json / "failure.json").read_bytes() != sentinel:
            raise RuntimeError("failure.json was replaced")
        if not (collision_json / "failure.bin").exists():
            raise RuntimeError("partial bin retention missing")
        oracle_bin = work / "reduce-oracle"
        command("oracle-compile", cc + flags + [
            str(snapshot / "parser-reduce-oracle.c"), "-o", str(oracle_bin)])
        command("oracle-libraries", ["/usr/bin/otool", "-L", str(oracle_bin)])
        deleted, delete_calls, _trace = reduce_input(
            "reduce-delete", oracle_bin, b"\x00\x00\x00", 0, "too-long",
            ["long"])
        if deleted != b"\x00\x00":
            raise RuntimeError("deletion did not stop at local minimum")
        zeroed, zero_calls, _trace = reduce_input(
            "reduce-zero", oracle_bin, b"\x00\x03\x00", 0, "nonzero",
            ["nonzero"])
        if zeroed != b"\x03":
            raise RuntimeError("zero reduction did not stop at local minimum")
        report["synthetic_reduction"] = {
            "delete_calls": delete_calls, "zero_calls": zero_calls,
            "deleted": list(deleted), "zeroed": list(zeroed),
        }
        try:
            reduce_input("reduce-none", oracle_bin, b"\x00\x00", 0, "nonzero",
                         ["nonzero"])
        except ReduceError as error:
            if str(error) != "non-reproducing input":
                raise
        else:
            raise RuntimeError("non-reproducing input was reduced")
        try:
            reduce_input("reduce-budget", oracle_bin, b"\x00\x00\x00", 0,
                         "too-long", ["long"], budget=1)
        except ReduceError as error:
            if str(error) != "reduction budget":
                raise
            budget_trace = json.loads(
                (work / "reduce-budget" / "trace.json").read_text())
            if (work / "reduce-budget" / "reduced.bin").exists():
                raise RuntimeError("budget exhaustion claimed a minimum")
            if len(budget_trace) != 1 or not budget_trace[0]["reproduced"]:
                raise RuntimeError("budget exhaustion lost the original")
        else:
            raise RuntimeError("budget exhaustion was not reported")
        canaries = {
            "asan": ('#include <stdlib.h>\nint main(void) { '
                     'volatile unsigned i = 8; volatile char *p = malloc(8); '
                     'if (!p) return 2; p[i] = 1; free((void *)p); return 0; }\n',
                     b"ERROR: AddressSanitizer: heap-buffer-overflow"),
            "ubsan": ('#include <limits.h>\nint main(void) { '
                      'volatile int x = INT_MAX; return x + 1; }\n',
                      b"runtime error: signed integer overflow"),
        }
        if ubsan_only:
            del canaries["asan"]
        for label, (source, marker) in canaries.items():
            path = work / (label + ".c")
            path.write_text("/* SPDX-License-Identifier: BSD-2-Clause */\n" + source)
            binary = work / label
            command(label + "-compile", cc + flags + [str(path), "-o", str(binary)])
            command(label, [str(binary)], None, marker)
            report[label + "_binary_sha256"] = sha(binary)
        verify()
        report["status"] = "pass"
    except (OSError, ValueError, RuntimeError) as error:
        report["error"] = str(error)
        print("[ERROR] " + json.dumps(str(error), ensure_ascii=True), file=sys.stderr)
        return 1
    finally:
        save()
    print("[PASS] Host parser mutation sweep, replay/reduction and " +
          ("UBSan controls; ASan NOT RUN." if ubsan_only
           else "ASan/UBSan controls."))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
