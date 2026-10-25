# SPDX-License-Identifier: BSD-2-Clause
"""Imported native-entry/launch checks; caller owns frozen inputs and cleanup."""
from pathlib import Path
import runpy
import re
import shutil
import time

S = Path(__file__).resolve().parent
home = runpy.run_path(str(S / 'check-home-wire.py'))
EXTRA_SOURCES = tuple(S / name for name in (
    'home-native-result.rs', 'native-home.rs', 'native-home-tests.rs',
    'launch-home-owner.rs', 'launch-home-owner-tests.rs', 'home-native-fixture.c',
    'directory-fixture.c', 'metadata-fixture.c', 'home-native.h', 'native-service.h', 'home_native_entry_checks.py'))
EXTRA_SOURCES += (home['R'].parent / 'user/storage/service-runtime/filesystem-engine.h',)


def check(record, work, proc, tools, deadline):
    require = home['require']
    env = proc.clean_env(work)
    env['DYLD_LIBRARY_PATH'] = str(Path(tools['rustc']['path']).parent.parent / 'lib')
    selected = [*home['cfg'](True), '--cfg', 'fs_home_wire', '--cfg', 'fs_home_native', '--cfg', 'fs_home_activation']
    safe = home['COMMON']
    boundary = [f for f in safe if f != '-Funsafe-code']
    crates = [('filesystem_metadata', 'metadata-lib.rs', []),
              ('filesystem_policy', 'owner.rs', ['filesystem_metadata']),
              ('filesystem_service', 'service.rs', ['filesystem_policy']),
              ('filesystem_bridge', 'bridge.rs', ['filesystem_metadata', 'filesystem_policy']),
              ('filesystem_activation', 'activation.rs', ['filesystem_policy', 'filesystem_service'])]

    def run(label, argv, expected=0):
        remaining = deadline - time.monotonic()
        require(remaining > 0, 'suite deadline before ' + label)
        child_env = dict(env)
        if str(argv[0]) not in [tools[name]['path'] for name in ('rustc', 'rustfmt', 'clippy-driver')]:
            child_env.pop('DYLD_LIBRARY_PATH', None)
        result = proc.run(list(map(str, argv)), cwd=home['R'], env=child_env, work=work,
                          label=label, timeout=min(60, remaining))
        record['rows'].append(dict(label=label, expected_exit=expected, process=result.record,
            stdout=result.stdout.decode(errors='replace')[-7000:], stderr=result.stderr.decode(errors='replace')[-7000:]))
        require(result.returncode == expected and result.record['complete'] and result.record['cleanup'] == 'complete', label)
        return result

    def deps(folder, names):
        return ['-Ldependency=' + str(folder), *[v for name in names for v in
            ('--extern', name + '=' + str(folder / ('lib' + name + '.rlib')))]]

    run('home-entry-rustfmt', [tools['rustfmt']['path'], '--edition=2021', '--check',
        *[p for p in EXTRA_SOURCES if p.suffix == '.rs']])
    run('home-entry-c-format', [tools['clang-format']['path'], '--dry-run', '--Werror',
        '--style=file:' + str(home['R'] / 'docs/quality/clang-format.yaml'), S / 'home-native-fixture.c'])
    sdk = run('home-entry-host-sdk', ['/usr/bin/xcrun', '--show-sdk-path']).stdout.decode().strip()
    ubsan = Path('/opt/homebrew/Cellar/llvm@21/21.1.8/lib/clang/21/lib/darwin/libclang_rt.ubsan_osx_dynamic.dylib')
    require(home['sha'](ubsan) == '7bfe170b03e5b9fb208d8568250aa84c35454933c306fe322c978295874c3746', 'pinned home entry UBSan')
    record['home_entry_ubsan'] = dict(path=str(ubsan), sha256=home['sha'](ubsan))
    fixture = work / 'home-entry-fixture.o'
    run('home-entry-typed-fixture', [tools['clang']['path'], '-std=c17', '-Wall', '-Wextra', '-Werror',
        '-O1', '-fsanitize=undefined', '-fno-sanitize-recover=all',
        '-isysroot', sdk, '-I' + str(home['R'].parent / 'user/storage/openzfs-volume'),
        '-I' + str(home['R'] / 'docs/evidence/filesystem-bridge-2026-10-18'),
        '-I' + str(S), '-I' + str(home['R'].parent / 'user/storage/service-runtime'),
        '-c', S / 'home-native-fixture.c', '-o', fixture])
    artifacts = record.setdefault('home_entry_artifacts', {})
    for stage, extra in (('host', []), ('native', home['NATIVE'])):
        folder = work / ('home-entry-' + stage)
        folder.mkdir()
        for name, filename, imports in crates:
            flags = boundary if name in ('filesystem_bridge', 'filesystem_metadata') else safe
            run(stage + '-home-entry-' + name, [tools['rustc']['path'], *flags, *selected, *extra,
                *deps(folder, imports), '--crate-type=lib', '--crate-name=' + name, '-Cmetadata=' + folder.name,
                S / filename, '-o', folder / ('lib' + name + '.rlib')])
        imports = [name for name, _, _ in crates]
        for filename in ('native-home.rs', 'launch-home-owner.rs'):
            for compiler in (() if stage == 'host' else ('rustc', 'clippy-driver')):
                artifact = folder / (compiler + '-' + filename + '.rlib')
                run(stage + '-' + compiler + '-' + filename, [tools[compiler]['path'], *boundary,
                    *selected, *extra, *deps(folder, imports), '--crate-type=lib', S / filename, '-o', artifact])
                artifacts[str(artifact.relative_to(work))] = home['sha'](artifact)
            if stage == 'host':
                for compiler in ('rustc', 'clippy-driver'):
                    binary = folder / (compiler + '-' + filename + '-tests')
                    run(compiler + '-home-tests-build-' + filename, [tools[compiler]['path'], *boundary,
                        *selected, *deps(folder, imports), '--test', S / filename,
                        *(['-Clink-arg=' + str(fixture), '-Clink-arg=' + str(ubsan)] if filename == 'native-home.rs' else []), '-o', binary])
                tested = run('home-tests-' + filename, [folder / ('rustc-' + filename + '-tests'), '--test-threads=1'])
                count = 19 if filename == 'native-home.rs' else 4
                require((str(count) + ' passed; 0 failed').encode() in tested.stdout, 'named home methods executed: ' + filename)
            else:
                artifact = folder / (filename + '.o')
                run('home-target-object-' + filename, [tools['rustc']['path'], *boundary, *selected,
                    *extra, *deps(folder, imports), '--crate-type=lib', '--emit=obj', S / filename, '-o', artifact])
                artifacts[str(artifact.relative_to(work))] = home['sha'](artifact)
                assembly = folder / (filename + '.s')
                run('home-target-local-frames-' + filename, [tools['rustc']['path'], *boundary, *selected,
                    *extra, *deps(folder, imports), '--crate-type=lib', '--emit=asm', S / filename, '-o', assembly])
                frames = []
                function = ''
                for line in assembly.read_text().splitlines():
                    if re.match(r'^[A-Za-z_][^\s:]*:', line):
                        function = line.split(':', 1)[0]
                    if re.search(r'\b(pushq|popq)\b|\b(subq|addq)\b[^,]*,\s*%rsp', line):
                        frames.append(dict(function=function, instruction=line.strip()))
                record.setdefault('home_entry_local_frames', {})[filename] = dict(
                    assembly_sha256=home['sha'](assembly), adjustments=frames,
                    scope='Optimized target object local stack adjustments; not native peak or complete engine fit.')
                symbols = run('home-target-symbols-' + filename, [tools['nm']['path'], '-g', artifact])
                expected = b'aether_fs_home_run' if filename == 'native-home.rs' else b'aether_fs_home_launch_serve'
                require(expected in symbols.stdout, 'distinct selected symbol ' + filename)
    host = work / 'home-entry-host'
    for filename, marker in (('native-home.rs', b'home native entry requires'), ('launch-home-owner.rs', b'home executable owner requires')):
        rejected = run('home-missing-selection-' + filename, [tools['rustc']['path'], *boundary,
            *deps(host, [name for name, _, _ in crates]), '--crate-type=lib', S / filename, '-o', work / 'absent.rlib'], expected=1)
        require(marker in rejected.stderr, 'explicit native selection required')
    controls = [
        ('first-receipt', 'let outcome = retain(&mut out.create, observed);',
         'out.mkdir = BootstrapReceipt::default(); let outcome = retain(&mut out.create, observed);',
         'tests::create_failures_preserve_first_obligation_and_original_typed_result', 'HOME_FIRST_RECEIPT'),
        ('lost-uncertainty', 'Err(_) => receipt.provider = 2,', 'Err(_) => receipt.provider = 0,',
         'tests::typed_lost_observation_flattens_uncertainty_and_requires_ordering', 'HOME_LOST_UNCERTAINTY'),
        ('monotonic-order', 'if out.create.requires_ordering() {',
         'out.flags &= !ORDERED; if out.create.requires_ordering() {',
         'tests::create_failures_preserve_first_obligation_and_original_typed_result', 'HOME_ORDER_MONOTONIC'),
    ]
    record['home_entry_controls'] = []
    original = (S / 'native-home.rs').read_text()
    for label, before, after, case, marker in controls:
        require(original.count(before) == 1, 'unique native entry control: ' + label)
        folder = work / ('home-entry-control-' + label)
        folder.mkdir()
        for filename in ('native-home.rs', 'native-home-tests.rs', 'home-native-result.rs'):
            shutil.copy2(S / filename, folder / filename)
        (folder / 'native-home.rs').write_text(original.replace(before, after, 1))
        run(label + '-entry-control-build', [tools['rustc']['path'], *boundary, *selected,
            *deps(host, [name for name, _, _ in crates]), '--test', folder / 'native-home.rs',
            '-Clink-arg=' + str(fixture), '-Clink-arg=' + str(ubsan), '-o', folder / 'tests'])
        rejected = run(label + '-entry-control-rejected', [folder / 'tests', '--exact', case, '--nocapture'], expected=101)
        require(case.encode() in rejected.stdout and b'1 failed' in rejected.stdout and marker.encode() in rejected.stderr,
            'named native entry semantic control: ' + label)
        record['home_entry_controls'].append(dict(label=label, before=before, after=after, test=case,
            marker=marker, sha256=home['sha'](folder / 'native-home.rs')))
    record['home_entry_sources'] = {str(path): home['sha'](path) for path in EXTRA_SOURCES}
    record.setdefault('finalverify_extra_sources', []).extend(map(str, EXTRA_SOURCES))
