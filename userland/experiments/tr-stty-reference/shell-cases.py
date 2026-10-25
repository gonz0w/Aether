#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""GNU shell fixtures inside the pinned Linux image; Python 3.10+."""

import fcntl
import hashlib
import json
import os
from pathlib import Path
import platform
import pty
import signal
import struct
import subprocess
import sys
import termios


def main():
    source = Path(sys.argv[1])
    extended = sys.argv[2:] == ["--extended"]
    env = dict(os.environ, LC_ALL="C", srcdir=str(source),
               abs_top_srcdir=str(source), built_programs="tr stty",
               RUN_EXPENSIVE_TESTS="yes", VERBOSE="yes", SHELL="/bin/bash", PATH_SEPARATOR=":")
    env["PATH"] = str(source / "src") + ":/usr/bin:/bin"
    results = []
    for script in [source / "src/tr", source / "src/stty", source / "src/getlimits",
                   source / "tests/tr/tr-case-class.sh",
                   source / "tests/stty/stty-row-col.sh",
                   source / "tests/stty/stty-invalid.sh",
                   source / "tests/stty/stty.sh",
                   source / "tests/stty/stty-pairs.sh"]:
        subprocess.run(["/bin/bash", "-n", str(script)], cwd="/scratch",
                       env=env, check=True, timeout=5)

    def run(name, tty=False, deadline=45):
        master = slave = None
        before = size_before = None
        if tty:
            master, slave = pty.openpty()
            fcntl.ioctl(slave, termios.TIOCSWINSZ,
                        struct.pack("HHHH", 24, 80, 0, 0))
            before = termios.tcgetattr(slave)
            size_before = fcntl.ioctl(slave, termios.TIOCGWINSZ, bytes(8))

        def session():
            os.setsid()
            if tty:
                fcntl.ioctl(0, termios.TIOCSCTTY, 0)

        command = ["/bin/bash", "-c", 'exec 9>&2; exec /bin/bash "$1"',
                   "gnu-test", str(source / "tests" / name)]
        try:
            proc = subprocess.Popen(
                command, cwd="/scratch", env=env,
                stdin=slave if tty else subprocess.DEVNULL,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                preexec_fn=session)
            try:
                stdout, stderr = proc.communicate(timeout=deadline)
                status = proc.returncode
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                stdout, stderr = proc.communicate(timeout=5)
                status = "timeout"
            row = {"name": name, "pty": tty, "argv": command,
                   "status": status, "deadline_seconds": deadline, "stdout": stdout.decode(errors="replace"),
                   "stderr": stderr.decode(errors="replace")}
            if tty:
                after = termios.tcgetattr(slave)
                size_after = fcntl.ioctl(slave, termios.TIOCGWINSZ, bytes(8))
                row.update(termios_before=repr(before), termios_after=repr(after),
                           size_before=size_before.hex(),
                           size_after=size_after.hex(),
                           restored=before == after and size_before == size_after)
            results.append(row)
        finally:
            if slave is not None:
                os.close(slave)
            if master is not None:
                os.close(master)

    limits = subprocess.run(
        [str(source / "src/getlimits")], env=env, cwd="/scratch",
        capture_output=True, timeout=15)
    if (limits.returncode != 0
            or b"ULONG_OFLOW=18446744073709551616" not in limits.stdout):
        raise RuntimeError("wrong or unavailable target numeric limits")
    locale = subprocess.run(
        ["/usr/bin/locale", "charmap"], env=dict(env, LC_ALL="en_US.ISO-8859-1"),
        cwd="/scratch", capture_output=True, timeout=5)
    run("tr/tr-case-class.sh")
    run("stty/stty-row-col.sh", tty=True)
    run("stty/stty-row-col.sh")
    run("stty/stty-invalid.sh", tty=True)
    passed = (results[0]["status"] == 0 and results[1]["status"] == 0
              and results[1]["restored"]
              and [line for line in results[1]["stdout"].splitlines()
                   if line.startswith("test ")]
              == [f"test {i}... ok" for i in range(1, 12)]
              and results[2]["status"] == 77
              and "requires controlling input terminal" in results[2]["stderr"]
              and results[3]["status"] == 0 and results[3]["restored"]
              and results[3]["stderr"].count("+ returns_ 1 stty ispeed ") == 12
              and "+ returns_ 1 stty eol -F /dev/tty" in results[3]["stderr"]
              and "+ returns_ 1 stty -F /dev/tty eol" in results[3]["stderr"]
              and "+ returns_ 1 stty -F/dev/tty eol" in results[3]["stderr"]
              and "+ returns_ 1 stty eol -F/dev/tty eol" in results[3]["stderr"])
    if extended:
        run("stty/stty.sh", tty=True)
        run("stty/stty-pairs.sh", tty=True, deadline=240)
        passed = (passed and results[4]["status"] == 0
                  and results[4]["restored"] and results[5]["status"] == 0
                  and results[5]["restored"]
                  and results[5]["stderr"].count("+ stty ") > 100)
    scratch_empty = not list(Path("/scratch").iterdir())
    passed = passed and scratch_empty
    report = {"scratch_empty": scratch_empty,"scope": "Linux reference; private controlling PTY only",
              "python": sys.version, "kernel": platform.uname()._asdict(),
              "qemu_sha256": hashlib.sha256(
                  Path("/usr/bin/qemu-x86_64").read_bytes()).hexdigest(),
              "getlimits": {"status": limits.returncode,
                            "stdout": limits.stdout.decode(),
                            "stderr": limits.stderr.decode()},
              "iso_locale": {"status": locale.returncode,
                             "stdout": locale.stdout.decode(),
                             "stderr": locale.stderr.decode()},
              "results": results, "pass": passed}
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
