#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Check CLI routing independently of package helper implementation."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

REPO = Path(__file__).resolve().parents[1]
# Independent public command contract; never derive expected routing from the CLI.
COMMANDS = {
    'list': ('state', []), 'owners': ('state', []),
    'verify': ('state', []), 'orphans': ('state', []),
    'files': ('state', ['sample']), 'deps': ('state', ['sample']),
    'rdeps': ('state', ['sample']), 'export': ('binary', ['sample']),
    'import': ('binary', ["/bundle with 'quotes'", 'bundle-pin', 'target']),
    'recover': ('binary', ["/bundle with 'quotes'", 'bundle-pin', 'target']),
    'preflight': ('binary', ["/bundle with 'quotes'", 'bundle-pin', 'target']),
    'prepare': ('replacement', ["/bundle with 'quotes'", 'bundle-pin', 'target', 'old-pin']),
    'finish': ('replacement', ['intent-pin']),
}
HELPER = r'''#!/bin/sh
set -eu
printf '%s\000' "${0##*/}" "$@" > "$DISPATCH_CALL"
cat "$DISPATCH_OUT"
cat "$DISPATCH_ERR" >&2
exit "$DISPATCH_STATUS"
'''


def main():
    with tempfile.TemporaryDirectory(prefix='pkg-cli-dispatch-') as directory:
        root = Path(directory)
        (root / 'bin').mkdir()
        (root / 'mk').mkdir()
        scratch = root / 'tmp'
        scratch.mkdir()
        shutil.copy2(REPO / 'bin/pkg-mgr', root / 'bin/pkg-mgr')
        for helper in ('state', 'binary', 'replacement'):
            (root / 'mk' / (helper + '.sh')).write_text(HELPER)
        output = b'receipt\tvalue with spaces\nsecond\t\xc3\xa9\r\n'
        diagnostic = b'helper diagnostic\tunchanged\n'
        (root / 'stdout').write_bytes(output)
        (root / 'stderr').write_bytes(diagnostic)
        call = root / 'call'
        private = root / "private 'root'"
        env = dict(os.environ, TMPDIR=str(scratch), TERM='dumb',
                   DISPATCH_CALL=str(call), DISPATCH_OUT=str(root / 'stdout'),
                   DISPATCH_ERR=str(root / 'stderr'))
        base = [str(root / 'bin/pkg-mgr'), '--root', str(private), '--format', 'tsv']
        passed = 0
        for command, (helper, arguments) in COMMANDS.items():
            expected = [helper + '.sh', command, str(private), *arguments]
            for status in (0, 2, 73):
                call.unlink(missing_ok=True)
                result = subprocess.run([*base, command, *arguments],
                                        env=dict(env, DISPATCH_STATUS=str(status)),
                                        capture_output=True, timeout=5)
                assert result.returncode == status, (command, status, result)
                assert result.stdout == output and result.stderr == diagnostic, command
                assert call.read_bytes() == b''.join(x.encode() + b'\0' for x in expected), command
                assert not list(scratch.iterdir()), 'CLI temporary leak'
                passed += 1
            invalid = [arguments + ['unexpected']]
            if arguments:
                invalid.append(arguments[:-1])
            for wrong in invalid:
                call.unlink(missing_ok=True)
                result = subprocess.run([*base, command, *wrong],
                                        env=dict(env, DISPATCH_STATUS='0'),
                                        capture_output=True, timeout=5)
                assert result.returncode == 64 and result.stdout == b'', command
                assert result.stderr == b'[FAILED] Invalid command or options. Run pkg-mgr --help.\n', command
                assert not call.exists() and not list(scratch.iterdir()), command
                passed += 1
        print(f'CLI dispatch: {passed} routing/status/arity cases passed for 13 commands')


if __name__ == '__main__':
    main()
