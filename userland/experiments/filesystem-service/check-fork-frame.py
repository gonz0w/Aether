# SPDX-License-Identifier: BSD-2-Clause
"""Python3.10+ private owned AEFORK01 codec checks; no native transaction."""
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
W = Path(tempfile.mkdtemp(prefix='filesystem-fork-frame-', dir=R / 'build'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(root, digest):
    if sha(root / 'SHA256SUMS') != digest:
        raise ValueError('manifest pin: ' + str(root))
    members = {}
    for line in (root / 'SHA256SUMS').read_text().splitlines():
        expected, name = line.split('  ', 1)
        p = Path(name)
        if p.is_absolute() or '..' in p.parts or name in members:
            raise ValueError('manifest shape')
        if sha(root / p) != expected:
            raise ValueError('member pin: ' + name)
        members[name] = expected
    return members


record = dict(status='incomplete', python=sys.version, host=platform.platform(),
              interpreter=dict(path=sys.executable, sha256=sha(Path(sys.executable))),
              checker_sha256=sha(Path(__file__)), sources={}, rows=[],
              native_executed=False)
shutil.copyfile(Path(__file__), W / 'checker.py')
try:
    predecessor = R / 'build/service-deliveries/filesystem-fd-libc-2026-10-22-v1'
    predecessor_pin = '70f699d4e5a76cd2af547220598cbc52b78d7bb54b4ce8a21d44aa853daf1ac5'
    record['predecessor'] = verify(predecessor, predecessor_pin)
    source = W / 'source'
    shutil.copytree(predecessor / 'source', source)
    names = ['fd-fork-frame.h', 'fd-fork-frame.c', 'fd-fork-frame-tests.c']
    for name in names:
        record['sources'][name] = sha(S / name)
        shutil.copyfile(S / name, source / name)
    manifest = R / 'docs/evidence/filesystem-transport-2026-10-19/inputs.json'
    if sha(manifest) != 'f200c7507b7fc300f9d4303191b0196acfa35dc7f9cffecd51e6a21e7933c82d':
        raise ValueError('tool manifest pin')
    pins = json.loads(manifest.read_text())
    tools = {name: pins['tools'][name] for name in
             ['clang', 'clang-format', 'nm', 'readelf', 'lld']}
    record['tools'] = tools
    record['resource_headers'] = pins['clang_resource_headers']
    for tool in tools.values():
        if sha(Path(tool['path'])) != tool['sha256']:
            raise ValueError('tool changed')
    for path, digest in record['resource_headers'].items():
        if sha(Path(path)) != digest:
            raise ValueError('resource header changed')
    runtime = Path('/opt/homebrew/Cellar/llvm@21/21.1.8/lib/clang/21/lib/darwin/libclang_rt.ubsan_osx_dynamic.dylib')
    runtime_pin = '7bfe170b03e5b9fb208d8568250aa84c35454933c306fe322c978295874c3746'
    if sha(runtime) != runtime_pin:
        raise ValueError('UBSan runtime pin')
    record['ubsan'] = dict(path=str(runtime), sha256=runtime_pin)
    helper = R / 'experiments/command-runner/process.py'
    if sha(helper) != '9f0c0464c10fa23bfc7c3c91fe26b04e5ab063ca058eeb6d41542d98c6186e4e':
        raise ValueError('process helper pin')
    proc = types.ModuleType('owned')
    exec(compile(helper.read_bytes(), str(helper), 'exec'), proc.__dict__)

    def run(label, argv, expected=0, timeout=60):
        result = proc.run(list(map(str, argv)), cwd=R, env=proc.clean_env(W),
                          work=W, label=label, timeout=timeout)
        record['rows'].append(dict(label=label, expected=expected, process=result.record))
        if result.returncode != expected or not result.record['complete'] or result.record['cleanup'] != 'complete':
            raise RuntimeError(label)
        return result

    run('format', [tools['clang-format']['path'], '--dry-run', '--Werror',
        '--style=file:' + str(R / 'docs/quality/clang-format.yaml'),
        *[source / name for name in names]])
    flags = ['-std=c17', '-Wall', '-Wextra', '-Wpedantic', '-Wconversion',
             '-Wsign-conversion', '-Wshadow', '-Wstrict-prototypes',
             '-Wmissing-prototypes', '-Werror']
    host_flags = flags + ['-fsanitize=undefined', '-fno-sanitize-recover=all']
    deps = run('host-headers', [tools['clang']['path'], '-std=c17', '-M',
        source / 'fd-native.c', source / 'fd-fork-frame.c', source / 'fd-fork-frame-tests.c'])
    headers = set()
    for line in deps.stdout.decode().replace('\\\n', ' ').splitlines():
        headers.update(shlex.split(line.split(':', 1)[1]))
    record['host_headers'] = {name: sha(Path(name)) for name in sorted(headers)}

    def build(label, implementation):
        run(label + '-build', [tools['clang']['path'], *host_flags,
            source / 'fd-native.c', implementation, source / 'fd-fork-frame-tests.c',
            '-I' + str(source), '-o', W / label])

    build('codec', source / 'fd-fork-frame.c')
    observed = run('tests', [W / 'codec'], timeout=30)
    text = observed.stdout.decode()
    if not text.endswith(' fork-frame cases pass\n'):
        raise ValueError('test outcome')
    record['cases'] = int(text.split()[0])
    if record['cases'] < 4900:
        raise ValueError('missing boundary cases')
    original = (source / 'fd-fork-frame.c').read_text()
    controls = {
        'accept-stale-parent-reply': ('aefd_word(raw, 1) != sequence', '!sequence'),
        'ignore-ready-tail': ('!aefd_word(raw, 3)', '1'),
        'ignore-source-correspondence': ('!!(seen & (1U << i)) != !!sources[i].reference', 'seen == UINT32_MAX'),
        'lose-fork-cloexec': ('memmove(out, snapshot, AEFD_FORK_REQUEST_BYTES);', 'memmove(out, snapshot, AEFD_FORK_REQUEST_BYTES); out[126] = 0;'),
        'wrap-transaction-sequence': ('counter == out || *counter == UINT64_MAX', 'counter == out'),
        'reuse-child-file-generation': ('aefd_word(startup + 48, 1) == aefd_word(request + 48, 1)', 'aefd_word(startup + 48, 1) == 0'),
        'ignore-child-fd-correspondence': ('memcmp(startup + 112, request + 112, 64)', '0'),
        'accept-outside-private-errno': ('result < -4095', 'result < -4096'),
    }
    record['controls'] = []
    for label, (old, new) in controls.items():
        if original.count(old) != 1:
            raise ValueError('control target: ' + label)
        mutant = W / (label + '.c')
        mutant.write_text(original.replace(old, new, 1))
        build(label, mutant)
        rejected = run(label + '-test', [W / label], expected=-6, timeout=30)
        if b'Assertion failed:' not in rejected.stderr:
            raise ValueError('nonsemantic rejection: ' + label)
        record['controls'].append(dict(label=label, sha256=sha(mutant)))
    include = R / 'build/sdk-deliveries/native-service-runtime-2026-10-06-v2/sdk/stage/usr/include'
    record['native_headers'] = {str(p): sha(p) for p in sorted(include.rglob('*')) if p.is_file()}
    if record['native_headers'] != json.loads((predecessor / 'dependency.json').read_text())['native_header_pins']:
        raise ValueError('native header closure')
    native = W / 'native'
    native.mkdir()
    for unit in ['fd-native', 'fd-fork-frame']:
        run('native-' + unit, [tools['clang']['path'], *flags,
            '--target=x86_64-unknown-none', '-ffreestanding', '-fno-builtin',
            '-O2', '-fstack-usage', '-nostdinc', '-isystem', include,
            '-I' + str(source), '-c', source / (unit + '.c'), '-o', native / (unit + '.o')])
    run('native-link', [tools['lld']['path'], '-r', native / 'fd-native.o',
        native / 'fd-fork-frame.o', '-o', native / 'combined.o'])
    elf = run('native-elf', [tools['readelf']['path'], '-h', '-S', '-s', native / 'combined.o'])
    if b'ELF64' not in elf.stdout or b'X86-64' not in elf.stdout:
        raise ValueError('target object')
    symbols = run('native-imports', [tools['nm']['path'], '--undefined-only', native / 'combined.o'])
    record['native_imports'] = symbols.stdout.decode().splitlines()
    if {line.split()[-1] for line in record['native_imports']} - {'memcpy', 'memmove', 'memset', 'memcmp'}:
        raise ValueError('unexpected native imports')
    frames = []
    for path in native.glob('*.su'):
        for line in path.read_text().splitlines():
            parts = line.split('\t')
            if len(parts) != 3 or parts[2] != 'static':
                raise ValueError('nonstatic frame')
            frames.append(dict(function=parts[0], bytes=int(parts[1])))
    if not frames:
        raise ValueError('missing stack evidence')
    record['static_frames'] = frames
    for name, digest in record['sources'].items():
        if sha(S / name) != digest:
            raise ValueError('source changed')
    for name, digest in record['host_headers'].items():
        if sha(Path(name)) != digest:
            raise ValueError('host header changed')
    verify(predecessor, predecessor_pin)
    record['status'] = 'pass'
except BaseException as error:
    record.update(status='failed', error=repr(error))
    raise
finally:
    (W / 'results.json').write_text(json.dumps(record, indent=2) + '\n')
    print(record['status'], W)
