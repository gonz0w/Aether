# SPDX-License-Identifier: BSD-2-Clause
"""Python3.10+ owned live C/Rust host pipe qualification; no native runtime."""
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
W = Path(tempfile.mkdtemp(prefix='filesystem-fd-facade-', dir=R / 'build'))


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
              live_rust_executed=True)
shutil.copyfile(Path(__file__), W / 'checker.py')
try:
    deliveries = R / 'build/service-deliveries'
    service = deliveries / 'filesystem-service-metadata-2026-10-21-v1'
    wire = deliveries / 'filesystem-fd-wire-2026-10-21-v3'
    client = deliveries / 'filesystem-fd-client-2026-10-21-v1'
    record['dependencies'] = {}
    for root, digest in [
        (service, '98a9fd12db4ecd1c736fe3ce332c9b69c631e043d4d87313827145675ba230a8'),
        (wire, 'ad1c8082948e08c1e2cc507dd2b069540699e20d9fe97852eadb390a63a4eabf'),
        (client, 'eac972b501518c97f67d483aafe6186ea2b5863dfaad26930108d4d7d290c48c')]:
        record['dependencies'][root.name] = verify(root, digest)
    source = W / 'source'
    shutil.copytree(service / 'source', source)
    for root in [wire, client]:
        for path in (root / 'source').rglob('*'):
            if path.is_file():
                dest = source / path.relative_to(root / 'source')
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, dest)
    for name in ['fd-facade.c', 'fd-facade.h', 'fd-facade-host.c',
                 'fd-facade-host.rs', 'fd-facade-live.rs']:
        shutil.copyfile(S / name, source / name)
    record['sources'] = {str(path.relative_to(source)): sha(path)
                         for path in source.rglob('*') if path.is_file()}
    for root in [wire, client]:
        for name, digest in record['dependencies'][root.name].items():
            if name.startswith('source/') and sha(W / name) != digest:
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
        if (result.returncode != expected or not result.record['complete']
                or result.record['cleanup'] != 'complete'):
            raise RuntimeError(label)
        return result

    run('rust-format', [tools['rustfmt']['path'], '--edition', '2021', '--check',
        '--config-path', R / 'docs/vendor/aether-approved-drafts/2026-09-05/drafts/coding-v0.1.0/configs/rustfmt.toml',
        source / 'fd-facade-host.rs'])
    run('c-format', [tools['clang-format']['path'], '--dry-run', '--Werror',
        '--style=file:' + str(R / 'docs/quality/clang-format.yaml'),
        *[source / name for name in ['fd-facade.c', 'fd-facade.h', 'fd-facade-host.c']]])
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
            *imports, source / 'fd-facade-host.rs', '-o', W / ('server-' + compiler)])
    target = run('c-target', [tools['clang']['path'], '-dumpmachine'])
    record['target'] = target.stdout.decode().strip()
    headers = run('headers', [tools['clang']['path'], '-std=c17', '-M',
        source / 'fd-client.c', source / 'fd-facade.c', source / 'fd-facade-host.c'])
    names = set()
    for line in headers.stdout.decode().replace('\\\n', ' ').splitlines():
        names.update(shlex.split(line.split(':', 1)[1]))
    record['sdk_headers'] = {name: sha(Path(name)) for name in sorted(names)}
    cflags = ['-std=c17', '-Wall', '-Wextra', '-Wpedantic', '-Wconversion',
              '-Wsign-conversion', '-Wshadow', '-Wstrict-prototypes',
              '-Wmissing-prototypes', '-Werror', '-fsanitize=undefined',
              '-fno-sanitize-recover=all']

    def build(label, facade):
        run(label, [tools['clang']['path'], *cflags, source / 'fd-client.c',
            facade, source / 'fd-facade-host.c', '-I' + str(source), '-o', W / label])

    build('consumer', source / 'fd-facade.c')
    baseline = run('live', [W / 'server-rustc', W / 'consumer'], timeout=30)
    if baseline.stdout != b'74 live C/Rust host cases pass\n':
        raise ValueError('live case count')
    original = (source / 'fd-facade.c').read_text()
    controls = {
        'mask-semantic-errno': ('return reply.status;', 'return -5;', b'== -9'),
        'skip-read-copy': ('memcpy(out, client->workspace, (size_t)result);',
                            '(void)out;', b'!memcmp(out, "ab", 2)'),
        'copy-unused-tail': ('memcpy(out, client->workspace, (size_t)result);',
                             'memcpy(out, client->workspace, AEFD_READ_MAX);', b'out[i] == 0xa5'),
        'wrong-seek-origin': ('(uint64_t)whence', '(uint64_t)(whence * 0)', b'== 5'),
        'skip-close': ('return invoke(client, 5, args, NULL, 0);',
                       'return invoke(client, 6, args, NULL, 0);', b'== -9'),
        'mask-retired': ('return completed == 0 ? -22 : -5;',
                         'return completed == 0 ? -22 : 0;', b'== -5')}
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
    for name in ['fd-facade.c', 'fd-facade.h', 'fd-facade-host.c',
                 'fd-facade-host.rs', 'fd-facade-live.rs']:
        if sha(S / name) != record['sources'][name]:
            raise ValueError('maintained source drift')
    record.update(status='pass', live_cases=74, semantic_controls=len(controls),
                  c_binary_sha256=sha(W / 'consumer'),
                  rust_binary_sha256=sha(W / 'server-rustc'))
except BaseException as error:
    record.update(status='failed', error=repr(error))
    raise
finally:
    (W / 'results.json').write_text(json.dumps(record, indent=2) + '\n')
    print(W)
