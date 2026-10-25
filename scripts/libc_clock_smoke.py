# SPDX-License-Identifier: BSD-2-Clause
"""Private real-clock musl conditions/sleep; keep compact results, not artifacts."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import sys
from datetime import datetime, timezone
from deps import ROOT
from evidence import compact_run
from memory_probe import build
from native_smoke import run
from regression import Parser
from thread_smoke import check_terminals


def check_clock_trace(serial):
    parks = re.findall(r'^NATIVE CLOCK park task=([0-9]+) start=([0-9]+) deadline=([0-9]+)$', serial, re.MULTILINE)
    timeouts = re.findall(r'^NATIVE CLOCK timeout task=([0-9]+) now=([0-9]+) elapsed=([0-9]+)$', serial, re.MULTILINE)
    if any(not 0 < int(elapsed) <= int(now) for _, now, elapsed in timeouts):
        raise RuntimeError('invalid registered timeout observation')
    deadlines = {}
    for task, start, deadline in parks:
        if not 0 < int(deadline) - int(start) <= 1000000000:
            raise RuntimeError('invalid registered libc deadline')
        deadlines.setdefault(task, []).append(int(deadline))
    if set(deadlines) != {'0', '1'} or {t for t, _, _ in timeouts} != {'0', '1'}:
        raise RuntimeError('missing or foreign clock owner')
    repeats = 0
    for task, values in deadlines.items():
        count = sum(values.count(d) - 1 for d in set(values))
        if count < 2 or sum(t == task for t, _, _ in timeouts) < 4:
            raise RuntimeError('missing actual spurious retries or sleep/condition timeouts')
        repeats += count
    return {'parks': len(parks), 'timeouts': len(timeouts), 'same_deadline_retries': repeats}


def selected_cases(long_waits=False, case=None):
    cases = (
        ('real', 'LIFE_REAL_TIME', True, None, 0),
        ('repeat', 'LIFE_REAL_TIME', True, None, 0),
        ('early', 'LIFE_REAL_TIME', True, 'native-clock-skip-wait', 331),
        ('disabled', 'LIFE_REAL_TIME', False, None, 330),
        ('legacy', 'LIFE_PAIR_TIME', False, None, 0))
    if long_waits:
        cases = cases[:3] + (('old-bound', 'LIFE_REAL_TIME', True, None, 341),)
    if case is not None:
        cases = tuple(row for row in cases if row[0] == case)
        if not cases:
            raise ValueError('case unavailable in selected clock profile: ' + case)
    return cases


def suite(libc_build, tools_lock, long_waits=False, case=None):
    cases = selected_cases(long_waits, case)
    out = Path(tempfile.mkdtemp(prefix='thread-suite-clock-', dir=ROOT / 'zig-out'))
    record = {'status': 'incomplete', 'scope': 'private BSP musl timed conditions/sleep; not SDK adoption',
              'commands': [], 'cases': []}
    record['long_waits'] = long_waits
    record['selected_case'] = case
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    sources = [ROOT / 'build.zig']
    for parent in ('kernel', 'user/native-memory', 'scripts'):
        sources += [p for p in (ROOT / parent).rglob('*') if p.is_file()
                    and '__pycache__' not in p.parts and p.name != '.DS_Store']
    record['sources'] = {str(p.relative_to(ROOT)): sha(p) for p in sources}
    now = lambda: datetime.now(timezone.utc).isoformat()

    def command(argv, log):
        row = {'argv': [str(a) for a in argv], 'start_utc': now(), 'status': 'running'}
        record['commands'].append(row)
        try:
            with log.open('wb') as stream:
                result = subprocess.run(row['argv'], cwd=ROOT, stdout=stream,
                                        stderr=subprocess.STDOUT, timeout=180)
            row['exit_code'] = result.returncode
            result.check_returncode()
            row['status'] = 'pass'
        except BaseException as error:
            row.update(status='failed', error=str(error))
            raise
        finally:
            row['end_utc'] = now()

    print('[RUNNING] Libc clock results:', out, file=sys.stderr, flush=True)
    try:
        for name, fault, clock, mutant, status in cases:
            row = {'name': name, 'status': 'running', 'start_utc': now(),
                   'expected_terminal': status}
            record['cases'].append(row)
            # Producer hashes/commands are retained by memory_probe's receipt.
            producer = out / (name + '-producer')
            build(libc_build, tools_lock, producer, fault, threads=True,
                  pthread_lifecycle=True, long_waits=long_waits)
            if name == 'old-bound':
                recipe = json.loads((producer / 'evidence.json').read_text())['commands']
                original = next(c for c in recipe if c[-1] == str(producer / 'real_time.o'))
                command([a for a in original if a != '-DAETHER_LONG_WAITS'],
                        producer / 'old-bound-compile.log')
                command(recipe[-1], producer / 'old-bound-link.log')
                envelope = producer / 'native-c.bin'
                envelope.write_bytes(envelope.read_bytes()[:40] +
                                     (producer / 'probe.elf').read_bytes())
                receipt = json.loads((producer / 'evidence.json').read_text())
                receipt.update(original_elf_sha256=receipt['elf_sha256'],
                               original_envelope_sha256=receipt['envelope_sha256'],
                               elf_sha256=sha(producer / 'probe.elf'),
                               envelope_sha256=sha(envelope),
                               control='Old-bound relink/repack commands in parent results')
                (producer / 'evidence.json').write_text(json.dumps(receipt, indent=2) + '\n')
            dest = out / name
            dest.mkdir()
            row['elf_sha256'] = sha(producer / 'probe.elf')
            row['envelope_sha256'] = sha(producer / 'native-c.bin')
            encoded = (producer / 'native-c.bin').read_bytes()
            if encoded[:8] != b'AENATC01' or encoded[40:] != (producer / 'probe.elf').read_bytes():
                raise RuntimeError('clock envelope does not contain the recorded ELF')
            args = ['zig', 'build', '-Dsmp=false', '-Dnative-memory=true',
                    '-Dnative-threads=true', '-Dnative-thread-pair=true',
                    '-Dnative-clock=' + str(clock).lower(),
                    '-Dnative-c-image=' + str(producer / 'native-c.bin'),
                    '-p', str(dest), '--cache-dir', str(ROOT / '.zig-cache'),
                    '--global-cache-dir', str(ROOT / '.zig-cache/global')]
            if mutant:
                args += ['-D' + mutant + '=true']
            command(args, dest / 'build.log')
            run(dest / 'aether.iso', expected_panic=b'native C profile rejected' if status else None)
            serial = (dest / 'native-serial.log').read_text()
            check_terminals(serial, [(1, status), (1, status)])
            if clock and not status:
                row.update(check_clock_trace(serial))
            row.update(status='pass', end_utc=now())
        if any(sha(ROOT / p) != h for p, h in record['sources'].items()):
            raise RuntimeError('sources changed during qualified run')
        record['status'] = 'pass'
    except BaseException as error:
        record.update(status='failed', error=str(error))
        if record['cases'] and record['cases'][-1]['status'] == 'running':
            record['cases'][-1].update(status='failed', error=str(error), end_utc=now())
        raise
    finally:
        (out / 'results.json').write_text(json.dumps(record, indent=2) + '\n')
        compact_run(out, record)
    print('[PASS] Libc clock cases:', len(record['cases']))
    return out


if __name__ == '__main__':
    parser = Parser(description=__doc__)
    parser.add_argument('--libc-build', required=True)
    parser.add_argument('--tools-lock', required=True)
    parser.add_argument('--long-waits', action='store_true', help='Focused opt-in two-second sleeps/conditions with bounded native parks; no SDK adoption')
    parser.add_argument('--case', choices=['real', 'repeat', 'early', 'disabled', 'legacy', 'old-bound'], help='Run one available case; reports only that selected coverage')
    parser.add_argument('--version', action='version', version='aether-libc-clock-smoke 1')
    args = parser.parse_args()
    try:
        suite(args.libc_build, args.tools_lock, args.long_waits, args.case)
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as error:
        parser.exit(1, f'[FAIL] {error}\n')
