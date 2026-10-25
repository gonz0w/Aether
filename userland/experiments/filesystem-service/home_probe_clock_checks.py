# SPDX-License-Identifier: BSD-2-Clause
"""Selected zero-state UTC enforcement checks; imported, never starts a guest."""
from pathlib import Path
import json
import runpy
import shlex
import time

S = Path(__file__).resolve().parent
home = runpy.run_path(str(S / 'check-home-wire.py'))
SOURCE_NAMES = ('owner.rs', 'namespace-policy.rs', 'home-policy.rs', 'directory-context-policy.rs',
    'metadata-policy.rs', 'metadata-lib.rs', 'metadata.rs', 'bridge.rs', 'namespace-bridge.rs',
    'mixed-bridge.rs', 'directory-bridge.rs', 'directory-context-bridge.rs', 'service.rs',
    'channel.rs', 'bulk-service.rs', 'names-service.rs', 'home-service.rs', 'metadata-service.rs',
    'directory-context-service.rs', 'activation.rs', 'home-activation.rs', 'native-home.rs',
    'native-home-tests.rs', 'home-native-result.rs', 'directory-fixture.c', 'metadata-fixture.c',
    'home-native-fixture.c', 'home-native.h', 'native-service.h')
EXTRA_SOURCES = tuple(S / name for name in SOURCE_NAMES) + (Path(__file__).resolve(),
    home['R'] / 'docs/evidence/filesystem-bridge-2026-10-18/utc.h',
    home['R'].parent / 'user/storage/service-runtime/filesystem-engine.h') + tuple(
    home['R'].parent / 'user/storage/openzfs-volume' / name for name in (
        'zpl-context.h', 'zpl-directories.h', 'zpl-metadata.h', 'zpl-mutate.h', 'zpl-write.h',
        'zpl-read.h', 'pool-bulk-lifetime.h', 'pool-lifetime.h'))
CASES = (
    ('tests::selected_clock_accepts_only_the_half_open_window_before_first_effect', 'HOME_CLOCK_WINDOW'),
    ('tests::selected_clock_rechecks_second_bootstrap_readiness_and_request_mutation', 'HOME_CLOCK_RECHECK'))


def check(record, work, proc, tools, deadline, expect_red=False):
    require = home['require']
    frozen = {str(path): home['sha'](path) for path in EXTRA_SOURCES}
    record['home_probe_clock_sources'] = frozen
    pins = json.loads(home['PINS'].read_text())
    home['verify'](home['PINS'], home['PINS_SHA'])
    home['verify'](home['HELPER'], home['HELPER_SHA'])
    for name, tool in pins['tools'].items():
        home['verify'](tool['path'], tool['sha256'])
        tools[name] = tool
    for path, digest in pins['clang_resource_headers'].items():
        home['verify'](path, digest)
    for path, digest in pins['rust_native_libraries'].items():
        home['verify'](path, digest)
    runtime = Path('/opt/homebrew/Cellar/llvm@21/21.1.8/lib/clang/21/lib/darwin/libclang_rt.ubsan_osx_dynamic.dylib')
    home['verify'](runtime, '7bfe170b03e5b9fb208d8568250aa84c35454933c306fe322c978295874c3746')
    record['home_probe_clock_ubsan'] = dict(path=str(runtime), sha256=home['sha'](runtime))
    env = proc.clean_env(work)
    folder = work / 'home-probe-clock'
    folder.mkdir()
    flags = [*home['cfg'](True), '--cfg', 'fs_home_wire', '--cfg', 'fs_home_native',
        '--cfg', 'fs_home_activation', '--cfg', 'fs_home_probe_three']
    boundary = [arg for arg in home['COMMON'] if arg != '-Funsafe-code']
    crates = [('filesystem_metadata', 'metadata-lib.rs', []),
        ('filesystem_policy', 'owner.rs', ['filesystem_metadata']),
        ('filesystem_service', 'service.rs', ['filesystem_policy']),
        ('filesystem_bridge', 'bridge.rs', ['filesystem_metadata', 'filesystem_policy']),
        ('filesystem_activation', 'activation.rs', ['filesystem_policy', 'filesystem_service'])]

    def run(label, argv, expected=0):
        remaining = deadline - time.monotonic()
        require(remaining > 0, 'clock deadline before ' + label)
        child_env = dict(env)
        if str(argv[0]) in [tools[n]['path'] for n in ('rustc', 'rustfmt', 'clippy-driver')]:
            child_env['DYLD_LIBRARY_PATH'] = str(Path(tools['rustc']['path']).parent.parent / 'lib')
        result = proc.run(list(map(str, argv)), cwd=home['R'], env=child_env, work=work,
            label=label, timeout=min(180, remaining))
        record['rows'].append(dict(label=label, expected_exit=expected, process=result.record,
            stdout=result.stdout.decode(errors='replace')[-7000:], stderr=result.stderr.decode(errors='replace')[-7000:]))
        require(result.returncode == expected and result.record['complete'] and result.record['cleanup'] == 'complete', label)
        return result

    def deps(root, names):
        return ['-Ldependency=' + str(root), *[v for name in names for v in
            ('--extern', name + '=' + str(root / ('lib' + name + '.rlib')))]]
    sdk_headers = {}
    try:
        run('probe-clock-rustfmt', [tools['rustfmt']['path'], '--edition=2021', '--check',
            S / 'native-home.rs', S / 'native-home-tests.rs'])
        run('probe-clock-fixture-format', [tools['clang-format']['path'], '--dry-run', '--Werror',
            '--style=file:' + str(home['R'] / 'docs/quality/clang-format.yaml'), S / 'home-native-fixture.c'])
        sdk = run('probe-clock-host-sdk', ['/usr/bin/xcrun', '--show-sdk-path']).stdout.decode().strip()
        record['home_probe_clock_sdk'] = sdk
        fixture = folder / 'fixture.o'
        depfile = folder / 'fixture.d'
        run('probe-clock-fixture', [tools['clang']['path'], '--no-default-config', '-std=c17',
            '-Wall', '-Wextra', '-Werror', '-O1', '-fsanitize=undefined', '-fno-sanitize-recover=all',
            '-isysroot', sdk, '-I' + str(S), '-I' + str(home['R'].parent / 'user/storage/openzfs-volume'),
            '-I' + str(home['R'].parent / 'user/storage/service-runtime'),
            '-I' + str(home['R'] / 'docs/evidence/filesystem-bridge-2026-10-18'),
            '-MD', '-MF', depfile, '-c', S / 'home-native-fixture.c', '-o', fixture])
        sdk_headers = {p: home['sha'](p) for p in shlex.split(depfile.read_text().replace('\\\n', ' ').split(':', 1)[1])}
        record['home_probe_clock_host_headers'] = sdk_headers
        for stage, extra in [('host', []), *([] if expect_red else [('native', home['NATIVE'])])]:
            root = folder / stage
            root.mkdir()
            for name, filename, imports in crates:
                common = boundary if name in ('filesystem_bridge', 'filesystem_metadata') else home['COMMON']
                run(stage + '-probe-clock-' + name, [tools['rustc']['path'], *common, *flags, *extra,
                    *deps(root, imports), '--crate-type=lib', '--crate-name=' + name, S / filename,
                    '-o', root / ('lib' + name + '.rlib')])
            imports = [name for name, _, _ in crates]
            for compiler in ('rustc', 'clippy-driver'):
                if stage == 'host':
                    run(compiler + '-probe-clock-tests-build', [tools[compiler]['path'], *boundary,
                        *flags, *deps(root, imports), '--test', S / 'native-home.rs',
                        '-Clink-arg=' + str(fixture), '-Clink-arg=' + str(runtime), '-o', root / (compiler + '-tests')])
                else:
                    artifact = root / (compiler + '-entry.rlib')
                    run(compiler + '-probe-clock-native', [tools[compiler]['path'], *boundary, *flags,
                        *extra, *deps(root, imports), '--crate-type=lib', S / 'native-home.rs', '-o', artifact])
                    record.setdefault('home_probe_clock_libraries', {})[compiler] = home['sha'](artifact)
            if stage == 'host':
                for case, marker in CASES:
                    observed = run('probe-clock-' + case.split('::')[-1], [root / 'rustc-tests', '--exact',
                        case, '--nocapture'], expected=101 if expect_red else 0)
                    require(case.encode() in observed.stdout and (b'1 failed' if expect_red else b'1 passed') in observed.stdout,
                        'named selected clock method')
                    if expect_red:
                        require(marker.encode() in observed.stderr, 'named expected clock semantic red')
        record['home_probe_clock'] = dict(selection='fs_home_probe_three', utc_min=1791290040,
            utc_max=1791290100, half_open=True, methods=[case for case, _ in CASES],
            expected_red=expect_red, production_counter=False, native_executed=False)
    finally:
        for path, digest in {**frozen, **sdk_headers}.items():
            home['verify'](path, digest)
        record['home_probe_clock_final_input_verification'] = 'pass'
