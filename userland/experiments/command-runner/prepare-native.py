#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Build broker requester candidates only; never boot or claim native acceptance."""
import argparse
import hashlib
import json
import re
import struct
import tempfile
from pathlib import Path

from process import clean_env, run as owned_run

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def need(ok, msg):
    if not ok:
        raise RuntimeError(msg)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sdk', type=Path, required=True)
    p.add_argument('--bootstrap-controls', action='store_true')
    p.add_argument('--reply-controls', action='store_true')
    p.add_argument('--launch-controls', action='store_true')
    p.add_argument('--terminal-controls', action='store_true')
    p.add_argument('--startup-controls', action='store_true')
    p.add_argument('--mapped-results', action='store_true')
    p.add_argument('--mapped-uncertainty', action='store_true')
    p.add_argument('--carrier-controls', action='store_true')
    p.add_argument('--budget-controls', action='store_true')
    a = p.parse_args()
    if a.mapped_uncertainty or a.carrier_controls or a.budget_controls:
        a.mapped_results = True
    sdk = a.sdk.resolve()
    pin = (
        ROOT / 'docs/evidence/native-stdio-files-2026-09-05/libc/evidence.json'
    )
    reference = json.loads(pin.read_text())
    tools = reference['tools']
    for name, t in tools.items():
        need(sha(Path(t['path'])) == t['sha256'], 'changed tool: ' + name)

    def inventory():
        return {
            str(p.relative_to(sdk)): sha(p)
            for p in (sdk / 'stage').rglob('*')
            if p.is_file()
        }

    need(
        not any((p.is_symlink() for p in (sdk / 'stage').rglob('*'))),
        'SDK symlink'
    )
    need(inventory() == reference['sdk_inputs'], 'SDK differs from tested pin')
    need(
        sha(sdk / 'evidence.json') == reference['libc_receipt_sha256'],
        'SDK receipt changed'
    )
    runner_source = HERE / 'runner.c'
    channel_source = HERE.parent / 'native-channel/channel.c'
    inputs = [
        runner_source,
        HERE / 'prepare-native.py',
        channel_source,
        HERE.parent / 'native-channel/channel.h'
    ]
    inputs += [
        HERE / 'process.py',
        HERE / 'bytecount.c',
        HERE / 'native-io.c',
        HERE / 'native-io.h',
        HERE / 'native-entry.c'
    ]
    if a.bootstrap_controls:
        inputs.append(HERE / 'bootstrap-native.c')
    if a.reply_controls:
        inputs.append(HERE / 'reply-native.c')
    if a.launch_controls:
        inputs.append(HERE / 'launch-native.h')
    if a.terminal_controls:
        inputs.append(HERE / 'terminal-native.c')
    if a.startup_controls or a.mapped_results:
        inputs += [HERE / n for n in ('runner-parse.c', 'runner-parse.h',
                                      'startup-observer.c')]
    if a.mapped_results:
        inputs += [HERE / n for n in ('runner-result.c', 'runner-result.h',
                   'mapped-runner.h', 'mapped-child.c', 'mapped-cleanup.c')]
    if a.mapped_uncertainty:
        inputs += [HERE / 'mapped-uncertainty.c', HERE / 'mapped-controls.h']
    if a.carrier_controls:
        inputs.append(HERE / 'carrier-native.c')
    if a.budget_controls:
        inputs += [HERE / 'budget-native.c', HERE / 'mapped-controls.h']
    local = {str(p): sha(p) for p in inputs}
    work = Path(tempfile.mkdtemp(
        prefix='command-clients-',
        dir=ROOT / 'build'
    ))
    print(work, flush=True)
    r = {
        'schema': 'aether-userland.command-clients-build.v1',
        'status': 'incomplete',
        'scope': (
            'source-rebuilt client ELFs; linking and inspection '
            'only, no native execution or producer acceptance'
        ),
        'sdk_pin': str(pin),
        'sdk_pin_sha256': sha(pin),
        'local_sources': local,
        'commands': [],
        'artifacts': {}
    }

    def save():
        (work / 'evidence.json').write_text(json.dumps(r, indent=2) + '\n')

    def run(label, cmd):
        result = owned_run(
            cmd,
            cwd=work,
            env=clean_env(work),
            work=work,
            label=label,
            timeout=180
        )
        (work / (label + '.log')).write_bytes(result.stdout + result.stderr)
        r['commands'].append({
            'label': label,
            'argv': cmd,
            'exit': result.returncode,
            'process': result.record
        })
        save()
        need(
            result.record['complete'] and result.returncode == 0,
            label + ' failed'
        )
        return result.stdout
    save()
    try:
        cc = [
            tools['clang']['path'],
            '--no-default-config',
            '--target=x86_64-linux-musl',
            '--sysroot=' + str(sdk / 'empty-root')
        ]
        flags = [
            '-D_POSIX_C_SOURCE=200809L',
            '-std=c17',
            '-O2',
            '-Wall',
            '-Wextra',
            '-Werror',
            '-ffreestanding',
            '-fno-builtin',
            '-fstack-protector-strong',
            '-nostdinc',
            '-isystem',
            str(sdk / 'stage/usr/include')
        ]
        r['profile'] = 'inherited-launch'
        run(
            'channel',
            cc + flags + [
                '-D__aether_io=__aether_channel_io',
                '-c',
                str(channel_source),
                '-o',
                str(work / 'channel.o')
            ]
        )
        run(
            'native-io',
            cc + flags + [
                '-c',
                str(HERE / 'native-io.c'),
                '-o',
                str(work / 'native-io.o')
            ]
        )
        run(
            'entry',
            cc + flags + [
                '-c',
                str(HERE / 'native-entry.c'),
                '-o',
                str(work / 'entry.o')
            ]
        )
        lib = sdk / 'stage/usr/lib'
        variants = [
            ('parent', []),
            ('rejected-launch', ['-DREJECT_LAUNCH']),
            ('partial-reservation', ['-DREJECT_CAPACITY']),
            ('full-output', ['-DFULL_OUTPUT']),
            ('command', ['-Dmain=bytecount_main'])
        ]
        if a.bootstrap_controls:
            original = (HERE / 'native-io.c').read_text()
            anchor = '    /* Validate the complete pair before publishing either binding. */'
            need(original.count(anchor) == 1, 'mutation anchor changed')
            mutated = original.replace(anchor,
                '    refs[0] = native_word(r + 4);\n'
                '    fds[0] = native_word(r + 8);\n'
                '    rights[0] = native_word(r + 12);\n'
                '    live[0] = 1;\n' + anchor)
            path = work / 'early-io.c'
            path.write_text(mutated)
            run('early-io', cc + flags + ['-I', str(HERE), '-c', str(path),
                '-o', str(work / 'early-io.o')])
            r['mutation_sha256'] = sha(path)
            variants += [(label, ['-DBOOTSTRAP_FIELD=' + str(field)])
                         for label, field in [('bootstrap-reference', 16),
                         ('bootstrap-descriptor', 20), ('bootstrap-rights', 24),
                         ('bootstrap-early-publication', 24)]]
        if a.reply_controls:
            original = (HERE / 'native-io.c').read_text()
            guard = '    if (poisoned)\n        return 0;'
            need(original.count(guard) == 1, 'poison mutation anchor changed')
            path = work / 'unguarded-io.c'
            path.write_text(original.replace(guard, '    /* test-only removed guard */'))
            run('unguarded-io', cc + flags + ['-I', str(HERE), '-c', str(path),
                '-o', str(work / 'unguarded-io.o')])
            r['unguarded_mutation_sha256'] = sha(path)
            variants += [('reply-drop-read', []), ('reply-bad-read', ['-DBAD_REPLY']),
                         ('reply-drop-close', ['-DDROP_CLOSE']),
                         ('reply-disabled-poison', [])]
        if a.launch_controls:
            variants += [('launch-corpus', ['-DLAUNCH_CORPUS'])]
            variants += [('launch-eof-' + str(n), ['-DLAUNCH_PREFIX=' + str(n)])
                         for n in (0, 1, 4, 16, 31, 32, 383)]
        if a.terminal_controls:
            for kind, extra in [('normal', []), ('fault', ['-DTERMINAL_FAULT'])]:
                run('terminal-' + kind + '-wrapper', cc + flags + extra + [
                    '-c', str(HERE / 'terminal-native.c'),
                    '-o', str(work / ('terminal-' + kind + '-wrapper.o'))])
            variants += [
                ('terminal-normal-parent', ['-DTERMINAL_DETAIL=134', '-DTERMINAL_KIND=1']),
                ('terminal-fault-parent', ['-DTERMINAL_DETAIL=134', '-DTERMINAL_KIND=2']),
                ('terminal-normal-command', ['-Dmain=bytecount_main']),
                ('terminal-fault-command', ['-Dmain=bytecount_main']),
            ]
        if a.startup_controls or a.mapped_results:
            for label, source, defines in [
                ('startup-io', 'native-io.c', ['-DNATIVE_RUNNER_STARTUP']),
                ('runner-parse', 'runner-parse.c', []),
            ]:
                run(label, cc + flags + defines + ['-c', str(HERE / source),
                    '-o', str(work / (label + '.o'))])
            variants += [('startup-parent', ['-DNATIVE_RUNNER_STARTUP']),
                         ('startup-corrupt-parent', ['-DNATIVE_RUNNER_STARTUP',
                                                     '-DCORRUPT_STARTUP']),
                         ('startup-observer', [])]
        if a.mapped_results:
            strict = ['-Wpedantic', '-Wconversion', '-Wsign-conversion',
                      '-Wshadow', '-Wstrict-prototypes', '-Wmissing-prototypes']
            for label, source in [('runner-result', 'runner-result.c'),
                                  ('mapped-cleanup', 'mapped-cleanup.c')]:
                run(label, cc + flags + strict + ['-c', str(HERE / source),
                    '-o', str(work / (label + '.o'))])
            for value in ('0', '1', '2', '64', '125', '126', '127', '134', '255', 'fault'):
                name = 'mapped-child-' + value
                define = ('-DMAPPED_CHILD_FAULT' if value == 'fault'
                          else '-DMAPPED_CHILD_STATUS=' + value)
                run(name + '-wrapper', cc + flags + strict + [define, '-c',
                    str(HERE / 'mapped-child.c'), '-o', str(work / (name + '-wrapper.o'))])
                variants.append((name, ['-Dmain=bytecount_main']))
            for name, extra in [('mapped-parent', []),
                                ('mapped-ignore-kind', ['-DMAPPED_IGNORE_KIND']),
                                ('mapped-force-zero', ['-DMAPPED_FORCE_ZERO']),
                                ('mapped-cleanup-parent', [])]:
                variants.append((name, ['-DNATIVE_RUNNER_STARTUP',
                                       '-DNATIVE_MAPPED_RESULTS'] + extra))
        if a.mapped_uncertainty:
            uncertainty = [
                ('uncertain-admission-lost', ['-DUNCERTAIN_OP=4']),
                ('uncertain-admission-padding', ['-DUNCERTAIN_OP=4', '-DUNCERTAIN_PADDING']),
                ('uncertain-collection-lost', ['-DUNCERTAIN_OP=5']),
                ('uncertain-collection-padding', ['-DUNCERTAIN_OP=5', '-DUNCERTAIN_PADDING']),
                ('uncertain-collection-receipt', ['-DUNCERTAIN_OP=5', '-DUNCERTAIN_RECEIPT']),
                ('uncertain-retry', ['-DUNCERTAIN_OP=5']),
            ]
            original = (HERE / 'mapped-runner.h').read_text()
            anchor = '        if (!native_exchange(q, 32, r))\n            return 1;'
            need(original.count(anchor) == 1, 'mapped retry mutation anchor')
            (work / 'mapped-runner.h').write_text(original.replace(anchor,
                anchor.replace('return 1;', 'continue;')))
            (work / 'retry-runner.c').write_bytes(runner_source.read_bytes())
            for name, defines in uncertainty:
                run(name + '-wrapper', cc + flags + strict + defines + ['-c',
                    str(HERE / 'mapped-uncertainty.c'), '-o', str(work / (name + '-wrapper.o'))])
                variants.append((name, ['-DNATIVE_RUNNER_STARTUP', '-DNATIVE_MAPPED_RESULTS',
                    '-Dmain=runner_main', '-include', str(HERE / 'mapped-controls.h'),
                    '-I', str(HERE)]))
        if a.carrier_controls:
            original = (HERE / 'native-io.c').read_text()
            anchor = '    unsigned char r[32];\n    if (!input'
            need(original.count(anchor) == 1, 'carrier publication mutation anchor')
            path = work / 'carrier-early-io.c'
            path.write_text(original.replace(anchor,
                '    if (carrier)\n        *startup = candidate;\n' + anchor))
            run('carrier-early-io', cc + flags + ['-DNATIVE_RUNNER_STARTUP',
                '-I', str(HERE), '-c', str(path), '-o', str(work / 'carrier-early-io.o')])
            r['carrier_mutation_sha256'] = sha(path)
            variants += [('carrier-' + name, ['-DNATIVE_RUNNER_STARTUP',
                         '-DCARRIER_FIELD=' + str(field)]) for name, field in (
                         ('magic', 0), ('count', 8), ('reserved', 12),
                         ('padding', 63), ('rights', 248), ('early-arguments', 248))]
            variants += [('carrier-prefix-' + str(n), ['-DNATIVE_RUNNER_STARTUP',
                         '-DCARRIER_PREFIX=' + str(n)]) for n in (0, 223, 255)]
        if a.budget_controls:
            for name, defines, mutation in (
                ('budget-last', ['-DBUDGET_LAST'], None),
                ('budget-exhausted', [], None),
                ('budget-overrun', [], 'turn <= 100000'),
                ('budget-short', ['-DBUDGET_LAST', '-DBUDGET_SHORT'], 'turn < 99999')):
                run(name + '-wrapper', cc + flags + strict + defines + ['-c',
                    str(HERE / 'budget-native.c'), '-o', str(work / (name + '-wrapper.o'))])
                if mutation:
                    private = work / name
                    private.mkdir()
                    original = (HERE / 'mapped-runner.h').read_text()
                    need(original.count('turn < 100000') == 1, 'budget mutation anchor')
                    (private / 'mapped-runner.h').write_text(
                        original.replace('turn < 100000', mutation))
                    (private / 'runner.c').write_bytes(runner_source.read_bytes())
                variants.append((name, ['-DNATIVE_RUNNER_STARTUP', '-DNATIVE_MAPPED_RESULTS',
                    '-Dmain=runner_main', '-include', str(HERE / 'mapped-controls.h'),
                    '-I', str(HERE)]))
        for name, flag in variants:
            obj = work / (name + '.o')
            elf = work / (name + '.elf')
            terminal_command = name in ('terminal-normal-command', 'terminal-fault-command')
            mapped_child = name.startswith('mapped-child-')
            carrier_parent = name.startswith('carrier-')
            budget_parent = name.startswith('budget-')
            uncertainty_parent = name.startswith('uncertain-')
            mapped_parent = budget_parent or uncertainty_parent or name in ('mapped-parent', 'mapped-ignore-kind',
                                     'mapped-force-zero', 'mapped-cleanup-parent')
            command_client = name == 'command' or terminal_command or mapped_child
            reply_probe = name.startswith('reply-')
            probe = name.startswith('bootstrap-') or reply_probe
            source = (HERE / 'carrier-native.c' if carrier_parent else
                      HERE / 'startup-observer.c' if name == 'startup-observer' else
                      HERE / 'reply-native.c' if reply_probe else
                      HERE / 'bootstrap-native.c' if probe else
                      HERE / 'bytecount.c' if command_client else runner_source)
            if name == 'uncertain-retry':
                source = work / 'retry-runner.c'
            if name in ('budget-short', 'budget-overrun'):
                source = work / name / 'runner.c'
            adapter = 'early-io.o' if name == 'bootstrap-early-publication' else 'native-io.o'
            startup_parent = carrier_parent or mapped_parent or name in ('startup-parent', 'startup-corrupt-parent')
            if startup_parent:
                adapter = 'startup-io.o'
            if name == 'carrier-early-arguments':
                adapter = 'carrier-early-io.o'
            if name == 'reply-disabled-poison':
                adapter = 'unguarded-io.o'
            run(
                name + '-compile',
                cc + flags + flag + (['-Wpedantic', '-Wconversion',
                    '-Wsign-conversion', '-Wshadow', '-Wstrict-prototypes',
                    '-Wmissing-prototypes'] if name == 'startup-observer' or mapped_parent or carrier_parent else []) + [
                    '-c',
                    str(source),
                    '-o',
                    str(obj)
                ]
            )
            run(
                name + '-link',
                cc + [
                    '--ld-path=' + tools['lld']['path'],
                    '-nostdlib',
                    '-static',
                    '-Wl,-z,noexecstack',
                    '-Wl,--no-undefined',
                    '-Wl,-Map,' + str(work / (name + '.map')),
                    str(lib / 'crt1.o'),
                    str(lib / 'crti.o'),
                    str(obj),
                    str(work / adapter),
                    *([str(work / 'runner-parse.o')] if startup_parent else []),
                    *([str(work / 'runner-result.o')] if mapped_parent else []),
                    *([str(work / (name + '-wrapper.o')), '-Wl,--wrap=native_exchange',
                       '-Wl,--wrap=channel_raw', '-Wl,--wrap=channel_yield',
                       '-Wl,--wrap=read', '-Wl,--wrap=close', '-Wl,--wrap=ar_terminal_exit']
                      if budget_parent else []),
                    *([str(work / (name + '-wrapper.o')), '-Wl,--wrap=channel_raw',
                       '-Wl,--wrap=native_exchange', '-Wl,--wrap=read', '-Wl,--wrap=close',
                       '-Wl,--wrap=ar_terminal_exit'] if uncertainty_parent else []),
                    *([str(work / (name + '-wrapper.o')), '-Wl,--wrap=close']
                      if mapped_child else []),
                    *([str(work / 'mapped-cleanup.o'), '-Wl,--wrap=close',
                       '-Wl,--wrap=ar_terminal_exit'] if name == 'mapped-cleanup-parent' else []),
                    *([str(work / 'command.o')] if name == 'startup-observer' else []),
                    *(['-Wl,--wrap=channel_raw'] if probe else []),
                    *(['-Wl,--wrap=channel_raw', '-Wl,--wrap=getauxval']
                      if carrier_parent else []),
                    *([str(work / 'entry.o')] if command_client else []),
                    *([str(work / (name.replace('-command', '-wrapper') + '.o')),
                       '-Wl,--wrap=close'] if terminal_command else []),
                    str(work / 'channel.o'),
                    str(lib / 'libc.a'),
                    str(lib / 'crtn.o'),
                    '-o',
                    str(elf)
                ]
            )
            if command_client or probe or carrier_parent:
                need(
                    all(('libc.a(' + symbol + '.lo)' in (work / (name + '.map')).read_text() for symbol in (
                        'read',
                        'write',
                        'close'
                    ))),
                    'command bypassed public musl'
                )
            need(
                'pthread_cancel.lo' not in (work / (name + '.map')).read_text(),
                'threaded cancellation path'
            )
            need(
                not run(
                    name + '-undefined',
                    [
                        tools['nm']['path'],
                        '--undefined-only',
                        '--extern-only',
                        str(elf)
                    ]
                ).strip(),
                'undefined symbol'
            )
            need(
                not re.search(
                    b'\\bsyscall\\b',
                    run(
                        name + '-disassembly',
                        [tools['objdump']['path'], '-d', str(elf)]
                    )
                ),
                'Linux syscall instruction'
            )
            run(
                name + '-headers',
                [tools['readelf']['path'], '-h', '-l', str(elf)]
            )
            data = elf.read_bytes()
            offset = struct.unpack_from('<Q', data, 32)[0]
            width, count = struct.unpack_from('<HH', data, 54)
            headers = [struct.unpack_from(
                '<IIQQQQQQ',
                data,
                offset + i * width
            ) for i in range(count)]
            need(
                data[:6] == b'\x7fELF\x02\x01' and struct.unpack_from(
                    '<HH',
                    data,
                    16
                ) == (2, 62),
                'ELF type/machine'
            )
            need(
                len(data) <= 1048576 and any(
                    h[0] == 7 and h[1] == 4 and (0 < h[6] <= 4096)
                    for h in headers
                ),
                'size/TLS bound'
            )
            need(
                not any((h[0] in (
                    2,
                    3
                ) or (h[0] == 1 and h[1] & 3 == 3) for h in headers)),
                'dynamic/WX segment'
            )
            need(
                any((h[0] == 0x6474E551 and (not h[1] & 1) for h in headers)),
                'missing NX stack'
            )
            r['artifacts'][name] = {
                'path': str(elf),
                'sha256': sha(elf),
                'bytes': len(data)
            }
        need(
            inventory() == reference['sdk_inputs'],
            'SDK changed during build'
        )
        for name, h in local.items():
            need(sha(Path(name)) == h, 'source changed during build')
        r['status'] = 'pass'
        print('PASS: ' + str(len(variants)) + ' inspected client ELFs; native execution pending')
    finally:
        save()

if __name__ == '__main__':
    main()
