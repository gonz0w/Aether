# SPDX-License-Identifier: BSD-2-Clause
"""Frozen failed-exec session workload and native observation checks."""
import hashlib
import json
import re
from pathlib import Path
from fixture_inputs import read_inputs
from deps import ROOT
from session_smoke import observations

INPUTS = {'experiments/dash-native/failed-exec-session/composed.sh': '62013e4600ea11967c0cd1c018805d31542b3fafc1b0b7ac71498eda082a6ec8', 'experiments/dash-native/failed-exec-session/expected.stdout': '37821d781d271d7002ecb806fcbcc33aeb3d655a1918f007560b8f3a2b362b39', 'experiments/dash-native/failed-exec-session/expected.stderr': 'f30e55cb4af6b5cd4dc09e51c5ef921264f0129f210248b56281c63198bf4565', 'experiments/dash-reference/helper.c': '3fdea5d515011e49516f35cf8b9abdc214024a226bb3ba560480fa9775cebcf8', 'experiments/dash-native/SESSION-FAILED-EXEC.md': 'ecb4ccf10db3cee9596c73b5526bd67e62020d98406ba9625bb41aa6eb70cb1d', 'experiments/dash-native/failed-exec-session/manifest.json': '0cc89d99029055145280dcd1153157692b1ad9c7adf020686f59a0f5a01031bb'}
CASES = [
    ('composed', '', '', None, 24),
    ('wrong-missing', '', 'exec_wrong_missing', 2860, 2),
    ('wrong-denied', '', 'exec_wrong_denied', 2861, 3),
    ('wrong-env', 'SESSION_WRONG_ENV', 'exec_wrong_env', 2862, 4),
    ('fd-leak', 'SESSION_FD_LEAK', 'exec_fd_leak', 2863, 8),
    ('skip-request', 'EXEC_SKIP_REQUEST', '', 2864, 2),
    ('stderr-error', '', 'exec_stderr_error', 2865, 8),
    ('stale-wait', 'SESSION_STALE_WAIT', '', None, 24),
    ('bad-byte', 'SESSION_BAD_BYTE', '', None, 24),
]


def consumer_inputs():
    return read_inputs('failed-exec-session-2026-09-29', INPUTS)


def check_admissions(serial, expected):
    lines = serial.splitlines()
    records = [tuple(map(int, match)) for match in re.findall(
        r'^NATIVE MEMORY admitted slot=(\d+) generation=(\d+) used=(\d+) remaining=(\d+)$', serial, re.M)]
    if (len(records) != len(expected) or {r[:2] for r in records} != expected
            or sum(line.startswith('NATIVE MEMORY admitted ') for line in lines) != len(expected)
            or any(r[2] == 0 for r in records)):
        raise RuntimeError('EXEC-SESSION admission identity mismatch')
    for slot, generation, used, remaining in records:
        admission = lines.index(f'NATIVE MEMORY admitted slot={slot} generation={generation} used={used} remaining={remaining}')
        terminal = next(i for i,line in enumerate(lines) if line.startswith(
            f'NATIVE terminal slot={slot} generation={generation} kind='))
        if admission >= terminal:
            raise RuntimeError('EXEC-SESSION admission after terminal')


def check_failed_exec(serial, label, inputs):
    if label not in ('composed', 'stale-wait', 'bad-byte'):
        return check_negative(serial, label)

    lines = serial.splitlines()
    completion = 'NATIVE supervisor result=100 reclaimed=24'
    marker = 'AETHER NATIVE CONNECTIONS PASS'
    if (lines.count(completion) != 1 or serial.count('NATIVE supervisor result=') != 1
            or lines.count(marker) != 1 or 'PANIC' in serial
            or lines.index(completion) >= lines.index(marker)):
        raise RuntimeError('EXEC-SESSION completion mismatch')
    terminals = [tuple(map(int, row)) for row in re.findall(
        r'^NATIVE terminal slot=(\d+) generation=(\d+) kind=(\d+) detail=(\d+)$', serial, re.M)]
    expected = {(0,g):(1,0) for g in range(1,4)}
    expected.update({(2,g):(1,127 if (g-1)%5 == 0 else 126 if (g-1)%5 == 1 else 0) for g in range(1,16)})
    expected.update({(s,g):(1,0) for s in (3,4) for g in range(1,4)})
    if (len(terminals) != 24 or sum(line.startswith('NATIVE terminal ') for line in lines) != 24
            or {r[:2]:r[2:] for r in terminals} != expected):
        raise RuntimeError('EXEC-SESSION terminal mismatch')
    check_admissions(serial, {(s,g) for s in (0,3,4) for g in range(1,4)} |
                     {(2,g) for g in (3,5,8,10,13,15)})
    rows = observations(serial)
    if rows != [(g,7,4,inputs['expected.stdout'],inputs['expected.stderr']) for g in range(1,4)]:
        raise RuntimeError('EXEC-SESSION stream mismatch')
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
            raise RuntimeError('EXEC-SESSION phase order mismatch')
        previous=observed[g-1]


def check_negative(serial, label):
    _, _, _, failure, count = next(row for row in CASES if row[0] == label)
    spec = {
        'wrong-missing': (1,0,(1,51),[(1,126)],b''),
        'wrong-denied': (2,0,(1,52),[(1,127),(1,127)],b''),
        'wrong-env': (3,1,(1,53),[(1,127),(1,126),(1,91)],b'exec errors ok\n'),
        'fd-leak': (7,4,(1,55),[(1,127),(1,126),(1,0),(1,0),(1,95)],b'exec errors ok\nargv ok\npipe data\n'),
        'skip-request': (1,0,(3,143),[(1,127)],b''),
        'stderr-error': (7,4,(1,141),[(1,127),(1,126),(1,0),(1,0),(1,0)],b'exec errors ok\nargv ok\npipe data\nclosed ok\n'),
    }
    copies, execs, parent, children, stdout = spec[label]
    lines=serial.splitlines()
    completion=f'NATIVE supervisor result={failure} reclaimed={count}'
    panic='AETHER PANIC: native C profile rejected'
    if (lines.count(completion)!=1 or serial.count('NATIVE supervisor result=')!=1
            or lines.count(panic)!=1 or serial.count('AETHER PANIC:')!=1
            or 'AETHER NATIVE CONNECTIONS PASS' in serial or lines.index(panic)<=lines.index(completion)):
        raise RuntimeError('EXEC-SESSION negative completion mismatch')
    terminals=[tuple(map(int,r)) for r in re.findall(r'^NATIVE terminal slot=(\d+) generation=(\d+) kind=(\d+) detail=(\d+)$',serial,re.M)]
    expected={(0,1):parent};expected.update({(2,g):v for g,v in enumerate(children,1)})
    if copies==7:expected.update({(s,1):(1,0) for s in (3,4)})
    if (len(terminals)!=count or sum(line.startswith('NATIVE terminal ') for line in lines)!=count
            or {r[:2]:r[2:] for r in terminals}!=expected):
        raise RuntimeError('EXEC-SESSION negative terminal mismatch')
    admitted = {(0,1)}
    if execs: admitted.add((2,3))
    if execs == 4: admitted.update({(2,5),(3,1),(4,1)})
    check_admissions(serial, admitted)
    if observations(serial)!=[(1,copies,execs,stdout,b'')]:
        raise RuntimeError('EXEC-SESSION negative observation mismatch')
    observation=next(i for i,v in enumerate(lines) if v.startswith('NATIVE SESSION '))
    positions=[i for i,v in enumerate(lines) if v.startswith('NATIVE terminal ')]
    if not max(positions)<observation<lines.index(completion):
        raise RuntimeError('EXEC-SESSION negative cleanup mismatch')
    def pos(slot,g):
        k,d=expected[(slot,g)]
        return lines.index(f'NATIVE terminal slot={slot} generation={g} kind={k} detail={d}')
    if not all(pos(2,g)<pos(2,g+1) for g in range(1,len(children))) or pos(2,len(children))>=pos(0,1):
        raise RuntimeError('EXEC-SESSION negative phase mismatch')
    if copies==7 and not pos(2,3)<min(pos(2,4),pos(3,1),pos(4,1))<=max(pos(2,4),pos(3,1),pos(4,1))<pos(2,5):
        raise RuntimeError('EXEC-SESSION negative pipeline order mismatch')
