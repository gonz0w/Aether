# SPDX-License-Identifier: BSD-2-Clause
"""Python3.10+ owned C17 callback checks; no native or live-Rust execution."""
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
W = Path(tempfile.mkdtemp(prefix='filesystem-fd-client-', dir=R / 'build'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verified_manifest(root, digest):
    manifest = root / 'SHA256SUMS'
    if sha(manifest) != digest:
        raise ValueError('manifest pin: ' + str(root))
    members = {}
    for line in manifest.read_text().splitlines():
        expected, name = line.split('  ', 1)
        path = Path(name)
        if path.is_absolute() or '..' in path.parts or name in members:
            raise ValueError('manifest member')
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
    selected = R / 'build/service-deliveries/filesystem-fd-wire-2026-10-21-v3'
    record['wire'] = verified_manifest(
        selected, 'ad1c8082948e08c1e2cc507dd2b069540699e20d9fe97852eadb390a63a4eabf')
    evidence = R / 'docs/evidence/filesystem-fd-wire-2026-10-21'
    record['recorded_exchange'] = verified_manifest(
        evidence, 'd61bd9dfe80579ba6bfcd7f6bd23ec32e5c22c4165a848a55fa19168989b4f94')
    if sha(S / 'fd-protocol.h') != record['wire']['source/fd-protocol.h']:
        raise ValueError('codec drift')
    fixtures = R / 'docs/evidence/filesystem-fd-client-2026-10-21/inputs'
    recorded_hashes = {
        'requests.bin': '92050730356810b5c659f6b7803ed5f95befcf93f2065e670dc8f3a9e20c1db8',
        'replies.bin': 'cb73e8a769273025e915cdc67a47955d70150775683c1e636d1531dde668a73c'}
    record['fixtures'] = recorded_hashes
    for name, digest in recorded_hashes.items():
        if sha(fixtures / name) != digest:
            raise ValueError('recorded exchange pin')
        shutil.copyfile(fixtures / name, W / name)
    source = W / 'source'
    source.mkdir()
    for name in ('fd-client.h', 'fd-client.c', 'fd-client-tests.c', 'fd-protocol.h'):
        record['sources'][name] = sha(S / name)
        shutil.copyfile(S / name, source / name)
    tool_manifest = R / 'docs/evidence/filesystem-transport-2026-10-19/inputs.json'
    if sha(tool_manifest) != 'f200c7507b7fc300f9d4303191b0196acfa35dc7f9cffecd51e6a21e7933c82d':
        raise ValueError('tool manifest pin')
    pins = json.loads(tool_manifest.read_text())
    tools = {name: pins['tools'][name] for name in ('clang', 'clang-format')}
    record['tools'] = tools
    for tool in tools.values():
        if sha(Path(tool['path'])) != tool['sha256']:
            raise ValueError('tool pin')
    record['resource_headers'] = pins['clang_resource_headers']
    ubsan = Path('/opt/homebrew/Cellar/llvm@21/21.1.8/lib/clang/21/lib/darwin/libclang_rt.ubsan_osx_dynamic.dylib')
    runtime_digest = '7bfe170b03e5b9fb208d8568250aa84c35454933c306fe322c978295874c3746'
    record['ubsan'] = dict(path=str(ubsan), sha256=runtime_digest)
    for name, digest in record['resource_headers'].items():
        if sha(Path(name)) != digest:
            raise ValueError('resource header pin')
    if sha(ubsan) != runtime_digest:
        raise ValueError('UBSan pin')
    helper = R / 'experiments/command-runner/process.py'
    if sha(helper) != '9f0c0464c10fa23bfc7c3c91fe26b04e5ab063ca058eeb6d41542d98c6186e4e':
        raise ValueError('runner pin')
    proc = types.ModuleType('owned')
    exec(compile(helper.read_bytes(), str(helper), 'exec'), proc.__dict__)

    def run(label, argv, expected=0, timeout=60):
        result = proc.run(list(map(str, argv)), cwd=R, env=proc.clean_env(W),
                          work=W, label=label, timeout=timeout)
        record['rows'].append(dict(label=label, expected=expected,
                                   process=result.record))
        if (result.returncode != expected or not result.record['complete']
                or result.record['cleanup'] != 'complete'):
            raise RuntimeError(label)
        return result

    run('format', [tools['clang-format']['path'], '--dry-run', '--Werror',
        '--style=file:' + str(R / 'docs/quality/clang-format.yaml'),
        *[source / name for name in record['sources']]])
    target = run('target', [tools['clang']['path'], '-dumpmachine'])
    record['target'] = target.stdout.decode().strip()
    headers = run('headers', [tools['clang']['path'], '-std=c17', '-M',
        source / 'fd-client.c', source / 'fd-client-tests.c'])
    header_names = set()
    for line in headers.stdout.decode().replace('\\\n', ' ').splitlines():
        header_names.update(shlex.split(line.split(':', 1)[1]))
    record['sdk_headers'] = {name: sha(Path(name)) for name in sorted(header_names)}
    flags = ['-std=c17', '-Wall', '-Wextra', '-Wpedantic', '-Wconversion',
             '-Wsign-conversion', '-Wshadow', '-Wstrict-prototypes',
             '-Wmissing-prototypes', '-Werror', '-fsanitize=undefined',
             '-fno-sanitize-recover=all']

    def build(label, implementation):
        run(label, [tools['clang']['path'], *flags, implementation,
            source / 'fd-client-tests.c', '-I' + str(source), '-o', W / label])

    build('client', source / 'fd-client.c')
    baseline = run('tests', [W / 'client', W / 'requests.bin', W / 'replies.bin'], timeout=30)
    if baseline.stdout != b'1631 C client schedules pass\n':
        raise ValueError('schedule count')
    original = (source / 'fd-client.c').read_text()
    controls = {
        'skip-sequence': ('++client->sequence;', 'client->sequence += 0;'),
        'skip-wait-failure': ('if (client->io.wait(client->io.context, writing))',
                              'if (client->io.wait(client->io.context, writing) == 12345)'),
        'skip-budget': ('if (!*budget)', 'if (*budget == UINT32_MAX)'),
        'skip-body-validation':
            ('!aefd_body(client->workspace, client->workspace, incoming, reply.body)', '0'),
        'skip-retirement': ('client->live = 0;', 'client->live = 1;'),
        'skip-zeroing': ('memset(client->workspace, 0, AEFD_READ_MAX);',
                         '/* omitted failure clearing */'),
        'skip-local-shape': ('!shape(opcode, args, name_length)',
                             '(shape(opcode, args, name_length) == 12345)')}
    record['mutations'] = []
    assertions = {
        'skip-sequence': b'client.sequence == (uint64_t)i + 2',
        'skip-wait-failure': b'!expect_failure',
        'skip-budget': b'script.reads + script.writes == AEFD_IO_BUDGET',
        'skip-body-validation': b'!data[i]',
        'skip-retirement': b'!client->live',
        'skip-zeroing': b'!data[i]',
        'skip-local-shape': b'length, &reply) == 0'}
    for label, (old, new) in controls.items():
        if old not in original:
            raise ValueError('mutation target: ' + label)
        # Clear-on-abort is the first matching occurrence, not normal call setup.
        mutation = original.replace(old, new, 1)
        path = W / (label + '.c')
        path.write_text(mutation)
        record['mutations'].append(dict(label=label, old=old, new=new,
                                         sha256=sha(path)))
        build(label, path)
        failure = run(label + '-test', [W / label, W / 'requests.bin', W / 'replies.bin'],
                      expected=-6, timeout=30)
        if (b'Assertion failed:' not in failure.stderr
                or assertions[label] not in failure.stderr):
            raise ValueError('nonassertion failure: ' + label)
    for name, digest in record['sdk_headers'].items():
        if sha(Path(name)) != digest:
            raise ValueError('header drift')
    for name, digest in record['resource_headers'].items():
        if sha(Path(name)) != digest:
            raise ValueError('resource drift')
    if sha(ubsan) != runtime_digest:
        raise ValueError('runtime drift')
    for name, digest in record['sources'].items():
        if sha(S / name) != digest:
            raise ValueError('source drift')
    record.update(status='pass', schedules=1631, semantic_controls=len(controls),
                  binary_sha256=sha(W / 'client'))
except BaseException as error:
    record.update(status='failed', error=repr(error))
    raise
finally:
    (W / 'results.json').write_text(json.dumps(record, indent=2) + '\n')
    print(W)
