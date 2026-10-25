#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Diagnose pinned Clang ASan on this host; Python 3.10+. Not a sanitizer pass."""
import hashlib
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import tempfile
import time

from process import clean_env, run

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PLAN = ROOT / "docs/evidence/asan-host-2026-09-07/PLAN.md"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if sys.argv[1:] == ["--help"]:
        print(__doc__)
        print("Usage: python3 -B experiments/command-runner/"
              "check-asan-host.py [--help|--version]")
        print("No arguments: diagnose pinned ASan; retain results under build/.")
        print("Does not switch the Clang pin. See EXTENDED.md.")
        return 0
    if sys.argv[1:] == ["--version"]:
        print("aether-asan-host 0.1.0")
        return 0
    if sys.argv[1:]:
        print("[ERROR] Unexpected arguments; use --help.", file=sys.stderr)
        return 64
    work = Path(tempfile.mkdtemp(prefix="asan-host-", dir=ROOT / "build"))
    print("[INFO] Evidence: " + str(work), file=sys.stderr, flush=True)
    pin = ROOT / "docs/evidence/native-stdio-files-2026-09-05/libc/evidence.json"
    tool = json.loads(pin.read_text())["tools"]["clang"]
    apple = Path("/usr/bin/clang")
    sources = [HERE / "check-asan-host.py", HERE / "process.py", PLAN]
    report = {"status": "incomplete",
              "scope": "pinned Clang 21.1.8 ASan diagnosis; not product ASan",
              "python": sys.version, "platform": platform.platform(),
              "compiler": tool, "apple_clang": str(apple),
              "apple_clang_sha256": sha(apple), "pin_sha256": sha(pin),
              "sources": {str(p): sha(p) for p in sources}, "commands": []}
    env = clean_env(work)
    env["ASAN_OPTIONS"] = "halt_on_error=1:detect_leaks=0:symbolize=0"
    env["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=0"

    def save():
        (work / "summary.json").write_text(json.dumps(report, indent=2) + "\n")

    def command(label, argv, expected=0, timeout=30, cwd=None, extra_env=None):
        started = time.monotonic()
        child_env = dict(env)
        if extra_env:
            child_env.update(extra_env)
        result = run(argv, cwd=cwd or work, env=child_env, work=work,
                     label=label, timeout=timeout)
        report["commands"].append({"label": label, "process": result.record,
                                   "elapsed_seconds": time.monotonic() - started})
        save()
        if not result.record["complete"] or result.returncode != expected:
            raise RuntimeError(label + ": unexpected result; see evidence")
        return result

    save()
    try:
        if sha(Path(tool["path"])) != tool["sha256"]:
            raise RuntimeError("compiler pin mismatch")
        snapshot = work / "sources"
        snapshot.mkdir()
        for p in sources:
            (snapshot / p.name).write_bytes(p.read_bytes())
        cc = [tool["path"], "--no-default-config"]
        sdk = Path(command("host-sdk", ["/usr/bin/xcrun", "--show-sdk-path"])
                   .stdout.decode().strip())
        flags = ["-std=c17", "-Wall", "-Wextra", "-Werror", "-O1", "-g",
                 "-fno-omit-frame-pointer", "-fno-sanitize-recover=all",
                 "-isysroot", str(sdk)]
        empty = work / "empty.c"
        empty.write_text("/* SPDX-License-Identifier: BSD-2-Clause */\n"
                         "int main(void) { return 0; }\n")
        ubsan = work / "empty-ubsan"
        command("ubsan-compile", cc + flags + ["-fsanitize=undefined",
                str(empty), "-o", str(ubsan)])
        command("ubsan-empty", [str(ubsan)], timeout=5)
        asan = work / "empty-asan"
        command("asan-compile", cc + flags + ["-fsanitize=address",
                str(empty), "-o", str(asan)])
        command("asan-libraries", ["/usr/bin/otool", "-L", str(asan)])
        started = time.monotonic()
        stdout_path = work / "asan-empty.stdout"
        stderr_path = work / "asan-empty.stderr"
        stdin_path = work / "asan-empty.stdin"
        stdin_path.write_bytes(b"")
        hang = {
            "argv": [str(asan)], "cwd": str(work), "environment": dict(env),
            "timeout_seconds": 5, "exit": None, "complete": False,
            "cleanup": "not-started", "failure": None,
        }
        (work / "asan-empty.process.json").write_text(
            json.dumps(hang, indent=2) + "\n")
        with stdin_path.open("rb") as stdin, stdout_path.open("wb") as stdout:
            with stderr_path.open("wb") as stderr:
                proc = subprocess.Popen(
                    [str(asan)], cwd=work, env=env, stdin=stdin,
                    stdout=stdout, stderr=stderr, start_new_session=True)
                hang["process_group"] = proc.pid
                (work / "asan-empty.process.json").write_text(
                    json.dumps(hang, indent=2) + "\n")
                time.sleep(1)
                sample = work / "asan-empty.sample.txt"
                command("asan-sample",
                        ["/usr/bin/sample", str(proc.pid), "1", "-file",
                         str(sample)], timeout=15)
                os.killpg(proc.pid, signal.SIGKILL)
                hang["exit"] = proc.wait(timeout=5)
                hang["failure"] = "timeout"
                hang["cleanup"] = "complete"
                hang["elapsed_seconds"] = time.monotonic() - started
        (work / "asan-empty.process.json").write_text(
            json.dumps(hang, indent=2) + "\n")
        report["commands"].append({"label": "asan-empty", "process": hang})
        save()
        text = sample.read_text(errors="replace")
        if "AsanInitInternal" not in text or "LockSlow" not in text:
            raise RuntimeError("sample missing ASan init deadlock frames")
        if stdout_path.read_bytes() or stderr_path.read_bytes():
            raise RuntimeError("ASan hang produced output")
        report["asan_deadlock"] = {
            "os": platform.platform(),
            "sample": str(sample),
            "frames": ["AsanInitInternal", "LockSlow"],
        }
        canary = work / "canary.c"
        canary.write_text(
            "/* SPDX-License-Identifier: BSD-2-Clause */\n"
            "#include <stdlib.h>\nint main(void) { volatile unsigned i = 8; "
            "volatile char *p = malloc(8); if (!p) return 2; p[i] = 1; "
            "free((void *)p); return 0; }\n")
        canary_bin = work / "canary-asan"
        command("canary-compile", cc + flags + ["-fsanitize=address",
                str(canary), "-o", str(canary_bin)])
        started = time.monotonic()
        canary_result = run([str(canary_bin)], cwd=work, env=env, work=work,
                            label="canary-asan", timeout=5)
        report["commands"].append({
            "label": "canary-asan", "process": canary_result.record,
            "elapsed_seconds": time.monotonic() - started,
        })
        save()
        if (canary_result.record.get("failure") != "timeout" or
                canary_result.record.get("cleanup") != "complete"):
            raise RuntimeError("pinned ASan canary did not time out cleanly")
        if b"AddressSanitizer" in canary_result.stderr:
            raise RuntimeError("canary reached ASan diagnostics")
        apple_bin = work / "empty-apple-asan"
        apple_env = {"PATH": "/usr/bin:/bin", "LC_ALL": "C",
                     "TMPDIR": str(work)}
        command("apple-version", [str(apple), "--version"], extra_env=apple_env)
        command("apple-compile",
                [str(apple), "-std=c17", "-fsanitize=address",
                 str(empty), "-o", str(apple_bin)], extra_env=apple_env)
        command("apple-libraries", ["/usr/bin/otool", "-L", str(apple_bin)])
        apple_run = command("apple-asan-empty", [str(apple_bin)], timeout=5,
                            extra_env=apple_env)
        report["apple_comparison"] = {
            "qualified": False,
            "empty_main_exit": apple_run.returncode,
            "note": "comparison only; not the pinned compiler",
        }
        report["status"] = "pass"
    except (OSError, ValueError, RuntimeError) as error:
        report["error"] = str(error)
        print("[ERROR] " + json.dumps(str(error), ensure_ascii=True),
              file=sys.stderr)
        return 1
    finally:
        save()
    print("[PASS] Pinned ASan deadlocks at init on this OS; UBSan empty main "
          "works; Apple clang ASan comparison only; PXE-04 blocked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
