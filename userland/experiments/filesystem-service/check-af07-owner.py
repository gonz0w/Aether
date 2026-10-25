# SPDX-License-Identifier: BSD-2-Clause
"""Owned offline AF07 launch-owner checks; no engine build or VM."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import types

R = Path(__file__).resolve().parents[2]
S = Path(__file__).resolve().parent
P = R / 'docs/evidence/filesystem-af07-owner-2026-10-21'
sha = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
inputs = json.loads((P / 'inputs.json').read_text())
D = R / inputs['dependency']
assert sha(D / 'SHA256SUMS') == inputs['dependency_manifest']
for line in (D / 'SHA256SUMS').read_text().splitlines():
    digest, name = line.split(maxsplit=1)
    assert sha(D / name) == digest, name
for name, digest in inputs['local_before'].items():
    assert sha(S / name) == digest, name
for name, digest in inputs['producer'].items():
    assert sha(P / 'producer' / name) == digest, name
pins = json.loads((D / 'inputs.json').read_text())
tools = pins['tools']
for tool in tools.values():
    assert sha(Path(tool['path'])) == tool['sha256']
for name, digest in (pins['rust_native_libraries'] | pins['clang_resource_headers']).items():
    assert sha(Path(name)) == digest, name
helper = R / 'experiments/command-runner/process.py'
assert sha(helper) == '9f0c0464c10fa23bfc7c3c91fe26b04e5ab063ca058eeb6d41542d98c6186e4e'
proc = types.ModuleType('owned')
exec(compile(helper.read_bytes(), str(helper), 'exec'), proc.__dict__)
W = Path(tempfile.mkdtemp(prefix='filesystem-af07-owner-', dir=R / 'build'))
record = dict(status='running', root=str(W), python=sys.version,
              python_executable=sys.executable, python_sha256=sha(Path(sys.executable)),
              input_sha256=sha(P / 'inputs.json'), rows=[], native_executed=False,
              full_engine_linked=False)


def run(label, argv, expected=0, timeout=60):
    env = proc.clean_env(W)
    if Path(str(argv[0])).name in ('rustc', 'rustfmt', 'clippy-driver'):
        env['DYLD_LIBRARY_PATH'] = str(Path(tools['rustc']['path']).parent.parent / 'lib')
    result = proc.run(list(map(str, argv)), cwd=R, env=env, work=W,
                      label=label, timeout=timeout)
    record['rows'].append(dict(name=label, expected=expected, process=result.record))
    assert result.returncode == expected and result.record['complete'] and result.record['cleanup'] == 'complete', label
    return result


try:
    sources = [S / 'launch-metadata-owner.rs', S / 'launch-metadata-owner-tests.rs']
    if sys.argv[1:] == ['--format']:
        run('format', [tools['rustfmt']['path'], '--edition=2021', *sources])
    elif sys.argv[1:]:
        raise ValueError('internal recipe accepts only --format')
    record['sources'] = {str(f.relative_to(R)): sha(f) for f in [*sources, Path(__file__)]}
    for f in [*sources, Path(__file__)]:
        shutil.copy2(f, W / f.name)
    run('format-check', [tools['rustfmt']['path'], '--edition=2021', '--check', *sources])
    common = ['--edition=2021', '-Dwarnings', '-Dunsafe_op_in_unsafe_fn']
    for label, tool in [('host', 'rustc'), ('clippy', 'clippy-driver')]:
        run(label + '-compile', [tools[tool]['path'], *common, '--test', sources[0], '-o', W / label])
    observed = run('host-tests', [W / 'host', '--test-threads=1'], timeout=30)
    assert '8 passed; 0 failed' in observed.stdout.decode()
    # Preserve selected AF06 source and actual host behavior as a separate check.
    run('af06-tests-compile', [tools['rustc']['path'], *common, '--test', S / 'launch-owner.rs', '-o', W / 'af06'])
    legacy = run('af06-tests', [W / 'af06', '--test-threads=1'], timeout=30)
    assert '5 passed; 0 failed' in legacy.stdout.decode()
    source = sources[0].read_text()
    omissions = {
        'error': ('if error != 0 {', 'if error != 0 { return 0;'),
        'phases': ('state.phases != FINISHED', '(state.phases != FINISHED && false)'),
        'writer-close': ('service.writer_close != 0', '(service.writer_close != 0 && false)'),
        'startup-close': ('state.phases & ENTERED == 0 && service_unobserved', 'state.phases & ENTERED != 0 && service_unobserved'),
        'entered': ('|| state.phases & ENTERED == 0', '|| (state.phases & ENTERED == 0 && false)'),
        'metadata-right': ('            31,', '            15,'),
        'progress': ('|| !progress_valid', '|| (!progress_valid && false)'),
        'request': ('|| service.requests == 0', '|| (service.requests == 0 && false)'),
        'ambiguous-close': ('&& service_unobserved {', '&& { let _ = service_unobserved; true } {'),
    }
    for label, (old, new) in omissions.items():
        assert source.count(old) == 1, label
        mutant = W / (label + '.rs')
        mutant.write_text(source.replace(old, new, 1))
        run('compile-' + label, [tools['rustc']['path'], '--edition=2021',
            '-Dunsafe_op_in_unsafe_fn', '--test', mutant, '-o', W / ('test-' + label)])
        rejected = run('reject-' + label, [W / ('test-' + label), '--test-threads=1'], expected=101, timeout=30)
        assert 'test result: FAILED.' in rejected.stdout.decode(), label
    native = ['--target=x86_64-unknown-none', '--crate-type=lib', '--emit=obj',
              '-Cpanic=abort', '-Copt-level=2', '-Crelocation-model=static', '-Cno-redzone=yes', '-Ccodegen-units=1']
    for label, tool in [('native', 'rustc'), ('native-clippy', 'clippy-driver')]:
        run(label, [tools[tool]['path'], *common, *native, sources[0], '-o', W / (label + '.o')])
    record['native_clippy_sha256'] = sha(W / 'native-clippy.o')
    record['compiler_variant_bytes_equal'] = sha(W / 'native.o') == sha(W / 'native-clippy.o')
    symbols = run('defined', [tools['nm']['path'], '--defined-only', W / 'native.o']).stdout.decode()
    for name in ['main', 'aether_fs_launch_serve']:
        assert sum(line.split()[-1:] == [name] for line in symbols.splitlines()) == 1
    imports = run('imports', [tools['nm']['path'], '--undefined-only', W / 'native.o']).stdout.decode()
    for name in ['aether_fs_engine_run', 'aether_fs_metadata_run', 'getauxval']:
        assert name in imports, name
    assert 'aether_fs_directories_run' not in imports
    run('elf', [tools['readelf']['path'], '-h', W / 'native.o'])
    run('sections', [tools['readelf']['path'], '-S', '--wide', W / 'native.o'])
    run('af06-native', [tools['rustc']['path'], *common, *native, S / 'launch-owner.rs', '-o', W / 'af06-native.o'])
    duplicate = run('duplicate-owner', [tools['lld']['path'], '-r', W / 'native.o',
        W / 'af06-native.o', '-o', W / 'duplicate.o'], expected=1)
    assert 'duplicate symbol: main' in duplicate.stderr.decode()
    assert 'duplicate symbol: aether_fs_launch_serve' in duplicate.stderr.decode()
    layout = W / 'layout.c'
    layout.write_text('#include "filesystem-engine.h"\n#include "metadata-service.h"\n'
        '_Static_assert(sizeof(struct aether_fs_service_result)==72,"result");\n'
        '_Static_assert(_Alignof(struct aether_fs_launch_state)==8,"align");\n'
        '_Static_assert(offsetof(struct aether_fs_launch_state,engine_error)==40,"error");\n'
        '_Static_assert(offsetof(struct aether_fs_launch_state,startup_reader_close)==120,"reader");\n'
        '_Static_assert(offsetof(struct aether_fs_launch_state,startup_writer_close)==128,"writer");\n')
    cflags = ['--target=x86_64-unknown-none', '-ffreestanding', '-std=c17',
              '-Wall', '-Wextra', '-Werror', '-I' + str(D / 'source'),
              '-I' + str(P / 'producer/user/storage/service-runtime')]
    run('layout', [tools['clang']['path'], *cflags, '-c', layout, '-o', W / 'layout.o'])
    packed = run('reject-packed', [tools['clang']['path'], *cflags, '-fpack-struct=1', '-c', layout, '-o', W / 'packed.o'], expected=1)
    assert 'static assertion failed' in packed.stderr.decode()
    # Typed symbol-only doubles, never executed or distributed as an engine.
    stub = W / 'stub.c'
    stub.write_text('#include "metadata-service.h"\n'
        'int ENTRY(void*a,const unsigned char*b,size_t c,uint64_t d,uint64_t e,uint64_t f,uint64_t g,uint64_t h,struct aether_fs_service_result*i)'
        '{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;(void)g;(void)h;(void)i;return 5;}\n')
    for label, entry in [('matched', 'aether_fs_metadata_run'), ('old', 'aether_fs_directories_run')]:
        run(label + '-stub', [tools['clang']['path'], *cflags, '-DENTRY=' + entry,
            '-c', stub, '-o', W / (label + '.o')])
        run(label + '-partial-link', [tools['lld']['path'], '-r', W / 'native.o', W / (label + '.o'), '-o', W / (label + '-partial.o')])
        unresolved = run(label + '-imports', [tools['nm']['path'], '--undefined-only', W / (label + '-partial.o')]).stdout.decode()
        assert ('aether_fs_metadata_run' in unresolved) == (label == 'old')
    for name, digest in record['sources'].items():
        assert sha(R / name) == digest, name
    for name, digest in inputs['local_before'].items():
        assert sha(S / name) == digest, name
    record.update(status='pass', host_tests=8, legacy_host_tests=5,
        semantic_omissions=len(omissions), native_object_sha256=sha(W / 'native.o'),
        native_imports=imports, native_object_bytes=(W / 'native.o').stat().st_size)
except BaseException as error:
    record.update(status='failed', error=repr(error))
    raise
finally:
    (W / 'results.json').write_text(json.dumps(record, indent=2) + '\n')
    print('AF07 operational owner check:', record['status'], W)
