# SPDX-License-Identifier: BSD-2-Clause
"""Owned host helper compilation for dash tests; Python 3.10+."""
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[2]
PROCESS = runpy.run_path(str(ROOT / 'experiments/command-runner/process.py'))


def compile_helper(argv, work, *, timeout=45, file_limit=16 * 1024**2):
    """Run a verified compiler wrapper in a trusted private output directory.

    Callers must verify wrapper/tool/SDK inputs first. This function owns only
    the local non-detached session; it must not run a remote container launcher.
    """
    work = Path(work).resolve()
    result = PROCESS['run'](
        argv, cwd=work, env=PROCESS['clean_env'](work), work=work,
        label='helper-build', timeout=timeout, file_limit=file_limit,
    )
    # Preserve the original dash test log name and separate raw byte streams.
    (work / 'helper-build.trace').write_bytes(result.stderr)
    if not result.record['complete'] or result.returncode != 0:
        raise RuntimeError(f'helper-build failed; retained evidence: {work}')
    return result
