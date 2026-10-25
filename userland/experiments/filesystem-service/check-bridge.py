# SPDX-License-Identifier: BSD-2-Clause
"""Owned C ABI, lifetime and native-object checks for the private bridge."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import types

R = Path(__file__).resolve().parents[2]
S = Path(__file__).resolve().parent
P = R / 'docs/evidence/filesystem-bridge-2026-10-18'
I = json.loads((P / 'inputs.json').read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for name, digest in I['producer_files'].items():
    f = P / 'utc.h' if name == 'userland/utc.h' else P / 'producer' / name
    assert sha(f) == digest, name
for tool in I['tools'].values():
    assert sha(Path(tool['path'])) == tool['sha256']
for name, digest in I['rust_native_libraries'].items():
    assert sha(Path(name)) == digest, name
baseline_info = I['native_engine_baseline']
assert sha(Path(baseline_info['manifest_path'])) == baseline_info['manifest_sha256']
baseline_manifest = json.loads(Path(baseline_info['manifest_path']).read_text())
BASE = Path(baseline_info['root'])
for name, digest in baseline_manifest['current_files'].items():
    assert sha(BASE / name) == digest, name
for name, digest in I['clang_resource_headers'].items():
    assert sha(Path(name)) == digest, name
assert sha(S / 'owner.rs') == I['policy_source_sha256']
helper = R / 'experiments/command-runner/process.py'
assert sha(helper) == '9f0c0464c10fa23bfc7c3c91fe26b04e5ab063ca058eeb6d41542d98c6186e4e'
proc = types.ModuleType('owned')
exec(compile(helper.read_bytes(), str(helper), 'exec'), proc.__dict__)
W = Path(tempfile.mkdtemp(prefix='filesystem-bridge-', dir=R / 'build'))
env = proc.clean_env(W)
tools = I['tools']
rust = Path(tools['rustc']['path']).parent
rows = []
record = {'status': 'running', 'root': str(W), 'rows': rows, 'python': sys.version,
          'driver_sha256': sha(Path(__file__)), 'input_manifest_sha256': sha(P / 'inputs.json')}


def run(name, argv, expected=0, rust_env=False, timeout=60):
    selected = dict(env)
    if rust_env:
        selected['DYLD_LIBRARY_PATH'] = str(rust.parent / 'lib')
    result = proc.run([str(a) for a in argv], cwd=R, env=selected, work=W, label=name, timeout=timeout)
    rows.append({'name': name, 'expected': expected, 'record': result.record})
    assert result.returncode == expected and result.record['complete'] and result.record['cleanup'] == 'complete', name
    return result


try:
    sources = [S / n for n in ('bridge.rs', 'bridge-tests.rs', 'native-probe.rs')]
    if '--format' in sys.argv[1:]:
        run('rust-format', [tools['rustfmt']['path'], '--edition=2021', *sources], rust_env=True)
        run('c-format', [tools['clang-format']['path'], '-i', '--style=file:docs/quality/clang-format.yaml', S / 'bridge-fixture.c', S / 'native-probe.h'])
    record['sources'] = {str(p.relative_to(R)): sha(p) for p in [*sources, S / 'bridge-fixture.c', S / 'native-probe.h', S / 'owner.rs', Path(__file__)]}
    run('rust-format-check', [tools['rustfmt']['path'], '--edition=2021', '--check', *sources], rust_env=True)
    run('c-format-check', [tools['clang-format']['path'], '--dry-run', '--Werror', '--style=file:docs/quality/clang-format.yaml', S / 'bridge-fixture.c', S / 'native-probe.h'])
    run('fixture', [tools['clang']['path'], '-std=c17', '-Wall', '-Wextra', '-Werror', '-I' + str(P),
                    '-I' + str(P / 'producer/user/storage/openzfs-volume'), '-c', S / 'bridge-fixture.c', '-o', W / 'fixture.o'])
    packed = run('reject-packed-c', [tools['clang']['path'], '-std=c17', '-fpack-struct=1', '-I' + str(P),
                 '-I' + str(P / 'producer/user/storage/openzfs-volume'), '-c', S / 'bridge-fixture.c', '-o', W / 'packed.o'], 1)
    assert 'static assertion failed' in packed.stderr.decode()
    common = ['--edition=2021', '-Dwarnings', '-Dunsafe_op_in_unsafe_fn']
    run('host-policy', [tools['rustc']['path'], *common, '--crate-name=filesystem_policy', '--crate-type=lib',
                       '-Funsafe-code', S / 'owner.rs', '-o', W / 'libfilesystem_policy.rlib'], rust_env=True)
    external = ['--extern', 'filesystem_policy=' + str(W / 'libfilesystem_policy.rlib')]
    run('host-bridge', [tools['rustc']['path'], *common, *external, '--crate-name=filesystem_bridge',
                       '--crate-type=lib', S / 'bridge.rs', '-o', W / 'libfilesystem_bridge.rlib'], rust_env=True)
    run('host-probe', [tools['rustc']['path'], *common, *external, '--extern',
                      'filesystem_bridge=' + str(W / 'libfilesystem_bridge.rlib'), '-Ldependency=' + str(W),
                      '--crate-name=filesystem_probe', '--crate-type=lib', S / 'native-probe.rs',
                      '-o', W / 'libfilesystem_probe.rlib'], rust_env=True)
    run('clippy-probe', [tools['clippy-driver']['path'], *common, *external, '--extern',
                      'filesystem_bridge=' + str(W / 'libfilesystem_bridge.rlib'), '-Ldependency=' + str(W),
                      '--crate-name=filesystem_probe', '--crate-type=lib', S / 'native-probe.rs',
                      '-o', W / 'clippy-probe.rlib'], rust_env=True)
    test_external = [*external, '--extern', 'filesystem_probe=' + str(W / 'libfilesystem_probe.rlib'), '-Ldependency=' + str(W)]
    run('host-tests-compile', [tools['rustc']['path'], *common, *test_external, '--test', S / 'bridge.rs',
                             '-Clink-arg=' + str(W / 'fixture.o'), '-o', W / 'tests'], rust_env=True)
    run('host-tests', [W / 'tests', '--test-threads=1'], timeout=30)
    run('clippy', [tools['clippy-driver']['path'], *common, *test_external, '--test', S / 'bridge.rs',
                  '-Clink-arg=' + str(W / 'fixture.o'), '-o', W / 'clippy-tests'], rust_env=True)
    # The pointer-bearing bridge must not be transferable/shareable, duplicated,
    # or used to outlive the exclusive SPA token. These are compiler negatives.
    compile_common = [tools['rustc']['path'], *common, *external, '--extern',
                      'filesystem_bridge=' + str(W / 'libfilesystem_bridge.rlib'),
                      '-Ldependency=' + str(W), '--crate-type=lib']
    failures = {
        'send': ('fn require<T: Send>() {} pub fn bad() { require::<filesystem_bridge::Zpl<\'static>>(); }', 'cannot be sent'),
        'sync': ('fn require<T: Sync>() {} pub fn bad() { require::<filesystem_bridge::Spa<\'static>>(); }', 'cannot be shared'),
        'overlap': ('pub fn bad(s: &mut filesystem_bridge::Spa<\'_>) { let a=s.open(c"x").unwrap(); let b=s.open(c"x").unwrap(); drop((a,b)); }', 'more than once'),
        'escape': ('pub fn bad(s: &mut filesystem_bridge::Spa<\'_>) -> filesystem_bridge::Zpl<\'static> {s.open(c"x").unwrap()}', 'lifetime may not live long enough'),
        'clone': ('pub fn bad(s: filesystem_bridge::Spa<\'_>) {let _ = s.clone();}', 'no method named `clone`'),
        'move-spa': ('pub fn bad(mut s: filesystem_bridge::Spa<\'_>) {let c=s.open(c"x").unwrap(); drop(s); drop(c);}', 'cannot move out'),
    }
    for name, (text, error) in failures.items():
        f = W / (name + '.rs'); f.write_text(text)
        result = run('deny-' + name, [*compile_common, f, '-o', W / (name + '.rlib')], 1, True)
        assert error in result.stderr.decode(), name
    drift = W / 'abi-drift.rs'
    text = (S / 'bridge.rs').read_text()
    original = 'struct RawWrite {\n    txg: u64,\n    bytes_staged: u64,\n    state: u64,\n}'
    assert text.count(original) == 1
    drift.write_text(text.replace(original, 'struct RawWrite { state: u64, bytes_staged: u64, txg: u64 }', 1))
    result = run('reject-rust-layout', [*compile_common, drift, '-o', W / 'drift.rlib'], 1, True)
    assert 'evaluation panicked' in result.stderr.decode()
    N = W / 'native'; N.mkdir()
    native = ['--target=x86_64-unknown-none', '-Cpanic=abort', '-Copt-level=2', '-Crelocation-model=static', '-Ccodegen-units=1']
    run('native-policy', [tools['rustc']['path'], *common, *native, '--crate-name=filesystem_policy', '--crate-type=lib',
                         S / 'owner.rs', '--emit=link=' + str(N / 'libfilesystem_policy.rlib') + ',obj=' + str(N / 'policy.o')], rust_env=True)
    ne = ['--extern', 'filesystem_policy=' + str(N / 'libfilesystem_policy.rlib'), '-Ldependency=' + str(N)]
    run('native-bridge', [tools['rustc']['path'], *common, *native, *ne, '--crate-name=filesystem_bridge', '--crate-type=lib',
                         S / 'bridge.rs', '--emit=link=' + str(N / 'libfilesystem_bridge.rlib') + ',obj=' + str(N / 'bridge.o')], rust_env=True)
    run('native-probe', [tools['rustc']['path'], *common, *native, *ne, '--extern', 'filesystem_bridge=' + str(N / 'libfilesystem_bridge.rlib'),
                        '--crate-type=lib', S / 'native-probe.rs', '--emit=obj', '-o', W / 'native-probe.o'], rust_env=True)
    run('native-link', [tools['lld']['path'], '-r', N / 'policy.o', N / 'bridge.o', W / 'native-probe.o', '-o', W / 'native-consumer.o'])
    imports = run('native-imports', [tools['nm']['path'], '--undefined-only', W / 'native-consumer.o']).stdout.decode()
    symbols = run('native-symbols', [tools['nm']['path'], '--defined-only', W / 'native-consumer.o']).stdout.decode()
    assert 'aether_fs_policy_write_probe' in symbols
    for name in ('aether_zpl_open_write', 'aether_zpl_close', 'aether_zpl_root', 'aether_zpl_lookup', 'aether_zpl_read', 'aether_zpl_write', 'aether_utc_read'):
        assert name in imports, name
    run('native-elf', [tools['readelf']['path'], '-h', W / 'native-consumer.o'])
    # Compile the actual private C implementation against the preserved original
    # native headers. This is an object composition, not a whole engine/guest.
    recipe = json.loads((BASE / 'build-attempt-5/results.json').read_text())
    argv = next(row['argv'] for row in recipe['commands'] if row['name'] == 'input-176-checked')
    def route(arg):
        if arg.startswith('-fmacro-prefix-map='):
            left, right = arg.removeprefix('-fmacro-prefix-map=').split('=', 1)
            return '-fmacro-prefix-map=' + route(left) + '=' + right
        return arg.replace('/Users/cam/DEV/Aether/zig-out/openzfs-native-time-callers-2026-10-05', str(BASE))
    prefix = [route(arg) for arg in argv[:argv.index('-c')]]
    assert prefix[0] == tools['clang']['path']
    private = P / 'producer/user/storage/openzfs-volume'
    flags = ['-I' + str(private), '-I' + str(P), '-I' + str(S), '-std=c17', '-Wall', '-Wextra', '-Werror',
             '-DAETHER_ZPL_ORDERED_WRITE=1', '-fstack-usage']
    run('native-original-c', [*prefix, *flags, '-c', private / 'zpl-write.c', '-o', W / 'zpl-engine.o'])
    fixture = (S / 'bridge-fixture.c').read_text()
    layout = W / 'native-abi.c'
    layout.write_text(fixture[:fixture.index('struct aether_zpl_view')])
    run('native-c-abi', [*prefix, *flags, '-c', layout, '-o', W / 'native-abi.o'])
    run('native-c-rust-link', [tools['lld']['path'], '-r', W / 'native-consumer.o', W / 'zpl-engine.o',
                             '-Map=' + str(W / 'native-c-rust.map'), '-o', W / 'native-c-rust.o'])
    actual = run('native-c-rust-imports', [tools['nm']['path'], '--undefined-only', W / 'native-c-rust.o']).stdout.decode()
    definitions = run('native-c-definitions', [tools['nm']['path'], '--defined-only', W / 'zpl-engine.o']).stdout.decode()
    for name in ('aether_zpl_open_write', 'aether_zpl_close', 'aether_zpl_root', 'aether_zpl_lookup', 'aether_zpl_read', 'aether_zpl_write'):
        assert name not in actual and sum(line.split()[-1:] == [name] for line in definitions.splitlines()) == 1, name
    run('native-omit-write', [*prefix, *flags, '-Daether_zpl_write=aether_omitted_zpl_write',
                             '-c', private / 'zpl-write.c', '-o', W / 'omitted-write.o'])
    run('native-omitted-link', [tools['lld']['path'], '-r', W / 'native-consumer.o', W / 'omitted-write.o', '-o', W / 'omitted.o'])
    omitted = run('native-omission-imports', [tools['nm']['path'], '--undefined-only', W / 'omitted.o']).stdout.decode()
    assert 'aether_zpl_write' in omitted
    for name, digest in record['sources'].items(): assert sha(R / name) == digest, name
    record.update(status='pass', host_tests=9, compiler_denials=6, abi_denials=2,
                  native_consumer_sha256=sha(W / 'native-consumer.o'), native_imports=imports,
                  original_c_sha256=sha(W / 'zpl-engine.o'), native_c_rust_sha256=sha(W / 'native-c-rust.o'),
                  original_c_bindings_resolved=6, missing_write_symbol_detected=True,
                  native_executed=False, full_engine_linked=False)
except BaseException as error:
    record.update(status='failed', error=repr(error))
    raise
finally:
    (W / 'results.json').write_text(json.dumps(record, indent=2) + '\n')
    print('Filesystem bridge check:', record['status'], str(W))
