# SPDX-License-Identifier: BSD-2-Clause
"""Fixed namespace or file-size recovery batch; no retry/resume."""
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from deps import ROOT
from native_smoke import NativeStopError
from openzfs_mutation import OPERATIONS, SIZE_OPERATIONS, EIGHT_OPERATIONS, LIFETIME_OPERATIONS
import service_runtime_smoke as runtime
import zpl_pair as pair


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def compact_build(build):
    keys = ('status', 'delivery_seal', 'utc_delivery_seal', 'namespace_mutation',
            'pool_zpl_write', 'pool_zpl_recover', 'pool_zpl_writer_budget', 'pool_zpl_repeat',
            'pool_recovery_diagnostic', 'pool_recovery_writer_60s', 'cases',
            'fs_service', 'fs_service_case', 'fs_namespace_operation')
    result = {key: build[key] for key in keys if key in build}
    for key in ('sources', 'tools', 'dependency_files', 'utc_inputs', 'commands'):
        result[key + '_sha256'] = digest(build.get(key))
    commands = build.get('commands', [])
    result['command_count'] = len(commands)
    result['selected_commands'] = [command for command in commands if
        any('zpl-mutation-selected.c' in str(arg) or '-Dnative-service-zpl-budget=' in str(arg)
            or 'fs_namespace_' in str(arg) or 'bridge-partial.map' in str(arg)
            for arg in command.get('argv', []))]
    result['rust_inputs'] = build.get('port', {}).get('volume', {}).get('rust_inputs', {})
    result['namespace_objects'] = build.get('port', {}).get('volume', {}).get('namespace_objects', {})
    result['fs_service_origins'] = build.get('port', {}).get('fs_service_origins', {})
    return result


def owned_pair():
    return Path(tempfile.mkdtemp(prefix=pair.PREFIX, dir=ROOT / 'zig-out'))


def batch(delivery, utc_delivery, file_sizes=False, eight_writes=False, write_lifetimes=False, filesystem_service=None, filesystem_service_case='normal'):
    if not isinstance(file_sizes, bool) or not isinstance(eight_writes, bool) or not isinstance(write_lifetimes, bool) or sum((file_sizes,eight_writes,write_lifetimes)) > 1:
        raise ValueError('file-size batch selectors must be exclusive booleans')
    if filesystem_service_case not in ('normal', 'lost-reply', 'close-failure') or (filesystem_service is None and filesystem_service_case != 'normal'):
        raise ValueError('namespace service interruption requires its exact selection')
    if filesystem_service is not None:
        if file_sizes or eight_writes or write_lifetimes:
            raise ValueError('namespace service cannot select file-size or write profiles')
        from openzfs_fs_namespace import intake
        intake(filesystem_service)
    operations = LIFETIME_OPERATIONS if write_lifetimes else EIGHT_OPERATIONS if eight_writes else SIZE_OPERATIONS if file_sizes else OPERATIONS
    label = 'Write-lifetime' if write_lifetimes else 'Eight-write' if eight_writes else 'File-size' if file_sizes else 'Namespace'
    (ROOT / 'zig-out').mkdir(exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix='thread-suite-service-runtime-namespace-batch-', dir=ROOT / 'zig-out'))
    record = {'format': 'aether-namespace-batch-v1', 'status': 'preparing',
              'start_utc': datetime.now(timezone.utc).isoformat(), 'builds': {},
              **({'file_sizes': True} if file_sizes else {}),
              **({'eight_writes': True} if eight_writes else {}),
              **({'write_lifetimes': True} if write_lifetimes else {}),
              'phases': {}, 'native_attempted': False, 'vm_stop_confirmed': True,
              **({'filesystem_service': str(filesystem_service), 'filesystem_service_case': filesystem_service_case} if filesystem_service is not None else {}),
              'scope': 'three fresh one-transaction writers, independently recovered between operations; original file preserved; no public service/crash/power-loss claim'}
    if file_sizes:
        record['scope'] = 'nonzero shrink, initialized4096-byte extension, two4096-byte writes on the existing two-record witness; fresh recovery after each; no general sustained-service claim'
    if eight_writes:
        record['scope'] = 'fixed eight4096-byte appends after shrink/initialized extension; eight append-only records/10240-byte observer, fresh recovery; no general service uptime'
    if write_lifetimes:
        record['scope'] = 'eight4096-byte appends with one epoch-scoped reusable successful-TXG record, explicit consuming context retirement and fresh recovery; no general service uptime'
    roots = {operation: owned_pair() for operation in operations}
    builds = {operation: {} for operation in operations}
    build_roots = set()
    try:
        for operation in operations:
            for role in (('baseline', 'writer', 'reader') if operation == operations[0] else ('writer', 'reader')):
                print('[RUNNING] ' + label + ' preparation: ' + operation + '/' + role, file=sys.stderr, flush=True)
                try:
                    runtime.suite(delivery, case='pool-import', fixed_reaper=True, engine_utc=True,
                        utc_delivery=utc_delivery, pool_create=True, pool_namespace=True,
                        pool_diagnose='build', pool_zpl_write=role == 'writer',
                        pool_zpl_recover=role == 'reader', _zpl_stage=roots[operation] / role,
                        _zpl_writer_budget=role == 'writer',
                        _zpl_recovery_diagnostic=role == 'reader',
                        _zpl_recovery_writer_60s=role == 'reader',
                        _zpl_namespace_mutation=operation if role != 'baseline' else None,
                        _zpl_repeat=operation in ('repeat', 'eight', 'lifetimes') and role == 'writer',
                        namespace_ipc=filesystem_service is not None and role == 'writer',
                        _zpl_fs_service=filesystem_service if role == 'writer' else None,
                        _zpl_fs_service_case=filesystem_service_case if role == 'writer' else 'normal',
                        _zpl_fs_namespace=operation if filesystem_service is not None and role != 'baseline' else None)
                finally:
                    location = roots[operation] / (role + '-build.json')
                    if location.is_file():
                        built = json.loads(location.read_text())
                        build_roots.add(Path(built['output']))
                        builds[operation][role] = built['report']
                        record['builds'][operation + '/' + role] = compact_build(built['report'])
                if role == 'baseline':
                    common = builds[operation][role]
                    record['inputs'] = {key: common.get(key) for key in ('sources', 'tools', 'dependency_files', 'utc_inputs')}
            if operation != operations[0]:
                baseline = builds[operations[0]]['baseline']
                builds[operation]['baseline'] = copy.deepcopy(baseline)
                (roots[operation] / 'baseline').mkdir()
                for name in ('aether.iso', 'engine.elf'):
                    shutil.copyfile(roots[operations[0]] / 'baseline' / name, roots[operation] / 'baseline' / name)
        # Every profile and code/stack/origin outcome is admitted before any VM.
        for operation in operations:
            pair.verify_prepared(roots[operation], builds[operation], writer_ticks_6000=True,
                                 recovery_diagnostic=True, writer_60s=True, namespace_mutation=operation,
                                 repeated_writes=operation in ('repeat', 'eight', 'lifetimes'),
                                 filesystem_service=filesystem_service, filesystem_service_case=filesystem_service_case,
                                 filesystem_service_namespace=filesystem_service is not None)
        record['all_seven_images_prepared_before_any_vm'] = True
        previous = None
        for operation in operations:
            phase = {'format': 'aether-zpl-pair-v1', 'status': 'running', 'cases': [],
                     'native_attempted': False, 'namespace_mutation': operation,
                     **({'filesystem_service': str(filesystem_service), 'filesystem_service_case': filesystem_service_case,
                         'filesystem_service_namespace': True} if filesystem_service is not None else {}),
                     'repeated_writes': operation in ('repeat', 'eight', 'lifetimes'),
                     'writer_ticks_6000': True, 'writer_60s_diagnostic': True,
                     'recovery_diagnostic': True, 'writer_kernel_tick_limit': 6000,
                     'readonly_kernel_tick_limit': 3000, 'writer_watchdog_seconds': 60,
                     'readonly_watchdog_seconds': 30, 'normal_30_second_writer_qualified': False,
                     'sources_manifest_sha256': digest(builds[operation]['writer']['sources'])}
            if previous is not None:
                phase['namespace_seed'] = str(roots[previous])
            record['phases'][operation] = phase
            print('[RUNNING] ' + label + ' execution: ' + operation, file=sys.stderr, flush=True)
            try:
                pair.execute_pair(roots[operation], builds[operation], phase)
                phase.update(status='pass', vm_stop_confirmed=True)
                (roots[operation] / 'results.json').write_text(json.dumps(phase, indent=2) + '\n')
            except BaseException as error:
                phase.update(status='failed', error=str(error), vm_stop_confirmed=not isinstance(error, NativeStopError))
                if phase['cases']:
                    case = phase['cases'][-1]
                    case.update(status='failed', error=str(error))
                    pair.diagnose(roots[operation], case['role'], builds[operation][case['role']], phase)
                raise
            previous = operation
        record.update(status='pass', all_three_operations_recovered=True)
    except BaseException as error:
        record.update(status='failed', error=str(error), vm_stop_confirmed=not isinstance(error, NativeStopError))
        raise
    finally:
        record['native_attempted'] = any(phase.get('native_attempted') for phase in record['phases'].values())
        record['human_disposition_required'] = record['status'] == 'failed' and record['native_attempted']
        for operation, root in roots.items():
            phase = record['phases'].get(operation)
            if phase:
                from openzfs_namespace import written_native_media_snapshot
                disk = root / 'native-namespace.raw'
                if disk.is_file() and record['vm_stop_confirmed']:
                    try:
                        phase['final_media'] = written_native_media_snapshot(disk)
                    except (ValueError, OSError) as error:
                        phase['final_media_error'] = str(error)
                for role in ('baseline', 'writer', 'reader'):
                    command = root / role / 'native-qemu-command.json'
                    if command.is_file():
                        phase.setdefault('vm_commands', {})[role] = {
                            'sha256': runtime.sha(command), **json.loads(command.read_text())}
                    log = root / role / 'native-serial.log'
                    if log.is_file():
                        # Complete machine observations plus short operational tail.
                        text = log.read_text()
                        phase.setdefault('traces', {})[role] = {
                            'sha256': runtime.sha(log), 'bytes': log.stat().st_size,
                            'observations': [line for line in text.splitlines() if line.startswith('NATIVE observation')],
                            'tail': text[-6000:]}
        record['build_failure_logs'] = {}
        for root in build_roots:
            if root.parent != ROOT / 'zig-out' or root.is_symlink() or not root.name.startswith('thread-suite-service-runtime-') or root.name.startswith(pair.PREFIX):
                raise ValueError('namespace refuses unowned build cleanup')
            for log in root.glob('*.log'):
                if log.stat().st_size:
                    record['build_failure_logs'][root.name + '/' + log.name] = log.read_text(errors='replace')[-2000:]
            if record['vm_stop_confirmed']:
                shutil.rmtree(root)
        if record['vm_stop_confirmed']:
            for root in roots.values():
                shutil.rmtree(root)
            record['owned_outputs_disposed'] = all(not root.exists() for root in [*roots.values(), *build_roots])
        else:
            record['cleanup_blocked'] = 'VM stop unconfirmed; retain owned roots'
            record['retained_roots'] = [str(root) for root in roots.values()]
        record['end_utc'] = datetime.now(timezone.utc).isoformat()
        (output / 'results.json').write_text(json.dumps(record, indent=2) + '\n')
    print('[PASS] ' + ('Write-lifetime shrink/extend/eight-appends' if write_lifetimes else 'Eight-write shrink/extend/eight-appends' if eight_writes else 'File-size shrink/extend/two-write' if file_sizes else 'Namespace create/rename/remove') + ' recovered; compact results: ' + str(output))
    return output


if __name__ == '__main__':
    parser = runtime.IntakeParser(description=__doc__, color=False)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument('--write-lifetimes', action='store_true', help='fixed eight-write successful-record lifetime batch')
    selection.add_argument('--eight-writes', action='store_true', help='fixed eight-transaction/10KiB observer batch')
    selection.add_argument('--file-sizes', action='store_true', help='fixed nonzero shrink/initialized extension/two-write batch')
    parser.add_argument('--filesystem-service', type=Path, help='exact one-attempt AFSRPC02 namespace candidate')
    parser.add_argument('--filesystem-service-case', choices=('normal','lost-reply','close-failure'), default='normal')
    parser.add_argument('--delivery', type=Path, required=True)
    parser.add_argument('--utc-delivery', type=Path, required=True)
    args = parser.parse_args()
    if (args.filesystem_service is not None and (args.file_sizes or args.eight_writes or args.write_lifetimes)) or (args.filesystem_service is None and args.filesystem_service_case != 'normal'):
        parser.error('namespace service requires an exclusive matching selection')
    try:
        batch(args.delivery, args.utc_delivery, args.file_sizes, args.eight_writes, args.write_lifetimes, args.filesystem_service, args.filesystem_service_case)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        parser.exit(1, runtime.display(error) + '\n')
