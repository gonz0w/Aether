# SPDX-License-Identifier: BSD-2-Clause
"""Experimental component admission, Python 3.10+; no native authority."""
import hashlib
from pathlib import Path

REQUIRED = frozenset({'runtime', 'application', 'memory', 'fork', '_Fork', 'rebind',
                      'waitpid', 'wait3', 'wait4', 'crt1', 'crti', 'crtn', 'libc'})
FS_PROFILE = 'AENFS003/ABI29'
FS_PARENT_REQUIRED = REQUIRED | frozenset('dash-%02d' % i for i in range(32))
FS_HELPER_REQUIRED = frozenset({'runtime', 'application', 'memory', 'body',
                                'crt1', 'crti', 'crtn', 'libc'})


def required_components(profile, variant=None):
    """Select the explicit linked inventory; no runtime or native authority."""
    if profile in ('AENMX008/ABI23', 'AENMX009/ABI24'):
        return REQUIRED
    if profile == FS_PROFILE and variant in ('parent', 'helper'):
        return (FS_PARENT_REQUIRED if variant == 'parent'
                else FS_HELPER_REQUIRED)
    raise ValueError('component profile or variant mismatch')


def validate(manifest, expected_profile='AENMX008/ABI23'):
    """Reject incomplete/stale component receipts before any link invocation."""
    if (manifest.get('profile') != expected_profile
            or manifest.get('schema') != 'aether-session-components-v1'):
        raise ValueError('component profile or schema mismatch')
    required = required_components(expected_profile, manifest.get('variant'))
    entries = manifest.get('components')
    if not isinstance(entries, list) or any(not isinstance(e, dict) for e in entries):
        raise ValueError('invalid component inventory')
    names = [entry.get('name') for entry in entries]
    if len(names) != len(required) or set(names) != required:
        raise ValueError('missing or duplicate required component')
    paths = []
    for entry in entries:
        path = Path(entry['path'])
        if not path.is_absolute() or not path.is_file() or path.is_symlink():
            raise ValueError('component must be an absolute regular input')
        paths.append(path.resolve())
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(chunk)
        if digest.hexdigest() != entry.get('sha256'):
            raise ValueError('stale component: ' + entry['name'])
    if len(set(paths)) != len(paths):
        raise ValueError('duplicate component input')
