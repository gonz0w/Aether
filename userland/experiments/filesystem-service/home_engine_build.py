# SPDX-License-Identifier: BSD-2-Clause
"""Build current selected AF09 Rust objects in place; no engine import or guest."""
from pathlib import Path
import hashlib
import json
import runpy
import time

S = Path(__file__).resolve().parent
R = S.parents[1]
PROFILE = tuple('fs_' + name for name in ('namespace', 'lifetimes', 'mixed', 'wait', 'bulk',
    'runtime', 'activation', 'names', 'directories', 'metadata', 'directory_contexts',
    'home', 'home_wire', 'home_native', 'home_activation', 'home_probe_three'))
DRAIN_PROFILE = (*PROFILE[:-1], 'fs_af09_drain')
DRAIN_CASES = ('file_prefix', 'exec_prefix', 'fork_prefix', 'stream', 'no_ack',
               'partial_ack', 'exit_deadline', 'pending_fragment')
CRATES = (
    ('filesystem_metadata', 'metadata-lib.rs', ()),
    ('filesystem_policy', 'owner.rs', ('filesystem_metadata',)),
    ('filesystem_bridge', 'bridge.rs', ('filesystem_metadata', 'filesystem_policy')),
    ('filesystem_service', 'service.rs', ('filesystem_policy',)),
    ('filesystem_activation', 'activation.rs', ('filesystem_policy', 'filesystem_service')))
BASE = ('--edition=2021', '--target=x86_64-unknown-none', '-Dwarnings',
    '-Dunsafe_op_in_unsafe_fn', '-Cpanic=abort', '-Copt-level=2',
    '-Crelocation-model=static', '-Ccodegen-units=1', '-Cno-redzone=yes')
OLD = frozenset(('aether_fs_service_run', 'aether_fs_namespace_run', 'aether_fs_mixed_run',
    'aether_fs_mixed_wait_run', 'aether_fs_bulk_run', 'aether_fs_runtime_run',
    'aether_fs_activation_run', 'aether_fs_names_run', 'aether_fs_directories_run',
    'aether_fs_metadata_run', 'aether_fs_engine_run', 'aether_fs_engine_import',
    'aether_fs_launch_serve'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def drain_selection(drain_case):
    if not isinstance(drain_case, str) or drain_case not in ('none', *DRAIN_CASES):
        raise ValueError('AF09 drain case must be none or one exact selected case')
    return 0 if drain_case == 'none' else DRAIN_CASES.index(drain_case) + 1


def validate_profile(profile, *, drain_case='none'):
    selected = DRAIN_PROFILE if drain_selection(drain_case) else PROFILE
    if tuple(profile) != selected:
        raise ValueError('AF09 profile must match every explicit selected flag')
    return selected


def validate_symbols(service, launch):
    rows = [[line.split() for line in text.splitlines() if line.split()]
            for text in (service, launch)]
    for index, names in ((0, ('aether_fs_home_run',)),
                         (1, ('main', 'aether_fs_home_launch_serve'))):
        for name in names:
            wanted = [row for row in rows[index] if row[-1] == name]
            wrong = [row for row in rows[1 - index] if row[-1] == name]
            if len(wanted) != 1 or len(wanted[0]) != 3 or wanted[0][1] != 'T' or wrong:
                raise ValueError('AF09 strong definition/origin: ' + name)
    if any(row[-1] in OLD for group in rows for row in group):
        raise ValueError('AF09 old service/launch symbol')


def build(work, proc, tools, deadline, record, *, drain_case='none'):
    """Return service/launch object Paths; caller owns work and cleanup.

    This follows the existing five-crate native metadata-service object recipe.
    The original volume static library, linked by the complete C engine, remains
    the sole panic/runtime provider. This partial object creates no panic stub or
    alternate native-service entry and does not reuse an older service object.
    """
    case_id = drain_selection(drain_case)
    profile = validate_profile(DRAIN_PROFILE if case_id else PROFILE, drain_case=drain_case)
    folder = work / 'home-engine-rust'
    folder.mkdir()
    pins_path = R / 'docs/evidence/filesystem-transport-2026-10-19/inputs.json'
    if sha(pins_path) != 'f200c7507b7fc300f9d4303191b0196acfa35dc7f9cffecd51e6a21e7933c82d':
        raise ValueError('AF09 native Rust dependency manifest')
    pins = json.loads(pins_path.read_text())
    for name in ('rustc', 'clippy-driver', 'lld', 'nm', 'readelf'):
        selected = pins['tools'][name]
        if sha(selected['path']) != selected['sha256']:
            raise ValueError('AF09 native Rust tool: ' + name)
        if name in tools and tools[name] != selected:
            raise ValueError('AF09 supplied native tool differs: ' + name)
        tools[name] = selected
    libraries = pins['rust_native_libraries']
    if not any('libcore-' in name for name in libraries) or not any('libcompiler_builtins-' in name for name in libraries):
        raise ValueError('AF09 native core/compiler-builtins unavailable')
    for path, digest in libraries.items():
        if sha(path) != digest:
            raise ValueError('AF09 native Rust library changed: ' + path)
    # The imported checks enumerate the exact production module graph without
    # copying the source tree or consulting archived per-run directories.
    graph = runpy.run_path(str(S / 'home_probe_clock_checks.py'))
    source_paths = [p for p in graph['EXTRA_SOURCES'] if p.suffix == '.rs']
    source_paths += [S / name for name in ('launch-home-owner.rs', 'home-native-result.rs',
        'home_engine_build.py', 'home_engine_build_tests.py', 'check-metadata-service.py',
        'home_probe_clock_checks.py', 'check-home-wire.py')]
    sources = {str(p): sha(p) for p in source_paths}
    inputs = {**sources, **libraries, str(pins_path): sha(pins_path),
        **{tools[name]['path']: tools[name]['sha256'] for name in ('rustc', 'clippy-driver', 'lld', 'nm', 'readelf')}}
    retained = record.setdefault('inputs', {})
    for path, digest in inputs.items():
        if not Path(path).is_absolute() or path in retained and retained[path] != digest:
            raise ValueError('AF09 inconsistent native Rust input: ' + path)
        retained[path] = digest
    flags = [*BASE, *[arg for name in profile for arg in ('--cfg', name)]]
    record['home_engine_rust'] = dict(profile=list(profile), flags=flags, sources=sources,
        tools={name: dict(tools[name]) for name in ('rustc', 'clippy-driver', 'lld', 'nm', 'readelf')},
        native_libraries=dict(libraries), service_result_bytes=320, launch_state_bytes=384,
        panic_runtime='Original user/storage/openzfs-volume/volume.rs via the complete engine archive; no new stub.',
        inputs_manifest=dict(path=str(pins_path), sha256=sha(pins_path)))
    if case_id:
        record['home_engine_rust'].update(drain_case=drain_case, drain_case_id=case_id)
    env = proc.clean_env(work)

    def run(label, argv):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError('AF09 native build deadline before ' + label)
        child_env = dict(env)
        if str(argv[0]) in [tools[name]['path'] for name in ('rustc', 'clippy-driver')]:
            child_env['DYLD_LIBRARY_PATH'] = str(Path(tools['rustc']['path']).parent.parent / 'lib')
        result = proc.run(list(map(str, argv)), cwd=R, env=child_env, work=work,
            label=label, timeout=min(180, remaining))
        record.setdefault('rows', []).append(dict(label=label, expected_exit=0, process=result.record,
            stdout=result.stdout.decode(errors='replace')[-7000:], stderr=result.stderr.decode(errors='replace')[-7000:]))
        if result.returncode != 0 or not result.record['complete'] or result.record['cleanup'] != 'complete':
            raise RuntimeError(label)
        return result

    def deps(root, names):
        return ['-Ldependency=' + str(root), *[arg for name in names for arg in
            ('--extern', name + '=' + str(root / ('lib' + name + '.rlib')))]]

    try:
        for stage, compiler in (('rustc', 'rustc'), ('clippy', 'clippy-driver')):
            root = folder / stage
            root.mkdir()
            for name, filename, imports in CRATES:
                safe = ['-Funsafe-code'] if name in ('filesystem_policy', 'filesystem_service', 'filesystem_activation') else []
                run(stage + '-home-engine-' + name, [tools[compiler]['path'], *flags, *safe,
                    *deps(root, imports), '--crate-name=' + name, '--crate-type=lib', S / filename,
                    '--emit=link=' + str(root / ('lib' + name + '.rlib')) + ',obj=' + str(root / (name + '.o'))])
            run(stage + '-home-engine-entry', [tools[compiler]['path'], *flags,
                *deps(root, [name for name, _, _ in CRATES]), '--crate-name=filesystem_home_entry',
                '--crate-type=lib', '--emit=obj', S / 'native-home.rs', '-o', root / 'entry.o'])
            run(stage + '-home-engine-launch', [tools[compiler]['path'], *flags,
                '--crate-name=filesystem_home_launch', '--crate-type=lib', '--emit=obj',
                S / 'launch-home-owner.rs', '-o', root / 'launch-home-owner.o'])
        root = folder / 'rustc'
        service = folder / 'filesystem-home.o'
        launch = root / 'launch-home-owner.o'
        object_inputs = [root / (name + '.o') for name, _, _ in CRATES] + [root / 'entry.o']
        link_map = folder / 'filesystem-home.map'
        run('home-engine-rust-partial-link', [tools['lld']['path'], '-r', '-Map=' + str(link_map),
            *object_inputs, '-o', service])
        service_symbols = run('home-engine-rust-service-symbols', [tools['nm']['path'], '--defined-only', service]).stdout.decode()
        launch_symbols = run('home-engine-rust-launch-symbols', [tools['nm']['path'], '--defined-only', launch]).stdout.decode()
        validate_symbols(service_symbols, launch_symbols)
        imports = {}
        for name, path in (('service', service), ('launch', launch)):
            symbols = run('home-engine-rust-' + name + '-imports', [tools['nm']['path'], '--undefined-only', path]).stdout.decode()
            imports[name] = [line.split()[-1] for line in symbols.splitlines() if line.split()]
            if any(symbol in OLD for symbol in imports[name]):
                raise ValueError('AF09 old service/launch import')
            elf = run('home-engine-rust-' + name + '-elf', [tools['readelf']['path'], '-h', path]).stdout
            if b'ELF64' not in elf or b'X86-64' not in elf or b'REL (Relocatable file)' not in elf:
                raise ValueError('AF09 native object target/type: ' + name)
        map_text = link_map.read_text()
        if 'entry.o:(.text.aether_fs_home_run)' not in map_text:
            raise ValueError('AF09 actual home entry object origin')
        artifact_rows = {name: dict(path=str(path), sha256=sha(path), bytes=path.stat().st_size)
            for name, path in (('service', service), ('launch', launch))}
        record['home_engine_rust'].update(artifacts=artifact_rows, imports=imports,
            partial_inputs={str(p): sha(p) for p in object_inputs}, link_map_sha256=sha(link_map),
            entry_origin=str(root / 'entry.o'), native_executed=False)
        result = dict(service=service, launch=launch, sources=sources, flags=flags,
            profile=list(profile), dependencies=dict(libraries), artifacts=artifact_rows)
        if case_id:
            result.update(drain_case=drain_case, drain_case_id=case_id)
        return result
    finally:
        for path, digest in inputs.items():
            if sha(path) != digest:
                raise ValueError('AF09 native Rust input changed during build: ' + path)
        record['home_engine_rust']['final_input_verification'] = 'pass'
