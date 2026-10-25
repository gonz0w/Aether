# SPDX-License-Identifier: BSD-2-Clause
"""Independent sealed runtime intake and scoped empty-engine qualification."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import struct
import subprocess
import sys
import tempfile

from deps import ROOT
from evidence import compact_run
from native_smoke import run
from regression import Parser

SEAL = '101001e0edefb8471546ebc85d9aea6ffa759529243c8507abe288ddb84d0ba1'
ARCHIVE = '0d9b906f2fcf505ee69bc7c74a7e0e2ad4fb805f53963a343fdd709fbfcb6178'
BASE = ROOT / '.deps/native-current/sdk'
DEPENDENCY = ROOT / '.deps/native-service-runtime-v2'
SOURCE = ROOT / 'user/storage/service-runtime'
UTC_SEAL = '15887618d50ac659da095d7a32af0255a8f382b41e40661e6ac6614e6b32645c'
UTC_ARCHIVE = 'd894b4a8f5624a265e265029a28e0b532f1e688cdb6a925cb3cd54f0ca4ee3e4'
UTC_DEPENDENCY = ROOT / '.deps/native-utc-v2'
FIXED_SEAL = '5adc4f6e9c255df3ead08404fca177d22db00a089429f1c0666fd90dd1812c6d'
FIXED_ARCHIVE = '8262b1977be3b8fff449a6e9ac6d86b20acbc7ab0a1e38102287aecff20b9b23'
FIXED_UTC_SEAL = 'ce420b8ac745287ea057b6c0b8949eb436a63b519e270b7ed7bf164ef342bad3'
FIXED_UTC_ARCHIVE = '693518d97acafe99f427cae5b42b5cc7aea7f0e8656c17f185fc8c24a0e06150'
EXHAUSTION_CASE = 'reaper-exhaustion'
UTC_CASES = ('utc-spa', 'utc-leap', 'utc-disabled', 'utc-policy', 'utc-reuse', 'utc-reuse-short')
PHYSICAL_CORE_CASES = ('spa-physical-small', 'spa-physical-no-callback', 'spa-physical-corrupt', 'spa-physical')
WRITE_CASES = ('spa-physical-write', 'spa-physical-write-verify', 'spa-physical-no-flush',
               'spa-physical-flush-rights', 'spa-physical-flush-revoked', 'spa-physical-write-no-callback')
PHYSICAL_CASES = (*PHYSICAL_CORE_CASES, 'spa-physical-revoked', 'spa-physical-open-checkpoint', *WRITE_CASES)
ACTIVE_CASES = ('spa-active', 'spa-active-no-activation', 'spa-active-no-callback')
SPA_UTC_CASES = ('spa-utc', 'spa-utc-no-observer')
POOL_CASES = ('pool-create', 'pool-import')
WORKER_CASES = ('block-workers', 'block-workers-readonly', 'block-workers-inline')
REAPER_CASES = ('reaper-cycle', 'reaper-serial')


def pool_cases(case):
    if case == 'pool-import':
        return POOL_CASES
    if case in (None, 'pool-create'):
        return ('pool-create',)
    raise ValueError('unknown pool case')


def pool_attached_media(out, case):
    return out / ('disposable.raw' if case == 'pool-import' else 'pool-create/disposable.raw')

def physical_cases(case, writable=False):
    if case is None:
        return WRITE_CASES if writable else PHYSICAL_CORE_CASES
    if case == 'spa-physical-write-verify':
        raise ValueError('fresh-VM physical verify requires the preceding write in --spa-write')
    if case not in PHYSICAL_CASES:
        raise ValueError('unknown physical case')
    if writable and case not in WRITE_CASES:
        raise ValueError('write group requires writable physical cases')
    return (case,)


def volume_readonly(case):
    if case == 'pool-import':
        return True
    if case in WRITE_CASES:
        return case == 'spa-physical-write-verify'
    return case in ('block-readonly', 'block-workers-readonly', 'block-workers-inline', *SPA_UTC_CASES, *UTC_CASES, *ACTIVE_CASES, *PHYSICAL_CASES)


def check_write_trace(serial, case):
    tags = {
        'spa-physical-write': 'BIUVWACOqstkhgcfjipQSTKHPDJFR',
        'spa-physical-write-verify': 'BIUVWACOQSTKHPDJFR',
        'spa-physical-no-flush': 'BIUVWACOqstkhgi',
        'spa-physical-flush-rights': 'BIUVWACOqstkhgcfei',
        'spa-physical-flush-revoked': 'BIUVWACOqstkhgcfei',
        'spa-physical-write-no-callback': 'BIUVWACOqsth',
    }[case]
    rows = re.findall(r'^NATIVE observation slot=(\d+) generation=(\d+) offset=(\d+) byte=(\d+)$', serial, re.M)
    expected = [(0, 1, i * 8, ord(tag)) for i, tag in enumerate(tags)]
    if case in WRITE_CASES[:2]:
        expected += [(0, g, i * 8, ord(tag)) for g in (2, 3) for i, tag in enumerate('BNR')]
    if [tuple(map(int, row)) for row in rows] != expected:
        raise ValueError('physical write/flush observation order or identity')
    if case not in WRITE_CASES[:2]:
        detail = 868 if case == 'spa-physical-no-flush' else 871 if case == 'spa-physical-write-no-callback' else 869
        terminals = re.findall(r'^NATIVE terminal slot=(\d+) generation=(\d+) kind=(\d+) detail=(\d+)$', serial, re.M)
        if [tuple(map(int, row)) for row in terminals] != [(0, 1, 1, detail)] or (
                re.findall(r'^NATIVE supervisor result=(\d+) reclaimed=(\d+)$', serial, re.M) != [('401', '0')]):
            raise ValueError('physical write/flush exact failure and unclean owner')
    return {'write_flush_observation_rows': len(tags),
            'actual_provider_flush_qualified': case == 'spa-physical-write',
            'fresh_vm_read_only': case == 'spa-physical-write-verify'}


def check_pool_create_trace(serial, pool_data=False, pool_capacity=False):
    if pool_capacity and not pool_data:
        raise ValueError('capacity trace requires assigned baseline data')
    rows = [tuple(map(int, r)) for r in re.findall(
        r'^NATIVE observation slot=(\d+) generation=(\d+) offset=(\d+) byte=(\d+)$', serial, re.M)]
    phases = b"BIUVWP????????CAT????????SDJFR" if pool_data else b"BIUVWP????????CADJFR"
    if pool_capacity:
        phases = b"BIUVWP????????CAT????????SQ\x1cDJFR"
    expected = [(0, 1, i * 8) for i in range(len(phases))]
    expected += [(0, g, i * 8) for g in (2, 3) for i in range(3)]
    if [r[:3] for r in rows] != expected:
        raise ValueError('pool creation observation identity/count/order')
    for i, r in enumerate(rows[:len(phases)]):
        if not (6 <= i < 14 or (pool_data and 17 <= i < 25)) and r[3] != phases[i]:
            raise ValueError('pool creation phase missing')
    if bytes(r[3] for r in rows[len(phases):]) != b"BNRBNR":
        raise ValueError('pool replacement authority denial absent')
    target = int.from_bytes(bytes(r[3] for r in rows[17:25]), 'little') if pool_data else 0
    if pool_data and not target:
        raise ValueError('pool data assigned target absent')
    result = {'assigned_target_txg': target, 'ordered_provider_witness': pool_data,
            'creation_owner_generations': [1], 'denied_owner_generations': [2, 3],
            'input_xdr_fnv1a64': bytes(r[3] for r in rows[6:14]).hex(),
            'clean_export_observed': True, 'assigned_DMU_transaction': pool_data,
            'resource_scope': 'phase-end observations only; transient peaks/stack demand unqualified'}
    if pool_capacity:
        result.update(capacity_denial_baseline_validated=True, reservation_bytes=128 * 1024 * 1024,
                      original_reservation_errno=28)
    return result


def check_pool_import_trace(serial, pool_data=False, zpl_stages=False, first_write=False, txg_worker=False, sync_stages=False):
    if sync_stages and not txg_worker:
        raise ValueError("sync stages require worker profile")
    rows = [tuple(map(int, r)) for r in re.findall(
        r'^NATIVE observation slot=(\d+) generation=(\d+) offset=(\d+) byte=(\d+)$', serial, re.M)]
    if txg_worker and (not zpl_stages or first_write):
        raise ValueError('TXG worker trace requires exclusive stage profile')
    if first_write and not zpl_stages:
        raise ValueError('first-write trace requires stage profile')
    if zpl_stages and not pool_data:
        raise ValueError('ZPL stage trace requires data profile')
    phases = b'BIUVWLP????????OAMT????????SDJFR' if pool_data else b'BIUVWLP????????OAMDJFR'
    if zpl_stages:
        phases = b'BIUVWLPOAMTbeicpvrw????????SDJFR' if sync_stages else b'BIUVWLPOAMTbqsluodw????????SDJFR' if txg_worker else b'BIUVWLPOAMTeabcdwsf????????SDJFR' if first_write else b'BIUVWLPOAMTorhc12vx????????SDJFR'
    expected = [(0, 1, i * 8) for i in range(len(phases))]
    expected += [(0, g, i * 8) for g in (2, 3) for i in range(3)]
    if [r[:3] for r in rows] != expected:
        raise ValueError('pool import observation identity/count/order')
    for i, row in enumerate(rows[:len(phases)]):
        if not ((not zpl_stages and 7 <= i < 15) or (pool_data and 19 <= i < 27)) and row[3] != phases[i]:
            raise ValueError('pool import phase missing')
    if bytes(row[3] for row in rows[len(phases):]) != b'BNRBNR':
        raise ValueError('pool import replacement denial absent')
    target = int.from_bytes(bytes(row[3] for row in rows[19:27]), 'little') if pool_data else 0
    if pool_data and not target:
        raise ValueError('pool data recovered target absent')
    result = {'recovered_target_txg': target, 'readonly_data_readback': pool_data,
            'import_owner_generations': [1], 'denied_owner_generations': [2, 3],
            'readonly_MOS_creation_version_readback': True, 'readonly_pool_retired': True,
            'clean_export_observed': False,
            'assigned_DMU_transaction': False}
    if zpl_stages:
        result['stage_boundaries_observed'] = 'beicpvrw' if sync_stages else 'bqsluodw' if txg_worker else 'eabcdwsf' if first_write else 'orhc12vx'
    else:
        result['input_xdr_fnv1a64'] = bytes(row[3] for row in rows[7:15]).hex()
    return result


def check_pool_data_pair(creator, importer, interrupted=False, uncommitted=False):
    if uncommitted and (not interrupted or not creator.get('checkpoint_before_commit') or
                        not creator.get('baseline_synced') or creator.get('candidate_committed') is not False or
                        creator.get('uncommitted_candidate_txg', 0) <= creator.get('assigned_target_txg', 0)):
        raise ValueError('uncommitted pair requires dirty held candidate newer than synced baseline')
    if interrupted and (not creator.get('writer_vm_interrupted') or
                        not creator.get('vm_run_returned') or
                        not creator.get('checkpoint_before_commit' if uncommitted else 'checkpoint_after_sync') or
                        creator.get('clean_export_observed') or creator.get('guest_reclaim_qualified')):
        raise ValueError('interrupted data pair requires confirmed unclean checkpoint/VM stop')
    if (not creator.get('assigned_DMU_transaction') or
            not creator.get('ordered_provider_witness') or
            not importer.get('readonly_data_readback') or
            not creator.get('assigned_target_txg') or
            creator['assigned_target_txg'] != importer.get('recovered_target_txg')):
        raise ValueError('pool data assigned/recovered target or ordered witness mismatch')
    qualification = ('uncommitted_recovery_qualified' if uncommitted else
                     'interrupted_data_recovery_qualified' if interrupted else 'fresh_data_pair_qualified')
    return {qualification: True,
            'original_assigned_target_txg': creator['assigned_target_txg']}


def check_pool_interrupted_trace(serial, uncommitted=False):
    """Exact selected live checkpoint, with no clean export or guest reclaim."""
    lines = serial.splitlines()
    raw = [line for line in lines if line.startswith('NATIVE observation ')]
    pattern = r'NATIVE observation slot=(\d+) generation=(\d+) offset=(\d+) byte=(\d+)'
    rows = [re.fullmatch(pattern, line) for line in raw]
    phases = b'BIUVWPCAT????????SH????????K' if uncommitted else b'BIUVWP????????CAT????????SK'
    target_start = 9 if uncommitted else 17
    if len(rows) != len(phases) or any(row is None for row in rows):
        raise ValueError('interrupted writer exact checkpoint row count/shape')
    values = [tuple(map(int, row.groups())) for row in rows]
    for index, (slot, generation, offset, byte) in enumerate(values):
        if (slot, generation, offset) != (0, 1, index * 8) or not 0 <= byte <= 255:
            raise ValueError('interrupted writer observation identity/byte')
        variable = (9 <= index < 17 or 19 <= index < 27) if uncommitted else (
            6 <= index < 14 or 17 <= index < 25)
        if not variable and byte != phases[index]:
            raise ValueError('interrupted writer checkpoint order')
    if any(line.startswith(('NATIVE terminal ', 'NATIVE CLEANUP ',
                            'NATIVE supervisor result=', 'AETHER PANIC:')) or
           line == 'AETHER NATIVE BLOCK PASS' for line in lines):
        raise ValueError('interrupted writer has forbidden terminal/cleanup/export result')
    target = int.from_bytes(bytes(row[3] for row in values[target_start:target_start + 8]), 'little')
    if not target:
        raise ValueError('interrupted writer nonzero assigned target required')
    result = {'writer_vm_interrupted': True, 'assigned_target_txg': target,
            'ordered_provider_witness': True, 'assigned_DMU_transaction': True,
            'clean_export_observed': False, 'guest_reclaim_qualified': False,
              'reclaimed': 0, 'checkpoint_after_sync': not uncommitted}
    if uncommitted:
        candidate = int.from_bytes(bytes(row[3] for row in values[19:27]), 'little')
        if candidate <= target:
            raise ValueError('uncommitted candidate must be newer than synced baseline')
        result.update(checkpoint_before_commit=True, baseline_synced=True,
                      uncommitted_candidate_txg=candidate, candidate_committed=False)
    else:
        result['input_xdr_fnv1a64'] = bytes(row[3] for row in values[6:14]).hex()
    return result


def check_pool_import_media(prior, disk, interrupted=False, uncommitted=False):
    """Host run returned/stopped and the validated previous outcome owns media."""
    if (prior.get('name') != 'pool-create' or prior.get('status') != 'pass' or
            not prior.get('vm_run_returned') or prior.get('disk_sha256') != sha(disk)):
        raise ValueError('fresh pool import requires completed create/VM teardown on exact media')
    if interrupted and (not prior.get('writer_vm_interrupted') or
                        not prior.get('ordered_provider_witness') or
                        not prior.get('assigned_target_txg') or
                        prior.get('clean_export_observed') or prior.get('guest_reclaim_qualified')):
        raise ValueError('fresh interrupted import requires unclean ordered stopped writer')
    if uncommitted and (not interrupted or not prior.get('checkpoint_before_commit') or
                        not prior.get('baseline_synced') or prior.get('candidate_committed') is not False or
                        prior.get('uncommitted_candidate_txg', 0) <= prior.get('assigned_target_txg', 0)):
        raise ValueError('fresh uncommitted import requires dirty held candidate and synced baseline')


def corrupt_pool_label_headers(data):
    """Only after confirmed writer stop; mutate four original encoding bytes."""
    region = 64 * 1024 * 1024
    if (len(data) != region + 8192 or data[:4096] != bytes([165]) * 4096 or
            data[-4096:] != bytes([165]) * 4096):
        raise ValueError('label corruption requires exact disposable geometry/canaries')
    offsets = [4096 + start + 16384 for start in
               (0, 262144, region - 524288, region - 262144)]
    if any(data[offset] != 1 for offset in offsets):
        raise ValueError('label corruption requires four original XDR encoding bytes')
    changed = bytearray(data)
    for offset in offsets:
        changed[offset] = 255
    return bytes(changed), {
        'pre_corruption_sha256': hashlib.sha256(data).hexdigest(),
        'post_corruption_sha256': hashlib.sha256(changed).hexdigest(),
        'changes': [{'offset': offset, 'before': 1, 'after': 255} for offset in offsets],
        'scope': 'four header encoding bytes only; writer stopped before host mutation',
    }


def corrupt_pool_uberblocks(data):
    """Damage only populated 1KiB slots on this stopped, private ashift9 disk."""
    region = 64 * 1024 * 1024
    if (len(data) != region + 8192 or data[:4096] != bytes([165]) * 4096 or
            data[-4096:] != bytes([165]) * 4096):
        raise ValueError('uberblock corruption requires exact disposable geometry/canaries')
    changes = []
    for label, start in enumerate((0, 262144, region - 524288, region - 262144)):
        populated = 0
        for slot in range(128):
            offset = 4096 + start + 131072 + slot * 1024
            magic, version, txg = struct.unpack_from('<QQQ', data, offset)
            if magic != 0xBAB10C:
                continue
            if version != 5000 or not txg or struct.unpack_from('<Q', data, offset + 984)[0] != 0x210DA7AB10C7A11:
                raise ValueError('uberblock corruption requires original populated slot geometry')
            byte_offset = offset + 1023
            changes.append({'label': label, 'slot': slot, 'txg': txg, 'offset': byte_offset,
                            'before': data[byte_offset], 'after': data[byte_offset] ^ 1})
            populated += 1
        if not populated:
            raise ValueError('uberblock corruption requires populated slots in all four labels')
    changed = bytearray(data)
    for row in changes:
        changed[row['offset']] = row['after']
    return bytes(changed), {'pre_corruption_sha256': hashlib.sha256(data).hexdigest(),
                           'post_corruption_sha256': hashlib.sha256(changed).hexdigest(),
                           'changes': changes,
                           'scope': 'one checksum bit per populated uberblock; stopped owned media only; labels and all other bytes preserved'}


def check_pool_corrupt_label_trace(serial, uberblocks=False):
    """Exact planned header or original SPA checksum rejection; no guest reclaim."""
    lines = serial.splitlines()
    observations = [line for line in lines if line.startswith('NATIVE observation ')]
    expected = [f'NATIVE observation slot=0 generation=1 offset={i * 8} byte={byte}'
                for i, byte in enumerate(b'BIUVWL')]
    if uberblocks:
        pattern = r'NATIVE observation slot=0 generation=1 offset=(\d+) byte=(\d+)'
        rows = [re.fullmatch(pattern, line) for line in observations]
        if len(rows) != 21 or any(row is None or not 0 <= int(row[2]) <= 255 for row in rows):
            raise ValueError('corrupt uberblock observation shape')
        tags = b'BIUVWLP' + bytes(int(row[2]) for row in rows[7:15]) + b'OE\x06\0\0\0'
        expected = [f'NATIVE observation slot=0 generation=1 offset={i * 8} byte={byte}'
                    for i, byte in enumerate(tags)]
    terminal = 'NATIVE terminal slot=0 generation=1 kind=1 detail=873'
    cleanup = [f'NATIVE CLEANUP v=1 slot=0 generation=1 phase={phase} '
               f'selected={selected} pages=8192 reclaimed=0'
               for phase, selected in ((1, 0), (2, 2))]
    final = 'NATIVE supervisor result=401 reclaimed=0'
    panic = 'AETHER PANIC: native C profile rejected'
    if (observations != expected or
            [line for line in lines if line.startswith('NATIVE terminal ')] != [terminal] or
            [line for line in lines if line.startswith('NATIVE CLEANUP ')] != cleanup or
            [line for line in lines if line.startswith('NATIVE supervisor result=')] != [final] or
            [line for line in lines if line.startswith('AETHER PANIC:')] != [panic] or
            'AETHER NATIVE BLOCK PASS' in lines):
        raise ValueError('corrupt label exact pre-import rejection/unclean owner')
    ordered = expected + [terminal, *cleanup, final, panic]
    if [lines.index(line) for line in ordered] != sorted(lines.index(line) for line in ordered):
        raise ValueError('corrupt label rejection operation order')
    result = {'corrupt_uberblock_rejection_observed' if uberblocks else 'corrupt_label_rejection_observed': True,
              'pool_import_attempted': uberblocks,
            'readonly_data_readback': False, 'readonly_pool_retired': False,
            'guest_reclaim_qualified': False, 'reclaimed': 0, 'terminal_detail': 873,
            'cleanup_trace_version': 1, 'partial_cleanup_phases': [1, 2]}
    if uberblocks:
        result['original_import_errno'] = 6
    return result


def check_pool_cleanup_trace(serial):
    """Private v1 checkpoints observe cleanup boundaries, never partial acceptance."""
    pattern = (r'^NATIVE CLEANUP v=1 slot=(\d+) generation=(\d+) phase=(\d+) '
               r'selected=(\d+) pages=(\d+) reclaimed=(\d+)$')
    rows = [tuple(map(int, row)) for row in re.findall(pattern, serial, re.M)]
    expected = [(0, generation, phase, 0 if phase == 1 else 2, 8192,
                 generation if phase == 7 else generation - 1)
                for generation in (1, 2, 3) for phase in range(1, 8)]
    if rows != expected or serial.count('NATIVE CLEANUP ') != len(expected):
        raise ValueError('pool cleanup v1 identity/phase/resource sequence')
    lines = serial.splitlines()
    previous = -1
    for generation in (1, 2, 3):
        terminal = f'NATIVE terminal slot=0 generation={generation} kind=1 detail=0'
        try:
            position = lines.index(terminal)
        except ValueError:
            raise ValueError('pool cleanup v1 terminal boundary') from None
        if position <= previous:
            raise ValueError('pool cleanup v1 terminal order')
        for row in expected[(generation - 1) * 7:generation * 7]:
            slot, gen, phase, selected, pages, reclaimed = row
            line = (f'NATIVE CLEANUP v=1 slot={slot} generation={gen} phase={phase} '
                    f'selected={selected} pages={pages} reclaimed={reclaimed}')
            next_position = lines.index(line)
            if next_position <= position:
                raise ValueError('pool cleanup v1 operation order')
            position = next_position
        previous = position
    final = 'NATIVE supervisor result=100 reclaimed=3'
    if lines.count(final) != 1 or lines.index(final) <= previous:
        raise ValueError('pool cleanup v1 final reclaim missing')
    return {'cleanup_trace_version': 1, 'cleanup_boundaries_per_generation': 7}


def check_namespace_trace(serial):
    # Canonical readonly trace plus one success observation, after complete SHA256
    # verification and context closure. Remove it only after exact row validation.
    rows = re.findall(r'^NATIVE observation slot=(\d+) generation=(\d+) offset=(\d+) byte=(\d+)$', serial, re.M)
    if len(rows) != sum(line.startswith('NATIVE observation ') for line in serial.splitlines()):
        raise ValueError('namespace malformed observation')
    primary = [tuple(map(int, row)) for row in rows if row[1] == '1']
    tags = b'BIUVWLP????????OAMZDJFR'
    if len(primary) != len(tags) or any(slot != 0 or generation != 1 or offset != i * 8 or
            (not 7 <= i < 15 and byte != tags[i])
            for i, (slot, generation, offset, byte) in enumerate(primary)):
        raise ValueError('namespace observation order, identity or full-read success')
    # The existing checker owns resource/cleanup interpretation. Adapt only the
    # checked extra row; preserve every other byte and malformed line for denial.
    lines = []
    for line in serial.splitlines():
        match = re.fullmatch(r'NATIVE observation slot=0 generation=1 offset=(\d+) byte=(\d+)', line)
        if match and int(match[1]) == 144:
            continue
        if match and int(match[1]) > 144:
            line = f'NATIVE observation slot=0 generation=1 offset={int(match[1]) - 8} byte={match[2]}'
        lines.append(line)
    result = check_pool_import_trace('\n'.join(lines))
    return {**result, 'namespace_bytes_verified': 780248, 'namespace_primary_rows': len(tags)}


def check_zpl_write_trace(serial, stage_diagnostic=False, first_write=False, txg_worker=False, sync_stages=False):
    if sync_stages and not txg_worker:
        raise ValueError("sync stages require worker profile")
    """Private writer shape; cleanup/terminal checks remain separately required."""
    observations = [line for line in serial.splitlines()
                    if line.startswith('NATIVE observation ')]
    pattern = r'NATIVE observation slot=\d+ generation=\d+ offset=\d+ byte=\d+'
    if any(re.fullmatch(pattern, line) is None for line in observations):
        raise ValueError('ZPL writer malformed observation')
    result = check_pool_import_trace(serial, pool_data=True, zpl_stages=stage_diagnostic, first_write=first_write, txg_worker=txg_worker, sync_stages=sync_stages)
    target = result['recovered_target_txg']
    if target <= 782:
        raise ValueError('ZPL writer assigned target must advance original fixture')
    return {'assigned_target_txg': target, 'namespace_bytes_verified': 780248,
            'namespace_primary_rows': 32, 'ordered_provider_witness': True,
            'assigned_DMU_transaction': True, 'clean_export_observed': True,
            **({'stage_boundaries_observed': result['stage_boundaries_observed']} if stage_diagnostic else
               {'input_xdr_fnv1a64': result['input_xdr_fnv1a64']}),
            'denied_owner_generations': result['denied_owner_generations'],
            'resource_scope': 'phase observations only; not peak memory or full stack'}


def check_zpl_recovery_trace(serial):
    # Same bounded phase shape, different meaning: loaded pool TXG, not assigned
    # application transaction. Matching writer comparison is a separate gate.
    check_zpl_write_trace(serial)
    result = check_pool_import_trace(serial, pool_data=True)
    txg = result.pop('recovered_target_txg')
    return {**result, 'recovered_pool_txg': txg,
            'namespace_bytes_verified': 780248, 'namespace_primary_rows': 32}


def check_zpl_recovery_media(writer, disk):
    """Prior qualified writer outcome plus stopped-VM byte identity, not a retry."""
    required = {'name': 'pool-import', 'status': 'pass', 'generations': 3,
                'reclaimed': 3, 'final_live_workers': 0, 'cleanup_trace_version': 1,
                'cleanup_boundaries_per_generation': 7}
    target = writer.get('assigned_target_txg')
    if (any(writer.get(k) != v for k, v in required.items()) or
            any(writer.get(k) is not True for k in (
                'vm_run_returned', 'assigned_DMU_transaction',
                'ordered_provider_witness', 'clean_export_observed')) or
            type(target) is not int or not 782 < target <= 0xffffffffffffffff):
        raise ValueError('ZPL recovery requires qualified clean stopped writer')
    digest = writer.get('disk_sha256')
    if digest is None:
        raise ValueError('ZPL recovery requires sealed writer media')
    from openzfs_namespace import written_native_media_snapshot
    return written_native_media_snapshot(disk, digest)


def check_zpl_recovery_pair(writer, reader, expected_bytes=780248):
    """Compare qualified VM outcomes; byte snapshots are required on both sides."""
    for outcome in (writer, reader):
        if (outcome.get('status') != 'pass' or outcome.get('vm_run_returned') is not True or
                outcome.get('reclaimed') != 3 or outcome.get('generations') != 3 or
                outcome.get('final_live_workers') != 0 or
                outcome.get('cleanup_trace_version') != 1 or
                outcome.get('cleanup_boundaries_per_generation') != 7):
            raise ValueError('ZPL recovery pair requires clean stopped VM outcomes')
    assigned, recovered = writer.get('assigned_target_txg'), reader.get('recovered_pool_txg')
    if (type(assigned) is not int or type(recovered) is not int or
            not 782 < assigned <= recovered <= 0xffffffffffffffff or
            any(writer.get(k) is not True for k in (
                'assigned_DMU_transaction', 'ordered_provider_witness', 'clean_export_observed')) or
            reader.get('readonly_pool_retired') is not True or
            type(expected_bytes) is not int or expected_bytes < 0 or
            reader.get('namespace_bytes_verified') != expected_bytes or
            not writer.get('disk_sha256') or
            writer.get('disk_sha256') != reader.get('disk_sha256')):
        raise ValueError('ZPL recovery pair target/data/media mismatch')
    return {'assigned_target_txg': assigned, 'recovered_pool_txg': recovered,
            'fresh_vm_readback_qualified': True, 'reader_media_unchanged': True}


def pool_media_snapshot(path):
    """Read owned disposable media before cleanup, including failed runs."""
    if path.is_symlink() or not path.is_file():
        return {'status': 'unavailable'}
    with path.open('rb') as stream:
        digest = hashlib.sha256()
        size = 0
        first = stream.read(4096)
        digest.update(first)
        size += len(first)
        last = first
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
            size += len(chunk)
            last = (last + chunk)[-4096:]
    return {'status': 'captured', 'bytes': size, 'sha256': digest.hexdigest(),
            'outside_region_canaries_match': size == 64 * 1024 * 1024 + 8192 and
                first == bytes([165]) * 4096 and last == bytes([165]) * 4096,
            'scope': 'host final bytes only; no flush, export or retirement proof'}


def pool_diagnostic_driver(text):
    """The raw emitter proof carries padding, not sampled resource counters."""
    anchor = '            let live = byte(owner, offset + 1);'
    if text.count(anchor) != 1 or text.count('let observed = byte(owner, offset);') != 1:
        raise ValueError('pool diagnostic supervisor context changed')
    guard = '''            if cfg!(pool_create) && !cfg!(pool_import) && stale == 0 && stage == 14 {
                check(observed == b'C');
                for n in 1..8 {
                    check(byte(owner, offset + n) == 0);
                }
                continue;
            }
'''
    return text.replace(anchor, guard + anchor, 1)


def physical_expected_disk(before, case):
    if case in WRITE_CASES and case != 'spa-physical-write-verify':
        expected = bytearray(before)
        offset = 4096 + 1048576
        expected[offset:offset + 512] = bytes((i * 17 + 91) & 255 for i in range(512))
        return bytes(expected)
    return before


def display(value):
    return ''.join(f'\\x{ord(c):02x}' if ord(c) < 32 or ord(c) == 127 else c
                   for c in str(value))


class IntakeParser(Parser):
    def error(self, message):
        super().error(display(message))


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def sealed(root, expected, count):
    """Check path/type before hashing: manifests are inert data, never code."""
    from fs_host_dependencies import retained_root
    root = retained_root(Path(root).absolute())
    if root.is_symlink() or (root / 'SHA256SUMS').is_symlink():
        raise ValueError('symlink seal root')
    seal = root / 'SHA256SUMS'
    if seal.stat().st_size > 1024 * 1024 or sha(seal) != expected:
        raise ValueError('seal digest')
    files = {}
    for line in seal.read_text().splitlines():
        if not re.fullmatch(r'[0-9a-f]{64}  [^\s]+', line):
            raise ValueError('seal syntax')
        digest, name = line.split('  ', 1)
        path = PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts or str(path) != name or name in files:
            raise ValueError('seal path')
        target = root
        for part in path.parts:
            target /= part
            if target.is_symlink():
                raise ValueError('seal symlink')
        if not target.is_file() or sha(target) != digest:
            raise ValueError('seal member: ' + name)
        files[name] = digest
    if len(files) != count:
        raise ValueError('seal member count')
    return files


def intake(delivery, fixed_reaper=False):
    seal = FIXED_SEAL if fixed_reaper else SEAL
    archive = FIXED_ARCHIVE if fixed_reaper else ARCHIVE
    dependency = ROOT / '.deps/native-service-runtime-v3' if fixed_reaper else DEPENDENCY
    members = sealed(delivery, seal, 294 if fixed_reaper else 282)
    base = sealed(Path(delivery) / 'sdk',
                  'f6bc6d6da3b051e1e4617e60ae256cbd35d193b608631ac29f7c42dbe73b13dc', 240)
    if any(sha(BASE / n) != h for n, h in base.items()):
        raise ValueError('current guarded SDK differs from delivery')
    selected = {n: h for n, h in members.items()
                if n.startswith(('source/', 'runtime/')) or n in ('OWNER.md', 'link.json', 'tools.lock.json')}
    if dependency.exists():
        if dependency.is_symlink():
            raise ValueError('dependency symlink')
        for n, h in selected.items():
            target = dependency / n
            if any(p.is_symlink() for p in (target, *target.parents)) or sha(target) != h:
                raise ValueError('retained dependency changed: ' + n)
        actual = {str(p.relative_to(dependency)) for p in dependency.rglob('*') if p.is_file()}
        if actual != set(selected) | {'intake.json'}:
            raise ValueError('retained dependency inventory')
    else:
        dependency.mkdir()
        for n in selected:
            target = dependency / n
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(Path(delivery) / n, target)
        (dependency / 'intake.json').write_text(json.dumps({
            'delivery_seal': seal, 'members_verified': len(members),
            'base_members_verified': len(base), 'files': selected,
            'base': str(BASE), 'promotion': False,
        }, indent=2) + '\n')
    # A sibling may change between verification and copying. Verify retained
    # bytes before any copied build recipe is executed, not just after a run.
    for n, h in selected.items():
        target = dependency / n
        if any(p.is_symlink() for p in (target, *target.parents)) or sha(target) != h:
            raise ValueError('retained dependency changed: ' + n)
    if sha(dependency / 'runtime/libaether_runtime.a') != archive:
        raise ValueError('runtime archive')
    return selected



def intake_utc(delivery, fixed_reaper=False):
    seal = FIXED_SEAL if fixed_reaper else SEAL
    utc_seal = FIXED_UTC_SEAL if fixed_reaper else UTC_SEAL
    utc_archive = FIXED_UTC_ARCHIVE if fixed_reaper else UTC_ARCHIVE
    utc_dependency = ROOT / '.deps/native-utc-v3' if fixed_reaper else UTC_DEPENDENCY
    members = sealed(delivery, utc_seal, 343 if fixed_reaper else 314)
    sealed(Path(delivery) / 'base', seal, 294 if fixed_reaper else 282)
    base = sealed(Path(delivery) / 'base/sdk',
                  'f6bc6d6da3b051e1e4617e60ae256cbd35d193b608631ac29f7c42dbe73b13dc', 240)
    if any(sha(BASE / n) != h for n, h in base.items()):
        raise ValueError('UTC guarded SDK differs')
    if utc_dependency.exists():
        if utc_dependency.is_symlink():
            raise ValueError('UTC dependency symlink')
    else:
        utc_dependency.mkdir()
        for n in (*members, 'SHA256SUMS'):
            target = utc_dependency / n
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(Path(delivery) / n, target)
    # Revalidate the copied seal/members before executing the copied recipe.
    if sealed(utc_dependency, utc_seal, 343 if fixed_reaper else 314) != members:
        raise ValueError('retained UTC input changed')
    actual = {str(p.relative_to(utc_dependency)) for p in utc_dependency.rglob('*') if p.is_file()}
    if actual != set(members) | {'SHA256SUMS'}:
        raise ValueError('retained UTC inventory')
    if sha(utc_dependency / 'runtime/libaether_runtime.a') != utc_archive:
        raise ValueError('UTC runtime archive')
    return members

def check_trace(serial, stopped=False, marker='AETHER NATIVE SUPERVISION PASS'):
    terminals = re.findall(r'^NATIVE terminal slot=(\d+) generation=(\d+) kind=(\d+) detail=(\d+)$', serial, re.M)
    # Explicit stop has no ordinary terminal line. The source-bound supervisor
    # checks returned detail143/kind3 before reclaim and replacement.
    expected = [('1', '1', '1', '0'), ('0', '2', '1', '0')]
    if not stopped:
        expected.append(('0', '1', '1', '0'))
    if sorted(terminals) != sorted(expected):
        raise ValueError('runtime terminals do not match owner generations')
    if serial.count('NATIVE supervisor result=100 reclaimed=3\n') != 1:
        raise ValueError('runtime reclaim accounting')
    if serial.count(marker + '\n') != 1:
        raise ValueError('runtime supervision marker')
    return {'terminals': terminals, 'reclaimed': 3}


def check_reaper_bindings(mapping, symbols):
    # LLD omits the wrapped original from its map's symbol rows. Match its
    # final ELF address to exactly one input text range instead of accepting
    # an archive merely because it appears somewhere in the link.
    sections = []
    for line in mapping.splitlines():
        match = re.match(r'^\s*([0-9a-f]+)\s+[0-9a-f]+\s+([0-9a-f]+)\s+\d+\s+(.+):\((\.text[^)]*)\)$', line)
        if match:
            sections.append((int(match[1], 16), int(match[2], 16), match[3]))
    origins = {}
    for symbol, suffix in [('__wrap___unmapself', 'probe.o'),
                           ('__wrap___tl_lock', 'probe.o'),
                           ('__tl_lock', 'libaether_runtime.a(pthread.o)'),
                           ('__unmapself', 'libaether_runtime.a(backend.o)'),
                           ('reap', 'libaether_runtime.a(backend.o)')]:
        addresses = re.findall(r'^([0-9a-f]+) [tT] ' + re.escape(symbol) + r'$', symbols, re.M)
        if len(addresses) != 1:
            raise ValueError('maintained reaper symbol absent/duplicated: ' + symbol)
        address = int(addresses[0], 16)
        owners = [owner for base, size, owner in sections if base <= address < base + size]
        if len(owners) != 1 or not owners[0].endswith('/' + suffix):
            raise ValueError('maintained reaper origin mismatch: ' + symbol)
        origins[symbol] = owners[0]
    return origins


def check_callers(mapping):
    callers = ['cv_init', 'cv_timedwait_hires', 'mutex_enter', 'mutex_exit']
    for symbol in callers:
        if not re.search(r'kernel\.c-native\.o:\(\.text\.' + symbol + r'\)', mapping):
            raise ValueError('actual OpenZFS caller missing: ' + symbol)
    return callers


def check_engine_bindings(mapping, startup=False, volume=False, workers=False, spa_utc=False, utc=False, spa_active=False, spa_physical=False, spa_write=False, pool=False, diagnostics=False, pool_import=False, pool_data=False, pool_interrupt=False, pool_uncommitted=False, pool_recovery_check=None, pool_namespace=False, pool_zpl_write=False, pool_zpl_recover=False, txg_worker=False, fs_bridge=False, zpl_zero=False, namespace_mutation=None, fs_service=False, fs_service_case='normal', fs_service_lifetimes=False, fs_service_namespace=False, fs_service_mixed=False, fs_service_wait=False, fs_service_bulk=False, fs_service_runtime=False, fs_service_activation=False, fs_service_names=False, fs_service_directories=False):
    """Read LLD's input-section attribution, not just a list of symbol names."""
    required = {
        'main': 'engine-startup.o',
        'kernel_init': 'selected-engine.o', 'kernel_fini': 'selected-engine.o',
        'cv_init': 'selected-engine.o', 'cv_timedwait_hires': 'selected-engine.o',
        'random_init': 'selected-engine.o', 'random_get_bytes': 'selected-engine.o',
        'arc_all_memory': 'selected-engine.o', 'arc_available_memory': 'selected-engine.o',
        'aether_zfs_granted_pages': 'selected-engine.o',
        'aether_zfs_assigned_cpus': 'selected-engine.o',
        'aether_runtime_init': 'libaether_runtime.a(backend.o)',
        'aether_runtime_finish': 'libaether_runtime.a(backend.o)',
        '__aether_io': 'libaether_runtime.a(backend.o)',
    }
    if startup:
        required.update({s: 'selected-engine.o' for s in
                         ('aether_zfs_startup_bind', 'aether_zfs_hostid',
                          'aether_zfs_uname', 'aether_zfs_empty_cache')})
    if volume:
        required.update({s: 'selected-engine.o' for s in
                         ('vdev_file_ops', 'zfs_file_open', 'zfs_file_pread',
                          'zfs_file_pwrite', 'zfs_file_fsync', 'aether_zfs_volume_bind')})
        required.update({s: 'volume-probe.o' for s in
                         ('aether_volume_start_probe', 'aether_volume_engine_probe', 'aether_volume_finish_probe')})
        required.update({s: None for s in
                         ('aether_volume_bind', 'aether_volume_check', 'aether_volume_io', 'aether_volume_flush')})
    if spa_utc:
        required.update({s: 'selected-engine.o' for s in
                         ('spa_add', 'spa_remove', 'spa_namespace_enter', '__zfs_dbgmsg')})
        required.update({s: 'spa-utc-probe.o' for s in
                         ('aether_volume_spa_utc_probe', '__wrap__Exit', '__wrap_clock_gettime')})
    if utc:
        required.update({s: 'selected-engine.o' for s in
                         ('spa_add', 'spa_remove', 'spa_namespace_enter', '__zfs_dbgmsg',
                          'taskq_create', 'taskq_dispatch', 'taskq_wait', 'taskq_destroy', 'taskq_of_curthread')})
        required.update({s: 'volume-utc-probe.o' for s in
                         ('aether_engine_utc_start', 'aether_engine_utc_probe', 'aether_engine_utc_finish')})
        required.update({s: 'libaether_runtime.a(utc.o)' for s in
                         ('aether_utc_establish', 'aether_utc_read', 'aether_utc_close')})
        required.update({'clock_gettime': 'libaether_runtime.a(real_time.o)',
                         'time': 'libaether_runtime.a(wrappers.o)',
                         'gettimeofday': 'libaether_runtime.a(wrappers.o)'})
    if spa_active:
        required.update({s: 'selected-engine.o' for s in
                         ('aether_spa_active_probe', 'aether_root_done', 'spa_activate', 'spa_deactivate', 'zio_root', 'zio_wait', 'metaslab_class_create', 'metaslab_class_destroy')})
    if spa_physical:
        required.update({s: 'engine-startup.o' for s in
                         ('aether_engine_utc_phase', 'aether_physical_io_phase')})
        required.update({s: 'selected-engine.o' for s in
                         ('aether_spa_physical_probe', 'aether_physical_done', 'aether_physical_pread_original', 'spa_activate', 'spa_deactivate',
                          'vdev_alloc', 'vdev_open', 'vdev_free', 'zio_read_phys', 'zio_wait',
                          'vdev_file_io_start', 'vdev_file_io_strategy', 'zio_delay_interrupt',
                          'abd_get_from_buf', 'abd_free')})
    if txg_worker:
        required['aether_pool_worker_phase'] = 'engine-startup.o'
    if pool:
        required['aether_engine_utc_phase'] = 'engine-startup.o'
        required.update({s: 'selected-engine.o' for s in
                         ('aether_pool_prepare', 'aether_spa_pool_probe', 'spa_create',
                          'spa_export', 'spa_open', 'spa_close', 'spa_feature_is_enabled',
                          'aether_pool_hooks_prepare', 'aether_pool_hooks_check',
                          'aether_pool_root_begin', 'aether_pool_root_end',
                          'aether_pool_zio_child', 'aether_pool_zio_retire',
                          'aether_pool_write_requested', 'aether_pool_flush_requested',
                          'aether_pool_txg_observe', 'aether_pool_sync_observe',
                          'aether_pool_io_begin', 'aether_pool_provider_done',
                          'aether_pool_leaf_done', 'nvlist_pack')})
        if pool_import:
            for symbol in ('aether_pool_prepare', 'aether_spa_pool_probe', 'spa_create',
                           'aether_pool_hooks_prepare', 'aether_pool_hooks_check'):
                required.pop(symbol)
            required.update({s: 'selected-engine.o' for s in
                             ('aether_spa_import_probe', 'spa_import', 'aether_pool_label_read',
                              'aether_pool_label_config', 'zap_lookup')})
    if pool_interrupt and not pool_import:
        required['aether_engine_pool_checkpoint'] = 'engine-startup.o'
        if pool_uncommitted:
            required['aether_engine_pool_uncommitted'] = 'engine-startup.o'
            required['aether_pool_data_hold'] = 'selected-engine.o'
    if pool_recovery_check == 'capacity' and not pool_import:
        required['aether_pool_data_capacity'] = 'selected-engine.o'
        required.update({symbol: 'selected-engine.o' for symbol in
                         ('dsl_dataset_set_refreservation', 'dsl_get_refreservation', 'dmu_objset_ds')})
    if pool_namespace and not pool_zpl_write:
        required.update({symbol: 'selected-engine.o' for symbol in
                         (*(('aether_pool_namespace_recover',) if pool_zpl_recover else
                            ('aether_pool_namespace_read', 'aether_namespace_owner_probe', 'aether_namespace_hash_update')),
                          'aether_zpl_open', 'aether_zpl_close',
                          'aether_zpl_lookup', 'aether_zpl_read', 'aether_zpl_root',
                          'sa_setup', 'sa_handle_get', 'sa_bulk_lookup', 'sa_handle_destroy',
                          'dmu_objset_own', 'dmu_objset_disown', 'dmu_objset_spa',
                          'dmu_read', 'dmu_object_info', 'dmu_buf_user_evict_wait',
                          'SHA2Init', 'SHA2Update', 'SHA2Final')})
    if pool_zpl_recover and (pool_zpl_write or not (pool_namespace and pool_import)):
        raise ValueError('ZPL recovery origins require namespace import')
    if pool_zpl_recover:
        required.update({symbol: 'selected-engine.o' for symbol in
                         ('spa_evict_all', 'spa_refcount_zero')})
    if fs_service:
        if not pool_zpl_write:
            raise ValueError('filesystem service origins require writer')
        required['aether_fs_directories_run' if fs_service_directories else 'aether_fs_names_run' if fs_service_names else 'aether_fs_activation_run' if fs_service_activation else 'aether_fs_runtime_run' if fs_service_runtime else 'aether_fs_bulk_run' if fs_service_bulk else 'aether_fs_mixed_wait_run' if fs_service_wait else 'aether_fs_mixed_run' if fs_service_mixed else 'aether_fs_namespace_run' if fs_service_namespace else 'aether_fs_service_run'] = 'selected-engine.o'
        if fs_service_lifetimes:
            required['aether_pool_service16_retire'] = 'selected-engine.o'
        from openzfs_fs_service import case_number
        if case_number(fs_service_case) == 3:
            required['__wrap_aether_zpl_close'] = 'selected-engine.o'
    if fs_bridge:
        if not pool_zpl_write:
            raise ValueError('filesystem bridge origins require writer')
        required['aether_fs_policy_write_probe'] = 'selected-engine.o'
    if pool_zpl_write:
        if not (pool_namespace and pool_import):
            raise ValueError('ZPL writer origins require namespace import')
        required.update({symbol: 'selected-engine.o' for symbol in (
            'aether_pool_namespace_write', 'aether_zpl_accounting_init', 'zpl_get_file_info',
            'dmu_objset_register_type', 'aether_pool_prepare', 'aether_pool_hooks_prepare',
            'aether_zpl_open_write', 'aether_zpl_close', 'aether_zpl_root', 'aether_zpl_lookup',
            'aether_zpl_read', 'aether_zpl_write', 'sa_setup', 'sa_handle_get', 'sa_bulk_lookup',
            'sa_bulk_update', 'sa_handle_destroy', 'dmu_objset_own', 'dmu_objset_disown',
            'dmu_objset_spa', 'dmu_read', 'dmu_write', 'dmu_tx_create', 'dmu_tx_hold_sa',
            'dmu_tx_hold_write', 'dmu_tx_assign', 'dmu_tx_get_txg', 'dmu_tx_commit', 'dmu_tx_abort',
            'txg_wait_synced_flags', 'spa_last_synced_txg', 'aether_pool_hooks_bind_transaction',
            'aether_pool_hooks_check_ordered', 'dmu_buf_user_evict_wait',
            'SHA2Init', 'SHA2Update', 'SHA2Final')})
    if fs_service_mixed:
        if not pool_namespace or not pool_import or not (pool_zpl_write or pool_zpl_recover) or namespace_mutation is not None or zpl_zero or fs_bridge:
            raise ValueError('mixed service origins require exclusive namespace import')
        required.update({s:'selected-engine.o' for s in ('dmu_object_next','zap_count')})
        if pool_zpl_write:
            required.update({s:'selected-engine.o' for s in ('aether_zpl_create','aether_zpl_rename','aether_zpl_remove',
                'dmu_object_alloc','dmu_tx_hold_sa_create','sa_replace_all_by_template','zap_add','zap_remove',
                'dmu_object_free','dmu_tx_hold_free','dmu_tx_mark_netfree','dmu_tx_hold_zap','sa_lookup',
                'aether_pool_namespace0_retire','aether_pool_service_bytes_retire' if fs_service_bulk else 'aether_pool_service16_retire')})
    if namespace_mutation is not None:
        from openzfs_mutation import validate
        validate(namespace_mutation)
        if not pool_namespace or not (pool_zpl_write or pool_zpl_recover) or zpl_zero or fs_bridge:
            raise ValueError('namespace mutation origins require exclusive profile')
        if namespace_mutation in ('create', 'rename', 'remove'):
            required.update({symbol: 'selected-engine.o' for symbol in ('dmu_object_next', 'zap_count')})
        if pool_zpl_write:
            if namespace_mutation not in ('extend', 'repeat', 'eight', 'lifetimes'):
                for symbol in ('aether_zpl_write', 'dmu_write', 'dmu_tx_hold_write'):
                    required.pop(symbol)
            selected = {'create': ('dmu_object_alloc', 'dmu_tx_hold_sa_create', 'sa_replace_all_by_template', 'zap_add'),
                        'rename': ('zap_add', 'zap_remove'),
                        'remove': ('zap_remove', 'dmu_object_free', 'dmu_tx_hold_free', 'dmu_tx_mark_netfree', 'sa_update'),
                        'shrink': ('dmu_free_range', 'dmu_tx_hold_free', 'dmu_tx_mark_netfree'),
                        'extend': (), 'repeat': (), 'eight': (), 'lifetimes': ()}[namespace_mutation]
            primitive = 'aether_zpl_write' if namespace_mutation in ('repeat', 'eight', 'lifetimes') else 'aether_zpl_' + namespace_mutation
            required.update({symbol: 'selected-engine.o' for symbol in
                             (primitive, *selected)})
            if namespace_mutation == 'lifetimes':
                required['aether_pool_lifetime_retire'] = 'selected-engine.o'
            if namespace_mutation in ('create', 'rename', 'remove'):
                required.update({symbol: 'selected-engine.o' for symbol in ('dmu_tx_hold_zap', 'sa_lookup')})
    if zpl_zero:
        if not pool_zpl_write or fs_bridge:
            raise ValueError('truncate zero origins require exclusive writer')
        for symbol in ('aether_zpl_write', 'dmu_write', 'dmu_tx_hold_write'):
            required.pop(symbol)
        required.update({symbol: 'selected-engine.o' for symbol in
                         ('aether_zpl_shrink', 'dmu_free_range', 'dmu_tx_hold_free', 'dmu_tx_mark_netfree')})
    if pool_data:
        if not pool:
            raise ValueError('pool data origins require pool selection')
        common = ('dmu_objset_own', 'dmu_objset_disown', 'dmu_objset_spa', 'dmu_read')
        chosen = (('aether_pool_data_read', 'dmu_object_info', 'spa_last_synced_txg', 'dmu_buf_user_evict_wait') if pool_import else
                  ('aether_pool_data_write', 'dmu_objset_create', 'dmu_object_claim',
                   'dmu_tx_create', 'dmu_tx_hold_write', 'dmu_tx_assign', 'dmu_tx_get_txg',
                   'dmu_tx_commit', 'dmu_tx_abort', 'dmu_write', 'txg_wait_synced_flags',
                   'aether_pool_hooks_bind_transaction', 'aether_pool_hooks_check_ordered'))
        required.update({symbol: 'selected-engine.o' for symbol in (*common, *chosen)})
    if spa_write:
        required.update({s: 'selected-engine.o' for s in
                         ('aether_physical_write_probe', 'aether_physical_write_done',
                          'aether_physical_write_begin', 'aether_physical_write_end',
                          'aether_physical_flush_callback', 'aether_physical_pwrite_original',
                          'aether_physical_fsync_provider_original', 'aether_physical_fsync_callback_original',
                          'vdev_file_io_fsync', 'zio_write_phys', 'zio_flush')})
    if workers:
        required.update({s: 'selected-engine.o' for s in
                         ('taskq_create', 'taskq_dispatch', 'taskq_wait', 'taskq_destroy', 'taskq_of_curthread')})
        required.update({s: 'volume-worker-probe.o' for s in
                         ('aether_volume_workers_probe', 'aether_volume_workers_finish')})
    if pool:
        required['system_taskq_init'] = 'selected-engine.o'
        required['system_taskq_fini'] = 'selected-engine.o'
    if diagnostics:
        if not pool:
            raise ValueError('failure origins require pool profile')
        required['aether_pool_failure_site'] = 'selected-engine.o'
        required['aether_pool_failure_allocation'] = 'selected-engine.o'
        required['aether_pool_failure_assertion'] = 'selected-engine.o'
        required['aether_pool_failure_pthread'] = 'selected-engine.o'
        required['aether_pool_failure_denial'] = 'selected-engine.o'
        required['aether_pool_failure_tid'] = 'selected-engine.o'
    if fs_service_directories:
        if not (fs_service_names and ((fs_service and pool_zpl_write) or (not fs_service and pool_zpl_recover))):
            raise ValueError('directories binding requires selected writer or independent recovery')
        if fs_service:
            required.update({n:'selected-engine.o' for n in ('aether_zpl_directory','aether_zpl_mkdir','aether_zpl_rmdir')})
    seen = {}
    owner = None
    for line in mapping.splitlines():
        fields = line.split()
        if len(fields) < 5:
            continue
        entry = fields[-1]
        if ':(' in entry:
            owner = entry.split(':(', 1)[0]
        elif entry in required:
            if entry in seen or owner is None or not (owner.endswith(required[entry]) if required[entry] else '/libaether_volume.a(' in owner):
                raise ValueError('wrong engine symbol origin: ' + entry)
            seen[entry] = owner
    if set(seen) != set(required):
        raise ValueError('missing engine symbol origins: ' + ','.join(sorted(set(required) - set(seen))))
    if any(name in mapping for name in ('zfs-waits.inc', 'kernel.c-native.o', 'engine/adapter.o')):
        raise ValueError('private/old adapter in engine composition')
    return seen


def check_engine_trace(serial, marker="AETHER NATIVE SUPERVISION PASS"):
    terminals = re.findall(r'^NATIVE terminal slot=(\d+) generation=(\d+) kind=(\d+) detail=(\d+)$', serial, re.M)
    if terminals != [('0', str(g), '1', '0') for g in range(1, 4)]:
        raise ValueError('engine owner generations did not finish normally')
    if serial.count('NATIVE supervisor result=100 reclaimed=3\n') != 1 or serial.count(marker + '\n') != 1:
        raise ValueError('engine replacement/reclaim oracle absent')
    return {'generations': 3, 'reclaimed': 3, 'small_peer_image_denial': True,
            'four_checked_observations_per_generation': True,
            'final_live_workers': 0, 'observations_exported': False}


def check_open_probe_trace(serial):
    rows = re.findall(r'^NATIVE observation slot=(\d+) generation=(\d+) offset=(\d+) byte=(\d+)$', serial, re.M)
    if len(rows) != 14 or [(slot, generation, int(offset)) for slot, generation, offset, _ in rows] != [
            ('0', '1', i * 8) for i in range(14)]:
        raise ValueError('open probe observation identity/count/offset mismatch')
    phases = [int(row[3]) for row in rows]
    if phases[:7] != list(b'BIUVWAC') or phases[-1] != ord('O'):
        raise ValueError('open probe prefix/completion absent')
    entered = completed = 0
    for phase in phases[7:-1]:
        if phase == ord('L'):
            entered += 1
        elif phase == ord('M'):
            completed += 1
        else:
            raise ValueError('open probe provider failed or stage unknown')
        if completed > entered:
            raise ValueError('open probe completion precedes entry')
    if entered != 3 or completed != 3:
        raise ValueError('original three open probe reads incomplete')
    if re.findall(r'^NATIVE terminal slot=(\d+) generation=(\d+) kind=(\d+) detail=(\d+)$', serial, re.M) != [('0', '1', '1', '867')]:
        raise ValueError('open probe checkpoint terminal absent')
    rejection = 'NATIVE supervisor result=401 reclaimed=0\n'
    if serial.count(rejection) != 1:
        raise ValueError('open probe checkpoint rejection absent')
    terminal = serial.index('NATIVE terminal slot=0 generation=1 kind=1 detail=867\n')
    if terminal < serial.rfind('NATIVE observation ') or serial.index(rejection) < terminal:
        raise ValueError('open probe checkpoint output order mismatch')
    return {'open_probe_provider_reads': 3, 'open_probe_rows': 14, 'clean_lifetime': False}


def compose_engine(port, command, cc, tools, native=False, control=None, volume=False, workers=False, spa_utc=False, utc=False, runtime=DEPENDENCY, spa_active=False, spa_physical=False, pool=False, diagnostics=False, pool_data=False, pool_interrupt=False, pool_uncommitted=False, pool_recovery_check=None, pool_namespace=False, pool_zpl_write=False, pool_zpl_recover=False, txg_worker=False, fs_bridge=False, zpl_zero=False, namespace_mutation=None, fs_service=False, fs_service_case='normal', fs_service_lifetimes=False, fs_service_namespace=False, fs_service_mixed=False, fs_service_wait=False, fs_service_bulk=False, fs_service_runtime=False, fs_service_activation=False, fs_service_names=False, fs_service_directories=False):
    from openzfs_elapsed import CURRENT, OWNED
    controls = {'no-fini': '-DENGINE_SKIP_FINI', 'no-finish': '-DENGINE_SKIP_FINISH',
                'write-mode': '-DENGINE_WRITE_MODE'}
    utc_base = '2000-02-29T12:34:00' if control in ('utc-leap', 'utc-reuse', 'utc-reuse-short') else '2026-10-06T12:34:00'
    utc_seconds = int(datetime.fromisoformat(utc_base).replace(tzinfo=timezone.utc).timestamp())
    if pool_zpl_recover and (pool_zpl_write or not (pool_namespace and pool and control == 'pool-import')):
        raise ValueError('ZPL recovery composition requires isolated namespace import')
    if pool_zpl_write and not (pool_namespace and pool and control == 'pool-import'):
        raise ValueError('ZPL writer composition requires namespace import')
    startup_source = SOURCE / 'engine-startup.c'
    if txg_worker:
        if not (native and pool_zpl_write):
            raise ValueError('TXG worker publisher requires native writer')
        from openzfs_pool import worker_publisher
        startup_source = port / 'engine-worker-startup.c'
        startup_source.write_text(worker_publisher((SOURCE / 'engine-startup.c').read_text()))
    command(cc + (['-DENGINE_ZPL_WRITE', '-DENGINE_WRITE_MODE'] if pool_zpl_write else []) + (['-DENGINE_POOL_INTERRUPT'] if pool_interrupt and control != 'pool-import' else []) +
            (['-DENGINE_POOL_UNCOMMITTED'] if pool_uncommitted and control != 'pool-import' else []) +
            (['-DENGINE_POOL'] if pool else []) +
            (['-DENGINE_POOL_IMPORT'] if control == 'pool-import' else []) + (['-DENGINE_SPA_PHYSICAL',
                   '-DSPA_PHYSICAL_SMALL=' + str(int(control == 'spa-physical-small')),
                   '-DSPA_PHYSICAL_SKIP_CALLBACK=' + str(WRITE_CASES.index(control) if control in WRITE_CASES else 2 if control == 'spa-physical-open-checkpoint' else int(control == 'spa-physical-no-callback')),
                   '-DSPA_PHYSICAL_REVOKED=' + str(int(control == 'spa-physical-revoked'))] if spa_physical else []) +
            (['-DENGINE_SPA_ACTIVE',
                   '-DSPA_SKIP_ACTIVATION=' + str(int(control == 'spa-active-no-activation')),
                   '-DSPA_SKIP_CALLBACK=' + str(int(control == 'spa-active-no-callback'))] if spa_active else []) +
            (['-DENGINE_UTC', '-DUTC_POLICY=' + str(int(control != 'utc-policy')),
                   '-DUTC_DISABLED=' + str(int(control == 'utc-disabled')),
                   '-DUTC_SECONDS=' + str(utc_seconds),
                   '-DUTC_CYCLES=' + str(7 if control == 'utc-reuse-short' else 8 if control == 'utc-reuse' else 1)] if utc else []) +
            (['-DENGINE_SPA_UTC', '-DUTC_SKIP_OBSERVER=' + str(int(control == 'spa-utc-no-observer'))] if spa_utc else []) +
            (['-DENGINE_VOLUME_WORKERS', '-DWORKERS_INLINE=' + str(int(control == 'block-workers-inline'))] if workers else []) +
            (['-DENGINE_VOLUME', *([] if control == 'pool-import' else ['-DENGINE_WRITE_MODE']),
                   '-DBLOCK_VERIFY=' + str(int(control in ('block-verify', 'block-corrupt'))),
                   '-DBLOCK_READONLY=' + str(int(volume_readonly(control) and not pool_zpl_write))] if volume else []) +
            (['-DENGINE_NATIVE'] if native else []) +
            ([controls[control]] if control in controls else []) +
            ['-I', OWNED, *(['-I', SOURCE] if txg_worker else []), '-c', startup_source, '-o', port / 'engine-startup.o'],
            port / 'startup.log')
    link = [tools['lld']['path'], '-static', '-z', 'noexecstack', '--no-undefined',
            '--gc-sections', '-z', 'nostart-stop-gc',
            *(['--wrap=_Exit', '--wrap=clock_gettime'] if spa_utc else []),
            BASE / 'stage/usr/lib/crt1.o', BASE / 'stage/usr/lib/crti.o',
            port / 'engine-startup.o', port / 'selected-engine.o',
            *([port / 'volume-probe.o', port / 'libaether_volume.a'] if volume else []),
            *([port / 'volume-worker-probe.o'] if workers else []),
            *([port / 'spa-utc-probe.o'] if spa_utc else []),
            *([port / 'volume-utc-probe.o'] if utc else []),
            '--whole-archive', (port / 'failure-runtime/libaether_runtime.a' if diagnostics else runtime / 'runtime/libaether_runtime.a'), '--no-whole-archive',
            BASE / 'stage/usr/lib/libc.a', BASE / 'stage/usr/lib/crtn.o']
    if pool:
        # The compiler may inline the thin original spa_export wrapper. Keep
        # its emitted original body for identity inspection, not as a call trace.
        link += ['--undefined=spa_export']
        if namespace_mutation is not None:
            keep = ['aether_zpl_close', 'aether_zpl_read', 'aether_zpl_root', 'aether_zpl_lookup']
            if pool_zpl_write:
                primitive = 'aether_zpl_write' if namespace_mutation in ('repeat', 'eight', 'lifetimes') else 'aether_zpl_' + namespace_mutation
                keep += ['aether_zpl_open_write', primitive]
                if namespace_mutation == 'lifetimes':
                    keep += ['aether_pool_lifetime_retire']
            link += ['--undefined=' + symbol for symbol in keep]
        if zpl_zero:
            link += ['--undefined=' + symbol for symbol in
                     ('aether_zpl_shrink', 'aether_zpl_open_write', 'aether_zpl_close',
                      'aether_zpl_read', 'aether_zpl_root', 'aether_zpl_lookup')]
        if pool_zpl_recover:
            # The probe shares the reader's private context in one translation
            # unit, so Clang may inline and GC these existing FFI definitions.
            # Retain their original bodies for origin inspection, not as proof
            # of out-of-line calls; executed inlined code uses the same sources.
            link += ['--undefined=' + symbol for symbol in
                     ('aether_zpl_close', 'aether_zpl_read', 'aether_zpl_root')]
        if pool_data:
            link += ['--undefined=' + ('aether_pool_data_read' if control == 'pool-import' else 'aether_pool_data_write')]
        if pool_uncommitted and control != 'pool-import':
            link += ['--undefined=aether_pool_data_hold']
        if pool_recovery_check == 'capacity' and control != 'pool-import':
            link += ['--undefined=aether_pool_data_capacity']
        if control == 'pool-import':
            link += ['--undefined=spa_import']
    if control in ('no-fini', 'no-finish'):
        # Preserve both actual function origins while deliberately skipping a call.
        link += ['-u', 'kernel_fini', '-u', 'aether_runtime_finish']
    command(link + ['-Map=' + str(port / 'engine.map'), '-o', port / 'engine.elf'],
            port / 'engine-link.log')
    bindings = check_engine_bindings((port / 'engine.map').read_text(), startup=True, volume=volume, workers=workers, spa_utc=spa_utc, utc=utc, spa_active=spa_active, spa_physical=spa_physical, spa_write=control in WRITE_CASES, pool=pool, diagnostics=diagnostics, pool_import=control == 'pool-import', pool_data=pool_data, pool_interrupt=pool_interrupt, pool_uncommitted=pool_uncommitted, pool_recovery_check=pool_recovery_check, pool_namespace=pool_namespace, pool_zpl_write=pool_zpl_write, pool_zpl_recover=pool_zpl_recover, txg_worker=txg_worker, fs_bridge=fs_bridge, zpl_zero=zpl_zero, namespace_mutation=namespace_mutation, fs_service=fs_service, fs_service_case=fs_service_case, fs_service_lifetimes=fs_service_lifetimes, fs_service_namespace=fs_service_namespace, fs_service_mixed=fs_service_mixed,fs_service_wait=fs_service_wait,fs_service_bulk=fs_service_bulk,fs_service_runtime=fs_service_runtime,fs_service_activation=fs_service_activation,fs_service_names=fs_service_names,fs_service_directories=fs_service_directories)
    if volume:
        without_volume = [p for p in link if p != port / 'libaether_volume.a']
        command(without_volume + ['-o', port / 'volume-omitted.elf'],
                port / 'volume-omitted.log', rejection='undefined symbol: aether_volume_bind')
    command(link + [CURRENT / 'engine/adapter.o', '-o', port / 'overlap.elf'],
            port / 'overlap.log', rejection='duplicate symbol: __aether_io')
    omitted = link.copy()
    index = omitted.index('--whole-archive')
    del omitted[index:index + 3]
    command(omitted + ['-o', port / 'omitted.elf'], port / 'omitted.log',
            rejection='undefined symbol: aether_runtime_init')
    nm = Path(tools['clang']['path']).parent / 'llvm-nm'
    command([nm, '--undefined-only', port / 'engine.elf'], port / 'engine-imports.log')
    if any(line.split()[-1] != '_DYNAMIC' for line in (port / 'engine-imports.log').read_text().splitlines() if line.strip()):
        raise ValueError('unresolved engine import')
    readelf = nm.parent / 'llvm-readelf'
    command([readelf, '-rW', port / 'engine.elf'], port / 'engine-relocations.log')
    if (port / 'engine-relocations.log').read_text().strip() != 'There are no relocations in this file.':
        raise ValueError('engine static relocations')
    command([readelf, '-lW', port / 'engine.elf'], port / 'engine-segments.log')
    # Execute the actual kernel parser on host bytes, never the engine. This is
    # structural loader evidence, not native admission or resource fit.
    checker = port / 'image-check.zig'
    checker.write_text('''const std = @import("std");
const elf = @import("native_elf");
pub fn main() !void {
    const bytes = @embedFile("engine.elf");
    const image = try elf.parseWithLimits(bytes, elf.large_limits);
    if (elf.parse(bytes)) |_| return error.OldProfileAccepted else |err| {
        if (err != error.InvalidImage) return err;
    }
    var pages: usize = 16;
    for (image.segments[0..image.count]) |s|
        pages += (s.address % 4096 + s.memsz + 4095) / 4096;
    std.debug.print("ELF structural pages={d} segments={d} entry={x}\\n", .{pages, image.count, image.entry});
}
''')
    command(['zig', 'run', '--cache-dir', ROOT / '.zig-cache', '--global-cache-dir',
             ROOT / '.zig-cache/global', '-O', 'ReleaseSafe', '--dep', 'native_elf',
             '-Mroot=' + str(checker), '-Mnative_elf=' + str(ROOT / 'kernel/native_elf.zig')],
            port / 'image-check.log')
    return {'elf_sha256': sha(port / 'engine.elf'), 'elf_bytes': (port / 'engine.elf').stat().st_size,
            'startup_object_sha256': sha(port / 'engine-startup.o'),
            'map_sha256': sha(port / 'engine.map'), 'bindings': bindings,
            'image_checker_sha256': sha(checker),
            'structural_loader': (port / 'image-check.log').read_text().strip(),
            'old_adapter_overlap_rejected': True, 'runtime_omission_rejected': True,
            'engine_entry_executed': False}


def namespace_driver(text, writable=False, recover=False, stages=False, first_write=False, txg_worker=False, sync_stages=False):
    if sync_stages and not txg_worker:
        raise ValueError("sync stages require worker profile")
    """Select one fixed region; retain ABI14 and the existing output capacity."""
    if txg_worker and (not stages or first_write):
        raise ValueError('TXG worker controller requires exclusive stage profile')
    if first_write and not stages:
        raise ValueError('first-write controller requires stage profile')
    if stages and not (writable and not recover):
        raise ValueError('stage diagnostic requires writer controller')
    if writable and recover:
        raise ValueError('namespace writer/recovery controllers are exclusive')
    old_region = ('let region = [8u64, if cfg!(physical_small) { 16384 } else { 131072 }, '
                  'if cfg!(pool_create) { if cfg!(pool_import) { 1 } else { 7 } } '
                  'else if cfg!(physical_write) { if cfg!(physical_no_flush_rights) '
                  '{ 3 } else { 7 } } else { 1 }];')
    old_tags = 'b"BIUVWLP????????OAMDJFR"'
    if text.count(old_region) != 1 or text.count(old_tags) != 1:
        raise ValueError('namespace supervisor region/phase context changed')
    text = text.replace(old_region, 'let region = [8u64, 2097152, 7];' if writable
                        else old_region.replace('else { 131072 }', 'else { 2097152 }'), 1)
    text = text.replace(old_tags, 'b"BIUVWLP????????OAMT????????SDJFR"' if writable or recover
                        else 'b"BIUVWLP????????OAMZDJFR"', 1)
    if not (writable or recover):
        return text
    if stages:
        text = text.replace('b"BIUVWLP????????OAMT????????SDJFR"',
                            'b"BIUVWLPOAMTbeicpvrw????????SDJFR"' if sync_stages else 'b"BIUVWLPOAMTbqsluodw????????SDJFR"' if txg_worker else 'b"BIUVWLPOAMTeabcdwsf????????SDJFR"' if first_write else 'b"BIUVWLPOAMTorhc12vx????????SDJFR"', 1)
    old = '(7..15).contains(&stage)'
    end = '        check(call(0x20003, owner, tags.len() as u64 * 8).0 == -11);'
    if text.count(old) != 1 or text.count(end) != 1:
        raise ValueError('ZPL writer supervisor target context changed')
    text = text.replace(old, '(19..27).contains(&stage)' if stages else old + ' || (19..27).contains(&stage)', 1)
    target_check = '''        if stale == 0 {
            let mut target = 0u64;
            for i in 0..8 {
                target |= (byte(owner, (19 + i) * 8) as u64) << (8 * i);
            }
            check(target > 782);
        }
'''
    return text.replace(end, target_check + end, 1)


def namespace_ipc_driver(text, waiting=False):
    """Compose only the admission/connection witness into the existing driver."""
    replacements = (
        ('fn call(op:', '#[inline(never)]\nfn call(op:'),
        ('abi == 14', 'abi == 26' if waiting else 'abi == 25'),
        ('check(call(0x20000, factory, 1).0 == -12);',
         'check(call(0x20000, factory, 1).0 == -38);\n    let mut old_endpoint = 0;'),
        ('let owner = call(0x20000, factory, 0).0;',
         'let connection = namespace_client::Connection::new();\n'
         '        if old_endpoint != 0 { namespace_client::stale(old_endpoint); }\n'
         '        let owner = connection.admit(factory);'),
        ('        let mut completed = false;',
         '        if stale == 0 { connection.exercise(); }\n        let mut completed = false;'),
        ('        for (stage, tag) in',
         '        old_endpoint = connection.finish();\n        for (stage, tag) in'),
        ('    end(100)', '    namespace_client::exhausted();\n    end(100)'),
    )
    for old, new in replacements:
        if text.count(old) != 1:
            raise ValueError('namespace IPC supervisor context changed: ' + old)
        text = text.replace(old, new, 1)
    marker = 'use core::arch::asm;'
    if text.count(marker) != 1:
        raise ValueError('namespace IPC supervisor import context changed')
    return text.replace(marker, marker + '\n#[path = "' + str(SOURCE / 'namespace-client.rs') + '"]\nmod namespace_client;', 1)


def zpl_stage_destination(stage):
    """Admit only fixed image roles under a live pair-owned root."""
    stage = Path(stage).absolute()
    owner = stage.parent
    if (owner.parent != ROOT / 'zig-out' or
            not owner.name.startswith('thread-suite-service-runtime-zpl-pair-') or
            owner.resolve() != owner or owner.is_symlink() or not owner.is_dir() or
            stage.name not in ('baseline', 'writer', 'reader') or stage.exists() or stage.is_symlink()):
        raise ValueError('ZPL staging requires an unused pair-owned destination')
    return stage


def stage_zpl_image(stage, destination, engine, row):
    """Temporary pair-owned boot/diagnostic inputs; never a retained build tree."""
    stage = zpl_stage_destination(stage)
    stage.mkdir()
    result = {}
    for source, name, expected in ((destination / 'aether.iso', 'aether.iso', row['iso_sha256']),
                                   (engine, 'engine.elf', row['elf_sha256'])):
        shutil.copyfile(source, stage / name)
        if sha(stage / name) != expected:
            raise ValueError('ZPL staged artifact changed: ' + name)
        result[name] = expected
    return result


def suite(delivery, case=None, openzfs_waits=False, engine_link=False, startup_config=False, engine_native=False, rtc_source=False, block_region=False, engine_volume=False, engine_volume_workers=False, engine_spa_utc=False, engine_utc=False, utc_delivery=None, fixed_reaper=False, spa_active=False, spa_physical=False, spa_write=False, pool_create=False, pool_diagnose=None, pool_data=False, pool_corrupt_labels=False, pool_interrupt=False, pool_uncommitted=False, pool_recovery_check=None, pool_namespace=False, namespace_ipc=False, pool_zpl_write=False, pool_zpl_recover=False, _zpl_stage=None, _zpl_repeat=False, _zpl_stages=False, _zpl_write_stages=False, _zpl_txg_stages=False, _zpl_sync_stages=False, _zpl_writer_budget=False, _zpl_fs_bridge=None, _zpl_recovery_diagnostic=False, _zpl_recovery_writer_60s=False, _zpl_zero=False, _zpl_namespace_mutation=None, _zpl_fs_service=None, _zpl_fs_service_case='normal', _zpl_fs_lifetimes=False, _zpl_fs_namespace=None, _zpl_fs_mixed=False, _zpl_fs_mixed_empty=False, namespace_wait=False, _zpl_fs_bulk=False, _zpl_fs_runtime=False, _zpl_fs_activation=False, _zpl_fs_names=False, _zpl_fs_directories=False, _zpl_storage_lifetime=False, _fs_launch_output=None):
    if _fs_launch_output is not None:
        if not (_zpl_fs_directories and _zpl_fs_service_case == 'normal' and pool_diagnose == 'build' and not _zpl_storage_lifetime):
            raise ValueError('launch owner requires normal directory build-only preparation')
        from fs_launch import validate_destination
        validate_destination(_fs_launch_output)
    from openzfs_mutation import validate as validate_mutation
    validate_mutation(_zpl_namespace_mutation)
    from openzfs_fs_runtime_service import validate_profile as runtime_profile
    runtime_profile(_zpl_fs_runtime, _zpl_fs_bulk, _zpl_fs_service)
    from openzfs_fs_activation_service import validate_profile as activation_profile
    activation_profile(_zpl_fs_activation, _zpl_fs_runtime, pool_zpl_write, _zpl_fs_service)
    from openzfs_fs_directories_service import validate_profile as directories_profile
    directories_profile(_zpl_fs_directories,_zpl_fs_names,pool_zpl_recover,_zpl_fs_service)
    from storage_lifetime import validate as storage_lifetime_profile
    storage_lifetime_profile(_zpl_storage_lifetime,_zpl_fs_directories,pool_zpl_recover,_zpl_fs_service_case)
    from openzfs_fs_names_service import validate_profile as names_profile
    names_profile(_zpl_fs_names,_zpl_fs_activation,_zpl_fs_runtime,pool_zpl_recover,_zpl_fs_service)
    from openzfs_fs_bulk_service import validate_profile as bulk_profile
    bulk_profile(_zpl_fs_bulk, _zpl_fs_mixed, namespace_wait, pool_zpl_write, pool_zpl_recover, _zpl_fs_service)
    from storage_channel_wait import validate as validate_wait
    validate_wait(namespace_wait,namespace_ipc,pool_namespace,pool_zpl_write,pool_zpl_recover,_zpl_fs_service,_zpl_namespace_mutation,_zpl_fs_mixed)
    if namespace_wait and not (fixed_reaper and engine_utc and pool_create and pool_diagnose in ('build','run') and case=='pool-import'):
        raise ValueError('namespace wait requires fixed readonly import/cleanup profile')
    from openzfs_fs_service import case_number
    service_case = case_number(_zpl_fs_service_case)
    from openzfs_fs_namespace import validate_profile as namespace_profile
    namespace_profile(_zpl_fs_namespace, _zpl_namespace_mutation, pool_zpl_write, pool_zpl_recover,
                      _zpl_fs_service, _zpl_fs_lifetimes, _zpl_fs_service_case)
    from openzfs_fs_mixed_service import validate_profile as mixed_profile
    mixed_profile(_zpl_fs_mixed,pool_zpl_write,pool_zpl_recover,_zpl_fs_service,
                  _zpl_fs_lifetimes,_zpl_fs_namespace,_zpl_fs_mixed_empty,_zpl_fs_service_case)
    if _zpl_fs_mixed and not (pool_namespace and pool_create and (pool_zpl_write != pool_zpl_recover) and
            pool_diagnose=='build' and _zpl_stage is not None and case=='pool-import' and fixed_reaper and engine_utc and
            (pool_zpl_write or (_zpl_recovery_diagnostic and _zpl_recovery_writer_60s)) and
            _zpl_fs_bridge is None and not _zpl_zero and _zpl_namespace_mutation is None):
        raise ValueError('mixed service requires exclusive fixed-budget paired build')
    if not isinstance(_zpl_fs_lifetimes, bool) or (_zpl_fs_lifetimes and not (
            (pool_zpl_write and _zpl_fs_service is not None) or
            (pool_zpl_recover and _zpl_recovery_writer_60s and _zpl_recovery_diagnostic))):
        raise ValueError('filesystem service lifetimes require exact writer/recovery profile')
    if service_case and _zpl_fs_service is None:
        raise ValueError('filesystem service case requires its exact selection')
    if _zpl_fs_service is not None and (not (pool_zpl_write and pool_namespace and namespace_ipc and
            not pool_zpl_recover and pool_diagnose == 'build' and _zpl_stage is not None and
            case == 'pool-import' and fixed_reaper and engine_utc and _zpl_writer_budget) or
            _zpl_fs_bridge is not None or _zpl_zero or (_zpl_namespace_mutation is not None and _zpl_fs_namespace is None) or
            any((_zpl_repeat, _zpl_stages, _zpl_txg_stages, _zpl_write_stages, _zpl_sync_stages))):
        raise ValueError('filesystem service requires exclusive paired writable IPC build')
    if _zpl_namespace_mutation is not None and (not (pool_namespace and (pool_zpl_write != pool_zpl_recover) and
            (not namespace_ipc or _zpl_fs_namespace is not None) and pool_diagnose == 'build' and _zpl_stage is not None and
            case == 'pool-import' and fixed_reaper and engine_utc) or
            _zpl_fs_bridge is not None or _zpl_zero or _zpl_stages or
            _zpl_repeat is not (_zpl_namespace_mutation in ('repeat', 'eight', 'lifetimes') and pool_zpl_write) or
            (pool_zpl_write and not _zpl_writer_budget) or
            (pool_zpl_recover and not (_zpl_recovery_diagnostic and _zpl_recovery_writer_60s))):
        raise ValueError('namespace mutation requires exclusive paired fixed-budget profile')
    if not isinstance(_zpl_zero, bool):
        raise ValueError('truncate zero selector must be boolean')
    if _zpl_zero and (not (pool_namespace and (pool_zpl_write or pool_zpl_recover) and
            not namespace_ipc and pool_diagnose == 'build' and _zpl_stage is not None and
            case == 'pool-import' and fixed_reaper and engine_utc) or
            _zpl_fs_bridge is not None or any((_zpl_repeat, _zpl_stages, _zpl_txg_stages, _zpl_sync_stages)) or
            (pool_zpl_write and not _zpl_writer_budget) or
            (pool_zpl_recover and not (_zpl_recovery_writer_60s and _zpl_recovery_diagnostic))):
        raise ValueError('truncate zero requires exclusive paired fixed-budget profiles')
    if not isinstance(_zpl_recovery_writer_60s, bool):
        raise ValueError('recovery writer window selector must be boolean')
    if _zpl_recovery_writer_60s and (not (pool_zpl_recover and pool_namespace and
            not pool_zpl_write and not namespace_ipc and pool_diagnose == 'build' and
            _zpl_stage is not None and case == 'pool-import' and fixed_reaper and engine_utc) or
            _zpl_fs_bridge is not None or _zpl_writer_budget):
        raise ValueError('recovery writer window requires paired build-only readonly profile')
    if _zpl_recovery_diagnostic and (not (pool_zpl_recover and pool_namespace and
            not pool_zpl_write and not namespace_ipc and pool_diagnose == 'build' and
            _zpl_stage is not None and case == 'pool-import' and fixed_reaper and engine_utc) or
            _zpl_fs_bridge is not None or _zpl_writer_budget):
        raise ValueError('recovery diagnostic requires paired build-only readonly profile')
    if _zpl_fs_bridge is not None and (not (pool_zpl_write and pool_namespace and
            not pool_zpl_recover and not namespace_ipc and pool_diagnose == 'build' and
            _zpl_stage is not None and case == 'pool-import' and fixed_reaper and engine_utc and _zpl_writer_budget) or
            any((_zpl_repeat, _zpl_stages, _zpl_txg_stages, _zpl_write_stages, _zpl_sync_stages))):
        raise ValueError('filesystem bridge requires exclusive paired single-write build')
    if not isinstance(_zpl_writer_budget, bool):
        raise ValueError('writer tick budget selector must be boolean')
    if _zpl_writer_budget and not (((_zpl_sync_stages and _zpl_txg_stages and _zpl_stages and
            _zpl_repeat) or _zpl_fs_bridge is not None or _zpl_zero or _zpl_namespace_mutation is not None or _zpl_fs_service is not None) and pool_zpl_write and not pool_zpl_recover and pool_namespace and
            (not namespace_ipc or _zpl_fs_service is not None) and pool_diagnose == 'build' and _zpl_stage is not None and
            case == 'pool-import' and fixed_reaper and engine_utc):
        raise ValueError('writer tick budget requires paired build-only sync-stage writer')
    if _zpl_sync_stages and not _zpl_txg_stages:
        raise ValueError("sync stages require worker profile")
    if _zpl_txg_stages and (not _zpl_stages or _zpl_write_stages):
        raise ValueError('TXG worker diagnostic requires exclusive stage profile')
    if _zpl_write_stages and not _zpl_stages:
        raise ValueError('first-write diagnostic requires stage profile')
    if _zpl_stages and not _zpl_repeat:
        raise ValueError('stage diagnostic requires paired repeated writer')
    if _zpl_repeat and (not pool_zpl_write or _zpl_stage is None):
        raise ValueError('repeated ZPL requires paired build-only writer')
    if _zpl_stage is not None and (not pool_namespace or (namespace_ipc and _zpl_fs_service is None) or
            (pool_zpl_write and pool_zpl_recover) or pool_diagnose != 'build' or
            Path(_zpl_stage).name != ('writer' if pool_zpl_write else 'reader' if pool_zpl_recover else 'baseline')):
        raise ValueError('ZPL staging requires the matching isolated build-only profile')
    if _zpl_stage is not None:
        _zpl_stage = zpl_stage_destination(_zpl_stage)
    if pool_zpl_recover and (not pool_namespace or namespace_ipc or pool_zpl_write or pool_diagnose != 'build'):
        raise ValueError('ZPL recovery requires isolated build-only namespace profile')
    if pool_zpl_write and (not pool_namespace or (namespace_ipc and _zpl_fs_service is None) or pool_diagnose != 'build'):
        raise ValueError('ZPL writer requires isolated build-only namespace profile')
    if namespace_ipc and not pool_namespace:
        raise ValueError('namespace IPC requires namespace profile')
    seal = FIXED_SEAL if fixed_reaper else SEAL
    archive = FIXED_ARCHIVE if fixed_reaper else ARCHIVE
    utc_seal = FIXED_UTC_SEAL if fixed_reaper else UTC_SEAL
    utc_archive = FIXED_UTC_ARCHIVE if fixed_reaper else UTC_ARCHIVE
    dependency = ROOT / '.deps/native-service-runtime-v3' if fixed_reaper else DEPENDENCY
    utc_dependency = ROOT / '.deps/native-utc-v3' if fixed_reaper else UTC_DEPENDENCY
    if fixed_reaper and any((openzfs_waits, engine_link, startup_config, engine_native,
                             rtc_source, block_region, engine_volume, engine_volume_workers, engine_spa_utc)):
        raise ValueError('fixed-reaper intake supports elapsed regressions and shared UTC only')
    if pool_namespace and (not (pool_create and pool_diagnose and case == 'pool-import') or
            pool_data or pool_interrupt or pool_uncommitted or pool_corrupt_labels or pool_recovery_check):
        raise ValueError('namespace requires exclusive diagnostic pool import')
    if pool_recovery_check is not None and (pool_recovery_check not in ('capacity', 'uberblock-checksum') or
            not (pool_data and pool_create and pool_diagnose and case == 'pool-import') or
            pool_interrupt or pool_uncommitted or pool_corrupt_labels):
        raise ValueError('pool recovery check requires exclusive diagnostic data import pair')
    if pool_uncommitted and not pool_interrupt:
        raise ValueError("uncommitted pool requires interrupted data import pair")
    if pool_interrupt and not (pool_data and pool_create and pool_diagnose and case == 'pool-import' and not pool_corrupt_labels):
        raise ValueError('pool interruption requires exclusive diagnostic data import pair')
    if pool_corrupt_labels and not (pool_data and pool_create and pool_diagnose and case == 'pool-import'):
        raise ValueError('corrupt labels requires explicit diagnostic data import pair')
    if pool_data and (not pool_create or not pool_diagnose or case not in POOL_CASES):
        raise ValueError('pool data requires explicit diagnostic pool case')
    if pool_diagnose not in (None, 'build', 'run') or (pool_diagnose and not pool_create):
        raise ValueError('pool diagnostics require exclusive pool creation selection')
    if (pool_create or case in POOL_CASES) and (
            not (pool_create and engine_utc and fixed_reaper) or
            any((spa_active, spa_physical, spa_write)) or case not in (None, *POOL_CASES)):
        raise ValueError('pool creation requires exclusive corrected shared UTC selection')
    spa_write = spa_write or case in WRITE_CASES
    if spa_write and spa_physical:
        raise ValueError('write and read physical groups are exclusive')
    spa_physical = spa_physical or spa_write or case in PHYSICAL_CASES
    if spa_write:
        physical_cases(case, writable=True)
    spa_active = spa_active or case in ACTIVE_CASES
    if spa_physical and (spa_active or not (engine_utc and fixed_reaper)):
        raise ValueError('physical ZIO requires corrected UTC v3 and an exclusive physical selection')
    if spa_active and not (engine_utc and fixed_reaper):
        raise ValueError('SPA activation requires explicitly selected corrected UTC v3')
    if case == EXHAUSTION_CASE and not fixed_reaper:
        raise ValueError('lifetime exhaustion requires --fixed-reaper')
    if sum((openzfs_waits, engine_link, startup_config, engine_native, rtc_source, block_region, engine_volume, engine_volume_workers, engine_spa_utc, engine_utc)) > 1:
        raise ValueError('select only one runtime profile')
    engine_volume = engine_volume or engine_volume_workers or engine_spa_utc or engine_utc
    engine_native = engine_native or engine_volume
    volume = block_region or engine_volume
    allowed = (None, 'normal', 'stop', 'disabled', 'early', *REAPER_CASES) + ((EXHAUSTION_CASE,) if fixed_reaper else ())
    if startup_config:
        allowed += ('missing', 'version', 'cache')
    if engine_native:
        allowed = (None, 'no-fini', 'no-finish', 'no-entropy', 'write-mode')
    if rtc_source:
        allowed = (None, 'rtc', 'rtc-leap', 'rtc-disabled')
    if volume:
        allowed = (None, 'block-write', 'block-verify', 'block-readonly', 'block-corrupt')
        if case == 'block-verify':
            raise ValueError('fresh-VM verify requires the preceding actual write case')
    if engine_volume_workers:
        allowed = (None, *WORKER_CASES)
    if engine_spa_utc:
        allowed = (None, *SPA_UTC_CASES)
    if engine_utc:
        allowed = (None, *(POOL_CASES if pool_create else PHYSICAL_CASES if spa_physical else ACTIVE_CASES if spa_active else UTC_CASES))
    if engine_utc != (utc_delivery is not None):
        raise ValueError('--engine-utc requires exactly one --utc-delivery')
    if case in REAPER_CASES and any((openzfs_waits, startup_config, engine_link,
                                   engine_native, rtc_source, block_region)):
        raise ValueError('reaper witness requires the unadapted elapsed runtime')
    if case not in allowed:
        raise ValueError('case unavailable in runtime intake profile')
    if sum((openzfs_waits, engine_link, startup_config, engine_native, rtc_source, block_region)) > 1:
        raise ValueError('select only one runtime profile')
    if engine_link and case is not None:
        raise ValueError('engine link is build-only; incompatible with native case/waits selection')
    from openzfs_fs_bridge import intake as bridge_intake
    bridge = bridge_intake(_zpl_fs_bridge) if _zpl_fs_bridge is not None else None
    from openzfs_fs_service import intake as service_intake
    service = service_intake(_zpl_fs_service, _zpl_fs_lifetimes, _zpl_fs_namespace is not None, _zpl_fs_mixed, namespace_wait, _zpl_fs_bulk, _zpl_fs_runtime, _zpl_fs_activation, _zpl_fs_names, _zpl_fs_directories) if _zpl_fs_service is not None else None
    selected = intake(delivery, fixed_reaper)
    utc_selected = intake_utc(utc_delivery, fixed_reaper) if engine_utc else None
    runtime = utc_dependency if engine_utc else dependency
    tools = json.loads(((BASE if fixed_reaper else dependency) / 'tools.lock.json').read_text())['tools']
    for name, entry in tools.items():
        if sha(entry['path']) != entry['sha256']:
            raise ValueError('tool drift: ' + name)
    files = [ROOT / 'build.zig', *SOURCE.iterdir(), *[p for p in (ROOT / 'kernel').rglob('*') if p.is_file()],
             *[p for p in (ROOT / 'scripts').glob('*.py')]]
    if openzfs_waits or engine_link or startup_config or engine_native:
        from openzfs_elapsed import OWNED
        files += [p for p in OWNED.iterdir() if p.is_file()]
    if engine_volume:
        from openzfs_volume import OWNED as VOLUME_SOURCE
        files += [p for p in VOLUME_SOURCE.iterdir() if p.is_file()]
    if pool_namespace:
        files.append(ROOT / 'user/storage/namespace.rs')
        files.append(ROOT / 'user/storage/namespace-wire.rs')
    if pool_namespace:
        files.append(ROOT / 'user/storage/namespace-channel.rs')
    if pool_namespace:
        files.append(ROOT / 'user/storage/namespace-wait-channel.rs')
    sources = {str(p.relative_to(ROOT)): sha(p) for p in files}
    out = Path(tempfile.mkdtemp(prefix='thread-suite-service-runtime-', dir=ROOT / 'zig-out'))
    record = {'status': 'incomplete', 'delivery_seal': seal, 'dependency_files': selected,
              'sources': sources, 'tools': tools, 'commands': [], 'cases': [],
              'engine_entry_executed': False}
    record['fixed_reaper'] = fixed_reaper
    record['openzfs_waits'] = openzfs_waits
    record['engine_link'] = engine_link
    record['startup_config'] = startup_config
    record['engine_native'] = engine_native
    record['engine_write_mode'] = pool_zpl_write or (engine_volume and case != 'pool-import') or (engine_native and case == 'write-mode')
    record['engine_volume'] = engine_volume
    record['engine_volume_workers'] = engine_volume_workers
    record['engine_spa_utc'] = engine_spa_utc
    record['engine_utc'] = engine_utc
    record['engine_spa_active'] = spa_active
    record['engine_spa_physical'] = spa_physical
    record['engine_spa_write'] = spa_write
    record['pool_create'] = pool_create
    record['pool_diagnose'] = pool_diagnose
    record['pool_data'] = pool_data
    record['pool_corrupt_labels'] = pool_corrupt_labels
    record['pool_interrupt'] = pool_interrupt
    record['pool_uncommitted'] = pool_uncommitted
    record['pool_recovery_check'] = pool_recovery_check
    record['pool_namespace'] = pool_namespace
    record['namespace_ipc'] = namespace_ipc
    if namespace_wait: record['namespace_wait'] = True
    record['pool_zpl_stages'] = _zpl_stages
    record['pool_zpl_write_stages'] = _zpl_write_stages
    record['pool_zpl_txg_stages'] = _zpl_txg_stages
    record['pool_zpl_sync_stages'] = _zpl_sync_stages
    record['pool_zpl_writer_budget'] = _zpl_writer_budget
    record['namespace_mutation'] = _zpl_namespace_mutation
    record['pool_zpl_zero'] = _zpl_zero
    record['pool_recovery_writer_60s'] = _zpl_recovery_writer_60s
    record['pool_recovery_diagnostic'] = _zpl_recovery_diagnostic
    if _zpl_fs_namespace is not None:
        record['fs_namespace_operation']=_zpl_fs_namespace
    if _zpl_fs_mixed:
        record['fs_service_mixed']=True
        if _zpl_fs_bulk:record['fs_service_bulk']=True
        if _zpl_fs_runtime:record['fs_service_runtime']=True
        if _zpl_fs_activation:record['fs_service_activation']=True
        if _zpl_fs_names:record['fs_service_names']=True
        if _zpl_fs_directories:record['fs_service_directories']=True
        if _zpl_storage_lifetime:record['storage_lifetime']=True
        record['fs_service_mixed_empty']=_zpl_fs_mixed_empty
    record['fs_bridge'] = bridge
    if _zpl_fs_lifetimes:
        record['fs_service_lifetimes'] = True
    if service is not None:
        record['fs_service'] = service
        record['fs_service_case'] = _zpl_fs_service_case
    record['pool_zpl_repeat'] = _zpl_repeat
    record['pool_zpl_write'] = pool_zpl_write
    record['pool_zpl_recover'] = pool_zpl_recover
    if engine_utc:
        record['utc_delivery_seal'] = utc_seal
        record['utc_inputs'] = utc_selected
    record['rtc_source'] = rtc_source
    record['block_region'] = block_region
    if engine_native:
        # Unknown until a target result proves the actual call was reached.
        record['engine_entry_executed'] = None
        record['engine_lifecycle_qualified'] = False
    now = lambda: datetime.now(timezone.utc).isoformat()

    def command(argv, log, rejection=None):
        args = [str(a) for a in argv]
        row = {'argv': args, 'start_utc': now()}
        record['commands'].append(row)
        with log.open('wb') as stream:
            result = subprocess.run(args, cwd=ROOT, stdout=stream,
                                    stderr=subprocess.STDOUT, timeout=180)
        row.update(exit_code=result.returncode, end_utc=now())
        if rejection:
            if result.returncode == 0 or rejection not in log.read_text():
                raise ValueError('missing named linker rejection')
        else:
            result.check_returncode()

    print('[RUNNING] Service runtime results:', out, file=sys.stderr, flush=True)
    try:
        checkout = out / 'checkout'
        shutil.copytree(runtime / 'source', checkout)
        (checkout / 'build').mkdir()
        rebuilt = checkout / 'build/runtime'
        if engine_utc:
            command([sys.executable, '-B', checkout / 'experiments/native-utc/build.py',
                     '--delivery', runtime / 'base', '--output', rebuilt], out / 'rebuild.log')
        else:
            command([sys.executable, '-B', checkout / 'experiments/native-service-runtime/build.py',
                     '--sdk', BASE, '--output', rebuilt], out / 'rebuild.log')
        record['rebuilt_archive_sha256'] = sha(rebuilt / 'libaether_runtime.a')
        if record['rebuilt_archive_sha256'] != (utc_archive if engine_utc else archive):
            raise ValueError('supplemental rebuild differs')
        probe = SOURCE / ('reaper-cycle.c' if case in REAPER_CASES else 'reaper-exhaustion.c' if case == EXHAUSTION_CASE else 'probe.c')
        objects = []
        if openzfs_waits or engine_link or engine_native:
            from openzfs_elapsed import prepare, declarations, adapt_runtime
            whole = engine_link or engine_native
            diagnostic_cc = None
            if pool_diagnose:
                from openzfs_failure import runtime_archive
                record['diagnostic_runtime'] = runtime_archive(out / 'diagnostic-runtime', runtime, tools, command)
                diagnostic_cc = record['diagnostic_runtime']['backend_compiler_prefix']
            port = prepare(out / 'port', command, entropy=whole, allocation=whole,
                           resources=whole, arc=whole, startup=whole, volume=engine_volume, volume_workers=engine_volume_workers, volume_spa_utc=engine_spa_utc, volume_utc=engine_utc, volume_spa_active=spa_active, utc_runtime=runtime / "runtime", volume_spa_physical=spa_physical, volume_open_trace=spa_physical and case == 'spa-physical-open-checkpoint', volume_write=spa_write, volume_pool=pool_create, pool_diagnostics=bool(pool_diagnose), diagnostic_cc=diagnostic_cc, volume_pool_data=pool_data, volume_pool_interrupt=pool_interrupt, volume_pool_uncommitted=pool_uncommitted, volume_pool_recovery_check=pool_recovery_check, volume_pool_namespace=pool_namespace, volume_namespace_ipc=namespace_ipc, volume_pool_zpl_write=pool_zpl_write, volume_pool_zpl_recover=pool_zpl_recover, volume_pool_zpl_repeat=_zpl_repeat, volume_pool_zpl_stages=_zpl_stages, volume_pool_zpl_write_stages=_zpl_write_stages, volume_pool_zpl_txg_stages=_zpl_txg_stages, volume_pool_zpl_sync_stages=_zpl_sync_stages, volume_fs_bridge=bridge, volume_recovery_diagnostic=_zpl_recovery_diagnostic, volume_recovery_writer_60s=_zpl_recovery_writer_60s, volume_pool_zpl_zero=_zpl_zero, volume_namespace_mutation=_zpl_namespace_mutation, volume_fs_service=service, volume_fs_service_case=_zpl_fs_service_case, volume_fs_lifetimes=_zpl_fs_lifetimes, volume_fs_namespace=_zpl_fs_namespace, volume_fs_mixed=_zpl_fs_mixed, volume_fs_mixed_empty=_zpl_fs_mixed_empty, namespace_wait=namespace_wait, volume_fs_bulk=_zpl_fs_bulk,volume_fs_runtime=_zpl_fs_runtime,volume_fs_names=_zpl_fs_names,volume_fs_directories=_zpl_fs_directories,volume_storage_lifetime=_zpl_storage_lifetime)
            record['port'] = json.loads((port / 'port-results.json').read_text())
            if pool_diagnose:
                (port / 'failure-runtime').mkdir()
                (out / 'diagnostic-runtime/failure-runtime/libaether_runtime.a').rename(port / 'failure-runtime/libaether_runtime.a')
                if sha(port / 'failure-runtime/libaether_runtime.a') != record['diagnostic_runtime']['archive_sha256']:
                    raise ValueError('private diagnostic archive moved bytes differ')
        if openzfs_waits:
            (out / 'zfs-declarations.h').write_text(declarations())
            adapted, record['adaptation'] = adapt_runtime(probe.read_text())
            probe = out / 'probe.c'
            probe.write_text(adapted)
            record['adapted_probe_sha256'] = sha(probe)
            record['declarations_sha256'] = sha(out / 'zfs-declarations.h')
            objects = [port / 'kernel.c-native.o']
        cc = [tools['clang']['path'], '--no-default-config', '--target=x86_64-linux-musl',
              '--sysroot=' + str(BASE / 'empty-root'), '-std=c17', '-D_POSIX_C_SOURCE=200809L',
              '-O2', '-Wall', '-Wextra',
              '-Werror', '-ffreestanding', '-fno-builtin', '-fstack-protector-strong', '-nostdinc',
              '-isystem', BASE / 'stage/usr/include', '-I', runtime / 'runtime']
        if engine_volume:
            driver_text = (SOURCE / 'engine-supervisor.rs').read_text()
            signature = '_start(abi: u64, factory: u64)'
            check = '    check(abi == 1 && factory == 0xa001);'
            start = '        let owner = owner as u64;'
            if any(driver_text.count(a) != 1 for a in (signature, check, start)):
                raise ValueError('engine volume supervisor context changed')
            driver_text = driver_text.replace(signature, '_start(abi: u64, factory: u64, grant: u64)', 1)
            driver_text = driver_text.replace(check, '    check(abi == 14 && factory == 0xa001 && grant == 0xf101);', 1)
            driver_text = driver_text.replace(start, start + """
        if stale == 0 {
            let region = [8u64, 16384, if cfg!(block_readonly) { 1 } else { 7 }];
            let result: i64;
            unsafe {
                asm!("int 0x81", inlateout("rax") 0x27005u64 => result,
                     in("rdi") grant, in("rsi") owner,
                     inlateout("rdx") region.as_ptr() as u64 => _, in("r10") 24u64,
                     lateout("rcx") _, lateout("r8") _, lateout("r9") _, lateout("r11") _);
            }
            check(result == 0);
        }
""", 1)
            if spa_physical or pool_create:
                old = 'let region = [8u64, 16384, if cfg!(block_readonly) { 1 } else { 7 }];'
                if driver_text.count(old) != 1:
                    raise ValueError('physical region supervisor context changed')
                driver_text = driver_text.replace(old,
                    'let region = [8u64, if cfg!(physical_small) { 16384 } else { 131072 }, if cfg!(pool_create) { if cfg!(pool_import) { 1 } else { 7 } } else if cfg!(physical_write) { if cfg!(physical_no_flush_rights) { 3 } else { 7 } } else { 1 }];', 1)
            if engine_utc:
                old = '        check(completed);'
                diagnostic = """        if !completed {
            let mut phase = 0u64;
            for offset in (0..256).step_by(8) {
                let value = call(0x20003, owner, offset).0;
                if value == -11 { break; }
                check((0..=255).contains(&value));
                phase = value as u64;
            }
            end(900 + phase);
        }"""
                if driver_text.count(old) != 1:
                    raise ValueError('UTC progress supervisor context changed')
                driver_text = driver_text.replace(old, diagnostic, 1)
                old = '        for (stage, tag) in b"BIFR".iter().enumerate() {'
                new = '        let tags = if cfg!(pool_create) { if stale == 0 { if cfg!(pool_import) { b"BIUVWLP????????OAMDJFR".as_slice() } else { b"BIUVWP????????CADJFR".as_slice() } } else { b"BNR".as_slice() } } else if cfg!(spa_physical) { if stale == 0 { if cfg!(physical_write) { b"BIUVWACOqstkhgcfjipQSTKHPDJFR".as_slice() } else if cfg!(physical_revoked) { b"BIUVWACOQSXKHEDJFR".as_slice() } else { b"BIUVWACOQSTKHPDJFR".as_slice() } } else { b"BNR".as_slice() } } else if cfg!(utc_reuse) { b"BIUVWUVWUVWUVWUVWUVWUVWUVWJFR".as_slice() } else if cfg!(spa_active) { b"BIUVWAZDJFR".as_slice() } else { b"BIUVWJFR".as_slice() };\n        for (stage, tag) in tags.iter().enumerate() {'
                if driver_text.count(old) != 1:
                    raise ValueError('UTC phase supervisor context changed')
                driver_text = driver_text.replace(old, new, 1)
                driver_text = driver_text.replace('1 => live > 1 && live <= 82 && admissions > 1,',
                                                   'n if n + 1 < tags.len() => if (cfg!(spa_physical) || cfg!(pool_create)) && stale != 0 { live == 1 && admissions == 1 } else { live > 0 && live <= 82 && admissions > 1 },', 1)
                old = '            check(byte(owner, offset) == *tag);'
                new = '            let observed = byte(owner, offset);\n            if cfg!(utc_reuse) && observed != *tag { end(847); }\n            check((cfg!(pool_create) && stale == 0 && (if cfg!(pool_import) { (7..15).contains(&stage) } else { (6..14).contains(&stage) })) || observed == *tag);'
                if driver_text.count(old) != 1:
                    raise ValueError('UTC reuse phase check context changed')
                driver_text = driver_text.replace(old, new, 1)
                driver_text = driver_text.replace('2 => live <= 82,', '', 1)
                driver_text = driver_text.replace('owner, 32)', 'owner, tags.len() as u64 * 8)', 1)
                if pool_data:
                    driver_text = driver_text.replace('b"BIUVWP????????CADJFR"', 'b"BIUVWP????????CAT????????SDJFR"')
                    driver_text = driver_text.replace('b"BIUVWLP????????OAMDJFR"', 'b"BIUVWLP????????OAMT????????SDJFR"')
                    driver_text = driver_text.replace('(7..15).contains(&stage)', '(7..15).contains(&stage) || (19..27).contains(&stage)')
                    driver_text = driver_text.replace('(6..14).contains(&stage)', '(6..14).contains(&stage) || (17..25).contains(&stage)')
                if pool_recovery_check == "capacity":
                    old = 'b"BIUVWP????????CAT????????SDJFR"'
                    if driver_text.count(old) != 1:
                        raise ValueError("capacity supervisor context changed")
                    driver_text = driver_text.replace(old, 'b"BIUVWP????????CAT????????SQ\\x1cDJFR"', 1)
                if pool_diagnose:
                    driver_text = pool_diagnostic_driver(driver_text)
            if pool_namespace:
                driver_text = namespace_driver(driver_text, pool_zpl_write, pool_zpl_recover, _zpl_stages, _zpl_write_stages, _zpl_txg_stages, _zpl_sync_stages)
            if namespace_ipc:
                driver_text = namespace_ipc_driver(driver_text,namespace_wait)
                if service is not None:
                    old = str(SOURCE / 'namespace-client.rs')
                    if driver_text.count(old) != 1:
                        raise ValueError('filesystem service client context changed')
                    driver_text = driver_text.replace(old, str(SOURCE / 'fs-service-client.rs'), 1)
                    if driver_text.count('old_endpoint = connection.finish();') != 1:
                        raise ValueError('filesystem service finish context changed')
                    driver_text = driver_text.replace('old_endpoint = connection.finish();', 'old_endpoint = connection.finish(stale == 0);', 1)
                    if service.get('activation',False):
                        from openzfs_fs_activation_service import driver as activation_driver
                        driver_text = activation_driver(driver_text)
            if _zpl_storage_lifetime and service is not None:
                from storage_lifetime import controller as lifetime_controller
                driver_text = lifetime_controller(driver_text)
            driver_source = out / 'supervisor.rs'
            driver_source.write_text(driver_text)
            record['adapted_supervisor_sha256'] = sha(driver_source)
            if pool_namespace:
                from openzfs_namespace import prepare_native_fixture
                record['namespace_fixture'] = prepare_native_fixture(out)
                shared_disk = Path(record['namespace_fixture']['output'])
                record['disk_seed_sha256'] = record['namespace_fixture']['sha256']
                seed = changed = None
            else:
                seed = bytearray([165] * (64 * 1024 * 1024 + 8192 if (spa_physical or pool_create) and case != "spa-physical-small" else 16 * 1024 * 1024))
                seed[8 * 512:9 * 512] = bytes((i * 17 + 3) & 255 for i in range(512))
                if spa_physical:
                    seed[4096 + 1048576:4096 + 1048576 + 512] = bytes((i * 17 + 7) & 255 for i in range(512))
                changed = bytearray(seed)
                changed[8 * 512:9 * 512] = bytes((i * 17 + 91) & 255 for i in range(512))
                shared_disk = out / 'disposable.raw'
                shared_disk.write_bytes(seed)
                record['disk_seed_sha256'] = sha(shared_disk)
        if block_region:
            text = probe.read_text()
            anchors = ['static void *worker(void *argument)', '          800);\n    unsigned long memory',
                       '    unsigned mode = (uintptr_t)argument;',
                       '    CHECK(!aether_runtime_finish()', '        if (mode == 0) {']
            if any(text.count(a) != 1 for a in anchors):
                raise ValueError('volume runtime witness context changed')
            text = text.replace(anchors[0], '#include "block-probe.inc"\n' + anchors[0], 1)
            text = text.replace(anchors[1], '          800);\n    int volume_status = volume_start_probe();\n'
                                '    CHECK(!volume_status, volume_status);\n    unsigned long memory', 1)
            text = text.replace(anchors[2], anchors[2] + '\n    if (mode == 0 && volume_worker_probe())\n        return (void *)843;', 1)
            text = text.replace(anchors[3], '    CHECK(!volume_finish_probe(), 844);\n' + anchors[3], 1)
            text = text.replace(anchors[4], '        if (mode == 2 && volume_full_probe())\n            return (void *)843;\n' + anchors[4], 1)
            cc += ['-I', SOURCE]
            probe = out / 'probe.c'
            probe.write_text(text)
            record['adapted_probe_sha256'] = sha(probe)
            # Only this private startup route changes. The lifecycle witness is
            # unchanged after the copied one-hop transfer.
            driver_text = (SOURCE / 'supervisor.rs').read_text()
            signature = '_start(abi: u64, factory: u64)'
            check = '    check(abi == 1 && factory == 0xa001);'
            start = '    check(a > 0);'
            if any(driver_text.count(a) != 1 for a in (signature, check, start)):
                raise ValueError('volume supervisor context changed')
            driver_text = driver_text.replace(signature, '_start(abi: u64, factory: u64, grant: u64)', 1)
            driver_text = driver_text.replace(check, '    check(abi == 14 && factory == 0xa001 && grant == 0xf101);', 1)
            driver_text = driver_text.replace(start, start + '''
    let region = [8u64, 16384, if cfg!(block_readonly) { 1 } else { 7 }];
    let result: i64;
    // Copied scalar record lives through the synchronous native call only.
    unsafe {
        asm!("int 0x81", inlateout("rax") 0x27005u64 => result,
             in("rdi") grant, in("rsi") a as u64,
             inlateout("rdx") region.as_ptr() as u64 => _, in("r10") 24u64,
             lateout("rcx") _, lateout("r8") _, lateout("r9") _, lateout("r11") _);
    }
    check(result == 0);
''', 1)
            driver_source = out / 'supervisor.rs'
            driver_source.write_text(driver_text)
            record['adapted_supervisor_sha256'] = sha(driver_source)
            seed = bytearray([165] * (16 * 1024 * 1024))
            seed[8 * 512:9 * 512] = bytes((i * 17 + 3) & 255 for i in range(512))
            changed = bytearray(seed)
            changed[8 * 512:9 * 512] = bytes((i * 17 + 91) & 255 for i in range(512))
            shared_disk = out / 'disposable.raw'
            shared_disk.write_bytes(seed)
            record['disk_seed_sha256'] = sha(shared_disk)
        if rtc_source:
            text = probe.read_text()
            anchor = '          800);\n    unsigned long memory'
            if text.count('int main(void)') != 1 or text.count(anchor) != 1:
                raise ValueError('RTC witness context changed')
            text = text.replace('int main(void)', '#include "rtc-probe.inc"\nint main(void)', 1)
            text = text.replace(anchor, '          800);\n    int rtc_status = rtc_probe();\n'
                                '    CHECK(!rtc_status, rtc_status);\n    unsigned long memory', 1)
            cc += ['-I', SOURCE]
            probe = out / 'probe.c'
            probe.write_text(text)
            record['adapted_probe_sha256'] = sha(probe)
        if case in REAPER_CASES:
            cc += ['-I', dependency / 'source/experiments/native-service-runtime']
        if startup_config:
            from openzfs_elapsed import OWNED
            cc += ['-I', OWNED]
            provider = out / 'startup-provider.o'
            command(cc + ['-c', OWNED / 'startup.c', '-o', provider], out / 'startup-provider.log')
            objects = [provider]
            text = probe.read_text()
            old = 'int main(void)'
            anchor = '          800);\n    unsigned long memory'
            if text.count(old) != 1 or text.count(anchor) != 1:
                raise ValueError('startup witness context changed')
            text = text.replace(old, '#include "startup-probe.inc"\n' + old, 1)
            text = text.replace(anchor, '          800);\n    CHECK(!startup_probe(), 830);\n    unsigned long memory', 1)
            probe = out / 'probe.c'
            probe.write_text(text)
            record['startup_provider_sha256'] = sha(provider)
            record['adapted_probe_sha256'] = sha(probe)
        if openzfs_waits:
            cc += ['-I', SOURCE, '-I', out]
        if (engine_link or engine_native) and not engine_volume:
            record['engine_composition'] = compose_engine(port, command, cc, tools, engine_native, case)
        cases = [('normal', [], None), ('stop', [], None),
                                     ('disabled', ['-Dnative-clock=false'], 804),
                                     ('early', ['-Dnative-clock-skip-wait=true'],
                                      125 if openzfs_waits else 802)]
        if startup_config:
            cases += [('missing', [], 125), ('version', [], 830), ('cache', [], 830)]
        if case in REAPER_CASES:
            cases = [('reaper-cycle', ['-DREAPER_CYCLE'], None if fixed_reaper else 870), ('reaper-serial', [], None)]
        if engine_native:
            cases = [(case or 'engine', [], {'no-fini': 224, 'no-finish': 225, 'no-entropy': 125}.get(case))]
        if rtc_source:
            cases = [('rtc', [], None), ('rtc-leap', [], None), ('rtc-disabled', [], 831)]
        if volume:
            cases = [('block-write', [], None), ('block-verify', [], None),
                     ('block-readonly', [], None), ('block-corrupt', [], 840)]
        if engine_volume_workers:
            cases = [(name, [], 846 if name == 'block-workers-inline' else None) for name in WORKER_CASES]
            # Exact current default artifact identity permits the previous native
            # volume results to stand; worker object/entry are opt-in only.
            default = compose_engine(port, command, cc, tools, True, 'block-write', volume=True)
            if default['elf_sha256'] != 'd35601edd0379f11cc2ee51ca7e3a823170066f0e9e3c6bb8f98320e96fc6ba7':
                raise ValueError('default volume artifact changed')
            record['default_volume_identity'] = default
        if case == EXHAUSTION_CASE:
            cases = [(EXHAUSTION_CASE, [], None)]
        if engine_spa_utc:
            cases = [(name, [], 849 if name == 'spa-utc' else 125) for name in SPA_UTC_CASES]
        if engine_utc:
            cases = [(name, [], {'utc-disabled': 856, 'utc-policy': 855, 'spa-active-no-activation': 857,
                                 'spa-active-no-callback': 858, 'spa-physical-open-checkpoint': 867, 'spa-physical-small': 861,
                                 'spa-physical-no-callback': 862, 'spa-physical-corrupt': 860,
                                 'spa-physical-no-flush': 868, 'spa-physical-flush-rights': 869,
                                 'spa-physical-flush-revoked': 869, 'spa-physical-write-no-callback': 871}.get(name))
                     for name in (('pool-import',) if pool_namespace else pool_cases(case) if pool_create else physical_cases(case, writable=spa_write) if spa_physical else ACTIVE_CASES if spa_active else UTC_CASES)]
        for name, flags, expected in cases:
            if (pool_corrupt_labels or pool_recovery_check == 'uberblock-checksum') and name == 'pool-import':
                expected = 873
            if engine_link:
                break
            if case is not None and name != case and not (pool_create and case == 'pool-import' and name == 'pool-create'):
                continue
            dest = out / name
            dest.mkdir()
            row = {'name': name, 'status': 'running', 'expected_detail': expected, 'start_utc': now()}
            record['cases'].append(row)
            cflags = ['-DSTOP_LIVE'] if name == 'stop' else []
            if fixed_reaper and name in REAPER_CASES:
                cflags += ['-DREAPER_FIXED']
            if name == 'reaper-cycle':
                cflags += ['-DREAPER_CYCLE']
                flags = []
            rtc_base = None
            if rtc_source:
                leap = name == 'rtc-leap'
                rtc_base = '2000-02-29T12:34:00' if leap else '2026-10-06T12:34:00'
                cflags += ['-DRTC_DAY=' + ('0x29' if leap else '0x06'),
                           '-DRTC_MONTH=' + ('0x02' if leap else '0x10'),
                           '-DRTC_YEAR=' + ('0x00' if leap else '0x26')]
                row['rtc_base'] = rtc_base
            if engine_utc:
                rtc_base = '2000-02-29T12:34:00' if name in ('utc-leap', 'utc-reuse', 'utc-reuse-short') else '2026-10-06T12:34:00'
                row['rtc_base'] = rtc_base
            block_disk = None
            if volume:
                cflags += ['-DBLOCK_VERIFY=' + str(int(name in ('block-verify', 'block-corrupt'))),
                           '-DBLOCK_READONLY=' + str(int(volume_readonly(name)))]
                if name in ('block-write', 'block-verify', *WRITE_CASES[:2]) or (pool_create and case == 'pool-import'):
                    block_disk = shared_disk
                else:
                    block_disk = dest / 'disposable.raw'
                    contents = bytearray(seed[:16 * 1024 * 1024] if name == 'spa-physical-small' else seed)
                    if name == 'spa-physical-corrupt':
                        contents[4096 + 1048576] ^= 1
                    if name == 'block-corrupt':
                        contents = bytearray(changed)
                        contents[8 * 512] ^= 1
                    block_disk.write_bytes(contents)
                before_disk = None if pool_namespace else block_disk.read_bytes()
                if name == 'pool-import' and pool_diagnose != 'build' and not pool_namespace:
                    prior = record['cases'][-2]
                    check_pool_import_media(prior, block_disk, pool_interrupt, pool_uncommitted)
                    if pool_corrupt_labels:
                        before_disk, mutation = corrupt_pool_label_headers(before_disk)
                        block_disk.write_bytes(before_disk)
                        row['label_corruption'] = mutation
                    if pool_recovery_check == 'uberblock-checksum':
                        before_disk, mutation = corrupt_pool_uberblocks(before_disk)
                        block_disk.write_bytes(before_disk)
                        row['uberblock_corruption'] = mutation
            if startup_config and name in ('missing', 'version', 'cache'):
                cflags += ['-DSTARTUP_' + name.upper()]
            if engine_volume:
                composition = compose_engine(port, command, cc, tools, True, name, volume=True, workers=engine_volume_workers, spa_utc=engine_spa_utc, utc=engine_utc, runtime=runtime, spa_active=spa_active, spa_physical=spa_physical, pool=pool_create, diagnostics=bool(pool_diagnose), pool_data=pool_data, pool_interrupt=pool_interrupt, pool_uncommitted=pool_uncommitted, pool_recovery_check=pool_recovery_check, pool_namespace=pool_namespace, pool_zpl_write=pool_zpl_write, pool_zpl_recover=pool_zpl_recover, txg_worker=_zpl_txg_stages, fs_bridge=bridge is not None, zpl_zero=_zpl_zero and pool_zpl_write, namespace_mutation=_zpl_namespace_mutation, fs_service=service is not None, fs_service_case=_zpl_fs_service_case, fs_service_lifetimes=_zpl_fs_lifetimes, fs_service_namespace=_zpl_fs_namespace is not None, fs_service_mixed=_zpl_fs_mixed,fs_service_wait=namespace_wait and service is not None,fs_service_bulk=_zpl_fs_bulk,fs_service_runtime=_zpl_fs_runtime,fs_service_activation=_zpl_fs_activation,fs_service_names=_zpl_fs_names,fs_service_directories=_zpl_fs_directories)
                row['engine_composition'] = composition
            if not engine_native:
                command(cc + cflags +
                        ['-c', probe, '-o', dest / 'probe.o'], dest / 'compile.log')
            link = [tools['lld']['path'], '-static', '-z', 'noexecstack', '--no-undefined',
                    BASE / 'stage/usr/lib/crt1.o', BASE / 'stage/usr/lib/crti.o', dest / 'probe.o', *objects,
                    '--whole-archive', dependency / 'runtime/libaether_runtime.a', '--no-whole-archive',
                    BASE / 'stage/usr/lib/libc.a', BASE / 'stage/usr/lib/crtn.o', '-o', dest / 'probe.elf']
            if name in REAPER_CASES:
                link += ['--wrap=__unmapself', '--wrap=__tl_lock', '-Map=' + str(dest / 'probe.map')]
            if openzfs_waits:
                link += ['--gc-sections', '-Map=' + str(dest / 'probe.map')]
            if not engine_native:
                command(link, dest / 'link.log')
            if name in REAPER_CASES:
                mapping = (dest / 'probe.map').read_text()
                command([tools['nm']['path'], dest / 'probe.elf'], dest / 'symbols.log')
                origins = check_reaper_bindings(mapping, (dest / 'symbols.log').read_text())
                row['actual_reaper_bindings'] = origins
                row['map_sha256'] = sha(dest / 'probe.map')
                command([a for a in link if a != '--wrap=__unmapself'] + ['-o', dest / 'wrapper-omitted.elf'],
                        dest / 'wrapper-omitted.log', rejection='undefined symbol: __real___unmapself')
            if openzfs_waits:
                mapping = (dest / 'probe.map').read_text()
                row['actual_callers'] = check_callers(mapping)
                row['map_sha256'] = sha(dest / 'probe.map')
            command(['rustc', '+1.98.0', '--edition=2024', '--target=x86_64-unknown-none',
                     '-C', 'opt-level=z' if namespace_ipc else 'opt-level=2',
                     *(['-Clto=fat', '-Ccodegen-units=1'] if namespace_ipc else []),
                     *(['--cfg','fs_directories'] if _zpl_fs_directories and service is not None else []),
                     *(['--cfg','fs_storage_lifetime'] if _zpl_storage_lifetime and service is not None else []),
                     *(['--cfg','fs_names'] if _zpl_fs_names and service is not None else []),
                     *(['--cfg','fs_activation'] if _zpl_fs_activation else []),
                     *(['--cfg','fs_runtime'] if _zpl_fs_runtime and service is not None else []),
                     *(['--cfg','fs_bulk'] if _zpl_fs_bulk and service is not None else []),
                     *(['--cfg','fs_mixed'] if _zpl_fs_mixed and service is not None else []),
                     *(['--cfg','namespace_wait'] if namespace_wait else []),
                     *(['--cfg', 'fs_namespace_'+_zpl_fs_namespace] if _zpl_fs_namespace is not None and service is not None else []),
                     *(['--cfg', 'fs_eight_writes'] if _zpl_fs_lifetimes and service is not None else []),
                     *(['--cfg', 'fs_lost_reply'] if service_case == 1 else ['--cfg', 'fs_partial_request'] if service_case == 2 else []),
                     '-C', 'panic=abort', '-C', 'relocation-model=static',
                     '-C', 'link-arg=-Tuser/storage/service-runtime/activation-linker.ld' if _zpl_fs_activation else 'link-arg=-Tuser/protection/linker.ld', '-C', 'link-arg=--oformat=binary',
                     driver_source if volume else SOURCE / ('engine-supervisor.rs' if engine_native else 'supervisor.rs'), '-o', dest / 'supervisor.raw'] +
                    (['--cfg', 'stop_live'] if name == 'stop' else []) +
                    (['--cfg', 'block_readonly'] if volume_readonly(name) and not pool_zpl_write else []) +
                    (['--cfg', 'utc_reuse'] if name in ('utc-reuse', 'utc-reuse-short') else []) +
                    (['--cfg', 'spa_active'] if spa_active else []) +
                    (['--cfg', 'pool_create'] if pool_create else []) +
                    (['--cfg', 'pool_import'] if name == 'pool-import' else []) +
                    (['--cfg', 'spa_physical'] if spa_physical else []) +
                    (['--cfg', 'physical_small'] if name == 'spa-physical-small' else []) +
                    (['--cfg', 'physical_revoked'] if name == 'spa-physical-revoked' else []) +
                    (['--cfg', 'physical_write'] if name in WRITE_CASES and name != WRITE_CASES[1] else []) +
                    (['--cfg', 'physical_no_flush_rights'] if name == 'spa-physical-flush-rights' else []), dest / 'supervisor.log')
            image = port / 'engine.elf' if engine_native else dest / 'probe.elf'
            elf, driver = image.read_bytes(), (dest / 'supervisor.raw').read_bytes()
            if not 0 < len(driver) <= (8192 if _zpl_fs_activation else 4096):
                raise ValueError('supervisor code budget')
            if pool_diagnose == 'build' and not (namespace_ipc or pool_zpl_write or pool_zpl_recover or _zpl_stage is not None):
                row.update(status='build-only', end_utc=now(), engine_entry_executed=False,
                           supervisor_sha256=sha(dest / 'supervisor.raw'), supervisor_bytes=len(driver))
                if case == 'pool-import':
                    continue
                break
            envelope = dest / 'native-c.bin'
            envelope.write_bytes(struct.pack('<8sII', b'AENBD005' if _zpl_storage_lifetime and service is not None else b'AENBD004' if namespace_wait else b'AENBD003' if namespace_ipc else b'AENBD002' if volume else b'AENSUP01', len(elf), len(driver)) + os.urandom(32) + elf + driver)
            row.update(elf_sha256=sha(image), supervisor_sha256=sha(dest / 'supervisor.raw'),
                       envelope_sha256=sha(envelope))
            options = ['-Dsmp=false', '-Dnative-memory=true', '-Dnative-memory-large=true',
                       '-Dnative-image-large=true', '-Dnative-backing=true', '-Dnative-service-memory=true',
                       '-Dnative-threads=true', '-Dnative-thread-pair=true', '-Dnative-thread-reuse=true',
                       '-Dnative-thread-origin=true', '-Dnative-service-workers=true', '-Dnative-clock=true']
            if engine_native and name != 'no-entropy':
                options += ['-Dnative-entropy=true']
            if (rtc_source and name != 'rtc-disabled') or (engine_utc and name != 'utc-disabled'):
                options += ['-Dnative-rtc=true']
            if volume:
                options += ['-Dnative-service-block=true']
            if pool_diagnose:
                options += ['-Dnative-service-cleanup-trace=true']
            if namespace_ipc:
                options += ['-Dnative-service-channel=true']
            if namespace_wait:
                options += ['-Dnative-service-channel-wait=true']
            if _zpl_fs_activation:
                options += ['-Dnative-service-activation=true']
            if _zpl_storage_lifetime and service is not None:
                options += ['-Dnative-service-lifetime=true']
            if _zpl_writer_budget:
                options += ['-Dnative-service-zpl-budget=true']
            options = [o for o in options if not (name == 'disabled' and o == '-Dnative-clock=true')]
            command(['zig', 'build', '-p', dest, '--cache-dir', ROOT / '.zig-cache',
                     '--global-cache-dir', ROOT / '.zig-cache/global', '-Dnative-c-image=' + str(envelope)] +
                    options + flags, dest / 'build.log')
            row['iso_sha256'] = sha(dest / 'aether.iso')
            if pool_diagnose == 'build':
                # Build the selected controller/envelope against the enforcing
                # kernel before any guest; this does not execute its transfer.
                row.update(status='build-only', end_utc=now(), engine_entry_executed=False,
                           supervisor_bytes=len(driver), kernel_profile=(
                               'AENBD005/owner27/engine26' if _zpl_storage_lifetime and service is not None else 'AENBD004/ABI26' if namespace_wait else 'AENBD003/ABI25' if namespace_ipc else 'AENBD002/ABI14'))
                if _zpl_stage is not None:
                    row['staged_artifacts'] = stage_zpl_image(_zpl_stage, dest, image, row)
                continue
            context = () if expected is None else (
                f'NATIVE terminal slot=0 generation=1 kind=1 detail={expected}'.encode(),
                b'NATIVE supervisor result=401 reclaimed=0')
            short_reuse = name == 'utc-reuse-short'
            if short_reuse:
                context = (b'NATIVE terminal slot=0 generation=1 kind=1 detail=0',
                           b'NATIVE supervisor result=847 reclaimed=0')
                row['expected_supervisor_result'] = 847
            if engine_native:
                record['engine_entry_attempted'] = True
            marker = 'AETHER NATIVE BLOCK PASS' if volume else 'AETHER NATIVE SUPERVISION PASS'
            if pool_interrupt and name == 'pool-create':
                marker = ('NATIVE observation slot=0 generation=1 offset=216 byte=75' if pool_uncommitted else
                          'NATIVE observation slot=0 generation=1 offset=208 byte=75')
            run(dest / 'aether.iso', marker=marker.encode(),
                expected_panic=b'native C profile rejected' if expected or short_reuse else None,
                panic_context=context, entropy=engine_native and name != 'no-entropy', rtc_base=rtc_base, block_disk=block_disk,
                block_large=(spa_physical or pool_create) and name != "spa-physical-small",
                **({'block_namespace': True} if pool_namespace else {}))
            row['vm_run_returned'] = True
            if namespace_wait:
                from storage_channel_wait import trace as wait_trace
                row.update(wait_trace((dest/'native-serial.log').read_text()))
            if name == 'spa-physical-open-checkpoint':
                row.update(check_open_probe_trace((dest / 'native-serial.log').read_text()))
            if name in WRITE_CASES:
                row.update(check_write_trace((dest / 'native-serial.log').read_text(), name))
            if pool_namespace:
                from openzfs_namespace import native_media_snapshot
                row['namespace_media'] = native_media_snapshot(block_disk)
                if row['namespace_media']['sha256'] != record['disk_seed_sha256']:
                    raise ValueError('namespace whole media changed')
                row['disk_sha256'] = row['namespace_media']['sha256']
            else:
                if volume:
                    expected_disk = bytes(changed) if name in ('block-write', 'block-workers') else physical_expected_disk(before_disk, name)
                    after_disk = block_disk.read_bytes()
                    if pool_create and name == 'pool-create':
                        if (after_disk[:4096] != before_disk[:4096] or
                                after_disk[-4096:] != before_disk[-4096:] or
                                after_disk == before_disk):
                            raise ValueError('pool creation disk/canary oracle')
                        expected_disk = after_disk
                    if after_disk != expected_disk:
                        raise ValueError('whole disposable disk/canaries changed: ' + name)
                    row['disk_sha256'] = sha(block_disk)
            if pool_interrupt and name == 'pool-create':
                row.update(check_pool_interrupted_trace((dest / 'native-serial.log').read_text(), pool_uncommitted))
            elif expected is None and not short_reuse:
                serial = (dest / 'native-serial.log').read_text()
                row.update(check_engine_trace(serial, marker) if engine_native else check_trace(serial, name == 'stop', marker))
                if engine_utc:
                    row.pop('four_checked_observations_per_generation', None)
                    if pool_create:
                        row.update(check_namespace_trace(serial) if pool_namespace else check_pool_import_trace(serial, pool_data) if name == 'pool-import' else check_pool_create_trace(serial, pool_data, pool_recovery_check == 'capacity'))
                        if pool_diagnose:
                            row.update(check_pool_cleanup_trace(serial))
                    elif spa_physical:
                        row['physical_io_owner_generations'] = [1]
                        row['post_close_zio_qualified'] = name == 'spa-physical-revoked'
                        row['denied_volume_owner_generations'] = [2, 3]
                        row['checked_observation_rows'] = [29 if name == 'spa-physical-write' else 18, 3, 3]
                    else:
                        row['checked_observations_per_generation'] = 29 if name == 'utc-reuse' else 11 if spa_active else 8
                if engine_native:
                    record['engine_entry_executed'] = True
                    record['engine_lifecycle_qualified'] = True
            elif (pool_corrupt_labels or pool_recovery_check == 'uberblock-checksum') and name == 'pool-import':
                bad_uberblocks = pool_recovery_check == 'uberblock-checksum'
                row.update(check_pool_corrupt_label_trace((dest / 'native-serial.log').read_text(), bad_uberblocks))
                record['corrupt_uberblock_rejection_qualified' if bad_uberblocks else 'corrupt_label_rejection_qualified'] = True
            elif short_reuse or (engine_native and expected in (224, 225, 846, 849, 857, 858, 860, 861, 862, 867, 868, 869, 871)):
                # These source-bound return sites follow actual kernel_init.
                record['engine_entry_executed'] = True
            if pool_data and not pool_corrupt_labels and pool_recovery_check != 'uberblock-checksum' and name == 'pool-import':
                record.update(check_pool_data_pair(record['cases'][-2], row, interrupted=pool_interrupt, uncommitted=pool_uncommitted))
                if pool_recovery_check == 'capacity':
                    if not record['cases'][-2].get('capacity_denial_baseline_validated'):
                        raise ValueError('capacity denial witness missing')
                    record['capacity_denial_recovery_qualified'] = True
            row.update(status='pass', end_utc=now())
        if any(sha(ROOT / n) != h for n, h in sources.items()) or any(
                sha(dependency / n) != h for n, h in selected.items()):
            raise ValueError('inputs changed during qualification')
        if engine_utc:
            sealed(utc_dependency, utc_seal, 343 if fixed_reaper else 314)
        sealed(BASE, 'f6bc6d6da3b051e1e4617e60ae256cbd35d193b608631ac29f7c42dbe73b13dc', 240)
        if not engine_link and not record['cases']:
            raise ValueError('native qualification executed zero cases')
        record['status'] = 'pass'
    except BaseException as error:
        record.update(status='failed', error=str(error))
        if record['cases'] and record['cases'][-1]['status'] == 'running':
            record['cases'][-1].update(status='failed', error=str(error), end_utc=now())
        raise
    finally:
        if pool_diagnose:
            catalogue = record.get('port', {}).get('failure_catalogue', [])[:]
            for consumer in record.get('port', {}).get('allocation_consumers', {}).get('objects', []):
                catalogue += consumer.get('failure_catalogue', [])
            catalogue += record.get('diagnostic_runtime', {}).get('catalogue', [])
            catalogue += [{'site': 80, 'family': 'volume', 'context': 'Rust volume panic handler'}]
            record['failure_catalogue'] = catalogue
            last_case = (record.get('cases') or [{}])[-1]
            serial_path = out / last_case.get('name', 'pool-create') / 'native-serial.log'
            if serial_path.is_file():
                from openzfs_failure import decode_site, symbolize_assertion
                try:
                    record['failure_site'] = decode_site(serial_path.read_text(), catalogue)
                except ValueError as diagnostic_error:
                    record['failure_site'] = {'status': 'unlocalized', 'error': str(diagnostic_error)}
                if record['failure_site'].get('site') == 65:
                    try:
                        record['assertion_caller'] = symbolize_assertion(record['failure_site'], port / 'engine.elf', tools, command)
                    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError) as diagnostic_error:
                        record['assertion_caller'] = {'status': 'unlocalized', 'error': str(diagnostic_error)}
        if pool_create:
            # QEMU run() has returned/stopped before this read. A digest never
            # substitutes for engine/provider retirement or accepted durability.
            try:
                # Pair attaches shared media; standalone creation attaches case media.
                record['pool_media_path'] = str(out / 'native-namespace.raw' if pool_namespace else pool_attached_media(out, case))
                if pool_namespace and Path(record['pool_media_path']).is_file():
                    from openzfs_namespace import native_media_snapshot
                    record['final_pool_media'] = native_media_snapshot(record['pool_media_path'])
                else:
                    record['final_pool_media'] = pool_media_snapshot(Path(record['pool_media_path']))
                if record['final_pool_media']['status'] == 'captured':
                    record['final_pool_media']['whole_disk_matches_seed'] = (
                        record['final_pool_media']['sha256'] == record.get('disk_seed_sha256'))
            except (OSError, ValueError) as media_error:
                record['final_pool_media'] = {'status': 'unavailable', 'error': str(media_error)}
        (out / 'results.json').write_text(json.dumps(record, indent=2) + '\n')
        if _fs_launch_output is not None and record['status'] == 'pass':
            from fs_launch import compose
            try:
                record['launch_owner'] = compose(out, record, _fs_launch_output)
            finally:
                compact_run(out, record)
                if _zpl_stage is not None:
                    (_zpl_stage.parent / (_zpl_stage.name + '-build.json')).write_text(
                        json.dumps({'output': str(out), 'report': record}, indent=2) + '\n')
        else:
            compact_run(out, record)
        if _zpl_stage is not None:
            (_zpl_stage.parent / (_zpl_stage.name + '-build.json')).write_text(
                json.dumps({'output': str(out), 'report': record}, indent=2) + '\n')
    if pool_diagnose == 'build':
        print('[PASS] Pool diagnostic composition built; engine not executed')
    elif engine_link:
        print('[PASS] Selected engine composition and structural loader checks; engine not executed')
    else:
        print('[PASS] Service runtime selected native cases:', len(record['cases']))
    return out


if __name__ == '__main__':
    parser = IntakeParser(description=__doc__)
    parser.add_argument('--version', action='version', version='aether-service-runtime-intake 1')
    parser.add_argument('--fixed-reaper', action='store_true', help='explicitly intake corrected v3 candidates; defaults stay v2')
    parser.add_argument('--pool-diagnose', choices=('build', 'run'), help='private failure-site diagnostics; build executes no guest')
    parser.add_argument('--pool-recovery-check', choices=('capacity', 'uberblock-checksum'),
                        help='check capacity denial or corrupted uberblocks; requires exclusive diagnostic data import pair')
    parser.add_argument('--pool-uncommitted', action='store_true',
                        help='hold a dirty second transaction before commit; requires --pool-interrupt')
    parser.add_argument('--pool-interrupt', action='store_true',
                        help='stop writer after sync before export, then fresh readonly recovery; requires diagnostic data import pair')
    parser.add_argument('--pool-corrupt-labels', action='store_true',
                        help='reject four malformed label headers after writer export; requires diagnostic data import pair')
    parser.add_argument('--namespace-ipc', action='store_true',
                        help='private admission-bound storage request/reply profile (requires --pool-namespace)')
    parser.add_argument('--pool-zpl-recover', action='store_true',
                        help='build-only readonly modified-ZPL reader; requires isolated namespace diagnostics')
    parser.add_argument('--pool-zpl-write', action='store_true',
                        help='build-only original ZPL writer (requires isolated namespace/build diagnostics)')
    parser.add_argument('--pool-namespace', action='store_true',
                        help='read the pinned upstream ZPL fixture; requires exclusive diagnostic pool import')
    parser.add_argument('--pool-data', action='store_true',
                        help='opt-in assigned dataset write/fresh readonly read; requires explicit diagnostic pool case')
    parser.add_argument('--pool-create', action='store_true',
                        help='create/export a disposable pool within current grants; requires corrected --engine-utc')
    parser.add_argument('--spa-physical', action='store_true',
                        help='qualify real vdev/physical read and controls; requires corrected --engine-utc')
    parser.add_argument('--spa-write', action='store_true',
                        help='qualify physical write/flush and fresh-VM read; requires corrected --engine-utc')
    parser.add_argument('--spa-active', action='store_true',
                        help='qualify activation/root ZIO and controls; requires corrected --engine-utc')
    parser.add_argument('--delivery', type=Path, required=True)
    parser.add_argument('--utc-delivery', type=Path)
    parser.add_argument('--case', choices=('normal', 'stop', 'disabled', 'early', *REAPER_CASES, EXHAUSTION_CASE, 'missing', 'version', 'cache',
                                          'no-fini', 'no-finish', 'no-entropy', 'write-mode', 'rtc', 'rtc-leap', 'rtc-disabled',
                                          'block-write', 'block-verify', 'block-readonly', 'block-corrupt', *WORKER_CASES, *SPA_UTC_CASES, *UTC_CASES, *ACTIVE_CASES, *PHYSICAL_CASES, *POOL_CASES))
    profiles = parser.add_mutually_exclusive_group()
    profiles.add_argument('--openzfs-waits', action='store_true',
                          help='compose actual selected OpenZFS CV/mutex callers; no engine entry')
    profiles.add_argument('--engine-link', action='store_true',
                          help='build selected ports/runtime/lifecycle; never execute the engine')
    profiles.add_argument('--startup-config', action='store_true',
                          help='test private declared storage metadata and empty-cache binding')
    profiles.add_argument('--engine-native', action='store_true',
                          help='qualify empty engine startup/fini and three large-owner generations')
    profiles.add_argument('--rtc-source', action='store_true',
                          help='qualify raw q35/TCG source intake; never establish runtime UTC')
    profiles.add_argument('--engine-utc', action='store_true',
                          help='intake sealed opt-in shared UTC and qualify actual engine time consumers')
    profiles.add_argument('--engine-spa-utc', action='store_true',
                          help='prove actual SPA setup fails closed on unavailable shared UTC')
    profiles.add_argument('--engine-volume-workers', action='store_true',
                          help='qualify actual queued worker I/O, bounds, revoke and drain; disposable disk only')
    profiles.add_argument('--engine-volume', action='store_true',
                          help='qualify actual file-vdev/Rust region binding; fresh disposable disk only')
    profiles.add_argument('--block-region', action='store_true',
                          help='qualify maintained runtime with one-hop volume transfer; fresh disposable disk only')
    parser.add_argument('--namespace-wait', action='store_true', help='private ABI26 primary-only channel waits; requires readonly namespace IPC import')
    args = parser.parse_args()
    if args.namespace_wait and not (args.namespace_ipc and args.pool_namespace and args.pool_diagnose in ('build','run') and args.case=='pool-import' and args.fixed_reaper and args.engine_utc):
        parser.error('namespace wait requires fixed readonly namespace IPC import')
    if args.engine_link and args.case is not None:
        parser.error('--engine-link is incompatible with --case')
    if args.case in ('missing', 'version', 'cache') and not args.startup_config:
        parser.error('startup controls require --startup-config')
    if (args.rtc_source and args.case not in (None, 'rtc', 'rtc-leap', 'rtc-disabled')) or (
            not args.rtc_source and args.case in ('rtc', 'rtc-leap', 'rtc-disabled')):
        parser.error('RTC source cases require --rtc-source; ordinary selection is incompatible')
    if (args.engine_spa_utc and args.case not in (None, *SPA_UTC_CASES)) or (
            not args.engine_spa_utc and args.case in SPA_UTC_CASES):
        parser.error('SPA UTC controls require --engine-spa-utc')
    if (args.engine_utc and (args.utc_delivery is None or args.case not in (None, *UTC_CASES, *ACTIVE_CASES, *PHYSICAL_CASES, *POOL_CASES))) or (
            not args.engine_utc and (args.utc_delivery is not None or args.case in (*UTC_CASES, *ACTIVE_CASES, *PHYSICAL_CASES, *POOL_CASES))):
        parser.error('UTC engine cases require --engine-utc and --utc-delivery')
    volume = args.block_region or args.engine_volume
    if (volume and args.case not in (None, 'block-write', 'block-readonly', 'block-corrupt')) or (
            not volume and args.case in ('block-write', 'block-verify', 'block-readonly', 'block-corrupt')):
        parser.error('volume cases require --block-region; fresh-VM verify requires the full sequence')
    if (args.engine_volume_workers and args.case not in (None, *WORKER_CASES)) or (
            not args.engine_volume_workers and args.case in WORKER_CASES):
        parser.error('queued volume cases require --engine-volume-workers')
    if (args.engine_native and args.case not in (None, 'no-fini', 'no-finish', 'no-entropy', 'write-mode')) or (
            not args.engine_native and args.case in ('no-fini', 'no-finish', 'no-entropy', 'write-mode')):
        parser.error('engine admission controls require --engine-native; ordinary case selection is incompatible')
    if args.fixed_reaper and any((args.openzfs_waits, args.engine_link, args.startup_config, args.engine_native, args.rtc_source, args.block_region, args.engine_volume, args.engine_volume_workers, args.engine_spa_utc)):
        parser.error('fixed-reaper intake supports elapsed regressions and shared UTC only')
    if (args.spa_physical or args.case in PHYSICAL_CASES) and (args.spa_active or not (args.fixed_reaper and args.engine_utc) or args.case not in (None, *PHYSICAL_CASES)):
        parser.error('--spa-physical requires corrected --engine-utc and exclusive physical cases')
    if args.pool_zpl_recover and (not args.pool_namespace or args.namespace_ipc or args.pool_zpl_write or args.pool_diagnose != 'build'):
        parser.error('ZPL recovery requires isolated build-only namespace profile')
    if args.pool_zpl_write and (not args.pool_namespace or args.namespace_ipc or args.pool_diagnose != 'build'):
        parser.error('ZPL writer requires isolated build-only namespace profile')
    if args.namespace_ipc and not args.pool_namespace:
        parser.error('namespace IPC requires namespace profile')
    if args.pool_namespace and (not (args.pool_create and args.pool_diagnose and args.case == 'pool-import') or
            args.pool_data or args.pool_interrupt or args.pool_uncommitted or args.pool_corrupt_labels or args.pool_recovery_check):
        parser.error('namespace requires exclusive diagnostic pool import')
    if args.pool_recovery_check is not None and (
            not (args.pool_data and args.pool_create and args.pool_diagnose and args.case == 'pool-import') or
            args.pool_interrupt or args.pool_uncommitted or args.pool_corrupt_labels):
        parser.error('--pool-recovery-check requires exclusive diagnostic data import pair')
    if args.pool_uncommitted and not args.pool_interrupt:
        parser.error('--pool-uncommitted requires --pool-interrupt')
    if args.pool_interrupt and not (args.pool_data and args.pool_create and args.pool_diagnose and args.case == 'pool-import' and not args.pool_corrupt_labels):
        parser.error('--pool-interrupt requires exclusive diagnostic data import pair')
    if args.pool_corrupt_labels and not (args.pool_data and args.pool_create and args.pool_diagnose and args.case == 'pool-import'):
        parser.error('--pool-corrupt-labels requires explicit diagnostic data import pair')
    if args.pool_data and (not args.pool_create or not args.pool_diagnose or args.case not in POOL_CASES):
        parser.error('--pool-data requires explicit diagnostic pool case')
    if args.pool_diagnose and not args.pool_create:
        parser.error('pool diagnostics require --pool-create')
    if (args.pool_create or args.case in POOL_CASES) and (
            not (args.pool_create and args.engine_utc and args.fixed_reaper) or
            args.spa_active or args.spa_physical or args.spa_write or
            args.case not in (None, *POOL_CASES)):
        parser.error('--pool-create requires corrected --engine-utc and exclusive pool cases')
    if args.spa_write and (args.spa_physical or args.spa_active or not (args.fixed_reaper and args.engine_utc) or args.case not in (None, *WRITE_CASES)):
        parser.error('--spa-write requires corrected --engine-utc and exclusive write cases')
    if args.case == 'spa-physical-write-verify':
        parser.error('fresh-VM physical verify requires the full --spa-write sequence')
    if args.spa_active and (not (args.fixed_reaper and args.engine_utc) or args.case not in (None, *ACTIVE_CASES)):
        parser.error('--spa-active requires corrected --engine-utc and activation cases')
    if args.case in ACTIVE_CASES and not args.fixed_reaper:
        parser.error('SPA activation requires --fixed-reaper')
    if args.case == EXHAUSTION_CASE and not args.fixed_reaper:
        parser.error('lifetime exhaustion requires --fixed-reaper')
    try:
        suite(args.delivery, args.case, args.openzfs_waits, args.engine_link, args.startup_config, args.engine_native, args.rtc_source, args.block_region, args.engine_volume, args.engine_volume_workers, args.engine_spa_utc, args.engine_utc, args.utc_delivery, args.fixed_reaper, args.spa_active, args.spa_physical, args.spa_write, args.pool_create, args.pool_diagnose, args.pool_data, args.pool_corrupt_labels, args.pool_interrupt, args.pool_uncommitted, args.pool_recovery_check, args.pool_namespace, args.namespace_ipc, args.pool_zpl_write, args.pool_zpl_recover, namespace_wait=args.namespace_wait)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        parser.exit(1, display(error) + '\n')
