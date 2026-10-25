# SPDX-License-Identifier: BSD-2-Clause
"""Private source-bound exit125 sites; no runtime policy or accepted cleanup."""
import hashlib
import json
from pathlib import Path
import re
import shutil

DECLARATION = ('extern void aether_pool_failure_site(unsigned);\n'
               'extern void aether_pool_failure_allocation(unsigned, unsigned long long, unsigned);\n'
               'extern void aether_pool_failure_assertion(unsigned, unsigned long long);\n'
               'extern void aether_pool_failure_pthread(unsigned long long, unsigned);\n'
               'extern void aether_pool_failure_denial(unsigned, long, unsigned, unsigned);\n'
               'extern unsigned aether_pool_failure_tid(void);\n')
# Expected counts deliberately reject newly added/missing guards.
FAMILIES = {'allocation': (1, 3), 'kernel': (16, 14), 'tpool': (32, 3),
            'resources': (40, 2), 'arc': (48, 1), 'startup': (56, 3),
            'assertion': (64, 2), 'time': (112, 6)}


def instrument(text, family):
    start, count = FAMILIES[family]
    matches = list(re.finditer(r'_Exit\(125\);', text))
    if len(matches) != count:
        raise ValueError('pool failure guard count changed: ' + family)
    rows = []
    for index, match in reversed(list(enumerate(matches))):
        site = start + index
        rows.append({'site': site, 'family': family,
                     'line': text[:match.start()].count('\n') + 1,
                     'context': text[max(0, match.start() - 180):match.end()]})
        marker = f'aether_pool_failure_site({site})'
        if family == 'allocation' and index < 2:
            marker = f'aether_pool_failure_allocation({site}, size, ' + ('errno)' if index == 0 else 'error)')
        if family == 'assertion' and index == 1:
            marker = 'aether_pool_assertion_record(func, line, format, args, (unsigned long long)__builtin_return_address(0))'
        text = text[:match.start()] + f'({marker}, _Exit(125));' + text[match.end():]
    if family == 'assertion':
        anchor = '\t(void) file; (void) func; (void) line; (void) format;'
        if text.count(anchor) != 1:
            raise ValueError('native assertion arguments changed')
        text = text.replace(anchor, '\t(void) file;\n\tva_list args;\n\tva_start(args, format);', 1)
        # Only the trusted VERIFY0 macro has this exact format/argument contract.
        helper = r"""
#include <stdarg.h>
#include <string.h>
static void aether_pool_assertion_record(const char *func, int line,
    const char *format, va_list args, unsigned long long caller)
{
    if (!strcmp(func, "zk_thread_create") &&
        !strcmp(format, "VERIFY0(%s) failed (%lld)")) {
        const char *expression = va_arg(args, const char *);
        if (!strcmp(expression, "pthread_create(&tid, &attr, zk_thread_wrapper, ztw)")) {
            unsigned long long error = va_arg(args, unsigned long long);
            aether_pool_failure_pthread(error, aether_pool_failure_tid());
            return;
        }
    }
    aether_pool_failure_assertion((unsigned)line, caller);
}
"""
        # Exit is still unconditional. End the caller's varargs lifetime first.
        text = text.replace('(aether_pool_assertion_record(func, line, format, args, (unsigned long long)__builtin_return_address(0)), _Exit(125));',
                            '(aether_pool_assertion_record(func, line, format, args, (unsigned long long)__builtin_return_address(0)), va_end(args), _Exit(125));', 1)
        rows.append({'site': 66, 'family': 'pthread-assertion',
                     'context': 'zk_thread_create exact VERIFY0 pthread_create expression; original error bits'})
        return DECLARATION + helper + text, sorted(rows, key=lambda row: row['site'])
    return DECLARATION + text, list(reversed(rows))


# Stages describe actual branches, not inferred availability or joint snapshots.
THREAD_STAGES = {
    1: ('admission-state', 'direct'), 2: ('admission-closing', 'direct'),
    3: ('admission-total-limit', 'direct'), 4: ('admission-live-limit', 'direct'),
    5: ('admission-c11', 'direct'), 6: ('admission-attribute-bounds', 'direct'),
    7: ('admission-attribute-extra', 'direct'), 8: ('clone-shape-or-lock', 'eagain'),
    9: ('clone-state-or-total-limit', 'eagain'), 10: ('clone-records-full', 'eagain'),
    11: ('clone-mapping-geometry', 'eagain'), 12: ('clone-stack-geometry', 'eagain'),
    13: ('clone-native-return', 'eagain'), 14: ('signal-mask-native-return', 'negate'),
    15: ('mmap-native-return', 'eagain'), 16: ('mprotect-native-return', 'eagain'),
    17: ('munmap-native-return', 'cleanup'),
}


def instrument_thread_backend(text):
    scope = 'admission'
    def replace(old, new):
        nonlocal text
        bounds = {'admission': ('int aether_pthread_admit(', 'int __clone('),
                  'clone': ('int __clone(', 'int __pthread_join('),
                  'syscall': ('long aether_wait_syscall(', 'long __aether_io(')}
        first, last = bounds[scope]
        begin, end = text.index(first), text.index(last)
        section = text[begin:end]
        if section.count(old) != 1:
            raise ValueError('thread diagnostic backend context changed: ' + old)
        text = text[:begin] + section.replace(old, new, 1) + text[end:]

    replace('        return broken ? broken : ENOSYS;',
            '        return thread_denial(1, broken ? broken : ENOSYS, 0);')
    replace('    if (closing || admissions >= 512 || live >= capacity)\n        return EAGAIN;',
            '    if (closing)\n        return thread_denial(2, EAGAIN, 1);\n'
            '    unsigned seen_admissions = admissions;\n'
            '    if (seen_admissions >= 512)\n        return thread_denial(3, EAGAIN, seen_admissions);\n'
            '    unsigned seen_live = live;\n'
            '    if (seen_live >= capacity)\n        return thread_denial(4, EAGAIN, seen_live);')
    replace('    if (attr == __ATTRP_C11_THREAD)\n        return ENOTSUP;',
            '    if (attr == __ATTRP_C11_THREAD)\n        return thread_denial(5, ENOTSUP, 0);')
    replace('given->_a_guardsize % 4096 || given->_a_detach > 1)\n            return ENOTSUP;',
            'given->_a_guardsize % 4096 || given->_a_detach > 1)\n            return thread_denial(6, ENOTSUP, 0);')
    replace('        if (memcmp(given, &accepted, sizeof accepted))\n            return ENOTSUP;',
            '        if (memcmp(given, &accepted, sizeof accepted))\n            return thread_denial(7, ENOTSUP, 0);')
    scope = 'clone'
    replace('        __thread_list_lock != __pthread_self()->tid)\n        return -ENOTSUP;',
            '        __thread_list_lock != __pthread_self()->tid)\n        return thread_denial(8, -ENOTSUP, 0);')
    replace('    if (closing || broken || admissions >= 512)\n        return broken ? -broken : -EAGAIN;',
            '    if (closing || broken || admissions >= 512)\n        return thread_denial(9, broken ? -broken : -EAGAIN, 0);')
    replace('    if (!record)\n        return -EAGAIN;',
            '    if (!record)\n        return thread_denial(10, -EAGAIN, capacity);')
    replace('        td->map_size > UINTPTR_MAX - (uintptr_t)td->map_base)\n        return -EINVAL;',
            '        td->map_size > UINTPTR_MAX - (uintptr_t)td->map_base)\n        return thread_denial(11, -EINVAL, 0);')
    replace('    if (base > UINTPTR_MAX - 136 || aligned < base + 136)\n        return -EINVAL;',
            '    if (base > UINTPTR_MAX - 136 || aligned < base + 136)\n        return thread_denial(12, -EINVAL, 0);')
    replace('    long result = memtrap(0x28006, thread_cap, (uintptr_t)&request, 0, 0);',
            '    long result = memtrap(0x28006, thread_cap, (uintptr_t)&request, 0, 0);\n'
            '    if (result < 0)\n        thread_denial(13, result, 0);')
    scope = 'syscall'
    for stage, call in ((14, 'memtrap(0x28009, thread_cap, a, b, c)'),
                        (15, 'memtrap(0x22001, memory_cap, b, c, 0)'),
                        (16, 'memtrap(0x22002, memory_cap, a, b, c)'),
                        (17, 'memtrap(0x22003, memory_cap, a, b, 0)')):
        replace('return ' + call + ';', f'return thread_result({stage}, {call});')
    helper = """
static long thread_denial(unsigned stage, long result, unsigned value)
{
    aether_pool_failure_denial(stage, result, value, aether_pool_failure_tid());
    return result;
}
static long thread_result(unsigned stage, long result)
{
    if (result < 0) thread_denial(stage, result, 0);
    return result;
}
"""
    scope = 'admission'
    replace('int aether_pthread_admit(const void *attr)', helper + '\nint aether_pthread_admit(const void *attr)')
    return text


def instrument_backend(text):
    # These nine calls belong to the sealed v3 backend. Its fatal body and
    # broken=EIO/terminal effects stay intact; record inside fatal after EIO.
    anchor = 'static _Noreturn void fatal(void)\n{\n    broken = EIO;\n'
    if text.count(anchor) != 1:
        raise ValueError('pool runtime fatal state transition changed')
    matches = list(re.finditer(r'(?m)^\s+fatal\(\);', text))
    if len(matches) != 9:
        raise ValueError('pool runtime fatal caller count changed')
    rows = []
    for index, match in reversed(list(enumerate(matches))):
        site = 96 + index
        rows.append({'site': site, 'family': 'runtime',
                     'line': text[:match.end()].count('\n'),
                     'context': text[max(0, match.start() - 180):match.end()]})
        text = text[:match.start()] + match.group().replace(
            'fatal();', f'fatal({site});') + text[match.end():]
    text = text.replace(anchor, 'static _Noreturn void fatal(unsigned site)\n{\n    broken = EIO;\n    aether_pool_failure_site(site);\n', 1)
    text = instrument_thread_backend(text)
    rows.append({'site': 120, 'family': 'thread-denial',
                 'stages': {str(k): {'name': v[0], 'conversion': v[1]} for k, v in THREAD_STAGES.items()}})
    return DECLARATION + text, sorted(rows, key=lambda row: row['site'])


def runtime_archive(port, runtime, tools, command):
    """Rebuild sealed base exactly first, then replace only a copied backend.o."""
    sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
    checkout = port / 'failure-runtime-checkout'
    shutil.copytree(runtime / 'base/source', checkout)
    (checkout / 'build').mkdir()
    output = checkout / 'build/runtime'
    command(['python3', '-B', checkout / 'experiments/native-service-runtime/build.py',
             '--sdk', runtime / 'base/sdk', '--output', output], port / 'failure-runtime.log')
    original = output / 'libaether_runtime.a'
    if sha(original) != sha(runtime / 'base/runtime/libaether_runtime.a'):
        raise ValueError('pool diagnostic base runtime reconstruction differs')
    source = runtime / 'base/source/experiments/native-service-runtime/backend.c'
    changed, catalogue = instrument_backend(source.read_text())
    selected = output / 'backend.c'
    selected.write_text(changed)
    # Reuse the actual base builder's compiler prefix and include inventories.
    commands = json.loads((output / 'commands.json').read_text())
    recipe = next(row['argv'] for row in commands if row['label'] == 'backend')
    prefix = recipe[:recipe.index('-c')]
    original_object_sha256 = sha(output / 'backend.o')
    command(prefix + ['-c', selected, '-o', output / 'backend.o'], port / 'failure-backend.log')
    archive = port / 'failure-runtime/libaether_runtime.a'
    archive.parent.mkdir()
    shutil.copyfile(runtime / 'runtime/libaether_runtime.a', archive)
    command([tools['ar']['path'], 'rcs', archive, output / 'backend.o'], port / 'failure-archive.log')
    return {'backend_compiler_prefix': prefix, 'archive_sha256': sha(archive), 'base_reconstruction_sha256': sha(original),
            'original_backend_sha256': original_object_sha256,
            'selected_backend_sha256': sha(output / 'backend.o'),
            'original_source_sha256': sha(source), 'selected_source_sha256': sha(selected),
            'catalogue': catalogue, 'scope': 'private diagnostic copy; not the sealed runtime archive'}


def decode_site(serial, catalogue):
    """Only the exact creation prefix plus one site/125 is attributable."""
    known = {row['site']: row for row in catalogue}
    if len(known) != len(catalogue):
        raise ValueError('duplicate failure site identity')
    rows = [tuple(map(int, row)) for row in re.findall(
        r'^NATIVE observation slot=(\d+) generation=(\d+) offset=(\d+) byte=(\d+)$', serial, re.M)]
    terminals = re.findall(r'^NATIVE terminal slot=(\d+) generation=(\d+) kind=(\d+) detail=(\d+)$', serial, re.M)
    if len(rows) not in (16, 22, 28, 32) or [r[:3] for r in rows] != [(0, 1, i * 8) for i in range(len(rows))]:
        raise ValueError('failure marker missing/interleaved or foreign')
    if bytes(r[3] for r in rows[:6]) != b'BIUVWP' or rows[14][3] != ord('C'):
        raise ValueError('failure creation prefix absent')
    if terminals != [('0', '1', '1', '125')] or serial.count('NATIVE supervisor result=401 reclaimed=0\n') != 1:
        raise ValueError('failure terminal/unclean owner mismatch')
    terminal = serial.index('NATIVE terminal slot=0 generation=1 kind=1 detail=125\n')
    if terminal < serial.rfind('NATIVE observation ') or serial.index('NATIVE supervisor result=401 reclaimed=0\n') < terminal:
        raise ValueError('failure result ordering mismatch')
    site = rows[15][3]
    if site not in known:
        raise ValueError('unknown failure site')
    result = known[site].copy()
    if site in (66, 120):
        data = bytes(r[3] for r in rows)
        start = 15
        denial = None
        if site == 120:
            if len(rows) != 32 or data[25] != 66 or 66 not in known:
                raise ValueError('thread denial/assertion incomplete or repeated')
            stage, error = data[16], int.from_bytes(data[17:19], 'little', signed=True)
            value, tid = int.from_bytes(data[19:21], 'little'), int.from_bytes(data[21:25], 'little')
            if stage not in THREAD_STAGES or not error or error == -32768 or not tid:
                raise ValueError('invalid thread denial payload')
            name, conversion = THREAD_STAGES[stage]
            if conversion == 'cleanup':
                raise ValueError('cleanup failure is not a thread rejection')
            if (conversion == 'direct' and error <= 0) or (conversion != 'direct' and error >= 0):
                raise ValueError('thread denial error sign mismatch')
            expected_errors = {2: 11, 3: 11, 4: 11, 5: 95, 6: 95, 7: 95,
                               8: -95, 10: -11, 11: -22, 12: -22}
            if stage in expected_errors and error != expected_errors[stage]:
                raise ValueError('thread denial branch error mismatch')
            if ((stage == 2 and value != 1) or (stage == 3 and value < 512) or
                    (stage == 4 and value < 82) or (stage == 10 and value != 82) or
                    (stage not in (2, 3, 4, 10) and value != 0)):
                raise ValueError('thread denial guard value mismatch')
            denial = dict(stage=stage, branch=name, original_return=error,
                          compared_value=value, caller_tid=tid,
                          conversion=conversion, joint_resource_snapshot=False)
            start = 25
        elif len(rows) != 22:
            raise ValueError('pthread assertion incomplete')
        error = int.from_bytes(data[start+1:start+3], 'little')
        tid = int.from_bytes(data[start+3:start+7], 'little')
        if not 0 < error <= 32767 or not tid:
            raise ValueError('invalid original pthread error/identity')
        if denial:
            expected = denial['original_return'] if denial['conversion'] == 'direct' else (
                11 if denial['conversion'] == 'eagain' else -denial['original_return'])
            if tid != denial['caller_tid'] or error != expected:
                raise ValueError('thread denial caller/error conversion mismatch')
        result = known[66].copy()
        result.update(pthread_error=error, caller_tid=tid, denial=denial)
        return result
    if site in (1, 2):
        if len(rows) != 28:
            raise ValueError('allocation diagnostic incomplete')
        result.update(requested_bytes=int.from_bytes(bytes(r[3] for r in rows[16:24]), 'little'),
                      error_bits=int.from_bytes(bytes(r[3] for r in rows[24:28]), 'little'))
    elif site == 65:
        if len(rows) != 28:
            raise ValueError('assertion diagnostic incomplete')
        result.update(assertion_line=int.from_bytes(bytes(r[3] for r in rows[16:20]), 'little'),
                      caller_return_address=int.from_bytes(bytes(r[3] for r in rows[20:28]), 'little'))
    elif len(rows) != 16:
        raise ValueError('unexpected diagnostic payload')
    return result


def assertion_symbol(symbols, caller):
    """Require a sized text symbol covering the last byte before return."""
    if not isinstance(caller, int) or caller <= 0 or caller >= 1 << 64:
        raise ValueError('invalid assertion return address')
    matches = []
    for line in symbols.splitlines():
        fields = line.split()
        if len(fields) == 4 and fields[2] in ('t', 'T'):
            start, size = int(fields[0], 16), int(fields[1], 16)
            if start <= caller - 1 < start + size:
                matches.append({'symbol': fields[3], 'start': start, 'bytes': size,
                                'return_offset': caller - start})
    if len(matches) != 1:
        raise ValueError('assertion caller symbol absent/ambiguous')
    return matches[0]


def symbolize_assertion(site, elf, tools, command):
    """Compact host analysis of an observed PC; no guest read or stack walk."""
    symbols = elf.parent / 'assertion-symbols.log'
    command([tools['nm']['path'], '--print-size', '--defined-only', elf], symbols)
    original_sha256 = hashlib.sha256(symbols.read_bytes()).hexdigest()
    try:
        result = assertion_symbol(symbols.read_text(), site['caller_return_address'])
    finally:
        symbols.unlink()
    caller = site['caller_return_address']
    disassembly = elf.parent / 'assertion-caller.log'
    objdump = Path(tools['nm']['path']).parent / 'llvm-objdump'
    if not objdump.is_file():
        raise ValueError('assertion disassembler unavailable')
    command([objdump, '-d', '--start-address=' + str(max(result['start'], caller - 48)),
             '--stop-address=' + str(min(result['start'] + result['bytes'], caller + 16)),
             elf], disassembly)
    result.update(symbols_sha256=original_sha256,
                  objdump_sha256=hashlib.sha256(objdump.read_bytes()).hexdigest(),
                  disassembly=disassembly.read_text(),
                  scope='sized text symbol containing return PC; inspect call instruction; no source-file or root-cause claim')
    return result
