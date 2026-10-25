# SPDX-License-Identifier: BSD-2-Clause
"""Explicit local locations for fixed retained host dependencies, never source ROOT."""
import hashlib
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = 'AETHER_HOST_DEPENDENCY_ROOT'
HISTORICAL = 'sys-init/docs/evidence/filesystem-af07-owner-2026-10-21'
HISTORICAL_STUB = '536c3452204ca7081368019927857dc10c87fb82f68b58dec4a55be80076cbdb'
PREFIXES = ('.deps/native-current', '.deps/native-utc-v3',
            '.deps/native-service-runtime-v3',
            'userland/build/session-deliveries/filesystem-abi29-linked-2026-10-21-v1',
            'userland/build/session-deliveries/filesystem-abi29-linked-2026-10-21-v2',
            'sys-init/docs/evidence/filesystem-af07-owner-2026-10-21')
SEALED_ROOTS = {'.deps/native-current/sdk', '.deps/native-utc-v3',
                '.deps/native-utc-v3/base', '.deps/native-utc-v3/base/sdk',
                '.deps/native-service-runtime-v3', '.deps/native-service-runtime-v3/sdk',
                *PREFIXES[3:], *(name+'/bundle' for name in PREFIXES[3:5])}


def declaration():
    value = os.environ.get(ENV)
    if value is None:
        return None
    path = Path(value)
    if (not value or not path.is_absolute() or path != path.resolve()
            or path.is_symlink() or not path.is_dir()):
        raise ValueError('retained dependency root declaration')
    return str(path)


def _location(path, sealed):
    if '..' in Path(path).parts:
        raise ValueError('retained dependency parent traversal')
    original = Path(path).absolute()
    base = declaration()
    if base is None or not original.is_relative_to(ROOT):
        return original
    relative = original.relative_to(ROOT).as_posix()
    if not any(relative == prefix or relative.startswith(prefix+'/') for prefix in PREFIXES):
        return original
    if sealed and relative not in SEALED_ROOTS:
        return original
    target = Path(base)/relative
    actual = original.resolve()
    # A configured alias is an input location, not an OS read-only guarantee.
    # Never hide a different alias or conflicting real capsule behind routing.
    if actual != original and actual != target.resolve():
        raise ValueError('retained dependency alias target')
    if original.exists() and actual == original:
        stub = sealed and relative == HISTORICAL and original.is_dir() and {p.name for p in original.iterdir()} == {'README.md'} and hashlib.sha256((original/'README.md').read_bytes()).hexdigest() == HISTORICAL_STUB
        if not stub:
            if sealed:
                raise ValueError('retained dependency conflicts with real local capsule')
            return original
    if sealed and (target.is_symlink() or target.resolve() != target or not target.is_dir()):
        raise ValueError('retained dependency requires a real original directory')
    return target


def retained_root(path):
    """Only exact canonical capsule names map; copied/adversarial roots do not."""
    return _location(path, True)


def retained_input(path):
    """After legacy source relocation, route only named dependency member paths."""
    return _location(path, False)
