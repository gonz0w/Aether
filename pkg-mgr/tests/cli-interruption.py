#!/usr/bin/env python3
"""Development-only signal driver; CLI and controlled helper remain POSIX sh."""
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import time

REPO = Path(__file__).resolve().parent.parent
HELPER = r'''#!/bin/sh
set -eu
root=$2
stop() { printf 'helper interrupted\n' >&2; exit "$1"; }
trap 'stop 130' INT
trap 'stop 129' HUP
trap 'stop 143' TERM
printf 'prepared\tfixture\tfixture-intent-pin\n'
printf 'fixture diagnostic\n' >&2
printf 'pending\n' > "$root/pending"
printf '%s\n' "$$" > "$root/ready"
read -r release < "$root/gate"
printf 'continued\n' > "$root/continued"
'''


def run_case(base, mode, sig, group):
    root = base / f'{mode}-{sig.name}-{group}'
    root.mkdir()
    os.mkfifo(root / 'gate')
    # Keep both ends open so test cleanup cannot deadlock on a dead helper.
    gate = os.open(root / 'gate', os.O_RDWR | os.O_NONBLOCK)
    env = dict(os.environ, TMPDIR=str(root), TERM='dumb')
    p = subprocess.Popen([str(base / 'bin/pkg-mgr'), '--root', str(root),
                          '--format', mode, '--quiet', 'prepare',
                          '/fixture', 'pin', 'target', 'old-pin'],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         env=env, start_new_session=True)
    try:
        deadline = time.monotonic() + 10
        while not (root / 'ready').exists():
            assert p.poll() is None, 'wrapper exited before helper readiness'
            assert time.monotonic() < deadline, 'helper readiness timeout'
            time.sleep(.01)
        if group:
            os.killpg(p.pid, sig)
        else:
            os.kill(p.pid, sig)
        # Release the read after either signal scope. Some host shells defer
        # a trapped signal until a blocking FIFO read can complete; do not make
        # prompt interruption of that syscall a test precondition.
        os.write(gate, b'continue\n')
        out, err = p.communicate(timeout=10)
        assert p.returncode == 128 + sig, (sig, group, p.returncode, err)
        assert b'[UNKNOWN]' in err and b'[OK]' not in err, err
        assert b'fixture diagnostic' in err, err
        assert b'fixture-intent-pin' in out, (mode, sig, group, out, err)
        assert b'\x1b' not in out + err
        assert (root / 'pending').read_text() == 'pending\n'
        assert (root / 'continued').exists() != group
        if mode == 'tsv':
            assert out == b'prepared\tfixture\tfixture-intent-pin\n', out
        else:
            assert b'Replacement is pending' in out, out
        assert not list(root.glob('pkg-mgr-cli.*')), 'wrapper scratch leaked'
        if group:
            assert b'helper interrupted' in err, err
    finally:
        # Only this test's new process group; never signal the runner's group.
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        p.communicate(timeout=10)
        os.close(gate)


with tempfile.TemporaryDirectory(prefix='pkg-cli-signals-') as temporary:
    base = Path(temporary)
    (base / 'bin').mkdir()
    (base / 'mk').mkdir()
    shutil.copy2(REPO / 'bin/pkg-mgr', base / 'bin/pkg-mgr')
    shutil.copy2(REPO / 'mk/cli-render.awk', base / 'mk/cli-render.awk')
    (base / 'mk/replacement.sh').write_text(HELPER)
    for mode in ('human', 'tsv'):
        for sig in (signal.SIGINT, signal.SIGHUP, signal.SIGTERM):
            for group in (False, True):
                run_case(base, mode, sig, group)
print('CLI interruption: 12 wrapper/group signal cases preserve receipts, diagnostics and pending state')
