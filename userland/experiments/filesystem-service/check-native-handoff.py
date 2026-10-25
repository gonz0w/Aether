# SPDX-License-Identifier: BSD-2-Clause
"""Review one pinned retained Aether receipt; never launch a guest or sibling code."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import sys

RECEIPT = '93126506aa78231106b73f93c0f5f954179ed28c82bd291078d35d3a43dd05b4'
SEAL = '5dd5f492dd2ab2c57321a8fd610f1f6fa488dece4c4b40466a37236bf24144c4'
OBJECT = 'dab564abbcc70ca93cebec7fec8d6017c569367dde8419abbf2d2701401150b1'
SIZES = {'normal': 3868, 'lost-reply': 3292,
         'partial-request': 3900, 'close-failure': 3868}
ROLES = ('baseline', 'writer', 'reader')


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def pairs(values):
    result = {}
    for key, value in values:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def load(data):
    require(len(data) <= 2 * 1024 * 1024, 'receipt size')
    require(hashlib.sha256(data).hexdigest() == RECEIPT, 'receipt identity')
    return json.loads(data, object_pairs_hook=pairs)


def review(record):
    """Check retained evidence, not freshness, full-log replay or human sign-off."""
    matrix = record['native_matrix']
    require(record['status'] == matrix['status'] == 'pass', 'matrix result')
    require(matrix['native_attempted'] is True and
            matrix['vm_stop_confirmed'] is True, 'execution/stop')
    require(matrix['final_sources_drift'] == matrix['final_tools_drift'] == [],
            'input drift')
    require(matrix['owned_outputs_disposed'] is True and
            len(set(matrix['disposed_roots'])) == 10, 'owned disposal')
    admission = matrix['pre_execution_admission']
    require(all(admission[key] is True for key in (
        'all_six_distinct_images_prepared_before_any_guest',
        'all_twelve_launch_roles_sealed',
        'baseline_recovery_engines_and_supervisors_match_positive')),
        'prelaunch admission')
    require(admission['controllers'] == SIZES, 'controller bounds')
    service = matrix['service_selection']
    require(service['manifest_sha256'] == SEAL and
            len(service['inputs']) == 345 and
            service['inputs'][service['object']] == OBJECT, 'service identity')
    require(len(record['native_matrix_attempts']) == 2 and
            all(attempt['native_attempted'] is False
                for attempt in record['native_matrix_attempts']),
            'pre-guest attempt history')
    require('unqualified' in record['coverage_correction']['initial_positive'],
            'initial coverage correction')
    require(set(matrix['phases']) == set(SIZES), 'case closure')
    rows = []
    for name in SIZES:
        phase = matrix['phases'][name]
        require(phase['status'] == 'pass' and
                phase['filesystem_service_case'] == name, 'case selection')
        require(phase['assigned_target_txg'] == 788 and
                phase['recovered_pool_txg'] == 798 and
                phase['fresh_vm_readback_qualified'] is True and
                phase['reader_media_unchanged'] is True, 'fresh recovery')
        cases = phase['cases']
        require([case['role'] for case in cases] == list(ROLES), 'role closure')
        require(set(phase['traces']) == set(phase['vm_commands']) == set(ROLES),
                'trace/command closure')
        writer_hash = cases[1]['disk_sha256']
        require(cases[0]['disk_sha256'] != writer_hash and
                cases[2]['disk_sha256'] == writer_hash and
                cases[2]['admitted_media']['sha256'] == writer_hash,
                'writer/recovery media linkage')
        for case in cases:
            role = case['role']
            writer = role == 'writer'
            bound, ticks = (60, 6000) if writer else (30, 3000)
            require(case['status'] == 'pass' and
                    case['vm_run_returned'] is True and
                    case['small_peer_image_denial'] is True,
                    'guest result/denial')
            require(case['watchdog_seconds'] == bound and
                    case['kernel_tick_limit'] == ticks, 'guest bounds')
            require(case['generations'] == case['reclaimed'] == 3 and
                    case['final_live_workers'] == 0 and
                    case['cleanup_trace_version'] == 1 and
                    case['cleanup_boundaries_per_generation'] == 7,
                    'guest cleanup projection')
            require(case['namespace_bytes_verified'] == 780248 and
                    case['namespace_media']['outside_region_canaries_match'] is True and
                    case['namespace_media']['sha256'] == case['disk_sha256'],
                    'file/media verification')
            if writer:
                require(case['assigned_target_txg'] == 788 and all(
                    case[key] is True for key in (
                        'ordered_provider_witness', 'assigned_DMU_transaction',
                        'clean_export_observed')), 'writer ordering/export')
            if role == 'reader':
                require(case['readonly_data_readback'] is True and
                        case['readonly_pool_retired'] is True and
                        case['recovered_pool_txg'] == 798, 'reader result')
            trace = phase['traces'][role]
            require(trace['sha256'] == case['serial_sha256'], 'trace identity')
            tail = trace['tail']
            cleanup = re.findall(
                r'^NATIVE CLEANUP v=1 slot=0 generation=(\d+) phase=(\d+) '
                r'selected=(\d+) pages=8192 reclaimed=(\d+)$', tail, re.M)
            expected = [(str(g), str(p), '0' if p == 1 else '2',
                         str(g if p == 7 else g - 1))
                        for g in range(1, 4) for p in range(1, 8)]
            require(cleanup == expected, 'retained cleanup trace')
            require(re.findall(
                r'^NATIVE terminal slot=0 generation=(\d+) kind=1 detail=0$',
                tail, re.M) == ['1', '2', '3'], 'retained terminal trace')
            require(tail.count('AETHER NATIVE BLOCK PASS\n') == 1 and
                    tail.count('NATIVE supervisor result=100 reclaimed=3\n') == 1,
                    'retained native marker')
            command = phase['vm_commands'][role]
            args = command['argv']
            retained = {key: value for key, value in command.items() if key != 'sha256'}
            encoded = (json.dumps(retained, indent=2) + '\n').encode()
            require(hashlib.sha256(encoded).hexdigest() ==
                    command['sha256'], 'command identity')
            require(args[0] == 'qemu-system-x86_64' and
                    args[args.index('-smp') + 1] == '1' and
                    args[args.index('-m') + 1] == '256M' and
                    args[args.index('-nic') + 1] == 'none' and
                    command['entropy'] is True and
                    command.get('writer_watchdog_seconds', 30) == bound, 'VM profile')
            build = matrix['builds'][name + '/writer' if writer else 'normal/' + role]
            require(build['status'] == 'pass' and
                    build['pool_zpl_writer_budget'] is writer, 'build writer bound')
            if writer:
                origins = build['fs_service_origins']
                require(origins['aether_fs_service_run'] == service['object'] and
                        all(origins[symbol].endswith('/zpl-write.o') for symbol in (
                            'aether_zpl_close', 'aether_zpl_root',
                            'aether_zpl_lookup', 'aether_zpl_read',
                            'aether_zpl_open_write', 'aether_zpl_write')),
                        'original engine/Rust origins')
                require(build['fs_service_case'] == name, 'writer build case')
            rows.append(name + '/' + role)
    return rows


def controls(record):
    changes = [
        (('native_matrix', 'status'), 'fail', 'matrix result'),
        (('native_matrix', 'vm_stop_confirmed'), False, 'execution/stop'),
        (('native_matrix', 'final_sources_drift'), ['changed'], 'input drift'),
        (('native_matrix', 'owned_outputs_disposed'), False, 'owned disposal'),
        (('native_matrix', 'pre_execution_admission', 'all_twelve_launch_roles_sealed'), False, 'prelaunch admission'),
        (('native_matrix', 'pre_execution_admission', 'controllers', 'normal'), 4097, 'controller bounds'),
        (('native_matrix', 'service_selection', 'manifest_sha256'), '0' * 64, 'service identity'),
        (('coverage_correction', 'initial_positive'), 'all covered', 'initial coverage correction'),
        (('native_matrix', 'phases', 'normal', 'recovered_pool_txg'), 787, 'fresh recovery'),
        (('native_matrix', 'phases', 'normal', 'cases', 1, 'watchdog_seconds'), 120, 'guest bounds'),
        (('native_matrix', 'phases', 'normal', 'cases', 1, 'small_peer_image_denial'), False, 'guest result/denial'),
        (('native_matrix', 'phases', 'normal', 'cases', 1, 'final_live_workers'), 1, 'guest cleanup projection'),
        (('native_matrix', 'phases', 'normal', 'cases', 1, 'namespace_bytes_verified'), 16, 'file/media verification'),
        (('native_matrix', 'phases', 'normal', 'cases', 1, 'clean_export_observed'), False, 'writer ordering/export'),
        (('native_matrix', 'phases', 'normal', 'cases', 2, 'admitted_media', 'sha256'), '0' * 64, 'writer/recovery media linkage'),
        (('native_matrix', 'phases', 'normal', 'traces', 'writer', 'tail'), 'AETHER NATIVE BLOCK PASS\n', 'retained cleanup trace'),
        (('native_matrix', 'phases', 'normal', 'vm_commands', 'writer', 'sha256'), '0' * 64, 'command identity'),
        (('native_matrix', 'builds', 'normal/writer', 'fs_service_case'), 'lost-reply', 'writer build case'),
        (('native_matrix', 'builds', 'normal/writer', 'fs_service_origins', 'aether_zpl_write'), '/fake/fixture.o', 'original engine/Rust origins'),
    ]
    for path, value, reason in changes:
        changed = copy.deepcopy(record)
        cursor = changed
        for part in path[:-1]:
            cursor = cursor[part]
        cursor[path[-1]] = value
        try:
            review(changed)
        except ValueError as error:
            require(str(error) == reason, 'wrong negative oracle: ' + reason)
        else:
            raise ValueError('accepted negative control: ' + reason)
    return len(changes)


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(64, '[FAIL] ' + ascii(message) + '\n')


def main():
    parser = Parser(description=__doc__)
    parser.add_argument('receipt', type=Path, help='explicit pinned producer JSON receipt')
    args = parser.parse_args()
    with args.receipt.open('rb') as stream:
        record = load(stream.read(2 * 1024 * 1024 + 1))
    rows = review(record)
    count = controls(record)
    print('[PASS] Retained producer evidence: ' + str(len(rows)) + ' guest roles; ' +
          str(count) + ' semantic rejection controls')
    print('[NOT RUN] Independent native execution, full-report replay and release acceptance')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, IndexError) as error:
        print('[FAIL] ' + ascii(str(error)), file=sys.stderr)
        sys.exit(1)
