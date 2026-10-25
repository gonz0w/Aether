# SPDX-License-Identifier: BSD-2-Clause
"""Frozen scratch session workload and native observation checks."""
import hashlib
import json
import re
from pathlib import Path
from fixture_inputs import read_inputs
from deps import ROOT
from session_smoke import observations

INPUTS = {
    "experiments/dash-native/scratch-session/composed.sh": "9b008b0f4105759c06a50170882495621007cc7beb6f5f56e2d44a4f73432bdf",
    "experiments/dash-native/scratch-session/expected.stdout": "383c2804c291450090c36243d351240f37222e41fd2310307891888968c78aea",
    "experiments/dash-native/scratch-session/expected.stderr": "16f638c919892cf239496c10e1c05f460ee108d82e13c2686c1dff11a83f87ad",
    "experiments/dash-native/scratch-session/initial-data.bin": "cdf0910fedce48000712b120772f30954a5b93f3c6f33f465811c132929536dc",
    "experiments/dash-native/scratch-session/protected.bin": "4378f5f8c155589bc148ca4213669f0b620dd18942e10450eae5779ce6c59beb",
    "experiments/dash-reference/helper.c": "3fdea5d515011e49516f35cf8b9abdc214024a226bb3ba560480fa9775cebcf8",
    "experiments/dash-native/SESSION-SCRATCH.md": "c27c84501c69de27a0221045769b400d3aa34823ca7bdd7737c19064dd4e8e6b",
    "experiments/dash-native/scratch-session/manifest.json": "41fd9bd9a9543d19a6335e43a912f59bfc379c8dafa777bb9344ef05fdfacbc2"
}
CASES = [
    ('composed', '', '', None, 24),
    ('lose-b', '', 'scratch_lose_b', 2880, 8),
    ('bad-read', '', 'scratch_bad_read', None, 24),
    ('wrong-denied', '', 'scratch_wrong_denied', 2882, 8),
    ('skip-read', '', 'scratch_skip_read', 2883, 8),
    ('skip-request', 'SCRATCH_SKIP_REQUEST', '', 2884, 2),
    ('early-close', 'SCRATCH_EARLY_CLOSE', 'scratch_early_close', 2885, 1),
    ('wrong-env', 'SESSION_WRONG_ENV', 'scratch_wrong_env', 2886, 4),
    ('fd-leak', 'SESSION_FD_LEAK', 'scratch_fd_leak', 2887, 8),
    ('stderr-error', '', 'scratch_stderr_error', 2888, 8),
    ('stale-reference', 'SCRATCH_STALE_REFERENCE', '', None, 24),
    ('bad-byte', 'SESSION_BAD_BYTE', '', None, 24),
]


def consumer_inputs():
    return read_inputs('scratch-session-2026-09-29', INPUTS)


def check_admissions(serial, expected):
    lines = serial.splitlines()
    records = [tuple(map(int, match)) for match in re.findall(
        r'^NATIVE MEMORY admitted slot=(\d+) generation=(\d+) used=(\d+) remaining=(\d+)$', serial, re.M)]
    if (len(records) != len(expected) or {r[:2] for r in records} != expected
            or sum(line.startswith('NATIVE MEMORY admitted ') for line in lines) != len(expected)
            or any(r[2] == 0 for r in records)):
        raise RuntimeError('SCRATCH-SESSION admission identity mismatch')
    for slot, generation, used, remaining in records:
        admission = lines.index(f'NATIVE MEMORY admitted slot={slot} generation={generation} used={used} remaining={remaining}')
        terminal = next(i for i,line in enumerate(lines) if line.startswith(
            f'NATIVE terminal slot={slot} generation={generation} kind='))
        if admission >= terminal:
            raise RuntimeError('SCRATCH-SESSION admission after terminal')


def check_scratch(serial, label, inputs):
    if next(c for c in CASES if c[0] == label)[3] is not None:
        return check_negative(serial, label, inputs)

    lines = serial.splitlines()
    completion = 'NATIVE supervisor result=100 reclaimed=24'
    marker = 'AETHER NATIVE CONNECTIONS PASS'
    if (lines.count(completion) != 1 or serial.count('NATIVE supervisor result=') != 1
            or lines.count(marker) != 1 or 'PANIC' in serial
            or lines.index(completion) >= lines.index(marker)):
        raise RuntimeError('SCRATCH-SESSION completion mismatch')
    terminals = [tuple(map(int, row)) for row in re.findall(
        r'^NATIVE terminal slot=(\d+) generation=(\d+) kind=(\d+) detail=(\d+)$', serial, re.M)]
    expected = {(0,g):(1,0) for g in range(1,4)}
    expected.update({(2,g):(1,2 if (g-1)%5 == 0 else 0) for g in range(1,16)})
    expected.update({(s,g):(1,0) for s in (3,4) for g in range(1,4)})
    if (len(terminals) != 24 or sum(line.startswith('NATIVE terminal ') for line in lines) != 24
            or {r[:2]:r[2:] for r in terminals} != expected):
        raise RuntimeError('SCRATCH-SESSION terminal mismatch')
    check_admissions(serial, {(s,g) for s in (0,3,4) for g in range(1,4)} |
                     {(2,g) for g in (2,3,5,7,8,10,12,13,15)})
    rows = observations(serial)
    if rows != [(g,7,5,inputs['expected.stdout'],inputs['expected.stderr']) for g in range(1,4)]:
        raise RuntimeError('SCRATCH-SESSION stream mismatch')
    observed = [i for i,line in enumerate(lines) if line.startswith('NATIVE SESSION ')]
    previous = -1
    for g in range(1,4):
        def pos(slot, generation):
            status = expected[(slot,generation)]
            return lines.index(f'NATIVE terminal slot={slot} generation={generation} kind={status[0]} detail={status[1]}')
        a=5*(g-1)
        first,second,argv=pos(2,a+1),pos(2,a+2),pos(2,a+3)
        stages=[pos(2,a+4),pos(3,g),pos(4,g)]
        closed,parent=pos(2,a+5),pos(0,g)
        if not previous < first < second < argv < min(stages) <= max(stages) < closed < parent < observed[g-1] < lines.index(completion):
            raise RuntimeError('SCRATCH-SESSION phase order mismatch')
        previous=observed[g-1]



def check_negative(serial, label, inputs):
    _, _, _, failure, count = next(c for c in CASES if c[0] == label)
    spec = {
        'lose-b': (7,5,0,[(1,2),(1,0),(1,0),(1,0),(1,0)], inputs['expected.stdout'].replace(b'AB',b'A\0'), inputs['expected.stderr']),
        'wrong-denied': (7,5,0,[(1,2),(1,0),(1,0),(1,0),(1,0)], inputs['expected.stdout'], inputs['expected.stderr']),
        'skip-read': (7,5,0,[(1,2),(1,0),(1,0),(1,0),(1,0)], inputs['expected.stdout'].replace(b'AB',b''), inputs['expected.stderr']),
        'skip-request': (1,0,None,[(1,2)], b'', b''),
        'early-close': (0,0,141,[], b'', b'sh: 7: printf: printf: I/O error'),
        'wrong-env': (3,2,66,[(1,2),(1,0),(1,91)], b'denied ok\nAB\n', b''),
        'fd-leak': (7,5,68,[(1,2),(1,0),(1,0),(1,0),(1,95)], b'denied ok\nAB\nargv ok\npipe data\n', b''),
        'stderr-error': (7,5,141,[(1,2),(1,0),(1,0),(1,0),(1,0)], b'denied ok\nAB\nargv ok\npipe data\nclosed ok\n', b''),
    }
    copies, execs, parent, children, out, err = spec[label]
    lines = serial.splitlines()
    completion = f'NATIVE supervisor result={failure} reclaimed={count}'
    panic = 'AETHER PANIC: native C profile rejected'
    if (lines.count(completion)!=1 or serial.count('NATIVE supervisor result=')!=1
            or lines.count(panic)!=1 or serial.count('AETHER PANIC:')!=1
            or 'AETHER NATIVE CONNECTIONS PASS' in serial or lines.index(panic)<=lines.index(completion)):
        raise RuntimeError('SCRATCH-SESSION negative completion mismatch')
    terminals = [tuple(map(int,r)) for r in re.findall(r'^NATIVE terminal slot=(\d+) generation=(\d+) kind=(\d+) detail=(\d+)$', serial, re.M)]
    expected = {(0,1):(3,143) if parent is None else (1,parent)}
    expected.update({(2,g):v for g,v in enumerate(children,1)})
    if copies == 7:
        expected.update({(s, 1): (1, 0) for s in (3, 4)})
    if (len(terminals)!=count or sum(line.startswith('NATIVE terminal ') for line in lines)!=count
            or {r[:2]:r[2:] for r in terminals}!=expected):
        raise RuntimeError('SCRATCH-SESSION negative terminal mismatch')
    admitted = {(0,1)}
    if execs:
        admitted.update({(2, 2), (2, 3)})
    if execs == 5:
        admitted.update({(2, 5), (3, 1), (4, 1)})
    check_admissions(serial, admitted)
    rows = observations(serial)
    if len(rows)!=1 or rows[0][:3]!=(1,copies,execs) or rows[0][3]!=out or rows[0][4]!=err:
        raise RuntimeError('SCRATCH-SESSION negative observation mismatch')
    observed = next(i for i,line in enumerate(lines) if line.startswith('NATIVE SESSION '))
    positions = [i for i,line in enumerate(lines) if line.startswith('NATIVE terminal ')]
    if not max(positions)<observed<lines.index(completion):
        raise RuntimeError('SCRATCH-SESSION negative cleanup order mismatch')
