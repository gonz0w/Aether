# SPDX-License-Identifier: BSD-2-Clause
"""Build and observe the bounded, unchanged dash SESSION consumer workload."""
import hashlib
import json
import re
import struct
from collections import Counter
from pathlib import Path

from fixture_inputs import read_inputs
from deps import ROOT

INPUTS = {
    'experiments/dash-native/session/composed.sh': '7198674f3caddffb414eede635dc99554cdfa8aa0f78f11dfbec0a8769084aaf',
    'experiments/dash-native/session/expected.stdout': '1ce618850d679001b403ab163a67b8758105fe338f1af2b670825b326a0203f4',
    'experiments/dash-native/session/expected.stderr': 'bedec5c40043515e48d87e3cb292087342a4bc2d1ababb6d8c2f3c2afa009a75',
    'experiments/dash-reference/helper.c': '3fdea5d515011e49516f35cf8b9abdc214024a226bb3ba560480fa9775cebcf8',
    'experiments/dash-native/SESSION.md': '0fd3f84261af864eafe73d72bc7927c3e49b64baf3466af55bfa3220d9447ba1',
    'experiments/dash-native/session/manifest.json': '40a923d4d16064785c17df104e253f29349f79d959351084691ba36a5472791d',
}


def consumer_inputs():
    return read_inputs('shell-streams-2026-09-24', INPUTS)


# Each negative terminates only after cleanup of every actually admitted worker.
CASES = [
    ('composed', '', '', None, 30),
    ('wrong-env', 'SESSION_WRONG_ENV', 'session_wrong_env', 2800, 2),
    ('bad-byte', 'SESSION_BAD_BYTE', '', None, 30),
    ('bad-substitution', '', 'session_bad_substitution', 2801, 6),
    ('fd-leak', 'SESSION_FD_LEAK', 'session_fd_leak', 2802, 10),
    ('stale-wait', 'SESSION_STALE_WAIT', '', None, 30),
    ('stale-accept', 'SESSION_STALE_WAIT', 'session_stale_accept', 2803, 5),
    ('retained-writer', 'SESSION_RETAINED_WRITER', 'session_retained_writer', 2804, 5),
]


def build_cases(command, cc, flags, output, report, entropy, recovery=False, failed_exec=False, scratch=False, serial=False):
    if serial:
        from serial_session import consumer_inputs as read_inputs, INPUTS as pins, CASES as cases_spec
        inputs = read_inputs()
    elif scratch:
        from scratch_smoke import consumer_inputs as read_inputs, INPUTS as pins, CASES as cases_spec
        inputs = read_inputs()
    elif failed_exec:
        from failed_exec_smoke import consumer_inputs as read_inputs, INPUTS as pins, CASES as cases_spec
        inputs = read_inputs()
    elif recovery:
        from recovery_smoke import consumer_inputs as read_inputs, INPUTS as pins, CASES as cases_spec
        inputs = read_inputs()
    else:
        pins, cases_spec, inputs = INPUTS, CASES, consumer_inputs()
    prefix = 'serial-session' if serial else 'scratch' if scratch else 'failed-exec' if failed_exec else 'recovery' if recovery else 'session'
    report[prefix + '_inputs'] = pins
    helper = output / (prefix + '-helper.c')
    helper.write_bytes(inputs['helper.c'])
    command(cc + flags + ['-c', str(helper), '-o', str(output / (prefix + '-helper-body.o'))], prefix + '-helper-body')
    source = 'user/native-capacity/session-client.c'
    script = '-DAETHER_SESSION_SCRIPT=' + json.dumps(inputs['early-reader.sh' if recovery else 'composed.sh'].decode())
    parent_template = next(c.copy() for c in report['commands'] if '-c' not in c and '-o' in c
                           and c[c.index('-o') + 1].endswith('/remap-helper-natural-main-fds-parent' + ('-serial' if serial else '') + '-worker.elf'))
    helper_template = next(c.copy() for c in report['commands'] if '-c' not in c and '-o' in c
                           and c[c.index('-o') + 1].endswith('/consumer-parent-replacement-worker.elf'))

    def client(label, defines, template, original):
        obj, elf = output / (label + '.o'), output / (label + '.elf')
        command(cc + flags + defines + ['-c', source, '-o', str(obj)], label)
        link = [str(obj) if v.endswith('/' + original + '.o') else
                str(output / (prefix + '-helper-body.o')) if v.endswith('/consumer-helper.o') else v for v in template]
        link[link.index('-o') + 1] = str(elf)
        if '-Wl,--wrap=_exit' not in link:
            link += ['-Wl,--wrap=_exit']
        command(link, label + '-link')
        return elf.read_bytes()

    helper_image = client(prefix + '-helper', ['-DSESSION_HELPER'] + (['-DSESSION_SERIAL'] if serial else []) + (['-DSESSION_SCRATCH'] if scratch else []), helper_template, 'consumer-parent-replacement-worker')
    parents, owners, cases = {}, {}, []
    for label, c_define, config, failure, reclaimed in cases_spec:
        if c_define not in parents:
            parents[c_define] = client(prefix + '-parent-' + label, [script] + (['-DSESSION_SERIAL'] if serial else []) + (['-DSESSION_SCRATCH'] if scratch else []) + (['-DSESSION_FAILED_EXEC'] if failed_exec else []) + (['-DSESSION_RECOVERY'] if recovery else []) + (['-D' + c_define] if c_define else []),
                                       parent_template, 'remap-helper-natural-main-fds-parent' + ('-serial' if serial else '') + '-worker')
        if config not in owners:
            raw = output / (prefix + '-owner-' + label + '.raw')
            args = ['rustc', '+1.98.0', '--edition=2024', '--target=x86_64-unknown-none', '-C', 'opt-level=s',
                    '-C', 'panic=abort', '-C', 'relocation-model=static', '-C', 'lto=fat', '-C', 'codegen-units=1',
                    '-C', 'link-arg=-Tuser/native-capacity/linker.ld', '-C', 'link-arg=--oformat=binary',
                    'user/native-capacity/session-owner.rs', '--cfg', 'pipeline_dash_parent', '-o', str(raw)] + (['--cfg', 'session_serial'] if serial else []) + (['--cfg', 'session_scratch'] if scratch else []) + (['--cfg', 'session_failed_exec'] if failed_exec else []) + (['--cfg', 'session_recovery'] if recovery else []) + (['--cfg', config] if config else [])
            command(args, prefix + '-owner-' + label)
            linked = [v for v in args if v != 'link-arg=--oformat=binary']
            # Remove the -C that belonged to binary format.
            at = linked.index('user/native-capacity/session-owner.rs')
            assert linked[at - 1] == '-C'
            linked.pop(at - 1)
            linked[linked.index('-o') + 1] = str(raw.with_suffix('.elf'))
            command(linked, prefix + '-owner-' + label + '-link')
            owners[config] = raw.read_bytes()
            assert 0 < len(owners[config]) <= 24576
        parent, owner = parents[c_define], owners[config]
        payload = struct.pack('<8sIIIIQ', b'AENMX008' if serial else b'AENMX007', len(parent), len(helper_image), len(parent), len(owner), 0)
        payload += entropy + parent + helper_image + parent + owner
        context = (f'NATIVE supervisor result={failure} reclaimed={reclaimed}'.encode(),) if failure else ()
        cases.append((prefix + '-' + label, payload, True, b'native C profile rejected' if failure else None, context))
    return cases


def observations(serial):
    rows = []
    for line in serial.splitlines():
        if 'NATIVE SESSION' not in line:
            continue
        match = re.fullmatch(r'NATIVE SESSION generation=([1-3]) copies=([0-9]+) execs=([0-9]+) stdout=([0-9a-f]*) stderr=([0-9a-f]*)', line)
        if not match or any(len(match[n]) % 2 for n in (4, 5)):
            raise RuntimeError('invalid SESSION observation')
        generation, copies, execs = (int(match[n]) for n in (1, 2, 3))
        out, err = bytes.fromhex(match[4]), bytes.fromhex(match[5])
        if len(out) > 128 or len(err) > 32 or not 0 <= execs <= copies <= 9:
            raise RuntimeError('unbounded SESSION observation')
        rows.append((generation, copies, execs, out, err))
    return rows


def check_session(serial, label, inputs):
    """Validate independent stream/lifecycle observations, never guest success alone."""
    case = next(c for c in CASES if c[0] == label)
    _, _, _, failure, reclaimed = case
    if serial.count(f'NATIVE supervisor result={failure or 100} reclaimed={reclaimed}') != 1:
        raise RuntimeError('SESSION completion mismatch')
    if serial.count('NATIVE supervisor result=') != 1:
        raise RuntimeError('duplicate SESSION completion')
    if failure is None and ('PANIC' in serial or serial.count('AETHER NATIVE CONNECTIONS PASS') != 1):
        raise RuntimeError('SESSION did not finish normally')
    rows = observations(serial)
    lines = serial.splitlines()
    completion = next(i for i, line in enumerate(lines) if line.startswith('NATIVE supervisor result='))
    terminal_positions = [i for i, line in enumerate(lines) if line.startswith('NATIVE terminal slot=')]
    observation_positions = [i for i, line in enumerate(lines) if line.startswith('NATIVE SESSION ')]
    if not terminal_positions or not observation_positions or not max(terminal_positions) < max(observation_positions) < completion:
        raise RuntimeError('SESSION early completion or observation')
    final_marker = 'AETHER PANIC: native C profile rejected' if failure else 'AETHER NATIVE CONNECTIONS PASS'
    if final_marker not in lines or lines.index(final_marker) <= completion:
        raise RuntimeError('SESSION early final marker')
    terminals = [tuple(map(int, m)) for m in re.findall(r'^NATIVE terminal slot=(\d+) generation=(\d+) kind=(\d+) detail=(\d+)$', serial, re.M)]
    if len(terminals) != reclaimed or len({r[:2] for r in terminals}) != reclaimed:
        raise RuntimeError('SESSION terminal identity/count mismatch')
    if failure is None:
        expected = [(g, 9, 7, inputs['expected.stdout'], inputs['expected.stderr']) for g in range(1, 4)]
        ids = {(0, g) for g in range(1, 4)} | {(2, g) for g in range(1, 16)} | {(s, g) for s in (3, 4) for g in range(1, 7)}
        if {r[:2] for r in terminals} != ids or any(r[2:] != (1, 0) for r in terminals):
            raise RuntimeError('SESSION terminal status mismatch')
        if serial.count('NATIVE MEMORY admitted slot=') != 24:
            raise RuntimeError('SESSION image admission mismatch')
        if rows != expected:
            raise RuntimeError('SESSION stream mismatch')
    else:
        if serial.count('AETHER PANIC: native C profile rejected') != 1 or 'AETHER NATIVE CONNECTIONS PASS' in serial:
            raise RuntimeError('SESSION negative rejection missing')
        count = {'wrong-env': (1, 1, 31), 'bad-substitution': (5, 4, 33), 'fd-leak': (9, 7, 35),
                 'stale-accept': (4, 3, 144), 'retained-writer': (4, 3, None)}[label]
        if len(rows) != 1 or rows[0][:3] != (1, *count[:2]):
            raise RuntimeError('SESSION negative observation mismatch')
        parent = next((r for r in terminals if r[:2] == (0, 1)), None)
        if parent is None or parent[2:] != ((3, 143) if count[2] is None else (1, count[2])):
            raise RuntimeError('SESSION negative parent result mismatch')
        required = {'wrong-env': (2, 1, 1, 91), 'fd-leak': (2, 5, 1, 95)}.get(label)
        if required is not None and required not in terminals:
            raise RuntimeError('SESSION helper rejection missing')
        rounds = {'wrong-env': (1, 0), 'bad-substitution': (3, 1), 'fd-leak': (5, 2),
                  'stale-accept': (2, 1), 'retained-writer': (2, 1)}[label]
        ids = {(0, 1)} | {(2, g) for g in range(1, rounds[0] + 1)} | {(s, g) for s in (3, 4) for g in range(1, rounds[1] + 1)}
        if {r[:2] for r in terminals} != ids or any(r[2] not in (1, 3) for r in terminals):
            raise RuntimeError('SESSION negative identity/fault mismatch')
        prefix = {'wrong-env': b'', 'bad-substitution': b'argv ok\npipe data\n',
                  'fd-leak': b'argv ok\npipe data\nsubstitution ok\npipe data\n',
                  'stale-accept': b'argv ok\n', 'retained-writer': b'argv ok\npipe data\n'}[label]
        actual, errors = rows[0][3:]
        # The stale-wait probe races real pipeline progress, so only an observed
        # prefix is promised before confirmed stop. Retained-writer reaches EOF.
        valid = actual.startswith(prefix) and b'pipe data\n'.startswith(actual[len(prefix):]) if label == 'stale-accept' else actual == prefix
        if not valid or errors:
            raise RuntimeError('SESSION negative stream mismatch')
        if label == 'retained-writer' and Counter(r[2] for r in terminals) != Counter({1: 2, 3: 3}):
            raise RuntimeError('SESSION retained writer cleanup mismatch')
    return rows
