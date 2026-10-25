# SPDX-License-Identifier: BSD-2-Clause
"""Owned reference-check execution on POSIX hosts; Python 3.10+."""

from pathlib import Path
import runpy
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]


def run_checked(argv, timeout):
    """Run trusted local code, retain receipts and replay separate byte streams.

    The existing helper owns the child session and its non-detached descendants.
    No outer subprocess owner may kill this function while its group is live.
    This is not containment of hostile session escape or owner SIGKILL.
    """
    helper = runpy.run_path(str(
        ROOT / "experiments/command-runner/process.py"
    ))
    build = ROOT / "build"
    build.mkdir(exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="quality-process-", dir=build))
    result = helper["run"](
        argv, cwd=ROOT, env=helper["clean_env"](work), work=work,
        label="check", timeout=timeout,
    )
    # Retained bytes/receipt survive even a broken consumer output pipe.
    sys.stdout.buffer.write(result.stdout)
    sys.stdout.buffer.flush()
    sys.stderr.buffer.write(result.stderr)
    sys.stderr.buffer.flush()
    if not result.record["complete"] or result.returncode != 0:
        raise ValueError(f"reference check failed; retained evidence: {work}")
    return work
