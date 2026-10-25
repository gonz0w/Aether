#!/usr/bin/env python3
"""Exercise lost CLI output against the binary fixture's actual transactions."""
import hashlib
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parent.parent
source, bundle = map(Path, sys.argv[1:3])
bundle_pin, old_pin = sys.argv[3:5]
CLI = str(REPO / 'bin/pkg-mgr')


def invoke(argv, **kwargs):
    process = subprocess.Popen(argv, start_new_session=True, **kwargs)
    try:
        stdout, stderr = process.communicate(timeout=30)
        return subprocess.CompletedProcess(argv, process.returncode, stdout, stderr)
    finally:
        # Timeout must not leave a real helper mutating its disposable root.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.communicate(timeout=10)


def run(root, *args, code=0):
    result = invoke([CLI, '--root', str(root), '--format', 'tsv', *args],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert result.returncode == code, (args, result.returncode, result.stderr)
    return result


def lose_output(root, receipts, mode, *args):
    before = set(receipts.iterdir())
    read_fd, write_fd = os.pipe()
    os.close(read_fd)
    try:
        result = invoke(
            [CLI, '--root', str(root), '--format', mode, '--quiet', *args],
            stdout=write_fd, stderr=write_fd if mode == 'tsv' else subprocess.PIPE,
            env=dict(os.environ, TMPDIR=str(receipts), TERM='dumb'))
    finally:
        os.close(write_fd)
    assert result.returncode == 1, (args, result.returncode, result.stderr)
    added = set(receipts.iterdir()) - before
    assert len(added) == 1, added
    receipt = added.pop()
    assert receipt.stat().st_mode & 0o777 == 0o700
    assert (receipt / 'helper-exit').read_bytes() == b'0\n'
    if mode == 'human':
        assert b'Retained helper output' in result.stderr
        assert str(receipt).encode() in result.stderr
        assert b'[OK]' not in result.stderr
    return receipt


with tempfile.TemporaryDirectory(prefix='cli-receipt-', dir=source.parent) as temporary:
    base = Path(temporary)
    for mode in ('human', 'tsv'):
        root = base / mode
        shutil.copytree(source, root, copy_function=shutil.copy2)
        receipts = base / (mode + '-receipts')
        receipts.mkdir(mode=0o700)
        old_record = (root / 'state/packages/app.tsv').read_bytes()
        old_payload = (root / 'stage/app/obsolete').read_bytes()
        world = (root / 'state/world').read_bytes()
        unrelated = (root / 'state/packages/base.tsv').read_bytes()
        assert hashlib.sha256(old_record).hexdigest() == old_pin
        prepared = lose_output(root, receipts, mode, 'prepare', str(bundle),
                               bundle_pin, 'test-host-v1', old_pin)
        fields = (prepared / 'out').read_text().strip().split('\t')
        assert fields[:2] == ['prepared', 'app'] and len(fields) == 3
        intent = fields[2]
        assert hashlib.sha256((root / '.replacement/intent.kv').read_bytes()).hexdigest() == intent
        assert b'replacement pending' in run(root, 'verify', code=1).stderr
        assert (root / 'state/packages/app.tsv').read_bytes() == old_record
        assert (root / 'stage/app/obsolete').read_bytes() == old_payload
        # A modified retained receipt grants no authority. Its wrong digest must
        # fail normal finish validation without consuming the pending transaction.
        bad_pin = ('0' if intent[0] != '0' else '1') + intent[1:]
        (prepared / 'out').write_text(f'prepared\tapp\t{bad_pin}\n')
        run(root, 'finish', bad_pin, code=1)
        assert (root / '.replacement').is_dir()
        assert (root / 'state/packages/app.tsv').read_bytes() == old_record
        assert (root / 'stage/app/obsolete').read_bytes() == old_payload
        (prepared / 'out').write_text(f'prepared\tapp\t{intent}\n')
        finished = lose_output(root, receipts, mode, 'finish', intent)
        assert (finished / 'out').read_text() == f'completed\tapp\t{intent}\n'
        assert not (root / '.replacement').exists()
        # Output delivery failed after publication. Retry validates completed
        # history, preserving new authority and the retained old payload.
        assert run(root, 'finish', intent).stdout == (finished / 'out').read_bytes()
        run(root, 'verify')
        assert (root / 'state/packages/app.tsv').read_bytes() == (bundle / 'package.tsv').read_bytes()
        assert (root / 'state/world').read_bytes() == world
        assert (root / 'state/packages/base.tsv').read_bytes() == unrelated
        history = root / 'replacements' / intent
        assert (history / 'old-record').read_bytes() == old_record
        assert (history / 'previous/obsolete').read_bytes() == old_payload
        assert not (root / 'stage/app/obsolete').exists()
        assert (root / 'stage/app/new.conf').is_file()
        assert len(list(receipts.iterdir())) == 2
        print(f'Actual CLI receipt recovery: {mode}, prepare/finish delivery failure, forged pin rejected, repeat finish and retained payload passed')
