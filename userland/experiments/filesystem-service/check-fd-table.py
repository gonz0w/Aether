# SPDX-License-Identifier: BSD-2-Clause
"""Python3.10+ owned tagged file-table C/Rust host qualification; no native runtime."""
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
W = Path(tempfile.mkdtemp(prefix='filesystem-fd-table-', dir=R / 'build'))


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
    record['dependencies'] = {}
    for root, digest in [
        (service, '98a9fd12db4ecd1c736fe3ce332c9b69c631e043d4d87313827145675ba230a8'),
        (wire, 'ad1c8082948e08c1e2cc507dd2b069540699e20d9fe97852eadb390a63a4eabf'),
        (client, 'eac972b501518c97f67d483aafe6186ea2b5863dfaad26930108d4d7d290c48c'),
        (facade, '695b758f7d37547ad7ee14f01f0fbfe68cb73549aa69029cc612411b2c5260ce'),
        (bindings, '6ee051f6947d40cf4c8ce22c6c5dba965ba2b0ca5bad551d21ef9fd90715f420'),
        (routing, '7213a504d1f60c25d244fc45d19590eaf6e315cdb33f89f1657fe92ba69a5433')]:
        record['dependencies'][root.name] = verify(root, digest)
    source = W / 'source'
    shutil.copytree(service / 'source', source)
    for root in [wire, client, facade, bindings, routing]:
        for path in (root / 'source').rglob('*'):
            if path.is_file():
                dest = source / path.relative_to(root / 'source')
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, dest)
    for name in ['fd-table.c', 'fd-table.h', 'fd-table-host.c', 'fd-table-host.rs', 'fd-table-live.rs']:
        shutil.copyfile(S / name, source / name)
    record['sources'] = {str(path.relative_to(source)): sha(path)
                         for path in source.rglob('*') if path.is_file()}
    for root in [wire, client, facade, bindings, routing]:
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
        *[source / name for name in ['fd-table.c', 'fd-table.h', 'fd-table-host.c']]])
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
        source / 'fd-client.c', source / 'fd-facade.c', source / 'fd-routing.c', source / 'fd-table.c', source / 'fd-table-host.c'])
    names = set()
    for line in headers.stdout.decode().replace('\\\n', ' ').splitlines():
        names.update(shlex.split(line.split(':', 1)[1]))
    record['sdk_headers'] = {name: sha(Path(name)) for name in sorted(names)}
    cflags = ['-std=c17', '-Wall', '-Wextra', '-Wpedantic', '-Wconversion',
              '-Wsign-conversion', '-Wshadow', '-Wstrict-prototypes',
              '-Wmissing-prototypes', '-Werror', '-fsanitize=undefined',
              '-fno-sanitize-recover=all']

    def build(label, table):
        run(label, [tools['clang']['path'], *cflags, source / 'fd-client.c',
            source / 'fd-facade.c', source / 'fd-routing.c', table, source / 'fd-table-host.c', '-I' + str(source), '-o', W / label])

    build('consumer', source / 'fd-table.c')
    baseline = run('live', [W / 'server-rustc', W / 'consumer'], timeout=30)
    if baseline.stdout != b'269 live C/Rust table cases pass\n':
        raise ValueError('live case count')
    original = (source / 'fd-table.c').read_text()
    controls = {
        'alias-without-dup': ('aefd_file_dup(client, binding.selector, 3, cloexec)',
                              '(int64_t)binding.selector + cloexec * 0', b'== 6'),
        'skip-selector-uniqueness': ('map->slots[i].selector == selector',
                                     'map->slots[i].selector == 255', b'== -5'),
        'skip-confirmed-close-clear': ('map->slots[fd] = (struct aefd_binding){0};',
                                       '(void)fd;', b'map->slots[5].kind == AEFD_BIND_EMPTY'),
        'clear-on-close-error': ('if (result == 0)\n        map->slots[fd] =',
                                 'if (result <= 0)\n        map->slots[fd] =', b'!memcmp(map, before'),
        'skip-cloexec-commit': ('map->slots[fd].cloexec = (unsigned char)cloexec;',
                                '(void)cloexec;', b'map->slots[6].cloexec == 1'),
        'use-logical-as-selector': ('(unsigned char)selector,',
                                    '(unsigned char)logical,', b'map->slots[5].selector == 3')}
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
    for name in ['fd-table.c', 'fd-table.h', 'fd-table-host.c', 'fd-table-host.rs', 'fd-table-live.rs']:
        if sha(S / name) != record['sources'][name]:
            raise ValueError('maintained source drift')
    record.update(status='pass', live_cases=269, semantic_controls=len(controls),
                  c_binary_sha256=sha(W / 'consumer'),
                  rust_binary_sha256=sha(W / 'server-rustc'))
except BaseException as error:
    record.update(status='failed', error=repr(error))
    raise
finally:
    (W / 'results.json').write_text(json.dumps(record, indent=2) + '\n')
    print(W)
