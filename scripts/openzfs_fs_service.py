# SPDX-License-Identifier: BSD-2-Clause
"""Exact private userland service intake and trusted one-write adaptation."""
import hashlib
import json
import os
from pathlib import Path

from deps import ROOT
from openzfs_fs_bridge import C_INPUTS, UTC_SHA256, PROBE_SHA256

CASES = ('normal', 'lost-reply', 'partial-request', 'close-failure')


def case_number(case):
    if not isinstance(case, str) or case not in CASES:
        raise ValueError('filesystem service requires a fixed case')
    return CASES.index(case)


SEAL = '5dd5f492dd2ab2c57321a8fd610f1f6fa488dece4c4b40466a37236bf24144c4'
LIFETIMES_SEAL = '0eddb895d8a8d6276834a0d4ec58aa77e13e44be882d5eab46695cf716ff825c'
LIFETIMES_DIGEST = 'e5e77fb2840ab21fb01a3cc4ca92059407ebdc5504f675f791c5d188e88c87aa'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def intake(delivery, lifetimes=False, namespace=False, mixed=False, waiting=False, bulk=False, runtime=False, activation=False, names=False, directories=False):
    if not isinstance(directories,bool) or (directories and not names):raise ValueError('directories require explicit names selection')
    if not isinstance(names,bool) or (names and not activation):raise ValueError('names require explicit activation selection')
    if not isinstance(activation,bool) or (activation and not (runtime and bulk and waiting and mixed)):
        raise ValueError('activation requires explicit runtime mixed wait selection')
    if not isinstance(runtime,bool) or (runtime and not bulk):raise ValueError('runtime requires explicit bulk selection')
    if not isinstance(bulk,bool) or (bulk and not (mixed and waiting)):raise ValueError('bulk requires explicit mixed wait selection')
    if not isinstance(waiting,bool) or (waiting and not mixed):
        raise ValueError('filesystem service wait requires explicit mixed selection')
    if not isinstance(lifetimes, bool):
        raise ValueError('filesystem service lifetime selector must be boolean')
    if not isinstance(namespace,bool) or (namespace and lifetimes):
        raise ValueError('filesystem service namespace/lifetimes selectors are exclusive booleans')
    if not isinstance(mixed,bool) or (mixed and (namespace or lifetimes)):
        raise ValueError('filesystem service mixed selector must be exclusive boolean')
    if mixed:
        from openzfs_fs_mixed_service import intake as mixed_intake
        return mixed_intake(delivery,waiting,bulk,runtime,activation,names,directories)
    if namespace:
        from openzfs_fs_namespace import intake as namespace_intake
        return namespace_intake(delivery)
    expected = LIFETIMES_SEAL if lifetimes else SEAL
    root = Path(os.path.abspath(delivery))
    if root.resolve() != root or not root.is_dir():
        raise ValueError('filesystem service requires a real delivery directory')
    seal = root / 'SHA256SUMS'
    if seal.is_symlink() or sha(seal) != expected:
        raise ValueError('filesystem service manifest identity')
    inputs = {str(seal): expected}
    names = set()
    for line in seal.read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        path = Path(name)
        if path.is_absolute() or '..' in path.parts or name in names:
            raise ValueError('filesystem service member path')
        names.add(name)
        member = root / path
        if member.resolve() != member or not member.is_file() or sha(member) != digest:
            raise ValueError('filesystem service member identity: ' + name)
        inputs[str(member)] = digest
    if (len(names) != (27 if lifetimes else 25) or any(p.is_symlink() for p in root.rglob('*')) or
            {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()} != names | {'SHA256SUMS'}):
        raise ValueError('filesystem service member closure')
    recorded = json.loads((root / 'inputs.json').read_text())
    if lifetimes:
        required = {'scripts/openzfs_fs_lifetime.py', 'scripts/openzfs_pool.py',
                    'user/storage/openzfs-volume/pool-lifetime.inc',
                    'user/storage/openzfs-volume/pool-lifetime.h',
                    'user/storage/openzfs-volume/pool-service-lifetime.h'}
        if set(recorded['producer_lifetime_files']) != required:
            raise ValueError('filesystem service lifetime contract closure')
        for name, digest in recorded['producer_lifetime_files'].items():
            if sha(ROOT / name) != digest:
                raise ValueError('filesystem service lifetime contract drift: ' + name)
            inputs[str(ROOT / name)] = digest
        if sha(root / 'ffi/pool-service-lifetime.h') != sha(ROOT / 'user/storage/openzfs-volume/pool-service-lifetime.h'):
            raise ValueError('filesystem service lifetime header mismatch')
    # Reviewed immutable C and channel contracts. Historical builder/doc hashes
    # are provenance; the new owner adaptation is separately frozen below.
    contracts = C_INPUTS | {'user/storage/namespace-channel.rs': recorded['producer_files']['user/storage/namespace-channel.rs'],
                            'user/storage/namespace-wire.rs': recorded['producer_files']['user/storage/namespace-wire.rs']}
    for name, digest in contracts.items():
        if sha(ROOT / name) != digest:
            raise ValueError('filesystem service original interface drift: ' + name)
        inputs[str(ROOT / name)] = digest
    utc = ROOT / '.deps/native-utc-v3/runtime/utc.h'
    if sha(utc) != UTC_SHA256:
        raise ValueError('filesystem service UTC interface drift')
    inputs[str(utc)] = UTC_SHA256
    for entry in recorded['tools'].values():
        if sha(entry['path']) != entry['sha256']:
            raise ValueError('filesystem service tool drift')
        inputs[entry['path']] = entry['sha256']
    for name, digest in (recorded['rust_native_libraries'] | recorded['clang_resource_headers']).items():
        if sha(name) != digest:
            raise ValueError('filesystem service native dependency drift: ' + name)
        inputs[name] = digest
    for name in ('openzfs_fs_service.py', 'openzfs_volume.py', 'openzfs_elapsed.py', 'service_runtime_smoke.py'):
        path = ROOT / 'scripts' / name
        inputs[str(path)] = sha(path)
    return {**({'lifetimes': True} if lifetimes else {}),
            'manifest_sha256': expected, 'root': str(root), 'inputs': inputs,
            'object': str(root / 'objects/filesystem-service.o'),
            'header_directory': str(root / 'source'),
            'scope': 'new source-compatible private owner adaptation; build-only producer object, not service acceptance'}


def recheck(selected):
    # Reconstruct the canonical selection as well as hashing consumed members:
    # changing an object/header pointer or deleting its hash cannot bypass intake.
    if selected.get('mixed',False):
        from openzfs_fs_mixed_service import intake as mixed_intake
        if selected != mixed_intake(selected['root'],selected.get('waiting',False),selected.get('bulk',False),selected.get('runtime',False),selected.get('activation',False),selected.get('names',False),selected.get('directories',False)):
            raise ValueError('mixed service consumed selection/input drift')
        return
    if selected.get('namespace',False):
        from openzfs_fs_namespace import intake as namespace_intake
        if selected != namespace_intake(selected['root']):
            raise ValueError('namespace service consumed selection/input drift')
        return
    lifetimes = selected.get('lifetimes', False)
    if selected.get('manifest_sha256') != (LIFETIMES_SEAL if lifetimes else SEAL):
        raise ValueError('filesystem service selection identity')
    if selected != intake(selected['root'], lifetimes):
        raise ValueError('filesystem service consumed selection/input drift')


def probe(text, case='normal', lifetimes=False):
    if not isinstance(lifetimes, bool):
        raise ValueError('filesystem service lifetime selector must be boolean')
    number = case_number(case)
    if hashlib.sha256(text.encode()).hexdigest() != PROBE_SHA256:
        raise ValueError('filesystem service original probe drift')
    start = text.index('        unsigned char bytes[ZPL_PROBE_LENGTH];')
    end = text.index('\n    }', start)
    text = text[:start] + '''        aether_zpl_close(&view);
        error = aether_fs_owner_probe(spa, &result);
        if (!error)
            error = aether_zpl_open_write(spa, "testpool_zstd/x86_64", &view);''' + text[end:]
    old = '    if (!error)\n        *assigned = result.txg;'
    if text.count(old) != 1:
        raise ValueError('filesystem service assigned result context')
    if lifetimes and number != 1:
        span = 'ZPL_PROBE_OFFSET + ZPL_PROBE_LENGTH)'
        if text.count(span) != 1:
            raise ValueError('filesystem service lifetime prediction context')
        text = text.replace(span, 'ZPL_PROBE_OFFSET + 128)', 1)
    return ('#define AETHER_FS_SERVICE_LIFETIMES 1\n' if lifetimes else '') + (('#define AETHER_FS_SERVICE_CASE ' + str(number) + '\n') if number else '') + text.replace(old, '    *assigned = result.txg;', 1).replace(
        '#include "zpl-write.h"', '#include "zpl-write.h"\n#include "fs-service-owner.inc"', 1)


def lifetime_recovery(text):
    from openzfs_fs_bridge import recovery_source
    selected = recovery_source(text, True, True)
    begin = selected.index('    static const unsigned char expected[32] = {')
    end = selected.index('};', begin) + 2
    expected = bytes.fromhex(LIFETIMES_DIGEST)
    replacement = ('    static const unsigned char expected[32] = {\n        ' +
                   ', '.join(f'0x{byte:02x}' for byte in expected) + '};')
    return selected[:begin] + replacement + selected[end:]


def partial_origins(mapping, case='normal', symbols=None, lifetimes=False):
    number = case_number(case)
    required = {'aether_fs_service_run': 'filesystem-service.o'}
    if lifetimes:
        required['aether_pool_service16_retire'] = 'vdev-selected.o'
    required.update({name: 'zpl-write.o' for name in (
        'aether_zpl_open_write', 'aether_zpl_close', 'aether_zpl_root',
        'aether_zpl_lookup', 'aether_zpl_read', 'aether_zpl_write')})
    if number == 3:
        required['__wrap_aether_zpl_close'] = 'zpl-write-probe.o'
    found = {}
    close_sections = []
    owner = None
    for line in mapping.splitlines():
        fields = line.split()
        if len(fields) < 5:
            continue
        entry = fields[-1]
        if ':(' in entry:
            owner = entry.split(':(', 1)[0]
            if entry.endswith(':(.text.aether_zpl_close)'):
                close_sections.append((owner, fields[0], fields[2]))
        elif entry in required:
            if entry in found or owner is None or not owner.endswith('/' + required[entry]):
                raise ValueError('filesystem service partial symbol origin: ' + entry)
            found[entry] = owner
    if number == 3 and 'aether_zpl_close' not in found:
        # LLD --wrap omits this original symbol label from its map although
        # the original function section and global definition both remain.
        # Require both independent views with matching address/size; never
        # infer an original function from its wrapper or a bare section name.
        definitions = [line.split() for line in (symbols or '').splitlines()
                       if line.split()[-1:] == ['aether_zpl_close']]
        if (len(close_sections) != 1 or len(definitions) != 1 or
                len(definitions[0]) != 4 or definitions[0][2] != 'T' or
                not close_sections[0][0].endswith('/zpl-write.o') or
                int(definitions[0][0], 16) != int(close_sections[0][1], 16) or
                int(definitions[0][1], 16) != int(close_sections[0][2], 16) or
                int(definitions[0][1], 16) == 0):
            raise ValueError('filesystem service original close section/definition mismatch')
        found['aether_zpl_close'] = close_sections[0][0]
    if set(found) != set(required):
        raise ValueError('filesystem service missing partial origins: ' + ', '.join(sorted(set(required) - set(found))))
    return found
