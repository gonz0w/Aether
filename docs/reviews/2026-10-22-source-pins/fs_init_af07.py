# SPDX-License-Identifier: BSD-2-Clause
"""Exact AF07 sys-init delivery intake; activation policy remains in sys-init."""
import json
from pathlib import Path

from deps import ROOT
from fs_init_consumer import PROGRAM, trace as activation_trace
from fs_init_intake import intake as inspect_owner
from fs_launch_intake import digest
from fs_metadata_launch import closure, intake as engine_intake

DELIVERY = ROOT.parent/'sys-init/docs/evidence/filesystem-af07-owner-2026-10-21'
SEAL = '8f99308958df2552b527bc6abf07a78ea6b8a8bb670fd706139d1cab5c5ddd96'
ENGINE = ROOT/'.deps/fs-launch-af07-2026-10-21-v3'
ENGINE_SEAL = 'e28d249b97d2e0a94c376190ec3f3839d50b6c1426cf788bab8f303fdb4084ac'
ELF = '87598149c7a33307fffd3dc393f4cb87a04f635b40276f079943f93a904ebc03'
RAW = '620939e5218df104586ff38ce843776696c70814efdd2180c0244e7defae08a7'
ENGINE_ELF = '9039e7b1d9a488076e3f8329b3666f39d85385f294d89954dd03df7c2df1753a'


def intake(directory, seal):
    """Associate a fresh harness build with the exact engine selected by init.

    Original v3 members stay sealed. Its historical harness inputs need not
    equal the changed harness; the new build's entire live closure must pass,
    and its guest executable must equal the pinned original executable.
    """
    files = {}
    def admit(path, expected):
        path = Path(path)
        if path.is_symlink() or not path.is_file() or digest(path) != expected:
            raise ValueError('AF07 sys-init input drift: '+str(path))
        files[str(path)] = expected
    admit(DELIVERY/'sha256.json', SEAL)
    members = json.loads((DELIVERY/'sha256.json').read_text())
    actual = set()
    for path in DELIVERY.rglob('*'):
        if path.is_symlink():
            raise ValueError('AF07 sys-init delivery symlink')
        if path.is_file():
            actual.add(str(path.relative_to(DELIVERY)))
    if actual != set(members) | {'sha256.json'}:
        raise ValueError('AF07 sys-init member closure')
    for name, row in members.items():
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('AF07 sys-init member path')
        admit(DELIVERY/relative, row['sha256'])
        if (DELIVERY/relative).stat().st_size != row['bytes']:
            raise ValueError('AF07 sys-init member size')
    record = json.loads((DELIVERY/'preparation.json').read_text())
    selected = json.loads((DELIVERY/'inputs.json').read_text())
    if (selected['profile'] != 'AENFS003/ABI29 with nested AENMX009'
            or selected['bootstrap'] != [29, 0xa001, 0xf101, 0xc002, 0xd001, 0xc003]
            or selected['roles'] != dict(engine=0, selected_process=1,
                available_process_slots=[1, 2, 3, 4, 5], owner=6)
            or selected['wire_protocol'] != 'AFSRPC07' or selected['engine_root_rights'] != 31
            or selected['engine_manifest_sha256'] != ENGINE_SEAL
            or selected['engine_elf_sha256'] != ENGINE_ELF
            or selected['selected_program_c002']['sha256'] != PROGRAM
            or selected['native_acceptance'] is not False
            or record['native_acceptance'] is not False or record['all_inputs_unchanged'] is not True):
        raise ValueError('AF07 sys-init selection/coverage')
    source_names = {'init.rs', 'policy.rs', 'tests.rs', 'owner.ld', 'inputs.json'}
    if set(record['sources']) != {'prototypes/native-filesystem-af07/'+n for n in source_names}:
        raise ValueError('AF07 sys-init source closure')
    for name, expected in record['sources'].items():
        admit(ROOT.parent/'sys-init'/name, expected)
        admit(DELIVERY/Path(name).name, expected)
    for group in ('old_and_external_inputs', 'engine_members', 'tools'):
        for name, expected in record[group].items():
            if not Path(name).is_absolute():
                raise ValueError('AF07 sys-init external path')
            admit(name, expected)
    _, engine_members = closure(ENGINE, ENGINE_SEAL, 30)
    if engine_members['filesystem.elf'] != ENGINE_ELF:
        raise ValueError('AF07 sys-init original engine identity')
    rebuilt = engine_intake(directory, seal)
    if rebuilt['elf_sha256'] != ENGINE_ELF:
        raise ValueError('AF07 sys-init rebuilt engine differs from selected executable')
    admit(Path(directory)/'SHA256SUMS', seal)
    admit(Path(directory)/'filesystem.elf', ENGINE_ELF)
    result = inspect_owner(DELIVERY/'owner.elf', DELIVERY/'owner.raw', ELF, RAW)
    if result['raw_bytes'] != 2072 or result['stack']['entry_stack_bytes'] != 1096:
        raise ValueError('AF07 sys-init code/stack changed')
    return dict(inputs=files, owner_intake=result, raw=str(DELIVERY/'owner.raw'),
        elf=str(DELIVERY/'owner.elf'), selected_program_sha256=PROGRAM,
        original_engine_manifest=ENGINE_SEAL, selected_engine_manifest=seal,
        same_selected_engine_elf=ENGINE_ELF, protocol='AFSRPC07',
        scope='Exact AF07 read-only activation; not filesystem mutations or shell')


def trace(text):
    result = activation_trace(text, engine_pages=1329)
    result.update(filesystem_protocol='AFSRPC07', engine_loader_pages=1329)
    return result


def failed_peer_source(text):
    if text.count('AFSRPC06') != 2 or text.count('AFSRPC05') != 1:
        raise ValueError('AF07 failed-peer wire context changed')
    return text.replace('AFSRPC06', 'AFSRPC07').replace('AFSRPC05', 'AFSRPC06')
