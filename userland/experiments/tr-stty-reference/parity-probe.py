#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Isolate cmspar behavior on owned Linux PTYs; Python 3.10+."""
import json
import os
from pathlib import Path
import pty
import subprocess
import sys
import termios

rows = []
for name, prefix in [("candidate", ["/usr/bin/qemu-x86_64", sys.argv[1]]),
                     ("image-helper", ["/usr/bin/stty"])]:
    for options in [["cmspar"], ["-cmspar"], ["parodd", "cmspar"]]:
        master, slave = pty.openpty()
        try:
            before = termios.tcgetattr(slave)
            result = subprocess.run(prefix + options, stdin=slave,
                                    capture_output=True, timeout=10,
                                    cwd="/scratch", env=dict(os.environ, LC_ALL="C"))
            after = termios.tcgetattr(slave)
            rows.append({"provider": name, "argv": prefix + options,
                         "status": result.returncode,
                         "stdout": result.stdout.decode(),
                         "stderr": result.stderr.decode(),
                         "before": repr(before), "after": repr(after)})
        finally:
            os.close(slave)
            os.close(master)
print(json.dumps(rows, indent=2))
