#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Fixed Linux-QEMU byte and disposable-PTY checks; Python 3.10+."""

import hashlib
import json
import os
from pathlib import Path
import platform
import pty
import subprocess
import sys
import termios


def main():
    build = Path(sys.argv[1])
    evidence = json.loads((build / "evidence.json").read_text())
    commands = {}
    for name, row in evidence["binaries"].items():
        path = Path(row["path"])
        if hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
            raise RuntimeError("binary changed")
        commands[name] = ["/usr/bin/qemu-x86_64", str(path)]
        if "applet" in row:
            if row["applet"] != name or name not in {"tr", "stty"}:
                raise RuntimeError("unexpected applet binding")
            commands[name].append(name)
    results = []

    def run(name, program, args, data=b"", expected=b"", status=0,
            fd=None, output=None):
        options = {"input": data} if fd is None else {"stdin": fd}
        result = subprocess.run(
            commands[program] + args, **options,
            stdout=subprocess.PIPE if output is None else output,
            stderr=subprocess.PIPE, timeout=15,
            env={"PATH": "/usr/bin:/bin", "LC_ALL": "C"}, cwd="/scratch",
        )
        passed = (result.returncode == status
                  and (expected is None or result.stdout == expected)
                  and (result.stderr == b"" if status == 0
                       else bool(result.stderr)))
        results.append({"case": name, "argv": commands[program] + args,
                        "status": result.returncode, "expected_status": status,
                        "stdin_hex": data.hex(), "expected_stdout_hex":
                        None if expected is None else expected.hex(),
                        "stdout_hex": (result.stdout or b"").hex(),
                        "stderr_hex": result.stderr.hex(), "pass": passed})
        Path("/scratch/partial-cases.json").write_text(
            json.dumps(results, indent=2) + "\n")
        return result

    run("package-whitespace", "tr", ["-d", "[:space:]"],
        b" \t12\n3\v\f\r ", b"123")
    run("translation", "tr", ["a-z", "A-Z"], b"ab9\n", b"AB9\n")
    run("squeeze", "tr", ["-s", "a"], b"aaabbbaa\n", b"abbba\n")
    run("complement", "tr", ["-cd", "0-9"], b"a1b2\n", b"12")
    run("nul-delete", "tr", ["-d", "\\000"], b"a\0b\0", b"ab")
    high = bytes(range(128, 256))
    run("high-bytes", "tr", ["a", "b"], high, high)
    run("repeat", "tr", ["0-9", "[x*]"], b"a123\n", b"axxx\n")
    run("print-class", "tr", ["-cd", "[:print:]"], b"\0 A\n\xff", b" A")
    run("invalid-class", "tr", ["-d", "[:bogus:]"], status=1)
    run("reversed-range", "tr", ["z-a", "x"], status=1)
    run("empty-target", "tr", ["a", ""], status=1)
    with open("/dev/full", "wb") as full:
        run("output-full", "tr", ["a", "b"], b"a", expected=None,
            status=1, output=full)
    run("not-terminal", "stty", ["-g"], status=1)
    master, slave = pty.openpty()
    try:
        original = termios.tcgetattr(slave)
        saved = run("pty-save", "stty", ["-g"], expected=None, fd=slave)
        state = saved.stdout.decode().strip()
        if not state or saved.returncode:
            raise RuntimeError("no terminal state")
        run("pty-noecho", "stty", ["-echo"], fd=slave)
        actual = termios.tcgetattr(slave)
        results[-1]["termios_before"] = repr(original)
        results[-1]["termios_after"] = repr(actual)
        results[-1]["expected_echo"] = False
        results[-1]["pass"] &= not bool(actual[3] & termios.ECHO)
        run("pty-restore", "stty", [state], fd=slave)
        observed = termios.tcgetattr(slave)
        results[-1]["expected_termios"] = repr(original)
        results[-1]["observed_termios"] = repr(observed)
        results[-1]["pass"] &= observed == original
        run("pty-invalid", "stty", ["aether-invalid-mode"], status=1, fd=slave)
        observed = termios.tcgetattr(slave)
        results[-1]["expected_termios"] = repr(original)
        results[-1]["observed_termios"] = repr(observed)
        results[-1]["pass"] &= observed == original
    finally:
        os.close(slave)
        os.close(master)
    summary = {"scope": "Linux QEMU, private PTY; not Aether TTY authority",
               "python": sys.version, "kernel": platform.uname()._asdict(),
               "qemu_sha256": hashlib.sha256(
                   Path("/usr/bin/qemu-x86_64").read_bytes()).hexdigest(),
               "results": results,
               "expected_cases": 17, "pass": len(results) == 17
               and all(row["pass"] for row in results)}
    Path("/scratch/cases.json").write_text(
        json.dumps(summary, indent=2) + "\n")
    print("PASS" if summary["pass"] else "INCOMPLETE")
    return 0 if summary["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
