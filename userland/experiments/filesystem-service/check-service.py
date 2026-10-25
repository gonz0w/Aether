# SPDX-License-Identifier: BSD-2-Clause
"""Owned offline checks for the private bounded filesystem connection."""
import hashlib
import ast
import json
from pathlib import Path
import sys
import tempfile
import types

R = Path(__file__).resolve().parents[2]
S = Path(__file__).resolve().parent
P = R / 'docs/evidence/filesystem-transport-2026-10-19'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


inputs = json.loads((P / 'inputs.json').read_text())
for name, digest in inputs['producer_files'].items():
    assert sha(P / 'producer' / name) == digest, name
for tool in inputs['tools'].values():
    assert sha(Path(tool['path'])) == tool['sha256']
for name, digest in inputs['rust_native_libraries'].items():
    assert sha(Path(name)) == digest, name
for name, digest in inputs['clang_resource_headers'].items():
    assert sha(Path(name)) == digest, name
helper = R / 'experiments/command-runner/process.py'
assert sha(helper) == '9f0c0464c10fa23bfc7c3c91fe26b04e5ab063ca058eeb6d41542d98c6186e4e'
proc = types.ModuleType('owned')
exec(compile(helper.read_bytes(), str(helper), 'exec'), proc.__dict__)
W = Path(tempfile.mkdtemp(prefix='filesystem-service-', dir=R / 'build'))
env = proc.clean_env(W)
tools = inputs['tools']
rust = Path(tools['rustc']['path']).parent
lifetimes = '--lifetimes' in sys.argv[1:]
rows = []
record = {'status': 'running', 'root': str(W), 'rows': rows,
          'python': sys.version, 'driver_sha256': sha(Path(__file__)),
          'python_executable': sys.executable,
          'python_sha256': sha(Path(sys.executable)),
          'input_manifest_sha256': sha(P / 'inputs.json')}


def run(name, argv, expected=0, rust_env=False, timeout=60):
    selected = dict(env)
    if rust_env:
        selected['DYLD_LIBRARY_PATH'] = str(rust.parent / 'lib')
    result = proc.run([str(a) for a in argv], cwd=R, env=selected,
                      work=W, label=name, timeout=timeout)
    rows.append({'name': name, 'expected': expected, 'record': result.record})
    assert (result.returncode == expected and result.record['complete']
            and result.record['cleanup'] == 'complete'), name
    return result


try:
    # Execute the isolated actual owner guard, without importing sibling code or
    # running a builder. This is a precondition witness, not a native test.
    tree = ast.parse((P / 'producer/scripts/openzfs_volume.py').read_text())
    build = next(node for node in tree.body
                 if isinstance(node, ast.FunctionDef) and node.name == 'build')
    guard = next(node for node in build.body if isinstance(node, ast.If)
                 and ast.unparse(node.test) == 'pool_fs_bridge is not None')
    guard_code = compile(ast.Module(body=[guard], type_ignores=[]),
                         'pinned-owner-exclusive-guard', 'exec')
    try:
        exec(guard_code, dict(pool_fs_bridge=object(), pool_zpl_write=True,
             pool_namespace=True, pool=True, diagnostics=True,
             namespace_ipc=True, pool_zpl_recover=False,
             pool_zpl_repeat=False, pool_zpl_stages=False))
    except ValueError as blocked:
        assert str(blocked) == 'filesystem bridge requires exclusive single-write namespace build'
        record['owner_guard'] = str(blocked)
    else:
        raise AssertionError('owner no longer rejects this mixed profile')
    sources = [S / n for n in ('service.rs', 'service-tests.rs', 'channel.rs',
                               'native-service.rs', 'native-service-tests.rs')]
    if lifetimes:
        sources.append(S / 'lifetime-service-tests.rs')
    if '--format' in sys.argv[1:]:
        run('format', [tools['rustfmt']['path'], '--edition=2021',
                       '--config-path', R / 'docs/vendor/aether-approved-drafts/2026-09-05/drafts/coding-v0.1.0/configs/rustfmt.toml',
                       *sources], rust_env=True)
        run('c-format', [tools['clang-format']['path'], '-i',
                         '--style=file:docs/quality/clang-format.yaml',
                         S / 'native-service.h'])
    all_sources = [*sources, S / 'owner.rs', S / 'bridge.rs',
                   S / 'bridge-fixture.c', S / 'native-service.h', Path(__file__)]
    record['sources'] = {str(p.relative_to(R)): sha(p) for p in all_sources}
    snapshot = W / 'sources'
    snapshot.mkdir()
    for source in all_sources:
        (snapshot / source.name).write_bytes(source.read_bytes())
    run('format-check', [tools['rustfmt']['path'], '--edition=2021',
                         '--check', *sources], rust_env=True)
    run('c-format-check', [tools['clang-format']['path'], '--dry-run',
                           '--Werror', '--style=file:docs/quality/clang-format.yaml',
                           S / 'native-service.h'])
    common = ['--edition=2021', '-Dwarnings', '-Dunsafe_op_in_unsafe_fn']
    run('host-policy', [tools['rustc']['path'], *common, '-Funsafe-code',
                        '--crate-name=filesystem_policy', '--crate-type=lib',
                        S / 'owner.rs', '-o', W / 'libfilesystem_policy.rlib'],
        rust_env=True)
    external = ['--extern', 'filesystem_policy=' + str(W / 'libfilesystem_policy.rlib')]
    for name, tool, tests in [('library', 'rustc', False),
                               ('clippy', 'clippy-driver', False),
                               ('test-build', 'rustc', True),
                               ('clippy-tests', 'clippy-driver', True)]:
        args = ['--test'] if tests else ['--crate-type=lib']
        output = W / 'libfilesystem_service.rlib' if name == 'library' else W / name
        run(name, [tools[tool]['path'], *common, '-Funsafe-code', *external,
                   '--crate-name=filesystem_service', *args, S / 'service.rs',
                   '-o', output], rust_env=True)
    result = run('tests', [W / 'test-build', '--test-threads=1'], timeout=30)
    assert '11 passed; 0 failed' in result.stdout.decode()
    bridge_packet = R / 'docs/evidence/filesystem-bridge-2026-10-18'
    bridge_inputs = bridge_packet / 'inputs.json'
    assert sha(bridge_inputs) == inputs['prior_bridge_inputs_sha256']
    prior = json.loads(bridge_inputs.read_text())
    for name, digest in prior['producer_files'].items():
        source = (bridge_packet / 'utc.h' if name == 'userland/utc.h'
                  else bridge_packet / 'producer' / name)
        assert sha(source) == digest, name
    run('host-c-fixture', [tools['clang']['path'], '-std=c17', '-Wall',
         '-Wextra', '-Werror', '-I' + str(bridge_packet),
         '-I' + str(bridge_packet / 'producer/user/storage/openzfs-volume'),
         '-c', S / 'bridge-fixture.c', '-o', W / 'fixture.o'])
    run('host-bridge', [tools['rustc']['path'], *common, *external,
         '--crate-name=filesystem_bridge', '--crate-type=lib', S / 'bridge.rs',
         '-o', W / 'libfilesystem_bridge.rlib'], rust_env=True)
    entry_deps = [*external, '-Ldependency=' + str(W), '--extern',
         'filesystem_bridge=' + str(W / 'libfilesystem_bridge.rlib'), '--extern',
         'filesystem_service=' + str(W / 'libfilesystem_service.rlib')]
    for label, tool in [('entry-test-build', 'rustc'),
                         ('entry-clippy-tests', 'clippy-driver')]:
        run(label, [tools[tool]['path'], *common, *entry_deps, '--test',
             S / 'native-service.rs', '-Clink-arg=' + str(W / 'fixture.o'),
             '-o', W / label], rust_env=True)
    result = run('entry-tests', [W / 'entry-test-build', '--test-threads=1'],
                 timeout=30)
    assert '4 passed; 0 failed' in result.stdout.decode()
    # Compiling semantic omissions must fail assertions, not merely fail to build.
    mutants = {
        'version': ('raw[..8] != MAGIC[..]', 'false'),
        'epoch': ('word(raw, 2) != self.epoch', 'false'),
        'attenuation': ('Rights::new(bits)?', '{ let _ = bits; Rights::ALL }'),
        'retirement': ('owner.shutdown();', 'let _ = ();'),
        'token-reuse': ('let id = self.next;', 'let id = 2;'),
        'input-zero': ('bytes.fill(0);', 'let _ = &bytes;'),
        'budget': ('for _ in 0..REQUESTS {', 'for _ in 0..REQUESTS + 1 {'),
    }
    for name, (old, new) in mutants.items():
        m = W / name
        m.mkdir()
        for f in ('service.rs', 'service-tests.rs', 'channel.rs'):
            text = (S / f).read_text()
            if old in text:
                text = text.replace(old, new)
            (m / f).write_text(text)
        assert any(old in (S / f).read_text() for f in
                   ('service.rs', 'channel.rs')), name
        run('mutant-build-' + name, [tools['rustc']['path'], *common,
             *external, '--test', m / 'service.rs', '-o', m / 'tests'],
            rust_env=True)
        failed = run('mutant-' + name, [m / 'tests', '--test-threads=1'],
                     expected=101, timeout=30)
        assert 'test result: FAILED.' in failed.stdout.decode(), name
    if lifetimes:
        h = W / 'lifetimes-host'
        h.mkdir()
        flags = [*common, '--cfg', 'fs_lifetimes']
        run('lifetime-c-fixture', [tools['clang']['path'], '-std=c17', '-Wall',
            '-Wextra', '-Werror', '-DFS_LIFETIMES=1', '-I' + str(bridge_packet),
            '-I' + str(bridge_packet / 'producer/user/storage/openzfs-volume'),
            '-c', S / 'bridge-fixture.c', '-o', h / 'fixture.o'])
        def lifetime_host(directory, label, clippy=True):
            for crate, source, deps in [
                ('filesystem_policy', 'owner.rs', []),
                ('filesystem_bridge', 'bridge.rs', ['filesystem_policy']),
                ('filesystem_service', 'service.rs', ['filesystem_policy']),
            ]:
                dependencies = ['-Ldependency=' + str(directory)]
                for dep in deps:
                    dependencies += ['--extern', dep + '=' + str(directory / ('lib' + dep + '.rlib'))]
                run(label + '-' + crate, [tools['rustc']['path'], *flags,
                    *dependencies, '--crate-name=' + crate, '--crate-type=lib',
                    directory / source if (directory / source).exists() else S / source,
                    '-o', directory / ('lib' + crate + '.rlib')], rust_env=True)
            dependencies = ['-Ldependency=' + str(directory)]
            for dep in ('filesystem_policy', 'filesystem_bridge', 'filesystem_service'):
                dependencies += ['--extern', dep + '=' + str(directory / ('lib' + dep + '.rlib'))]
            for kind, compiler in [('tests', 'rustc'), ('clippy', 'clippy-driver')]:
                if kind == 'clippy' and not clippy:
                    continue
                run(label + '-' + kind, [tools[compiler]['path'], *flags,
                    *dependencies, '--test',
                    directory / 'native-service.rs' if (directory / 'native-service.rs').exists() else S / 'native-service.rs',
                    '-Clink-arg=' + str(h / 'fixture.o'), '-o', directory / kind], rust_env=True)
        lifetime_host(h, 'lifetime')
        observed = run('lifetime-tests', [h / 'tests', '--test-threads=1'], timeout=30)
        assert '7 passed; 0 failed' in observed.stdout.decode()
        variants = {
            'read-verification': [('bridge.rs', 'if !verified {', 'if { let _ = verified; false } {')],
            'retire-error': [('bridge.rs', 'if retired != 0 {', 'if false {')],
            'reopen-error': [('bridge.rs', 'if reopened != 0 || next.is_null() {', 'if { let _ = reopened; false } {')],
            'aggregate-budget': [('owner.rs', 'self.writes += 1;', 'self.writes += 0;'),
                                 ('bridge.rs', 'self.writes += 1;', 'self.writes += 0;')],
        }
        for label, replacements in variants.items():
            directory = W / ('lifetime-omission-' + label)
            directory.mkdir()
            for name in ('owner.rs', 'bridge.rs', 'service.rs', 'native-service.rs',
                         'lifetime-service-tests.rs', 'channel.rs'):
                text = (S / name).read_text()
                for selected, old, new in replacements:
                    if selected == name:
                        assert text.count(old) == 1, (label, old)
                        text = text.replace(old, new, 1)
                (directory / name).write_text(text)
            lifetime_host(directory, 'lifetime-omission-' + label, clippy=False)
            rejected = run('lifetime-reject-' + label,
                           [directory / 'tests', '--test-threads=1'], expected=101, timeout=30)
            assert 'test result: FAILED.' in rejected.stdout.decode()
            assert 'panicked at' in rejected.stdout.decode() + rejected.stderr.decode()
        record['lifetime_entry_tests'] = 7
        record['lifetime_semantic_omissions'] = len(variants)
    native = ['--target=x86_64-unknown-none', '-Cpanic=abort',
              '-Copt-level=2', '-Crelocation-model=static', '-Ccodegen-units=1']
    if lifetimes:
        native += ['--cfg', 'fs_lifetimes']
    n = W / 'native'
    n.mkdir()
    for crate, source, deps in [
        ('filesystem_policy', 'owner.rs', []),
        ('filesystem_service', 'service.rs', ['filesystem_policy']),
        ('filesystem_bridge', 'bridge.rs', ['filesystem_policy']),
        ('filesystem_native_service', 'native-service.rs',
         ['filesystem_policy', 'filesystem_service', 'filesystem_bridge']),
    ]:
        dependencies = ['-Ldependency=' + str(n)]
        for dep in deps:
            dependencies += ['--extern', dep + '=' + str(n / ('lib' + dep + '.rlib'))]
        for label, compiler in [('native', 'rustc'), ('native-clippy', 'clippy-driver')]:
            run(label + '-' + crate, [tools[compiler]['path'], *common,
                *native, *dependencies, '--crate-name=' + crate,
                '--crate-type=lib', S / source,
                '--emit=link=' + str(n / ('lib' + crate + '.rlib'))
                + ',obj=' + str(n / (crate + '.o'))], rust_env=True)
    objects = sorted(n.glob('*.o'))
    run('native-link', [tools['lld']['path'], '-r', *objects,
                        '-o', W / 'filesystem-service.o'])
    definitions = run('native-symbols', [tools['nm']['path'],
                      '--defined-only', W / 'filesystem-service.o']).stdout.decode()
    assert sum(line.split()[-1:] == ['aether_fs_service_run']
               for line in definitions.splitlines()) == 1
    imports = run('native-imports', [tools['nm']['path'],
                  '--undefined-only', W / 'filesystem-service.o']).stdout.decode()
    for name in ('aether_zpl_open_write', 'aether_zpl_close', 'aether_zpl_root',
                 'aether_zpl_lookup', 'aether_zpl_read', 'aether_zpl_write',
                 'aether_utc_read'):
        assert name in imports, name
    if lifetimes:
        assert 'aether_pool_service16_retire' in imports
    run('native-elf', [tools['readelf']['path'], '-h', W / 'filesystem-service.o'])
    layout = W / 'layout.c'
    layout.write_text('#include "native-service.h"\n'
        '_Static_assert(sizeof(struct aether_fs_service_result)==72,"size");\n'
        '_Static_assert(_Alignof(struct aether_fs_service_result)==8,"align");\n'
        '_Static_assert(offsetof(struct aether_fs_service_result,txg)==48,"txg");\n')
    run('c-layout', [tools['clang']['path'], '--target=x86_64-unknown-none',
                     '-std=c17', '-Wall', '-Wextra', '-Werror',
                     '-I' + str(S), '-ffreestanding', '-c', layout,
                     '-o', W / 'layout.o'])
    result = run('c-layout-packed', [tools['clang']['path'],
        '--target=x86_64-unknown-none', '-std=c17', '-I' + str(S),
        '-ffreestanding', '-fpack-struct=1', '-c', layout,
        '-o', W / 'packed.o'], expected=1)
    assert 'static assertion failed' in result.stderr.decode()
    for name, digest in record['sources'].items():
        assert sha(R / name) == digest, name
    record.update(status='pass', profile='lifetimes' if lifetimes else 'single', tests=11, entry_tests=4,
        semantic_omissions=len(mutants),
        native_object_sha256=sha(W / 'filesystem-service.o'),
        imports=imports, native_executed=False, full_engine_linked=False)
except BaseException as error:
    record.update(status='failed', error=repr(error))
    raise
finally:
    (W / 'results.json').write_text(json.dumps(record, indent=2) + '\n')
    print('Filesystem service check:', record['status'], str(W))
