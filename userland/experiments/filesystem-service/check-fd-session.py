# SPDX-License-Identifier: BSD-2-Clause
"""Python3.10+ owned integrated descriptor batch C/Rust host qualification; no native runtime."""
import hashlib
import json
from pathlib import Path
import platform
import shlex
import shutil
import sys
import tempfile
import types

R = Path(__file__).resolve().parents[2]
S = Path(__file__).resolve().parent
W = Path(tempfile.mkdtemp(prefix='filesystem-fd-session-', dir=R / 'build'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(root, digest):
    if sha(root / 'SHA256SUMS') != digest:
        raise ValueError('manifest pin: ' + str(root))
    members = {}
    for line in (root / 'SHA256SUMS').read_text().splitlines():
        expected, name = line.split('  ', 1)
        path = Path(name)
        if path.is_absolute() or '..' in path.parts or name in members:
            raise ValueError('manifest shape')
        if sha(root / path) != expected:
            raise ValueError('member pin: ' + name)
        members[name] = expected
    return members


record = dict(status='incomplete', python=sys.version,
              interpreter=dict(path=sys.executable, sha256=sha(Path(sys.executable))),
              checker_sha256=sha(Path(__file__)), sources={}, rows=[],
              host=platform.platform(), native_executed=False,
              live_rust_executed=False)
shutil.copyfile(Path(__file__), W / 'checker.py')
try:
    deliveries = R / 'build/service-deliveries'
    service = deliveries / 'filesystem-service-metadata-2026-10-21-v1'
    wire = deliveries / 'filesystem-fd-wire-2026-10-21-v3'
    client = deliveries / 'filesystem-fd-client-2026-10-21-v1'
    facade = deliveries / 'filesystem-fd-facade-2026-10-21-v1'
    bindings = deliveries / 'filesystem-fd-bindings-2026-10-21-v1'
    routing = deliveries / 'filesystem-fd-routing-2026-10-21-v1'
    table = deliveries / 'filesystem-fd-table-2026-10-21-v1'
    streams = deliveries / 'filesystem-fd-streams-2026-10-21-v1'
    write = deliveries / 'filesystem-fd-write-2026-10-21-v1'
    pipe = deliveries / 'filesystem-fd-pipe-2026-10-21-v1'
    replace = deliveries / 'filesystem-fd-replace-2026-10-21-v1'
    record['dependencies'] = {}
    for root, digest in [
        (service, '98a9fd12db4ecd1c736fe3ce332c9b69c631e043d4d87313827145675ba230a8'),
        (wire, 'ad1c8082948e08c1e2cc507dd2b069540699e20d9fe97852eadb390a63a4eabf'),
        (client, 'eac972b501518c97f67d483aafe6186ea2b5863dfaad26930108d4d7d290c48c'),
        (facade, '695b758f7d37547ad7ee14f01f0fbfe68cb73549aa69029cc612411b2c5260ce'),
        (bindings, '6ee051f6947d40cf4c8ce22c6c5dba965ba2b0ca5bad551d21ef9fd90715f420'),
        (routing, '7213a504d1f60c25d244fc45d19590eaf6e315cdb33f89f1657fe92ba69a5433'),
        (table, 'fe10be587ff93896cf66198d679a94c7d745ec18076369cd05ead01825e021ea'),
        (streams, '587b22a1192f5ac6f768c7becfe3f8144e4d42a2e56b6530bbf9b7dbb0b96e2c'),
        (write, '4213eb0244501c77f8993b63915c00cfabc33dce7390d07dc3dcedff2c862941'),
        (pipe, '63bfc774ba42832b501bb2647ff46d720130f253a64dcc099e12197ec6cb6fcc'),
        (replace, '5b43ec90ed2481b618d0b23e4801b9dde18d5997bbcd319e611f984824cd7183')]:
        record['dependencies'][root.name] = verify(root, digest)
    source = W / 'source'
    shutil.copytree(service / 'source', source)
    for root in [wire, client, facade, bindings, routing, table, streams, write, pipe, replace]:
        for path in (root / 'source').rglob('*'):
            if path.is_file():
                dest = source / path.relative_to(root / 'source')
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, dest)
    for name in ['fd-session.c', 'fd-session.h', 'fd-session-tests.c', 'fd-session-tests.h']:
        shutil.copyfile(S / name, source / name)
    record['sources'] = {str(path.relative_to(source)): sha(path)
                         for path in source.rglob('*') if path.is_file()}
    for root in [wire, client, facade, bindings, routing, table, streams, write, pipe, replace]:
        for name, digest in record['dependencies'][root.name].items():
            if (name.startswith('source/') and not (root == table and name in ['source/fd-table.c', 'source/fd-table.h'])
                    and sha(W / name) != digest):
                raise ValueError('overlapping dependency drift')
    manifest = R / 'docs/evidence/filesystem-transport-2026-10-19/inputs.json'
    if sha(manifest) != 'f200c7507b7fc300f9d4303191b0196acfa35dc7f9cffecd51e6a21e7933c82d':
        raise ValueError('tool manifest pin')
    pins = json.loads(manifest.read_text())
    tools = pins['tools']
    record['tools'] = tools
    record['resource_headers'] = pins['clang_resource_headers']
    record['rust_native_libraries'] = pins['rust_native_libraries']
    for tool in tools.values():
        if sha(Path(tool['path'])) != tool['sha256']:
            raise ValueError('tool pin')
    for name, digest in record['resource_headers'].items():
        if sha(Path(name)) != digest:
            raise ValueError('resource header pin')
    for name, digest in record['rust_native_libraries'].items():
        if sha(Path(name)) != digest:
            raise ValueError('Rust library pin')
    ubsan = Path('/opt/homebrew/Cellar/llvm@21/21.1.8/lib/clang/21/lib/darwin/libclang_rt.ubsan_osx_dynamic.dylib')
    runtime_digest = '7bfe170b03e5b9fb208d8568250aa84c35454933c306fe322c978295874c3746'
    record['ubsan'] = dict(path=str(ubsan), sha256=runtime_digest)
    if sha(ubsan) != runtime_digest:
        raise ValueError('UBSan pin')
    helper = R / 'experiments/command-runner/process.py'
    if sha(helper) != '9f0c0464c10fa23bfc7c3c91fe26b04e5ab063ca058eeb6d41542d98c6186e4e':
        raise ValueError('runner pin')
    proc = types.ModuleType('owned')
    exec(compile(helper.read_bytes(), str(helper), 'exec'), proc.__dict__)

    def run(label, argv, expected=0, timeout=60):
        env = proc.clean_env(W)
        if str(argv[0]) in [tools[n]['path'] for n in ['rustc', 'rustfmt', 'clippy-driver']]:
            env['DYLD_LIBRARY_PATH'] = str(Path(tools['rustc']['path']).parent.parent / 'lib')
        result = proc.run(list(map(str, argv)), cwd=R, env=env,
                          work=W, label=label, timeout=timeout)
        record['rows'].append(dict(label=label, expected=expected,
                                   process=result.record))
        if label == 'live':
            record['live_rust_executed'] = True
        if (result.returncode != expected or not result.record['complete']
                or result.record['cleanup'] != 'complete'):
            raise RuntimeError(label)
        return result

    run('rust-format', [tools['rustfmt']['path'], '--edition', '2021', '--check',
        '--config-path', R / 'docs/vendor/aether-approved-drafts/2026-09-05/drafts/coding-v0.1.0/configs/rustfmt.toml',
        source / 'fd-table-host.rs'])
    run('c-format', [tools['clang-format']['path'], '--dry-run', '--Werror',
        '--style=file:' + str(R / 'docs/quality/clang-format.yaml'),
        *[source / name for name in ['fd-session.c', 'fd-session.h', 'fd-session-tests.c', 'fd-session-tests.h']]])
    flags = ['--edition=2021', '-Dwarnings', '-Dunsafe_op_in_unsafe_fn']
    for selection in ['namespace', 'lifetimes', 'mixed', 'wait', 'bulk', 'runtime',
                      'activation', 'names', 'directories', 'metadata', 'process_views']:
        flags += ['--cfg', 'fs_' + selection]
    host = W / 'host'
    host.mkdir()

    def dependencies(names):
        args = ['-Ldependency=' + str(host)]
        for name in names:
            args += ['--extern', name + '=' + str(host / ('lib' + name + '.rlib'))]
        return args

    for name, filename, imports in [
        ('filesystem_metadata', 'metadata-lib.rs', []),
        ('filesystem_policy', 'owner.rs', ['filesystem_metadata']),
        ('filesystem_service', 'service.rs', ['filesystem_policy']),
        ('filesystem_client', 'client.rs', ['filesystem_service']),
        ('filesystem_remote_descriptors', 'remote-descriptors.rs', ['filesystem_client', 'filesystem_service']),
        ('filesystem_fd_protocol', 'fd-protocol.rs', ['filesystem_client', 'filesystem_service', 'filesystem_remote_descriptors'])]:
        run('library-' + name, [tools['rustc']['path'], *flags,
            *dependencies(imports), '--crate-type=lib', '--crate-name=' + name,
            *(['-Funsafe-code'] if name != 'filesystem_metadata' else []),
            source / filename, '-o', host / ('lib' + name + '.rlib')])
    imports = dependencies(['filesystem_policy', 'filesystem_service', 'filesystem_client',
                            'filesystem_remote_descriptors', 'filesystem_fd_protocol'])
    for compiler in ['rustc', 'clippy-driver']:
        run('server-' + compiler, [tools[compiler]['path'], *flags, '-Funsafe-code',
            *imports, source / 'fd-table-host.rs', '-o', W / ('server-' + compiler)])
    target = run('c-target', [tools['clang']['path'], '-dumpmachine'])
    record['target'] = target.stdout.decode().strip()
    headers = run('headers', [tools['clang']['path'], '-std=c17', '-M',
        source / 'fd-client.c', source / 'fd-facade.c', source / 'fd-routing.c', source / 'fd-table.c', source / 'fd-table-host.c', source / 'fd-stream-tests.c', source / 'fd-write.c', source / 'fd-write-tests.c', source / 'fd-pipe.c', source / 'fd-pipe-tests.c', source / 'fd-replace.c', source / 'fd-replace-tests.c', source / 'fd-session.c', source / 'fd-session-tests.c'])
    names = set()
    for line in headers.stdout.decode().replace('\\\n', ' ').splitlines():
        names.update(shlex.split(line.split(':', 1)[1]))
    record['sdk_headers'] = {name: sha(Path(name)) for name in sorted(names)}
    cflags = ['-std=c17', '-Wall', '-Wextra', '-Wpedantic', '-Wconversion',
              '-Wsign-conversion', '-Wshadow', '-Wstrict-prototypes',
              '-Wmissing-prototypes', '-Werror', '-fsanitize=undefined',
              '-fno-sanitize-recover=all']

    fixture_object = W / 'fixture.o'
    aliases = ['-Daefd_table_open=aefd_session_test_open',
               '-Daefd_table_dup=aefd_session_test_dup',
               '-Daefd_table_close=aefd_session_test_close',
               '-Daefd_table_set_cloexec=aefd_session_test_flags',
               '-Daefd_table_seek=aefd_session_test_seek']
    run('fixture-object', [tools['clang']['path'], *cflags, *aliases,
        '-c', source / 'fd-table-host.c', '-o', fixture_object])

    def build(label, implementation):
        run(label, [tools['clang']['path'], *cflags, source / 'fd-client.c',
            source / 'fd-facade.c', source / 'fd-routing.c', source / 'fd-table.c', source / 'fd-write.c', source / 'fd-pipe.c', source / 'fd-replace.c', implementation,
            source / 'fd-stream-tests.c', source / 'fd-write-tests.c', source / 'fd-pipe-tests.c', source / 'fd-replace-tests.c', source / 'fd-session-tests.c', fixture_object,
            '-I' + str(source), '-o', W / label])

    build('consumer', source / 'fd-session.c')
    baseline = run('live', [W / 'server-rustc', W / 'consumer'], timeout=30)
    if baseline.stdout != b'269 live C/Rust table cases pass\n':
        raise ValueError('live case count')
    original = (source / 'fd-session.c').read_text()
    controls = {
        'allow-readmission': ('s->initialized || client->generation || client->live ||\n        client->workspace', 's->initialized == 999', b'== -16'),
        'omit-projection': ('if (omit_cloexec)', 'if (omit_cloexec == 999)', b'!decoded.slots[0].kind'),
        'mask-invalid-snapshot': ('return -5;\n    }\n    if (omit_cloexec)', 'return 0;\n    }\n    if (omit_cloexec)', b'== -5'),
        'omit-removal-count': ('++result.removed;', '(void)result.removed;', b'f.attempted == 3 && f.removed == 3'),
        'mask-retired-empty': ('if (!ready(s)) {\n        result.unknown = 1;', 'if (s->initialized == 999) {\n        result.unknown = 1;', b'f.unknown && f.first_error == -5'),
        'mask-transport-errors': ('result.transport = s->client->closed;', 'result.transport = (struct aefd_close_result){0};', b'again.transport.input == -5'),
        'discard-cached-receipt': ('if (s->finished)', 'if (s->finished == 999)', b'again.attempted == saved.attempted'),
        'mask-stream-seek': (': -29;', ': -38;', b'== -29')}
    record['mutations'] = []
    for label, (old, new, assertion) in controls.items():
        if old not in original:
            raise ValueError('mutation target: ' + label)
        path = W / (label + '.c')
        path.write_text(original.replace(old, new, 1))
        record['mutations'].append(dict(label=label, old=old, new=new, sha256=sha(path)))
        build(label, path)
        failure = run(label + '-test', [W / 'server-rustc', W / label], expected=101, timeout=30)
        if (b'Assertion failed:' not in failure.stderr or assertion not in failure.stderr
                or b'C consumer failed:' not in failure.stderr):
            raise ValueError('nonsemantic control failure: ' + label)
    include = R / 'build/sdk-deliveries/native-service-runtime-2026-10-06-v2/sdk/stage/usr/include'
    record['native_headers'] = {str(p): sha(p) for p in sorted(include.rglob('*')) if p.is_file()}
    if not record['native_headers'] or not (include / 'bits/alltypes.h').is_file():
        raise ValueError('native headers unavailable')
    native = W / 'native'
    native.mkdir()
    units = ['fd-client', 'fd-facade', 'fd-routing', 'fd-table', 'fd-write', 'fd-pipe', 'fd-replace', 'fd-session']
    for unit in units:
        run('native-' + unit, [tools['clang']['path'], *cflags[:-2],
            '--target=x86_64-unknown-none', '-ffreestanding', '-fno-builtin',
            '-O2', '-fstack-usage', '-nostdinc', '-isystem', include,
            '-I' + str(source), '-c', source / (unit + '.c'), '-o', native / (unit + '.o')])
    run('native-link', [tools['lld']['path'], '-r', *[native / (u + '.o') for u in units], '-o', native / 'combined.o'])
    elf = run('native-inspect', [tools['readelf']['path'], '-h', '-S', '-s', native / 'combined.o'])
    if b'ELF64' not in elf.stdout or b'Advanced Micro Devices X86-64' not in elf.stdout or b'REL (Relocatable file)' not in elf.stdout:
        raise ValueError('native object shape')
    symbols = run('native-unresolved', [tools['nm']['path'], '--undefined-only', native / 'combined.o'])
    undefined = [line.split()[-1] for line in symbols.stdout.decode().splitlines() if line.strip()]
    if not undefined or not set(undefined) <= {'memcpy', 'memset', 'memcmp', 'memmove'}:
        raise ValueError('native unresolved imports')
    stack = []
    for path in sorted(native.glob('*.su')):
        for line in path.read_text().splitlines():
            name, size, kind = line.split('\t')
            if kind != 'static':
                raise ValueError('dynamic stack')
            stack.append(dict(function=name, bytes=int(size)))
    if not stack:
        raise ValueError('missing stack reports')
    record['native_build'] = dict(target='x86_64-unknown-none', objects=len(units),
        linked_sha256=sha(native / 'combined.o'), unresolved=undefined,
        stack=stack, maximum_individual_frame=max(row['bytes'] for row in stack),
        scope='Freestanding ELF objects and relocatable link only. libc memory imports unresolved intentionally. No executable, loader, native execution or whole call-stack/fit acceptance.')
    for name, digest in record['native_headers'].items():
        if sha(Path(name)) != digest:
            raise ValueError('native header drift')
    for name, digest in record['sdk_headers'].items():
        if sha(Path(name)) != digest:
            raise ValueError('header drift')
    for name, digest in record['resource_headers'].items():
        if sha(Path(name)) != digest:
            raise ValueError('resource drift')
    if sha(ubsan) != runtime_digest:
        raise ValueError('runtime drift')
    for name, digest in record['sources'].items():
        if sha(source / name) != digest:
            raise ValueError('snapshot drift')
    for name in ['fd-session.c', 'fd-session.h', 'fd-session-tests.c', 'fd-session-tests.h']:
        if sha(S / name) != record['sources'][name]:
            raise ValueError('maintained source drift')
    record.update(status='pass', live_cases=269, stream_cases_per_child=14, write_cases_per_child=18, pipe_cases_per_child=22, replacement_cases_per_child=19, session_cases_per_child=15, semantic_controls=len(controls),
                  c_binary_sha256=sha(W / 'consumer'),
                  rust_binary_sha256=sha(W / 'server-rustc'))
except BaseException as error:
    record.update(status='failed', error=repr(error))
    raise
finally:
    (W / 'results.json').write_text(json.dumps(record, indent=2) + '\n')
    print(W)
