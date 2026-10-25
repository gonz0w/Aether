# SPDX-License-Identifier: BSD-2-Clause
"""Python3.10+ owned C17 tagged startup snapshot checks; no native execution."""
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
W = Path(tempfile.mkdtemp(prefix='filesystem-fd-bindings-', dir=R / 'build'))


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
    selected = R / 'build/service-deliveries/filesystem-fd-client-2026-10-21-v1'
    record['client'] = verified_manifest(
        selected, 'eac972b501518c97f67d483aafe6186ea2b5863dfaad26930108d4d7d290c48c')
    source = W / 'source'
    source.mkdir()
    for name in ('fd-bindings.h', 'fd-bindings-tests.c'):
        record['sources'][name] = sha(S / name)
        shutil.copyfile(S / name, source / name)
    name = 'fd-protocol.h'
    shutil.copyfile(selected / 'source' / name, source / name)
    record['sources'][name] = sha(source / name)
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
        source / 'fd-bindings-tests.c'])
    header_names = set()
    for line in headers.stdout.decode().replace('\\\n', ' ').splitlines():
        header_names.update(shlex.split(line.split(':', 1)[1]))
    record['sdk_headers'] = {name: sha(Path(name)) for name in sorted(header_names)}
    flags = ['-std=c17', '-Wall', '-Wextra', '-Wpedantic', '-Wconversion',
             '-Wsign-conversion', '-Wshadow', '-Wstrict-prototypes',
             '-Wmissing-prototypes', '-Werror', '-fsanitize=undefined',
             '-fno-sanitize-recover=all']

    def build(label, directory):
        run(label, [tools['clang']['path'], *flags,
            directory / 'fd-bindings-tests.c', '-I' + str(directory), '-o', W / label])

    build('bindings', source)
    baseline = run('tests', [W / 'bindings'], timeout=30)
    if baseline.stdout != b'65951 tagged binding cases pass\n':
        raise ValueError('binding case count')
    original = (source / 'fd-bindings.h').read_text()
    controls = {
        'skip-generation': ('aefd_word(raw, 1) != generation',
                             'aefd_word(raw, 1) == UINT64_MAX', b'!aefd_bindings_decode'),
        'skip-reserved': ('if (aefd_word(raw, i))',
                          'if (aefd_word(raw, i) == UINT64_MAX)', b'!aefd_bindings_decode'),
        'skip-file-uniqueness': ('value.slots[j].kind == AEFD_BIND_FILE',
                                 'value.slots[j].kind == 255', b'!aefd_bindings_decode'),
        'widen-pipe-selector': ('return slot.selector >= 3 && slot.selector <= 6;',
                                'return slot.selector <= 15;', b'== expected'),
        'lose-class': ('*out = slot;', 'slot.kind = AEFD_BIND_FILE; *out = slot;',
                       b'pipe.kind == AEFD_BIND_PIPE')}
    record['mutations'] = []
    for label, (old, new, assertion) in controls.items():
        if old not in original:
            raise ValueError('mutation target: ' + label)
        directory = W / (label + '-source')
        directory.mkdir()
        for name in record['sources']:
            shutil.copyfile(source / name, directory / name)
        path = directory / 'fd-bindings.h'
        path.write_text(original.replace(old, new, 1))
        record['mutations'].append(dict(label=label, old=old, new=new,
                                         sha256=sha(path)))
        build(label, directory)
        failure = run(label + '-test', [W / label], expected=-6, timeout=30)
        if (b'Assertion failed:' not in failure.stderr or assertion not in failure.stderr):
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
        if sha(source / name) != digest or sha(S / name) != digest:
            raise ValueError('source drift')
    record.update(status='pass', cases=65951, semantic_controls=len(controls),
                  binary_sha256=sha(W / 'bindings'))
except BaseException as error:
    record.update(status='failed', error=repr(error))
    raise
finally:
    (W / 'results.json').write_text(json.dumps(record, indent=2) + '\n')
    print(W)
