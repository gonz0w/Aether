# SPDX-License-Identifier: BSD-2-Clause
"""Owned host/no_std checks of per-process shared descriptions over pinned AF07."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import types

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--in-place', action='store_true', help='select additive mapped broker initialization')
parser.add_argument('--paths', action='store_true', help='select canonical delegated-root reads for this separate producer')
parser.add_argument('--replace', action='store_true', help='select exact-target FILE alias replacement; no wire/libc change')
parser.add_argument('--file16', action='store_true', help='select 16 aliases/13 descriptions; requires --replace')
parser.add_argument('--cwd', action='store_true', help='retain per-process service directories; requires --paths; no public wire')
options = parser.parse_args()
if options.cwd and not options.paths:
    parser.error('--cwd requires --paths')
if options.file16 and not options.replace:
    parser.error('--file16 requires --replace')
unsafe_policy = [] if options.in_place else ['-Funsafe-code']

R = Path(__file__).resolve().parents[2]
S = Path(__file__).resolve().parent
D = R / 'build/service-deliveries/filesystem-service-metadata-2026-10-21-v1'
W = Path(tempfile.mkdtemp(prefix='filesystem-process-fds-', dir=R / 'build'))
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
              dependency=dependency, tools=tools, native_executed=False, path_wire=options.paths, replace=options.replace, file16=options.file16, cwd=options.cwd,
              tool_manifest=dict(path=str(prior), sha256=sha(prior)),
              rust_native_libraries=pins['rust_native_libraries'],
              sources={}, rows=[])
shutil.copytree(D / 'source', W / 'source')
for name in ('client.rs', 'client-tests.rs', 'paths.rs', 'path-tests.rs', 'replace-tests.rs', 'file16-tests.rs', 'fd-protocol.rs', 'fd-protocol-tests.rs', 'fd-dup2-wire-tests.rs', 'fd-wire-fixture.rs', 'file-descriptions.rs', 'remote-descriptors.rs', 'remote-descriptor-tests.rs', 'process-descriptors.rs', 'process-cwd.rs', 'process-cwd-tests.rs', 'process-descriptor-tests.rs', 'process-fd-fixture.rs', 'vendor/abi29-startup.rs', *(['broker-init-tests.rs'] if options.in_place else [])):
    record['sources'][name] = sha(S / name)
    (W / 'source' / name).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(S / name, W / 'source' / name)
if sha(S / 'vendor/abi29-startup.rs') != 'ba23cba7730e8c10c7f0ea0ccf68a227b71ac70890a72c475ff892d13136e704':
    raise ValueError('ABI29 identity input pin')
record['checker_sha256'] = sha(Path(__file__))


def run(label, argv, expected=0, timeout=60):
    env = proc.clean_env(W)
    env['DYLD_LIBRARY_PATH'] = str(Path(tools['rustc']['path']).parent.parent / 'lib')
    result = proc.run(list(map(str, argv)), cwd=R, env=env, work=W,
                      label=label, timeout=timeout)
    record['rows'].append(dict(label=label, expected=expected, process=result.record, stdout_sha256=hashlib.sha256(result.stdout).hexdigest(), stderr_sha256=hashlib.sha256(result.stderr).hexdigest()))
    if result.returncode != expected or not result.record['complete'] or result.record['cleanup'] != 'complete':
        record['rows'][-1].update(stdout_tail=result.stdout.decode(errors='replace')[-1800:], stderr_tail=result.stderr.decode(errors='replace')[-1800:])
        raise RuntimeError(label)
    return result


flags = ['--edition=2021', '-Dwarnings', '-Dunsafe_op_in_unsafe_fn']
if options.file16:
    flags += ['--cfg', 'fs_file16']
if options.replace:
    flags += ['--cfg', 'fs_replace']
if options.cwd:
    flags += ['--cfg', 'fs_cwd']
if options.paths:
    flags += ['--cfg', 'fs_paths']
if options.in_place:
    flags += ['--cfg', 'fs_in_place']
for selection in ('namespace', 'lifetimes', 'mixed', 'wait', 'bulk', 'runtime',
                  'activation', 'names', 'directories', 'metadata', 'process_views'):
    flags += ['--cfg', 'fs_' + selection]


def dependencies(directory, names):
    args = ['-Ldependency=' + str(directory)]
    for name in names:
        args += ['--extern', name + '=' + str(directory / ('lib' + name + '.rlib'))]
    return args


try:
    run('format', [tools['rustfmt']['path'], '--edition', '2021', '--check',
        '--config-path', R / 'docs/vendor/aether-approved-drafts/2026-09-05/drafts/coding-v0.1.0/configs/rustfmt.toml',
        *[S / name for name in record['sources']]])
    for stage, native in (('host', False), ('native', True)):
        directory = W / stage
        directory.mkdir()
        extra = ['--target=x86_64-unknown-none', '-Cpanic=abort', '-Copt-level=2'] if native else []
        for name, source, imports in (
            ('filesystem_metadata', D / 'source/metadata-lib.rs', []),
            ('filesystem_policy', D / 'source/owner.rs', ['filesystem_metadata']),
            ('filesystem_service', D / 'source/service.rs', ['filesystem_policy']),
            ('filesystem_client', S / 'client.rs' if native else W / 'source/client.rs', ['filesystem_service']),
            ('filesystem_remote_descriptors', S / 'remote-descriptors.rs' if native else W / 'source/remote-descriptors.rs', ['filesystem_client', 'filesystem_service'])):
            run(stage + '-' + name, [tools['rustc']['path'], *flags, *extra,
                *dependencies(directory, imports), '--crate-type=lib',
                '--crate-name=' + name,
                *(unsafe_policy if name in ('filesystem_client', 'filesystem_remote_descriptors') else (['-Funsafe-code'] if name != 'filesystem_metadata' else [])),
                source, '-o', directory / ('lib' + name + '.rlib')])
    if options.file16 and not options.cwd:
        for stage, native in (('host', False), ('native', True)):
            rejected = run(stage + '-reject-legacy-wire', [tools['rustc']['path'], *flags,
                *(['--cfg', 'fs_path_wire'] if options.paths else []),
                *(['--target=x86_64-unknown-none', '-Cpanic=abort'] if native else []),
                *dependencies(W / stage, ['filesystem_client', 'filesystem_service', 'filesystem_remote_descriptors']),
                '-Funsafe-code', '--crate-type=lib', '--crate-name=filesystem_fd_protocol',
                S / 'fd-protocol.rs', '-o', W / stage / 'liblegacy_wire.rlib'], expected=1)
            if b'E0080' not in rejected.stderr or b'FILE_SLOTS_16' not in rejected.stderr:
                raise ValueError('legacy wire rejected for wrong reason')
    if options.cwd:
        for stage, native in (('host', False), ('native', True)):
            rejected = run(stage + '-reject-cwd-on-old-wire', [tools['rustc']['path'], *flags,
                '--cfg', 'fs_path_wire',
                *(['--cfg', 'fs_dup2_wire'] if options.file16 else []),
                *(['--target=x86_64-unknown-none', '-Cpanic=abort'] if native else []),
                *dependencies(W / stage, ['filesystem_client', 'filesystem_service', 'filesystem_remote_descriptors']),
                '-Funsafe-code', '--crate-type=lib', '--crate-name=filesystem_fd_protocol',
                S / 'fd-protocol.rs', '-o', W / stage / 'libcwd_old_wire.rlib'], expected=1)
            if b'CWD requires a separate public FILE contract' not in rejected.stderr:
                raise ValueError('CWD wire rejected for wrong reason')
    if options.cwd:
        baseline_flags = list(flags)
        at = baseline_flags.index('fs_cwd')
        del baseline_flags[at - 1:at + 1]
        layout = W / 'cwd-layout.rs'
        layout.write_text('''#![cfg_attr(target_os = "none", no_std)]
use filesystem_service::{Channel, Message};
pub struct Probe;
impl Channel for Probe {
    fn send(&mut self,_:&Message)->Result<(),i64>{Err(-95)}
    fn receive(&mut self,_:&mut Message)->Result<(),i64>{Err(-95)}
    fn close(&mut self)->[i64;2]{[0;2]}
}
type Before=filesystem_remote_baseline::ProcessFiles<Probe>;
type After=filesystem_remote_descriptors::ProcessFiles<Probe>;
const _:()=assert!(core::mem::size_of::<After>()<=core::mem::size_of::<Before>()+96);
const _:()=assert!(core::mem::align_of::<After>()==core::mem::align_of::<Before>());
#[cfg(not(target_os = "none"))]
fn main(){println!("{} {} {} {}", core::mem::size_of::<Before>(),core::mem::size_of::<After>(),
core::mem::align_of::<Before>(),core::mem::align_of::<After>());}
''')
        for stage, native in (('host', False), ('native', True)):
            extra = ['--target=x86_64-unknown-none', '-Cpanic=abort'] if native else []
            run(stage + '-baseline-layout-library', [tools['rustc']['path'], *baseline_flags, *extra,
                *dependencies(W / stage, ['filesystem_client', 'filesystem_service']),
                *unsafe_policy, '--crate-type=lib', '--crate-name=filesystem_remote_baseline',
                S / 'remote-descriptors.rs', '-o', W / stage / 'libfilesystem_remote_baseline.rlib'])
            run(stage + '-cwd-layout-build', [tools['rustc']['path'], '--edition=2021', '-Dwarnings',
                *extra, *(['--crate-type=lib'] if native else []),
                *dependencies(W / stage, ['filesystem_remote_baseline', 'filesystem_remote_descriptors', 'filesystem_service']),
                layout, '-o', W / stage / ('libcwd_layout.rlib' if native else 'cwd-layout')])
        output = run('cwd-layout', [W / 'host/cwd-layout']).stdout
        values = list(map(int, output.split()))
        if len(values) != 4 or not 0 < values[1] - values[0] <= 96 or values[2] != values[3]:
            raise ValueError('CWD layout growth')
        record['process_files_layout_before_after_alignments'] = values
        record['resident_delta_bytes'] = values[1] - values[0]
    consumer = W / 'copy-consumer.rs'
    consumer.write_text('''#![no_std]
pub fn bind<T: filesystem_service::Channel>(
    files: &mut filesystem_remote_descriptors::ProcessFiles<T>,
    parent: filesystem_remote_descriptors::Process,
    target: filesystem_remote_descriptors::NativeIdentity,
) -> core::result::Result<filesystem_remote_descriptors::Process,
                         filesystem_remote_descriptors::CopyInheritanceError<i32>> {
    let _: (u16, u16) = files.file_view_v1(parent).map_err(
        filesystem_remote_descriptors::CopyInheritanceError::BeforeCopy)?;
    files.copy_inherit_serialized_v1(parent, target, 9, || {
        filesystem_remote_descriptors::CopyAttempt::Refused(-11)
    })
}
''')
    for stage, native in (('host', False), ('native', True)):
        run(stage + '-external-copy-consumer', [tools['rustc']['path'], *flags,
            *(['--target=x86_64-unknown-none', '-Cpanic=abort'] if native else []),
            *dependencies(W / stage, ['filesystem_remote_descriptors', 'filesystem_service']),
            '-Funsafe-code', '--crate-type=lib', '--crate-name=copy_consumer',
            consumer, '-o', W / stage / 'libcopy_consumer.rlib'])
    host_deps = dependencies(W / 'host', ['filesystem_policy', 'filesystem_service', 'filesystem_client'])
    for compiler in ('rustc', 'clippy-driver'):
        run(compiler + '-tests', [tools[compiler]['path'], *flags, *host_deps,
            *unsafe_policy, '--test', W / 'source/remote-descriptors.rs', '-o', W / (compiler + '-tests')])
    tests = run('tests', [W / 'rustc-tests', '--test-threads=1'], timeout=30)
    if str(((11 + 4 * int(options.in_place)) if options.file16 else (37 if options.in_place else 33) + int(options.paths) + 4 * int(options.replace)) + 12 * int(options.cwd)).encode() + b' passed; 0 failed' not in tests.stdout:
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
    source_names = ['file-descriptions.rs', 'process-descriptors.rs']
    originals = {name: (W / 'source' / name).read_text() for name in source_names}
    controls = [
        ('file-descriptions.rs', 'lose-view-copy', 'self.descriptors[child] = self.descriptors[parent];', 'self.descriptors[child] = [None; SLOTS];'),
        ('file-descriptions.rs', 'close-other-view-alias', '.flatten()\n            .flatten()', '.take(1).flatten().flatten()'),
        ('process-descriptors.rs', 'ignore-process-epoch', 'self.records[slot as usize - 1].process != Some(process)', 'self.records[slot as usize - 1].process.map(|p| p.identity) != Some(process.identity)'),
        ('process-descriptors.rs', 'ignore-instance', 'self.records[slot as usize - 1].process != Some(process)', 'self.records[slot as usize - 1].process.is_none()'),
        ('process-descriptors.rs', 'skip-child-generation', 'child.epoch != self.records[view].last_generation + 1', 'false'),
        ('process-descriptors.rs', 'reset-generation-history', 'self.records[view].process = None;', 'self.records[view].process = None; self.records[view].last_generation = 0;'),
        ('process-descriptors.rs', 'ignore-live-children', 'self.records.iter().any(|r| r.process.is_some())', 'self.records[0].process.is_some()'),
        ('file-descriptions.rs', 'change-parent-cloexec', 'self.descriptors[view][index] = Some(binding);', 'self.descriptors[0][index] = Some(binding);'),
    ]
    controls += [
        ('process-descriptors.rs', 'accept-unexpected-copy',
         'identity != target || parent_pid != observed_parent', 'false'),
        ('process-descriptors.rs', 'leave-unknown-admitted',
         'if !self.complete {', 'if false {'),
    ]
    controls += [
        ('file-descriptions.rs', 'omit-high-file-slot',
         'self.descriptors[view].iter().enumerate()',
         'self.descriptors[view].iter().take(12).enumerate()'),
        ('file-descriptions.rs', 'omit-file-view-flags',
         'if binding.close_on_exec {', 'if false && binding.close_on_exec {'),
        ('process-descriptors.rs', 'export-wrong-process-view',
         'self.files.file_view_in(view).map_err(ProcessError::Files)',
         'self.files.file_view_in(view.min(0)).map_err(ProcessError::Files)'),
    ]
    if options.in_place:
        source_names += ['client.rs']
        originals['client.rs'] = (W / 'source/client.rs').read_text()
        controls += [
            ('process-descriptors.rs', 'seed-wrong-in-place-epoch',
             'addr_of_mut!((*pointer).epoch).write(epoch)', 'addr_of_mut!((*pointer).epoch).write(0)'),
            ('process-descriptors.rs', 'seed-occupied-generation',
             '                        last_generation: 0,', '                        last_generation: 1,'),
        ]
    if options.replace:
        controls += [
            ('file-descriptions.rs', 'replace-wrong-slot',
             'self.descriptors[view][target] = Some(Descriptor {\n            close_on_exec: false,',
             'self.descriptors[view][source] = Some(Descriptor {\n            close_on_exec: false,'),
            ('file-descriptions.rs', 'replace-preserve-cloexec',
             'close_on_exec: false,\n            ..binding', 'close_on_exec: true,\n            ..binding'),
            ('file-descriptions.rs', 'replace-skip-victim-close',
             'if let Err(error) = self.source.close(file.handle) {\n                    self.retire();',
             'if let Err(error) = { let _ = file; Ok::<(), S::Error>(()) } {\n                    self.retire();'),
            ('file-descriptions.rs', 'replace-close-inherited-victim',
             '.any(|other| other.description == previous.description)', '.any(|_| false)'),
        ]
    if options.file16:
        controls += [
            ('file-descriptions.rs', 'grow-description-pool', 'const DESCRIPTIONS: usize = 13;', 'const DESCRIPTIONS: usize = 16;'),
            ('file-descriptions.rs', 'omit-low-alias-mask',
             'self.descriptors[view].iter().enumerate()',
             'self.descriptors[view].iter().enumerate().filter(|(i, _)| *i >= 3)'),
        ]
    if options.cwd:
        source_names += ['process-cwd.rs']
        originals['process-cwd.rs'] = (W / 'source/process-cwd.rs').read_text()
        controls += [
            ('process-descriptors.rs', 'seed-borrowed-root-as-owned-cwd',
             'cwd: None,\n        };', 'cwd: Some(self.files.source.client.root().unwrap()),\n        };'),
            ('process-descriptors.rs', 'lose-cwd-inheritance',
             'cwd: self.records[0].cwd,', 'cwd: None,'),
            ('process-descriptors.rs', 'root-substitute-cwd-read',
             'let directory = self.directory_for(view)?;',
             'let directory = self.files.source.client.root().map_err(|error| ProcessError::Files(Failure::Source(error)))?;'),
            ('process-descriptors.rs', 'lose-cwd-on-exec',
             'self.files\n            .commit_exec_close_in(view)',
             '{ self.records[view].cwd = None; }\n        self.files\n            .commit_exec_close_in(view)'),
            ('process-descriptors.rs', 'omit-terminal-cwd-release',
             'self.release_directory(view)?;', '/* omitted terminal release */'),
            ('process-cwd.rs', 'close-inherited-cwd-early',
             'if !shared {', 'if !shared || shared {'),
            ('process-cwd.rs', 'omit-last-cwd-close',
             'if !shared {', 'if false && !shared {'),
            ('process-cwd.rs', 'publish-cwd-before-release',
             'self.release_directory(view)?;\n        self.records[view].cwd = next;',
             'self.records[view].cwd = next;\n        self.release_directory(view)?;'),
        ]
    record['mutations'] = []
    for name, label, old, new in controls:
        original = originals[name]
        if old not in original:
            raise ValueError('mutation target: ' + label)
        (W / 'source' / name).write_text(original.replace(old, new, 1))
        record['mutations'].append(dict(label=label, source=name, old=old, new=new, source_sha256=sha(W / 'source' / name)))
        run('compile-' + label, [tools['rustc']['path'], *flags, *host_deps,
            *unsafe_policy, '--test', W / 'source/remote-descriptors.rs', '-o', W / label])
        result = run('reject-' + label, [W / label, '--test-threads=1'], expected=101, timeout=30)
        record['rows'][-1]['semantic_failure_excerpt'] = result.stdout.decode(errors='replace')[-1400:]
        if b'test result: FAILED' not in result.stdout or b'assertion' not in result.stdout:
            raise ValueError('non-semantic rejection: ' + label)
        (W / 'source' / name).write_text(original)
    # An actual callback cannot mutate the exclusively borrowed ledger in safe Rust.
    test_path = W / ('source/file16-tests.rs' if options.file16 else 'source/process-descriptor-tests.rs')
    original_tests = test_path.read_text()
    test_path.write_text(original_tests + '''
#[test]
fn forbidden_copy_reentry() {
    let mut h = Harness::new(Fault::None, [0; 2]);
    let f = h.fds.as_mut().unwrap();
    let p = shell(f);
    let _ = f.copy_inherit_serialized_v1(p, identity(2, 1), 9, || {
        f.close(p, 3).unwrap();
        confirmed(identity(2, 1))
    });
}
''')
    rejected = run('reject-copy-reentry', [tools['rustc']['path'], *flags, *host_deps,
        *unsafe_policy, '--test', W / 'source/remote-descriptors.rs',
        '-o', W / 'forbidden-copy-reentry'], expected=1)
    if b'E0500' not in rejected.stderr and b'E0501' not in rejected.stderr and b'E0499' not in rejected.stderr:
        raise ValueError('reentry rejected for wrong reason')
    test_path.write_text(original_tests)
    for name, digest in record['sources'].items():
        if sha(S / name) != digest:
            raise ValueError('source changed')
    record['profile'] = 'in-place' if options.in_place else 'by-value'
    record['native_library_sha256'] = sha(W / 'native/libfilesystem_remote_descriptors.rlib')
    record['status'] = 'pass'
except BaseException as error:
    record.update(status='failed', error=repr(error))
    raise
finally:
    (W / 'results.json').write_text(json.dumps(record, indent=2) + '\n')
    print(record['status'], W)
