# SPDX-License-Identifier: BSD-2-Clause
"""Private checked file-vdev binding; no host-path fallback or pool policy."""
import hashlib
import json
import subprocess
from pathlib import Path
from deps import ROOT
from openzfs_elapsed import CURRENT, function, route

OWNED = ROOT / 'user/storage/openzfs-volume'
FUNCTIONS = ('zfs_file_open', 'zfs_file_close', 'zfs_file_write', 'zfs_file_pwrite',
             'zfs_file_read', 'zfs_file_pread', 'zfs_file_seek', 'zfs_file_getattr',
             'zfs_file_fsync', 'zfs_file_deallocate', 'zfs_file_off', 'zfs_file_unlink')


def patch_kernel(text, physical=False, open_trace=False, write=False):
    if open_trace and not physical:
        raise ValueError("open tracing requires the physical provider")
    if write and (not physical or open_trace):
        raise ValueError("write witness requires an exclusive physical provider")
    changes = []
    for name in FUNCTIONS:
        old = function(text, name)
        text = text.replace(old, '', 1)
        changes.append({'function': name, 'removed_sha256': hashlib.sha256(old.encode()).hexdigest()})
    anchor = 'uint64_t physmem;'
    if text.count(anchor) != 1 or 'file-functions.inc' in text:
        raise RuntimeError('volume provider include context changed')
    include = "file-physical-functions.inc" if physical else "file-functions.inc"
    trace = '#define AETHER_PHYSICAL_OPEN_TRACE 1\n' if open_trace else ''
    if write:
        trace += '#define AETHER_PHYSICAL_WRITE 1\n'
    return text.replace(anchor, trace + '#include "' + include + '"\n' + anchor, 1), changes


def patch_vdev(text, write=False):
    old = '\tvd->vdev_has_trim = B_TRUE;'
    if text.count(old) != 1:
        raise RuntimeError('volume TRIM context changed')
    text = text.replace(old, '\t/* Delegated region has no discard operation. */\n'
                       '\tvd->vdev_has_trim = B_FALSE;', 1)
    if write:
        original = function(text, 'vdev_file_io_fsync')
        renamed = original.replace('vdev_file_io_fsync(', 'aether_physical_fsync_callback_original(', 1)
        wrapper = '''
#include "write-witness.h"
static void vdev_file_io_fsync(void *argument)
{
    zio_t *zio = argument;
    aether_physical_flush_callback(zio->io_vd, zio->io_type == ZIO_TYPE_FLUSH);
    /* Original interrupt may release zio: no access after this call. */
    aether_physical_fsync_callback_original(argument);
}
'''
        declaration = 'static void aether_physical_fsync_callback_original(void *) __attribute__((__noinline__));\n'
        text = text.replace(original, declaration + renamed + wrapper, 1)
    return text


def patch_pool_workers(text):
    """One named throughput floor; retain every other pool queue and assertion."""
    old = '{ ZTI_SCALE(32), ZTI_NULL,\tZTI_ONE,\tZTI_NULL }, /* FREE */'
    new = '{ ZTI_SCALE(8), ZTI_NULL,\tZTI_ONE,\tZTI_NULL }, /* FREE */'
    if text.count(old) != 1:
        raise RuntimeError('pool FREE queue context changed')
    return text.replace(old, new, 1), [{'old': old, 'new': new}]


def build(output, base, command, workers=False, spa_utc=False, utc=False, spa_active=False, utc_runtime=None, spa_physical=False, write=False, pool=False, diagnostics=False, pool_data=False, pool_interrupt=False, pool_uncommitted=False, pool_recovery_check=None, pool_namespace=False, namespace_ipc=False, pool_zpl_write=False, pool_zpl_recover=False, pool_zpl_repeat=False, pool_zpl_stages=False, pool_zpl_write_stages=False, pool_zpl_txg_stages=False, pool_zpl_sync_stages=False, pool_fs_bridge=None, pool_recovery_diagnostic=False, pool_recovery_writer_60s=False, pool_zpl_zero=False, pool_namespace_mutation=None, pool_fs_service=None, pool_fs_service_case='normal', pool_fs_lifetimes=False, pool_fs_namespace=None, pool_fs_mixed=False, pool_fs_mixed_empty=False, namespace_wait=False, pool_fs_bulk=False, pool_fs_runtime=False, pool_fs_names=False, pool_fs_directories=False, pool_storage_lifetime=False):
    from openzfs_fs_runtime_service import validate_profile as runtime_profile
    runtime_profile(pool_fs_runtime, pool_fs_bulk, pool_fs_service)
    from openzfs_fs_directories_service import validate_profile as directories_profile
    directories_profile(pool_fs_directories,pool_fs_names,pool_zpl_recover,pool_fs_service)
    from storage_lifetime import validate as storage_lifetime_profile
    storage_lifetime_profile(pool_storage_lifetime,pool_fs_directories,pool_zpl_recover,pool_fs_service_case)
    from openzfs_fs_names_service import validate_profile as names_profile
    names_profile(pool_fs_names, isinstance(pool_fs_service,dict) and pool_fs_service.get('activation',False),pool_fs_runtime,pool_zpl_recover,pool_fs_service)
    from openzfs_fs_bulk_service import validate_profile as bulk_profile
    bulk_profile(pool_fs_bulk, pool_fs_mixed, namespace_wait, pool_zpl_write, pool_zpl_recover, pool_fs_service)
    from storage_channel_wait import validate as validate_wait
    validate_wait(namespace_wait,namespace_ipc,pool_namespace,pool_zpl_write,pool_zpl_recover,pool_fs_service,pool_namespace_mutation,pool_fs_mixed)
    from openzfs_fs_service import case_number
    service_case = case_number(pool_fs_service_case)
    from openzfs_fs_namespace import validate_profile as namespace_profile
    namespace_profile(pool_fs_namespace, pool_namespace_mutation, pool_zpl_write, pool_zpl_recover,
                      pool_fs_service, pool_fs_lifetimes, pool_fs_service_case)
    from openzfs_fs_mixed_service import validate_profile as mixed_profile
    mixed_profile(pool_fs_mixed,pool_zpl_write,pool_zpl_recover,pool_fs_service,
                  pool_fs_lifetimes,pool_fs_namespace,pool_fs_mixed_empty,pool_fs_service_case)
    if pool_fs_mixed and not (pool_namespace and pool and diagnostics and
            (pool_zpl_write or (pool_zpl_recover and pool_recovery_diagnostic and pool_recovery_writer_60s))):
        raise ValueError('mixed service requires fixed-budget namespace build')
    if not isinstance(pool_fs_lifetimes, bool) or (pool_fs_lifetimes and not (
            (pool_zpl_write and pool_fs_service is not None) or
            (pool_zpl_recover and pool_recovery_writer_60s and pool_recovery_diagnostic))):
        raise ValueError('filesystem service lifetimes require exact writer/recovery profile')
    if service_case and pool_fs_service is None:
        raise ValueError('filesystem service case requires its exact selection')
    if pool_fs_service is not None:
        if not (pool_zpl_write and namespace_ipc and pool_namespace and pool and diagnostics) or any((
                pool_fs_bridge is not None, pool_zpl_recover, pool_zpl_repeat, pool_zpl_stages,
                (pool_namespace_mutation is not None and pool_fs_namespace is None), pool_zpl_zero)):
            raise ValueError('filesystem service requires exclusive writable IPC namespace build')
        from openzfs_fs_service import recheck as service_recheck
        service_recheck(pool_fs_service)
        if pool_fs_service.get('lifetimes', False) is not pool_fs_lifetimes:
            raise ValueError('filesystem service lifetime delivery/profile mismatch')
    from openzfs_mutation import validate as validate_mutation
    validate_mutation(pool_namespace_mutation)
    if pool_namespace_mutation is not None and (not (pool_namespace and pool and diagnostics and (pool_zpl_write != pool_zpl_recover)) or
            pool_fs_bridge is not None or pool_zpl_zero or (namespace_ipc and pool_fs_namespace is None) or pool_zpl_stages or
            pool_zpl_repeat is not (pool_namespace_mutation in ('repeat', 'eight', 'lifetimes') and pool_zpl_write) or
            (pool_zpl_recover and not (pool_recovery_diagnostic and pool_recovery_writer_60s))):
        raise ValueError('namespace mutation requires exclusive namespace profile')
    if not isinstance(pool_zpl_zero, bool):
        raise ValueError('truncate zero selector must be boolean')
    if pool_zpl_zero and (not (pool_namespace and pool and diagnostics and (pool_zpl_write != pool_zpl_recover)) or
            pool_fs_bridge is not None or namespace_ipc or pool_zpl_repeat or pool_zpl_stages or
            (pool_zpl_recover and not (pool_recovery_writer_60s and pool_recovery_diagnostic))):
        raise ValueError('truncate zero requires exclusive namespace profiles')
    """Reconstruct the selected slot before replacing it; pin archive separately."""
    if not isinstance(pool_recovery_writer_60s, bool):
        raise ValueError('recovery writer window selector must be boolean')
    if pool_recovery_writer_60s and (not (pool_zpl_recover and pool_namespace and pool and diagnostics) or
            pool_zpl_write or namespace_ipc or pool_fs_bridge is not None):
        raise ValueError('recovery writer window requires isolated readonly namespace build')
    if pool_recovery_diagnostic and (not (pool_zpl_recover and pool_namespace and pool and diagnostics) or
            pool_zpl_write or namespace_ipc or pool_fs_bridge is not None):
        raise ValueError('recovery diagnostic requires isolated readonly namespace build')
    if pool_fs_bridge is not None:
        if not (pool_zpl_write and pool_namespace and pool and diagnostics) or any((
                namespace_ipc, pool_zpl_recover, pool_zpl_repeat, pool_zpl_stages)):
            raise ValueError('filesystem bridge requires exclusive single-write namespace build')
        from openzfs_fs_bridge import recheck
        recheck(pool_fs_bridge)
    if pool_zpl_sync_stages and not pool_zpl_txg_stages:
        raise ValueError("sync stages require worker profile")
    if pool_zpl_txg_stages and (not pool_zpl_stages or pool_zpl_write_stages):
        raise ValueError('TXG worker diagnostic requires exclusive stage profile')
    if pool_zpl_write_stages and not pool_zpl_stages:
        raise ValueError('first-write diagnostic requires stage profile')
    if pool_zpl_stages and not pool_zpl_repeat:
        raise ValueError('stage diagnostic requires repeated writer preparation')
    if pool_zpl_repeat and not pool_zpl_write:
        raise ValueError('repeated ZPL requires isolated writer preparation')
    if pool_zpl_recover and (not pool_namespace or namespace_ipc or pool_zpl_write):
        raise ValueError('ZPL recovery requires isolated namespace preparation')
    if pool_zpl_write and (not pool_namespace or (namespace_ipc and pool_fs_service is None)):
        raise ValueError('ZPL writer requires isolated namespace preparation')
    if namespace_ipc and not pool_namespace:
        raise ValueError('namespace IPC requires namespace profile')
    if pool_namespace and (not (pool and diagnostics) or pool_data or pool_interrupt or pool_recovery_check):
        raise ValueError('namespace requires exclusive diagnostic pool import')
    if pool_recovery_check is not None and (pool_recovery_check not in ('capacity', 'uberblock-checksum') or
            not (pool and pool_data and diagnostics) or pool_interrupt):
        raise ValueError('pool recovery check requires exclusive diagnostic data')
    if pool_uncommitted and not pool_interrupt:
        raise ValueError("uncommitted pool requires interrupted data")
    if pool_interrupt and not (pool and pool_data and diagnostics):
        raise ValueError('pool interruption requires diagnostic assigned data')
    if pool_data and not pool:
        raise ValueError('pool data requires pool selection')
    sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
    receipt = json.loads((CURRENT / 'build-attempt-5/results.json').read_text())
    recipe = next(c['argv'] for c in receipt['commands'] if c['name'] == 'input-104-checked')
    prefix = [route(a) for a in recipe[:recipe.index('-c')]]
    prefix[1:1] = ['-I' + str(output / 'resources'), '-I' + str(output / 'allocation'),
                   '-I' + str(OWNED)]
    if pool:
        prefix += ['-isystem', str(Path(prefix[0]).parents[1] / 'lib/clang/21/include'),
                   '-Wall', '-Wextra', '-Werror']
    source = Path(route(recipe[recipe.index('-c') + 1]))
    original = output / 'vdev-original.o'
    command(prefix + ['-c', source, '-o', original], output / 'vdev-original.log')
    if sha(original) != sha(base[104]):
        raise RuntimeError('selected vdev slot bytes changed')
    changed = output / 'vdev_file.c'
    vdev_text = source.read_text()
    if pool:
        from openzfs_pool import patch_pool_vdev
        vdev_text = patch_pool_vdev(vdev_text)
    if pool_zpl_write:
        from openzfs_pool import trusted_write_hooks, repeated_write_hooks, eight_write_hooks, lifetime_write_hooks
        hook_source = lifetime_write_hooks if pool_namespace_mutation == 'lifetimes' else eight_write_hooks if pool_namespace_mutation == 'eight' else repeated_write_hooks if pool_zpl_repeat else trusted_write_hooks
        if pool_fs_lifetimes:
            from openzfs_fs_lifetime import service_lifetime_hooks, service_lifetime_record
            hook_source = service_lifetime_hooks
            (output / 'pool-service-lifetime.inc').write_text(
                service_lifetime_record((OWNED / 'pool-lifetime.inc').read_text()))
        if pool_fs_mixed:
            from openzfs_fs_mixed import mixed_lifetime_hooks,mixed_lifetime_record
            if pool_fs_bulk:
                from openzfs_fs_bulk import bulk_lifetime_hooks as mixed_lifetime_hooks,bulk_lifetime_record as mixed_lifetime_record
            hook_source=mixed_lifetime_hooks
            (output/('pool-bulk-lifetime.inc' if pool_fs_bulk else 'pool-mixed-lifetime.inc')).write_text(mixed_lifetime_record((OWNED/'pool-lifetime.inc').read_text()))
        (output / 'pool-vdev-hooks.inc').write_text(
            hook_source((OWNED / 'pool-vdev-hooks.inc').read_text()))
    if pool_zpl_txg_stages:
        from openzfs_pool import worker_flow, sync_stage_flow
        (output / 'pool-repeat.inc').write_text((sync_stage_flow if pool_zpl_sync_stages else worker_flow)((OWNED / 'pool-repeat.inc').read_text()))
    changed.write_text(patch_vdev(vdev_text, write=write))
    target = str(source)
    for arg in prefix:
        if arg.startswith('-fmacro-prefix-map='):
            left, right = arg.removeprefix('-fmacro-prefix-map=').split('=', 1)
            if str(source).startswith(left):
                target = right + str(source)[len(left):]
                break
    vdev_selected = output / 'vdev-selected.o'
    command(prefix + ['-fmacro-prefix-map=' + str(changed) + '=' + target,
                     '-c', changed, '-o', vdev_selected], output / 'vdev-selected.log')
    base[104] = str(vdev_selected)
    probe = output / 'volume-probe.o'
    command(prefix + ['-Wall', '-Wextra', '-Werror', '-c', OWNED / 'probe.c', '-o', probe],
            output / 'volume-probe.log')
    worker_object = output / 'volume-worker-probe.o'
    if workers:
        command(prefix + ['-Wall', '-Wextra', '-Werror', '-c', OWNED / 'worker-probe.c', '-o', worker_object],
                output / 'volume-worker-probe.log')
    utc_object = output / 'spa-utc-probe.o'
    if spa_utc:
        command(prefix + ['-Wall', '-Wextra', '-Werror', '-c', OWNED / 'spa-utc-probe.c', '-o', utc_object],
                output / 'spa-utc-probe.log')
    utc_engine = output / 'volume-utc-probe.o'
    if utc:
        command(prefix + ['-I' + str(utc_runtime or ROOT / '.deps/native-utc-v2/runtime'),
                          '-Wall', '-Wextra', '-Werror', '-c', OWNED / 'volume-utc-probe.c', '-o', utc_engine],
                output / 'volume-utc-probe.log')
    active_receipt = None
    if spa_active or spa_physical or pool:
        # Match the allocation/resource-aware slot already reconstructed above.
        spa_recipe = next(c['argv'] for c in receipt['commands'] if c['name'] == 'input-90-checked')
        spa_prefix = [route(a) for a in spa_recipe[:spa_recipe.index('-c')]]
        spa_prefix[1:1] = ['-I' + str(output / 'resources'), '-I' + str(output / 'allocation')]
        if pool:
            spa_prefix += ['-isystem', str(Path(spa_prefix[0]).parents[1] / 'lib/clang/21/include')]
        spa_source = Path(route(spa_recipe[spa_recipe.index('-c') + 1]))
        spa_original = output / 'spa-active-original.o'
        command(spa_prefix + ['-c', spa_source, '-o', spa_original], output / 'spa-active-original.log')
        if sha(spa_original) != sha(base[90]):
            raise RuntimeError('selected resource/allocation SPA slot changed')
        import_include = OWNED / 'spa-import.inc'
        if pool_zpl_stages:
            from openzfs_pool import staged_import_probe
            import_include = output / 'spa-stage-import.inc'
            import_include.write_text(staged_import_probe((OWNED / 'spa-zpl-write.inc').read_text()))
        changed_spa = output / 'spa-active.c'
        spa_text = spa_source.read_text()
        worker_edits = []
        if pool:
            spa_text, worker_edits = patch_pool_workers(spa_text)
        if pool_zpl_sync_stages:
            from openzfs_pool import patch_sync_spa
            spa_text = patch_sync_spa(spa_text)
        changed_spa.write_text(spa_text + '\n' +
                               ('#define AETHER_PHYSICAL_WRITE 1\n' if write else '') +
                               ('#define AETHER_POOL_DIAGNOSTICS 1\n' if diagnostics else '') +
                               ('#define AETHER_POOL_INTERRUPT 1\n' if pool_interrupt else '') +
                               ('#define AETHER_POOL_UNCOMMITTED 1\n' if pool_uncommitted else '') +
                               ('#define AETHER_POOL_CAPACITY_PROBE 1\n' if pool_recovery_check == 'capacity' else '') +
                               ('#define AETHER_POOL_BAD_UBERBLOCKS 1\n' if pool_recovery_check == 'uberblock-checksum' else '') +
                               ('#define AETHER_POOL_DATA 1\n#include "pool-data.c"\n' if pool_data else '') +
                               ('#define AETHER_POOL_NAMESPACE 1\n' if pool_namespace else '') +
                               ('#define AETHER_POOL_ZPL_WRITE 1\n' if pool_zpl_write else '') +
                               ('#define AETHER_POOL_ZPL_RECOVER 1\n' if pool_zpl_recover else '') +
                               ('#include "spa-pool.inc"\n' if pool else '#include "spa-active.inc"\n') +
                               ('#include "' + import_include.name + '"\n' if pool else '') +
                               ('#include "spa-physical.inc"\n' if spa_physical else ''))
        macro_path = str(spa_source)
        for arg in spa_prefix:
            if arg.startswith('-fmacro-prefix-map='):
                left, right = arg.removeprefix('-fmacro-prefix-map=').split('=', 1)
                if str(spa_source).startswith(left):
                    macro_path = right + str(spa_source)[len(left):]
                    break
        spa_selected = output / 'spa-active-selected.o'
        command(spa_prefix + ['-I' + str(OWNED), '-fmacro-prefix-map=' + str(changed_spa) + '=' + macro_path,
                             '-ffunction-sections', '-fdata-sections', '-c', changed_spa, '-o', spa_selected], output / 'spa-active-selected.log')
        base[90] = str(spa_selected)
        active_receipt = {'slot': 90, 'original_sha256': sha(spa_original),
                          'selected_sha256': sha(spa_selected), 'source_sha256': sha(changed_spa),
                          **({'pool_worker_edits': worker_edits} if worker_edits else {}),
                          'include_sha256': sha(OWNED / ('spa-pool.inc' if pool else 'spa-active.inc')),
                          **({'import_include_sha256': sha(import_include)} if pool else {}),
                          'physical_include_sha256': sha(OWNED / 'spa-physical.inc') if spa_physical else None}
    pool_receipt = None
    if pool:
        from openzfs_pool import build_pool_objects
        pool_receipt = build_pool_objects(output, base, receipt, command, active_labels=pool_interrupt, namespace=pool_namespace, namespace_recovery=pool_zpl_recover or pool_namespace_mutation in ('rename', 'remove', 'extend', 'repeat', 'eight', 'lifetimes'), worker_stages=pool_zpl_txg_stages, sync_stages=pool_zpl_sync_stages)
    namespace_objects = {}
    if pool_fs_lifetimes and pool_zpl_write:
        namespace_objects['service-lifetime-hooks-source'] = sha(output / 'pool-vdev-hooks.inc')
        namespace_objects['service-lifetime-record-source'] = sha(output / 'pool-service-lifetime.inc')
    if pool_fs_mixed:
        namespace_objects['mixed-label-source']=sha(output/'namespace-recovery-label.inc' if pool_zpl_recover else OWNED/'namespace-label.inc')
        if pool_zpl_write:
            namespace_objects['mixed-hooks-source']=sha(output/'pool-vdev-hooks.inc')
            namespace_objects['mixed-record-source']=sha(output/('pool-bulk-lifetime.inc' if pool_fs_bulk else 'pool-mixed-lifetime.inc'))
    if pool_namespace_mutation is not None:
        namespace_objects['mutation-label-source'] = sha(
            output / 'namespace-recovery-label.inc' if pool_zpl_recover or
            pool_namespace_mutation in ('rename', 'remove', 'extend', 'repeat', 'eight', 'lifetimes') else OWNED / 'namespace-label.inc')
    if pool_zpl_write:
        namespace_objects['vdev-write-hooks-source'] = sha(output / 'pool-vdev-hooks.inc')
    if pool_namespace:
        node_recipe = next(c['argv'] for c in receipt['commands'] if c['name'] == 'input-176-checked')
        node_prefix = [route(a) for a in node_recipe[:node_recipe.index('-c')]]
        node_prefix[1:1] = ['-I' + str(output / 'resources'), '-I' + str(output / 'allocation'), '-I' + str(OWNED)]
        node_prefix += ['-isystem', str(Path(node_prefix[0]).parents[1] / 'lib/clang/21/include')]
        names = (('zpl-mutation', 'zpl-accounting') if pool_zpl_write else ('zpl-mutation',)) if pool_namespace_mutation is not None else ('zpl-zero-probe', 'zpl-accounting') if pool_zpl_zero and pool_zpl_write else ('zpl-write', 'zpl-accounting', 'zpl-write-probe') if pool_zpl_write else ('zpl-recovery',) if pool_zpl_recover else ('zpl-read', 'owner-probe')
        if pool_fs_mixed:names=('zpl-mutation','zpl-accounting') if pool_zpl_write else ('zpl-mutation',)
        for name in names:
            obj = output / (name + '.o')
            node_source = OWNED / (name + '.c')
            if name == 'zpl-mutation':
                from openzfs_mutation import source as mutation_source
                node_source = output / 'zpl-mutation-selected.c'
                if pool_fs_mixed:
                    from openzfs_fs_mixed_service import probe as mixed_probe,owner as mixed_owner
                    if pool_fs_bulk:
                        from openzfs_fs_bulk_service import probe as mixed_probe,owner as mixed_owner
                    if pool_fs_runtime:
                        from openzfs_fs_runtime_service import probe as mixed_probe,owner as mixed_owner
                    if pool_fs_service is not None and pool_fs_service.get('activation',False):
                        from openzfs_fs_activation_service import owner as mixed_owner
                    if pool_fs_names:
                        from openzfs_fs_names_service import probe as mixed_probe, owner as mixed_owner
                    if pool_fs_directories:
                        from openzfs_fs_directories_service import probe as mixed_probe, owner as mixed_owner
                    node_source.write_text(mixed_probe((OWNED/'zpl-mutation-probe.c').read_text(),pool_zpl_recover,
                        pool_fs_mixed_empty if pool_zpl_recover else pool_fs_service_case in (('lost-reply','partial-request') if pool_fs_bulk else ('lost-reply',)),pool_fs_service_case, **({'storage_lifetime':True} if pool_storage_lifetime else {})))
                    namespace_objects['mixed-probe-source']=sha(node_source)
                    if pool_zpl_write:
                        (output/'fs-mixed-owner.inc').write_text(mixed_owner((OWNED/'fs-service-owner.inc').read_text(),namespace_wait))
                        namespace_objects['mixed-owner-source']=sha(output/'fs-mixed-owner.inc')
                        node_prefix+=['-I'+pool_fs_service['header_directory']]
                elif pool_fs_namespace is not None:
                    from openzfs_fs_namespace import probe as namespace_service_probe, owner as namespace_service_owner
                    node_source.write_text(namespace_service_probe((OWNED/'zpl-mutation-probe.c').read_text(), pool_fs_namespace, pool_zpl_recover, pool_fs_service_case))
                    if pool_zpl_write:
                        (output/'fs-namespace-owner.inc').write_text(namespace_service_owner((OWNED/'fs-service-owner.inc').read_text()))
                        namespace_objects['fs-namespace-owner-source']=sha(output/'fs-namespace-owner.inc')
                        node_prefix += ['-I'+pool_fs_service['header_directory']]
                else:
                    node_source.write_text(mutation_source(pool_namespace_mutation, pool_zpl_recover))
                namespace_objects['mutation-selected-source'] = sha(node_source)
            if pool_zpl_txg_stages and name == 'zpl-write':
                from openzfs_pool import worker_write_provider
                node_source = output / 'zpl-write.c'
                node_source.write_text(worker_write_provider((OWNED / 'zpl-write.c').read_text()))
                namespace_objects['worker-provider-source'] = sha(node_source)
                namespace_objects['worker-flow-source'] = sha(output / 'pool-repeat.inc')
            if pool_zpl_write_stages and name == 'zpl-write':
                from openzfs_pool import first_write_provider
                node_source = output / 'zpl-write.c'
                node_source.write_text(first_write_provider((OWNED / 'zpl-write.c').read_text()))
                namespace_objects['first-write-provider-source'] = sha(node_source)
            if pool_zpl_repeat and name == 'zpl-write-probe':
                from openzfs_pool import repeated_write_probe, staged_write_probe, first_write_probe, transaction_write_probe
                node_source = output / 'zpl-write-probe.c'
                probe_source = transaction_write_probe if pool_zpl_txg_stages else first_write_probe if pool_zpl_write_stages else staged_write_probe if pool_zpl_stages else repeated_write_probe
                node_source.write_text(probe_source((OWNED / 'zpl-write-probe.c').read_text()))
                namespace_objects['repeat-probe-source'] = sha(node_source)
                namespace_objects['repeat-flow-source'] = sha(OWNED / 'pool-repeat.inc')
            if (pool_recovery_diagnostic or pool_recovery_writer_60s) and name == 'zpl-recovery':
                from openzfs_fs_bridge import recovery_source
                node_source = output / 'zpl-recovery-selected.c'
                if pool_fs_lifetimes:
                    from openzfs_fs_service import lifetime_recovery
                    text = lifetime_recovery((OWNED / 'zpl-recovery.c').read_text())
                elif pool_zpl_zero:
                    from openzfs_zero import recovery as zero_recovery
                    text = zero_recovery((OWNED / 'zpl-recovery.c').read_text())
                else:
                    text = recovery_source((OWNED / 'zpl-recovery.c').read_text(),
                                           pool_recovery_writer_60s, pool_recovery_diagnostic)
                node_source.write_text(text)
                namespace_objects['recovery-selected-source'] = sha(node_source)
            if pool_fs_service is not None and name == 'zpl-write-probe':
                from openzfs_fs_service import probe as service_probe
                node_source = output / 'zpl-service-probe.c'
                node_source.write_text(service_probe((OWNED / 'zpl-write-probe.c').read_text(), pool_fs_service_case, pool_fs_lifetimes))
                namespace_objects['fs-service-probe-source'] = sha(node_source)
                namespace_objects['fs-service-owner-source'] = sha(OWNED / 'fs-service-owner.inc')
                node_prefix += ['-I' + pool_fs_service['header_directory']]
            if pool_fs_bridge is not None and name == 'zpl-write-probe':
                from openzfs_fs_bridge import probe as bridge_probe
                node_source = output / 'zpl-bridge-probe.c'
                node_source.write_text(bridge_probe((OWNED / 'zpl-write-probe.c').read_text()))
                namespace_objects['fs-bridge-probe-source'] = sha(node_source)
                node_prefix += ['-I' + pool_fs_bridge['header_directory']]
            command(node_prefix + (['-DAETHER_ZPL_ORDERED_WRITE=1', '-fstack-usage'] if pool_zpl_write else ['-fstack-usage'] if pool_zpl_recover else []) + ['-std=gnu11', '-Wall', '-Wextra', '-Werror',
                                   '-ffunction-sections', '-fdata-sections', '-c', node_source, '-o', obj],
                    output / (name + '.log'))
            base.append(str(obj))
            namespace_objects[name] = sha(obj)
            if pool_fs_bridge is not None or pool_fs_service is not None or pool_zpl_zero or pool_namespace_mutation is not None or pool_fs_mixed:
                stack = obj.with_suffix('.su').read_text()
                if 'dynamic' in stack or any(int(row.split('\t')[1]) > 8192 for row in stack.splitlines()):
                    raise ValueError('filesystem bridge C local frame exceeds bound')
                namespace_objects[name + '-local-frames'] = stack
            if pool_zpl_txg_stages and name == 'zpl-write':
                stack = obj.with_suffix('.su').read_text()
                if 'dynamic' in stack or any(int(row.split('\t')[1]) > 8192 for row in stack.splitlines()):
                    raise ValueError('TXG worker provider local frame exceeds bound')
                namespace_objects['worker-provider-local-frames'] = stack
    if pool_zpl_write:
        from openzfs_namespace import accounting_source
        source = CURRENT / 'baseline/source/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1/module/zfs/zfs_quota.c'
        selected = output / 'zpl-quota-original.c'
        selected.write_text(accounting_source(source.read_text()))
        obj = output / 'zpl-quota.o'
        command(node_prefix + ['-std=gnu11', '-Wall', '-Wextra', '-Werror', '-Wno-error=sign-compare',
                              '-fstack-usage', '-ffunction-sections', '-fdata-sections', '-c', selected, '-o', obj],
                output / 'zpl-quota.log')
        base.append(str(obj))
        namespace_objects['zpl-quota'] = sha(obj)
        namespace_objects['zpl-quota-source'] = sha(selected)
    if pool_fs_bridge is not None:
        recheck(pool_fs_bridge)
        base.append(pool_fs_bridge['object'])
        namespace_objects['fs-bridge-consumer'] = sha(pool_fs_bridge['object'])
    if pool_fs_service is not None:
        service_recheck(pool_fs_service)
        if pool_fs_service.get('lifetimes', False) is not pool_fs_lifetimes:
            raise ValueError('filesystem service lifetime delivery/profile mismatch')
        base.append(pool_fs_service['object'])
        namespace_objects['fs-service-consumer'] = sha(pool_fs_service['object'])
    compiler = Path(subprocess.check_output(['rustup', 'which', '--toolchain', '1.98.0', 'rustc'], text=True).strip())
    libraries = Path(subprocess.check_output([str(compiler), '--print', 'target-libdir', '--target=x86_64-unknown-none'], text=True).strip())
    rust_inputs = {str(compiler): sha(compiler), **{str(p): sha(p) for p in libraries.glob('*.rlib')}}
    if not any('libcore-' in p for p in rust_inputs) or not any('libcompiler_builtins-' in p for p in rust_inputs):
        raise RuntimeError('missing native Rust libraries')
    if pool_namespace and not (pool_zpl_write or pool_zpl_recover):
        obj = output / 'namespace-zpl.o'
        command([compiler, '--crate-name', 'namespace_zpl', '--edition=2024',
                 '--crate-type=lib', '--target=x86_64-unknown-none', '--emit=obj',
                 '-Dwarnings', '-Copt-level=2', '-Cpanic=abort', '-Crelocation-model=static',
                 *(['--cfg', 'namespace_ipc'] if namespace_ipc else []),
                 *(['--cfg', 'namespace_wait'] if namespace_wait else []),
                 OWNED / 'namespace-zpl.rs', '-o', obj], output / 'namespace-zpl.log')
        base.append(str(obj))
        namespace_objects['namespace-zpl'] = sha(obj)
    archive = output / 'libaether_volume.a'
    command(['rustc', '+1.98.0', '--edition=2024', '--crate-type=staticlib',
             '--target=x86_64-unknown-none', '-C', 'opt-level=2', '-C', 'panic=abort',
             '-C', 'relocation-model=static', *(['--cfg', 'pool_diagnostics'] if diagnostics else []), OWNED / 'volume.rs', '-o', archive],
            output / 'volume-rust.log')
    if any(sha(p) != h for p, h in rust_inputs.items()):
        raise RuntimeError('Rust input changed during compilation')
    return {**({'fs_service': pool_fs_service} if pool_fs_service is not None else {}), **({'fs_bridge': pool_fs_bridge} if pool_fs_bridge is not None else {}), 'namespace_objects': namespace_objects, 'pool': pool_receipt, 'spa_active': active_receipt, 'utc_object_sha256': sha(utc_engine) if utc else None, 'spa_utc_object_sha256': sha(utc_object) if spa_utc else None, 'worker_object_sha256': sha(worker_object) if workers else None, 'rust_inputs': rust_inputs, 'vdev_slot': 104, 'original_sha256': sha(original),
            'selected_sha256': sha(vdev_selected), 'selected_source_sha256': sha(changed),
            'probe_sha256': sha(probe), 'rust_archive_sha256': sha(archive),
            'trim_available': False, 'rust_toolchain': '1.98.0'}
