#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Inspect the pinned image's terminal translation; Python 3.10+."""
import json
import os
from pathlib import Path
import pty
import subprocess
import sys
import termios


def command(argv, stdin=subprocess.DEVNULL):
    result = subprocess.run(argv, stdin=stdin, capture_output=True,
                            timeout=10, cwd="/scratch",
                            env=dict(os.environ, LC_ALL="C"))
    return {"argv": argv, "status": result.returncode,
            "stdout": result.stdout.decode(errors="replace"),
            "stderr": result.stderr.decode(errors="replace")}


metadata = [command(["/usr/bin/qemu-x86_64", "--version"]),
            command(["/usr/bin/dpkg-query", "-W", "qemu-user", "coreutils"]),
            command(["/usr/bin/strace", "-V"])]
rows = []
for name in ["candidate-set", "image-set", "candidate-read-seeded"]:
    master, slave = pty.openpty()
    try:
        before = termios.tcgetattr(slave)
        if name == "candidate-read-seeded":
            seed = command(["/usr/bin/stty", "cmspar"], slave)
            argv = ["/usr/bin/qemu-x86_64", sys.argv[1], "-a"]
        else:
            seed = None
            argv = (["/usr/bin/qemu-x86_64", sys.argv[1]]
                    if name == "candidate-set" else ["/usr/bin/stty"])
            argv += ["cmspar"]
        trace = command(["/usr/bin/strace", "-f", "-v", "-e", "trace=ioctl"]
                        + argv, slave)
        after = termios.tcgetattr(slave)
        termios.tcsetattr(slave, termios.TCSANOW, before)
        restored = termios.tcgetattr(slave) == before
        rows.append({"case": name, "seed": seed, "trace": trace,
                     "before": repr(before), "after": repr(after),
                     "explicit_host_restoration": restored})
    finally:
        os.close(slave)
        os.close(master)
print(json.dumps({"metadata": metadata, "cases": rows}, indent=2))
