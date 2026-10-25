# SPDX-License-Identifier: BSD-2-Clause
"""Qualify the one-child native thread experiment; not pthread compatibility."""
import contextlib
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
import tempfile

from evidence import compact_run
from deps import ROOT
from memory_probe import build
from native_smoke import run
from regression import Parser


def check_terminals(serial, expected):
    rows = re.findall(r'^NATIVE terminal slot=([01]) generation=0 kind=([12]) detail=([0-9]+)$', serial, re.MULTILINE)
    if len(rows) != 2 or {row[0] for row in rows} != {'0', '1'}:
        raise RuntimeError('missing or duplicate thread domain terminals')
    for slot, kind, status in rows:
        if (int(kind), int(status)) != expected[int(slot)]:
            raise RuntimeError('wrong thread domain terminal reason')
    summaries = re.findall(r'^NATIVE terminal task=([01]) status=([0-9]+) output=([0-9]+) fs=([0-9a-f]+) ticks=[0-9]+$', serial, re.MULTILINE)
    if len(summaries) != 2 or {row[0] for row in summaries} != {'0', '1'}:
        raise RuntimeError('missing or duplicate thread domain summaries')
    for slot, status, output, fs in summaries:
        expected_status = expected[int(slot)][1]
        if int(status) != expected_status or int(output) != (24 if expected_status == 0 else 0) or int(fs, 16) == 0:
            raise RuntimeError('inconsistent thread domain summary')


def check_idle(serial):
    rows = re.findall(r'^NATIVE WAIT idle ticks=([0-9]+)$', serial, re.MULTILINE)
    if len(rows) != 1 or int(rows[0]) == 0:
        raise RuntimeError('missing actual idle timer progress')


def suite(libc_build, tools_lock, large=False, waits=False, stacks=False, storage=False, libc_tls=False, indefinite=False, libc_wait=False, libc_lock=False, pthread_preflight=False, signal_mask=False, pthread_lifecycle=False, pair=False):
    libc_wait = libc_wait or libc_lock
    libc_tls = libc_tls or libc_wait
    out = Path(tempfile.mkdtemp(prefix='thread-suite-', dir=ROOT / 'zig-out'))
    record = {'format': 'aether-native-threads-evidence-v1', 'status': 'incomplete',
              'pair': pair, 'large': large, 'waits': waits, 'stacks': stacks, 'storage': storage, 'libc_tls': libc_tls, 'indefinite': indefinite, 'libc_wait': libc_wait, 'libc_lock': libc_lock, 'pthread_preflight': pthread_preflight, 'signal_mask': signal_mask, 'pthread_lifecycle': pthread_lifecycle, 'commands': [], 'cases': []}
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    sources = [ROOT / 'build.zig']
    for parent in ('kernel', 'user/native-memory', 'user/native-taskq', 'scripts', 'tests'):
        sources += [p for p in (ROOT / parent).rglob('*') if p.is_file()
                    and '__pycache__' not in p.parts and p.name != '.DS_Store']
    record['sources'] = {str(p.relative_to(ROOT)): sha(p) for p in sources}
    now = lambda: datetime.now(timezone.utc).isoformat()

    def command(args, log):
        item = {'argv': args, 'start_utc': now(), 'status': 'running'}
        record['commands'].append(item)
        try:
            with log.open('wb') as stream:
                result = subprocess.run(args, cwd=ROOT, stdout=stream,
                                        stderr=subprocess.STDOUT, timeout=180)
            item['exit_code'] = result.returncode
            result.check_returncode()
            item['status'] = 'pass'
        except BaseException as error:
            item.update(status='failed', error=str(error))
            raise
        finally:
            item['end_utc'] = now()

    print('[RUNNING] Thread evidence:', out, file=sys.stderr, flush=True)
    try:
        images = {}
        for name, fault in [('positive', None), ('fault', 'THREAD_FAULT'), ('stop', 'STOP_LIVE'), ('parent-exit', 'THREAD_ALIAS' if stacks or storage or libc_tls else 'THREAD_PARENT_EXIT')]:
            with (out / (name + '-producer.log')).open('w') as log, contextlib.redirect_stdout(log):
                build(libc_build, tools_lock, out / name, fault, large, threads=True, waits=waits or indefinite, stacks=stacks, storage=storage or libc_tls, libc_tls=libc_tls or pthread_preflight, indefinite=indefinite, libc_wait=libc_wait, libc_lock=libc_lock, pthread_preflight=pthread_preflight, signal_mask=signal_mask, pthread_lifecycle=pthread_lifecycle, pair=pair)
            images[name] = out / name / 'native-c.bin'
        if libc_tls:
            with (out / 'bad-self-producer.log').open('w') as log, contextlib.redirect_stdout(log):
                build(libc_build, tools_lock, out / 'bad-self', 'LIBC_BAD_SELF', large, threads=True, storage=True, libc_tls=True, libc_wait=libc_wait, libc_lock=libc_lock)
            images['bad-self'] = out / 'bad-self/native-c.bin'
        if libc_wait:
            with (out / 'drop-wake-producer.log').open('w') as log, contextlib.redirect_stdout(log):
                build(libc_build, tools_lock, out / 'drop-wake', 'LIBC_DROP_WAKE', large, threads=True, storage=True, libc_tls=True, libc_wait=True, libc_lock=libc_lock)
            images['drop-wake'] = out / 'drop-wake/native-c.bin'
        if libc_lock:
            with (out / 'skip-lock-producer.log').open('w') as log, contextlib.redirect_stdout(log):
                build(libc_build, tools_lock, out / 'skip-lock', 'LIBC_SKIP_LOCK', large, threads=True, storage=True, libc_tls=True, libc_wait=True, libc_lock=True)
            images['skip-lock'] = out / 'skip-lock/native-c.bin'
        if pthread_lifecycle:
            with (out / 'bad-cap-producer.log').open('w') as log, contextlib.redirect_stdout(log):
                build(libc_build, tools_lock, out / 'bad-cap', 'LIFE_BAD_CAP', large, threads=True, pthread_lifecycle=True)
            images['bad-cap'] = out / 'bad-cap/native-c.bin'
            for name, fault in [('taskq', 'TASKQ_POSITIVE'), ('taskq-drain', 'TASKQ_PREMATURE_DRAIN'), ('taskq-delay', 'TASKQ_FALSE_DELAY'), ('taskq-free', 'TASKQ_INVALID_FREE'), ('taskq-alloc', 'TASKQ_ALLOC_FAIL'), ('taskq-reap', 'TASKQ_EARLY_REAP'), ('detached', 'LIFE_PAIR_DETACHED'), ('early-reap', 'LIFE_REAP_EARLY'), ('timed', 'LIFE_PAIR_TIME'), ('frozen-clock', 'LIFE_TIME_FROZEN'), ('keys', 'LIFE_PAIR_KEYS'), ('keys-bypass', 'LIFE_KEYS_BYPASS'), ('rwlock', 'LIFE_PAIR_RW'), ('rwlock-bypass', 'LIFE_RW_BYPASS'), ('condition-pair', 'LIFE_PAIR_COND'), ('condition-requeue-bypass', 'LIFE_PAIR_REQUEUE_BYPASS'), ('concurrent', 'LIFE_PAIR'), ('explicit-stack', 'LIFE_STACK_ATTR'), ('guard-fault', 'LIFE_GUARD_FAULT'), ('attr-bypass', 'LIFE_SKIP_ATTR_CHECK'), ('repeated', 'LIFE_REPEAT'), ('mutex', 'LIFE_MUTEX'), ('mutex-bypass', 'LIFE_MUTEX_BYPASS'), ('condition', 'LIFE_COND'), ('condition-bypass', 'LIFE_COND_BYPASS')]:
                with (out / (name + '-producer.log')).open('w') as log, contextlib.redirect_stdout(log):
                    build(libc_build, tools_lock, out / name, fault, large, threads=True, pthread_lifecycle=True)
                images[name] = out / name / 'native-c.bin'
        if pthread_preflight:
            with (out / 'bypass-producer.log').open('w') as log, contextlib.redirect_stdout(log):
                build(libc_build, tools_lock, out / 'bypass', 'PTHREAD_SKIP_PREFLIGHT', large, threads=True, libc_tls=True, pthread_preflight=True)
            images['bypass'] = out / 'bypass/native-c.bin'
        if pair:
            with (out / 'requeued-stop-producer.log').open('w') as log, contextlib.redirect_stdout(log):
                build(libc_build, tools_lock, out / 'requeued-stop', 'STOP_REQUEUED', large, threads=True, pair=True)
            images['requeued-stop'] = out / 'requeued-stop/native-c.bin'
        supervisors = [('supervised', 'positive', []), ('stop-live', 'stop', ['stop_live'])]
        if pair:
            supervisors.append(('requeued-stop-live', 'requeued-stop', ['stop_live']))
        if pthread_lifecycle:
            supervisors.append(('taskq-supervised', 'taskq', []))
            supervisors.append(('taskq-alloc-supervised', 'taskq-alloc', ['taskq_allocation_failure']))
            supervisors.append(('detached-supervised', 'detached', []))
            supervisors.append(('timed-supervised', 'timed', []))
            supervisors.append(('keys-supervised', 'keys', []))
            supervisors.append(('rwlock-supervised', 'rwlock', []))
            supervisors.append(('condition-pair-supervised', 'condition-pair', []))
            supervisors.append(('concurrent-supervised', 'concurrent', []))
            supervisors.append(('stack-supervised', 'explicit-stack', []))
            supervisors.append(('repeat-supervised', 'repeated', []))
            supervisors.append(('mutex-supervised', 'mutex', []))
            supervisors.append(('condition-supervised', 'condition', []))
        for name, worker, configs in supervisors:
            raw_path = out / (name + '.raw')
            args = ['rustc', '+1.98.0', '--edition=2024', '--target=x86_64-unknown-none',
                    '-C', 'opt-level=2', '-C', 'panic=abort', '-C', 'relocation-model=static',
                    '-C', 'link-arg=-Tuser/protection/linker.ld', '-C', 'link-arg=--oformat=binary',
                    'user/native-memory/supervisor.rs', '-o', str(raw_path)]
            if indefinite:
                args += ['--cfg', 'long_wait']
            for config in configs:
                args += ['--cfg', config]
            command(args, out / (name + '-producer.log'))
            code = raw_path.read_bytes()
            if not 0 < len(code) <= 4096:
                raise RuntimeError('supervisor exceeds fixed code budget')
            raw = images[worker].read_bytes()
            images[name] = out / (name + '.bin')
            images[name].write_bytes(struct.pack('<8sII', b'AENSUP01', len(raw) - 40, len(code)) + raw[8:40] + raw[40:] + code)
        cases = [('positive', 'positive', True, None, None),
                 ('supervised', 'supervised', True, None, None),
                 ('parent-exit', 'parent-exit', True, None, None),
                 ('stop-live', 'stop-live', True, None, None),
                 ('child-fault', 'fault', True, None, [(2, 134), (1, 0)]),
                 ('skip-pin', 'positive', True, 'native-threads-skip-pin', [(1, 194), (1, 194)]),
                 ('disabled', 'positive', False, None, [(1, 182), (1, 182)])]
        if waits or indefinite:
            cases = [('positive', 'positive', True, None, None),
                     ('supervised', 'supervised', True, None, None),
                     ('parent-exit', 'parent-exit', True, None, None),
                     ('stop-live', 'stop-live', True, None, None),
                     ('skip-compare', 'positive', True, 'native-wait-skip-compare', [(1, 215), (1, 215)]),
                     ('skip-wait-pin', 'positive', True, 'native-wait-skip-pin', [(1, 218), (1, 218)])]
        if stacks or storage or libc_tls:
            cases = [('positive', 'positive', True, None, None),
                     ('supervised', 'supervised', True, None, None),
                     ('alias-descriptor', 'parent-exit', True, None, None),
                     ('stop-live', 'stop-live', True, None, None),
                     ('guard-fault', 'fault', True, None, [(2, 142), (1, 0)]),
                     ('skip-pin', 'positive', True, 'native-threads-skip-pin', [(1, 194), (1, 194)])]
        if libc_tls:
            cases.append(('bad-self', 'bad-self', True, None, [(1, 291), (1, 291)]))
        if libc_wait:
            cases.append(('drop-wake', 'drop-wake', True, None, [(1, 289), (1, 289)]))
        if libc_lock:
            cases.append(('skip-lock', 'skip-lock', True, None, [(1, 286), (1, 286)]))
        if pthread_preflight:
            cases = [('positive', 'positive', True, None, None), ('supervised', 'supervised', True, None, None), ('bypass', 'bypass', True, None, [(1, 181), (1, 181)])]
        if signal_mask:
            cases.append(('skip-inherit', 'positive', True, 'native-mask-skip-inherit', [(1, 220), (1, 220)]))
        if pthread_lifecycle:
            cases = [('taskq', 'taskq', True, None, None),
                     ('taskq-supervised', 'taskq-supervised', True, None, None),
                     ('taskq-alloc-supervised', 'taskq-alloc-supervised', True, None, None),
                     ('taskq-drain', 'taskq-drain', True, None, [(1,328),(1,328)]),
                     ('taskq-delay', 'taskq-delay', True, None, [(1,329),(1,329)]),
                     ('taskq-free', 'taskq-free', True, None, [(1,303),(1,303)]),
                     ('taskq-alloc', 'taskq-alloc', True, None, [(1,302),(1,302)]),
                     ('taskq-reap', 'taskq-reap', True, None, [(1,312),(1,312)]),
                     ('detached', 'detached', True, None, None),
                     ('detached-supervised', 'detached-supervised', True, None, None),
                     ('early-reap', 'early-reap', True, None, [(1,291),(1,291)]),
                     ('timed', 'timed', True, None, None),
                     ('timed-supervised', 'timed-supervised', True, None, None),
                     ('frozen-clock', 'frozen-clock', True, None, [(1,271),(1,271)]),
                     ('clock-disabled', 'timed', True, None, [(1,274),(1,274)]),
                     ('keys', 'keys', True, None, None),
                     ('keys-supervised', 'keys-supervised', True, None, None),
                     ('keys-bypass', 'keys-bypass', True, None, [(1,263),(1,263)]),
                     ('rwlock', 'rwlock', True, None, None),
                     ('rwlock-supervised', 'rwlock-supervised', True, None, None),
                     ('rwlock-bypass', 'rwlock-bypass', True, None, [(1,251),(1,251)]),
                     ('condition-pair', 'condition-pair', True, None, None),
                     ('condition-pair-supervised', 'condition-pair-supervised', True, None, None),
                     ('condition-requeue-bypass', 'condition-requeue-bypass', True, None, [(1,239),(1,239)]),
                     ('positive', 'positive', True, None, None),
                     ('supervised', 'supervised', True, None, None),
                     ('bad-cap', 'bad-cap', True, None, None),
                     ('attr-bypass', 'attr-bypass', True, None, [(1, 183), (1, 183)]),
                     ('repeated', 'repeated', True, None, None),
                     ('repeat-supervised', 'repeat-supervised', True, None, None),
                     ('mutex', 'mutex', True, None, None),
                     ('mutex-supervised', 'mutex-supervised', True, None, None),
                     ('mutex-bypass', 'mutex-bypass', True, None, [(1, 242), (1, 242)]),
                     ('condition', 'condition', True, None, None),
                     ('condition-supervised', 'condition-supervised', True, None, None),
                     ('condition-bypass', 'condition-bypass', True, None, [(1, 252), (1, 252)]),
                     ('same-id', 'repeated', True, 'native-child-same-id', [(1, 233), (1, 233)]),
                     ('explicit-stack', 'explicit-stack', True, None, None),
                     ('stack-supervised', 'stack-supervised', True, None, None),
                     ('concurrent', 'concurrent', True, None, None),
                     ('concurrent-supervised', 'concurrent-supervised', True, None, None),
                     ('concurrent-disabled', 'concurrent', True, None, [(1,202),(1,202)]),
                     ('concurrent-same-id', 'concurrent', True, 'native-child-same-id', [(1,203),(1,203)]),
                     ('guard-fault', 'guard-fault', True, None, [(2, 142), (1, 0)]),
                     ('skip-pin', 'positive', True, 'native-threads-skip-pin', [(1, 216), (1, 216)]),
                     ('child-fault', 'fault', True, None, [(2, 134), (1, 0)])]
        if pair:
            cases = [('positive', 'positive', True, None, None),
                     ('supervised', 'supervised', True, None, None),
                     ('parent-exit', 'parent-exit', True, None, None),
                     ('stop-live', 'stop-live', True, None, None),
                     ('child-fault', 'fault', True, None, [(2,134),(1,0)]),
                     ('skip-pin', 'positive', True, 'native-threads-skip-pin', [(1,191),(1,191)]),
                     ('disabled-pair', 'positive', True, None, [(1,190),(1,190)]),
                     ('unlimited-wake', 'positive', True, 'native-wake-unlimited', [(1,201),(1,201)]),
                     ('skip-requeue', 'positive', True, 'native-requeue-skip-move', [(1,205),(1,205)]),
                     ('requeued-stop-live', 'requeued-stop-live', True, None, None)]
        for name, producer, enabled, mutant, expected in cases:
            dest = out / ('run-' + name)
            dest.mkdir()
            item = {'name': name, 'status': 'running', 'start_utc': now(),
                    'envelope_sha256': sha(images[producer]), 'expected_terminals': expected}
            record['cases'].append(item)
            args = ['zig', 'build', '-Dsmp=false', '-Dnative-memory=true',
                    '-Dnative-c-image=' + str(images[producer]), '-p', str(dest),
                    '--cache-dir', str(ROOT / '.zig-cache'), '--global-cache-dir', str(ROOT / '.zig-cache/global')]
            if enabled:
                args += ['-Dnative-threads=true']
            if name.startswith('taskq') or pair and name != 'disabled-pair' or name in ('detached', 'detached-supervised', 'early-reap', 'timed', 'timed-supervised', 'frozen-clock', 'keys', 'keys-supervised', 'keys-bypass', 'rwlock', 'rwlock-supervised', 'rwlock-bypass', 'condition-pair', 'condition-pair-supervised', 'condition-requeue-bypass', 'concurrent', 'concurrent-supervised', 'concurrent-same-id'):
                args += ['-Dnative-thread-pair=true']
            if large:
                args += ['-Dnative-memory-large=true']
            if mutant:
                args += ['-D' + mutant + '=true']
            command(args, dest / 'build.log')
            with contextlib.redirect_stdout(sys.stderr):
                run(dest / 'aether.iso', expected_panic=b'native C profile rejected' if expected else None,
                    marker=b'AETHER NATIVE SUPERVISION PASS' if name in ('taskq-supervised', 'taskq-alloc-supervised', 'detached-supervised', 'timed-supervised', 'keys-supervised', 'rwlock-supervised', 'condition-pair-supervised', 'supervised', 'stop-live', 'stack-supervised', 'repeat-supervised', 'mutex-supervised', 'condition-supervised', 'concurrent-supervised', 'requeued-stop-live') else b'AETHER NATIVE C PASS')
            serial = (dest / 'native-serial.log').read_text()
            if expected:
                check_terminals(serial, expected)
            elif name in ('taskq', 'detached', 'timed', 'keys', 'rwlock', 'condition-pair', 'positive', 'parent-exit', 'alias-descriptor', 'bad-cap', 'explicit-stack', 'repeated', 'mutex', 'condition', 'concurrent'):
                check_terminals(serial, [(1, 0), (1, 0)])
            elif name == 'taskq-alloc-supervised':
                if 'NATIVE terminal slot=0 generation=2 kind=1 detail=302\n' not in serial:
                    raise RuntimeError('missing replaced taskq allocation failure')
            else:
                if 'NATIVE terminal slot=0 generation=2 kind=1 detail=0\n' not in serial:
                    raise RuntimeError('missing fresh thread domain completion')
            if (waits or indefinite) and name == 'positive':
                check_idle(serial)
            if name == 'child-fault' and not re.search(r'NATIVE fault vector=6 rip=[0-9a-f]+ error=0\n', serial):
                raise RuntimeError('missing actual child invalid-opcode fault')
            if name == 'guard-fault' and not re.search(r'NATIVE fault vector=14 rip=[0-9a-f]+ error=4\n', serial):
                raise RuntimeError('missing actual stack guard fault')
            item.update(status='pass', end_utc=now(), iso_sha256=sha(dest / 'aether.iso'),
                        serial_sha256=sha(dest / 'native-serial.log'))
        for name, digest in record['sources'].items():
            if sha(ROOT / name) != digest:
                raise RuntimeError('sources changed during thread qualification')
        record['status'] = 'pass'
    except BaseException as error:
        record.update(status='failed', error=str(error))
        raise
    finally:
        record['end_utc'] = now()
        (out / 'results.json').write_text(json.dumps(record, indent=2) + '\n')
        compact_run(out, record)
    print(f'[PASS] {len(cases)} native {"pthread lifecycle" if pthread_lifecycle else "signal mask" if signal_mask else "pthread preflight" if pthread_preflight else "libc lock" if libc_lock else "libc wait" if libc_wait else "indefinite wait" if indefinite else "libc TLS" if libc_tls else "storage" if storage else "stack" if stacks else "wait" if waits else "thread"} cases:', out, file=sys.stderr)


if __name__ == '__main__':
    parser = Parser(description=__doc__)
    parser.add_argument('--libc-build', required=True)
    parser.add_argument('--tools-lock', required=True)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--pair', action='store_true', help='Run two concurrent native children, ID observation and cleanup')
    mode.add_argument('--pthread-lifecycle', action='store_true', help='Run bounded actual pthread create/exit/join integration')
    mode.add_argument('--signal-mask', action='store_true', help='Run per-context mask state, inheritance and rejection checks')
    mode.add_argument('--pthread-preflight', action='store_true', help='Run actual pthread_create unsupported-setup rejection')
    mode.add_argument('--libc-lock', action='store_true', help='Run contended musl internal lock/unlock integration')
    mode.add_argument('--libc-wait', action='store_true', help='Run actual musl internal wait/wake integration')
    mode.add_argument('--indefinite', action='store_true', help='Run no-deadline wait, wake and teardown checks')
    mode.add_argument('--libc-tls', action='store_true', help='Run actual musl TLS construction and child libc checks')
    mode.add_argument('--storage', action='store_true', help='Run TLS extent and separate TID-storage qualification')
    mode.add_argument('--stacks', action='store_true', help='Run stack-range admission, guard, pin and replacement checks')
    mode.add_argument('--waits', action='store_true', help='Run compare/wait/wake, idle and teardown qualification')
    parser.add_argument('--large', action='store_true', help='Use the opt-in 8 MiB backing profile')
    parser.add_argument('--version', action='version', version='aether-thread-smoke 1')
    args = parser.parse_args()
    try:
        suite(args.libc_build, args.tools_lock, args.large, args.waits, args.stacks, args.storage, args.libc_tls, args.indefinite, args.libc_wait, args.libc_lock, args.pthread_preflight, args.signal_mask, args.pthread_lifecycle, args.pair)
    except (OSError, RuntimeError, TimeoutError, subprocess.SubprocessError) as error:
        parser.exit(1, f'[FAIL] {error}\n')
