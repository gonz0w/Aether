# SPDX-License-Identifier: BSD-2-Clause
"""Owned, recorded subprocesses for local experiments; Python 3.10+."""
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import time


def clean_env(work):
    return {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "TMPDIR": str(work)}


def identity(path):
    resolved = Path(path).resolve(strict=True)
    return {"path": str(path), "resolved_path": str(resolved),
            "sha256": hashlib.sha256(resolved.read_bytes()).hexdigest()}


def alive(group):
    try:
        os.killpg(group, 0)
        return True
    except ProcessLookupError:
        return False


def run(argv, *, cwd, env, work, label, timeout, input=None, file_limit=16 * 1024**2):
    """Return bytes and metadata; callers must require record['complete']."""
    work = Path(work)
    record = {"argv": list(argv), "cwd": str(cwd), "environment": dict(env),
              "timeout_seconds": timeout, "exit": None, "complete": False,
              "cleanup": "not-started", "failure": None, "file_limit_bytes": file_limit}
    receipt = work / (label + ".process.json")

    def save():
        receipt.write_text(json.dumps(record, indent=2) + "\n")

    def limits():
        resource.setrlimit(resource.RLIMIT_FSIZE, (file_limit, file_limit))

    save()
    proc = None
    stdout_path = work / (label + ".stdout")
    stderr_path = work / (label + ".stderr")
    stdin_path = work / (label + ".stdin")
    stdin_path.write_bytes(input if input is not None else b"")
    try:
        if not Path(argv[0]).is_absolute():
            raise ValueError("executable must be absolute")
        record["tool"] = identity(argv[0])
        save()
        with stdin_path.open("rb") as stdin, stdout_path.open("wb") as stdout:
            with stderr_path.open("wb") as stderr:
                proc = subprocess.Popen(
                    argv, cwd=cwd, env=env, stdin=stdin, stdout=stdout,
                    stderr=stderr, start_new_session=True, preexec_fn=limits)
                record["process_group"] = proc.pid
                save()
                try:
                    record["exit"] = proc.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    record["failure"] = "timeout"
                finally:
                    remaining = alive(proc.pid)
                    if remaining:
                        if record["failure"] is None:
                            record["failure"] = "descendant-after-exit"
                        try:
                            os.killpg(proc.pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                    try:
                        record["exit"] = proc.wait(timeout=5)
                        deadline = time.monotonic() + 5
                        while alive(proc.pid) and time.monotonic() < deadline:
                            time.sleep(0.01)
                        record["cleanup"] = ("unresolved" if alive(proc.pid)
                                             else "complete")
                    except subprocess.TimeoutExpired:
                        record["cleanup"] = "unresolved"
    except (OSError, ValueError) as error:
        record["failure"] = type(error).__name__ + ": " + str(error)
    finally:
        record["complete"] = (proc is not None and record["failure"] is None
                              and record["cleanup"] == "complete")
        save()
    result = subprocess.CompletedProcess(
        argv, record["exit"],
        stdout_path.read_bytes() if stdout_path.exists() else b"",
        stderr_path.read_bytes() if stderr_path.exists() else b"")
    result.record = record
    return result
