#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Exercise CLI read-only views against the state fixture's actual records."""
import hashlib
import os
from pathlib import Path
import stat
import subprocess
import sys

REPO = Path(__file__).resolve().parents[1]


def snapshot(root):
    result = {}
    for path in sorted(root.rglob('*')):
        info = path.lstat()
        assert stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode), path
        result[str(path.relative_to(root))] = (
            stat.S_IFMT(info.st_mode), stat.S_IMODE(info.st_mode),
            hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None)
    return result


def main():
    root = Path(sys.argv[1]).resolve()
    # Only the existing disposable package-state fixture owns this root.
    assert root.parent.name.startswith('.pkg-mgr-state-test.') and root.name == 'private root'
    assert (root / 'state/packages/app.tsv').is_file()
    initial = snapshot(root)
    cases = 0

    def compare(arguments, status):
        nonlocal cases
        before = snapshot(root)
        helper = subprocess.run(['sh', str(REPO / 'mk/state.sh'), arguments[0],
                                 str(root), *arguments[1:]], capture_output=True, timeout=5)
        assert snapshot(root) == before, arguments
        cli = subprocess.run([str(REPO / 'bin/pkg-mgr'), '--root', str(root),
                              '--format', 'tsv', *arguments], capture_output=True, timeout=5)
        assert helper.returncode == cli.returncode == status, (arguments, helper, cli)
        assert (cli.stdout, cli.stderr) == (helper.stdout, helper.stderr), arguments
        assert snapshot(root) == before, arguments
        cases += 1
        return cli

    for arguments in (['list'], ['owners'], ['verify'], ['orphans'],
                      ['files', 'base'], ['deps', 'app'], ['rdeps', 'base']):
        result = compare(arguments, 0)
        assert result.stderr == b'', arguments
        if arguments == ['list']:
            assert result.stdout == b'app\t0.1\texplicit\nbase\t0.1\tdependency\nspare\t0.1\tdependency\n'
        elif arguments == ['deps', 'app']:
            assert result.stdout == b'base\n'
        elif arguments == ['rdeps', 'base']:
            assert result.stdout == b'app\n'
        elif arguments == ['orphans']:
            assert result.stdout == b'report\torphan-plan-v1\tnon-deleting\norphan\tspare\n'
        elif arguments == ['files', 'base']:
            assert b'usr/local/share/base/file with spaces.txt\t' in result.stdout
    missing = compare(['files', 'missing'], 1)
    assert missing.stdout == b'' and missing.stderr == b'state-unknown-package: missing\n'
    payload = root / 'stage/app/usr/local/share/app/payload.txt'
    mode = stat.S_IMODE(payload.stat().st_mode)
    try:
        os.chmod(payload, 0o755 if mode != 0o755 else 0o644)
        drift = compare(['verify'], 1)
        assert drift.stdout == b'mode-mismatch\tapp\tusr/local/share/app/payload.txt\n'
        assert drift.stderr == b''
    finally:
        os.chmod(payload, mode)
    assert snapshot(root) == initial
    print(f'CLI populated state: {cases} real-helper views/failures preserved records and payloads')


if __name__ == '__main__':
    main()
