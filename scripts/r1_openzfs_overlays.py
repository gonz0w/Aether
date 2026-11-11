# SPDX-License-Identifier: BSD-2-Clause
"""Render the OpenZFS source adaptations selected by the R1 Zsh engine."""
import hashlib
import json
from pathlib import Path
import runpy
import sys

import fs_launch
import openzfs_elapsed as elapsed
import openzfs_failure as failure
import openzfs_fs_bulk as bulk
import openzfs_namespace as namespace
import openzfs_pool as pool
import openzfs_volume as volume

ROOT = Path(__file__).resolve().parents[1]
ELAPSED = ROOT / 'user/storage/openzfs-elapsed'
VOLUME = ROOT / 'user/storage/openzfs-volume'
OVERLAYS = VOLUME / 'r1-source-overlays'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def render(upstream, sdk, work):
    """Use pinned upstream and tracked adapters to render a fresh engine tree."""
    sys.path.insert(0, str(ROOT / 'sys-init/scripts'))
    from bounded_tools import run_tool

    staging = work / 'initial-overlays'
    staging.mkdir()
    specs = json.loads((OVERLAYS / 'inputs.json').read_text())
    originals = {}
    environment = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'}
    for name, row in specs.items():
        source = upstream / row['source']
        raw = source.read_bytes()
        require(digest(raw) == row['sha256'], 'upstream source differs: ' + name)
        if 'patch' in row:
            destination = staging / name
            run_tool(['/usr/bin/patch', '-s', '-o', str(destination),
                      str(source), str(OVERLAYS / row['patch'])], environment,
                     staging / (name + '.log'), timeout=10, cwd=staging)
            raw = destination.read_bytes()
        require(digest(raw) == row['adapted_sha256'], 'adapted source differs: ' + name)
        originals[name] = raw.decode()

    generated = {}

    def write(name, content):
        require(name not in generated, 'duplicate generated engine source')
        data = content.encode() if isinstance(content, str) else content
        path = work / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        generated[name] = digest(data)

    write('base/port/abd_os.c', originals['abd'])
    write('base/port/backtrace-native.c', originals['backtrace'])
    write('base/port/native-diagnostics.h',
          '/* SPDX-License-Identifier: BSD-2-Clause */\n'
          '#define AETHER_NATIVE_PROFILE 1\n#undef HAVE_BACKTRACE\n'
          '#undef HAVE_LIBUNWIND\n#undef HAVE_LIBUNWIND_ELF\n')
    write('base/port/resources/resources.h', (ELAPSED / 'resources.h').read_bytes())
    write('base/port/resources/sys/zfs_context.h',
          '/* SPDX-License-Identifier: BSD-2-Clause */\n'
          '#include_next <sys/zfs_context.h>\n#include <resources.h>\n'
          '#undef boot_ncpus\n#define boot_ncpus (aether_zfs_assigned_cpus())\n')
    text = failure.instrument(originals['time'], 'time')[0]
    require(text.count('#include_next <sys/time.h>') == 1, 'time include context')
    write('base/port/allocation/sys/time.h',
          text.replace('#include_next <sys/time.h>', '#include "sdk-time.h"'))
    write('base/port/allocation/sys/sdk-time.h', (sdk / 'include/sys/time.h').read_bytes())
    write('base/port/allocation/umem.h', elapsed.patch_alloc_header(originals['umem'])[0])

    text = originals['kernel']
    for patch in (elapsed.patch_kernel, elapsed.patch_entropy, elapsed.patch_alloc_kernel,
                  elapsed.patch_resources, elapsed.patch_startup):
        text = patch(text)[0]
    text = volume.patch_kernel(text, physical=False, open_trace=False, write=False)[0]
    write('base/port/kernel.c', failure.instrument(text, 'kernel')[0])
    write('base/port/thread_pool.c',
          failure.instrument(elapsed.patch_tpool(originals['thread-pool'])[0], 'tpool')[0])
    write('base/port/allocation/assert-native.c', failure.instrument(originals['assert'], 'assertion')[0])
    taskq = originals['taskq']
    cpu = 'sysconf(_SC_NPROCESSORS_ONLN)'
    require(taskq.count(cpu) == 1, 'taskq assigned CPU context')
    write('base/port/resources/taskq.c', taskq.replace(cpu, 'aether_zfs_assigned_cpus()'))
    arc = (upstream / 'lib/libzpool/arc_os.c').read_text()
    write('base/port/resources/arc_os.c', failure.instrument(elapsed.patch_arc_adapter(arc)[0], 'arc')[0])
    write('base/port/resources/arc.c',
          elapsed.patch_arc_initializer((upstream / 'module/zfs/arc.c').read_text())[0])
    write('base/port/resources/resources.c', failure.instrument((ELAPSED / 'resources.c').read_text(), 'resources')[0])
    write('base/port/startup-provider.c', failure.instrument((ELAPSED / 'startup.c').read_text(), 'startup')[0])
    write('base/port/vdev_file.c', volume.patch_vdev(pool.patch_pool_vdev(originals['vdev']), write=False))
    write('base/port/pool-vdev-hooks.inc', bulk.bulk_lifetime_hooks((VOLUME / 'pool-vdev-hooks.inc').read_text()))
    write('base/port/pool-bulk-lifetime.inc', bulk.bulk_lifetime_record((VOLUME / 'pool-lifetime.inc').read_text()))
    spa = volume.patch_pool_workers((upstream / 'module/zfs/spa.c').read_text())[0]
    write('base/port/spa-active.c', spa + '\n#define AETHER_POOL_DIAGNOSTICS 1\n'
          '#define AETHER_POOL_NAMESPACE 1\n#define AETHER_POOL_ZPL_WRITE 1\n'
          '#include "spa-pool.inc"\n#include "spa-import.inc"\n')
    for name, path, patch in (
        ('txg', 'txg.c', pool.patch_pool_txg),
        ('labels', 'vdev_label.c', pool.patch_pool_labels),
        ('graph', 'zio.c', pool.patch_pool_graph),
    ):
        write('base/port/pool-' + name + '.c', patch((upstream / 'module/zfs' / path).read_text()))
    write('base/port/pool-label-original.inc',
          pool.pool_label_bodies((upstream / 'lib/libzutil/zutil_import.c').read_text()))
    write('base/port/zpl-quota-original.c',
          namespace.accounting_source((upstream / 'module/zfs/zfs_quota.c').read_text()))
    frontend = ROOT / 'userland/experiments/filesystem-service/home_native_source.py'
    render_home = runpy.run_path(str(frontend))['render']
    for source in (ROOT / 'user/storage/service-runtime/filesystem-engine.c', VOLUME / 'filesystem-import.c'):
        text, _ = render_home(source)
        write('launch/home-c/home-' + source.name, text)
    write('launch/namespace-home-label.inc', fs_launch.labels((VOLUME / 'namespace-label.inc').read_text()))
    label = (VOLUME / 'pool-label.c').read_text()
    require(label.count('#include "namespace-label.inc"') == 1, 'home label context')
    write('launch/pool-home-label.c', label.replace('#include "namespace-label.inc"',
                                                 '#include "namespace-home-label.inc"'))
    return generated
