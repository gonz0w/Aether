# SPDX-License-Identifier: BSD-2-Clause
"""Private actual-musl 82-worker conditions/sleep; compact retention only."""
from collections import Counter
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

INPUT = ROOT / 'docs/evidence/native-service-origin-2026-10-05'
PINS = {'probe.c': '86be2d01be01a1e008fcb9606b1a474d4ec151c54290ff34bbe821fd48794bb4',
        'supervisor.rs': 'e6fa776623ed82eaff9a031d357227c5b86eea8a80c61b2e351bd80fe57e5d12'}


def adapt(source):
    """Exact insertion points preserve the pinned real pthread adapter."""
    changes = [
        ('long aether_wait_syscall(', '#include "service_time.inc"\nlong aether_wait_syscall('),
        ('    if (n == SYS_rt_sigprocmask) {',
         '    if ((n == SYS_nanosleep && !c && !d && !e && !f) ||\n'
         '        (n == SYS_clock_nanosleep && !e && !f))\n'
         '        return aether_sleep_syscall(n, a, b, c, d);\n'
         '    if (n == SYS_rt_sigprocmask) {'),
        ('            ++waits_entered;\n',
         '            if (a == (long)&timed_mutex._m_lock) ++timed_relocks;\n'
         '            ++waits_entered;\n'),
        ('    if (pthread_getspecific(deleted_key))\n',
         '    unsigned timed_result = service_time_worker(i);\n'
         '    if (timed_result) startups[i].error = timed_result;\n'
         '    if (pthread_getspecific(deleted_key))\n'),
        ('    unsigned map_pages = 0;\n',
         '    unsigned init_result = service_time_initialize();\n'
         '    CHECK(!init_result, init_result);\n    unsigned map_pages = 0;\n'),
        ('    gate = 1;\n',
         '    long start = timed_now();\n    CHECK(start >= 0, 380);\n'
         '    timed_deadline = timed_at((unsigned long)start + 900000000);\n'
         '    gate = 1;\n'),
        ('          337);\n#ifdef SERVICE_REAPER',
         '          337);\n    unsigned parent_result = service_time_parent();\n'
         '    CHECK(!parent_result, parent_result);\n#ifdef SERVICE_REAPER'),
        ('        CHECK(!pthread_join(startups[i].thread, &value) && !value &&\n'
         '                  !startups[i].error,\n              338);',
         '        CHECK(!pthread_join(startups[i].thread, &value), 338);\n'
         '        CHECK(!value && !startups[i].error,\n'
         '              value ? (unsigned long)value : startups[i].error);'),
        ('    CHECK(!deleted_calls && pthread_getspecific(value_key)',
         '    unsigned cleanup_result = service_time_cleanup();\n'
         '    CHECK(!cleanup_result, cleanup_result);\n'
         '    CHECK(!deleted_calls && pthread_getspecific(value_key)')]
    stop = ('#ifdef STOP_LIVE\n'
            '    if (limit == 82 && memtrap(0x20005, 0, 0, 0, 0) == 1) {\n'
            '        CHECK(!memtrap(0x20004, 0, 0, 0, 0), 330);\n'
            '        for (;;)\n            yield_primary();\n    }\n#endif\n')
    changes.append((stop, ''))
    for old, new in changes:
        if source.count(old) != 1:
            raise RuntimeError('service timed insertion context changed: ' + old)
        source = source.replace(old, new)
    return source, [{'old': old, 'new': new} for old, new in changes]


def check_trace(serial, mode=0, stopped=False, legacy=False, openzfs=False, heap=False, long_waits=False):
    if 'NATIVE supervisor result=100 reclaimed=3\n' not in serial:
        raise RuntimeError('missing supervisor cleanup/replacement')
    rows = re.findall(r'^NATIVE MEMORY admitted slot=([012]) generation=([0-9]+) used=([0-9]+) remaining=([0-9]+)$', serial, re.MULTILINE)
    if [(s, g) for s, g, _, _ in rows] != [('0', '1'), ('1', '1'), ('0', '2')]:
        raise RuntimeError('missing exact owner generations')
    if rows[0][2:] != rows[2][2:] or any(int(u) + int(f) != (8192 if s == '0' else 128) for s, _, u, f in rows):
        raise RuntimeError('changed owner backing accounting')
    terminals = re.findall(r'^NATIVE terminal slot=([01]) generation=([12]) kind=([13]) detail=([0-9]+)', serial, re.MULTILINE)
    expected_terminals = {('1', '1'), ('0', '2')} if stopped else {('0', '1'), ('1', '1'), ('0', '2')}
    if len(terminals) != len(expected_terminals) or {(s, g) for s, g, _, _ in terminals} != expected_terminals:
        raise RuntimeError('missing exact terminal records or unexpected stopped terminal')
    # Explicit stop has no ordinary terminal line. The pinned Rust supervisor
    # observes readiness, stop144/kind3, idempotence and reclaim before result100.
    observations = []
    for s, g, kind, detail in terminals:
        value = int(detail)
        low = value & 0xffffff if heap else value
        if kind != '1' or low & ~0xffff != 0x100000 or value & 255 != (66 if s == '0' else 34) or (value >> 8) & 255 > 16:
            raise RuntimeError('changed actual pthread mapping/allocator accounting')
        if heap:
            before, peak, held = [(value >> shift) & 8191 for shift in (24, 37, 50)]
            pages = 1024 if s == '0' else 4
            if not (value < 1 << 63 and 0 <= peak <= held < before <= (8191 if s == '0' else 128)
                    and pages <= before - held <= pages + 16):
                raise RuntimeError('invalid native heap backing observations')
            observations.append({'slot': int(s), 'generation': int(g), 'free_before_pages': before,
                                 'free_peak_pages': peak, 'free_held_pages': held,
                                 'probe_peak_pages': before - peak})
    if legacy:
        return {}
    parks = re.findall(r'^NATIVE CLOCK park task=([0-9]+) start=([0-9]+) deadline=([0-9]+)$', serial, re.MULTILINE)
    timeouts = re.findall(r'^NATIVE CLOCK timeout task=([0-9]+) now=([0-9]+) elapsed=([0-9]+)$', serial, re.MULTILINE)
    if {o for o, _, _ in parks} != {'0', '1'} or {o for o, _, _ in timeouts} != {'0', '1'}:
        raise RuntimeError('missing or foreign clock owner')
    for owner, workers in (('0', 164), ('1', 2)):
        active = workers - (82 if stopped and owner == '0' else 0)
        retries = active if mode == 1 else 0
        values = [int(d) for o, _, d in parks if o == owner]
        # An absolute sleep may already be due when musl is descheduled before
        # entering the backend. Require full condition cohorts and substantial
        # real sleep admission, rather than forbid that legitimate expiration.
        extra = active * 3 + 3 if openzfs else 0
        lower = workers + active // 2 + retries
        upper = workers + active * 2 + retries + extra
        stopped_workers = workers - active
        if long_waits:
            lower = workers + active * 2 + retries + stopped_workers
            upper = workers + active * 3 + retries + stopped_workers * 2 + 3
        if not lower <= len(values) <= upper:
            raise RuntimeError('missing or excessive owner-specific condition/sleep parks')
        sizes = sorted(Counter(values).values(), reverse=True)
        # Owner0 has two distinct condition cohorts, including stopped generation.
        expected = sorted(([82, 82 + (82 if mode == 1 else 0)] if stopped else
                           [82 * (1 + (mode == 1))] * 2) if owner == '0' else
                          [2 * (1 + (mode == 1))], reverse=True)
        if sizes[:len(expected)] != expected:
            raise RuntimeError('changed cohort deadline or missing original-deadline retries')
        count = active * (1 if mode == 2 else 2) + extra
        if long_waits:
            count = workers + active * 3 + stopped_workers * 2 + 3
        # Wake/requeue scans also settle expired records without the periodic
        # timeout diagnostic. Actual libc witnesses assert every result/time.
        if not 1 <= sum(o == owner for o, _, _ in timeouts) <= count:
            raise RuntimeError('missing or excess owner-specific periodic settlements')
    if any(not 0 < int(d) - int(s) <= 1000000000 for _, s, d in parks):
        raise RuntimeError('invalid deadline admission')
    seen = {'0': [], '1': []}
    for line in serial.splitlines():
        p = re.fullmatch(r'NATIVE CLOCK park task=([0-9]+) start=([0-9]+) deadline=([0-9]+)', line)
        t = re.fullmatch(r'NATIVE CLOCK timeout task=([0-9]+) now=([0-9]+) elapsed=([0-9]+)', line)
        if p:
            seen[p[1]].append(int(p[3]))
        if t and (not 0 < int(t[3]) <= int(t[2]) or
                  not any(0 <= int(t[2]) - d <= 1000000000 for d in seen[t[1]])):
            raise RuntimeError('early, late or unregistered settlement')
    costs = re.findall(r'^NATIVE CLOCK workers scans=([0-9]+) max_contexts=([0-9]+) max_ns=([0-9]+) valid=([01])$', serial, re.MULTILINE)
    if len(costs) != 1:
        raise RuntimeError('missing unique scan observation')
    scans, contexts, cost, valid = map(int, costs[0])
    if not scans or not 83 <= contexts <= 92 or not 0 <= cost < 1000000000 or valid != 1:
        raise RuntimeError('invalid scan source/budget')
    result = {'parks': len(parks), 'timeouts': len(timeouts), 'max_contexts': contexts,
              'max_scan_ns': cost, 'scan_ticks': scans}
    if heap:
        result['heap_observations'] = observations
    return result


def adapt_heap(source, supervisor):
    """Private diagnostics only; preserve the existing low24-bit oracle."""
    changes = [
        ('static unsigned long thread_cap, memory_cap;',
         'static unsigned long thread_cap, memory_cap;\n'
         'static unsigned long heap_observations[3];\n'
         'unsigned aether_umem_begin(unsigned, long (*)(void), unsigned long[3]);\n'
         'unsigned aether_umem_end(long (*)(void));\n'
         'static long heap_available(void) { return memtrap(0x22000, memory_cap, 0, 0, 0); }'),
        ('    free(heap);\n', '    free(heap);\n'
         '    unsigned heap_result = aether_umem_begin(limit, heap_available, heap_observations);\n'
         '    CHECK(!heap_result, heap_result);\n'),
        ('    unsigned cleanup_result = service_time_cleanup();',
         '    unsigned heap_cleanup = aether_umem_end(heap_available);\n'
         '    CHECK(!heap_cleanup, heap_cleanup);\n'
         '    unsigned cleanup_result = service_time_cleanup();'),
        ('return 0x100000 | map_pages | ((unsigned)(initial - final) << 8);',
         'memtrap(0x10000 + 231, 0x100000 | map_pages | ((unsigned)(initial - final) << 8) |\n'
         '           (heap_observations[0] << 24) | (heap_observations[1] << 37) |\n'
         '           (heap_observations[2] << 50), 0, 0, 0);\n'
         '    __builtin_unreachable();')]
    for old, new in changes:
        if source.count(old) != 1:
            raise RuntimeError('heap fixture insertion context changed: ' + old)
        source = source.replace(old, new)
    old = 'check(state.1 == 1 && detail & !0xffff == 0x100000);'
    new = '''check(state.1 == 1 && detail & 0xff0000 == 0x100000);
                let before = (detail >> 24) & 8191;
                let peak = (detail >> 37) & 8191;
                let held = (detail >> 50) & 8191;
                let service = detail & 255 == 66;
                let pages = if service {1024} else {4};
                check(peak <= held && held < before && before <= if service {8191} else {128});
                check(before - held >= pages && before - held <= pages + 16);'''
    if supervisor.count(old) != 1:
        raise RuntimeError('heap supervisor insertion context changed')
    supervisor = supervisor.replace(old, new)
    return source, supervisor, [{'old': old, 'new': new} for old, new in changes] + [{'old': old, 'new': new}]


def check_heap_object(disassembly):
    """Pinned optimized probe must retain its real denied allocation calls."""
    calls = Counter(re.findall(r'R_X86_64_PLT32\s+(\w+)-', disassembly))
    required = {'malloc': 3, 'calloc': 2, 'posix_memalign': 2, 'free': 2}
    if any(calls[name] < count for name, count in required.items()) or disassembly.count('$0x4000000') < 3:
        raise RuntimeError('optimized heap probe lost required allocation calls')
    return dict(calls)


def suite(libc_build, tools_lock, openzfs=False, entropy=False, heap=False, allocation=False, resources=False, arc=False, long_waits=False, case=None):
    resources = resources or arc
    allocation = allocation or resources
    heap = heap or allocation
    entropy = entropy or heap
    openzfs = openzfs or entropy
    if long_waits and openzfs:
        raise ValueError('long-wait service profile is not an OpenZFS engine/caller qualification')
    if long_waits and case not in (None, 'timeout', 'spurious', 'stop', 'old-bound'):
        raise ValueError('case unavailable in selected service clock profile: ' + case)
    out = Path(tempfile.mkdtemp(prefix='thread-suite-service-libc-clock-', dir=ROOT / 'zig-out'))
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    now = lambda: datetime.now(timezone.utc).isoformat()
    files = [ROOT / 'build.zig', *[INPUT / name for name in PINS]]
    for parent in ('kernel', 'user/native-memory', 'scripts'):
        files += [p for p in (ROOT / parent).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name != '.DS_Store']
    if openzfs:
        files += list((ROOT / 'user/storage/openzfs-elapsed').glob('*'))
    record = {'status': 'incomplete', 'scope': 'BSP actual musl 82/two-worker timing; not engine or production SDK adoption',
              'sources': {str(p.relative_to(ROOT)): sha(p) for p in files}, 'commands': [], 'cases': []}
    record.update(long_waits=long_waits, selected_case=case)

    def command(argv, log):
        row = {'argv': [str(a) for a in argv], 'status': 'running', 'start_utc': now()}
        record['commands'].append(row)
        try:
            with log.open('wb') as stream:
                result = subprocess.run(row['argv'], cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, timeout=180)
            row['exit_code'] = result.returncode
            result.check_returncode()
            row['status'] = 'pass'
        except BaseException as error:
            row.update(status='failed', error=str(error))
            raise
        finally:
            row['end_utc'] = now()

    print('[RUNNING] Service libc clock results:', out, file=sys.stderr, flush=True)
    try:
        if any(sha(INPUT / n) != h for n, h in PINS.items()):
            raise RuntimeError('pinned pthread input changed')
        private = out / 'private'
        build(libc_build, tools_lock, private, 'LIFE_REAL_TIME', pthread_lifecycle=True, pthread_keys=True, long_waits=long_waits)
        recipe = json.loads((private / 'evidence.json').read_text())['commands']
        cc = recipe[0][:recipe[0].index('-c')] + ['-Iuser/native-memory']
        link = recipe[-1]
        port = None
        if openzfs:
            from openzfs_elapsed import prepare, declarations, adapt_fixture
            port = prepare(out / 'openzfs', command, entropy, allocation, resources, arc)
            (port / 'zfs-declarations.h').write_text(declarations(entropy))
            inc, changes = adapt_fixture((ROOT / 'user/native-memory/service_time.inc').read_text())
            if entropy:
                from openzfs_elapsed import adapt_entropy_fixture
                inc, extra_changes = adapt_entropy_fixture(inc)
                changes += extra_changes
                (port / 'entropy-bridge.inc').write_bytes((ROOT / 'user/storage/openzfs-elapsed/entropy-bridge.inc').read_bytes())
            (port / 'service_time.inc').write_text(inc)
            (port / 'zfs-bridge.inc').write_bytes((ROOT / 'user/storage/openzfs-elapsed/zfs-bridge.inc').read_bytes())
            cc.insert(cc.index('-Iuser/native-memory'), '-I' + str(port))
            record.update(scope='Actual OpenZFS elapsed callers/82-worker musl; full engine relink only, not entry or maintained SDK',
                          openzfs_fixture_transforms=changes, openzfs_header_sha256=sha(port / 'zfs-declarations.h'))
        # Compile the original untimed backend for legacy regressions instead
        # of accidentally falling back to the guarded SDK syscall route.
        patched = private / 'musl-headers/src/thread/__timedwait.c'
        patch = json.loads((private / 'timedwait-patch.json').read_text())
        original = patched.read_text().replace(patch['new'], patch['old'])
        if hashlib.sha256(original.encode()).hexdigest() != patch['before_sha256']:
            raise RuntimeError('legacy timedwait restoration mismatch')
        legacy_source = private / 'legacy-timedwait.c'
        legacy_source.write_text(original)
        (private / 'legacy-timedwait.json').write_text(json.dumps({
            'source_sha256': sha(legacy_source), 'upstream': 'musl1.2.6/src/thread/__timedwait.c'}) + '\n')
        legacy_recipe = next(c for c in recipe if str(private / 'musl_timedwait.o') in c)
        legacy_cc = legacy_recipe[:legacy_recipe.index('-c')]
        command(legacy_cc + ['-c', legacy_source, '-o', private / 'legacy-timedwait.o'], private / 'legacy-timedwait.log')
        derived, changes = adapt((INPUT / 'probe.c').read_text())
        if openzfs:
            from openzfs_elapsed import adapt_exit
            derived, exit_change = adapt_exit(derived)
            changes.append(exit_change)
        record['transforms'] = changes
        supervisor = INPUT / 'supervisor.rs'
        heap_objects = {}
        if heap:
            from openzfs_elapsed import CURRENT, route
            derived, rust_source, heap_changes = adapt_heap(derived, supervisor.read_text())
            record['transforms'] += heap_changes
            supervisor = port / 'heap-supervisor.rs'
            supervisor.write_text(rust_source)
            selected = json.loads((CURRENT / 'build-attempt-1/results.json').read_text())
            original = next(c['argv'] for c in selected['commands'] if c['name'] == 'kernel.c-selected')
            prefix = [route(a) for a in original[:original.index('-c')]] + ['-Wall', '-Wextra', '-Werror']
            variants = [('normal', []), ('leak', ['-DHEAP_LEAK'])]
            if allocation:
                from openzfs_elapsed import function
                prefix.insert(1, '-I' + str(port / 'allocation'))
                prefix += ['-DALLOC_PORT']
                old_ctor = port / 'old-constructor'
                old_ctor.mkdir()
                patched = (port / 'allocation/umem.h').read_text()
                upstream_header = (CURRENT / 'build-attempt-5/guarded-include/umem.h').read_text()
                patched = patched.replace(function(patched, 'umem_cache_alloc'), function(upstream_header, 'umem_cache_alloc'), 1)
                (old_ctor / 'umem.h').write_text(patched)
                variants += [('old-constructor', ['-I' + str(old_ctor)])]
                variants += [(name, ['-DALLOC_FAILURE=' + str(number)]) for number, name in enumerate(
                    ('alloc-nofail', 'alloc-zero', 'alloc-aligned', 'alloc-constructor', 'alloc-metadata', 'alloc-invalid'), 1)]
            for name, flags in variants:
                obj = port / ('heap-' + name + '.o')
                active_prefix = prefix.copy()
                if name == 'old-constructor':
                    active_prefix.insert(1, flags[0])
                    flags = []
                command(active_prefix + flags + ['-c', ROOT / 'user/storage/openzfs-elapsed/heap-probe.c', '-o', obj],
                        port / ('heap-' + name + '.log'))
                heap_objects[name] = obj
            inspection = port / 'heap-disassembly.log'
            command([Path(prefix[0]).parent / 'llvm-objdump', '-dr', heap_objects['normal']], inspection)
            disassembly = inspection.read_text()
            record['heap_disassembly_sha256'] = sha(inspection)
            record['heap_disassembly_bytes'] = inspection.stat().st_size
            # Keep a short call-site excerpt, never the full successful dump.
            inspection.write_text('\n'.join(l for l in disassembly.splitlines() if 'R_X86_64_PLT32' in l)[:4096] + '\n')
            record['heap_disassembly_retention'] = 'call-site excerpt only; full dump discarded'
            record['heap_call_sites'] = check_heap_object(disassembly)
            header = CURRENT / 'build-attempt-5/guarded-include/umem.h'
            upstream = CURRENT / 'baseline/source/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1/lib/libspl/include/umem.h'
            if sha(header) != sha(upstream):
                raise RuntimeError('selected umem header differs from upstream')
            record['heap_upstream_header_sha256'] = sha(header)
            record.update(heap_objects={n: sha(p) for n, p in heap_objects.items()},
                          heap_supervisor_sha256=sha(supervisor))
        resource_objects = {}
        if resources:
            resource_source = ROOT / 'user/storage/openzfs-elapsed/resources.c'
            original_resource = resource_source.read_text()
            variants = [('normal', original_resource),
                        ('resource-absent', original_resource.replace('getauxval(0xa000)', '0', 1)),
                        ('resource-future', original_resource.replace('getauxval(0xa000)', '(getauxval(0xa000) + 256)', 1)),
                        ('resource-foreign', original_resource.replace('getauxval(0xa000)', '(getauxval(0xa000) + 1)', 1)),
                        ('resource-free-as-total', original_resource.replace('return aether_zfs_observe(0);', 'return aether_zfs_observe(1);', 1))]
            for name, text in variants:
                source = port / ('resource-' + name + '.c')
                source.write_text(text)
                obj = port / ('resource-' + name + '.o')
                command(cc + ['-Wall', '-Wextra', '-Werror', '-c', source, '-o', obj], port / ('resource-' + name + '.log'))
                resource_objects[name] = obj
            old = '    unsigned heap_result = aether_umem_begin(limit, heap_available, heap_observations);'
            new = '    unsigned resource_result = resource_check(limit);\n    CHECK(!resource_result, resource_result);\n' + old
            if derived.count(old) != 1:
                raise RuntimeError('resource probe insertion context changed')
            helper = """
#include <resources.h>
static unsigned resource_check(unsigned workers) {
    uint64_t total = aether_zfs_granted_pages();
    CHECK(total == (workers == 82 ? 8192 : 128), 414);
    CHECK(aether_zfs_assigned_cpus() == 1, 414);
    uint64_t before = aether_zfs_free_pages();
    CHECK(before == (uint64_t)heap_available() && before < total, 414);
    void *p = mmap(NULL, 4096, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
    CHECK(p != MAP_FAILED, 414);
    CHECK(aether_zfs_granted_pages() == total && aether_zfs_free_pages()+1 == before, 414);
    CHECK(aether_zfs_assigned_cpus() == 1 && !munmap(p,4096), 414);
    CHECK(aether_zfs_free_pages() == before && aether_zfs_granted_pages() == total, 414);
    return 0;
}
"""
            marker = 'static long heap_available(void) { return memtrap(0x22000, memory_cap, 0, 0, 0); }'
            if derived.count(marker) != 1:
                raise RuntimeError('resource check declaration context changed')
            derived = derived.replace(marker, marker + helper, 1).replace(old, new, 1)
            cc.insert(1, '-I' + str(port / 'resources'))
            record['resource_objects'] = {n:sha(o) for n,o in resource_objects.items()}
            record['transforms'] += [{'old':marker, 'new':marker + helper}, {'old':old,'new':new}]
        arc_objects = {}
        if arc:
            original = next(c['argv'] for c in selected['commands'] if c['name'] == 'kernel.c-selected')
            prefix = [route(a) for a in original[:original.index('-c')]]
            prefix.insert(1, '-I' + str(port / 'resources'))
            prefix.insert(1, '-I' + str(port / 'allocation'))
            prefix += ['-Wall', '-Wextra', '-Werror', '-ffunction-sections', '-fdata-sections']
            adapter_source = port / 'resources/arc_os.c'
            from openzfs_elapsed import function
            old_adapter = CURRENT / 'baseline/source/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1/lib/libzpool/arc_os.c'
            old_text = old_adapter.read_text()
            old_text = old_text.replace(function(old_text, 'arc_all_memory'),
                                        function(adapter_source.read_text(), 'arc_all_memory'), 1)
            old_source = port / 'arc-old-pressure.c'
            old_source.write_text(old_text)
            page_source = old_adapter.parent.parent / 'libspl/page.c'
            page_object = port / 'arc-page.o'
            command(prefix + ['-c', page_source, '-o', page_object], port / 'arc-page.log')
            arc_objects['page'] = page_object
            for name, source in [('normal', adapter_source), ('old-pressure', old_source)]:
                obj = port / ('arc-' + name + '.o')
                command(prefix + ['-c', source, '-o', obj], port / ('arc-' + name + '.log'))
                arc_objects[name] = obj
            for name, flags in [('probe', []), ('arc-headroom', ['-DARC_BAD_HEADROOM'])]:
                obj = port / ('arc-' + name + '.o')
                command(prefix + flags + ['-c', ROOT / 'user/storage/openzfs-elapsed/arc-probe.c', '-o', obj],
                        port / ('arc-' + name + '.log'))
                arc_objects[name] = obj
            marker = 'static unsigned resource_check(unsigned workers) {'
            new = 'unsigned aether_arc_probe(void);\n' + marker
            derived = derived.replace(marker, new, 1)
            marker = '    unsigned resource_result = resource_check(limit);\n    CHECK(!resource_result, resource_result);'
            new = marker + '\n    unsigned arc_result = aether_arc_probe();\n    CHECK(!arc_result, arc_result);'
            if derived.count(marker) != 1:
                raise RuntimeError('ARC probe insertion context changed')
            derived = derived.replace(marker, new, 1)
            record['arc_objects'] = {n:sha(o) for n,o in arc_objects.items()}
            record['transforms'] += [{'old':marker,'new':new}]
        cases = [
                ('timeout', 0, [], [], None, False),
                ('repeat', 0, [], [], None, False),
                ('spurious', 1, [], [], None, False),
                ('broadcast', 2, [], [], None, False),
                ('stop', 0, ['-DSTOP_LIVE'], [], None, False),
                ('early', 0, [], ['-Dnative-clock-skip-wait=true'], 125 if openzfs else 381, False),
                ('disabled', 0, [], [], 380, False),
                ('legacy-joinable', 0, [], [], None, True),
                ('legacy-reaper', 0, ['-DSERVICE_REAPER', '-DSERVICE_DETACHED'], [], None, True)]
        if openzfs:
            cases.append(('old-domain', 0, [], [], 125, False))
        if entropy:
            record['scope'] += '; actual bounded native entropy binding'
            cases += [('entropy-absent', 0, [], [], 125, False),
                      ('entropy-future', 0, [], [], 125, False),
                      ('entropy-closed', 0, ['-DENTROPY_CLOSED'], [], 125, False),
                      ('entropy-quota', 0, [], ['-Dnative-entropy-skip-quota=true'], 395, False)]
        if heap:
            record['scope'] += '; unchanged libspl malloc fallback/granted backing observations'
            cases.append(('heap-leak', 0, [], [], 399, False))
        if allocation:
            record['scope'] += '; bounded NOFAIL and default constructor cleanup; every selected header consumer rebuilt'
            cases += [('old-constructor', 0, [], [], 410, False)]
            cases += [(name, 0, [], [], 125, False) for name in (
                'alloc-nofail', 'alloc-zero', 'alloc-aligned', 'alloc-constructor', 'alloc-metadata', 'alloc-invalid')]
        if resources:
            record['scope'] += '; checked granted backing and one assigned core; not host physical resources'
            cases += [('resource-absent', 0, [], [], 125, False), ('resource-future', 0, [], [], 125, False),
                      ('resource-free-as-total', 0, [], [], 414, False), ('resource-foreign', 0, [], [], 125, False)]
        if arc:
            cases += [('arc-headroom', 0, [], [], 125, False), ('old-pressure', 0, [], [], 415, False)]
            record['scope'] += '; actual ARC adapter pressure, fixture stats only; no engine growth/reclaim'
        old_clock = None
        if long_waits:
            cases = [row for row in cases if row[0] in ('timeout', 'spurious', 'stop')]
            cases += [('old-bound', 0, [], [], 384, False)]
            old_clock = private / 'short-real-time.o'
            original = next(c for c in recipe if c[-1] == str(private / 'real_time.o'))
            original = [a for a in original if a != '-DAETHER_LONG_WAITS']
            original[-1] = str(old_clock)
            command(original, private / 'short-real-time.log')
            record['scope'] += '; two-second per-worker sleep and stop after first-chunk expiry; shared conditions stay900ms'
        if case is not None:
            cases = [row for row in cases if row[0] == case]
            if not cases:
                raise ValueError('case unavailable in selected service clock profile: ' + case)
        for name, mode, cflags, flags, expected, legacy in cases:
            dest = out / name
            dest.mkdir()
            row = {'name': name, 'status': 'running', 'start_utc': now(), 'expected_detail': expected}
            record['cases'].append(row)
            source = dest / 'probe.c'
            source.write_text((INPUT / 'probe.c').read_text() if legacy else derived)
            row['derived_sha256'] = sha(source)
            extra = [] if legacy else ['-DTIME_MODE=' + str(mode)]
            command(cc + extra + cflags + ['-c', source, '-o', dest / 'probe.o'], dest / 'producer.log')
            argv = [str(dest / 'probe.o') if a == str(private / 'probe.o') else
                    str(dest / 'probe.elf') if a == str(private / 'probe.elf') else
                    '-Wl,-Map,' + str(dest / 'probe.map') if a.startswith('-Wl,-Map,') else a for a in link]
            if legacy:
                argv.remove(str(private / 'real_time.o'))
                argv[argv.index(str(private / 'musl_timedwait.o'))] = str(private / 'legacy-timedwait.o')
            elif port:
                kernel = 'kernel.c-old-native.o' if name == 'old-domain' else 'kernel.c-native.o'
                if name == 'entropy-future':
                    kernel = 'kernel.c-future-native.o'
                argv += ['-Wl,--gc-sections', str(port / kernel), str(port / 'thread_pool.c-native.o')]
                if resources:
                    argv += [str(resource_objects.get(name, resource_objects['normal']))]
                if arc:
                    argv += [str(arc_objects['old-pressure' if name == 'old-pressure' else 'normal']),
                             str(arc_objects['arc-headroom' if name == 'arc-headroom' else 'probe'])]
                    if name == 'old-pressure':
                        argv += [str(arc_objects['page'])]
                if heap:
                    object_name = 'leak' if name == 'heap-leak' else name if name in heap_objects else 'normal'
                    argv += [str(heap_objects[object_name])]
            if name == 'old-bound':
                argv[argv.index(str(private / 'real_time.o'))] = str(old_clock)
            command(argv, dest / 'link.log')
            rust = ['rustc', '+1.98.0', '--edition=2024', '--target=x86_64-unknown-none',
                    '-C', 'opt-level=2', '-C', 'panic=abort', '-C', 'relocation-model=static',
                    '-C', 'link-arg=-Tuser/protection/linker.ld', '-C', 'link-arg=--oformat=binary',
                    INPUT / 'supervisor.rs' if legacy else supervisor, '-o', dest / 'supervisor.raw']
            if name == 'stop':
                rust += ['--cfg', 'stop_live']
            command(rust, dest / 'supervisor.log')
            code = (dest / 'supervisor.raw').read_bytes()
            elf = (dest / 'probe.elf').read_bytes()
            if not 0 < len(code) <= 4096:
                raise RuntimeError('supervisor code budget')
            envelope = dest / 'native-c.bin'
            envelope.write_bytes(struct.pack('<8sII', b'AENSUP01', len(elf), len(code)) + os.urandom(32) + elf + code)
            row['elf_sha256'], row['envelope_sha256'] = sha(dest / 'probe.elf'), sha(envelope)
            options = ['-Dsmp=false', '-Dnative-memory=true', '-Dnative-memory-large=true',
                       '-Dnative-image-large=true', '-Dnative-backing=true', '-Dnative-service-memory=true',
                       '-Dnative-threads=true', '-Dnative-thread-pair=true', '-Dnative-thread-reuse=true',
                       '-Dnative-thread-origin=true', '-Dnative-service-workers=true',
                       '-Dnative-clock=' + str(not legacy and name != 'disabled').lower()]
            if entropy and not legacy and name != 'entropy-absent':
                options += ['-Dnative-entropy=true']
            command(['zig', 'build', '-p', dest, '--cache-dir', ROOT / '.zig-cache',
                     '--global-cache-dir', ROOT / '.zig-cache/global', '-Dnative-c-image=' + str(envelope)] + options + flags, dest / 'build.log')
            context = () if expected is None else (f'NATIVE terminal slot=0 generation=1 kind=1 detail={expected}'.encode(), b'NATIVE supervisor result=401 reclaimed=0')
            run(dest / 'aether.iso', marker=b'AETHER NATIVE SUPERVISION PASS',
                expected_panic=b'native C profile rejected' if expected else None, panic_context=context,
                entropy=entropy and not legacy and name != 'entropy-absent')
            serial = (dest / 'native-serial.log').read_text()
            if expected is None:
                row.update(check_trace(serial, mode, name == 'stop', legacy, openzfs, heap and not legacy, long_waits))
            row.update(status='pass', end_utc=now())
        if any(sha(ROOT / n) != h for n, h in record['sources'].items()):
            raise RuntimeError('sources changed during qualification')
        record['status'] = 'pass'
    except BaseException as error:
        record.update(status='failed', error=str(error))
        if record['cases'] and record['cases'][-1]['status'] == 'running':
            record['cases'][-1].update(status='failed', error=str(error), end_utc=now())
        raise
    finally:
        (out / 'results.json').write_text(json.dumps(record, indent=2) + '\n')
        compact_run(out, record)
    print('[PASS] Service libc clock cases:', len(record['cases']))
    return out


if __name__ == '__main__':
    parser = Parser(description=__doc__)
    parser.add_argument('--libc-build', required=True)
    parser.add_argument('--tools-lock', required=True)
    parser.add_argument('--openzfs', action='store_true', help='Qualify selected actual OpenZFS elapsed callers; no engine entry')
    parser.add_argument('--openzfs-entropy', action='store_true', help='Also bind actual OpenZFS entropy callers to the bounded grant')
    parser.add_argument('--openzfs-heap', action='store_true', help='Also measure unchanged actual libspl malloc allocation under granted backing')
    parser.add_argument('--openzfs-alloc', action='store_true', help='Also port bounded allocation failure and rebuild all selected header consumers')
    parser.add_argument('--openzfs-resources', action='store_true', help='Also bind granted backing and one assigned CPU; no engine entry')
    parser.add_argument('--openzfs-arc', action='store_true', help='Also bind actual ARC pressure to granted backing; no engine entry')
    parser.add_argument('--long-waits', action='store_true', help='Focused82/two-worker segmented long-sleep/stop profile; incompatible with OpenZFS modes')
    parser.add_argument('--case', help='Run one named case available in the selected profile; only that case is reported')
    parser.add_argument('--version', action='version', version='aether-service-libc-clock-smoke 1')
    args = parser.parse_args()
    try:
        suite(args.libc_build, args.tools_lock, args.openzfs, args.openzfs_entropy, args.openzfs_heap, args.openzfs_alloc, args.openzfs_resources, args.openzfs_arc, args.long_waits, args.case)
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as error:
        parser.exit(1, f'[FAIL] {error}\n')
