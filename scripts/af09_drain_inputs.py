# SPDX-License-Identifier: BSD-2-Clause
"""Bind reviewed AF09 host provenance; identities alone do not qualify execution."""
import hashlib
import json
from pathlib import Path
import re

CASES = ('file_prefix', 'exec_prefix', 'fork_prefix', 'stream', 'no_ack',
         'partial_ack', 'exit_deadline', 'pending_fragment')
ROLES = ('c_fixture', 'c_fixture_impact', 'c_entry', 'counters', 'builders',
         'kernel', 'build_guards', 'regressions', 'complete_host', 'review')
SCHEMA = 'aether-af09-drain-host-inputs-v1'


def selection(case):
    if not isinstance(case, str) or case not in ('none', *CASES):
        raise ValueError('AF09 unknown diagnostic case')
    return 0 if case == 'none' else CASES.index(case) + 1


def _digest(path, *, limit=None):
    checksum = hashlib.sha256()
    used = 0
    with path.open('rb') as stream:
        while True:
            block = stream.read(65536 if limit is None else min(65536, limit - used + 1))
            if not block:
                break
            used += len(block)
            if limit is not None and used > limit:
                raise ValueError('AF09 host manifest size')
            checksum.update(block)
    return checksum.hexdigest()


def _identity(identity, *, limit=None):
    if (not isinstance(identity, dict) or set(identity) != {'path', 'sha256'}
            or not isinstance(identity['path'], str)
            or not isinstance(identity['sha256'], str)
            or re.fullmatch('[0-9a-f]{64}', identity['sha256']) is None):
        raise ValueError('AF09 host identity shape')
    path = Path(identity['path'])
    if not path.is_absolute() or path.is_symlink() or not path.is_file():
        raise ValueError('AF09 host input unavailable')
    if limit is not None and path.stat().st_size > limit:
        raise ValueError('AF09 host manifest size')
    if _digest(path, limit=limit) != identity['sha256']:
        raise ValueError('AF09 host input changed: ' + str(path))
    return dict(identity)


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError('AF09 duplicate host input field')
        result[key] = value
    return result


def host_inputs(identity, case):
    """Recheck a closed reviewed manifest and its retained current input files.

    Records are opaque provenance, not interpreted pass claims. The separate
    review and actual test receipts establish coverage; native evidence still
    requires artifact association and phase-specific oracles.
    """
    if selection(case) == 0:
        raise ValueError('AF09 host manifest requires selected diagnostic')
    identity = _identity(identity, limit=4 * 1024**2)
    path = Path(identity['path'])
    with path.open('rb') as stream:
        raw = stream.read(4 * 1024**2 + 1)
    if len(raw) > 4 * 1024**2:
        raise ValueError('AF09 host manifest size')
    if hashlib.sha256(raw).hexdigest() != identity['sha256']:
        raise ValueError('AF09 host manifest changed during read')
    report = json.loads(raw.decode('utf-8'), object_pairs_hook=_pairs)
    if (not isinstance(report, dict)
            or set(report) != {'schema', 'cases', 'inputs', 'records'}
            or report['schema'] != SCHEMA or report['cases'] != list(CASES)
            or not isinstance(report['inputs'], dict) or not report['inputs']
            or not isinstance(report['records'], dict)
            or set(report['records']) != set(ROLES)):
        raise ValueError('AF09 host manifest shape/case family')
    inputs = {}

    def merge(item):
        limit = 4 * 1024**2 if isinstance(item, dict) and item.get('path') == identity['path'] else None
        item = _identity(item, limit=limit)
        name, checksum = item['path'], item['sha256']
        if name in inputs and inputs[name] != checksum:
            raise ValueError('AF09 host input identity conflict')
        inputs[name] = checksum
        return item

    for name, checksum in report['inputs'].items():
        merge({'path': name, 'sha256': checksum})
    records = {role: merge(report['records'][role]) for role in ROLES}
    merge(identity)
    module = Path(__file__).resolve()
    merge({'path': str(module), 'sha256': _digest(module)})
    # Reject a concurrent manifest replacement, rather than associating new
    # contents with the identity that was checked before decoding.
    _identity(identity, limit=4 * 1024**2)
    return {'identity': identity, 'inputs': inputs, 'records': records}
