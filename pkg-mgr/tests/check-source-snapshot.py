#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Assemble and round-trip a local development source snapshot, never publish it."""
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import stat
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
FILES = ('README.md', 'AGENTS.md', 'CONTRIBUTING.md', 'SECURITY.md',
         'LICENSE', '.gitignore',
         '.planning/PROJECT.md', '.planning/ROADMAP.md', '.planning/STATE.md')
TREES = ('bin', 'mk', 'recipes', 'fixtures', 'manifests', 'tests', 'man', 'docs', '.githooks')
SKIP = {'__pycache__', '.DS_Store'}


def inventory(root):
    names = list(FILES)
    for tree in TREES:
        if not (root / tree).is_dir() or (root / tree).is_symlink():
            raise ValueError('missing or linked source tree: ' + tree)
        for directory, dirs, files in os.walk(root / tree, followlinks=False):
            dirs[:] = sorted(d for d in dirs if d not in SKIP)
            for name in dirs:
                if (Path(directory) / name).is_symlink():
                    raise ValueError('source directory link: ' + name)
            names.extend(str((Path(directory) / f).relative_to(root))
                         for f in files if f not in SKIP and not f.endswith('.pyc'))
    result = {}
    for name in sorted(names):
        path = root / name
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValueError('source must be an unlinked regular file: ' + name)
        mode = stat.S_IMODE(info.st_mode)
        if mode & 0o7000:
            raise ValueError('special source mode: ' + name)
        data = path.read_bytes()
        result[name] = {'sha256': hashlib.sha256(data).hexdigest(),
                        'size': len(data), 'mode': f'{mode:04o}'}
    return result


def assemble(root, output, records):
    # Fixed tar metadata; source file permissions remain explicit inputs.
    with tarfile.open(output, 'x', format=tarfile.PAX_FORMAT) as archive:
        for name, record in records.items():
            data = (root / name).read_bytes()
            if hashlib.sha256(data).hexdigest() != record['sha256']:
                raise ValueError('source changed while assembling: ' + name)
            info = tarfile.TarInfo('pkg-mgr/' + name)
            info.size = len(data)
            info.mode = int(record['mode'], 8)
            archive.addfile(info, io.BytesIO(data))
        data = (json.dumps(records, indent=2, sort_keys=True) + '\n').encode()
        info = tarfile.TarInfo('pkg-mgr/SOURCE-MANIFEST.json')
        info.size = len(data)
        info.mode = 0o644
        archive.addfile(info, io.BytesIO(data))


def verify(root, records):
    observed = {}
    for directory, dirs, files in os.walk(root, followlinks=False):
        for name in dirs:
            if (Path(directory) / name).is_symlink():
                raise ValueError('extracted directory link')
        for name in files:
            path = Path(directory) / name
            relative = str(path.relative_to(root))
            info = path.lstat()
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise ValueError('extracted special/link file')
            if relative == 'SOURCE-MANIFEST.json':
                if json.loads(path.read_text()) != records:
                    raise ValueError('embedded manifest mismatch')
                continue
            data = path.read_bytes()
            observed[relative] = {'sha256': hashlib.sha256(data).hexdigest(),
                                  'size': len(data),
                                  'mode': f'{stat.S_IMODE(info.st_mode):04o}'}
    if observed != records or not (root / 'SOURCE-MANIFEST.json').is_file():
        raise ValueError('extracted inventory/bytes/modes mismatch')


def main():
    output = Path(tempfile.mkdtemp(prefix='pkg-source-snapshot-')).resolve()
    print(f'retained_root={output}', flush=True)
    records = inventory(ROOT)
    (output / 'input-files.json').write_text(json.dumps(records, indent=2) + '\n')
    for name in ('source.tar', 'repeat.tar'):
        assemble(ROOT, output / name, records)
    digest = hashlib.sha256((output / 'source.tar').read_bytes()).hexdigest()
    if hashlib.sha256((output / 'repeat.tar').read_bytes()).hexdigest() != digest:
        raise ValueError('repeated source archive bytes differ')
    extracted = output / 'extracted'
    extracted.mkdir()
    # Only our just-created archive is consumed; never extract arbitrary downloads.
    subprocess.run(['tar', '-xpf', str(output / 'source.tar'), '-C', str(extracted)],
                   check=True, timeout=60)
    verify(extracted / 'pkg-mgr', records)
    if inventory(ROOT) != records:
        raise ValueError('source changed during snapshot check')
    (output / 'result.json').write_text(json.dumps({
        'status': 'pass', 'scope': 'local development snapshot; not a release approval',
        'source_root': str(ROOT), 'platform': platform.platform(),
        'python': platform.python_version(), 'files': len(records),
        'archive_sha256': digest, 'repeat_archive_sha256': digest,
        'extracted_root': str(extracted / 'pkg-mgr'),
        'excluded': ['.git', '.jj', '.pkg-mgr-live-*', 'work', 'stage', 'logs',
                     'distfiles', '__pycache__', '.DS_Store', '*.pyc'],
        'included_history': 'docs/archive and docs/evidence retained as reference, unqualified for publication',
    }, indent=2) + '\n')
    print(f'PASS: {len(records)} source files; identical repeated tar bytes and exact extracted bytes/modes')
    print('NOT RUN: independent review, publication licensing and release approval')


if __name__ == '__main__':
    main()
