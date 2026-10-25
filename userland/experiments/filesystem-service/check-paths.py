# SPDX-License-Identifier: BSD-2-Clause
"""Focused offline root-path client checks; no VM or shell profile selection."""
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
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
W = Path(tempfile.mkdtemp(prefix='filesystem-root-paths-', dir=R / 'build'))
record = dict(format='aether-root-path-check-v1', status='incomplete', native_executed=False,
              sources={}, rows=[], work=str(W), python=sys.version)


def run(label, argv, expected=0, timeout=60):
    result = proc.run(list(map(str, argv)), cwd=R, env=env, work=W, label=label, timeout=timeout)
    row = dict(label=label, argv=result.record['argv'], expected=expected,
               exit=result.returncode, complete=result.record['complete'],
               cleanup=result.record['cleanup'], timeout_seconds=timeout,
               stdout_sha256=hashlib.sha256(result.stdout).hexdigest(),
               stderr_sha256=hashlib.sha256(result.stderr).hexdigest())
    record['rows'].append(row)
    if result.returncode != expected or not result.record['complete'] or result.record['cleanup'] != 'complete':
        row.update(stdout_prefix=result.stdout.decode(errors='replace')[:1800],
                   stdout_tail=result.stdout.decode(errors='replace')[-1800:],
                   stderr_tail=result.stderr.decode(errors='replace')[-1800:])
        raise RuntimeError(label)
    if expected:
        row['semantic_failure_excerpt'] = result.stdout.decode(errors='replace')[-800:]
    return result


def dependencies(directory, names):
    return ['-Ldependency=' + str(directory), *[part for name in names
            for part in ('--extern', name + '=' + str(directory / ('lib' + name + '.rlib')))]]


try:
    manifest = D / 'SHA256SUMS'
    if sha(manifest) != '98a9fd12db4ecd1c736fe3ce332c9b69c631e043d4d87313827145675ba230a8':
        raise ValueError('AF07 dependency pin')
    members = manifest.read_text().splitlines()
    for line in members:
        digest, name = line.split(maxsplit=1)
        if sha(D / name) != digest:
            raise ValueError('AF07 dependency member')
    record['dependency'] = dict(manifest_sha256=sha(manifest), members=len(members))
    prior = R / 'docs/evidence/filesystem-transport-2026-10-19/inputs.json'
    if sha(prior) != 'f200c7507b7fc300f9d4303191b0196acfa35dc7f9cffecd51e6a21e7933c82d':
        raise ValueError('tool manifest pin')
    pins = json.loads(prior.read_text());tools = pins['tools']
    for tool in tools.values():
        if sha(Path(tool['path'])) != tool['sha256']:
            raise ValueError('tool drift')
    for name, digest in pins['rust_native_libraries'].items():
        if sha(Path(name)) != digest:
            raise ValueError('native library drift')
    helper = R / 'experiments/command-runner/process.py'
    if sha(helper) != '9f0c0464c10fa23bfc7c3c91fe26b04e5ab063ca058eeb6d41542d98c6186e4e':
        raise ValueError('process helper pin')
    proc = types.ModuleType('owned')
    exec(compile(helper.read_bytes(), str(helper), 'exec'), proc.__dict__)
    env = proc.clean_env(W)
    env['DYLD_LIBRARY_PATH'] = str(Path(tools['rustc']['path']).parent.parent / 'lib')
    record.update(tools=tools, native_libraries=pins['rust_native_libraries'],
                  checker_sha256=sha(Path(__file__)), environment=env)
    shutil.copytree(D / 'source', W / 'source')
    names = ('client.rs', 'client-tests.rs', 'paths.rs', 'path-tests.rs',
             'file-descriptions.rs', 'remote-descriptors.rs', 'remote-descriptor-tests.rs')
    for name in names:
        record['sources'][name] = sha(S / name)
        shutil.copy2(S / name, W / 'source' / name)
    flags = ['--edition=2021', '-Dwarnings', '-Dunsafe_op_in_unsafe_fn']
    for option in ('namespace', 'lifetimes', 'mixed', 'wait', 'bulk', 'runtime', 'activation', 'names', 'directories', 'metadata'):
        flags += ['--cfg', 'fs_' + option]
    selected = [*flags, '--cfg', 'fs_paths']
    run('format', [tools['rustfmt']['path'], '--edition', '2021', '--check', '--config-path',
        R / 'docs/vendor/aether-approved-drafts/2026-09-05/drafts/coding-v0.1.0/configs/rustfmt.toml', *[S / name for name in names]])
    for stage, native in (('host', False), ('native', True)):
        directory = W / stage;directory.mkdir()
        extra = ['--target=x86_64-unknown-none', '-Cpanic=abort', '-Copt-level=2'] if native else []
        for name, source, imports in (
            ('filesystem_metadata', W / 'source/metadata-lib.rs', []),
            ('filesystem_policy', W / 'source/owner.rs', ['filesystem_metadata']),
            ('filesystem_service', W / 'source/service.rs', ['filesystem_policy']),
            ('filesystem_client', W / 'source/client.rs', ['filesystem_service']),
            ('filesystem_remote_descriptors', W / 'source/remote-descriptors.rs', ['filesystem_client', 'filesystem_service'])):
            run(stage + '-' + name, [tools['rustc']['path'], *selected, *extra,
                *dependencies(directory, imports), '--crate-type=lib', '--crate-name=' + name,
                *(['-Funsafe-code'] if name != 'filesystem_metadata' else []), source,
                '-o', directory / ('lib' + name + '.rlib')])
    host_deps = dependencies(W / 'host', ['filesystem_policy', 'filesystem_service'])
    for compiler in ('rustc', 'clippy-driver'):
        run(compiler + '-tests', [tools[compiler]['path'], *selected, *host_deps,
            '-Funsafe-code', '--test', W / 'source/client.rs', '-o', W / (compiler + '-tests')])
    tests = run('tests', [W / 'rustc-tests', '--test-threads=1'], timeout=30)
    if b'30 passed; 0 failed' not in tests.stdout:
        raise ValueError('missing/incomplete path tests')
    run('default-compile', [tools['rustc']['path'], *flags, *host_deps, '-Funsafe-code',
        '--test', W / 'source/client.rs', '-o', W / 'default-tests'])
    result = run('default-tests', [W / 'default-tests', '--test-threads=1'], timeout=30)
    if b'13 passed; 0 failed' not in result.stdout:
        raise ValueError('missing/incomplete default tests')
    remote_deps = dependencies(W / 'host', ['filesystem_policy', 'filesystem_service', 'filesystem_client'])
    for compiler in ('rustc', 'clippy-driver'):
        run(compiler + '-broker-build', [tools[compiler]['path'], *selected, *remote_deps,
            '-Funsafe-code', '--test', W / 'source/remote-descriptors.rs', '-o', W / (compiler + '-broker')])
    result = run('broker-tests', [W / 'rustc-broker', '--test-threads=1'], timeout=30)
    if b'9 passed; 0 failed' not in result.stdout:
        raise ValueError('missing/incomplete root-path broker tests')
    run('default-library', [tools['rustc']['path'], *flags, *host_deps, '-Funsafe-code',
        '--crate-type=lib', '--crate-name=filesystem_client', W / 'source/client.rs',
        '-o', W / 'host/libfilesystem_client_default.rlib'])
    default_remote_deps = [*host_deps, '--extern', 'filesystem_client=' + str(W / 'host/libfilesystem_client_default.rlib')]
    run('default-broker-build', [tools['rustc']['path'], *flags, *default_remote_deps, '-Funsafe-code',
        '--test', W / 'source/remote-descriptors.rs', '-o', W / 'default-broker'])
    result = run('default-broker-tests', [W / 'default-broker', '--test-threads=1'], timeout=30)
    if b'8 passed; 0 failed' not in result.stdout:
        raise ValueError('missing/incomplete default broker tests')
    run('default-broker-library', [tools['rustc']['path'], *flags, *default_remote_deps, '-Funsafe-code',
        '--crate-type=lib', '--crate-name=filesystem_remote_descriptors', W / 'source/remote-descriptors.rs',
        '-o', W / 'host/libfilesystem_remote_descriptors_default.rlib'])
    (W / 'layout.rs').write_text('''
use filesystem_service::{Channel, Message};
struct Probe;
impl Channel for Probe {
    fn send(&mut self,_:&Message)->Result<(),i64>{Err(-95)}
    fn receive(&mut self,_:&mut Message)->Result<(),i64>{Err(-95)}
    fn close(&mut self)->[i64;2]{[0;2]}
}
fn main(){println!("{} {} {} {}",core::mem::size_of::<filesystem_client::Client<Probe>>(),
    core::mem::align_of::<filesystem_client::Client<Probe>>(),
    core::mem::size_of::<filesystem_remote_descriptors::Descriptors<Probe>>(),
    core::mem::align_of::<filesystem_remote_descriptors::Descriptors<Probe>>());}
''')
    layouts = []
    for label, library in [('selected', 'libfilesystem_client.rlib'), ('default', 'libfilesystem_client_default.rlib')]:
        remote = 'libfilesystem_remote_descriptors' + ('_default' if label == 'default' else '') + '.rlib'
        run(label + '-layout-build', [tools['rustc']['path'], '--edition=2021', '-Dwarnings',
            *host_deps, '--extern', 'filesystem_client=' + str(W / 'host' / library),
            '--extern', 'filesystem_remote_descriptors=' + str(W / 'host' / remote),
            W / 'layout.rs', '-o', W / (label + '-layout')])
        layouts.append(run(label + '-layout', [W / (label + '-layout')]).stdout)
    if layouts[0] != layouts[1] or len(layouts[0].split()) != 4:
        raise ValueError('Client layout changed')
    record['host_client_and_descriptors_probe_size_align'] = list(map(int, layouts[0].split()))
    original = (W / 'source/paths.rs').read_text()
    mutations = {
        'leak-parent': ('self.close(previous)?;', 'let _ = previous;'),
        'skip-preflight': ('if self.bindings.iter()', 'if false && self.bindings.iter()'),
        'attenuate-parent': ('} else {\n                    3\n                }', '} else {\n                    1\n                }'),
        'accept-directory-as-file': ('if entry.kind == kind {', 'if true {'),
        'root-fallback': ('temporary.unwrap_or(directory)', 'temporary.unwrap_or(self.root()?)'),
        'ignore-base-kind': ('if binding.entry.kind != Kind::Directory {', 'if false && binding.entry.kind != Kind::Directory {'),
        'attenuate-directory-result': ('if final_part && kind == Kind::File {', 'if final_part {'),
        'accept-root-escape': ('part == b".."', 'part == b"not-dotdot"'),
    }
    for label, (old, new) in mutations.items():
        if original.count(old) != 1:
            raise ValueError('missing control: ' + label)
        (W / 'source/paths.rs').write_text(original.replace(old, new))
        run('compile-' + label, [tools['rustc']['path'], *selected, *host_deps, '-Funsafe-code',
            '--test', W / 'source/client.rs', '-o', W / label])
        rejected = run('reject-' + label, [W / label, '--test-threads=1'], expected=101, timeout=30)
        if b'test result: FAILED' not in rejected.stdout or b'assertion' not in rejected.stdout:
            raise ValueError('non-semantic control: ' + label)
    (W / 'source/paths.rs').write_text(original)
    for name, digest in record['sources'].items():
        if sha(S / name) != digest:
            raise ValueError('source changed')
    for tool in tools.values():
        if sha(Path(tool['path'])) != tool['sha256']:
            raise ValueError('tool changed')
    record.update(status='pass', selected_tests=30, default_tests=13, controls=8,
                  broker_tests=9, default_broker_tests=8,
                  native_library_sha256=sha(W / 'native/libfilesystem_client.rlib'),
                  native_library_bytes=(W / 'native/libfilesystem_client.rlib').stat().st_size,
                  native_broker_library_sha256=sha(W / 'native/libfilesystem_remote_descriptors.rlib'),
                  layout='No Client fields or backing/handle capacity added; concrete native owner fit remains unmeasured.')
except BaseException as error:
    record.update(status='failed', error=repr(error))
    raise
finally:
    report = W.with_suffix('.json')
    report.write_text(json.dumps(record, indent=2) + '\n')
    unresolved = any(row.get('cleanup') != 'complete' for row in record['rows'])
    if not unresolved:
        shutil.rmtree(W)
    print(json.dumps(dict(status=record['status'], report=str(report), cleanup_complete=not unresolved)))
