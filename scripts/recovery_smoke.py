# SPDX-License-Identifier: BSD-2-Clause
"""Pinned dash early-reader recovery inputs and independent native oracle."""
import hashlib
import json
import re
from pathlib import Path
from fixture_inputs import read_inputs
from deps import ROOT
from session_smoke import observations

INPUTS = {'experiments/dash-native/recovery/early-reader.sh': '14a25030cfd2f94b8ef95be29241bd4be605a74f2cf07557875a4e60d1c519d4', 'experiments/dash-native/recovery/expected.stdout': 'df93c46970fa62c9ac09397fa4f4006a9fb1cae6468d90d6c46ee076d5dd063b', 'experiments/dash-native/recovery/expected.stderr': 'ba403ec5f8fc356cac72fdb41bb96792ec02b6606975856a40a3ad88044c6cbf', 'experiments/dash-reference/helper.c': '3fdea5d515011e49516f35cf8b9abdc214024a226bb3ba560480fa9775cebcf8', 'experiments/dash-native/SESSION-RECOVERY.md': '987a00f8fe669fc76aac095025eef512be05cf0caeb70673a9c69cf3dbf0be52', 'experiments/dash-native/recovery/manifest.json': 'fd5391bc3101f2aca6f45c56a143c61d5422ddbd0e7d8a09d75c5956321e03a4'}
CASES = [
    ('composed', '', '', None, 24),
    ('wrong-env', 'SESSION_WRONG_ENV', 'recovery_wrong_env', 2840, 4),
    ('bad-byte', 'SESSION_BAD_BYTE', '', None, 24),
    ('fd-leak', 'SESSION_FD_LEAK', 'recovery_fd_leak', 2841, 8),
    ('wrong-epipe', '', 'recovery_wrong_epipe', 2842, 3),
    ('stale-wait', 'SESSION_STALE_WAIT', '', None, 24),
    ('retained-reader', 'RECOVERY_RETAINED_READER', 'recovery_retained_reader', 2844, 3),
]


def consumer_inputs():
    return read_inputs('recovery-native-2026-09-25', INPUTS)


def check_recovery(serial, label, inputs):
    _, _, _, failure, reclaimed = next(c for c in CASES if c[0] == label)
    lines = serial.splitlines()
    completion = f'NATIVE supervisor result={failure or 100} reclaimed={reclaimed}'
    marker = 'AETHER PANIC: native C profile rejected' if failure else 'AETHER NATIVE CONNECTIONS PASS'
    if lines.count(completion) != 1 or serial.count('NATIVE supervisor result=') != 1 or lines.count(marker) != 1:
        raise RuntimeError('RECOVERY completion mismatch')
    if (failure is None and 'PANIC' in serial) or (failure and 'AETHER NATIVE CONNECTIONS PASS' in serial):
        raise RuntimeError('RECOVERY wrong completion kind')
    terminals = [tuple(map(int, m)) for m in re.findall(r'^NATIVE terminal slot=(\d+) generation=(\d+) kind=(\d+) detail=(\d+)$', serial, re.M)]
    if (len(terminals) != reclaimed or len({r[:2] for r in terminals}) != reclaimed
            or sum(line.startswith('NATIVE terminal ') for line in lines) != reclaimed):
        raise RuntimeError('RECOVERY terminal identity/count mismatch')
    rows = observations(serial)
    if not rows or not lines.index(completion) < lines.index(marker):
        raise RuntimeError('RECOVERY missing observation or early marker')
    observation_indices = [i for i, v in enumerate(lines) if v.startswith('NATIVE SESSION ')]
    terminal_indices = [i for i, v in enumerate(lines) if v.startswith('NATIVE terminal ')]
    if max(terminal_indices) >= max(observation_indices) or max(observation_indices) >= lines.index(completion):
        raise RuntimeError('RECOVERY early completion')
    if len(rows) != (1 if failure else 3):
        raise RuntimeError('RECOVERY observation count mismatch')
    if failure is None:
        expected = {(0, g): (1, 0) for g in range(1, 4)}
        expected.update({(2, g): (1, 42 if g in (1, 5, 9) else 0) for g in range(1, 13)})
        expected.update({(3, g): (1, 0) for g in range(1, 7)})
        expected.update({(4, g): (1, 0) for g in range(1, 4)})
        if {r[:2]: r[2:] for r in terminals} != expected:
            raise RuntimeError('RECOVERY terminal status mismatch')
        if serial.count('NATIVE MEMORY admitted slot=') != 21:
            raise RuntimeError('RECOVERY image admission mismatch')
        # A prior shell must be fully observed before the next shell terminates.
        for g in range(1, 4):
            phase = [r for r in terminals if (r[0] == 0 and r[1] == g) or
                     (r[0] == 2 and 4*(g-1) < r[1] <= 4*g) or
                     (r[0] == 3 and 2*(g-1) < r[1] <= 2*g) or
                     (r[0] == 4 and r[1] == g)]
            positions = {r[:2]: lines.index(f'NATIVE terminal slot={r[0]} generation={r[1]} kind={r[2]} detail={r[3]}') for r in phase}
            if len(positions) != 8 or max(positions.values()) >= observation_indices[g-1]:
                raise RuntimeError('RECOVERY phase identity mismatch')
            if g > 1 and min(positions.values()) <= observation_indices[g-2]:
                raise RuntimeError('RECOVERY overlapping shell generations')
            # Both recovered children terminate before argv, then the healthy
            # pipeline completes before the closure helper and parent.
            a, b = 4*(g-1), 2*(g-1)
            if not max(positions[(2,a+1)], positions[(3,b+1)]) < positions[(2,a+2)] < min(positions[(2,a+3)], positions[(3,b+2)], positions[(4,g)]):
                raise RuntimeError('RECOVERY phase order mismatch')
            if not max(positions[(2,a+3)], positions[(3,b+2)], positions[(4,g)]) < positions[(2,a+4)] < positions[(0,g)]:
                raise RuntimeError('RECOVERY cleanup order mismatch')
        if rows != [(g, 7, 6, inputs['expected.stdout'], inputs['expected.stderr']) for g in range(1,4)]:
            raise RuntimeError('RECOVERY stream mismatch')
    else:
        copies, execs, status, prefix = {
            'wrong-env': (3,3,(1,43),b'epipe ok\n'),
            'fd-leak': (7,6,(1,45),b'epipe ok\nargv ok\npipe data\n'),
            'wrong-epipe': (2,2,(1,42),b''),
            'retained-reader': (2,2,(3,143),b''),
        }[label]
        if rows != [(1,copies,execs,prefix,b'')]:
            raise RuntimeError('RECOVERY negative stream/count mismatch')
        actual = {r[:2]: r[2:] for r in terminals}
        expected = {(0,1): status, (2,1): (1,98 if label == 'wrong-epipe' else 42), (3,1): (1,0)}
        if label in ('wrong-env','fd-leak'):
            expected[(2,2)] = (1,91 if label == 'wrong-env' else 0)
        if label == 'fd-leak':
            expected.update({(2,3):(1,0),(3,2):(1,0),(4,1):(1,0),(2,4):(1,95)})
        if label == 'retained-reader':
            # Closing the stopped parent's last reader may let pump observe
            # EPIPE before its own stop. Either terminal is explicit, not timeout.
            if actual.get((2,1)) not in ((1,42),(3,143)):
                raise RuntimeError('RECOVERY retained reader cleanup mismatch')
            expected[(2,1)] = actual[(2,1)]
        if actual != expected or serial.count('NATIVE MEMORY admitted slot=') != execs + 1:
            raise RuntimeError('RECOVERY negative lifecycle mismatch')
        positions = {r[:2]: lines.index(f'NATIVE terminal slot={r[0]} generation={r[1]} kind={r[2]} detail={r[3]}') for r in terminals}
        if label in ('wrong-env', 'fd-leak'):
            if not max(positions[(2,1)], positions[(3,1)]) < positions[(2,2)] < positions[(0,1)]:
                raise RuntimeError('RECOVERY negative phase order mismatch')
        if label == 'fd-leak':
            pipeline = [positions[k] for k in ((2,3),(3,2),(4,1))]
            if not positions[(2,2)] < min(pipeline) <= max(pipeline) < positions[(2,4)] < positions[(0,1)]:
                raise RuntimeError('RECOVERY negative pipeline order mismatch')
        if label == 'wrong-epipe' and not max(positions[(2,1)], positions[(3,1)]) < positions[(0,1)]:
            raise RuntimeError('RECOVERY negative collection order mismatch')
        if label == 'retained-reader' and not positions[(3,1)] < positions[(0,1)]:
            raise RuntimeError('RECOVERY retained reader stopped before reader exit')
    return rows
