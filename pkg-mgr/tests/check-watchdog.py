#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Development-only whole-suite deadline with an owned process group and logs."""
import os
from pathlib import Path
import signal
import shutil
import subprocess
import sys
import tempfile
import time


class Interrupted(Exception):
    def __init__(self, number):
        self.number = number


def interrupt(number, _frame):
    raise Interrupted(number)


def run(command, root, seconds):
    """Return child status, 124 for deadline, or 125 for leaked descendants.

    Children must remain in the new session. This is a cooperative test watchdog,
    not confinement against a child deliberately escaping its process group.
    """
    environment = dict(os.environ, TMPDIR=str(root))
    with (root / 'suite.log').open('wb') as log:
        child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                                 env=environment, start_new_session=True)
        expired = False
        status = 125
        previous = {sig: signal.signal(sig, interrupt)
                    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)}
        try:
            status = child.wait(timeout=seconds)
        except subprocess.TimeoutExpired:
            expired = True
            status = 124
        except Interrupted as error:
            status = 128 + error.number
        finally:
            for sig in previous:
                signal.signal(sig, signal.SIG_IGN)
            # Always clean our group, even if its leader exited first.
            try:
                os.killpg(child.pid, signal.SIGTERM)
                if status == 0:
                    status = 125
            except ProcessLookupError:
                pass
            try:
                child.wait(timeout=2)
            except subprocess.TimeoutExpired:
                pass
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            child.wait(timeout=2)
            for sig, handler in previous.items():
                signal.signal(sig, handler)
    return status


def qualify(status, log):
    """A zero status without the internal runner's completion is incomplete."""
    if status != 0:
        return status
    required = {
        'All sixteen active fixture tests passed.',
        'All three pinned standards checks passed (not runtime conformance).',
    }
    with log.open(errors='replace') as source:
        for line in source:
            required.discard(line.rstrip('\n'))
    return 125 if required else 0


def main():
    repo = Path(__file__).resolve().parents[1]
    root = Path(tempfile.mkdtemp(prefix='pkg-mgr-suite-')).resolve()
    print(f'check-run: retained_root={root}', flush=True)
    started = time.monotonic()
    try:
        status = run(['sh', str(repo / 'tests/check-fixtures.sh')], root, 600)
    except (OSError, subprocess.SubprocessError) as error:
        print(f'check-run: infra-error: {error}', file=sys.stderr)
        status = 125
    status = qualify(status, root / 'suite.log')
    label = 'pass' if status == 0 else ('timeout' if status == 124 else 'fail')
    (root / 'result.txt').write_text(
        f'result={label}\nexit={status}\nelapsed={time.monotonic()-started:.3f}\n'
        'deadline_seconds=600\n')
    with (root / 'suite.log').open(errors='replace') as log:
        shutil.copyfileobj(log, sys.stdout)
    print(f'check-run: {label}; retained_root={root}', flush=True)
    return status if status >= 0 else 128 - status


if __name__ == '__main__':
    sys.exit(main())
