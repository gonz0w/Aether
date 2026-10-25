# SPDX-License-Identifier: BSD-2-Clause
"""Pinned private Rust policy adaptation; no service protocol or ambient owner."""
import hashlib
import json
import os
from pathlib import Path

from deps import ROOT

SEAL = '76e4c6ba70836a33cc155022ad27ee25d7a451f6c9539ba0877ba39442a3a460'
PROBE_SHA256 = '16e7fb8daf125bb4a575b37c61a328b9897ae1b05e329d12080e1f1f6a677023'
C_INPUTS = {
    'user/storage/openzfs-volume/zpl-read.h': 'eb7bdc9155369747c918944baba8f3b109951fff295273930a4df7cea0c7cc8a',
    'user/storage/openzfs-volume/zpl-write.h': 'a96ea8a0ee84b50e04ac3716b38de87d9eec519dd7f06ac452c43076f145dc4b',
    'user/storage/openzfs-volume/zpl-read.c': 'bee69ab7d07fae3747dbe147513af1f74e9567fb087347c7fc5bed1f2a850e65',
    'user/storage/openzfs-volume/zpl-write.c': '7870e3841dc0c6b46dadd087c8db107367a461d62bd7bb068e5eab5beae1225d',
    'user/storage/openzfs-volume/owner-probe.c': 'e566b1ef0e6d2081c1329b34cdf626d2b435fb15599eb6a9417575a029266806',
}
BUILDER_PROVENANCE = {
    'scripts/openzfs_volume.py': '2abdb178fc907e6db3356011a6522e3ef976cba0a8c7a0f44920d2788a736201',
    'scripts/service_runtime_smoke.py': 'fe85a4a225f1f5c82407ab199c8532ffb445060a0a24a95cb59d098021ba290f',
}
UTC_SHA256 = '39c9f9ba9ffd129c7e6fcf9ec01373a782754caf8a883eaa95c67c8711aea029'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def intake(delivery):
    root = Path(os.path.abspath(delivery))
    if root.resolve() != root or not root.is_dir():
        raise ValueError('filesystem bridge requires a real delivery directory')
    seal = root / 'SHA256SUMS'
    if seal.is_symlink() or sha(seal) != SEAL:
        raise ValueError('filesystem bridge manifest identity')
    inputs = {str(seal): SEAL}
    names = set()
    for line in seal.read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        path = Path(name)
        if path.is_absolute() or '..' in path.parts or name in names:
            raise ValueError('filesystem bridge member path')
        names.add(name)
        member = root / path
        if member.resolve() != member or not member.is_file() or sha(member) != digest:
            raise ValueError('filesystem bridge member identity: ' + name)
        inputs[str(member)] = digest
    if len(names) != 18 or {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()} != names | {'SHA256SUMS'}:
        raise ValueError('filesystem bridge member closure')
    if any(p.is_symlink() for p in root.rglob('*')):
        raise ValueError('filesystem bridge symlink')
    recorded = json.loads((root / 'inputs.json').read_text())
    if recorded['producer_files'] != C_INPUTS | BUILDER_PROVENANCE | {'userland/utc.h': UTC_SHA256}:
        raise ValueError('filesystem bridge producer provenance')
    for name, digest in C_INPUTS.items():
        path = ROOT / name
        if sha(path) != digest:
            raise ValueError('filesystem bridge C interface drift: ' + name)
        inputs[str(path)] = digest
    utc = ROOT / '.deps/native-utc-v3/runtime/utc.h'
    if sha(utc) != UTC_SHA256:
        raise ValueError('filesystem bridge UTC interface drift')
    inputs[str(utc)] = UTC_SHA256
    for entry in recorded['tools'].values():
        if sha(entry['path']) != entry['sha256']:
            raise ValueError('filesystem bridge tool drift')
        inputs[entry['path']] = entry['sha256']
    for name, digest in (recorded['rust_native_libraries'] | recorded['clang_resource_headers']).items():
        if sha(name) != digest:
            raise ValueError('filesystem bridge native dependency drift: ' + name)
        inputs[name] = digest
    builders = {name: sha(ROOT / name) for name in BUILDER_PROVENANCE}
    inputs.update({str(ROOT / name): digest for name, digest in builders.items()})
    return {'manifest_sha256': SEAL, 'root': str(root), 'inputs': inputs,
            'object': str(root / 'objects/filesystem-consumer.o'),
            'header_directory': str(root / 'source'),
            'builder_provenance': BUILDER_PROVENANCE, 'adaptation_builders': builders,
            'scope': 'new source-compatible owner adaptation; older partial-link receipt is not current native acceptance'}


def recheck(selected):
    if selected['manifest_sha256'] != SEAL:
        raise ValueError('filesystem bridge selection identity')
    for name, digest in selected['inputs'].items():
        path = Path(name)
        # Pinned LLVM entry points legitimately alias versioned executables.
        # Delivery members themselves must remain real, immutable files.
        member = path.is_relative_to(Path(selected['root']))
        if (member and path.resolve() != path) or not path.is_file() or sha(path) != digest:
            raise ValueError('filesystem bridge consumed input drift: ' + name)


def probe(text):
    if hashlib.sha256(text.encode()).hexdigest() != PROBE_SHA256:
        raise ValueError('filesystem bridge original probe drift')
    start = text.index('        unsigned char bytes[ZPL_PROBE_LENGTH];')
    end = text.index('\n    }', start)
    text = text[:start] + '''        aether_zpl_close(&view);
        aether_fs_probe_result completion = {0};
        error = aether_fs_policy_write_probe(spa, &completion);
        result.txg = completion.txg;
        result.bytes_staged = completion.bytes_staged;
        result.state = completion.state;
        if (!error)
            error = aether_zpl_open_write(spa, "testpool_zstd/x86_64", &view);''' + text[end:]
    old = '    if (!error)\n        *assigned = result.txg;'
    if text.count(old) != 1:
        raise ValueError('filesystem bridge assigned result context')
    text = text.replace(old, '    *assigned = result.txg;', 1)
    return text.replace('#include "zpl-write.h"', '#include "zpl-write.h"\n#include "native-probe.h"', 1)


def partial_origins(mapping):
    required = {'aether_fs_policy_write_probe': 'filesystem-consumer.o'}
    required.update({name: 'zpl-write.o' for name in (
        'aether_zpl_open_write', 'aether_zpl_close', 'aether_zpl_root',
        'aether_zpl_lookup', 'aether_zpl_read', 'aether_zpl_write')})
    found = {}
    owner = None
    for line in mapping.splitlines():
        fields = line.split()
        if len(fields) < 5:
            continue
        entry = fields[-1]
        if ':(' in entry:
            owner = entry.split(':(', 1)[0]
        elif entry in required:
            if entry in found or owner is None or not owner.endswith('/' + required[entry]):
                raise ValueError('filesystem bridge partial symbol origin: ' + entry)
            found[entry] = owner
    if set(found) != set(required):
        raise ValueError('filesystem bridge missing partial origins')
    return found


RECOVERY_SHA256 = '355d80d91f6eb0a62c87eb7e6345e3c30187bbadb869ba24504ba731a5d69662'
RECOVERY_STAGES = ('readonly-SPA', 'context-open', 'root', 'lookup', 'stream-read',
                   'file-hash', 'EOF', 'metadata-handle', 'metadata-read',
                   'metadata-size', 'metadata-flags', 'metadata-time-equality',
                   'UTC-lower-bound', 'UTC-upper-bound', 'UTC-nanoseconds')


def recovery_probe(text):
    """Error-only attribution, preserving every original recovery predicate."""
    if hashlib.sha256(text.encode()).hexdigest() != RECOVERY_SHA256:
        raise ValueError('filesystem recovery original probe drift')
    def replace(old, new):
        nonlocal text
        if text.count(old) != 1:
            raise ValueError('filesystem recovery diagnostic context: ' + old)
        text = text.replace(old, new, 1)
    replace('static int recovery_metadata(aether_zpl_view *view)\n{',
            'static int recovery_metadata(aether_zpl_view *view, unsigned char *stage)\n{\n    *stage = 8;')
    replace('    error = sa_bulk_lookup(handle, attrs, n);',
            '    *stage = 9;\n    error = sa_bulk_lookup(handle, attrs, n);')
    start = text.index('    if (size != 780248 ||')
    end = text.index('    return 0;', start)
    predicates = ('size != 780248',
        '(flags & (ZFS_ARCHIVE | ZFS_AV_MODIFIED)) != (ZFS_ARCHIVE | ZFS_AV_MODIFIED)',
        'memcmp(mtime, ctime, sizeof(mtime))',
        'mtime[0] < UINT64_C(1791290040)', 'mtime[0] > UINT64_C(1791290070)',
        'mtime[1] >= 1000000000')
    text = text[:start] + ''.join('    if (' + predicate + ') {\n        *stage = ' + str(index) + ';\n        return EIO;\n    }\n'
                                  for index, predicate in enumerate(predicates, 10)) + text[end:]
    marker = '''extern void aether_engine_utc_phase(unsigned char);
static int recovery_error(unsigned char stage, int error)
{
    aether_engine_utc_phase('E');
    aether_engine_utc_phase(stage);
    for (unsigned i = 0; i < 4; ++i)
        aether_engine_utc_phase(((uint32_t)error >> (8 * i)) & 255);
    return error;
}

'''
    replace('int aether_pool_namespace_recover(spa_t *spa)\n{',
            marker + 'int aether_pool_namespace_recover(spa_t *spa)\n{\n    unsigned char stage = 1;')
    replace('        return EROFS;', '        return recovery_error(stage, EROFS);')
    replace('    if (error)\n        return error;\n    aether_zpl_node root, file;',
            '    if (error)\n        return recovery_error(2, error);\n    stage = 3;\n    aether_zpl_node root, file;')
    replace('    if (!error)\n        error = aether_zpl_lookup(view, 34, 45, (const unsigned char *)"zstd",\n                                  4, &file);',
            '    if (!error) {\n        stage = 4;\n        error = aether_zpl_lookup(view, 34, 45, (const unsigned char *)"zstd",\n                                  4, &file);\n    }')
    replace('    while (!error && offset < 780248) {',
            '    if (!error) stage = 5;\n    while (!error && offset < 780248) {')
    replace('    if (!error && memcmp(digest, expected, sizeof(expected)))',
            '    if (!error) stage = 6;\n    if (!error && memcmp(digest, expected, sizeof(expected)))')
    replace('    size_t count = 99;', '    if (!error) stage = 7;\n    size_t count = 99;')
    replace('        error = recovery_metadata(view);', '        error = recovery_metadata(view, &stage);')
    replace('    aether_zpl_close(&view);\n    return error;',
            '    aether_zpl_close(&view);\n    return error ? recovery_error(stage, error) : 0;')
    return text


def recovery_source(text, writer_60s=False, diagnostic=False):
    """Select a fixed writer horizon; the reader's execution limit is unchanged."""
    if not isinstance(writer_60s, bool) or not isinstance(diagnostic, bool):
        raise ValueError('recovery source selectors must be boolean')
    if hashlib.sha256(text.encode()).hexdigest() != RECOVERY_SHA256:
        raise ValueError('filesystem recovery original probe drift')
    if diagnostic:
        text = recovery_probe(text)
    if writer_60s:
        old = 'mtime[0] > UINT64_C(1791290070)'
        if text.count(old) != 1:
            raise ValueError('filesystem recovery timestamp context')
        text = text.replace(old, 'mtime[0] > UINT64_C(1791290100)', 1)
        text = text.replace('unchanged30-second watchdog', 'selected60-second writer watchdog')
    return text
