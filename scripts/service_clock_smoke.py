# SPDX-License-Identifier: BSD-2-Clause
"""Qualify private 82-worker clock/wait capacity with compact result retention."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import tempfile
from deps import ROOT
from evidence import compact_run
from memory_probe import build
from native_smoke import run
from regression import Parser

SUPERVISOR = ROOT / 'docs/evidence/native-service-workers-2026-10-04/thread-supervisor.rs'


def check_trace(serial, mode, stopped=False, legacy=False):
    if 'NATIVE supervisor result=100 reclaimed=3\n' not in serial:
        raise RuntimeError('missing supervisor cleanup/replacement')
    rows = re.findall(r'^NATIVE MEMORY admitted slot=([012]) generation=([0-9]+) used=([0-9]+) remaining=([0-9]+)$', serial, re.MULTILINE)
    first = [r for r in rows if r[:2] == ('0', '1')]
    fresh = [r for r in rows if r[:2] == ('0', '2')]
    if len(first) != 1 or len(fresh) != 1 or first[0][2:] != fresh[0][2:]:
        raise RuntimeError('changed replacement backing accounting')
    if any(int(used) + int(free) != (8192 if slot == '0' else 128)
           for slot, _, used, free in rows):
        raise RuntimeError('widened or missing owner quota')
    if legacy:
        return {}
    parks = re.findall(r'^NATIVE CLOCK park task=([0-9]+) start=([0-9]+) deadline=([0-9]+)$', serial, re.MULTILINE)
    if len(parks) != 166 or sum(owner == '0' for owner, _, _ in parks) != 164:
        raise RuntimeError('missing full-owner deadline registrations')
    if any(not 0 < int(d) - int(s) <= 1000000000 for _, s, d in parks):
        raise RuntimeError('invalid worker deadline admission')
    for owner in ('0', '1'):
        deadlines = [d for o, _, d in parks if o == owner]
        groups = {d: deadlines.count(d) for d in set(deadlines)}
        expected = [82, 82] if owner == '0' else [2]
        if sorted(groups.values()) != expected:
            raise RuntimeError('cohort deadline changed or replacement reused deadline')
    timeouts = re.findall(r'^NATIVE CLOCK timeout task=([0-9]+) now=([0-9]+) elapsed=([0-9]+)$', serial, re.MULTILINE)
    expected_timeouts = 0 if mode == 1 else 84 if stopped else 166
    if len(timeouts) != expected_timeouts:
        raise RuntimeError('missing or excess timeout settlements')
    if any(not 0 < int(e) <= int(n) for _, n, e in timeouts):
        raise RuntimeError('invalid timeout observation')
    expected_service = 0 if mode == 1 else 82 if stopped else 164
    expected_peer = 0 if mode == 1 else 2
    if (sum(o == '0' for o, _, _ in timeouts) != expected_service or
            sum(o == '1' for o, _, _ in timeouts) != expected_peer):
        raise RuntimeError('missing owner-specific timeout settlements')
    current_deadline = {}
    for line in serial.splitlines():
        park = re.fullmatch(r'NATIVE CLOCK park task=([0-9]+) start=([0-9]+) deadline=([0-9]+)', line)
        timeout = re.fullmatch(r'NATIVE CLOCK timeout task=([0-9]+) now=([0-9]+) elapsed=([0-9]+)', line)
        if park:
            current_deadline[park[1]] = int(park[3])
        if timeout:
            deadline = current_deadline.get(timeout[1])
            if deadline is None or not 0 <= int(timeout[2]) - deadline <= 1000000000:
                raise RuntimeError('early, late or unregistered worker timeout')
    costs = re.findall(r'^NATIVE CLOCK workers scans=([0-9]+) max_contexts=([0-9]+) max_ns=([0-9]+) valid=([01])$', serial, re.MULTILINE)
    if len(costs) != 1:
        raise RuntimeError('missing unique worker scan measurement')
    scans, contexts, cost, valid = map(int, costs[0])
    if not scans or not 83 <= contexts <= 92 or not 0 <= cost < 1000000000 or valid != 1:
        raise RuntimeError('worker scan source/count/budget rejection')
    return {'parks': len(parks), 'timeouts': len(timeouts),
            'scan_ticks': scans, 'max_contexts': contexts, 'max_scan_ns': cost}


def suite(libc_build, tools_lock):
    out = Path(tempfile.mkdtemp(prefix='thread-suite-service-clock-', dir=ROOT / 'zig-out'))
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    now = lambda: datetime.now(timezone.utc).isoformat()
    files = [ROOT / 'build.zig', SUPERVISOR,
             ROOT / 'docs/evidence/native-service-workers-2026-10-04/park-probe.c',
             ROOT / 'docs/evidence/native-service-workers-2026-10-04/probe.c']
    for parent in ('kernel', 'user/native-memory', 'scripts'):
        files += [p for p in (ROOT / parent).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name != '.DS_Store']
    record = {'status': 'incomplete', 'scope': 'BSP bare native 82/two-worker timing; not engine or SDK adoption',
              'sources': {str(p.relative_to(ROOT)): sha(p) for p in files},
              'commands': [], 'cases': []}

    def command(argv, log):
        row = {'argv': [str(a) for a in argv], 'status': 'running', 'start_utc': now()}
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

    print('[RUNNING] Service clock results:', out, file=sys.stderr, flush=True)
    try:
        private = out / 'private'
        build(libc_build, tools_lock, private, None)
        recipe = json.loads((private / 'evidence.json').read_text())['commands']
        cc = recipe[0][:recipe[0].index('-c')]
        resource = Path(cc[0]).parent.parent / 'lib/clang/21/include'
        cc += ['-idirafter', str(resource)]
        record['compiler_headers'] = {str(p.relative_to(resource)): sha(p)
                                      for p in resource.rglob('*') if p.is_file()}
        link = recipe[-1]
        for name, mode, cflags, flags, expected, legacy in (
                ('timeout', 0, [], [], None, False),
                ('repeat', 0, [], [], None, False),
                ('wake', 1, [], [], None, False),
                ('requeue', 2, [], [], None, False),
                ('stop', 0, ['-DSTOP_WORKERS'], [], None, False),
                ('early', 0, [], ['-Dnative-clock-skip-wait=true'], 388, False),
                ('unlimited-wake', 1, [], ['-Dnative-wake-unlimited=true'], 394, False),
                ('skip-requeue', 2, [], ['-Dnative-requeue-skip-move=true'], 392, False),
                ('skip-pin', 0, [], ['-Dnative-wait-skip-pin=true'], 392, False),
                ('legacy-capacity', 0, [], ['-Dnative-clock=false'], None, True)):
            dest = out / name
            dest.mkdir()
            row = {'name': name, 'status': 'running', 'start_utc': now(), 'expected_detail': expected}
            record['cases'].append(row)
            source = ROOT / 'user/native-memory/service_clock.c'
            if legacy:
                source = ROOT / 'docs/evidence/native-service-workers-2026-10-04/park-probe.c'
                # Frozen old client, with its separate main/yield accounting.
                driver = (ROOT / 'docs/evidence/native-service-workers-2026-10-04/probe.c').read_text()
                hook = '    CHECK(tls_marker == 17, 224);'
                insert = ('    extern int thread_probe(unsigned long, unsigned long, unsigned *);\n'
                          '    unsigned extra = 0; int e = thread_probe(cap, stop, &extra);\n'
                          '    CHECK(e == 0, e); CHECK(write(1, &extra, 4) == 4, 242);\n')
                assert driver.count(hook) == 1
                driver = '#include <unistd.h>\n' + driver.replace(hook, insert + hook)
                (dest / 'driver.c').write_text(driver)
                command(cc + ['-Iuser/native-memory', '-c', dest / 'driver.c', '-o', dest / 'probe.o'], dest / 'driver.log')
                command(cc + ['-Iuser/native-memory', '-c', source, '-o', dest / 'worker.o'], dest / 'worker.log')
            else:
                command(cc + ['-DMODE=' + str(mode)] + cflags + ['-c', source, '-o', dest / 'probe.o'], dest / 'producer.log')
            argv = [str(dest / 'probe.o') if a == str(private / 'probe.o') else
                    str(dest / 'probe.elf') if a == str(private / 'probe.elf') else
                    '-Wl,-Map,' + str(dest / 'probe.map') if a.startswith('-Wl,-Map,') else a for a in link]
            if legacy:
                argv.insert(argv.index(str(private / 'adapter.o')), str(dest / 'worker.o'))
            command(argv, dest / 'link.log')
            rust = ['rustc', '+1.98.0', '--edition=2024', '--target=x86_64-unknown-none',
                    '-C', 'opt-level=2', '-C', 'panic=abort', '-C', 'relocation-model=static',
                    '-C', 'link-arg=-Tuser/protection/linker.ld', '-C', 'link-arg=--oformat=binary',
                    SUPERVISOR, '-o', dest / 'supervisor.raw']
            if name == 'stop': rust += ['--cfg', 'stop_live']
            command(rust, dest / 'supervisor.log')
            code = (dest / 'supervisor.raw').read_bytes()
            elf = (dest / 'probe.elf').read_bytes()
            if not 0 < len(code) <= 4096: raise RuntimeError('supervisor code budget')
            envelope = dest / 'native-c.bin'
            envelope.write_bytes(struct.pack('<8sII', b'AENSUP01', len(elf), len(code)) + os.urandom(32) + elf + code)
            row['elf_sha256'], row['envelope_sha256'] = sha(dest / 'probe.elf'), sha(envelope)
            options = ['-Dsmp=false', '-Dnative-memory=true', '-Dnative-memory-large=true',
                       '-Dnative-image-large=true', '-Dnative-backing=true', '-Dnative-service-memory=true',
                       '-Dnative-threads=true', '-Dnative-thread-pair=true', '-Dnative-thread-reuse=true',
                       '-Dnative-thread-origin=true', '-Dnative-service-workers=true']
            if not legacy: options += ['-Dnative-clock=true']
            command(['zig', 'build', '-p', dest, '--cache-dir', ROOT / '.zig-cache',
                     '--global-cache-dir', ROOT / '.zig-cache/global', '-Dnative-c-image=' + str(envelope)] + options + flags, dest / 'build.log')
            context = () if expected is None else (f'NATIVE terminal slot=0 generation=1 kind=1 detail={expected}'.encode(), b'NATIVE supervisor result=401 reclaimed=0')
            run(dest / 'aether.iso', marker=b'AETHER NATIVE SUPERVISION PASS',
                expected_panic=b'native C profile rejected' if expected else None, panic_context=context)
            serial = (dest / 'native-serial.log').read_text()
            if expected is None: row.update(check_trace(serial, mode, name == 'stop', legacy))
            row.update(status='pass', end_utc=now())
        if any(sha(ROOT / n) != h for n, h in record['sources'].items()):
            raise RuntimeError('sources changed during qualification')
        record['status'] = 'pass'
    except BaseException as error:
        record.update(status='failed', error=str(error))
        raise
    finally:
        (out / 'results.json').write_text(json.dumps(record, indent=2) + '\n')
        compact_run(out, record)
    print('[PASS] Service clock cases:', len(record['cases']))
    return out


if __name__ == '__main__':
    parser = Parser(description=__doc__)
    parser.add_argument('--libc-build', required=True)
    parser.add_argument('--tools-lock', required=True)
    parser.add_argument('--version', action='version', version='aether-service-clock-smoke 1')
    args = parser.parse_args()
    try: suite(args.libc_build, args.tools_lock)
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        parser.exit(1, f'[FAIL] {error}\n')
