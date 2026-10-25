# SPDX-License-Identifier: BSD-2-Clause
"""Owned offline AF07 host/object checks; no guest or sibling mutations."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import types

R = Path(__file__).resolve().parents[2]
S = Path(__file__).resolve().parent
P = R / 'docs/evidence/filesystem-metadata-service-2026-10-21'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


inputs = json.loads((P / 'inputs.json').read_text())
prior = R / inputs['tools_from']
assert sha(prior) == inputs['tools_manifest_sha256']
pins = json.loads(prior.read_text())
for tool in pins['tools'].values():
    assert sha(Path(tool['path'])) == tool['sha256']
for name, digest in (pins['rust_native_libraries'] | pins['clang_resource_headers']).items():
    assert sha(Path(name)) == digest, name
for name, digest in inputs['engine_headers'].items():
    assert sha(P / 'headers' / name) == digest, name
for name, digest in inputs['old_deliveries'].items():
    assert sha(R / name / 'SHA256SUMS') == digest, name
    for line in (R / name / 'SHA256SUMS').read_text().splitlines():
        expected, member = line.split(maxsplit=1)
        assert sha(R / name / member) == expected, member
helper = R / 'experiments/command-runner/process.py'
assert sha(helper) == '9f0c0464c10fa23bfc7c3c91fe26b04e5ab063ca058eeb6d41542d98c6186e4e'
proc = types.ModuleType('owned')
exec(compile(helper.read_bytes(), str(helper), 'exec'), proc.__dict__)
W = Path(tempfile.mkdtemp(prefix='filesystem-metadata-service-', dir=R / 'build'))
tools = pins['tools']
rows = []
record = dict(status='running', root=str(W), rows=rows,
              python=sys.version, python_executable=sys.executable,
              python_sha256=sha(Path(sys.executable)), native_executed=False,
              full_engine_linked=False, input_sha256=sha(P / 'inputs.json'))


def run(label, argv, expected=0, timeout=60):
    env = proc.clean_env(W)
    if Path(str(argv[0])).name in ('rustc', 'clippy-driver', 'rustfmt'):
        env['DYLD_LIBRARY_PATH'] = str(Path(tools['rustc']['path']).parent.parent / 'lib')
    result = proc.run(list(map(str, argv)), cwd=R, env=env, work=W,
                      label=label, timeout=timeout)
    rows.append(dict(name=label, expected=expected, process=result.record))
    assert result.returncode == expected and result.record['complete'] and result.record['cleanup'] == 'complete', label
    return result


FLAGS = ['--edition=2021', '-Dwarnings', '-Dunsafe_op_in_unsafe_fn']
for selection in ('namespace', 'lifetimes', 'mixed', 'wait', 'bulk', 'runtime',
                  'activation', 'names', 'directories', 'metadata'):
    FLAGS += ['--cfg', 'fs_' + selection]
CRATES = [
    ('filesystem_metadata', 'metadata-lib.rs', []),
    ('filesystem_policy', 'owner.rs', ['filesystem_metadata']),
    ('filesystem_bridge', 'bridge.rs', ['filesystem_policy', 'filesystem_metadata']),
    ('filesystem_service', 'service.rs', ['filesystem_policy']),
    ('filesystem_activation', 'activation.rs', ['filesystem_policy', 'filesystem_service']),
]


def deps(directory, names):
    args = ['-Ldependency=' + str(directory)]
    for name in names:
        args += ['--extern', name + '=' + str(directory / ('lib' + name + '.rlib'))]
    return args


def build(directory, label, native=False, lint=False):
    compiler = tools['clippy-driver' if lint else 'rustc']['path']
    extra = (['--target=x86_64-unknown-none', '-Cpanic=abort', '-Copt-level=2',
              '-Crelocation-model=static', '-Ccodegen-units=1'] if native else [])
    source_directory = S if native else directory
    for name, source, imports in CRATES:
        output = directory / ('lib' + name + '.rlib')
        emission = (['--emit=link=' + str(output) + ',obj=' + str(directory / (name + '.o'))]
                    if native else ['-o', output])
        run(label + '-' + name, [compiler, *FLAGS, *extra,
            *deps(directory, imports), '--crate-name=' + name,
            *(['-Funsafe-code'] if name in ('filesystem_policy', 'filesystem_service', 'filesystem_activation') else []),
            '--crate-type=lib', source_directory / source, *emission])
    if not native:
        run(label + '-entry-tests', [compiler, *FLAGS,
            *deps(directory, [c[0] for c in CRATES]), '--test',
            directory / 'native-service.rs', '-Clink-arg=' + str(W / 'fixture.o'),
            '-o', directory / ('clippy-tests' if lint else 'tests')])
    else:
        run(label + '-entry', [compiler, *FLAGS, *extra,
            *deps(directory, [c[0] for c in CRATES]), '--crate-type=lib',
            '--crate-name=filesystem_native_service', source_directory / 'native-service.rs',
            '--emit=obj', '-o', directory / 'entry.o'])


try:
    changed = ['owner.rs', 'bridge.rs', 'service.rs', 'native-service.rs',
               'names-service.rs', 'directory-service-tests.rs', 'metadata-lib.rs',
               'metadata-policy.rs', 'metadata-service.rs', 'metadata-service-tests.rs']
    if sys.argv[1:] == ['--format']:
        run('format', [tools['rustfmt']['path'], '--edition=2021', *[S / n for n in changed]])
        run('c-format', [tools['clang-format']['path'], '-i',
                         '--style=file:docs/quality/clang-format.yaml',
                         S / 'metadata-fixture.c', S / 'metadata-service.h'])
    elif sys.argv[1:]:
        raise ValueError('internal recipe accepts only --format')
    assert sha(S / 'metadata.rs') == inputs['local_before']['experiments/filesystem-service/metadata.rs']
    record['sources'] = {str(f.relative_to(R)): sha(f) for f in S.iterdir()
                         if f.is_file() and f.suffix in ('.rs', '.c', '.h', '.py', '.json')}
    for name in record['sources']:
        shutil.copy2(R / name, W / Path(name).name)
    run('rustfmt', [tools['rustfmt']['path'], '--edition=2021', '--check', *[S / n for n in changed]])
    run('c-format-check', [tools['clang-format']['path'], '--dry-run', '--Werror',
        '--style=file:docs/quality/clang-format.yaml', S / 'metadata-fixture.c', S / 'metadata-service.h'])
    sdk = run('host-sdk', ['/usr/bin/xcrun', '--show-sdk-path']).stdout.decode().strip()
    record['host_sdk'] = sdk
    run('fixture', [tools['clang']['path'], '-std=c17', '-Wall', '-Wextra', '-Werror',
        '-isysroot', sdk, '-I' + str(P / 'headers'),
        '-I' + str(R / 'docs/evidence/filesystem-bridge-2026-10-18'),
        '-I' + str(W), '-c', W / 'metadata-fixture.c', '-o', W / 'fixture.o'])
    build(W, 'host')
    observed = run('host-tests', [W / 'tests', '--test-threads=1'], timeout=30)
    assert '23 passed; 0 failed' in observed.stdout.decode()
    build(W, 'clippy', lint=True)
    omissions = {
        'metadata-right': ('metadata-policy.rs', '!opened.rights.contains(Rights::METADATA)', 'false'),
        'metadata-retirement': ('metadata-policy.rs', 'self.retire();', 'let _ = ();'),
        'policy-size': ('metadata-policy.rs', 'value.node.size != opened.node.size', 'false'),
        'raw-id': ('metadata-service.rs', 'value.uid,', 'value.uid as u32 as u64,'),
        'signed-time': ('metadata-service.rs', 'value.mtime.seconds as u64,', 'value.mtime.seconds as u32 as u64,'),
        'wire-version': ('metadata-service.rs', 'raw[..8] != MAGIC[..]', 'false'),
        'reserved': ('metadata-service.rs', 'raw[32..].iter().any(|byte| *byte != 0)', 'false'),
        'reply-body': ('names-service.rs', '(cfg!(fs_metadata) && opcode == 12)\n                || (cfg!(fs_directory_contexts) && opcode == 14))', 'false\n                || (cfg!(fs_directory_contexts) && opcode == 14))'),
    }
    for label, (file, old, new) in omissions.items():
        folder = W / label
        folder.mkdir()
        for f in W.glob('*.rs'):
            text = f.read_text()
            if f.name == file:
                assert text.count(old) == (2 if label == 'metadata-retirement' else 1), (label, old)
                text = text.replace(old, new)
            (folder / f.name).write_text(text)
        build(folder, label)
        rejected = run('reject-' + label, [folder / 'tests', '--test-threads=1'], expected=101, timeout=30)
        assert 'test result: FAILED.' in rejected.stdout.decode()
    native = W / 'native'
    native.mkdir()
    for f in W.glob('*.rs'):
        shutil.copy2(f, native / f.name)
    build(native, 'native', native=True)
    build(native, 'native-clippy', native=True, lint=True)
    run('link', [tools['lld']['path'], '-r', *sorted(native.glob('*.o')),
                 '-o', W / 'filesystem-metadata.o'])
    symbols = run('symbols', [tools['nm']['path'], '--defined-only', W / 'filesystem-metadata.o']).stdout.decode()
    assert sum(line.split()[-1:] == ['aether_fs_metadata_run'] for line in symbols.splitlines()) == 1
    assert not any(line.split()[-1:] == ['aether_fs_directories_run'] for line in symbols.splitlines())
    imports = run('imports', [tools['nm']['path'], '--undefined-only', W / 'filesystem-metadata.o']).stdout.decode()
    assert 'aether_zpl_getattr' in imports
    layout = W / 'layout.c'
    layout.write_text('#include "metadata-service.h"\n'
        '_Static_assert(sizeof(struct aether_fs_service_result)==72,"size");\n'
        '_Static_assert(_Alignof(struct aether_fs_service_result)==8,"alignment");\n'
        '_Static_assert(offsetof(struct aether_fs_service_result,txg)==48,"offset");\n'
        'int (*entry)(void*,const unsigned char*,size_t,uint64_t,uint64_t,uint64_t,uint64_t,uint64_t,struct aether_fs_service_result*)=aether_fs_metadata_run;\n')
    run('native-c-layout', [tools['clang']['path'], '--target=x86_64-unknown-none',
        '-ffreestanding', '-std=c17', '-Wall', '-Wextra', '-Werror',
        '-I' + str(W), '-c', layout, '-o', W / 'layout.o'])
    packed = run('native-c-packed', [tools['clang']['path'],
        '--target=x86_64-unknown-none', '-ffreestanding', '-std=c17',
        '-fpack-struct=1', '-I' + str(W), '-c', layout,
        '-o', W / 'packed.o'], expected=1)
    assert 'static assertion failed' in packed.stderr.decode()
    record.update(status='pass', host_tests=23, semantic_omissions=len(omissions),
                  native_object_sha256=sha(W / 'filesystem-metadata.o'), imports=imports)
    for name, digest in record['sources'].items():
        assert sha(R / name) == digest, name
except BaseException as error:
    record.update(status='failed', error=repr(error))
    raise
finally:
    (W / 'results.json').write_text(json.dumps(record, indent=2) + '\n')
    print('Filesystem metadata service check:', record['status'], W)
