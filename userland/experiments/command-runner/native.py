#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Independent pinned ABI 9 coexistence consumer; no POSIX inheritance adoption."""
import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import sys
import tempfile
import tarfile
from pathlib import Path

from process import clean_env, run as owned_run

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def need(ok, msg):
    if not ok:
        raise RuntimeError(msg)


def expected_panic_context(name, detail):
    """Keep semantic failure evidence distinct from unrelated boot failures."""
    if not detail:
        return ()
    if detail == 53:
        child_status = 64 if name == 'wrong-startup' else 0
        return (
            f'NATIVE terminal slot=2 generation=1 kind=1 detail={child_status}',
            f'NATIVE terminal slot=0 generation=1 kind=1 detail={detail}',
            'NATIVE supervisor result=970 reclaimed=0',
        )
    return (
        'NATIVE terminal slot=2 generation=1 kind=1 detail=0',
        'NATIVE supervisor result=985 reclaimed=0',
    )


def expected_terminals(name):
    """Command, parent, backend exit order for each of two generations."""
    child_status = 1 if name == 'full-output' else 0
    statuses = ((2, child_status), (0, 29), (1, 17))
    return [
        f'NATIVE terminal slot={slot} generation={generation} '
        f'kind=1 detail={status}'
        for generation in (1, 2)
        for slot, status in statuses
    ]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--aether', type=Path, required=True)
    p.add_argument('--sdk', type=Path, required=True)
    p.add_argument(
        '--producer',
        type=Path,
        required=True,
        help='completed ABI 9 evidence directory'
    )
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
    owner = a.aether.resolve()
    producer = a.producer.resolve()
    if (a.bootstrap_controls or a.reply_controls or a.launch_controls or
            a.terminal_controls or a.startup_controls or a.mapped_results):
        lock_path = ROOT / 'docs/evidence/runner-owner-review-2026-09-06/review-input.lock.json'
        lock = json.loads(lock_path.read_text())
        report_path = producer / lock['report']
        archive = producer / lock['source_archive']
        need(sha(report_path) == lock['report_sha256'], 'producer report pin')
        need(sha(archive) == lock['source_archive_sha256'], 'producer archive pin')
    else:
        report_path = producer / 'summary.json'
        archive = producer / 'producer-sources.tar.gz'
        need(sha(report_path) == '01da8085be75c4470a255e4311791bd9a21911c560667ddd047c64583d41127c',
             'producer summary pin mismatch')
    summary = json.loads(report_path.read_text())
    need(sha(archive) == summary['source_archive_sha256'], 'source archive mismatch')
    need(sha(producer / 'command-runner/results.json') ==
         summary['suites']['command-runner']['report_sha256'], 'producer report mismatch')
    work = Path(tempfile.mkdtemp(
        prefix='native-command-userland-',
        dir=ROOT / 'build'
    ))
    print(work, flush=True)
    kernel = work / 'Aether'
    kernel.mkdir()
    sources = summary['inputs']
    # Materialize only receipt-listed regular files; reject links and paths.
    with tarfile.open(archive, 'r:gz') as tar:
        members = tar.getmembers()
        need(
            len(members) == len(sources)
            and len({m.name for m in members}) == len(members),
            'archive inventory/duplicates'
        )
        for m in members:
            name = Path(m.name)
            need(
                m.isfile()
                and (not name.is_absolute())
                and ('..' not in name.parts)
                and (m.name in sources),
                'unsafe/unlisted archive member'
            )
            data = tar.extractfile(m).read()
            need(
                hashlib.sha256(data).hexdigest() == sources[m.name],
                'archive member mismatch: ' + m.name
            )
            target = kernel / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    shutil.copytree(owner / '.deps', kernel / '.deps')
    local = {str(p): sha(p) for p in HERE.iterdir() if p.is_file()}
    host_tools = json.loads((HERE / 'host-tools.lock.json').read_text())
    for name, t in host_tools.items():
        need(sha(Path(t['path'])) == t['sha256'], 'host tool changed: ' + name)
    tool_bin = work / 'tools'
    tool_bin.mkdir()
    for name, t in host_tools.items():
        (tool_bin / name).symlink_to(t['path'])
    (tool_bin / 'python3').symlink_to(sys.executable)
    # Nested producer builds resolve rustc through this private wrapper.
    (tool_bin / 'rustc').unlink()
    rust_wrapper = tool_bin / 'rustc'
    rust_wrapper.write_text('#!' + sys.executable + '\n# SPDX-License-Identifier: BSD-2-Clause\nimport os,sys\ncompiler=' + repr(host_tools['rustc']['path']) + '\nos.environ["DYLD_LIBRARY_PATH"]=' + repr(str(Path(host_tools['rustc']['path']).parents[1] / 'lib')) + (
        '\nos.execv(compiler,[compiler]+[x for x in sys.argv[1:] '
        'if x!="+1.98.0"])\n'
    ))
    rust_wrapper.chmod(493)
    environment = clean_env(work)
    environment['PATH'] = str(tool_bin) + ':/usr/bin:/bin'
    rust_environment = dict(
        environment,
        DYLD_LIBRARY_PATH=str(Path(host_tools['rustc']['path']).parents[1] / 'lib')
    )
    r = {
        'schema': 'aether-userland.native-command-userland.v1',
        'status': 'incomplete',
        'scope': (
            'independent finite runner, two-binding adapter and '
            'bytecount command under owner broker/backend; no public '
            'aether-run CLI or full CR-01 acceptance'
        ),
        'bootstrap_controls': a.bootstrap_controls,
        'reply_controls': a.reply_controls,
        'launch_controls': a.launch_controls,
        'terminal_controls': a.terminal_controls,
        'startup_controls': a.startup_controls,
        'mapped_results': a.mapped_results,
        'mapped_uncertainty': a.mapped_uncertainty,
        'carrier_controls': a.carrier_controls,
        'budget_controls': a.budget_controls,
        'kernel_sources': sources,
        'local_sources': local,
        'producer_summary_sha256': sha(report_path),
        'producer_report_sha256': sha(producer / 'command-runner/results.json'),
        'producer_archive_sha256': sha(archive),
        'commands': [],
        'cases': [],
        'host_tools': host_tools,
        'environment': environment,
        'rust_wrapper_sha256': sha(rust_wrapper)
    }

    def save():
        (work / 'evidence.json').write_text(json.dumps(r, indent=2) + '\n')

    def run(label, cmd, extra_env=None):
        if cmd[0] in host_tools:
            cmd = [host_tools[cmd[0]]['path']] + [x for x in cmd[1:] if x != '+1.98.0']
        selected_env = dict(rust_environment if cmd[0] == host_tools['rustc']['path']
                            else environment)
        if extra_env:
            selected_env.update(extra_env)
        result = owned_run(
            cmd,
            cwd=kernel,
            env=selected_env,
            work=work,
            label=label,
            timeout=180,
            file_limit=512 * 1024 ** 2
        )
        (work / (label + '.log')).write_bytes(result.stdout + result.stderr)
        r['commands'].append({
            'label': label,
            'argv': cmd,
            'cwd': str(kernel),
            'exit': result.returncode,
            'process': result.record
        })
        save()
        need(
            result.record['complete'] and result.returncode == 0,
            label + ' failed; ' + str(work)
        )
        return result.stdout
    save()
    try:
        output = run(
            'requester-prepare',
            [
                sys.executable,
                str(HERE / 'prepare-native.py'),
                '--sdk',
                str(sdk),
                *(['--bootstrap-controls'] if a.bootstrap_controls else []),
                *(['--reply-controls'] if a.reply_controls else []),
                *(['--launch-controls'] if a.launch_controls else []),
                *(['--terminal-controls'] if a.terminal_controls else []),
                *(['--startup-controls'] if a.startup_controls else []),
                *(['--mapped-results'] if a.mapped_results else []),
                *(['--mapped-uncertainty'] if a.mapped_uncertainty else []),
                *(['--carrier-controls'] if a.carrier_controls else []),
                *(['--budget-controls'] if a.budget_controls else [])
            ]
        )
        prepared = Path(output.decode().splitlines()[0])
        receipt = json.loads((prepared / 'evidence.json').read_text())
        need(receipt['status'] == 'pass', 'requester build incomplete')
        r['requester_build'] = {
            'output': str(prepared),
            'receipt_sha256': sha(prepared / 'evidence.json')
        }
        reference = json.loads(Path(receipt['sdk_pin']).read_text())
        tools = reference['tools']
        r['tools'] = tools
        r['boot_dependency_manifest'] = json.loads((kernel / '.deps/manifest.json').read_text())
        for label, cmd in [
            ('zig-version', ['zig', 'version']),
            ('rust-version', ['rustc', '+1.98.0', '--version']),
            ('qemu-version', ['qemu-system-x86_64', '--version'])
        ]:
            run(label, cmd)
        cc = [
            tools['clang']['path'],
            '--no-default-config',
            '--target=x86_64-linux-musl',
            '--sysroot=' + str(sdk / 'empty-root')
        ]
        flags = [
            '-std=c11',
            '-D_GNU_SOURCE',
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
        run(
            'worker-compile',
            cc + flags + [
                '-DHELPER=2',
                '-DCOEXIST',
                '-c',
                'user/native-process/helper.c',
                '-o',
                str(work / 'worker.o')
            ]
        )
        run(
            'adapter-compile',
            cc + flags + [
                '-c',
                'user/native-memory/adapter.c',
                '-o',
                str(work / 'adapter.o')
            ]
        )
        lib = sdk / 'stage/usr/lib'
        worker = work / 'worker.elf'
        workers = {}
        for variant, cfg in [
            ('worker', None),
            ('empty-worker', 'empty_input')
        ]:
            service = work / (variant + '.a')
            worker = work / (variant + '.elf')
            cmd = [
                'rustc',
                '+1.98.0',
                '--edition=2024',
                '--target=x86_64-unknown-none',
                '--crate-type=staticlib',
                '-C',
                'opt-level=2',
                '-C',
                'panic=abort',
                '-C',
                'relocation-model=static',
                'user/native-files/service.rs',
                '--cfg',
                'writable',
                '--cfg',
                'command_runner',
                '-o',
                str(service)
            ]
            if cfg:
                cmd += ['--cfg', cfg]
            run(variant + '-service', cmd)
            run(
                variant + '-link',
                cc + [
                    '--ld-path=' + tools['lld']['path'],
                    '-nostdlib',
                    '-static',
                    '-Wl,-z,noexecstack',
                    '-Wl,--no-undefined',
                    '-Wl,-Map,' + str(work / (variant + '.map')),
                    str(lib / 'crt1.o'),
                    str(lib / 'crti.o'),
                    str(work / 'worker.o'),
                    str(work / 'adapter.o'),
                    str(service),
                    str(lib / 'libc.a'),
                    str(lib / 'crtn.o'),
                    '-o',
                    str(worker)
                ]
            )
            need(
                not run(
                    variant + '-undefined',
                    [
                        tools['nm']['path'],
                        '--undefined-only',
                        '--extern-only',
                        str(worker)
                    ]
                ).strip(),
                'worker unresolved'
            )
            need(
                not re.search(
                    b'\\bsyscall\\b',
                    run(
                        variant + '-disassembly',
                        [tools['objdump']['path'], '-d', str(worker)]
                    )
                ),
                'Linux transport'
            )
            run(
                variant + '-headers',
                [tools['readelf']['path'], '-h', '-l', str(worker)]
            )
            workers[variant] = worker
        startup_vectors = {
            'startup-simple': ['aether-run', 'bytecount', '--decimal'],
            'startup-delimiter': ['aether-run', '--', 'bytecount', '--decimal'],
            'startup-wide': ['aether-run', '--', 'bytecount', '--decimal', '', 'x' * 31],
            'startup-corrupt': ['aether-run', '--', 'bytecount', '--decimal', '', 'x' * 31],
        } if a.startup_controls else {}
        mapped_cases = [
            ('mapped-' + str(status), 'mapped-parent', 'mapped-child-' + str(status),
             1, status, status, False)
            for status in (0, 1, 2, 64, 125, 126, 127, 134, 255)
        ] if a.mapped_results else []
        if a.mapped_results:
            mapped_cases += [
                ('mapped-fault', 'mapped-parent', 'mapped-child-fault', 2, 134, 1, False),
                ('mapped-ignore-kind', 'mapped-ignore-kind', 'mapped-child-fault',
                 2, 134, 134, True),
                ('mapped-force-zero', 'mapped-force-zero', 'mapped-child-64',
                 1, 64, 0, True),
                ('mapped-cleanup', 'mapped-cleanup-parent', 'mapped-child-0',
                 1, 0, 1, True),
            ]
        if a.mapped_uncertainty:
            mapped_cases += [(name, name, 'mapped-child-0', 1, 0, witness, True)
                             for name, witness in (
                ('uncertain-admission-lost', 101), ('uncertain-admission-padding', 101),
                ('uncertain-collection-lost', 102), ('uncertain-collection-padding', 102),
                ('uncertain-collection-receipt', 102), ('uncertain-retry', 109))]
        if a.carrier_controls:
            mapped_cases += [('carrier-' + name, 'carrier-' + name, 'mapped-child-0',
                              1, 0, 112 if name == 'early-arguments' else 111, True)
                             for name in ('magic', 'count', 'reserved', 'padding',
                             'rights', 'early-arguments', 'prefix-0', 'prefix-223', 'prefix-255')]
        if a.budget_controls:
            mapped_cases += [(name, name, 'mapped-child-0', 1, 0, witness, witness != 0)
                             for name, witness in (('budget-last', 0),
                             ('budget-exhausted', 114), ('budget-overrun', 115),
                             ('budget-short', 116))]
        mapped = {row[0]: row[1:] for row in mapped_cases}
        for name in mapped:
            startup_vectors[name] = ['aether-run', '--', 'bytecount', '--decimal']
        brokers = {}
        for name, cfg in [
            ('broker', None),
            ('rejected-launch', 'reject_launch'),
            ('partial-reservation', 'partial_reservation'),
            ('short-write', 'short_write'),
            ('full-output', 'full_output'),
            ('wrong-startup', 'wrong_startup'),
            ('wrong-status', 'wrong_status'),
            ('skip-write', 'skip_write'),
            *([('allow-launch-version', 'allow_launch_version'),
               ('pad-launch-eof', 'pad_launch_eof')] if a.launch_controls else []),
            *([('fault-as-exit', 'fault_as_exit')] if a.terminal_controls else []),
            *[(name, 'runner_startup') for name in startup_vectors]
        ]:
            raw = work / (name + '.raw')
            cmd = [
                'rustc',
                '+1.98.0',
                '--edition=2024',
                '--target=x86_64-unknown-none',
                '-C',
                'opt-level=s',
                '--cfg',
                'coexist',
                '--cfg',
                'command_runner',
                '-C',
                'panic=abort',
                '-C',
                'relocation-model=static',
                '-C',
                'lto=fat',
                '-C',
                'codegen-units=1',
                '-C',
                'link-arg=-Tuser/native-process/program-linker.ld',
                '-C',
                'link-arg=--oformat=binary',
                'user/native-connections/supervisor.rs',
                '-o',
                str(raw)
            ]
            if cfg:
                cmd += ['--cfg', cfg]
            if name in mapped:
                cmd += ['--cfg', 'mapped_results']
            extra_env = None
            if name in startup_vectors:
                vector = startup_vectors[name]
                carrier = b'AERUN001' + struct.pack('<I', len(vector)) + bytes(20)
                carrier += b''.join(v.encode().ljust(32, b'\0') for v in vector)
                carrier += bytes((6 - len(vector)) * 32)
                need(len(carrier) == 224, 'carrier fixture size')
                path = work / (name + '.carrier')
                path.write_bytes(carrier)
                r.setdefault('startup_inputs', {})[name] = {
                    'argv': vector, 'sha256': sha(path)}
                extra_env = {'AETHER_RUNNER_STARTUP': str(path)}
            run(name + '-compile', cmd, extra_env)
            need(0 < raw.stat().st_size <= 8192, 'broker code bound')
            brokers[name] = raw
        entropy = os.urandom(48)
        worker = workers['worker']
        for artifact in receipt['artifacts'].values():
            need(
                sha(Path(artifact['path'])) == artifact['sha256'],
                'client changed'
            )

        def envelope(broker, parent_name, child_name):
            first = Path(receipt['artifacts'][parent_name]['path'])
            third = Path(receipt['artifacts'][child_name]['path'])
            return struct.pack(
                '<8sIIIIII',
                b'AENMX001',
                first.stat().st_size,
                worker.stat().st_size,
                third.stat().st_size,
                broker.stat().st_size,
                0,
                0
            ) + entropy + first.read_bytes() + worker.read_bytes() + third.read_bytes() + broker.read_bytes()
        cases = [
            ('positive', 'parent', None),
            ('empty-input', 'parent', None),
            ('rejected-launch', 'rejected-launch', None),
            ('partial-reservation', 'partial-reservation', None),
            ('short-write', 'parent', None),
            ('full-output', 'full-output', None),
            ('wrong-startup', 'parent', 53),
            ('wrong-status', 'parent', 53),
            ('skip-write', 'parent', 985)
        ]
        if a.bootstrap_controls:
            cases += [(name, 'parent', 53) for name in (
                'bootstrap-reference', 'bootstrap-descriptor',
                'bootstrap-rights', 'bootstrap-early-publication')]
        if a.reply_controls:
            cases += [(name, 'parent', 53) for name in (
                'reply-drop-read', 'reply-bad-read', 'reply-drop-close',
                'reply-disabled-poison')]
        if a.launch_controls:
            cases += [('launch-corpus', 'launch-corpus', None),
                      ('allow-launch-version', 'launch-corpus', 103)]
            cases += [('launch-eof-' + str(n), 'launch-eof-' + str(n), 1100 + n)
                      for n in (0, 1, 4, 16, 31, 32, 383)]
            cases += [('pad-launch-eof', 'launch-eof-383', 104)]
        if a.terminal_controls:
            cases += [('terminal-normal', 'terminal-normal-parent', None),
                      ('terminal-fault', 'terminal-fault-parent', None),
                      ('fault-as-exit', 'terminal-fault-parent', 53)]
        if a.startup_controls:
            cases += [(name, 'startup-corrupt-parent' if name == 'startup-corrupt'
                       else 'startup-parent', 53 if name == 'startup-corrupt' else None)
                      for name in startup_vectors if name not in mapped]
        cases += [(name, values[0], 970 if values[5] else None)
                  for name, values in mapped.items()]
        for name, parent_name, detail in cases:
            child_name = name if name.startswith(('bootstrap-', 'reply-')) else 'command'
            if name in ('terminal-normal', 'terminal-fault', 'fault-as-exit'):
                child_name = 'terminal-normal-command' if name == 'terminal-normal' else 'terminal-fault-command'
            if name in mapped:
                child_name = mapped[name][1]
            if name in ('startup-wide', 'startup-corrupt'):
                child_name = 'startup-observer'
            worker = workers['empty-worker' if name == 'empty-input' else 'worker']
            panic = b'native C profile rejected' if detail else None
            context = expected_panic_context(name, detail)
            if name.startswith('bootstrap-'):
                status = 97 if name == 'bootstrap-early-publication' else 95
                context = (
                    f'NATIVE terminal slot=2 generation=1 kind=1 detail={status}',
                    'NATIVE terminal slot=0 generation=1 kind=1 detail=53',
                    'NATIVE supervisor result=970 reclaimed=0',
                )
            if name.startswith('reply-'):
                status = 94 if name == 'reply-disabled-poison' else 84
                context = (
                    f'NATIVE terminal slot=2 generation=1 kind=1 detail={status}',
                    'NATIVE terminal slot=0 generation=1 kind=1 detail=53',
                    'NATIVE supervisor result=970 reclaimed=0',
                )
            if name.startswith('launch-eof-'):
                context = (f'NATIVE supervisor result={detail} reclaimed=0',)
            if name in ('allow-launch-version', 'pad-launch-eof'):
                context = (
                    f'NATIVE terminal slot=0 generation=1 kind=1 detail={detail}',
                    'NATIVE supervisor result=970 reclaimed=0',
                )
            if name == 'startup-corrupt':
                context = (
                    'NATIVE terminal slot=2 generation=1 kind=1 detail=80',
                    'NATIVE terminal slot=0 generation=1 kind=1 detail=53',
                    'NATIVE supervisor result=970 reclaimed=0',
                )
            if name == 'fault-as-exit':
                context = (
                    'NATIVE terminal slot=2 generation=1 kind=2 detail=134',
                    'NATIVE terminal slot=0 generation=1 kind=1 detail=53',
                    'NATIVE supervisor result=970 reclaimed=0',
                )
            if name in mapped and mapped[name][5]:
                _, _, kind, status, parent_status, _ = mapped[name]
                context = (
                    f'NATIVE terminal slot=2 generation=1 kind={kind} detail={status}',
                    f'NATIVE terminal slot=0 generation=1 kind=1 detail={parent_status}',
                    'NATIVE supervisor result=970 reclaimed=0',
                )
            if name.startswith('uncertain-admission-'):
                context = (
                    'NATIVE terminal slot=0 generation=1 kind=1 detail=101',
                    'NATIVE supervisor result=970 reclaimed=0',
                )
            if name.startswith('carrier-'):
                context = (f'NATIVE terminal slot=0 generation=1 kind=1 detail={mapped[name][4]}',)
            data = envelope(
                brokers[name if name in brokers else 'broker'],
                parent_name,
                child_name
            )
            dest = work / name
            dest.mkdir()
            payload = dest / 'native-c.bin'
            payload.write_bytes(data)
            run(
                name + '-kernel',
                [
                    'zig',
                    'build',
                    '-Dsmp=false',
                    '-Dnative-c-image=' + str(payload),
                    '-p',
                    str(dest),
                    '--cache-dir',
                    str(kernel / '.zig-cache'),
                    '--global-cache-dir',
                    str(kernel / '.zig-cache/global')
                ]
            )
            r['commands'].append({
                'label': name + '-smoke',
                'function': 'native_smoke.run',
                'module_sha256': sources['scripts/native_smoke.py'],
                'image': str(dest / 'aether.iso'),
                'expected_panic': panic.decode() if panic else None,
                'panic_context': list(context),
                'marker': 'AETHER NATIVE CONNECTIONS PASS'
            })
            save()
            launch = (
                'import sys,json; from pathlib import Path; '
                'sys.path.insert(0,sys.argv[1]); from native_smoke '
                'import run; p=json.loads(sys.argv[3]); '
                "run(Path(sys.argv[2]),expected_panic=p['panic'].encode()"
                " if p['panic'] else None,panic_context=tuple(x.encode() "
                "for x in p['context']),marker=b'AETHER NATIVE "
                "CONNECTIONS PASS')"
            )
            run(
                name + '-smoke-process',
                [
                    sys.executable,
                    '-c',
                    launch,
                    str(kernel / 'scripts'),
                    str(dest / 'aether.iso'),
                    json.dumps({
                        'panic': panic.decode() if panic else None,
                        'context': context
                    })
                ]
            )
            lines = (dest / 'native-serial.log').read_text().splitlines()
            if name.startswith('budget-') and panic:
                need([line for line in lines if line.startswith('NATIVE terminal')]
                     == list(context[:2]), 'budget negative terminal order')
                need([line for line in lines if line.startswith('NATIVE supervisor result=')]
                     == [context[2]], 'budget negative owner outcome')
            if name.startswith('carrier-'):
                need([line for line in lines if line.startswith('NATIVE terminal')]
                     == list(context), 'carrier published unexpected terminal')
                results = [line for line in lines if line.startswith('NATIVE supervisor result=')]
                need(len(results) == 1 and results[0] in (
                    'NATIVE supervisor result=970 reclaimed=0',
                    'NATIVE supervisor result=990 reclaimed=0'), 'carrier owner rejection stage')
                r.setdefault('carrier_owner_rejections', {})[name] = results[0]
            if name.startswith('uncertain-admission-'):
                allowed = {
                    'NATIVE terminal slot=0 generation=1 kind=1 detail=101',
                    'NATIVE terminal slot=2 generation=1 kind=1 detail=0',
                }
                need(all(line in allowed for line in lines
                         if line.startswith('NATIVE terminal')), 'unexpected admission terminal')
            if name.startswith('launch-eof-'):
                need(not any(line.startswith('NATIVE terminal') for line in lines),
                     'partial launch reached terminal')
            if panic:
                need(
                    'AETHER NATIVE CONNECTIONS PASS' not in lines,
                    'negative pass marker'
                )
            else:
                expected = expected_terminals(name)
                if name in ('terminal-normal', 'terminal-fault'):
                    kind = 1 if name == 'terminal-normal' else 2
                    expected = [
                        f'NATIVE terminal slot={slot} generation={generation} '
                        f'kind={kind if slot == 2 else 1} detail={status}'
                        for generation in (1, 2)
                        for slot, status in ((2, 134), (0, 29), (1, 17))
                    ]
                if name in mapped:
                    _, _, kind, status, parent_status, _ = mapped[name]
                    expected = [
                        f'NATIVE terminal slot={slot} generation={generation} '
                        f'kind={kind if slot == 2 else 1} detail={value}'
                        for generation in (1, 2)
                        for slot, value in ((2, status), (0, parent_status), (1, 17))
                    ]
                need(
                    [line for line in lines if line.startswith('NATIVE terminal')] == expected,
                    'terminal order mismatch'
                )
                need(
                    'NATIVE supervisor result=100 reclaimed=6' in lines,
                    'missing cleanup'
                )
            r['cases'].append({
                'case': name,
                'result': 'pass',
                'negative': panic is not None,
                'client_build_receipt_sha256': r['requester_build']['receipt_sha256'],
                'worker_sha256': sha(worker),
                'envelope_sha256': sha(payload),
                'iso_sha256': sha(dest / 'aether.iso'),
                'serial_sha256': sha(dest / 'native-serial.log')
            })
            save()
            print(name + ': PASS', flush=True)
        for name, h in sources.items():
            need(sha(kernel / name) == h, 'captured source changed: ' + name)
        for name, h in local.items():
            need(sha(Path(name)) == h, 'consumer source changed')
        for name, h in receipt['local_sources'].items():
            need(sha(Path(name)) == h, 'requester input changed')
        need(
            {str(p.relative_to(sdk)): sha(p) for p in (sdk / 'stage').rglob('*') if p.is_file()} == reference['sdk_inputs'],
            'SDK changed'
        )
        r['artifacts'] = {p.name: sha(p) for p in [
            *workers.values(),
            *brokers.values()
        ]}
        r['status'] = 'pass'
    finally:
        save()

if __name__ == '__main__':
    main()
