# SPDX-License-Identifier: BSD-2-Clause
"""Owned host/no_std checks of AEFD0001 file RPC over pinned process views."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import types
import platform
import shlex

R = Path(__file__).resolve().parents[2]
S = Path(__file__).resolve().parent
D = R / 'build/service-deliveries/filesystem-service-metadata-2026-10-21-v1'
class Parser(argparse.ArgumentParser):
    def error(self,message):self.exit(1,message+'\n')
parser=Parser(description=__doc__)
parser.add_argument('--paths',action='store_true')
parser.add_argument('--dup2',action='store_true',help='select matched16-slot FILE replacement wire; requires --paths')
options=parser.parse_args()
if options.dup2 and not options.paths:parser.error('--dup2 requires --paths')
path_wire=options.paths
W = Path(tempfile.mkdtemp(prefix='filesystem-fd-wire-', dir=R / 'build'))
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
for name, digest in pins['clang_resource_headers'].items():
    if sha(Path(name)) != digest:
        raise ValueError('Clang resource input changed')
ubsan = Path('/opt/homebrew/Cellar/llvm@21/21.1.8/lib/clang/21/lib/darwin/libclang_rt.ubsan_osx_dynamic.dylib')
if sha(ubsan) != '7bfe170b03e5b9fb208d8568250aa84c35454933c306fe322c978295874c3746':
    raise ValueError('host UBSan runtime pin')
helper = R / 'experiments/command-runner/process.py'
if sha(helper) != '9f0c0464c10fa23bfc7c3c91fe26b04e5ab063ca058eeb6d41542d98c6186e4e':
    raise ValueError('runner pin')
proc = types.ModuleType('owned')
exec(compile(helper.read_bytes(), str(helper), 'exec'), proc.__dict__)
record = dict(status='incomplete', work=str(W), python=sys.version,
              interpreter=dict(path=sys.executable, sha256=sha(Path(sys.executable))),
              dependency=dependency, tools=tools, native_executed=False, path_wire=path_wire, dup2_wire=options.dup2,
              tool_manifest=dict(path=str(prior), sha256=sha(prior)),
              rust_native_libraries=pins['rust_native_libraries'],
              host_environment=dict(platform=platform.platform(), machine=platform.machine(), mac_version=platform.mac_ver()),
              clang_resource_headers=pins['clang_resource_headers'],
              ubsan_runtime=dict(path=str(ubsan), sha256=sha(ubsan)),
              sources={}, rows=[])
shutil.copytree(D / 'source', W / 'source')
for name in ('client.rs', 'client-tests.rs', 'paths.rs', 'path-tests.rs', 'file-descriptions.rs', 'remote-descriptors.rs', 'remote-descriptor-tests.rs', 'process-descriptors.rs', 'process-descriptor-tests.rs', 'process-fd-fixture.rs', 'vendor/abi29-startup.rs', 'fd-protocol.rs', 'fd-protocol-tests.rs', 'fd-dup2-wire-tests.rs', 'fd-protocol.h', 'fd-protocol-fixture.c', 'fd-wire-fixture.rs'):
    record['sources'][name] = sha(S / name)
    (W / 'source' / name).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(S / name, W / 'source' / name)
if sha(S / 'vendor/abi29-startup.rs') != 'ba23cba7730e8c10c7f0ea0ccf68a227b71ac70890a72c475ff892d13136e704':
    raise ValueError('ABI29 identity input pin')
record['checker_sha256'] = sha(Path(__file__))


def run(label, argv, expected=0, timeout=60):
    env = proc.clean_env(W)
    if any(str(argv[0]) == tools[name]['path'] for name in ('rustc', 'rustfmt', 'clippy-driver')):
        env['DYLD_LIBRARY_PATH'] = str(Path(tools['rustc']['path']).parent.parent / 'lib')
    env['AEFD_C_REQUESTS'] = str(W / 'requests.bin')
    env['AEFD_RUST_REPLIES'] = str(W / (label + '-replies.bin'))
    result = proc.run(list(map(str, argv)), cwd=R, env=env, work=W,
                      label=label, timeout=timeout)
    record['rows'].append(dict(label=label, expected=expected, process=result.record))
    if result.returncode != expected or not result.record['complete'] or result.record['cleanup'] != 'complete':
        raise RuntimeError(label)
    return result


flags = ['--edition=2021', '-Dwarnings', '-Dunsafe_op_in_unsafe_fn']
for selection in ('namespace', 'lifetimes', 'mixed', 'wait', 'bulk', 'runtime',
                  'activation', 'names', 'directories', 'metadata', 'process_views'):
    flags += ['--cfg', 'fs_' + selection]
if options.dup2:
    flags += ['--cfg','fs_file16','--cfg','fs_replace','--cfg','fs_dup2_wire']
if path_wire:
    flags += ['--cfg', 'fs_paths', '--cfg', 'fs_path_wire']


def dependencies(directory, names):
    args = ['-Ldependency=' + str(directory)]
    for name in names:
        args += ['--extern', name + '=' + str(directory / ('lib' + name + '.rlib'))]
    return args


try:
    run('format', [tools['rustfmt']['path'], '--edition', '2021', '--check',
        '--config-path', R / 'docs/vendor/aether-approved-drafts/2026-09-05/drafts/coding-v0.1.0/configs/rustfmt.toml',
        *[S / name for name in record['sources'] if name.endswith('.rs')]])
    for stage, native in (('host', False), ('native', True)):
        directory = W / stage
        directory.mkdir()
        extra = ['--target=x86_64-unknown-none', '-Cpanic=abort', '-Copt-level=2'] if native else []
        for name, source, imports in (
            ('filesystem_metadata', D / 'source/metadata-lib.rs', []),
            ('filesystem_policy', D / 'source/owner.rs', ['filesystem_metadata']),
            ('filesystem_service', D / 'source/service.rs', ['filesystem_policy']),
            ('filesystem_client', S / 'client.rs' if native else W / 'source/client.rs', ['filesystem_service']),
            ('filesystem_remote_descriptors', S / 'remote-descriptors.rs' if native else W / 'source/remote-descriptors.rs', ['filesystem_client', 'filesystem_service']),
            ('filesystem_fd_protocol', S / 'fd-protocol.rs' if native else W / 'source/fd-protocol.rs', ['filesystem_client', 'filesystem_service', 'filesystem_remote_descriptors'])):
            run(stage + '-' + name, [tools['rustc']['path'], *flags, *extra,
                *dependencies(directory, imports), '--crate-type=lib',
                '--crate-name=' + name,
                *(['-Funsafe-code'] if name != 'filesystem_metadata' else []),
                source, '-o', directory / ('lib' + name + '.rlib')])
    host_deps = dependencies(W / 'host', ['filesystem_policy', 'filesystem_service', 'filesystem_client', 'filesystem_remote_descriptors'])
    mismatch = [v for v in flags if v != 'fs_path_wire']
    if path_wire:
        # Remove the now orphaned final --cfg, not a required runtime option.
        mismatch = mismatch[:-1]
    else:
        mismatch += ['--cfg', 'fs_paths', '--cfg', 'fs_path_wire']
    rejected = run('reject-mismatched-broker', [tools['rustc']['path'], *mismatch, *host_deps,
        '--crate-type=lib', '--crate-name=mismatch', W / 'source/fd-protocol.rs',
        '-o', W / 'mismatch.rlib'], expected=1)
    if b'E0080' not in rejected.stderr or b'ROOT_PATHS' not in rejected.stderr:
        raise ValueError('wrong broker selection rejection')

    for compiler in ('rustc', 'clippy-driver'):
        run(compiler + '-tests', [tools[compiler]['path'], *flags, *host_deps,
            '-Funsafe-code', '--test', W / 'source/fd-protocol.rs', '-o', W / (compiler + '-tests')])
    run('c-format', [tools['clang-format']['path'], '--dry-run', '--Werror',
        '--style=file:' + str(R / 'docs/quality/clang-format.yaml'),
        W / 'source/fd-protocol.h', W / 'source/fd-protocol-fixture.c'])
    target = run('c-target', [tools['clang']['path'], '-dumpmachine'])
    record['c_target'] = target.stdout.decode().strip()
    dependency_scan = run('c-header-scan', [tools['clang']['path'], '-std=c17', '-M', W / 'source/fd-protocol-fixture.c'])
    dependencies_text = dependency_scan.stdout.decode().replace('\\\n', ' ')
    header_paths = shlex.split(dependencies_text.split(':', 1)[1])
    record['c_headers_before_compile'] = {name: sha(Path(name)) for name in header_paths}
    (W / 'c-header-pins.json').write_text(json.dumps(record['c_headers_before_compile'], indent=2) + '\n')
    run('c-build', [tools['clang']['path'], *(['-DAEFD_PATH_WIRE'] if path_wire else []), *(['-DAEFD_DUP2_WIRE'] if options.dup2 else []), '-std=c17', '-Wall', '-Wextra', '-Werror',
        '-Wconversion', '-Wsign-conversion', '-fsanitize=undefined', '-fno-sanitize-recover=all',
        W / 'source/fd-protocol-fixture.c', '-o', W / 'c-fixture'])
    emitted = run('c-emit', [W / 'c-fixture', 'emit'], timeout=30)
    (W / 'requests.bin').write_bytes(emitted.stdout)
    record['c_requests_sha256'] = sha(W / 'requests.bin')
    # Actual interop test above must run after the request fixture is present.
    tests = run('tests', [W / 'rustc-tests', '--test-threads=1'], timeout=30)
    if (b'15 passed; 0 failed' if options.dup2 else b'11 passed; 0 failed' if path_wire else b'10 passed; 0 failed') not in tests.stdout:
        raise ValueError('test count/outcome')
    verified = run('c-verify', [W / 'c-fixture', 'verify', W / 'tests-replies.bin'], timeout=30)
    if (b'12 actual Rust replies / 96 malformed headers / 3 padded-body denials pass' if options.dup2 else b'10 actual Rust replies / 80 malformed headers / 3 padded-body denials pass') not in verified.stdout:
        raise ValueError('C interop count/outcome')
    record['rust_replies_sha256'] = sha(W / 'tests-replies.bin')
    borrow_source = """// SPDX-License-Identifier: BSD-2-Clause
use filesystem_fd_protocol::{Connection, Message};
use filesystem_remote_descriptors::{ProcessFiles, MAX_READ};
use filesystem_service::Channel;
pub fn client<T: Channel>(connection: &mut Connection, files: &mut ProcessFiles<T>, frame: &Message, workspace: &mut [u8; MAX_READ]) {
    let first = connection.prepare(files, frame, 0, workspace).unwrap();
    first.delivered();
    let second = connection.prepare(files, frame, 0, workspace).unwrap();
    second.delivered();
}
"""
    consumer_deps = dependencies(W / 'host', ['filesystem_fd_protocol', 'filesystem_service', 'filesystem_remote_descriptors'])
    (W / 'borrow-good.rs').write_text(borrow_source)
    record['borrow_good_sha256'] = sha(W / 'borrow-good.rs')
    run('borrow-good', [tools['rustc']['path'], *flags, *consumer_deps, '--crate-type=lib', '--crate-name=borrow_good', W / 'borrow-good.rs', '-o', W / 'borrow-good.rlib'])
    overlap = borrow_source.replace('    first.delivered();\n', '').replace('    second.delivered();', '    first.delivered();\n    second.delivered();')
    (W / 'borrow-bad.rs').write_text(overlap)
    record['borrow_bad_sha256'] = sha(W / 'borrow-bad.rs')
    rejection = run('borrow-bad', [tools['rustc']['path'], *flags, *consumer_deps, '--crate-type=lib', '--crate-name=borrow_bad', W / 'borrow-bad.rs', '-o', W / 'borrow-bad.rlib'], expected=1)
    if b'E0499' not in rejection.stderr or b'more than once' not in rejection.stderr:
        raise ValueError('wrong borrow rejection')
    original = (W / 'source/fd-protocol.rs').read_text()
    controls = {
        'skip-bound-process-validation': ('files\n            .validate_binding(self.process)\n            .map_err(|_| Error::Retired)?;', 'let _ = files;'),
        'skip-pending-state': ('self.pending = true;', 'self.pending = false;'),
        'skip-epoch': ('word(raw, 2) != self.generation', 'false'),
        'skip-sequence': ('word(raw, 3) != self.next', 'false'),
        'skip-name-padding': ('workspace[word(raw, 5) as usize..needed]', 'workspace[needed..needed]'),
        'skip-reply-drop-retirement': ('self.connection.abort(self.files);', 'let _ = &self.files;'),
        'skip-delivered-sequence': ('self.connection.next += 1;', 'self.connection.next += 0;'),
        'skip-error-output-clearing': ('workspace.fill(0);', '/* omitted initial failure clearing */'),
    }
    if options.dup2:
        controls.update({
            'replace-reversed-target': ('.replace(process, a as i32, b as i32)', '.replace(process, b as i32, a as i32)'),
            'replace-ignore-target-range': ('7 => fd(a) && fd(b) && c == 0 && d == 0,', '7 => fd(a) && c == 0 && d == 0,'),
        })
    record['mutations'] = []
    for label, (old, new) in controls.items():
        if old not in original:
            raise ValueError('mutation target: ' + label)
        (W / 'source/fd-protocol.rs').write_text(original.replace(old, new, 1))
        record['mutations'].append(dict(label=label, old=old, new=new, source_sha256=sha(W / 'source/fd-protocol.rs')))
        run('compile-' + label, [tools['rustc']['path'], *flags, *host_deps,
            '-Funsafe-code', '--test', W / 'source/fd-protocol.rs', '-o', W / label])
        result = run('reject-' + label, [W / label, '--test-threads=1'], expected=101, timeout=30)
        if b'test result: FAILED' not in result.stdout or b'assertion' not in result.stdout:
            raise ValueError('non-semantic rejection: ' + label)
    (W / 'source/fd-protocol.rs').write_text(original)
    for name, digest in record['c_headers_before_compile'].items():
        if sha(Path(name)) != digest:
            raise ValueError('host C input changed during qualification')
    if sha(ubsan) != record['ubsan_runtime']['sha256']:
        raise ValueError('host runtime changed during qualification')
    for name, digest in record['sources'].items():
        if sha(S / name) != digest:
            raise ValueError('source changed')
    record['native_library_sha256'] = sha(W / 'native/libfilesystem_fd_protocol.rlib')
    record['status'] = 'pass'
except BaseException as error:
    record.update(status='failed', error=repr(error))
    raise
finally:
    (W / 'results.json').write_text(json.dumps(record, indent=2) + '\n')
    print(record['status'], W)
