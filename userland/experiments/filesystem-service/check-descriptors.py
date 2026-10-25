# SPDX-License-Identifier: BSD-2-Clause
"""Owned host/no_std checks of read-only descriptions over pinned AF07 policy."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import types

R = Path(__file__).resolve().parents[2]
S = Path(__file__).resolve().parent
D = R / 'build/service-deliveries/filesystem-service-metadata-2026-10-21-v1'
W = Path(tempfile.mkdtemp(prefix='filesystem-descriptors-', dir=R / 'build'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if sha(D / 'SHA256SUMS') != '98a9fd12db4ecd1c736fe3ce332c9b69c631e043d4d87313827145675ba230a8':
    raise ValueError('AF07 dependency pin')
dependency = {}
for line in (D / 'SHA256SUMS').read_text().splitlines():
    digest, name = line.split(maxsplit=1)
    if sha(D / name) != digest:
        raise ValueError('AF07 member mismatch')
    dependency[name] = digest
inputs = json.loads((R / 'docs/evidence/filesystem-metadata-service-2026-10-21/inputs.json').read_text())
if (inputs['tools_from'] != 'docs/evidence/filesystem-transport-2026-10-19/inputs.json'
        or inputs['tools_manifest_sha256'] != 'f200c7507b7fc300f9d4303191b0196acfa35dc7f9cffecd51e6a21e7933c82d'):
    raise ValueError('selected tool manifest changed')
prior = R / inputs['tools_from']
if sha(prior) != inputs['tools_manifest_sha256']:
    raise ValueError('tool manifest pin')
pins = json.loads(prior.read_text())
tools = pins['tools']
for tool in tools.values():
    if sha(Path(tool['path'])) != tool['sha256']:
        raise ValueError('tool changed')
for name, digest in pins['rust_native_libraries'].items():
    if sha(Path(name)) != digest:
        raise ValueError('native Rust dependency changed')
helper = R / 'experiments/command-runner/process.py'
if sha(helper) != '9f0c0464c10fa23bfc7c3c91fe26b04e5ab063ca058eeb6d41542d98c6186e4e':
    raise ValueError('runner pin')
proc = types.ModuleType('owned')
exec(compile(helper.read_bytes(), str(helper), 'exec'), proc.__dict__)
record = dict(status='incomplete', work=str(W), python=sys.version,
              interpreter=dict(path=sys.executable, sha256=sha(Path(sys.executable))),
              dependency=dependency, tools=tools, native_executed=False,
              tool_manifest=dict(path=str(prior), sha256=sha(prior)),
              rust_native_libraries=pins['rust_native_libraries'],
              sources={}, rows=[])
shutil.copytree(D / 'source', W / 'source')
for name in ('descriptors.rs', 'descriptor-tests.rs', 'file-descriptions.rs'):
    record['sources'][name] = sha(S / name)
    shutil.copy2(S / name, W / 'source' / name)
record['checker_sha256'] = sha(Path(__file__))


def run(label, argv, expected=0, timeout=60):
    env = proc.clean_env(W)
    env['DYLD_LIBRARY_PATH'] = str(Path(tools['rustc']['path']).parent.parent / 'lib')
    result = proc.run(list(map(str, argv)), cwd=R, env=env, work=W,
                      label=label, timeout=timeout)
    record['rows'].append(dict(label=label, expected=expected, process=result.record))
    if result.returncode != expected or not result.record['complete'] or result.record['cleanup'] != 'complete':
        raise RuntimeError(label)
    return result


flags = ['--edition=2021', '-Dwarnings', '-Dunsafe_op_in_unsafe_fn']
for selection in ('namespace', 'lifetimes', 'mixed', 'wait', 'bulk', 'runtime',
                  'activation', 'names', 'directories', 'metadata'):
    flags += ['--cfg', 'fs_' + selection]


def dependencies(directory, names):
    args = ['-Ldependency=' + str(directory)]
    for name in names:
        args += ['--extern', name + '=' + str(directory / ('lib' + name + '.rlib'))]
    return args


try:
    run('format', [tools['rustfmt']['path'], '--edition', '2021', '--check',
        '--config-path', R / 'docs/vendor/aether-approved-drafts/2026-09-05/drafts/coding-v0.1.0/configs/rustfmt.toml',
        S / 'descriptors.rs', S / 'descriptor-tests.rs', S / 'file-descriptions.rs'])
    for stage, native in (('host', False), ('native', True)):
        directory = W / stage
        directory.mkdir()
        extra = ['--target=x86_64-unknown-none', '-Cpanic=abort', '-Copt-level=2'] if native else []
        for name, source, imports in (
            ('filesystem_metadata', D / 'source/metadata-lib.rs', []),
            ('filesystem_policy', D / 'source/owner.rs', ['filesystem_metadata']),
            ('filesystem_descriptors', S / 'descriptors.rs' if native else W / 'source/descriptors.rs', ['filesystem_policy'])):
            run(stage + '-' + name, [tools['rustc']['path'], *flags, *extra,
                *dependencies(directory, imports), '--crate-type=lib',
                '--crate-name=' + name,
                *(['-Funsafe-code'] if name != 'filesystem_metadata' else []),
                source, '-o', directory / ('lib' + name + '.rlib')])
    host_deps = dependencies(W / 'host', ['filesystem_policy'])
    for compiler in ('rustc', 'clippy-driver'):
        run(compiler + '-tests', [tools[compiler]['path'], *flags, *host_deps,
            '-Funsafe-code', '--test', W / 'source/descriptors.rs', '-o', W / (compiler + '-tests')])
    tests = run('tests', [W / 'rustc-tests', '--test-threads=1'], timeout=30)
    if b'12 passed; 0 failed' not in tests.stdout:
        raise ValueError('test count/outcome')
    mutations = {
        'skip-offset-advance': ('offset: file.offset + count as u64,', 'offset: file.offset,'),
        'close-shared-handle': ('.any(|other| other.description == binding.description)', '.any(|_| false)'),
        'skip-prevalidation-clearing': ('reply.fill(0);', '/* omitted clearing */'),
        'skip-retirement': ('self.retired = true;', 'self.retired = false;'),
        'close-unflagged-exec-fds': ('.is_some_and(|fd| fd.close_on_exec)', '.is_some()'),
        'lose-cloexec-setting': ('binding.close_on_exec = value;', 'binding.close_on_exec = !value;'),
        'overwrite-live-fd': ('.position(Option::is_none)', '.position(|_| true)'),
        'widen-read-offset-range': ('end > i64::MAX as u64', 'end > u64::MAX - 1'),
    }
    original = (W / 'source/file-descriptions.rs').read_text()
    record['mutations'] = []
    for label, (old, new) in mutations.items():
        if old not in original:
            raise ValueError('mutation target: ' + label)
        text = original.replace(old, new, 1)
        (W / 'source/file-descriptions.rs').write_text(text)
        row = dict(label=label, old=old, new=new,
                   source_sha256=sha(W / 'source/file-descriptions.rs'))
        record['mutations'].append(row)
        run('compile-' + label, [tools['rustc']['path'], *flags, *host_deps,
            '-Funsafe-code', '--test', W / 'source/descriptors.rs', '-o', W / label])
        result = run('reject-' + label, [W / label, '--test-threads=1'], expected=101, timeout=30)
        if b'test result: FAILED' not in result.stdout or b'assertion' not in result.stdout:
            raise ValueError('non-semantic rejection: ' + label)
    (W / 'source/file-descriptions.rs').write_text(original)
    for name, digest in record['sources'].items():
        if sha(S / name) != digest:
            raise ValueError('source changed')
    record['native_library_sha256'] = sha(W / 'native/libfilesystem_descriptors.rlib')
    record['status'] = 'pass'
except BaseException as error:
    record.update(status='failed', error=repr(error))
    raise
finally:
    (W / 'results.json').write_text(json.dumps(record, indent=2) + '\n')
    print(record['status'], W)
