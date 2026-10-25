#!/usr/bin/env python3
"""Bounded, host-only output failure tests against the real copied CLI."""
import os
from pathlib import Path
import select
import shutil
import signal
import subprocess
import tempfile

REPO = Path(__file__).resolve().parent.parent
RECEIPT = b'prepared\tfixture\tfixture-intent-pin\n'
HELPER = r'''#!/bin/sh
printf 'pending\n' > "$2/pending"
printf 'prepared\tfixture\tfixture-intent-pin\n'
if test "${LARGE:-no}" = yes; then
    awk 'BEGIN {for(i=0;i<20000;i++) print "payload-row-abcdefghijklmnopqrstuvwxyz0123456789"}'
fi
printf 'fixture diagnostic\n' >&2
exit "${HELPER_EXIT:-0}"
'''

with tempfile.TemporaryDirectory(prefix='pkg-cli-output-') as temporary:
    base = Path(temporary)
    (base / 'bin').mkdir()
    (base / 'mk').mkdir()
    shutil.copy2(REPO / 'bin/pkg-mgr', base / 'bin/pkg-mgr')
    shutil.copy2(REPO / 'mk/cli-render.awk', base / 'mk/cli-render.awk')
    (base / 'mk/replacement.sh').write_text(HELPER)
    count = 0
    for mode in ('human', 'tsv'):
        for failure in ('stdout', 'stderr', 'both', 'SIGINT', 'SIGHUP', 'SIGTERM'):
            for helper_code in ((0,) if failure.startswith('SIG') else (0, 2)):
                root = base / f'{mode}-{failure}-{helper_code}'
                root.mkdir()
                closed_read, closed_write = os.pipe()
                os.close(closed_read)
                p = subprocess.Popen(
                    [str(base / 'bin/pkg-mgr'), '--root', str(root), '--format', mode,
                     '--quiet', 'prepare', '/fixture', 'pin', 'target', 'old-pin'],
                    stdout=closed_write if failure in ('stdout', 'both') else subprocess.PIPE,
                    stderr=closed_write if failure in ('stderr', 'both') else subprocess.PIPE,
                    env=dict(os.environ, TMPDIR=str(root), TERM='dumb',
                             HELPER_EXIT=str(helper_code), LARGE='yes' if failure.startswith('SIG') else 'no'),
                    start_new_session=True)
                os.close(closed_write)
                try:
                    if failure.startswith('SIG'):
                        # A readable byte proves the renderer/cat has started. The
                        # large result exceeds pipe capacity so it cannot finish.
                        assert select.select([p.stdout], [], [], 10)[0], 'output timeout'
                        assert os.read(p.stdout.fileno(), 1), 'no rendered output'
                        os.killpg(p.pid, getattr(signal, failure))
                    out, err = p.communicate(timeout=10)
                    assert p.returncode == (128 + getattr(signal, failure) if failure.startswith('SIG') else 1), (mode, failure, p.returncode, err)
                    kept = list(root.glob('pkg-mgr-cli.*'))
                    assert len(kept) == 1, (mode, failure, 'missing retained output', err)
                    receipt = kept[0]
                    assert receipt.stat().st_mode & 0o777 == 0o700
                    expected = RECEIPT + (b'payload-row-abcdefghijklmnopqrstuvwxyz0123456789\n' * 20000 if failure.startswith('SIG') else b'')
                    assert (receipt / 'out').read_bytes() == expected
                    assert (receipt / 'err').read_bytes() == b'fixture diagnostic\n'
                    assert (receipt / 'helper-exit').read_text() == f'{helper_code}\n'
                    assert (root / 'pending').read_text() == 'pending\n'
                    if err is not None:
                        assert b'[OK]' not in err
                        assert b'Retained helper output' in err, err
                        assert str(receipt).encode() in err, err
                    count += 1
                finally:
                    try:
                        os.killpg(p.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    p.communicate(timeout=10)
    print(f'CLI output: {count} closed-stream/render-interruption cases retain private receipts and helper exit status')
