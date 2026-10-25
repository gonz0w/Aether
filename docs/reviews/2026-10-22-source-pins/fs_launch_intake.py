# SPDX-License-Identifier: BSD-2-Clause
"""Read-only intake of the reviewed local launch candidate; never starts a guest."""
import hashlib
import json
from pathlib import Path
import re

# Completed reviewed local dependency, never a mutable sibling selection.
SEAL = 'b69fd748b4d4fda334126dba96744a73f2a4b03649d5e9b1033ae253d52cc558'


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def intake(directory, expected=SEAL):
    root = Path(directory).absolute()
    if root.resolve() != root or root.is_symlink() or not root.is_dir():
        raise ValueError('launch intake requires a real directory')
    manifest = root/'SHA256SUMS'
    if not re.fullmatch('[0-9a-f]{64}', expected) or manifest.is_symlink() or digest(manifest) != expected:
        raise ValueError('launch manifest identity')
    members = {}
    for line in manifest.read_text().splitlines():
        checksum, name = line.split(maxsplit=1)
        path = Path(name)
        if (not re.fullmatch('[0-9a-f]{64}', checksum) or not path.parts or path.is_absolute()
                or '..' in path.parts or str(path) != name or name in members or name == 'SHA256SUMS'):
            raise ValueError('launch member path')
        member = root/path
        if member.resolve() != member or not member.is_file() or digest(member) != checksum:
            raise ValueError('launch member identity: '+name)
        members[name] = checksum
    actual = set()
    for path in root.rglob('*'):
        if path.is_symlink():
            raise ValueError('launch symlink')
        if path.is_file():
            actual.add(str(path.relative_to(root)))
    if actual != members.keys() | {'SHA256SUMS'}:
        raise ValueError('launch member closure')
    required = {'build.json','filesystem.elf','SOURCE.md','preparation.json',
                'notices/openzfs/LICENSE','notices/openzfs/COPYRIGHT','notices/openzfs/NOTICE',
                'notices/COPYRIGHT.musl','notices/LICENSE'}
    if not required <= members.keys():
        raise ValueError('launch required closure')
    record = json.loads((root/'build.json').read_text())
    if (record.get('schema') != 'aether-fs-launch-build-v1' or record.get('status') != 'pass'
            or record.get('executed') is not False or not record.get('origins')
            or record.get('elf_sha256') != members['filesystem.elf']
            or record.get('elf_bytes') != (root/'filesystem.elf').stat().st_size
            or not record.get('structural_loader','').startswith('ELF structural pages=')):
        raise ValueError('launch build identity/coverage')
    for name, checksum in record['inputs'].items():
        path = Path(name)
        # The sealed producer includes pinned Homebrew tool aliases. Their
        # content identity is authoritative; delivery members stay nonsymlinks.
        if not path.is_absolute() or not path.is_file() or digest(path) != checksum:
            raise ValueError('launch consumed source/input drift: '+name)
    for tool in record['tools'].values():
        if digest(Path(tool['resolved_path'])) != tool['sha256']:
            raise ValueError('launch tool drift')
    return dict(manifest_sha256=expected, elf=str(root/'filesystem.elf'),
                elf_sha256=members['filesystem.elf'], members=len(members),
                executed=False, native_acceptance=False,
                scope='Exact linked integration candidate; sys-init/kernel composition still required')
