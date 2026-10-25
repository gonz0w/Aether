# SPDX-License-Identifier: BSD-2-Clause
"""Guarded private ZPL overwrite and fresh-VM readonly readback; no retries."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from deps import ROOT
from evidence import compact_run
from native_smoke import NativeStopError, run
from openzfs_namespace import (native_media_snapshot, prepare_native_fixture,
                               written_native_media_snapshot)
import service_runtime_smoke as runtime

MARKER = 'AETHER NATIVE BLOCK PASS'
PREFIX = 'thread-suite-service-runtime-zpl-pair-'
ERROR_STAGES = ('open', 'root', 'lookup', 'baseline-hash', 'UTC', 'write',
                'progress', 'fresh-lookup', 'readback')


def decode_zpl_error(serial, recovery=False, write_lifetimes=False):
    """Failure attribution only; never accepts a transaction or cleanup."""
    from openzfs_fs_bridge import RECOVERY_STAGES
    if not isinstance(write_lifetimes, bool) or (recovery and write_lifetimes):
        raise ValueError('write lifetime errors require the fixed writer profile')
    stages = RECOVERY_STAGES if recovery else ERROR_STAGES + (('record-retirement',) if write_lifetimes else ())
    raw = [line for line in serial.splitlines() if line.startswith('NATIVE observation ')]
    pattern = r'NATIVE observation slot=0 generation=1 offset=(\d+) byte=(\d+)'
    matches = [re.fullmatch(pattern, line) for line in raw]
    if len(matches) != 25 or any(m is None for m in matches):
        raise ValueError('ZPL error requires exact25-row failed writer trace')
    values = []
    for index, match in enumerate(matches):
        offset, byte = map(int, match.groups())
        if offset != index * 8 or not 0 <= byte <= 255:
            raise ValueError('ZPL error observation identity/value')
        values.append(byte)
    prefix = b'BIUVWLP????????OAMTE'
    if any(value != prefix[i] for i, value in enumerate(values[:20]) if not 7 <= i < 15):
        raise ValueError('ZPL error phase prefix')
    stage = values[20]
    error = int.from_bytes(bytes(values[21:25]), 'little')
    terminal = re.findall(r'^NATIVE terminal .*$', serial, re.M)
    cleanup = [line for line in serial.splitlines() if line.startswith('NATIVE CLEANUP ')]
    expected = [f'NATIVE CLEANUP v=1 slot=0 generation=1 phase={phase} '
                f'selected={0 if phase == 1 else 2} pages=8192 reclaimed=0' for phase in (1, 2)]
    if (not 1 <= stage <= len(stages) or not 1 <= error <= 4095 or
            terminal != ['NATIVE terminal slot=0 generation=1 kind=1 detail=873'] or
            cleanup != expected or serial.count('NATIVE supervisor result=401 reclaimed=0\n') != 1 or
            MARKER in serial):
        raise ValueError('ZPL error stage/errno/failed lifetime mismatch')
    return {'format': 'aether-zpl-probe-error-v1', 'stage': stage,
            'operation': stages[stage - 1], 'errno': error,
            'scope': 'private probe failure only; assignment/commit and retirement remain unqualified'}


STAGE_TAGS = b'BIUVWLPOAMTorhc12vx????????SDJFR'
TXG_WORKER_TAGS = b'BIUVWLPOAMTbqsluodw????????SDJFR'
TXG_WORKER_PATHS = (b'bqsluodw',) + tuple(b'bqsluod'[:n] + b'w' for n in range(1, 7))
TXG_WORKER_NAMES = ('target-bound', 'quiesce-return-before-handoff', 'sync-worker-unlocked',
                    'block-root-return', 'uberblock-write-root-return',
                    'odd-label-flush-root-return', 'spa-sync-return', 'wait-return')
SYNC_STAGE_TAGS = b'BIUVWLPOAMTbeicpvrw????????SDJFR'
SYNC_STAGE_PATHS = (b'beicpvrw',) + tuple(b'beicpvr'[:n] + b'w' for n in range(1, 7))
SYNC_STAGE_NAMES = ('target-bound', 'spa-sync-entry', 'initial-open-io-wait-return',
                    'configuration-state-setup-complete', 'first-dataset-sync-entry',
                    'first-dataset-io-wait-return', 'convergence-return', 'wait-return')
FIRST_WRITE_TAGS = b'BIUVWLPOAMTeabcdwsf????????SDJFR'
FIRST_WRITE_PATHS = (b'eabcdwsf', b'ef', b'eabf', b'eabcdf')
FIRST_WRITE_NAMES = ('write-entry', 'assignment-entry', 'assignment-return',
                     'commit-entry', 'commit-return', 'sync-wait-entry',
                     'sync-wait-return', 'write-return-after-SA-cleanup')
STAGE_NAMES = ('open-entry', 'open-return', 'baseline-hash-entry', 'UTC-entry',
               'first-write-entry', 'second-write-entry-after-first-checked',
               'readback-entry-after-second-checked', 'readback-and-close-complete')


def decode_zpl_stages(serial, first_write=False, txg_worker=False, sync_stages=False):
    if sync_stages and not txg_worker:
        raise ValueError("sync stages require worker profile")
    """Strict observed prefix only; never completion, durability or reclaim."""
    if first_write and txg_worker:
        raise ValueError('TXG worker and helper stages are exclusive')
    detailed = first_write or txg_worker
    paths = SYNC_STAGE_PATHS if sync_stages else TXG_WORKER_PATHS if txg_worker else FIRST_WRITE_PATHS
    raw = [line for line in serial.splitlines() if line.startswith('NATIVE observation ')]
    pattern = r'NATIVE observation slot=(\d+) generation=(\d+) offset=(\d+) byte=(\d+)'
    matches = [re.fullmatch(pattern, line) for line in raw]
    if not matches or any(m is None for m in matches):
        raise ValueError('ZPL stages require exact observation syntax')
    rows = [tuple(map(int, m.groups())) for m in matches]
    primary = []
    tail = []
    for row in rows:
        if row[1] == 1 and not tail:
            primary.append(row)
        else:
            tail.append(row)
    if len(primary) > 32:
        raise ValueError('ZPL stage observation capacity')
    values = []
    for index, (slot, generation, offset, byte) in enumerate(primary):
        if (slot, generation, offset) != (0, 1, index * 8) or not 0 <= byte <= 255:
            raise ValueError('ZPL stage observation identity/value')
        values.append(byte)
    error = None
    error_start = next((i for i, value in enumerate(values) if value == ord('E') and i < 19), None)
    # At row19 E can also be a legitimate low TXG byte. Only the original
    # complete failed lifetime disambiguates a full eight-marker error suffix.
    if detailed and error_start is None and len(values) == 25 and values[19] == ord('E'):
        terminal = re.findall(r'^NATIVE terminal .*$', serial, re.M)
        cleanup = [line for line in serial.splitlines() if line.startswith('NATIVE CLEANUP ')]
        expected_cleanup = [f'NATIVE CLEANUP v=1 slot=0 generation=1 phase={phase} '
                            f'selected={0 if phase == 1 else 2} pages=8192 reclaimed=0' for phase in (1, 2)]
        if (terminal == ['NATIVE terminal slot=0 generation=1 kind=1 detail=873'] and
                cleanup == expected_cleanup and
                serial.count('NATIVE supervisor result=401 reclaimed=0\n') == 1 and MARKER not in serial):
            error_start = 19
    progress = values if error_start is None else values[:error_start]
    expected = SYNC_STAGE_TAGS if sync_stages else TXG_WORKER_TAGS if txg_worker else FIRST_WRITE_TAGS if first_write else STAGE_TAGS
    markers = bytes(progress[11:19])
    if detailed and not any(path.startswith(markers) for path in paths):
        raise ValueError('first-write stage path/order')
    for index, byte in enumerate(progress):
        if detailed and 11 <= index < 19:
            continue
        if not 19 <= index < 27 and byte != expected[index]:
            raise ValueError('ZPL stage prefix/order')
    if error_start is not None:
        suffix = values[error_start:]
        if len(suffix) > 6 or (len(suffix) >= 2 and not 1 <= suffix[1] <= 9):
            raise ValueError('ZPL stage error shape')
        boundaries = {1: (12,), 2: (13,), 3: (13,), 4: (14,), 5: (15,),
                      6: (16, 17), 7: (17,), 8: (18,), 9: (18,)}
        if detailed:
            complete = markers in paths
            if len(suffix) >= 2:
                stage = suffix[1]
                valid = (stage <= 5 and len(progress) == 11 or
                         stage == 6 and (txg_worker or complete) or stage >= 7 and markers == paths[0])
                if not valid:
                    raise ValueError('first-write error boundary mismatch')
            if len(progress) not in (11, 11 + len(markers)) or (markers and not complete and not txg_worker):
                raise ValueError('first-write error before helper return')
        elif len(suffix) >= 2 and len(progress) not in boundaries[suffix[1]]:
            raise ValueError('ZPL stage error boundary mismatch')
        if len(suffix) == 6:
            code = int.from_bytes(bytes(suffix[2:]), 'little')
            if not 1 <= code <= 4095:
                raise ValueError('ZPL stage errno bounds')
            error = {'stage': suffix[1], 'errno': code}
    expected_tail = [(0, g, i * 8, byte) for g in (2, 3) for i, byte in enumerate(b'BNR')]
    if tail and (len(progress) != 32 or error_start is not None or tail != expected_tail[:len(tail)]):
        raise ValueError('ZPL stage replacement prefix')
    names = SYNC_STAGE_NAMES if sync_stages else TXG_WORKER_NAMES if txg_worker else FIRST_WRITE_NAMES if first_write else STAGE_NAMES
    seen = max(0, min(len(progress) - 11, len(names)))
    alphabet = b'beicpvrw' if sync_stages else b'bqsluodw' if txg_worker else b'eabcdwsf'
    observed = ([names[alphabet.index(byte)] for byte in markers] if detailed else list(names[:seen]))
    return {'format': 'aether-zpl-stage-progress-v1',
            'primary_rows': len(primary), 'observed_boundaries': observed,
            'last_boundary': observed[-1] if observed else None,
            'error_projection': error, 'qualification': False,
            'scope': 'observed prefix only; operation completion/commit, root cause and reclaim unqualified'}


def verify_prepared(output, builds, repeated_writes=False, stage_diagnostic=False, first_write=False, txg_worker=False, sync_stages=False, writer_ticks_6000=False, filesystem_bridge=None, recovery_diagnostic=False, writer_60s=False, truncate_zero=False, namespace_mutation=None, filesystem_service=None, filesystem_service_case='normal', filesystem_service_lifetimes=False, filesystem_service_namespace=False, filesystem_service_mixed=False, filesystem_service_wait=False, filesystem_service_bulk=False, filesystem_service_runtime=False, filesystem_service_activation=False, filesystem_service_names=False, filesystem_service_directories=False, storage_lifetime=False):
    from storage_lifetime import validate as validate_storage_lifetime
    validate_storage_lifetime(storage_lifetime, filesystem_service_directories, False, filesystem_service_case)
    if not isinstance(filesystem_service_directories,bool) or (filesystem_service_directories and not filesystem_service_names):
        raise ValueError('directories require explicit names selection')
    if not isinstance(filesystem_service_names,bool) or (filesystem_service_names and not filesystem_service_activation):
        raise ValueError('names require explicit activation selection')
    if not isinstance(filesystem_service_activation,bool) or (filesystem_service_activation and not (filesystem_service_runtime and filesystem_service is not None)):
        raise ValueError('activation requires explicit runtime service pair')
    if not isinstance(filesystem_service_runtime,bool) or (filesystem_service_runtime and not filesystem_service_bulk):
        raise ValueError('runtime requires explicit bulk pair')
    if not isinstance(filesystem_service_bulk,bool) or (filesystem_service_bulk and not (filesystem_service_wait and filesystem_service_mixed)):
        raise ValueError('bulk requires explicit mixed waiting pair')
    if not isinstance(filesystem_service_wait,bool) or (filesystem_service_wait and not filesystem_service_mixed):
        raise ValueError('service wait requires explicit mixed selection')
    from openzfs_fs_service import case_number
    service_case = case_number(filesystem_service_case)
    if not isinstance(filesystem_service_mixed,bool) or (filesystem_service_mixed and
            (filesystem_service is None or filesystem_service_lifetimes or filesystem_service_namespace or namespace_mutation is not None)):
        raise ValueError('filesystem service mixed requires exclusive matching selection')
    if not isinstance(filesystem_service_namespace, bool):
        raise ValueError('filesystem service namespace selector must be boolean')
    if filesystem_service_namespace and (filesystem_service is None or filesystem_service_lifetimes or
            namespace_mutation not in ('create', 'rename', 'remove') or service_case == 2):
        raise ValueError('filesystem service namespace requires exact one-attempt selection')
    if not isinstance(filesystem_service_lifetimes, bool) or (filesystem_service_lifetimes and filesystem_service is None):
        raise ValueError('filesystem service lifetimes require exact service selection')
    if service_case and filesystem_service is None:
        raise ValueError('filesystem service case requires its exact selection')
    from openzfs_mutation import validate as validate_mutation
    validate_mutation(namespace_mutation)
    if namespace_mutation is not None and (truncate_zero or filesystem_bridge is not None or (filesystem_service is not None and not filesystem_service_namespace) or
            any((stage_diagnostic, first_write, txg_worker, sync_stages)) or
            repeated_writes is not (namespace_mutation in ('repeat', 'eight', 'lifetimes')) or
            not (writer_ticks_6000 and writer_60s and recovery_diagnostic)):
        raise ValueError('namespace mutation requires exclusive fixed-budget preparation')
    if not isinstance(truncate_zero, bool):
        raise ValueError('truncate zero selector must be boolean')
    if truncate_zero and (filesystem_bridge is not None or any((repeated_writes,
            stage_diagnostic, first_write, txg_worker, sync_stages))):
        raise ValueError('truncate zero requires exclusive single-transaction pair')
    if not isinstance(writer_60s, bool):
        raise ValueError('writer window selector must be boolean')
    if writer_60s and not (sync_stages or filesystem_bridge is not None or filesystem_service is not None or truncate_zero or namespace_mutation is not None):
        raise ValueError('writer window requires approved writer profile')
    if (writer_ticks_6000 or filesystem_bridge is not None or filesystem_service is not None or truncate_zero or namespace_mutation is not None) and not writer_60s:
        raise ValueError('writer window requires writer60')
    if recovery_diagnostic and filesystem_bridge is None and filesystem_service is None and not truncate_zero and namespace_mutation is None:
        raise ValueError('recovery diagnostic requires filesystem bridge pair')
    if filesystem_bridge is not None and (not writer_ticks_6000 or
            any((repeated_writes, stage_diagnostic, first_write, txg_worker, sync_stages))):
        raise ValueError('filesystem bridge requires exclusive fixed-budget single-write preparation')
    if not isinstance(writer_ticks_6000, bool):
        raise ValueError('writer tick budget selector must be boolean')
    if writer_ticks_6000 and not (sync_stages or filesystem_bridge is not None or filesystem_service is not None or truncate_zero or namespace_mutation is not None):
        raise ValueError("writer tick budget requires sync-stage diagnostic")
    if sync_stages and not txg_worker:
        raise ValueError("sync stages require worker profile")
    """Recheck independent build outcomes and their actual launch inputs."""
    if txg_worker and (not stage_diagnostic or first_write):
        raise ValueError('TXG worker diagnostic requires exclusive stage profile')
    if first_write and not stage_diagnostic:
        raise ValueError('first-write diagnostic requires stage profile')
    if stage_diagnostic and not repeated_writes:
        raise ValueError('stage diagnostic requires repeated writes')
    if truncate_zero and not (writer_ticks_6000 and recovery_diagnostic):
        raise ValueError('truncate zero requires fixed-budget diagnostic reader')
    if filesystem_service is not None and (filesystem_bridge is not None or truncate_zero or (namespace_mutation is not None and not filesystem_service_namespace) or
            any((repeated_writes, stage_diagnostic, first_write, txg_worker, sync_stages)) or
            not (writer_ticks_6000 and writer_60s and recovery_diagnostic)):
        raise ValueError('filesystem service requires exclusive fixed-budget preparation')
    from openzfs_fs_service import intake as service_intake
    service = service_intake(filesystem_service, filesystem_service_lifetimes, filesystem_service_namespace, filesystem_service_mixed,filesystem_service_wait,filesystem_service_bulk,filesystem_service_runtime,filesystem_service_activation,filesystem_service_names,filesystem_service_directories) if filesystem_service is not None else None
    from openzfs_fs_bridge import intake as bridge_intake
    bridge = bridge_intake(filesystem_bridge) if filesystem_bridge is not None else None
    roles = {'baseline', 'writer', 'reader'} if txg_worker or bridge is not None or service is not None or truncate_zero or namespace_mutation is not None else {'writer', 'reader'}
    if set(builds) != roles:
        raise ValueError('ZPL pair requires all prepared images')
    if any(build['sources'] != builds['writer']['sources'] for build in builds.values()):
        raise ValueError('ZPL pair build sources differ')
    for role, build in builds.items():
        if (build.get('status') != 'pass' or build.get('pool_diagnose') != 'build' or
                build.get('pool_namespace') is not True or build.get('namespace_ipc') is not (service is not None and role == 'writer') or
                build.get('namespace_wait',False) is not (filesystem_service_wait and role=='writer') or
                build.get('pool_zpl_write') is not (role == 'writer') or
                build.get('pool_zpl_recover') is not (role == 'reader') or
                build.get('pool_zpl_repeat', False) is not (repeated_writes and role == 'writer') or
                build.get('pool_zpl_stages', False) is not (stage_diagnostic and role == 'writer') or
                build.get('pool_zpl_write_stages', False) is not (first_write and role == 'writer') or
                build.get('pool_zpl_txg_stages', False) is not (txg_worker and role == 'writer') or
                build.get('pool_zpl_sync_stages', False) is not (sync_stages and role == 'writer') or
                build.get('namespace_mutation') != (namespace_mutation if role != 'baseline' else None) or
                build.get('fs_namespace_operation') != (namespace_mutation if filesystem_service_namespace and role != 'baseline' else None) or
                build.get('storage_lifetime',False) is not (storage_lifetime and role!='baseline') or
                build.get('fs_service_directories',False) is not (filesystem_service_directories and role!='baseline') or
                build.get('fs_service_names',False) is not (filesystem_service_names and role!='baseline') or
                build.get('fs_service_activation',False) is not (filesystem_service_activation and role=='writer') or
                build.get('fs_service_runtime',False) is not (filesystem_service_runtime and role!='baseline') or
                build.get('fs_service_bulk',False) is not (filesystem_service_bulk and role != 'baseline') or
                build.get('fs_service_mixed',False) is not (filesystem_service_mixed and role != 'baseline') or
                build.get('fs_service_mixed_empty',False) is not (filesystem_service_mixed and role == 'reader' and (service_case == 1 or (filesystem_service_bulk and service_case == 2))) or
                build.get('pool_zpl_zero', False) is not (truncate_zero and role != 'baseline') or
                build.get('pool_recovery_diagnostic', False) is not (recovery_diagnostic and role == 'reader') or
                build.get('pool_recovery_writer_60s', False) is not (writer_60s and role == 'reader') or
                build.get('pool_zpl_writer_budget', False) is not (writer_ticks_6000 and role == 'writer') or
                build.get('delivery_seal') != runtime.FIXED_SEAL or
                build.get('utc_delivery_seal') != runtime.FIXED_UTC_SEAL or
                len(build.get('cases', [])) != 1):
            raise ValueError('ZPL pair build profile or seal mismatch')
        # The profile flag alone cannot attest to the kernel that was built.
        kernel_commands = [c['argv'] for c in build.get('commands', [])
                           if c.get('argv', [])[:2] == ['zig', 'build']]
        life_options=[arg for command in kernel_commands for arg in command if arg.startswith('-Dnative-service-lifetime=')]
        life_cfgs=[args[i+1] for c in build.get('commands',[]) for args in [c.get('argv',[])]
                   if any('link-arg=--oformat=binary' in str(a) for a in args)
                   for i,arg in enumerate(args[:-1]) if arg=='--cfg' and args[i+1]=='fs_storage_lifetime']
        if life_options != (['-Dnative-service-lifetime=true'] if storage_lifetime and role=='writer' else []) or life_cfgs != (['fs_storage_lifetime'] if storage_lifetime and role=='writer' else []):
            raise ValueError('storage lifetime actual kernel/controller selection mismatch')
        directory_cfgs=[args[i+1] for c in build.get('commands',[]) for args in [c.get('argv',[])]
                        if any('link-arg=--oformat=binary' in str(a) for a in args)
                        for i,arg in enumerate(args[:-1]) if arg=='--cfg' and args[i+1]=='fs_directories']
        if directory_cfgs != (['fs_directories'] if filesystem_service_directories and role=='writer' else []):
            raise ValueError('directories actual driver cfg mismatch')
        name_cfgs=[args[i+1] for c in build.get('commands',[]) for args in [c.get('argv',[])]
                   if any('link-arg=--oformat=binary' in str(a) for a in args)
                   for i,arg in enumerate(args[:-1]) if arg=='--cfg' and args[i+1]=='fs_names']
        if name_cfgs != (['fs_names'] if filesystem_service_names and role=='writer' else []):
            raise ValueError('names actual driver cfg mismatch')
        activation_options=[arg for command in kernel_commands for arg in command if arg.startswith('-Dnative-service-activation=')]
        if activation_options != (['-Dnative-service-activation=true'] if filesystem_service_activation and role=='writer' else []):
            raise ValueError('activation actual kernel option mismatch')
        budget_options = [arg for command in kernel_commands for arg in command
                          if arg.startswith('-Dnative-service-zpl-budget=')]
        if (writer_ticks_6000 and role == 'writer' and
                (len(kernel_commands) != 1 or budget_options != ['-Dnative-service-zpl-budget=true'])) or (
                not (writer_ticks_6000 and role == 'writer') and budget_options):
            raise ValueError('ZPL pair kernel tick budget option mismatch')
        wait_options=[arg for args in kernel_commands for arg in args if arg.startswith('-Dnative-service-channel-wait=')]
        if wait_options != (['-Dnative-service-channel-wait=true'] if filesystem_service_wait and role=='writer' else []):
            raise ValueError('ZPL pair wait kernel option mismatch')
        channel_options = [arg for command in kernel_commands for arg in command
                           if arg.startswith('-Dnative-service-channel=')]
        if channel_options != (['-Dnative-service-channel=true'] if service is not None and role == 'writer' else []):
            raise ValueError('ZPL pair kernel channel option mismatch')
        expected_lifetimes = filesystem_service_lifetimes and (role == 'writer' or
            (role == 'reader' and service_case != 1))
        if build.get('fs_service_lifetimes', False) is not expected_lifetimes:
            raise ValueError('ZPL pair filesystem service lifetime profile mismatch')
        if service is not None and role == 'writer' and build.get('fs_service_case') != filesystem_service_case:
            raise ValueError('ZPL pair filesystem service case mismatch')
        if build.get('fs_service') != (service if role == 'writer' else None):
            raise ValueError('ZPL pair filesystem service selection mismatch')
        if service is not None and role == 'writer':
            driver_commands = [c['argv'] for c in build.get('commands', [])
                               if any(arg in c.get('argv', []) for arg in
                                      ('-Clink-arg=--oformat=binary', 'link-arg=--oformat=binary'))]
            wait_cfgs=[args[i+1] for args in driver_commands for i,arg in enumerate(args[:-1]) if arg=='--cfg' and args[i+1]=='namespace_wait']
            wait_options=[arg for args in kernel_commands for arg in args if arg.startswith('-Dnative-service-channel-wait=')]
            if wait_cfgs != (['namespace_wait'] if filesystem_service_wait else []) or wait_options != (['-Dnative-service-channel-wait=true'] if filesystem_service_wait else []):
                raise ValueError('ZPL pair wait driver/kernel option mismatch')
            cfgs = [args[i + 1] for args in driver_commands for i, arg in enumerate(args[:-1])
                    if arg == '--cfg' and args[i + 1].startswith('fs_')]
            expected_cfgs = (['fs_directories'] if filesystem_service_directories else []) + (['fs_storage_lifetime'] if storage_lifetime else []) + (['fs_names'] if filesystem_service_names else []) + (['fs_activation'] if filesystem_service_activation else []) + (['fs_runtime'] if filesystem_service_runtime else []) + (['fs_bulk'] if filesystem_service_bulk else []) + (['fs_mixed'] if filesystem_service_mixed else []) + (['fs_namespace_'+namespace_mutation] if filesystem_service_namespace else []) + (['fs_eight_writes'] if filesystem_service_lifetimes else []) + (['fs_lost_reply'] if service_case == 1 else
                             ['fs_partial_request'] if service_case == 2 else [])
            partial_commands = [c['argv'] for c in build.get('commands', []) if '-r' in c.get('argv', [])
                                and any(str(a).endswith('/bridge-partial.map') for a in c['argv'])]
            wraps = [a for args in partial_commands for a in args if a.startswith('--wrap=')]
            if (len(driver_commands) != 1 or cfgs != expected_cfgs or len(partial_commands) != 1 or
                    wraps != (['--wrap=aether_zpl_close'] if service_case == 3 else [])):
                raise ValueError('ZPL pair filesystem service driver/wrap option mismatch')
            from openzfs_fs_service import probe, sha
            objects = build.get('port', {}).get('volume', {}).get('namespace_objects', {})
            original = ROOT / 'user/storage/openzfs-volume'
            if objects.get('fs-service-consumer') != sha(service['object']):
                raise ValueError('ZPL pair filesystem service object mismatch')
            if filesystem_service_mixed:
                from openzfs_fs_mixed_service import owner as mixed_owner
                from openzfs_fs_mixed import mixed_lifetime_hooks,mixed_lifetime_record
                if filesystem_service_bulk:
                    from openzfs_fs_bulk_service import owner as mixed_owner
                    from openzfs_fs_bulk import bulk_lifetime_hooks as mixed_lifetime_hooks,bulk_lifetime_record as mixed_lifetime_record
                if filesystem_service_runtime:
                    from openzfs_fs_runtime_service import owner as mixed_owner
                if filesystem_service_activation:
                    from openzfs_fs_activation_service import owner as mixed_owner
                if filesystem_service_names:
                    from openzfs_fs_names_service import owner as mixed_owner
                if filesystem_service_directories:
                    from openzfs_fs_directories_service import owner as mixed_owner
                expected=hashlib.sha256(mixed_owner((original/'fs-service-owner.inc').read_text(),filesystem_service_wait).encode()).hexdigest()
                origins=build.get('port',{}).get('fs_service_origins',{})
                required={name:'zpl-mutation.o' for name in ('aether_zpl_open_write','aether_zpl_close','aether_zpl_root',
                    'aether_zpl_lookup','aether_zpl_read','aether_zpl_write','aether_zpl_create','aether_zpl_rename','aether_zpl_remove')}
                required.update(aether_fs_mixed_run='filesystem-mixed.o',aether_pool_namespace0_retire='vdev-selected.o',aether_pool_service16_retire='vdev-selected.o')
                if filesystem_service_wait:
                    required.pop('aether_fs_mixed_run')
                    required['aether_fs_mixed_wait_run']='filesystem-mixed-wait.o'
                if filesystem_service_bulk:
                    required.pop('aether_fs_mixed_wait_run');required.pop('aether_pool_service16_retire')
                    required.update(aether_fs_bulk_run='filesystem-bulk.o',aether_pool_service_bytes_retire='vdev-selected.o')
                if filesystem_service_runtime:
                    required.pop('aether_fs_bulk_run');required['aether_fs_runtime_run']='filesystem-runtime.o'
                if filesystem_service_activation:
                    required.pop('aether_fs_runtime_run');required['aether_fs_activation_run']='filesystem-activation.o'
                if filesystem_service_names:
                    required.pop('aether_fs_activation_run');required['aether_fs_names_run']='filesystem-names.o'
                if filesystem_service_directories:
                    required.pop('aether_fs_names_run');required['aether_fs_directories_run']='filesystem-directories.o'
                    required.update({n:'zpl-mutation.o' for n in ('aether_zpl_directory','aether_zpl_mkdir','aether_zpl_rmdir')})
                if service_case==3:required['__wrap_aether_zpl_close']='zpl-mutation.o'
                if objects.get('mixed-owner-source')!=expected or set(origins)!=set(required) or any(not origins[n].endswith('/'+owner) for n,owner in required.items()):
                    raise ValueError('ZPL pair mixed owner/origin mismatch')
                if (objects.get('mixed-hooks-source')!=hashlib.sha256(mixed_lifetime_hooks((original/'pool-vdev-hooks.inc').read_text()).encode()).hexdigest() or
                        objects.get('mixed-record-source')!=hashlib.sha256(mixed_lifetime_record((original/'pool-lifetime.inc').read_text()).encode()).hexdigest()):
                    raise ValueError('ZPL pair mixed typed retirement source mismatch')
            elif filesystem_service_namespace:
                from openzfs_fs_namespace import owner as namespace_owner
                expected = hashlib.sha256(namespace_owner((original/'fs-service-owner.inc').read_text()).encode()).hexdigest()
                origins = build.get('port', {}).get('fs_service_origins', {})
                required = {name:'zpl-mutation.o' for name in ('aether_zpl_open_write', 'aether_zpl_close',
                    'aether_zpl_root', 'aether_zpl_lookup', 'aether_zpl_read', 'aether_zpl_write',
                    'aether_zpl_create', 'aether_zpl_rename', 'aether_zpl_remove')}
                required['aether_fs_namespace_run'] = 'filesystem-namespace.o'
                if service_case == 3: required['__wrap_aether_zpl_close'] = 'zpl-mutation.o'
                if (objects.get('fs-namespace-owner-source') != expected or set(origins) != set(required) or
                        any(not origins[name].endswith('/'+owner) for name,owner in required.items())):
                    raise ValueError('ZPL pair filesystem service namespace owner/origin mismatch')
            elif (objects.get('fs-service-owner-source') != sha(original / 'fs-service-owner.inc') or
                    objects.get('fs-service-probe-source') != hashlib.sha256(probe((original / 'zpl-write-probe.c').read_text(), filesystem_service_case, filesystem_service_lifetimes).encode()).hexdigest()):
                raise ValueError('ZPL pair filesystem service source mismatch')
            if filesystem_service_lifetimes:
                from openzfs_fs_lifetime import service_lifetime_hooks, service_lifetime_record
                expected_hooks = service_lifetime_hooks((original / 'pool-vdev-hooks.inc').read_text())
                expected_record = service_lifetime_record((original / 'pool-lifetime.inc').read_text())
                if (objects.get('service-lifetime-hooks-source') != hashlib.sha256(expected_hooks.encode()).hexdigest() or
                        objects.get('service-lifetime-record-source') != hashlib.sha256(expected_record.encode()).hexdigest() or
                        not build.get('port', {}).get('fs_service_origins', {}).get('aether_pool_service16_retire', '').endswith('/vdev-selected.o')):
                    raise ValueError('ZPL pair service lifetime observer/origin mismatch')
        if build.get('fs_bridge') != (bridge if role == 'writer' else None):
            raise ValueError('ZPL pair filesystem bridge selection mismatch')
        if filesystem_service_mixed and role != 'baseline':
            from openzfs_fs_mixed_service import probe as mixed_probe
            if filesystem_service_bulk:
                from openzfs_fs_bulk_service import probe as mixed_probe
            if filesystem_service_runtime:
                from openzfs_fs_runtime_service import probe as mixed_probe
            if filesystem_service_names:
                from openzfs_fs_names_service import probe as mixed_probe
            if filesystem_service_directories:
                from openzfs_fs_directories_service import probe as mixed_probe
            from openzfs_namespace import recovery_label_source
            original=ROOT/'user/storage/openzfs-volume'
            expected=hashlib.sha256(mixed_probe((original/'zpl-mutation-probe.c').read_text(),role=='reader',
                (service_case==1 or (filesystem_service_bulk and service_case==2)),filesystem_service_case, **({'storage_lifetime':True} if storage_lifetime else {})).encode()).hexdigest()
            objects=build.get('port',{}).get('volume',{}).get('namespace_objects',{})
            label=(original/'namespace-label.inc').read_text()
            if role=='reader':label=recovery_label_source(label)
            if objects.get('mixed-probe-source')!=expected or objects.get('mixed-label-source')!=hashlib.sha256(label.encode()).hexdigest():
                raise ValueError('ZPL pair mixed probe/label source mismatch')
        elif namespace_mutation is not None and role != 'baseline':
            from openzfs_mutation import source_sha
            from openzfs_namespace import recovery_label_source
            objects = build.get('port', {}).get('volume', {}).get('namespace_objects', {})
            expected_source = source_sha(namespace_mutation, role == 'reader')
            if filesystem_service_namespace:
                from openzfs_fs_namespace import probe as namespace_probe
                original_probe = (ROOT/'user/storage/openzfs-volume/zpl-mutation-probe.c').read_text()
                expected_source = hashlib.sha256(namespace_probe(original_probe, namespace_mutation,
                    role == 'reader', filesystem_service_case, **({'storage_lifetime':True} if storage_lifetime else {})).encode()).hexdigest()
            if objects.get('mutation-selected-source') != expected_source:
                raise ValueError('namespace mutation selected source mismatch')
            if namespace_mutation in ('eight','lifetimes') and role == 'writer':
                from openzfs_pool import eight_write_hooks, lifetime_write_hooks
                hooks = (ROOT / 'user/storage/openzfs-volume/pool-vdev-hooks.inc').read_text()
                selected = lifetime_write_hooks if namespace_mutation == 'lifetimes' else eight_write_hooks
                if objects.get('vdev-write-hooks-source') != hashlib.sha256(selected(hooks).encode()).hexdigest():
                    raise ValueError('write observer source/count/budget mismatch')
            label = (ROOT / 'user/storage/openzfs-volume/namespace-label.inc').read_text()
            if role == 'reader' or namespace_mutation in ('rename', 'remove', 'extend', 'repeat', 'eight', 'lifetimes'):
                label = recovery_label_source(label)
            if objects.get('mutation-label-source') != hashlib.sha256(label.encode()).hexdigest():
                raise ValueError('namespace mutation label source mismatch')
        elif role == 'reader' and (writer_60s or recovery_diagnostic):
            from openzfs_fs_bridge import recovery_source
            seed = (ROOT / 'user/storage/openzfs-volume/zpl-recovery.c').read_text()
            if filesystem_service_lifetimes and service_case != 1:
                from openzfs_fs_service import lifetime_recovery
                source = lifetime_recovery(seed)
            elif truncate_zero:
                from openzfs_zero import recovery as zero_recovery
                source = zero_recovery(seed)
            else:
                source = recovery_source(seed, writer_60s, recovery_diagnostic)
            objects = build.get('port', {}).get('volume', {}).get('namespace_objects', {})
            if objects.get('recovery-selected-source') != hashlib.sha256(source.encode()).hexdigest():
                raise ValueError('ZPL pair recovery selected source mismatch')
        if filesystem_service_activation:
            kernel_commands=[c['argv'] for c in build.get('commands',[]) if c.get('argv',[None])[0]=='zig' and 'build' in c['argv']]
            expected_activation=role=='writer'
            if len(kernel_commands)!=1 or ('-Dnative-service-activation=true' in kernel_commands[0]) is not expected_activation:
                raise ValueError('activation actual kernel option mismatch')
            driver_commands=[c['argv'] for c in build.get('commands',[]) if any('link-arg=--oformat=binary' in str(a) for a in c.get('argv',[]))]
            expected_linker='link-arg=-Tuser/storage/service-runtime/activation-linker.ld' if expected_activation else 'link-arg=-Tuser/protection/linker.ld'
            if len(driver_commands)!=1 or expected_linker not in driver_commands[0]:
                raise ValueError('activation actual linker mismatch')
            length=build['cases'][0].get('supervisor_bytes',0)
            if not 0<length<=(8192 if expected_activation else 4096):
                raise ValueError('activation actual controller size')
        row = build['cases'][0]
        if (row.get('status') != 'build-only' or row.get('name') != 'pool-import' or
                row.get('kernel_profile') != ('AENBD005/owner27/engine26' if storage_lifetime and role=='writer' else 'AENBD004/ABI26' if filesystem_service_wait and role=='writer' else 'AENBD003/ABI25' if service is not None and role == 'writer' else 'AENBD002/ABI14') or
                row.get('engine_entry_executed') is not False or
                row.get('staged_artifacts') != {'aether.iso': row.get('iso_sha256'),
                                                'engine.elf': row.get('elf_sha256')}):
            raise ValueError('ZPL pair missing prepared artifact identity')
        for name, digest in row['staged_artifacts'].items():
            path = output / role / name
            if (path.parent.is_symlink() or path.is_symlink() or not path.is_file() or
                    runtime.sha(path) != digest):
                raise ValueError('ZPL pair staged artifact drift: ' + role + '/' + name)
        if not build.get('sources') or not build.get('tools'):
            raise ValueError('ZPL pair missing frozen inputs')
        for name, digest in build['sources'].items():
            if runtime.sha(ROOT / name) != digest:
                raise ValueError('ZPL pair source drift: ' + name)
        for name, tool in build['tools'].items():
            if runtime.sha(tool['path']) != tool['sha256']:
                raise ValueError('ZPL pair tool drift: ' + name)
        dependency = ROOT / '.deps/native-service-runtime-v3'
        if not build.get('dependency_files'):
            raise ValueError('ZPL pair missing runtime inputs')
        for name, digest in build['dependency_files'].items():
            path = dependency / name
            if any(p.is_symlink() for p in (path, *path.parents)) or runtime.sha(path) != digest:
                raise ValueError('ZPL pair runtime drift: ' + name)
    runtime.sealed(runtime.BASE, 'f6bc6d6da3b051e1e4617e60ae256cbd35d193b608631ac29f7c42dbe73b13dc', 240)
    runtime.sealed(ROOT / '.deps/native-utc-v3', runtime.FIXED_UTC_SEAL, 343)


def diagnose(output, role, build, record):
    if build.get('fs_bridge') is not None:
        record['fs_bridge_failure_progress'] = 'unknown from outer stage/errno trace; never infer no effects or retry'
    serial = output / role / 'native-serial.log'
    if not serial.is_file():
        return
    if role == 'writer' and build.get('pool_zpl_stages'):
        try:
            record['zpl_stage_progress'] = decode_zpl_stages(serial.read_text(), build.get('pool_zpl_write_stages', False), build.get('pool_zpl_txg_stages', False), build.get('pool_zpl_sync_stages', False))
            return
        except ValueError as error:
            record['stage_decode_error'] = str(error)
    if role == 'writer' or (role == 'reader' and build.get('pool_recovery_diagnostic')):
        try:
            record['zpl_probe_error'] = decode_zpl_error(serial.read_text(), recovery=role == 'reader',
                write_lifetimes=role == 'writer' and build.get('namespace_mutation') == 'lifetimes')
            if build.get('fs_service_mixed'):
                record['zpl_probe_error']['operation']=('mixed-recovery-check' if role=='reader' else
                    {1:'open',4:'mixed-pristine-namespace',5:'UTC',6:'mixed-service',7:'mixed-progress',8:'mixed-reopen',9:'mixed-final-namespace-file'}.get(record['zpl_probe_error']['stage'],'unknown-mixed-stage'))
                record['zpl_probe_error']['mutation_progress']='unknown from outer error; never replay'
            if build.get('namespace_mutation') is not None:
                stage = record['zpl_probe_error']['stage']
                record['zpl_probe_error']['operation'] = (
                    'namespace-recovery-check' if role == 'reader' else
                    build['namespace_mutation'] if stage == 6 else
                    {1: 'open', 4: 'namespace-precheck', 5: 'UTC', 7: 'progress',
                     8: 'reopen', 9: 'namespace-postcheck',
                     **({10: 'record-retirement'} if build['namespace_mutation'] == 'lifetimes' else {})}.get(stage, 'invalid-namespace-stage'))
                record['zpl_probe_error']['mutation_progress'] = 'unknown; never replay'
            if role == 'writer' and build.get('pool_zpl_zero'):
                names = {1: 'open', 2: 'pristine-identity', 4: 'pristine-hash/EOF',
                         5: 'UTC', 6: 'shrink', 7: 'progress', 8: 'reopen-identity',
                         9: 'empty-metadata/EOF'}
                stage = record['zpl_probe_error']['stage']
                if stage not in names:
                    raise ValueError('truncate zero impossible error stage')
                record['zpl_probe_error']['operation'] = names[stage]
                record['zpl_probe_error']['mutation_progress'] = 'unknown; never replay'
            return
        except ValueError:
            pass  # An original assertion or pre-probe failure has another shape.
    from openzfs_failure import decode_site, symbolize_assertion
    try:
        result = decode_site(serial.read_text(), build.get('failure_catalogue', []))
        record['failure_site'] = result
        if result.get('site') == 65:
            def command(argv, log):
                args = list(map(str, argv))
                with log.open('wb') as stream:
                    subprocess.run(args, stdout=stream, stderr=subprocess.STDOUT,
                                   check=True, timeout=30)
                record.setdefault('diagnostic_commands', []).append(args)
            record['assertion_caller'] = symbolize_assertion(
                result, output / role / 'engine.elf', build['tools'], command)
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError) as error:
        record['diagnostic_error'] = str(error)


def execute_pair(output, builds, record):
    """A failure ends this function; there is deliberately no retry/resume path."""
    if record.get('writer_ticks_6000', False) and not record.get('writer_60s_diagnostic', False):
        raise ValueError('writer tick budget requires writer60')
    if record.get('writer_60s_diagnostic', False) and not (
            (record.get('sync_stages') is True and record.get('txg_worker_diagnostic') is True) or
            record.get('filesystem_bridge') is not None or record.get('filesystem_service') is not None or record.get('truncate_zero', False) or record.get('namespace_mutation') is not None):
        raise ValueError('writer60 requires sync-stage diagnostic')
    verify_prepared(output, builds, record.get('repeated_writes', False), record.get('stage_diagnostic', False), record.get('first_write_diagnostic', False), record.get('txg_worker_diagnostic', False), record.get('sync_stages', False), record.get('writer_ticks_6000', False), record.get('filesystem_bridge'), record.get('recovery_diagnostic', False), record.get('writer_60s_diagnostic', False), record.get('truncate_zero', False), record.get('namespace_mutation'), record.get('filesystem_service'), record.get('filesystem_service_case', 'normal'), record.get('filesystem_service_lifetimes', False), record.get('filesystem_service_namespace', False), record.get('filesystem_service_mixed',False),record.get('filesystem_service_wait',False),record.get('filesystem_service_bulk',False),record.get('filesystem_service_runtime',False),record.get('filesystem_service_activation',False),record.get('filesystem_service_names',False),record.get('filesystem_service_directories',False),record.get('storage_lifetime',False))
    seed = None
    operation = record.get('namespace_mutation')
    previous = record.get('namespace_seed')
    if previous is not None:
        from openzfs_mutation import admit_seed
        seed = admit_seed(output, operation, previous, builds['writer']['sources'])
        record['seed_admission'] = seed
    elif operation not in (None, 'create', 'shrink'):
        raise ValueError('namespace mutation requires its qualified predecessor')
    else:
        record['namespace_fixture'] = prepare_native_fixture(output)
        record['pristine_media'] = native_media_snapshot(output / 'native-namespace.raw')
    disk = output / 'native-namespace.raw'
    writer = None
    roles = ('baseline', 'writer', 'reader') if record.get('txg_worker_diagnostic', False) or record.get('filesystem_bridge') is not None or record.get('filesystem_service') is not None or record.get('truncate_zero', False) or record.get('namespace_mutation') is not None else ('writer', 'reader')
    if seed is not None:
        roles = ('writer', 'reader')
    for role in roles:
        verify_prepared(output, builds, record.get('repeated_writes', False), record.get('stage_diagnostic', False), record.get('first_write_diagnostic', False), record.get('txg_worker_diagnostic', False), record.get('sync_stages', False), record.get('writer_ticks_6000', False), record.get('filesystem_bridge'), record.get('recovery_diagnostic', False), record.get('writer_60s_diagnostic', False), record.get('truncate_zero', False), record.get('namespace_mutation'), record.get('filesystem_service'), record.get('filesystem_service_case', 'normal'), record.get('filesystem_service_lifetimes', False), record.get('filesystem_service_namespace', False), record.get('filesystem_service_mixed',False),record.get('filesystem_service_wait',False),record.get('filesystem_service_bulk',False),record.get('filesystem_service_runtime',False),record.get('filesystem_service_activation',False),record.get('filesystem_service_names',False),record.get('filesystem_service_directories',False),record.get('storage_lifetime',False))
        row = {'name': 'pool-import', 'role': role, 'status': 'running',
               'start_utc': datetime.now(timezone.utc).isoformat(),
               'watchdog_seconds': 120 if role == 'writer' and record.get('storage_lifetime',False) else 60 if role == 'writer' and record.get('writer_60s_diagnostic', False) else 30,
               'kernel_tick_limit': None if role == 'writer' and record.get('storage_lifetime',False) else 6000 if role == 'writer' and record.get('writer_ticks_6000', False) else 3000}
        record['cases'].append(row)
        if role == 'reader':
            row['admitted_media'] = runtime.check_zpl_recovery_media(writer, disk)
        elif seed is not None:
            if runtime.check_zpl_recovery_media(seed['qualified_writer'], disk) != seed['media']:
                raise ValueError('namespace seed writer media drift')
        else:
            if native_media_snapshot(disk) != record['pristine_media']:
                raise ValueError('ZPL pair pristine media drift')
        record['native_attempted'] = True
        run(output / role / 'aether.iso', marker=MARKER.encode(), entropy=True,
            rtc_base='2026-10-06T12:34:00', block_disk=disk,
            block_large=True, block_namespace=True, _pair_stop=True,
            **({'_storage_lifetime':True} if role=='writer' and record.get('storage_lifetime',False) else {}),
            **({'_zpl_writer_60s': True} if role == 'writer' and record.get('writer_60s_diagnostic', False) else {}),
            **({'zpl_writer': writer} if role == 'reader' else
               {'zpl_writer': seed['qualified_writer'], '_zpl_mutation_seed': True} if seed is not None else {}))
        row['vm_run_returned'] = True  # run joins QEMU before returning.
        serial = (output / role / 'native-serial.log').read_text()
        row['serial_sha256'] = runtime.sha(output / role / 'native-serial.log')
        row.update(runtime.check_engine_trace(serial, MARKER))
        if role=='writer' and record.get('storage_lifetime',False):
            from storage_lifetime import trace as lifetime_trace
            row.update(lifetime_trace(serial))
        if role=='writer' and record.get('filesystem_service_wait',False):
            from storage_channel_wait import trace as wait_trace
            row.update(wait_trace(serial))
        row.pop('four_checked_observations_per_generation', None)
        row.update(runtime.check_pool_cleanup_trace(serial))
        row.update(runtime.check_namespace_trace(serial) if role == 'baseline' else
                   runtime.check_zpl_write_trace(serial, record.get('stage_diagnostic', False), record.get('first_write_diagnostic', False), record.get('txg_worker_diagnostic', False), record.get('sync_stages', False)) if role == 'writer' else
                   runtime.check_zpl_recovery_trace(serial))
        from openzfs_mutation import FILE_BYTES
        if role != 'baseline' and operation in FILE_BYTES:
            row['namespace_bytes_verified'] = FILE_BYTES[operation]
        row['namespace_media'] = (native_media_snapshot(disk) if role == 'baseline' else
                                  written_native_media_snapshot(disk) if role == 'writer' else
                                  runtime.check_zpl_recovery_media(writer, disk))
        if role == 'baseline' and row['namespace_media'] != record['pristine_media']:
            raise ValueError('ZPL baseline media changed')
        row['disk_sha256'] = row['namespace_media']['sha256']
        row.update(status='pass', end_utc=datetime.now(timezone.utc).isoformat())
        if role == 'baseline':
            record['separate_baseline_qualified'] = True
        elif role == 'writer':
            writer = row
        else:
            qualification = runtime.check_zpl_recovery_pair(writer, row, FILE_BYTES.get(operation, 780248))
    verify_prepared(output, builds, record.get('repeated_writes', False), record.get('stage_diagnostic', False), record.get('first_write_diagnostic', False), record.get('txg_worker_diagnostic', False), record.get('sync_stages', False), record.get('writer_ticks_6000', False), record.get('filesystem_bridge'), record.get('recovery_diagnostic', False), record.get('writer_60s_diagnostic', False), record.get('truncate_zero', False), record.get('namespace_mutation'), record.get('filesystem_service'), record.get('filesystem_service_case', 'normal'), record.get('filesystem_service_lifetimes', False), record.get('filesystem_service_namespace', False), record.get('filesystem_service_mixed',False),record.get('filesystem_service_wait',False),record.get('filesystem_service_bulk',False),record.get('filesystem_service_runtime',False),record.get('filesystem_service_activation',False),record.get('filesystem_service_names',False),record.get('filesystem_service_directories',False),record.get('storage_lifetime',False))
    record.update(qualification)


def pair(delivery, utc_delivery, repeated_writes=False, stage_diagnostic=False, first_write_diagnostic=False, txg_worker_diagnostic=False, sync_stages=False, writer_60s=False, writer_ticks_6000=False, filesystem_bridge=None, recovery_diagnostic=False, truncate_zero=False, filesystem_service=None, filesystem_service_case='normal', filesystem_service_lifetimes=False, filesystem_service_mixed=False, filesystem_service_wait=False, filesystem_service_bulk=False, filesystem_service_runtime=False, filesystem_service_activation=False, filesystem_service_names=False, filesystem_service_directories=False, storage_lifetime=False):
    from storage_lifetime import validate as validate_storage_lifetime
    validate_storage_lifetime(storage_lifetime, filesystem_service_directories, False, filesystem_service_case)
    if not isinstance(filesystem_service_directories,bool) or (filesystem_service_directories and not filesystem_service_names):
        raise ValueError('directories require explicit names selection')
    if not isinstance(filesystem_service_names,bool) or (filesystem_service_names and not filesystem_service_activation):
        raise ValueError('names require explicit activation selection')
    if not isinstance(filesystem_service_activation,bool) or (filesystem_service_activation and not (filesystem_service_runtime and filesystem_service is not None)):
        raise ValueError('activation requires explicit runtime service pair')
    if not isinstance(filesystem_service_runtime,bool) or (filesystem_service_runtime and not filesystem_service_bulk):
        raise ValueError('runtime requires explicit bulk pair')
    if not isinstance(filesystem_service_bulk,bool) or (filesystem_service_bulk and not (filesystem_service_wait and filesystem_service_mixed)):
        raise ValueError('bulk requires explicit mixed waiting pair')
    if not isinstance(filesystem_service_wait,bool) or (filesystem_service_wait and not filesystem_service_mixed):
        raise ValueError('service wait requires explicit mixed selection')
    from openzfs_fs_service import case_number
    service_case = case_number(filesystem_service_case)
    if not isinstance(filesystem_service_mixed, bool) or (filesystem_service_mixed and (filesystem_service is None or filesystem_service_lifetimes)):
        raise ValueError('mixed service requires exclusive exact service selection')
    if not isinstance(filesystem_service_lifetimes, bool) or (filesystem_service_lifetimes and filesystem_service is None):
        raise ValueError('filesystem service lifetimes require exact service selection')
    if service_case and filesystem_service is None:
        raise ValueError('filesystem service case requires its exact selection')
    if filesystem_service is not None:
        if filesystem_bridge is not None or truncate_zero or any((repeated_writes, stage_diagnostic,
                first_write_diagnostic, txg_worker_diagnostic, sync_stages)):
            raise ValueError('filesystem service requires exclusive single-write pair')
        from openzfs_fs_service import intake as service_intake
        service_intake(filesystem_service, filesystem_service_lifetimes, mixed=filesystem_service_mixed,waiting=filesystem_service_wait,bulk=filesystem_service_bulk,runtime=filesystem_service_runtime,activation=filesystem_service_activation,names=filesystem_service_names,directories=filesystem_service_directories)
        writer_60s = writer_ticks_6000 = recovery_diagnostic = True
    if not isinstance(truncate_zero, bool):
        raise ValueError('truncate zero selector must be boolean')
    if truncate_zero and (filesystem_bridge is not None or any((repeated_writes,
            stage_diagnostic, first_write_diagnostic, txg_worker_diagnostic, sync_stages))):
        raise ValueError('truncate zero requires exclusive single-transaction pair')
    if recovery_diagnostic and filesystem_bridge is None and filesystem_service is None and not truncate_zero:
        raise ValueError('recovery diagnostic requires filesystem bridge pair')
    if not isinstance(writer_ticks_6000, bool) or not isinstance(writer_60s, bool):
        raise ValueError('writer budget selectors must be boolean')
    if truncate_zero:
        writer_60s = writer_ticks_6000 = recovery_diagnostic = True
    if filesystem_bridge is not None:
        if any((repeated_writes, stage_diagnostic, first_write_diagnostic, txg_worker_diagnostic, sync_stages)):
            raise ValueError('filesystem bridge requires exclusive single-write pair')
        from openzfs_fs_bridge import intake as bridge_intake
        bridge_intake(filesystem_bridge)
        writer_60s = writer_ticks_6000 = True
    if not isinstance(writer_ticks_6000, bool):
        raise ValueError('writer tick budget selector must be boolean')
    if writer_ticks_6000 and not writer_60s:
        raise ValueError("writer tick budget requires writer60")
    if writer_60s and not (sync_stages or filesystem_bridge is not None or filesystem_service is not None or truncate_zero):
        raise ValueError("writer60 requires sync-stage diagnostic")
    if sync_stages and not txg_worker_diagnostic:
        raise ValueError("sync stages require worker profile")
    if sum((stage_diagnostic, first_write_diagnostic, txg_worker_diagnostic)) > 1:
        raise ValueError('stage diagnostic selectors are exclusive')
    stage_diagnostic = stage_diagnostic or first_write_diagnostic or txg_worker_diagnostic
    if stage_diagnostic and not repeated_writes:
        raise ValueError('stage diagnostic requires repeated writes')
    (ROOT / 'zig-out').mkdir(exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix=PREFIX, dir=ROOT / 'zig-out'))
    record = {'format': 'aether-zpl-pair-v1', 'status': 'incomplete', 'builds': {},
              'cases': [], 'native_attempted': False, 'fresh_vm_readback_qualified': False,
              'repeated_writes': repeated_writes,
              'stage_diagnostic': stage_diagnostic, 'first_write_diagnostic': first_write_diagnostic,
              'txg_worker_diagnostic': txg_worker_diagnostic,
              'baseline_separated': txg_worker_diagnostic or filesystem_bridge is not None or filesystem_service is not None or truncate_zero,
              'truncate_zero': truncate_zero,
              'sync_stages': sync_stages,
              'writer_60s_diagnostic': writer_60s,
              'writer_ticks_6000': writer_ticks_6000,
              'recovery_diagnostic': recovery_diagnostic,
              'storage_lifetime': storage_lifetime,
              'recovery_writer_window_seconds': 120 if storage_lifetime else 60 if writer_60s else 30,
              'filesystem_bridge': str(Path(filesystem_bridge).resolve()) if filesystem_bridge is not None else None,
              'writer_kernel_tick_limit': None if storage_lifetime else 6000 if writer_ticks_6000 else 3000,
              'readonly_kernel_tick_limit': 3000,
              **({'normal_30_second_writer_qualified': False} if writer_60s else {}),
              'writer_watchdog_seconds': 120 if storage_lifetime else 60 if writer_60s else 30,
              'readonly_watchdog_seconds': 30,
              'scope': 'one private existing-file write, clean export, fresh readonly VM; no crash/power-loss claim'}
    if filesystem_service is not None:
        record['filesystem_service'] = str(Path(filesystem_service).resolve())
        record['filesystem_service_case'] = filesystem_service_case
        if filesystem_service_wait:record['filesystem_service_wait']=True
        if filesystem_service_bulk:record['filesystem_service_bulk']=True
        if filesystem_service_runtime:record['filesystem_service_runtime']=True
        if filesystem_service_activation:record['filesystem_service_activation']=True
        if filesystem_service_names:record['filesystem_service_names']=True
        if filesystem_service_directories:record['filesystem_service_directories']=True
        if filesystem_service_mixed:
            record['filesystem_service_mixed'] = True
        if filesystem_service_lifetimes:
            record['filesystem_service_lifetimes'] = True
        record['scope'] = ('fixed eight16-byte Rust service writes with success-only consumed-context retirement; interruption cases stop early, original full-file/media/fresh recovery; no general uptime' if filesystem_service_lifetimes else 'matched one-write Rust AFSRPC01 service over authenticated channels, original full-file oracle and fresh recovery; failure matrix separate')
    if filesystem_service_mixed:
        record['scope'] = 'fixed eight mixed AFSRPC03 create/write/rename/remove transactions; original full-file/media/fresh recovery; no operational uptime claim'
    if repeated_writes:
        record['scope'] = 'two private successive writes with retained TXG ordering, clean export, fresh readonly VM; no unbounded/crash/power-loss claim'
    if txg_worker_diagnostic:
        record['scope'] = 'separate pristine readonly VM, two transaction writes with fixed independent file oracle, clean export and fresh readonly VM; no crash/power-loss claim'
    if truncate_zero:
        record['scope'] = 'one original-engine truncate-to-zero transaction, clean export, fresh readonly size/flags/time/empty hash/two EOF checks; no create/grow/Rust-service or crash claim'
    stopped = True
    print('[RUNNING] ZPL pair results:', output, file=sys.stderr, flush=True)
    try:
        for role in (('baseline', 'writer', 'reader') if txg_worker_diagnostic or filesystem_bridge is not None or filesystem_service is not None or truncate_zero else ('writer', 'reader')):
            runtime.suite(delivery, case='pool-import', fixed_reaper=True, engine_utc=True,
                          utc_delivery=utc_delivery, pool_create=True, pool_namespace=True,
                          pool_diagnose='build', pool_zpl_write=role == 'writer',
                          pool_zpl_recover=role == 'reader', _zpl_stage=output / role,
                          _zpl_repeat=repeated_writes and role == 'writer',
                          _zpl_stages=stage_diagnostic and role == 'writer',
                          _zpl_write_stages=first_write_diagnostic and role == 'writer',
                          _zpl_txg_stages=txg_worker_diagnostic and role == 'writer',
                          _zpl_sync_stages=sync_stages and role == 'writer',
                          _zpl_writer_budget=writer_ticks_6000 and role == 'writer',
                          _zpl_fs_bridge=filesystem_bridge if role == 'writer' else None,
                          _zpl_recovery_diagnostic=recovery_diagnostic and role == 'reader',
                          _zpl_recovery_writer_60s=writer_60s and role == 'reader',
                          _zpl_zero=truncate_zero and role != 'baseline',
                          namespace_ipc=filesystem_service is not None and role == 'writer',
                          _zpl_fs_service=filesystem_service if role == 'writer' else None,
                          _zpl_fs_service_case=filesystem_service_case if role == 'writer' else 'normal',
                          _zpl_fs_lifetimes=filesystem_service_lifetimes and (role == 'writer' or (role == 'reader' and service_case != 1)),
                          _zpl_fs_mixed=filesystem_service_mixed and role != 'baseline',
                          _zpl_fs_mixed_empty=filesystem_service_mixed and role == 'reader' and (service_case == 1 or (filesystem_service_bulk and service_case == 2)),
                          namespace_wait=filesystem_service_wait and role=='writer',_zpl_fs_bulk=filesystem_service_bulk and role!='baseline',_zpl_fs_runtime=filesystem_service_runtime and role!='baseline',_zpl_fs_activation=filesystem_service_activation and role=='writer',_zpl_fs_names=filesystem_service_names and role!='baseline',_zpl_fs_directories=filesystem_service_directories and role!='baseline',_zpl_storage_lifetime=storage_lifetime and role!='baseline')
            record['builds'][role] = json.loads((output / (role + '-build.json')).read_text())['report']
        execute_pair(output, record['builds'], record)
        record['status'] = 'pass'
    except BaseException as error:
        stopped = not isinstance(error, NativeStopError)
        record.update(status='failed', error=str(error), vm_stop_confirmed=stopped,
                      human_disposition_required=record['native_attempted'],
                      fresh_vm_readback_qualified=False)
        if record['cases']:
            row = record['cases'][-1]
            row.update(status='failed', error=str(error))
            diagnose(output, row['role'], record['builds'][row['role']], record)
        raise
    finally:
        # A failed build still publishes its compact receipt before propagating.
        for role in ('baseline', 'writer', 'reader'):
            location = output / (role + '-build.json')
            if location.is_file():
                build = json.loads(location.read_text())
                record['builds'][role] = build['report']
                root = Path(build['output'])
                if (root.parent != ROOT / 'zig-out' or root.is_symlink() or root.resolve() != root or
                        not root.name.startswith('thread-suite-service-runtime-') or
                        root.name.startswith(PREFIX)):
                    raise ValueError('ZPL pair refuses unowned build cleanup')
                # Preserve failed build logs in the compact pair before removal.
                for log in root.rglob('*.log'):
                    if log.stat().st_size:
                        target = output / (role + '-build-logs') / log.relative_to(root)
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copyfile(log, target)
                shutil.rmtree(root)
                location.unlink()
        if stopped:
            disk = output / 'native-namespace.raw'
            if disk.is_file():
                try:
                    from openzfs_namespace import _native_media_snapshot
                    record['final_media'] = _native_media_snapshot(disk)
                except (ValueError, OSError) as error:
                    record['final_media'] = {'status': 'unavailable', 'error': str(error)}
        record['vm_stop_confirmed'] = stopped
        (output / 'results.json').write_text(json.dumps(record, indent=2) + '\n')
        if stopped:
            compact_run(output, record)
        else:
            record['cleanup_blocked'] = 'VM stop unconfirmed; retain owned media until human disposition'
            (output / 'results.json').write_text(json.dumps(record, indent=2) + '\n')
    print('[PASS] ' + ('Separate120-second storage lifetime, fixed65-second idle and fresh recovery; compact results:' if storage_lifetime else 'Diagnostic 60-second writer and fresh readonly readback; no 30-second qualification; compact results:' if writer_60s else 'ZPL write and fresh-VM readonly readback; compact results:'), output)
    return output


if __name__ == '__main__':
    parser = runtime.IntakeParser(description=__doc__, color=False)
    parser.add_argument('--truncate-zero', action='store_true',
                        help='qualify one bounded original-engine truncate-to-zero transaction')
    parser.add_argument('--delivery', type=Path, required=True)
    parser.add_argument('--utc-delivery', type=Path, required=True)
    parser.add_argument('--repeated-writes', action='store_true',
                        help='qualify two successive transactions on one private engine')
    parser.add_argument('--stage-diagnostic', action='store_true',
                        help='reuse fingerprint slots for bounded repeated-write stage markers')
    parser.add_argument('--first-write-diagnostic', action='store_true',
                        help='reuse fingerprint slots for first-write assignment/commit/wait markers')
    parser.add_argument('--txg-worker-diagnostic', action='store_true',
                        help='verify pristine file in a separate readonly VM, then observe original TXG workers')
    parser.add_argument('--sync-stages', action='store_true',
                        help='refine TXG worker slots for original sync entry, I/O, configuration and dataset progress')
    parser.add_argument('--writer-60s', action='store_true',
                        help='fixed 60-second storage-writer ceiling; readonly guests remain 30 seconds')
    parser.add_argument('--writer-ticks-6000', action='store_true',
                        help='fixed6000-tick storage-writer ceiling; requires --writer-60s')
    parser.add_argument('--filesystem-service-case', choices=('normal', 'lost-reply', 'partial-request', 'close-failure'), default='normal',
                        help='fixed native service failure witness; requires --filesystem-service')
    parser.add_argument('--filesystem-service-names', action='store_true', help='separate AF05 components255/rename510; all other limits fixed')
    parser.add_argument('--storage-lifetime', action='store_true', help='separate AENBD005 owner27: one120s writer with6500-tick idle; readers30s')
    parser.add_argument('--filesystem-service-directories', action='store_true', help='separate AF06 delegated mkdir and empty-rmdir; current bounds remain fixed')
    parser.add_argument('--filesystem-service-activation', action='store_true', help='separate imported-root readiness profile; at most8KiB supervisor code')
    parser.add_argument('--filesystem-service-runtime', action='store_true', help='separate checked lifetime candidate; fixed9 mutations/96 native requests')
    parser.add_argument('--filesystem-service-bulk', action='store_true', help='separate fixed-eight AFSRPC04 4 KiB data profile; requires mixed/wait')
    parser.add_argument('--filesystem-service-wait', action='store_true', help='exact separate ABI26 mixed wait candidate')
    parser.add_argument('--filesystem-service-mixed', action='store_true',
                        help='sealed fixed-eight mixed AFSRPC03 profile; requires --filesystem-service')
    parser.add_argument('--filesystem-service-lifetimes', action='store_true',
                        help='separate sealed fixed-eight service16 profile; requires --filesystem-service')
    parser.add_argument('--filesystem-service', type=Path,
                        help='exact private AFSRPC01 service, fixed one-write IPC/recovery at60s/6000')
    parser.add_argument('--filesystem-bridge', type=Path,
                        help='pinned private Rust callback; exclusive single-write pair at fixed60s/6000 ticks')
    parser.add_argument('--recovery-diagnostic', action='store_true',
                        help='attribute failed reader checks without changing acceptance; requires --filesystem-bridge')
    args = parser.parse_args()
    if args.recovery_diagnostic and args.filesystem_bridge is None and args.filesystem_service is None and not args.truncate_zero:
        parser.error('recovery diagnostic requires filesystem bridge pair')
    if args.filesystem_service_mixed and (args.filesystem_service is None or args.filesystem_service_lifetimes):
        parser.error('mixed service requires exclusive exact service selection')
    if args.filesystem_service_directories and not args.filesystem_service_names:
        parser.error('directories require names selection')
    if args.filesystem_service_names and not args.filesystem_service_activation:
        parser.error('names require explicit activation selection')
    if args.filesystem_service_activation and not (args.filesystem_service_runtime and args.filesystem_service is not None):
        parser.error('activation requires explicit runtime service selection')
    if args.filesystem_service_runtime and not args.filesystem_service_bulk:
        parser.error('runtime requires explicit bulk selection')
    if args.filesystem_service_bulk and not (args.filesystem_service_wait and args.filesystem_service_mixed):
        parser.error('bulk requires explicit mixed wait selection')
    if args.filesystem_service_wait and not args.filesystem_service_mixed:
        parser.error('service wait requires explicit mixed selection')
    if args.filesystem_service_lifetimes and args.filesystem_service is None:
        parser.error('filesystem service lifetimes require its exact selection')
    if args.storage_lifetime and (not args.filesystem_service_directories or args.filesystem_service_case != 'normal'):
        parser.error('storage lifetime requires the separate normal directory profile')
    if args.filesystem_service_case != 'normal' and args.filesystem_service is None:
        parser.error('filesystem service case requires its exact selection')
    if args.filesystem_service is not None:
        if args.filesystem_bridge is not None or args.truncate_zero or any((args.repeated_writes, args.stage_diagnostic, args.first_write_diagnostic, args.txg_worker_diagnostic, args.sync_stages)):
            parser.error('filesystem service requires exclusive single-write pair')
        args.writer_60s = args.writer_ticks_6000 = args.recovery_diagnostic = True
    if args.truncate_zero:
        if args.filesystem_bridge is not None or any((args.repeated_writes, args.stage_diagnostic, args.first_write_diagnostic, args.txg_worker_diagnostic, args.sync_stages)):
            parser.error('truncate zero requires exclusive single-transaction pair')
        args.writer_60s = args.writer_ticks_6000 = args.recovery_diagnostic = True
    if args.filesystem_bridge is not None:
        if any((args.repeated_writes, args.stage_diagnostic, args.first_write_diagnostic, args.txg_worker_diagnostic, args.sync_stages)):
            parser.error('filesystem bridge requires exclusive single-write pair')
        args.writer_60s = args.writer_ticks_6000 = True
    if args.writer_ticks_6000 and not args.writer_60s:
        parser.error('writer tick budget requires writer60')
    if args.writer_60s and not (args.sync_stages or args.filesystem_bridge is not None or args.filesystem_service is not None or args.truncate_zero):
        parser.error('writer60 requires sync-stage diagnostic')
    if args.sync_stages and not args.txg_worker_diagnostic:
        parser.error('sync stages require worker profile')
    if sum((args.stage_diagnostic, args.first_write_diagnostic, args.txg_worker_diagnostic)) > 1:
        parser.error('stage diagnostic selectors are exclusive')
    if (args.stage_diagnostic or args.first_write_diagnostic or args.txg_worker_diagnostic) and not args.repeated_writes:
        parser.error('stage diagnostic requires repeated writes')
    try:
        pair(args.delivery, args.utc_delivery, args.repeated_writes, args.stage_diagnostic, args.first_write_diagnostic, args.txg_worker_diagnostic, args.sync_stages, args.writer_60s, args.writer_ticks_6000, args.filesystem_bridge, args.recovery_diagnostic, args.truncate_zero, args.filesystem_service, args.filesystem_service_case, args.filesystem_service_lifetimes, args.filesystem_service_mixed,args.filesystem_service_wait,args.filesystem_service_bulk,args.filesystem_service_runtime,args.filesystem_service_activation,args.filesystem_service_names,args.filesystem_service_directories,args.storage_lifetime)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        parser.exit(1, runtime.display(error) + '\n')
