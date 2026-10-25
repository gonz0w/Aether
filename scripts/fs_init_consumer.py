# SPDX-License-Identifier: BSD-2-Clause
"""Exact sys-init ABI29 intake and read-only activation oracle; no init policy."""
import json
from pathlib import Path
import re

from deps import ROOT
from fs_init_intake import intake as inspect_owner
from fs_launch_intake import digest

DELIVERY = ROOT / 'sys-init/docs/evidence/filesystem-init-owner-2026-10-20'
PREPARATION = 'd7bbb658307f27e48d87f786aa0417b0c8239a115695199f53819d927d75e568'
CANDIDATE = '092034e39375343388fa2a1c7198a484530b25bd0acc04796ec2606c03775c39'
ELF = '1bae5d805308c0f664945e52e5bb4564febd38315d2c62e515217fe1e54e53a9'
RAW = 'c0a01ec913eb44de96d27d93ac71416df015951cdb12095c09c7b17e9e8d706e'
PROGRAM = '76f7561bc8bcbbaf28ff63dcc5a1954026ed3b892ae3d5c24e07f1672708fc13'


def intake():
    files = {}
    def admit(path, expected):
        path = Path(path)
        if path.is_symlink() or not path.is_file() or digest(path) != expected:
            raise ValueError('sys-init consumer input drift: '+str(path))
        files[str(path)] = expected
    for name, expected in (('preparation.json', PREPARATION), ('candidate-inputs.json', CANDIDATE),
                           ('owner.elf', ELF), ('owner.raw', RAW)):
        admit(DELIVERY/name, expected)
    record = json.loads((DELIVERY/'preparation.json').read_text())
    selected = json.loads((DELIVERY/'candidate-inputs.json').read_text())
    if (selected['profile'] != 'AENFS003/ABI29 with nested AENMX009'
            or selected['bootstrap'] != [29, 0xa001, 0xf101, 0xc002, 0xd001, 0xc003]
            or selected['roles'] != dict(engine=0, selected_process=1,
                                        available_process_slots=[1, 2, 3, 4, 5], owner=6)
            or selected['engine_manifest_sha256'] != 'b69fd748b4d4fda334126dba96744a73f2a4b03649d5e9b1033ae253d52cc558'
            or selected['engine_elf_sha256'] != '89bbc3291a3d13d3639503048f6378a2ffac351d1cfe689d698135cbeab24997'
            or selected['selected_program_c002']['sha256'] != PROGRAM
            or record['status'] != 'pass-host-and-structural-only'
            or record['native_executed'] is not False):
        raise ValueError('sys-init consumer selection/coverage')
    sibling = ROOT / 'sys-init'
    for name, expected in record['sources'].items():
        if name not in ('prototypes/native-filesystem/'+n for n in ('init.rs', 'policy.rs', 'tests.rs', 'owner.ld')):
            raise ValueError('sys-init source closure')
        admit(sibling/name, expected)
        admit(DELIVERY/'source'/Path(name).name, expected)
    if len(record['sources']) != 4:
        raise ValueError('sys-init source closure')
    admit(sibling/'prototypes/native-filesystem/inputs.json', CANDIDATE)
    prior = selected['producer_mechanism_receipt']
    admit(ROOT/'docs/evidence/fs-session-init-native-2026-10-20.json', prior['sha256'])
    admit(ROOT/'user/storage/session/process.c', selected['selected_program_c002']['source_sha256'])
    for tool in record['tools'].values():
        admit(tool['path'], tool['sha256'])
    result = inspect_owner(DELIVERY/'owner.elf', DELIVERY/'owner.raw', ELF, RAW)
    if result['raw_bytes'] != 2072 or result['stack']['entry_stack_bytes'] != 1096:
        raise ValueError('sys-init matched code/stack result changed')
    return dict(inputs=files, owner_intake=result, raw=str(DELIVERY/'owner.raw'),
                elf=str(DELIVERY/'owner.elf'), selected_program_sha256=PROGRAM,
                scope='Read-only native activation candidate only; no mutation transcript or shell')


def trace(text, *, engine_pages=1328):
    """Validate this workload, never the conformance controller's RPT/TXG data.

    Readiness and protocol validation are bound to the exact reviewed owner;
    terminal0 is bound to the exact engine's aggregate cleanup contract. Native
    reclaim/VM stop and media inspection remain separate requirements.
    """
    if engine_pages not in (1328, 1329):
        raise ValueError('sys-init selected engine page count')
    lines = text.splitlines()
    if (lines.count('AETHER NATIVE BLOCK PASS') != 1
            or any(x in text for x in ('PANIC', 'NATIVE fault ', 'NATIVE supervisor result='))):
        raise ValueError('sys-init activation completion/fault')
    if [s for s in lines if s.startswith('NATIVE terminal ')] != [
            'NATIVE terminal slot=1 generation=1 kind=1 detail=0',
            'NATIVE terminal slot=0 generation=1 kind=1 detail=0']:
        raise ValueError('sys-init activation terminal identities')
    if any(s.startswith('NATIVE observation ') for s in lines):
        raise ValueError('sys-init activation must not use conformance observations')
    memory = re.findall(r'^NATIVE MEMORY admitted slot=(\d+) generation=(\d+) used=(\d+) remaining=(\d+)$', text, re.M)
    if len(memory) != 2 or sum(s.startswith('NATIVE MEMORY admitted ') for s in lines) != 2:
        raise ValueError('sys-init actual loader count')
    for row, slot, used, quota in zip(memory, (0, 1), (engine_pages, 21), (8192, 128), strict=True):
        if tuple(map(int, row)) != (slot, 1, used, quota-used):
            raise ValueError('sys-init actual loader role/identity')
    cleanup = []
    for slot, pages, prior in ((1, 128, 0), (0, 8192, 1)):
        cleanup += [f'NATIVE CLEANUP v=1 slot={slot} generation=1 phase={phase} selected={slot if phase == 1 else 6} pages={pages} reclaimed={prior+(phase == 7)}' for phase in range(1, 8)]
    if [s for s in lines if s.startswith('NATIVE CLEANUP ')] != cleanup:
        raise ValueError('sys-init ordered role cleanup')
    halts = re.findall(r'^NATIVE init halted ticks=(\d+) idle=(\d+) reclaimed=(\d+)$', text, re.M)
    if (len(halts) != 1 or sum(s.startswith('NATIVE init halted ') for s in lines) != 1
            or not 0 < int(halts[0][0]) <= 6000 or int(halts[0][2]) != 2):
        raise ValueError('sys-init quiescence/tick ceiling')
    order = [next(s for s in lines if s.startswith('NATIVE MEMORY admitted slot=0 ')),
             next(s for s in lines if s.startswith('NATIVE MEMORY admitted slot=1 ')),
             'NATIVE terminal slot=1 generation=1 kind=1 detail=0', *cleanup[:7],
             'NATIVE terminal slot=0 generation=1 kind=1 detail=0', *cleanup[7:],
             next(s for s in lines if s.startswith('NATIVE init halted ')), 'AETHER NATIVE BLOCK PASS']
    positions = [lines.index(s) for s in order]
    if positions != sorted(positions):
        raise ValueError('sys-init admission/settlement/halt ordering')
    pending = set()
    waits = wakes = 0
    for line in lines:
        if not line.startswith('NATIVE STORAGE WAIT '):
            continue
        match = re.fullmatch(r'NATIVE STORAGE WAIT slot=0 generation=1 phase=(park|wake) status=0', line)
        if match is None:
            raise ValueError('sys-init wait role/status')
        if match[1] == 'park':
            if pending:
                raise ValueError('sys-init duplicate park')
            pending.add(0)
            waits += 1
        else:
            if not pending:
                raise ValueError('sys-init unmatched wake')
            pending.clear()
            wakes += 1
    if pending or waits != wakes:
        raise ValueError('sys-init incomplete waits')
    return dict(profile='AENFS003/sys-init-owner29/engine26', admitted_instances=2,
                reclaimed=2, final_live_workers=0, cleanup_trace_version=1,
                cleanup_boundaries_per_instance=7, engine_terminal_zero=True,
                selected_process_terminal_zero=True, primary_channel_waits=waits,
                primary_channel_wakes=wakes, read_only_activation=True,
                source_bound_readiness_and_shutdown=True, native_failure_matrix=False,
                after_activation_file_readback=False)
