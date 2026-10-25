# SPDX-License-Identifier: BSD-2-Clause
"""Fixed three-operation engine selection; no public filesystem protocol."""
import hashlib
from pathlib import Path

from deps import ROOT

OPERATIONS = ('create', 'rename', 'remove')
SIZE_OPERATIONS = ('shrink', 'extend', 'repeat')
EIGHT_OPERATIONS = ('shrink', 'extend', 'eight')
LIFETIME_OPERATIONS = ('shrink', 'extend', 'lifetimes')
FILE_BYTES = {'shrink': 65539, 'extend': 69635, 'repeat': 73722, 'eight': 102403, 'lifetimes': 102403}


def validate(operation):
    if operation is not None and (not isinstance(operation, str) or operation not in OPERATIONS + SIZE_OPERATIONS + EIGHT_OPERATIONS + LIFETIME_OPERATIONS):
        raise ValueError('namespace mutation requires a fixed namespace or file-size operation')


def source(operation, reader):
    validate(operation)
    if operation is None or not isinstance(reader, bool):
        raise ValueError('namespace mutation source requires exact role')
    if operation == 'lifetimes':
        return ('#define SZ_KIND 3\n#define SZ_EIGHT 1\n#define SZ_LIFETIMES 1\n'
                '#define SZ_READER ' + str(int(reader)) + '\n'
                '#include "zpl-size-probe.c"\n')
    if operation == 'eight':
        return ('#define SZ_KIND 3\n#define SZ_EIGHT 1\n'
                '#define SZ_READER ' + str(int(reader)) + '\n'
                '#include "zpl-size-probe.c"\n')
    if operation in SIZE_OPERATIONS:
        return ('#define SZ_KIND ' + str(SIZE_OPERATIONS.index(operation) + 1) + '\n'
                '#define SZ_READER ' + str(int(reader)) + '\n'
                '#include "zpl-size-probe.c"\n')
    return ('#define MNS_KIND ' + str(OPERATIONS.index(operation) + 1) + '\n'
            '#define MNS_READER ' + str(int(reader)) + '\n'
            '#include "zpl-mutation-probe.c"\n')


def source_sha(operation, reader):
    return hashlib.sha256(source(operation, reader).encode()).hexdigest()


def admit_seed(output, operation, previous, sources):
    """Copy only a clean predecessor's independently recovered, stopped media."""
    import json
    import shutil
    import service_runtime_smoke as runtime
    from openzfs_namespace import written_native_media_snapshot
    expected = {'rename': 'create', 'remove': 'rename', 'extend': 'shrink', 'repeat': 'extend', 'eight': 'extend', 'lifetimes': 'extend'}.get(operation)
    output = Path(output)
    previous = Path(previous)
    if (output.parent != ROOT / 'zig-out' or output.is_symlink() or
            output.resolve() != output or not output.is_dir() or
            not output.name.startswith('thread-suite-service-runtime-zpl-pair-') or
            expected is None or previous.parent != ROOT / 'zig-out' or previous == output or
            not previous.name.startswith('thread-suite-service-runtime-zpl-pair-') or
            previous.is_symlink() or previous.resolve() != previous):
        raise ValueError('namespace seed requires owned exact predecessor')
    receipt = previous / 'results.json'
    if receipt.is_symlink() or not receipt.is_file():
        raise ValueError('namespace seed missing receipt')
    record = json.loads(receipt.read_text())
    if (record.get('status') != 'pass' or record.get('namespace_mutation') != expected or
            any(record.get(key) is not True for key in ('fresh_vm_readback_qualified',
                'reader_media_unchanged', 'vm_stop_confirmed')) or
            record.get('sources_manifest_sha256') != hashlib.sha256(
                json.dumps(sources, sort_keys=True).encode()).hexdigest()):
        raise ValueError('namespace seed missing exact clean qualification')
    cases = record.get('cases', [])
    if len(cases) < 2 or [case.get('role') for case in cases[-2:]] != ['writer', 'reader']:
        raise ValueError('namespace seed missing writer/reader pair')
    writer, reader = cases[-2:]
    runtime.check_zpl_recovery_pair(writer, reader, FILE_BYTES.get(expected, 780248))
    for role, case in (('writer', writer), ('reader', reader)):
        log = previous / role / 'native-serial.log'
        if log.parent.is_symlink() or log.is_symlink() or runtime.sha(log) != case.get('serial_sha256'):
            raise ValueError('namespace seed trace identity')
        text = log.read_text()
        runtime.check_engine_trace(text, 'AETHER NATIVE BLOCK PASS')
        runtime.check_pool_cleanup_trace(text)
        actual = runtime.check_zpl_write_trace(text) if role == 'writer' else runtime.check_zpl_recovery_trace(text)
        key = 'assigned_target_txg' if role == 'writer' else 'recovered_pool_txg'
        if actual[key] != case[key]:
            raise ValueError('namespace seed trace target mismatch')
    disk = previous / 'native-namespace.raw'
    before = runtime.check_zpl_recovery_media(writer, disk)
    target = output / 'native-namespace.raw'
    # Exclusive destination, both owned roots, joined VMs, immutable source hash.
    with disk.open('rb') as source, target.open('xb') as destination:
        shutil.copyfileobj(source, destination, 1024 * 1024)
    admitted = written_native_media_snapshot(target, writer['disk_sha256'])
    if runtime.check_zpl_recovery_media(writer, disk) != before or admitted != before:
        raise ValueError('namespace seed copy drift')
    return {'previous_operation': expected, 'previous_output': str(previous),
            'previous_receipt_sha256': runtime.sha(receipt),
            'qualified_writer': writer, 'media': admitted}
