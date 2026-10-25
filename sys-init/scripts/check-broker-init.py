#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Qualify mapped broker construction and measure a required native subset, not a VM."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import shutil
import subprocess
import sys
import tempfile
from bounded_tools import run_tool

ROOT = Path(__file__).resolve().parents[1]
SYSTEM = ROOT.parent
USER = SYSTEM / 'userland'
SOURCE = ROOT / 'prototypes/native-filesystem-session'
class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(64, 'broker-init-check: ' + ascii(message)[1:-1] + '\n')


parser = Parser(description=__doc__, epilog='Host component/size qualification only. No VM or complete owner acceptance; see userland/docs/proposals/FS-BROKER-INIT.md in the system repository.')
parser.add_argument('--version', action='version', version='aether-broker-init-check 1')
parser.add_argument('--libraries', required=True, type=Path,
                    help='owned passing check-process-descriptors.py --in-place output')
parser.add_argument('--compact-compare', action='store_true',
                    help='separately measure the pinned musl byte comparison (decision0208)')
parser.add_argument('--unified-route', action='store_true',
                    help='measure the composed mixed-channel route instead of independent FILE/capture roots (decision0210)')
parser.add_argument('--compose-owner', action='store_true',
                    help='link concrete owner for offline measurement; native acceptance remains separate')
parser.add_argument('--guarded-stack', action='store_true',
                    help='select the approved ABI31/8 KiB guarded owner stack for composition')
parser.add_argument('--exec-provider',type=Path,
                    help='passing current check-fork-stage.py --exec output for C/Rust correspondence')
parser.add_argument('--paths',action='store_true',help='require matching canonical root-path producer and C provider')
parser.add_argument('--dup2',action='store_true',help='select matching16-slot protocol/startup profile; requires --paths')
parser.add_argument('--cwd',action='store_true',help='match AF08 physical directory FILE profile; requires --dup2')
args = parser.parse_args()
if args.cwd and not args.dup2:parser.error('--cwd requires --dup2')
if args.dup2 and not args.paths:parser.error('--dup2 requires --paths')
if args.guarded_stack and not args.compose_owner:
    parser.error('--guarded-stack requires --compose-owner')
# Preserve the producer qualification's 16 MiB per-file ceiling in child tools.
soft, hard = resource.getrlimit(resource.RLIMIT_FSIZE)
ceiling = min([16 * 1024 * 1024] + [v for v in (soft, hard) if v != resource.RLIM_INFINITY])
resource.setrlimit(resource.RLIMIT_FSIZE, (ceiling, ceiling))
inputs = args.libraries.resolve()
record = json.loads((inputs / 'results.json').read_text())
if bool(record.get('cwd_wire',False)) != args.cwd:
    raise ValueError('directory profile mismatch')
if record['status'] != 'pass' or record.get('profile') != 'in-place' or bool(record.get('path_wire',False)) != args.paths or bool(record.get('file16',False)) != args.dup2:
    raise ValueError('requires successful in-place producer checks')
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
for name, digest in record['sources'].items():
    if sha(USER / 'experiments/filesystem-service' / name) != digest:
        raise ValueError('producer source changed: ' + name)
if sha(inputs / 'native/libfilesystem_remote_descriptors.rlib') != record['native_library_sha256']:
    raise ValueError('producer native library changed')
for tool in record['tools'].values():
    if sha(tool['path']) != tool['sha256']:
        raise ValueError('producer tool changed')
for path, digest in record['rust_native_libraries'].items():
    if sha(path) != digest:
        raise ValueError('producer target runtime changed: ' + path)
measurement_inputs = {
    'subset.rs.txt': '3d84e98f768dfed27243ced213477f0463e6f0bb56f3b1b8fcbba4c765ab948f',
    'subset.ld.txt': '18dd5022283453eb8c815ea52db731b7f550bc60f79ddfd8ebcea9af2adec0a7',
}
for name, digest in measurement_inputs.items():
    if sha(ROOT / 'docs/evidence/abi30-owner-placement-2026-10-22' / name) != digest:
        raise ValueError('frozen measurement input changed: ' + name)
work_parent = ROOT / 'out'
work_parent.mkdir(exist_ok=True)
work = Path(tempfile.mkdtemp(prefix='broker-init-', dir=work_parent))
rust = Path(record['tools']['rustc']['path'])
env = dict(os.environ, DYLD_LIBRARY_PATH=str(rust.parent.parent / 'lib'))
result = dict(status='incomplete', work=str(work), native_executed=False, path_wire=args.paths, dup2_wire=args.dup2, cwd_wire=args.cwd,
              profile='compact-compare' if args.compact_compare else 'compiler-builtins',
              producer_result_sha256=sha(inputs / 'results.json'), tools=record['tools'],
              sources={}, commands=[], limits=dict(code=16384, stack=4096, data=8192, output_file=ceiling))
result['measurement_inputs'] = measurement_inputs
result['routing'] = 'unified' if args.unified_route else 'independent'
result['rust_native_libraries'] = record['rust_native_libraries']

def save():
    (work / 'results.json').write_text(json.dumps(result, indent=2) + '\n')


def run(label, argv, expected=0):
    argv = list(map(str, argv))
    path = work / (label + '.log')
    row = dict(label=label, argv=argv, expected=expected, timeout_seconds=60,
               output_limit=4 * 1024 * 1024, tool_sha256=sha(argv[0]))
    result['commands'].append(row)
    save()
    try:
        try:
            tool_env = env if str(rust.parent) in argv[0] else {k: v for k, v in env.items() if k != 'DYLD_LIBRARY_PATH'}
            data = run_tool(argv, tool_env, path, timeout=60, limit=4 * 1024 * 1024, cwd=ROOT)
            code = 0
        except subprocess.CalledProcessError as error:
            data = path.read_bytes()
            code = error.returncode
        row.update(exit=code, log_sha256=sha(path))
        if code != expected:
            raise RuntimeError(label + ': ' + data.decode(errors='replace')[-2200:])
        return data
    finally:
        save()


def dependencies(stage, names):
    output = ['-Ldependency=' + str(inputs / stage), '-Ldependency=' + str(work / stage)]
    for name in names:
        directory = inputs if name.startswith('filesystem_') and name not in ('filesystem_fd_protocol', 'filesystem_fd_protocol_previous') else work
        output += ['--extern', name + '=' + str(directory / stage / ('lib' + name + '.rlib'))]
    return output


libraries = [
    ('abi29_dispatch_core', SOURCE / 'lib.rs', []),
    ('fd_startup', SOURCE / 'fd_startup.rs', ['abi29_dispatch_core']),
    ('fork_frames', SOURCE / 'fork_frames.rs', ['abi29_dispatch_core', 'fd_startup']),
    ('exec_frames', SOURCE / 'exec_frames.rs', ['abi29_dispatch_core', 'fd_startup', 'fork_frames']),
    ('fork_gate', SOURCE / 'fork_gate.rs', ['fd_startup', 'filesystem_remote_descriptors', 'filesystem_service', 'filesystem_client']),
    ('fork_streams', SOURCE / 'fork_streams.rs', ['fd_startup', 'fork_gate']),
    ('filesystem_fd_protocol', USER / 'experiments/filesystem-service/fd-protocol.rs', ['filesystem_remote_descriptors', 'filesystem_client', 'filesystem_service']),
    ('fd_dispatch', SOURCE / 'fd_dispatch.rs', ['filesystem_fd_protocol', 'filesystem_remote_descriptors', 'filesystem_service']),
    ('af07_transport', SOURCE / 'af07_transport.rs', ['filesystem_service']),
    ('fork_transport', SOURCE / 'fork_transport.rs', ['abi29_dispatch_core', 'af07_transport', 'fd_startup', 'filesystem_service', 'fork_gate', 'fork_frames']),
    ('owner_region', SOURCE / 'owner_region.rs', []),
    ('owner_entry', SOURCE / 'owner_entry.rs', []),
    ('owner_dispatch', SOURCE / 'owner_dispatch.rs', ['abi29_dispatch_core', 'fd_dispatch', 'fd_startup', 'filesystem_remote_descriptors', 'filesystem_service', 'fork_gate', 'fork_frames', 'exec_frames']),
    ('owner_control', SOURCE / 'owner_control.rs', ['af07_transport']),
    ('owner_runtime', SOURCE / 'owner_runtime.rs', ['abi29_dispatch_core', 'af07_transport', 'fd_dispatch', 'fd_startup', 'filesystem_client', 'filesystem_remote_descriptors', 'filesystem_service', 'fork_gate', 'fork_streams', 'fork_transport', 'owner_control', 'owner_dispatch', 'exec_frames']),
]
# Include module children in the frozen source closure, not just crate roots.
sources = [p for p in SOURCE.glob('*.rs')] + [ROOT / 'tests/native_broker_init.rs', Path(__file__), ROOT / 'scripts/bounded_tools.py']
sources += [USER / 'experiments/filesystem-service' / n for n in ['fd-protocol.rs', 'process-fd-fixture.rs']]
sources += [ROOT / 'tests' / n for n in ['native_fork_gate.rs', 'native_fork_streams.rs', 'native_fork_capture.rs', 'native_owner_region.rs', 'native_fork_publish.rs']]
sources += [ROOT / 'tests/native_owner_dispatch.rs', ROOT / 'tests/native_fd_dispatch.rs', ROOT / 'tests/native_fd_equivalence.rs', ROOT / 'tests/native_fork_refusal.rs']
sources += [ROOT / 'tests/native_owner_runtime.rs']
if args.compose_owner:
    sources += [ROOT / 'scripts/owner_measure.py', SYSTEM / 'scripts/owner_stack.py', SYSTEM / 'kernel/arch/x86_64/native_fs_roles.zig']
if args.compact_compare:
    sources += [ROOT / 'scripts/owner_compare.py', ROOT / 'tests/owner_compare.c',
                USER / 'docs/quality/clang-format.yaml']
result['sources'] = {str(p.relative_to(SYSTEM)): sha(p) for p in sources}
try:
    for stage in ['host', 'native']:
        (work / stage).mkdir()
        for name, source, imports in libraries:
            if stage == 'host' and name == 'owner_entry':
                continue  # x86_64 register bridge is target-only, not host code.
            flags = ['--edition=2024', '-Dwarnings', '-Dunsafe_op_in_unsafe_fn', '--cfg', 'fs_in_place']
            if args.dup2:
                flags += ['--cfg','fs_file16']
            if name == 'filesystem_fd_protocol' and args.dup2:
                flags += ['--cfg','fs_dup2_wire','--cfg','fs_replace']
            if name == 'filesystem_fd_protocol' and args.cwd:
                flags += ['--cfg','fs_cwd_wire']
            if name == 'filesystem_fd_protocol' and args.paths:
                flags += ['--cfg','fs_paths','--cfg','fs_process_views','--cfg','fs_path_wire']
            if stage == 'native':
                flags += ['--target=x86_64-unknown-none', '-Cpanic=abort', '-Copt-level=z']
                if args.compose_owner:
                    flags += ['-Cjump-tables=no']
            run(stage + '-' + name, [rust, *flags, *dependencies(stage, imports), '--crate-type=lib',
                                     '--crate-name=' + name, source, '-o', work / stage / ('lib' + name + '.rlib')])
    all_imports = [n for n, _, _ in libraries] + ['filesystem_policy', 'filesystem_service', 'filesystem_client', 'filesystem_remote_descriptors']
    for name in ['owner_control', 'owner_runtime']:
        _, source, imports = next(row for row in libraries if row[0] == name)
        run('clippy-' + name, [record['tools']['clippy-driver']['path'], '--edition=2024',
            '-Dwarnings', '--cfg', 'fs_in_place', *dependencies('native', imports),
            '--target=x86_64-unknown-none', '-Cpanic=abort', '--crate-type=lib',
            '--crate-name=' + name, source, '--emit=metadata', '-o', work / (name + '.rmeta')])
    runtime_imports=next(imports for name,_,imports in libraries if name=='owner_runtime')
    run('exec-owner-tests-build',[rust,'--edition=2024','-Dwarnings','--cfg','fs_in_place',
        *dependencies('host',runtime_imports),'--test',SOURCE/'owner_runtime.rs','-o',work/'exec-owner-tests'])
    result['exec_owner_tests']=run('exec-owner-tests',[work/'exec-owner-tests','--test-threads=1']).decode()
    if '4 passed; 0 failed' not in result['exec_owner_tests']:
        raise ValueError('missing actual private exec-owner test')
    # Rebuild each compiling omission against the same real private tests; a
    # compile error or unrelated crash is not an accepted security oracle.
    result['exec_controls']=[]
    original=(SOURCE/'owner_runtime.rs').read_text()
    for label,old,new in [
        ('ignore-exec-receipt','raw != 0 || kernel.receipt(id.handle) != (freeze as i64, 0xc003, 1)',
         'raw != 0 || (false && kernel.receipt(id.handle) != (freeze as i64, 0xc003, 1))'),
        ('omit-exec-cloexec','files.commit_exec_close(process).map_err(|_| -5)?;','{}'),
        ('omit-exec-readiness','ready(kernel, id.handle, remaining)?;','{}'),
    ]:
        if original.count(old)!=1:raise ValueError('exec control anchor: '+label)
        directory=work/label
        directory.mkdir()
        changed=directory/'owner_runtime.rs'
        changed.write_text(original.replace(old,new,1))
        shutil.copyfile(SOURCE/'owner_exec_tests.rs',directory/'owner_exec_tests.rs')
        executable=directory/'tests'
        run(label+'-build',[rust,'--edition=2024','-Dwarnings','--cfg','fs_in_place',
            *dependencies('host',runtime_imports),'--test',changed,'-o',executable])
        failure=run(label+'-reject',[executable,'--exact',
            'exec_tests::actual_exec_commit_controls_flags_holders_binding_publication_and_failure','--nocapture'],expected=101)
        if b'1 failed' not in failure or b'assertion' not in failure:
            raise ValueError('nonsemantic exec control: '+label)
        result['exec_controls'].append(dict(label=label,source_sha256=sha(changed)))
    # Host-only differential reference; immutable local object, never a live pin.
    previous = run('previous-protocol-input', [shutil.which('git'), 'show',
        '4e32ff296:userland/experiments/filesystem-service/fd-protocol.rs'])
    previous_digest = hashlib.sha256(previous).hexdigest()
    if previous_digest != '7b8bd810d0cb4943f3e873db65592854fe0001d78afd7418005aa6839bbefc32':
        raise ValueError('previous protocol differential pin')
    result['previous_protocol_sha256'] = previous_digest
    previous_source = work / 'previous-protocol.rs'
    previous_source.write_bytes(previous)
    run('previous-protocol-build', [rust, '--edition=2021', '-Dwarnings',
        *dependencies('host', ['filesystem_remote_descriptors', 'filesystem_client', 'filesystem_service']),
        '--crate-type=lib', '--crate-name=filesystem_fd_protocol_previous', previous_source,
        '-o', work / 'host/libfilesystem_fd_protocol_previous.rlib'])
    host_imports = [n for n in all_imports if n != 'owner_entry'] + ['filesystem_fd_protocol_previous']
    if args.exec_provider:
        delivery=args.exec_provider.resolve()
        provider=json.loads((delivery/'results.json').read_text())
        if (provider.get('status')!='pass' or not provider.get('helper_sha256')
                or provider.get('checker_sha256')!=sha(USER/'experiments/filesystem-service/check-fork-stage.py')
                or not provider.get('helper_parser','').startswith('pass;')
                or bool(provider.get('path_wire',False)) != args.paths
                or bool(provider.get('dup2_wire',False)) != args.dup2
                or bool(provider.get('cwd_wire',False)) != args.cwd):
            raise ValueError('missing complete exec-provider build')
        for name,digest in provider['sources'].items():
            if Path(name).is_absolute() or '..' in Path(name).parts or sha(USER/'experiments/filesystem-service'/name)!=digest:
                raise ValueError('exec-provider source mismatch')
        for name,key in [('exec-request.bin','exec_request_sha256'),('helper.elf','helper_sha256')]:
            if sha(delivery/name)!=provider[key]:raise ValueError('exec-provider artifact changed')
        result['exec_provider']=dict(report_sha256=sha(delivery/'results.json'),request_sha256=provider['exec_request_sha256'],helper_sha256=provider['helper_sha256'])
        cross=work/'exec-correspondence.rs'
        cross.write_text('''#[test] fn actual_c_exec_request_matches_rust_owner(){
let raw=include_bytes!("'''+str(delivery/'exec-request.bin')+'''");
let id=abi29_dispatch_core::startup::Identity::admitted(2,1,0xb0000103).unwrap();
let(plan,sequence)=exec_frames::request(raw,(id,9,18),&mut[0;304]).unwrap();
assert_eq!(sequence,2);assert_eq!(plan.bindings[3].kind,3);assert_eq!(plan.bindings[3].cloexec,1);
assert_eq!(&raw[304..318],b"/inputs/helper");
}
''')
        run('exec-correspondence-build',[rust,'--edition=2024','-Dwarnings',*dependencies('host',host_imports),'--test',cross,'-o',work/'exec-correspondence'])
        run('exec-correspondence',[work/'exec-correspondence'])
    wrapper = work / 'tests.rs'
    wrapper.write_text('use filesystem_remote_descriptors::ProcessFiles; use filesystem_service::Channel;\nmod tests {\n'
        + '#[path="' + str(USER / 'experiments/filesystem-service/process-fd-fixture.rs') + '"] mod fixture;\n'
        + ''.join('mod ' + name + ' { use super::fixture; include!("' + str(ROOT / 'tests' / name) + '.rs"); }\n'
                  for name in ['native_fork_gate', 'native_fork_streams', 'native_fork_capture', 'native_owner_region', 'native_fork_publish', 'native_owner_dispatch', *([] if args.paths else ['native_fd_equivalence']), 'native_fork_refusal'])
        + 'mod native_owner_runtime { include!("' + str(ROOT / 'tests/native_owner_runtime.rs') + '"); }\n'
        + 'mod native_fd_dispatch { use super::fixture; use filesystem_service::Channel; include!("' + str(ROOT / 'tests/native_fd_dispatch.rs') + '"); }\n'
        + 'mod broker { include!("' + str(ROOT / 'tests/native_broker_init.rs') + '"); }\n}\n')
    for tool in ['rustc', 'clippy-driver']:
        run(tool + '-tests-build', [record['tools'][tool]['path'], '--edition=2024', '-Dwarnings', '--cfg', 'fs_in_place',
                                   *dependencies('host', host_imports), '--test', wrapper, '-o', work / (tool + '-tests')])
    data = run('tests', [work / 'rustc-tests', '--test-threads=1'])
    if (b'56 passed; 0 failed' if args.paths else b'57 passed; 0 failed') not in data:
        raise ValueError('required owner/routing/stream/protocol tests did not pass')
    borrow_probes = [
        ('escape-peer-channel', '''use fd_dispatch::Peer; use filesystem_service::Channel;
pub fn escape<C:Channel>(peer:&mut Peer<C>)->&mut C {
 peer.with_channel(|channel| channel).unwrap()
}
''', b'lifetime may not live long enough'),
        ('reenter-route', '''use filesystem_service::Channel; use fork_gate::{Owner,Routed};
pub fn reenter<T:Channel,S>(owner:&mut Owner<T,S>) {
 let _ = owner.route::<()>(|_,_| { let _=owner.admit(|_,_|()); Ok(Routed::Complete) });
}
''', b'cannot borrow'),
    ]
    for label, text, oracle in borrow_probes:
        source = work / (label + '.rs')
        source.write_text(text)
        output = run(label, [rust, '--edition=2024', '-Dwarnings', '--crate-type=lib',
                            *dependencies('host', host_imports), source, '--emit=metadata',
                            '-o', work / (label + '.rmeta')], expected=1)
        if oracle not in output:
            raise ValueError('missing actual borrow denial: ' + label)
    # Existing semantic controls rebuild their own dependency closure. The new
    # Runtime links all those crates and is tested in the unchanged baseline;
    # excluding it here avoids accidentally mixing mutant and original crates.
    control_imports = [n for n in host_imports if n != 'owner_runtime']
    control_wrapper = work / 'control-tests.rs'
    runtime_module = 'mod native_owner_runtime { include!("' + str(ROOT / 'tests/native_owner_runtime.rs') + '"); }\n'
    if wrapper.read_text().count(runtime_module) != 1:
        raise ValueError('control wrapper runtime module anchor')
    control_wrapper.write_text(wrapper.read_text().replace(runtime_module, ''))
    router_source = (SOURCE / 'owner_dispatch.rs').read_text()
    routing_controls = [
        ('prefix-before-gate', '    let result = owner.route(',
         '    receive(peer, &mut [0u8; 1], budget).map_err(GateError::Capture)?;\n    let result = owner.route(',
         'closed_admission_and_unwind_cannot_consume_or_reopen', b'assertion `left == right` failed'),
        ('wait-idle-peer', 'if first == -11 {\n            event = Event::Idle;\n            return Ok(Routed::Complete);',
         'if first == -11 {\n            let _ = peer.with_channel(|channel| channel.0.wait(false));\n            event = Event::Idle;\n            return Ok(Routed::Complete);',
         'idle_parent_does_not_park_owner_or_starve_an_active_copied_child', b'assertion `left == right` failed'),
        ('lose-fork-capture', 'Ok(Routed::Fork {\n                sequence,\n                request: plan,\n            })',
         'let _ = (sequence, plan); Ok(Routed::Complete)',
         'same_channel_file_offset_then_fork_retains_exact_closed_capture', b'fork must retain captured owner admission'),
    ]
    router_imports = next(imports for name, _, imports in libraries if name == 'owner_dispatch')
    for label, old, new, test, oracle in routing_controls:
        if router_source.count(old) != 1:
            raise ValueError('routing control source anchor changed: ' + label)
        directory = work / label
        directory.mkdir()
        changed = directory / 'owner_dispatch.rs'
        changed.write_text(router_source.replace(old, new))
        library = directory / 'libowner_dispatch.rlib'
        run(label + '-library', [rust, '--edition=2024', '-Dwarnings', *dependencies('host', router_imports),
                                 '--crate-type=lib', '--crate-name=owner_dispatch', changed, '-o', library])
        executable = directory / 'tests'
        run(label + '-build', [rust, '--edition=2024', '-Dwarnings', '--cfg', 'fs_in_place',
                               *dependencies('host', [n for n in control_imports if n != 'owner_dispatch']),
                               '--extern', 'owner_dispatch=' + str(library), '--test', control_wrapper, '-o', executable])
        exact = 'tests::native_owner_dispatch::' + test
        failure = run(label + '-test', [executable, '--exact', exact, '--nocapture'], expected=101)
        if oracle not in failure or b'1 failed' not in failure or exact.encode() not in failure:
            raise ValueError('routing control did not fail its semantic assertion: ' + label)
    transport_source = (SOURCE / 'fork_transport.rs').read_text()
    controls = [
        ('unchecked-ready', 'if !fork_frames::ready(', 'if false && !fork_frames::ready(',
         'stale_ready_and_activation_failure_never_publish_parent_success'),
        ('early-parent-open', '        let reply = fork_frames::disposition(request.sequence,',
         '        owner.parent_delivered(request.sequence, pid).unwrap();\n        let reply = fork_frames::disposition(request.sequence,',
         'unwinding_during_each_phase_keeps_gate_closed_and_clears_scratch'),
        ('early-refusal-open', '        let reply = fork_frames::disposition(sequence, error)',
         '        owner.refusal_delivered(sequence, error).unwrap();\n        let reply = fork_frames::disposition(sequence, error)',
         'partial_or_unwound_refusal_delivery_never_reopens_or_thaws_again'),
    ]
    for label, old, new, test in controls:
        if transport_source.count(old) != 1:
            raise ValueError('publication control source anchor changed: ' + label)
        directory = work / label
        directory.mkdir()
        changed = directory / 'fork_transport.rs'
        changed.write_text(transport_source.replace(old, new))
        imports = next(imports for name, _, imports in libraries if name == 'fork_transport')
        library = directory / 'libfork_transport.rlib'
        run(label + '-library', [rust, '--edition=2024', '-Dwarnings', *dependencies('host', imports),
                                 '--crate-type=lib', '--crate-name=fork_transport', changed, '-o', library])
        executable = directory / 'tests'
        run(label + '-build', [rust, '--edition=2024', '-Dwarnings', '--cfg', 'fs_in_place',
                               *dependencies('host', [n for n in control_imports if n != 'fork_transport']),
                               '--extern', 'fork_transport=' + str(library), '--test', control_wrapper, '-o', executable])
        exact = 'tests::native_fork_publish::' + test
        failure = run(label + '-test', [executable, '--exact', exact, '--nocapture'], expected=101)
        oracle = (b'malformed ready or failed activation must not publish success'
                  if label == 'unchecked-ready' else b'assertion `left == right` failed')
        if oracle not in failure or b'1 failed' not in failure or exact.encode() not in failure:
            raise ValueError('publication control did not fail its semantic assertion: ' + label)
    # Require the new supervisor-result rule to detect the old parent-side value.
    directory = work / 'wrong-native-thaw-result'
    directory.mkdir()
    old = 'self.reconcile_refusal(sequence, error, 0, resolve)'
    gate_source = (SOURCE / 'fork_gate.rs').read_text()
    if gate_source.count(old) != 1:
        raise ValueError('native cancellation control anchor changed')
    changed = directory / 'fork_gate.rs'
    changed.write_text(gate_source.replace(old, 'self.reconcile_refusal(sequence, error, -11, resolve)'))
    overrides = {}
    for name in ['fork_gate', 'fork_streams', 'fork_transport', 'owner_dispatch']:
        _, source, imports = next(row for row in libraries if row[0] == name)
        args_ = dependencies('host', [n for n in imports if n not in overrides])
        for n in imports:
            if n in overrides:
                args_ += ['--extern', n + '=' + str(overrides[n])]
        output = directory / ('lib' + name + '.rlib')
        run('wrong-native-thaw-' + name, [rust, '--edition=2024', '-Dwarnings', '--cfg', 'fs_in_place',
            '-Ldependency=' + str(directory), *args_, '--crate-type=lib', '--crate-name=' + name,
            changed if name == 'fork_gate' else source, '-o', output])
        overrides[name] = output
    args_ = dependencies('host', [n for n in control_imports if n not in overrides])
    for name, library in overrides.items():
        args_ += ['--extern', name + '=' + str(library)]
    executable = directory / 'tests'
    run('wrong-native-thaw-tests', [rust, '--edition=2024', '-Dwarnings', '--cfg', 'fs_in_place',
        '-Ldependency=' + str(directory), *args_, '--test', control_wrapper, '-o', executable])
    exact = 'tests::native_fork_refusal::native_refusal_preserves_supervisor_result_and_original_errno_without_replay'
    failure = run('wrong-native-thaw-reject', [executable, '--exact', exact, '--nocapture'], expected=101)
    if b'assertion `left == right` failed' not in failure or b'1 failed' not in failure or exact.encode() not in failure:
        raise ValueError('native cancellation control did not fail its semantic assertion')
    # The new runtime must reject missing same-channel EOF proof before reclaim.
    directory = work / 'missing-export-eof'
    directory.mkdir()
    source = (SOURCE / 'owner_runtime.rs').read_text()
    old = 'if channel.0.transfer(false, &mut byte) != 0'
    if source.count(old) != 1:
        raise ValueError('runtime export proof anchor')
    changed = directory / 'owner_runtime.rs'
    changed.write_text(source.replace(old, 'if channel.0.transfer(false, &mut byte) == i64::MIN'))
    imports = next(imports for name, _, imports in libraries if name == 'owner_runtime')
    library = directory / 'libowner_runtime.rlib'
    run('missing-export-eof-library', [rust, '--edition=2024', '-Dwarnings', '--cfg', 'fs_in_place',
        *dependencies('host', imports), '--crate-type=lib', '--crate-name=owner_runtime', changed, '-o', library])
    executable = directory / 'tests'
    run('missing-export-eof-tests', [rust, '--edition=2024', '-Dwarnings', '--cfg', 'fs_in_place',
        *dependencies('host', control_imports), '--extern', 'owner_runtime=' + str(library),
        '--test', wrapper, '-o', executable])
    exact = 'tests::native_owner_runtime::concrete_owner_orders_startup_settlement_export_proof_and_native_reclaim'
    failure = run('missing-export-eof-rejection', [executable, '--exact', exact, '--nocapture'], expected=101)
    if b'assertion failed: !events.iter().any' not in failure or exact.encode() not in failure:
        raise ValueError('runtime export proof control did not fail its semantic assertion')
    # Reuse the prior required-root measurement, changing only the constructor.
    specimen = (ROOT / 'docs/evidence/abi30-owner-placement-2026-10-22/subset.rs.txt').read_text()
    first = specimen.index('#[inline(never)]')
    last = specimen.index('#[unsafe(no_mangle)]#[unsafe(link_section=".text.measure.settle")]', first)
    specimen = specimen[:first] + '''#[unsafe(no_mangle)]#[unsafe(link_section=".text.measure.boot")]
pub fn minimum_boot(slot:&mut core::mem::MaybeUninit<Gate>,channel:Channel,epoch:u64,streams:State)->bool {
 Owner::connect_in_place(slot,channel,epoch,streams).is_ok()
}
''' + specimen[last:]
    specimen = specimen.replace('{ProcessFiles,Process,NativeIdentity,CopyAttempt}', '{Process,NativeIdentity,CopyAttempt}')
    specimen += '''
#[unsafe(no_mangle)]#[unsafe(link_section=".text.measure.publish")]
pub fn minimum_publish(owner:&mut Gate,kernel:&mut Native,publication:fork_transport::Publication<'_>,remaining:&mut u32,scratch:&mut[u8;304])->bool {
 fork_transport::publish(owner,kernel,publication,remaining,scratch).is_ok()
}
#[unsafe(no_mangle)]#[unsafe(link_section=".text.measure.refuse")]
pub fn minimum_refuse(owner:&mut Gate,kernel:&mut Native,sequence:u64,error:i64,parent:u64,remaining:&mut u32,scratch:&mut[u8;304])->bool {
 fork_transport::refuse(owner,kernel,sequence,error,parent,remaining,scratch).is_ok()
}
'''
    if args.unified_route:
        first = specimen.index('#[unsafe(no_mangle)]#[unsafe(link_section=".text.measure.rpc")]')
        last = specimen.index('#[unsafe(no_mangle)]#[unsafe(link_section=".text.measure.copy")]', first)
        specimen = specimen[:first] + '''
#[unsafe(no_mangle)]#[unsafe(link_section=".text.measure.route")]
pub fn minimum_route(owner:&mut Gate,peer:&mut Peer<Channel>,expected:(Identity,u32,u64),remaining:&mut u32,workspace:&mut[u8;4096],stream:fn(&mut filesystem_remote_descriptors::ProcessFiles<Channel>,&mut State,&mut Peer<Channel>,&[u8;32],&mut u32)->Result<(),i64>)->bool {
 owner_dispatch::dispatch(owner,peer,expected,remaining,workspace,stream).is_ok()
}
#[unsafe(no_mangle)]#[unsafe(link_section=".text.measure.native_cancel")]
pub fn minimum_native_cancel(owner:&mut Gate,kernel:&mut Native,sequence:u64,error:i64,source:u64,freeze:u64)->bool {
 owner.resolve_native_refusal(sequence,error,|_|Ok(kernel.cancel_freeze(source,freeze))).is_ok_and(|raw|raw==Ok(0))
}
''' + specimen[last:]
    (work / 'subset.rs').write_text(specimen)
    linker = work / 'subset.ld'
    linker_bytes = (ROOT / 'docs/evidence/abi30-owner-placement-2026-10-22/subset.ld.txt').read_bytes()
    entry_symbol = 'minimum_route' if args.unified_route else 'minimum_rpc'
    if args.unified_route:
        if linker_bytes.count(b'ENTRY(minimum_rpc)') != 1:
            raise ValueError('measurement linker entry anchor changed')
        linker_bytes = linker_bytes.replace(b'ENTRY(minimum_rpc)', b'ENTRY(minimum_route)')
    linker.write_bytes(linker_bytes)
    rust_lld = rust.parent.parent / 'lib/rustlib/aarch64-apple-darwin/bin/rust-lld'
    extra_link = []
    if args.compact_compare:
        from owner_compare import prepare
        compare_object, result['comparison'] = prepare(SYSTEM, work, run, record['tools'])
        extra_link = ['-Clink-arg=' + str(compare_object)]
    run('subset-link', [rust, '--edition=2024', '-Dwarnings', '--cfg', 'fs_in_place', '--target=x86_64-unknown-none',
                        '-Cpanic=abort', '-Copt-level=z', '-Clto=fat', '-Ccodegen-units=1', '-Crelocation-model=static',
                        '-Clink-arg=--no-dynamic-linker', '-Clink-arg=-static', '-Clinker=' + str(rust_lld),
                        '-Clink-arg=-T' + str(linker), '-Clink-arg=--gc-sections', *extra_link, *dependencies('native', all_imports),
                        work / 'subset.rs', '-o', work / 'subset.elf'])
    # Inspect the actual target data layout separately from code/entry roots.
    layout = work / 'layout.rs'
    layout.write_text("""#![no_std]
use af07_transport::{Endpoints,native::Native};
use filesystem_service::channel::Framed;
type Channel=Framed<Endpoints<Native>>;
type Gate=fork_gate::Owner<Channel,fork_streams::State>;
#[used]#[unsafe(no_mangle)]#[unsafe(link_section=".rodata.owner_layout")]
pub static OWNER_LAYOUT:[u64;6]=[core::mem::size_of::<Gate>() as u64,4096,8192,
 core::mem::size_of::<fd_dispatch::Peer<Channel>>() as u64,
 core::mem::align_of::<Gate>() as u64,core::mem::size_of::<fork_streams::State>() as u64];
""")
    run('layout-build', [rust, '--edition=2024', '-Dwarnings', '--cfg', 'fs_in_place',
        '--target=x86_64-unknown-none', '-Cpanic=abort', '--crate-type=lib', '--emit=obj',
        *dependencies('native', all_imports), layout, '-o', work / 'layout.o'])
    dumped = run('layout-readelf', [record['tools']['readelf']['path'], '-x',
        '.rodata.owner_layout', work / 'layout.o']).decode()
    layout_bytes = bytes.fromhex(''.join(''.join(re.findall(r'\b[0-9a-fA-F]{8}\b',
        line.split(maxsplit=1)[1])[:4]) for line in dumped.splitlines() if line.lstrip().startswith('0x')))
    if len(layout_bytes) != 48:
        raise ValueError('target owner layout observation missing')
    values = [int.from_bytes(layout_bytes[i:i+8], 'little') for i in range(0,48,8)]
    result['resident'] = dict(zip(['gate','workspace','mapping','peer','alignment','streams'], values))
    result['resident']['gate_workspace'] = values[0] + values[1]
    result['resident']['remaining'] = values[2] - values[0] - values[1]
    result['resident']['scope'] = 'target type layout only; other owner state/peak fit still required'
    if values[1:3] != [4096,8192] or values[0] + values[1] > values[2]:
        raise ValueError('owner plus workspace exceeds fixed mapping')
    llvm = Path(record['tools']['readelf']['path']).parent
    sizes = run('subset-size', [llvm / 'llvm-size', '-A', work / 'subset.elf']).decode()
    sections = {m[0]: int(m[1]) for m in re.findall(r'^(\.\S+)\s+(\d+)\s+\d+', sizes, re.M)}
    assembly = run('subset-disassembly', [llvm / 'llvm-objdump', '-d', '--demangle', work / 'subset.elf']).decode()
    symbols = run('subset-symbols', [record['tools']['nm']['path'], '--defined-only', work / 'subset.elf']).decode()
    entry = int.from_bytes((work / 'subset.elf').read_bytes()[24:32], 'little')
    matches = re.findall(r'^([0-9a-fA-F]+)\s+T\s+' + entry_symbol + r'$', symbols, re.M)
    if len(matches) != 1 or entry == 0 or entry != int(matches[0], 16):
        raise ValueError('missing or wrong measurement root entry')
    result['measurement'] = dict(sections=sections, code_fits=sections.get('.text', 16385) <= 16384,
                                 entry_symbol=entry_symbol, entry_address=entry,
                                 fixed_reservations=sorted(set(int(x, 0) for x in re.findall(r'subq\s+\$(0x[0-9a-f]+|\d+), %rsp', assembly))),
                                 scope=('composed mixed-route plus required construction/copy/publication/settlement/native cancellation roots; no complete owner/entry/peak stack/native acceptance' if args.unified_route else 'required independent roots including actual publication path; no full owner, peak stack or native acceptance'))
    if args.compose_owner:
        from owner_measure import measure
        result['owner_measurement'] = measure(SYSTEM, work, rust, record['tools'],
            run, dependencies('native', all_imports), extra_link, args.guarded_stack)
        result['owner_limits'] = dict(code=result['owner_measurement']['code_budget'],
            stack=8192 if args.guarded_stack else 4096, data=8192,
            scope='Selected whole owner only; limits/measurement above describe historical subset roots')
    for path, digest in result['sources'].items():
        if sha(SYSTEM / path) != digest:
            raise ValueError('source changed during qualification: ' + path)
    result['artifacts'] = {p.name: dict(bytes=p.stat().st_size, sha256=sha(p)) for p in [work / 'subset.elf', work / 'rustc-tests']}
    result['host_checks'] = 'pass'
    if args.compose_owner:
        owner = result['owner_measurement']
        result['status'] = ('blocked-owner-resident' if not owner['resident_fits'] else
            'blocked-owner-stack' if owner['stack']['status'] != 'pass' else
            'blocked-owner-incomplete' if not args.guarded_stack or not args.exec_provider else
            'blocked-owner-code' if not owner['code_fits'] else 'pass')
        result['owner_admission'] = 'offline checks only; fresh native qualification and independent acceptance pending'
    else:
        result['status'] = 'pass' if result['measurement']['code_fits'] else 'blocked-code-fit'
except BaseException as error:
    result.update(status='failed', error=repr(error))
    raise
finally:
    save()
    print(json.dumps(dict(schema='aether-broker-init-check-v1', status=result['status'], report=str(work / 'results.json'))))
    if result['status'] == 'blocked-code-fit':
        print('[BLOCKED] Required native subset exceeds the 16384-byte code ceiling; no VM was started.', file=sys.stderr)
    elif result['status'].startswith('blocked-owner-'):
        print('[BLOCKED] Selected owner does not meet its offline build/provider/fit requirements; no VM was started.', file=sys.stderr)

if result["status"].startswith("blocked-"):
    sys.exit(2)
if result["status"] != "pass":
    sys.exit(1)
