# SPDX-License-Identifier: BSD-2-Clause
"""Retain compact diagnostics only from a completed suite's owned output root."""
import hashlib
import json
from pathlib import Path

from deps import ROOT

PREFIXES = ('regression-', 'memory-suite-', 'thread-suite-', 'native-image-',
            'block-', 'entropy-', 'console-', 'pipeline-capacity-',
            'command-runner-suite-', 'file-io-suite-', 'inherited-launch-suite-',
            'shared-files-suite-', 'connections-suite-', 'program-suite-',
            'coexist-suite-', 'process-suite-', 'lookup-suite-', 'init-composed-suite-',
            'init-large-suite-', 'init-suite-', 'writable-files-suite-', 'files-suite-',
            'channel-suite-', 'launch-suite-')
LOG_LIMIT = 1024 * 1024


def compact_run(output, report):
    output = Path(output).absolute()
    if (output.is_symlink() or output.parent != ROOT / 'zig-out'
            or output.parent.resolve() != ROOT / 'zig-out'
            or not output.name.startswith(PREFIXES) or not (output / 'results.json').is_file()
            or (output / 'results.json').is_symlink()):
        raise ValueError('cleanup requires a completed owned suite directory')
    removed = 0
    removed_bytes = 0
    shortened = {}
    paths = sorted(output.rglob('*'))
    for path in paths:
        if path.is_symlink():
            path.unlink()
            removed += 1
        elif path.is_file():
            size = path.stat().st_size
            if path == output / 'results.json':
                continue
            if path.suffix in ('.json', '.log') and size <= LOG_LIMIT:
                continue
            if path.suffix == '.log':
                with path.open('rb') as stream:
                    digest = hashlib.file_digest(stream, 'sha256').hexdigest()
                    stream.seek(max(0, size - LOG_LIMIT + 256))
                    tail = stream.read()
                path.write_bytes(f'[trimmed; original bytes={size} sha256={digest}]\n'.encode() + tail)
                shortened[str(path.relative_to(output))] = {'bytes': size, 'sha256': digest}
            else:
                path.unlink()
                removed += 1
                removed_bytes += size
    for path in reversed(paths):
        if path.is_dir() and not path.is_symlink():
            try:
                path.rmdir()
            except OSError:
                pass  # Nonempty retained diagnostics stay in place.
    report['artifact_retention'] = {'mode': 'compact', 'removed_files': removed,
                                    'removed_bytes': removed_bytes, 'shortened_logs': shortened}
    (output / 'results.json').write_text(json.dumps(report, indent=2) + '\n')
