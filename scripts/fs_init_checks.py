# SPDX-License-Identifier: BSD-2-Clause
"""Independent exported-pool reader and fixed failed-peer preparation/oracles."""
import json
from pathlib import Path
import re
import shutil
import struct

from deps import ROOT
from fs_launch import labels
from fs_launch_intake import digest
import service_runtime_smoke as runtime

FAILURES = ('startup-exit', 'malformed-greeting', 'reply-generation', 'failed-exit', 'reply-close')
TAGS = b'SGDFL'


def label_source(text):
    anchor = '#include "namespace-label.inc"'
    if text.count(anchor) != 1:
        raise ValueError('readback label include context')
    return text.replace(anchor, '#include "readonly-exported-label.inc"', 1)


def build_reader(stage, command, tools):
    """Reuse original object/providers; redirect exactly one copied label input.

    The supplied command is an explicit build composition dependency. No module
    monkeypatch, sealed-source edit or production filesystem entry substitution.
    """
    from openzfs_elapsed import prepare
    from openzfs_failure import runtime_archive
    stage.mkdir()
    volume = ROOT/'user/storage/openzfs-volume'
    (stage/'readonly-exported-label.inc').write_text(labels((volume/'namespace-label.inc').read_text()))
    selected = stage/'readonly-exported-label.c'
    selected.write_text(label_source((volume/'pool-label.c').read_text()))
    changes = []
    def selected_command(argv, log, rejection=None):
        args = list(map(str, argv))
        if '-c' in args and args[args.index('-c')+1] == str(volume/'pool-label.c'):
            if changes:
                raise ValueError('duplicate readback label recipe')
            changes.append(dict(original_sha256=digest(volume/'pool-label.c'),
                                selected_sha256=digest(selected),
                                label_sha256=digest(stage/'readonly-exported-label.inc')))
            args[args.index('-c')+1] = str(selected)
        command(args, log, rejection=rejection)
    dependency = ROOT/'.deps/native-utc-v3'
    diagnostic = stage/'diagnostic'
    diagnostic.mkdir()
    diagnostic_result = runtime_archive(diagnostic, dependency, tools, selected_command)
    port = prepare(stage/'port', selected_command, entropy=True, allocation=True,
                   resources=True, arc=True, startup=True, volume=True,
                   volume_utc=True, utc_runtime=dependency/'runtime', volume_pool=True,
                   pool_diagnostics=True,
                   diagnostic_cc=diagnostic_result['backend_compiler_prefix'],
                   volume_pool_namespace=True)
    if len(changes) != 1:
        raise ValueError('missing independent readback label recipe')
    (port/'failure-runtime').mkdir()
    shutil.copyfile(diagnostic/'failure-runtime/libaether_runtime.a', port/'failure-runtime/libaether_runtime.a')
    sdk = ROOT/'.deps/native-current/sdk'
    cc = [tools['clang']['path'], '--no-default-config', '--target=x86_64-linux-musl',
          '--sysroot='+str(sdk/'empty-root'), '-std=c11', '-D_GNU_SOURCE', '-O2',
          '-Wall', '-Wextra', '-Werror', '-ffreestanding', '-fno-builtin',
          '-fstack-protector-strong', '-nostdinc', '-isystem', str(sdk/'stage/usr/include'),
          '-I', str(dependency/'runtime')]
    composition = runtime.compose_engine(port, selected_command, cc, tools, True,
        'pool-import', volume=True, utc=True, runtime=dependency, pool=True,
        diagnostics=True, pool_namespace=True)
    shutil.copyfile(port/'engine.elf', stage/'engine.elf')
    command(['rustc', '+1.98.0', '--edition=2024', '--target=x86_64-unknown-none',
             '-Dwarnings', '-C', 'opt-level=2', '-C', 'panic=abort',
             '-C', 'relocation-model=static', '-C', 'link-arg=-Tuser/protection/linker.ld',
             '-C', 'link-arg=--oformat=binary', ROOT/'user/storage/session/readback.rs',
             '-o', stage/'supervisor.raw'], stage/'controller.log')
    engine, owner = (stage/'engine.elf').read_bytes(), (stage/'supervisor.raw').read_bytes()
    if not 0 < len(owner) <= 4096:
        raise ValueError('independent readback controller bound')
    envelope = struct.pack('<8sII', b'AENBD002', len(engine), len(owner))+bytes([91])*32+engine+owner
    (stage/'native-c.bin').write_bytes(envelope)
    flags = '''native-memory native-memory-large native-image-large native-backing
native-service-memory native-threads native-thread-pair native-thread-reuse
native-thread-origin native-service-workers native-clock native-entropy native-rtc
native-service-block native-service-cleanup-trace'''.split()
    command(['zig', 'build', '-p', stage, '--cache-dir', ROOT/'.zig-cache',
             '--global-cache-dir', ROOT/'.zig-cache/global', '-Dsmp=false',
             '-Dnative-c-image='+str(stage/'native-c.bin'), *['-D'+f+'=true' for f in flags]], stage/'kernel.log')
    return dict(composition=composition, label_derivation=changes[0], controller_bytes=len(owner),
                read_grant_only=True, kernel_tick_limit=3000,
                port_sources=json.loads((port/'port-results.json').read_text()))


def recovery_media(writer, disk):
    from openzfs_namespace import _native_media_snapshot
    expected = dict(profile='AENFS003/sys-init-owner29/engine26', status='pass',
                    admitted_instances=2, reclaimed=2, final_live_workers=0,
                    cleanup_trace_version=1, cleanup_boundaries_per_instance=7)
    if (any(writer.get(k) != v for k, v in expected.items())
            or any(writer.get(k) is not True for k in ('vm_run_returned', 'read_only_activation',
                       'engine_terminal_zero', 'selected_process_terminal_zero',
                       'source_bound_readiness_and_shutdown'))
            or re.fullmatch('[0-9a-f]{64}', writer.get('disk_sha256', '')) is None):
        raise ValueError('init readback requires a clean stopped actual activation')
    result = _native_media_snapshot(disk)
    if result['sha256'] != writer['disk_sha256']:
        raise ValueError('init readback exact stopped media mismatch')
    return result


def failure_trace(text, selection, engine_pages):
    if selection not in FAILURES or type(engine_pages) is not int or not 17 <= engine_pages <= 8192:
        raise ValueError('invalid fixed failed-peer selection')
    before_process = selection in FAILURES[:2]
    index = FAILURES.index(selection)
    lines = text.splitlines()
    if (lines.count('AETHER PANIC: native supervisor terminated') != 1
            or sum('AETHER PANIC:' in s for s in lines) != 1
            or any('AETHER NATIVE BLOCK PASS' in s or s.startswith('NATIVE init halted ') or
                   s.startswith('NATIVE supervisor result=') for s in lines)):
        raise ValueError('failed peer must never successfully halt')
    faults = [s for s in lines if s.startswith('NATIVE fault ')]
    if len(faults) != 1:
        raise ValueError('failed-peer owner fault count')
    fault = re.fullmatch(r'NATIVE fault vector=6 rip=([0-9a-f]+) error=0', faults[0])
    if fault is None or not 0x400000 <= int(fault[1], 16) < 0x400000+2072:
        raise ValueError('failed-peer must trap in exact actual owner')
    marker = f'NATIVE observation slot=0 generation=1 offset=0 byte={TAGS[index]}'
    if [s for s in lines if s.startswith('NATIVE observation ')] != [marker]:
        raise ValueError('failed-peer executed stage witness')
    memory = re.findall(r'^NATIVE MEMORY admitted slot=(\d+) generation=(\d+) used=(\d+) remaining=(\d+)$', text, re.M)
    expected = [(0, 1, engine_pages, 8192-engine_pages)]
    if not before_process:
        expected.append((1, 1, 21, 107))
    if ([tuple(map(int, row)) for row in memory] != expected
            or sum(s.startswith('NATIVE MEMORY admitted ') for s in lines) != len(expected)):
        raise ValueError('failed-peer dependent admission/replay')
    terminals = [] if before_process else ['NATIVE terminal slot=1 generation=1 kind=1 detail=0']
    if selection == 'startup-exit':
        terminals.append('NATIVE terminal slot=0 generation=1 kind=1 detail=71')
    if selection == 'failed-exit':
        terminals.append('NATIVE terminal slot=0 generation=1 kind=1 detail=72')
    if [s for s in lines if s.startswith('NATIVE terminal ')] != terminals:
        raise ValueError('failed-peer terminal kind/status')
    cleanup = [] if before_process else [f'NATIVE CLEANUP v=1 slot=1 generation=1 phase={phase} selected={1 if phase==1 else 6} pages=128 reclaimed={int(phase==7)}' for phase in range(1, 8)]
    # finish() stops contexts and rotates on every terminal, irrespective of
    # status. Those phase1/2 observations are not an owner reclaim request;
    # phases3..7 may never occur for the failed/uncertain engine.
    engine_stop = []
    if selection in ('startup-exit', 'failed-exit'):
        engine_stop = [f'NATIVE CLEANUP v=1 slot=0 generation=1 phase={phase} selected={0 if phase==1 else 6} pages=8192 reclaimed={int(not before_process)}' for phase in (1, 2)]
    cleanup += engine_stop
    if [s for s in lines if s.startswith('NATIVE CLEANUP ')] != cleanup:
        raise ValueError('failed-peer stop/reclaim boundaries')
    order = [marker, faults[0], 'AETHER PANIC: native supervisor terminated']
    if not before_process:
        order = [terminals[0], *cleanup[:7], marker, *terminals[1:], *engine_stop, faults[0], order[-1]]
    elif selection == 'startup-exit':
        order = [marker, terminals[0], *engine_stop, faults[0], order[-1]]
    positions = [lines.index(s) for s in order]
    if positions != sorted(positions):
        raise ValueError('failed-peer stage/settlement/fault order')
    return dict(expected_failure=selection, actual_owner_fail_stop=True,
                dependent_admitted=not before_process, reclaimed_processes=int(not before_process),
                engine_reclaimed=False, successful_halt=False, automatic_replay=False,
                engine_terminal_stop_boundaries=len(engine_stop),
                scope='Fixed hostile-peer witness, not real OpenZFS fault recovery/cleanup')
