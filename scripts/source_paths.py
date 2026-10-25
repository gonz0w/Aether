# SPDX-License-Identifier: BSD-2-Clause
"""Relocate recorded inputs; distinguish historical build tooling from live code."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY = Path('/Users/cam/DEV')
TOOLING = ROOT / 'docs/reviews/2026-10-22-source-pins'
CATALOG_SHA256 = '3a1250dfc231575111046b1083cf67c7f155e2d7a059ab200ed2d5fad264693d'


def relocate(path):
    """Map only the four former checkout prefixes; never resolve arbitrary links."""
    path = Path(path)
    for old, new in (('Aether', ROOT), ('Aether-userland', ROOT / 'userland'),
                     ('sys-init', ROOT / 'sys-init'), ('pkg-mgr', ROOT / 'pkg-mgr')):
        prefix = LEGACY / old
        if path.is_relative_to(prefix):
            return new / path.relative_to(prefix)
    return path


def dependency_input(path, expected):
    """Read exact build provenance for seven path-adapted Python tools only.

    This never substitutes kernel, service, ABI or binary inputs. Fresh builds
    must still capture and verify their live source closure separately. An old
    build receipt is provenance for its artifact, not current harness acceptance.
    """
    path = relocate(path)
    raw = (TOOLING / 'pins.json').read_bytes()
    if hashlib.sha256(raw).hexdigest() != CATALOG_SHA256:
        raise ValueError('migration tooling catalog changed')
    pins = json.loads(raw)
    relative = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else None
    if relative in pins and expected == pins[relative]:
        frozen = TOOLING / path.name
        if frozen.is_symlink() or hashlib.sha256(frozen.read_bytes()).hexdigest() != expected:
            raise ValueError('migration tooling provenance changed')
        return frozen
    from fs_host_dependencies import retained_input
    return retained_input(path)
