# SPDX-License-Identifier: BSD-2-Clause
"""Checked private OpenZFS elapsed port builder, not an engine startup runner."""
import hashlib
import json
from pathlib import Path
import re
from deps import ROOT

CURRENT = ROOT / '.deps/native-current'
OWNED = ROOT / 'user/storage/openzfs-elapsed'
PINS = {'build-attempt-1/source/kernel.c': '0009a198c38bb45f261359565434c53f894092c2c9242b54a0e1319998764faf',
        'previous-build/source/thread_pool.c': '2777669a32fab1feb1128dcc9b996cbe504230ce9d7d6b59040d2662ce032484'}


def check_intermediate_imports(imports, physical=False, worker_stages=False):
    """Geometry-only legacy link; final native origin checks stay mandatory."""
    allowed = {('U', '_DYNAMIC')}
    if physical:
        allowed.add(('w', 'aether_physical_io_phase'))
    if worker_stages:
        allowed.add(('w', 'aether_pool_worker_phase'))
    if any(tuple(line.split()) not in allowed for line in imports.splitlines() if line.strip()):
        raise RuntimeError('new unresolved engine import')


def function(text, name):
    """Audited brace-balanced functions in pinned sources, not a C parser."""
    matches = list(re.finditer(r'^(?:static (?:inline )?)?(?:void\s*\*|umem_cache_t\s*\*|void|int|uint64_t|int64_t|loff_t)\s*' + re.escape(name) + r'\(', text, re.MULTILINE))
    if len(matches) != 1:
        raise RuntimeError('elapsed function context changed: ' + name)
    start = matches[0].start()
    end = text.index('{', matches[0].end()) + 1
    depth = 1
    while depth and end < len(text):
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    if depth:
        raise RuntimeError('unclosed elapsed function: ' + name)
    return text[start:end]


def patch_alloc_header(text):
    replacement = (OWNED / 'alloc-functions.c').read_text()
    changes = []
    for name in ('umem_alloc', 'umem_alloc_aligned', 'umem_cache_create', 'umem_cache_alloc'):
        old, new = function(text, name), function(replacement, name)
        text = text.replace(old, new, 1)
        changes.append({'function': name, 'old': old, 'new': new})
    old = function(text, 'umem_nofail_callback')
    text = text.replace(old, '', 1)
    changes.append({'function': 'unused nofail callback registration', 'old': old, 'new': ''})
    return text, changes


def patch_alloc_kernel(text):
    old = function(text, 'umem_out_of_memory')
    registration = '\tumem_nofail_callback(umem_out_of_memory);\n'
    if text.count(registration) != 1:
        raise RuntimeError('allocation callback registration context changed')
    return text.replace(old, '', 1).replace(registration, '', 1), [
        {'function': 'unused core-dump routine', 'old': old, 'new': ''},
        {'old': registration, 'new': ''}]


def patch_resources(text):
    old = '\tphysmem = sysconf(_SC_PHYS_PAGES);\n\n\tdprintf("physmem = %llu pages (%.2f GB)\\n", (u_longlong_t)physmem,\n\t    (double)physmem * sysconf(_SC_PAGE_SIZE) / (1ULL << 30));'
    new = '\t/* Legacy upstream label: total granted domain backing, not RAM. */\n\tphysmem = aether_zfs_granted_pages();'
    if text.count(old) != 1:
        raise RuntimeError('resource initialization context changed')
    return text.replace(old, new, 1), [{'old': old, 'new': new}]


def patch_startup(text):
    changes = []
    for old, new in [
        ('get_system_hostid()', 'aether_zfs_hostid()'),
        ('VERIFY0(uname(&hw_utsname));', 'aether_zfs_uname(&hw_utsname);'),
        ('#include <poll.h>', '#include <poll.h>\n#include "startup.h"'),
    ]:
        if text.count(old) != 1:
            raise RuntimeError('startup binding context changed: ' + old)
        text = text.replace(old, new, 1)
        changes.append({'old': old, 'new': new})
    old = function(text, 'spa_config_load')
    new = 'static void\nspa_config_load(void)\n{\n\t/* Explicit empty configuration; no unsupported-I/O fallback. */\n\taether_zfs_empty_cache();\n}'
    text = text.replace(old, new, 1)
    changes.append({'function': 'spa_config_load', 'old': old, 'new': new})
    return text, changes


def patch_arc_adapter(text):
    replacement = (OWNED / 'arc-functions.c').read_text()
    changes = []
    for name in ('arc_all_memory', 'arc_free_memory', 'arc_available_memory'):
        old, new = function(text, name), function(replacement, name)
        text = text.replace(old, new, 1)
        changes.append({'function': name, 'old': old, 'new': new})
    return text, changes


def patch_arc_initializer(text):
    old = '\tarc_c_min = MAX(arc_c_max / 2, 2ULL << SPA_MAXBLOCKSHIFT);\n#endif'
    new = '\tarc_c_min = MAX(arc_c_max / 2, 2ULL << SPA_MAXBLOCKSHIFT);\n\t/* Native service headroom target, rounded down to whole pages. */\n\tarc_sys_free = (allmem / 4096 / 10) * 4096;\n#endif'
    if text.count(old) != 1:
        raise RuntimeError('ARC initializer resource context changed')
    return text.replace(old, new, 1), [{'old': old, 'new': new}]


def patch_kernel(text):
    changes = []
    replacement = (OWNED / 'kernel-functions.c').read_text()
    for name in ('cv_init', 'cv_deadline', 'cv_timedwait', 'cv_timedwait_hires', 'delay'):
        old, new = function(text, name), function(replacement, name)
        text = text.replace(old, new, 1)
        changes.append({'function': name, 'old': old, 'new': new})
    return text, changes


def patch_entropy(text):
    start = text.index('const char *random_path = "/dev/random";')
    end = text.index('\nint\nddi_strtoull(', start)
    old = text[start:end]
    if old.count('random_get_bytes_common') != 3 or old.count('open(') != 2:
        raise RuntimeError('OpenZFS entropy source context changed')
    owned = (OWNED / 'entropy-functions.c').read_text()
    new = owned[owned.index('/* Private libzpool replacement.'):].rstrip() + '\n'
    text = text[:start] + new + text[end:]
    include = '#include <poll.h>'
    if text.count(include) != 1:
        raise RuntimeError('OpenZFS entropy include context changed')
    text = text.replace(include, include + '\n#include <sys/auxv.h>')
    return text, [{'function': 'entropy lifecycle/fill', 'old': old, 'new': new},
                  {'old': include, 'new': include + '\n#include <sys/auxv.h>'}]


def patch_tpool(text):
    helper = '''static void
aether_tpool_cond_init(pthread_cond_t *cv)
{
\tpthread_condattr_t attr;
\tif (pthread_condattr_init(&attr) != 0 ||
\t    pthread_condattr_setclock(&attr, CLOCK_MONOTONIC) != 0 ||
\t    pthread_cond_init(cv, &attr) != 0 ||
\t    pthread_condattr_destroy(&attr) != 0)
\t\t_Exit(125);
}

'''
    old_wait = '''\t\t\t\tif (pthread_cond_timedwait(&tpool->tp_workcv,
\t\t\t\t    &tpool->tp_mutex, &ts) != 0) {
\t\t\t\t\telapsed = 1;
\t\t\t\t\tbreak;
\t\t\t\t}'''
    new_wait = '''\t\t\t\tint wait_error = pthread_cond_timedwait(&tpool->tp_workcv,
\t\t\t\t    &tpool->tp_mutex, &ts);
\t\t\t\tif (wait_error == ETIMEDOUT) {
\t\t\t\t\telapsed = 1;
\t\t\t\t\tbreak;
\t\t\t\t}
\t\t\t\tif (wait_error != 0)
\t\t\t\t\t_Exit(125);'''
    changes = [('static void *\ntpool_worker(', helper + 'static void *\ntpool_worker('),
               ('clock_gettime(CLOCK_REALTIME, &ts)', 'clock_gettime(CLOCK_MONOTONIC, &ts)'),
               ('\t(void) pthread_cond_init(&tpool->tp_workcv, NULL);', '\taether_tpool_cond_init(&tpool->tp_workcv);'),
               (old_wait, new_wait)]
    for old, new in changes:
        if text.count(old) != 1:
            raise RuntimeError('elapsed tpool context changed: ' + old)
        text = text.replace(old, new)
    return text, [{'old': old, 'new': new} for old, new in changes]


def route(arg):
    # Remap current preserved inputs only. Macro RHS is historical __FILE__ data.
    roots = ('openzfs-native-delay-2026-10-05', 'openzfs-native-wait-clocks-2026-10-05',
             'openzfs-native-time-callers-2026-10-05')
    if arg.startswith('-fmacro-prefix-map='):
        left, right = arg.removeprefix('-fmacro-prefix-map=').split('=', 1)
        return '-fmacro-prefix-map=' + route(left) + '=' + right
    for name in roots:
        old = str(ROOT / 'zig-out' / name)
        legacy = '/Users/cam/DEV/Aether/zig-out/' + name
        arg = re.sub(re.escape(legacy) + r'(?=/|$)', old, arg)
        if name.endswith('wait-clocks-2026-10-05'):
            arg = arg.replace(old + '/build-attempt-2', str(CURRENT / 'previous-build'))
        arg = arg.replace(old, str(CURRENT))
    return arg


def prepare(output, command, entropy=False, allocation=False, resources=False, arc=False, startup=False, volume=False, volume_workers=False, volume_spa_utc=False, volume_utc=False, volume_spa_active=False, utc_runtime=None, volume_spa_physical=False, volume_open_trace=False, volume_write=False, volume_pool=False, pool_diagnostics=False, diagnostic_cc=None, volume_pool_data=False, volume_pool_interrupt=False, volume_pool_uncommitted=False, volume_pool_recovery_check=None, volume_pool_namespace=False, volume_namespace_ipc=False, volume_pool_zpl_write=False, volume_pool_zpl_recover=False, volume_pool_zpl_repeat=False, volume_pool_zpl_stages=False, volume_pool_zpl_write_stages=False, volume_pool_zpl_txg_stages=False, volume_pool_zpl_sync_stages=False, volume_fs_bridge=None, volume_recovery_diagnostic=False, volume_recovery_writer_60s=False, volume_pool_zpl_zero=False, volume_namespace_mutation=None, volume_fs_service=None, volume_fs_service_case='normal', volume_fs_lifetimes=False, volume_fs_namespace=None, volume_fs_mixed=False, volume_fs_mixed_empty=False, namespace_wait=False, volume_fs_bulk=False, volume_fs_runtime=False, volume_fs_names=False, volume_fs_directories=False, volume_storage_lifetime=False):
    from openzfs_fs_runtime_service import validate_profile as runtime_profile
    runtime_profile(volume_fs_runtime, volume_fs_bulk, volume_fs_service)
    from openzfs_fs_directories_service import validate_profile as directories_profile
    directories_profile(volume_fs_directories,volume_fs_names,volume_pool_zpl_recover,volume_fs_service)
    from storage_lifetime import validate as storage_lifetime_profile
    storage_lifetime_profile(volume_storage_lifetime,volume_fs_directories,volume_pool_zpl_recover,volume_fs_service_case)
    from openzfs_fs_names_service import validate_profile as names_profile
    names_profile(volume_fs_names, isinstance(volume_fs_service,dict) and volume_fs_service.get('activation',False),volume_fs_runtime,volume_pool_zpl_recover,volume_fs_service)
    from openzfs_fs_bulk_service import validate_profile as bulk_profile
    bulk_profile(volume_fs_bulk, volume_fs_mixed, namespace_wait, volume_pool_zpl_write, volume_pool_zpl_recover, volume_fs_service)
    from storage_channel_wait import validate as validate_wait
    validate_wait(namespace_wait,volume_namespace_ipc,volume_pool_namespace,volume_pool_zpl_write,volume_pool_zpl_recover,volume_fs_service,volume_namespace_mutation,volume_fs_mixed)
    from openzfs_fs_service import case_number
    service_case = case_number(volume_fs_service_case)
    from openzfs_fs_namespace import validate_profile as namespace_profile
    namespace_profile(volume_fs_namespace, volume_namespace_mutation, volume_pool_zpl_write, volume_pool_zpl_recover,
                      volume_fs_service, volume_fs_lifetimes, volume_fs_service_case)
    from openzfs_fs_mixed_service import validate_profile as mixed_profile
    mixed_profile(volume_fs_mixed,volume_pool_zpl_write,volume_pool_zpl_recover,volume_fs_service,
                  volume_fs_lifetimes,volume_fs_namespace,volume_fs_mixed_empty,volume_fs_service_case)
    if volume_fs_mixed and not (volume_pool_namespace and volume_pool and pool_diagnostics and
            (volume_pool_zpl_write or (volume_pool_zpl_recover and volume_recovery_diagnostic and volume_recovery_writer_60s))):
        raise ValueError('mixed service requires fixed-budget namespace preparation')
    if not isinstance(volume_fs_lifetimes, bool) or (volume_fs_lifetimes and not (
            (volume_pool_zpl_write and volume_fs_service is not None) or
            (volume_pool_zpl_recover and volume_recovery_writer_60s and volume_recovery_diagnostic))):
        raise ValueError('filesystem service lifetimes require exact writer/recovery profile')
    if volume_fs_service is not None and volume_fs_service.get('lifetimes', False) is not volume_fs_lifetimes:
        raise ValueError('filesystem service lifetime delivery/profile mismatch')
    if service_case and volume_fs_service is None:
        raise ValueError('filesystem service case requires its exact selection')
    if volume_fs_service is not None:
        if not (volume_pool_zpl_write and volume_namespace_ipc and volume_pool_namespace and volume_pool and pool_diagnostics) or any((
                volume_fs_bridge is not None, volume_pool_zpl_recover, volume_pool_zpl_repeat,
                volume_pool_zpl_stages, (volume_namespace_mutation is not None and volume_fs_namespace is None), volume_pool_zpl_zero)):
            raise ValueError('filesystem service requires exclusive writable IPC preparation')
    from openzfs_mutation import validate as validate_mutation
    validate_mutation(volume_namespace_mutation)
    if volume_namespace_mutation is not None and (not (volume_pool_namespace and volume_pool and pool_diagnostics and (volume_pool_zpl_write != volume_pool_zpl_recover)) or
            volume_fs_bridge is not None or volume_pool_zpl_zero or (volume_namespace_ipc and volume_fs_namespace is None) or volume_pool_zpl_stages or
            volume_pool_zpl_repeat is not (volume_namespace_mutation in ('repeat', 'eight', 'lifetimes') and volume_pool_zpl_write) or
            (volume_pool_zpl_recover and not (volume_recovery_diagnostic and volume_recovery_writer_60s))):
        raise ValueError('namespace mutation requires exclusive namespace profile')
    if not isinstance(volume_pool_zpl_zero, bool):
        raise ValueError('truncate zero selector must be boolean')
    if volume_pool_zpl_zero and (not (volume_pool_namespace and volume_pool and pool_diagnostics and (volume_pool_zpl_write != volume_pool_zpl_recover)) or
            volume_fs_bridge is not None or volume_namespace_ipc or volume_pool_zpl_repeat or volume_pool_zpl_stages or
            (volume_pool_zpl_recover and not (volume_recovery_writer_60s and volume_recovery_diagnostic))):
        raise ValueError('truncate zero requires exclusive namespace profiles')
    if not isinstance(volume_recovery_writer_60s, bool):
        raise ValueError('recovery writer window selector must be boolean')
    if volume_recovery_writer_60s and (not (volume_pool_zpl_recover and volume_pool_namespace and volume_pool and pool_diagnostics) or
            volume_pool_zpl_write or volume_namespace_ipc or volume_fs_bridge is not None):
        raise ValueError('recovery writer window requires isolated readonly namespace build')
    if volume_recovery_diagnostic and (not (volume_pool_zpl_recover and volume_pool_namespace and volume_pool and pool_diagnostics) or
            volume_pool_zpl_write or volume_namespace_ipc or volume_fs_bridge is not None):
        raise ValueError('recovery diagnostic requires isolated readonly namespace build')
    if volume_fs_bridge is not None and (not (volume_pool_zpl_write and volume_pool_namespace and volume_pool and pool_diagnostics) or
            any((volume_namespace_ipc, volume_pool_zpl_repeat, volume_pool_zpl_stages, volume_pool_zpl_recover))):
        raise ValueError('filesystem bridge requires exclusive single-write namespace build')
    if volume_pool_zpl_sync_stages and not volume_pool_zpl_txg_stages:
        raise ValueError("sync stages require worker profile")
    if volume_pool_zpl_txg_stages and (not volume_pool_zpl_stages or volume_pool_zpl_write_stages):
        raise ValueError('TXG worker diagnostic requires exclusive stage profile')
    if volume_pool_zpl_write_stages and not volume_pool_zpl_stages:
        raise ValueError('first-write diagnostic requires stage profile')
    if volume_pool_zpl_stages and not volume_pool_zpl_repeat:
        raise ValueError('stage diagnostic requires repeated writer preparation')
    if volume_pool_zpl_repeat and not volume_pool_zpl_write:
        raise ValueError('repeated ZPL requires isolated writer preparation')
    if volume_pool_zpl_recover and (not volume_pool_namespace or volume_namespace_ipc or volume_pool_zpl_write):
        raise ValueError('ZPL recovery requires isolated namespace preparation')
    if volume_pool_zpl_write and (not volume_pool_namespace or (volume_namespace_ipc and volume_fs_service is None)):
        raise ValueError('ZPL writer requires isolated namespace preparation')
    if volume_namespace_ipc and not volume_pool_namespace:
        raise ValueError('namespace IPC requires namespace profile')
    if volume_pool_namespace and (not (volume_pool and pool_diagnostics) or volume_pool_data or volume_pool_interrupt or volume_pool_recovery_check):
        raise ValueError('namespace requires exclusive diagnostic pool import')
    if volume_pool_recovery_check is not None and (volume_pool_recovery_check not in ('capacity', 'uberblock-checksum') or
            not (volume_pool and volume_pool_data and pool_diagnostics) or volume_pool_interrupt):
        raise ValueError('pool recovery check requires exclusive diagnostic data')
    if volume_pool_uncommitted and not volume_pool_interrupt:
        raise ValueError("uncommitted pool requires interrupted data")
    if volume_pool_interrupt and not (volume_pool and volume_pool_data and pool_diagnostics):
        raise ValueError('pool interruption requires diagnostic assigned data')
    if volume_pool_data and not volume_pool:
        raise ValueError('pool data requires pool selection')
    if pool_diagnostics and not volume_pool:
        raise ValueError('pool diagnostics require pool creation selection')
    if volume_pool and (not (volume and volume_utc) or
                        any((volume_workers, volume_spa_utc, volume_spa_active,
                             volume_spa_physical, volume_open_trace, volume_write))):
        raise ValueError('pool creation requires exclusive shared UTC volume selection')
    if volume_open_trace and not (volume and volume_spa_physical):
        raise ValueError("open tracing requires the physical volume recipe")
    if volume_write and (not (volume and volume_spa_physical) or volume_open_trace):
        raise ValueError("write witness requires an exclusive physical volume")
    if bool(pool_diagnostics) != bool(diagnostic_cc):
        raise ValueError('pool diagnostic compiler must match selected runtime')
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    manifest = json.loads((CURRENT / 'current-inputs.json').read_text())
    if any(sha(CURRENT / p) != h for p, h in manifest['files'].items()):
        raise RuntimeError('current OpenZFS input drift')
    if any(sha(CURRENT / p) != h for p, h in PINS.items()):
        raise RuntimeError('selected elapsed source drift')
    output.mkdir()
    latest = json.loads((CURRENT / 'build-attempt-1/results.json').read_text())
    previous = json.loads((CURRENT / 'previous-build/results.json').read_text())
    for receipt in (latest, previous):
        if receipt['status'] != 'pass' or any(sha(Path(p)) != h for p, h in receipt['tools'].items()):
            raise RuntimeError('selected build/tool receipt drift')
    record = {'status': 'incomplete', 'engine_entry_executed': False,
              'input_manifest_sha256': sha(CURRENT / 'current-inputs.json'),
              'input_count': len(manifest['files']), 'functions': {}, 'objects': {},
              'physical_open_trace': volume_open_trace, 'physical_write': volume_write}
    resource_dir = output / 'resources'
    if resources:
        (resource_dir / 'sys').mkdir(parents=True)
        (resource_dir / 'resources.h').write_bytes((OWNED / 'resources.h').read_bytes())
        (resource_dir / 'sys/zfs_context.h').write_text(
            '/* SPDX-License-Identifier: BSD-2-Clause */\n'
            '#include_next <sys/zfs_context.h>\n#include <resources.h>\n'
            '#undef boot_ncpus\n#define boot_ncpus (aether_zfs_assigned_cpus())\n')
    if pool_diagnostics:
        from openzfs_failure import instrument
        record['failure_catalogue'] = []
    alloc_dir = output / 'allocation'
    if allocation:
        alloc_dir.mkdir()
        if pool_diagnostics:
            (alloc_dir / 'sys').mkdir()
            original_time = CURRENT / 'build-attempt-5/guarded-include/sys/time.h'
            changed_time, sites = instrument(original_time.read_text(), 'time')
            # The copied header is earlier in the search path. Preserve the
            # original include_next destination, not the original wrapper itself.
            if changed_time.count('#include_next <sys/time.h>') != 1:
                raise RuntimeError('diagnostic time include context changed')
            changed_time = changed_time.replace('#include_next <sys/time.h>',
                '#include "' + str(CURRENT / 'sdk/stage/usr/include/sys/time.h') + '"', 1)
            (alloc_dir / 'sys/time.h').write_text(changed_time)
            record['failure_catalogue'] += sites
            record['diagnostic_time_header'] = {'original_sha256': sha(original_time),
                                               'selected_sha256': sha(alloc_dir / 'sys/time.h')}
        header = CURRENT / 'build-attempt-5/guarded-include/umem.h'
        changed, edits = patch_alloc_header(header.read_text())
        if pool_diagnostics:
            changed, sites = instrument(changed, 'allocation')
            record['failure_catalogue'] += sites
        (alloc_dir / 'umem.h').write_text(changed)
        record['allocation_header'] = {'original_sha256': sha(header), 'selected_sha256': sha(alloc_dir / 'umem.h'),
                                       'functions': edits}
    def cmd(receipt, name):
        return [route(a) for a in next(c['argv'] for c in receipt['commands'] if c['name'] == name)]
    base_cmd, support_cmd = cmd(latest, 'selected-libzpool'), cmd(latest, 'selected-engine')
    base = base_cmd[2:base_cmd.index('-o')]
    support = support_cmd[2:support_cmd.index('-o')]
    if len(base) != 177 or len(support) != 113:
        raise RuntimeError('changed ordered engine closure')
    link = cmd(latest, 'selected-startup')
    link = link[:link.index('-o')]
    tool = base_cmd[0]
    original_support = support.copy()
    try:
        command([tool, '-r', *base, '-o', output / 'baseline-libzpool.o'], output / 'baseline-libzpool.log')
        if sha(output / 'baseline-libzpool.o') != sha(CURRENT / 'build-attempt-1/selected-libzpool.o'):
            raise RuntimeError('baseline libzpool bytes changed')
        support[0] = str(output / 'baseline-libzpool.o')
        command([tool, '-r', *support, '-o', output / 'baseline-engine.o'], output / 'baseline-engine.log')
        if sha(output / 'baseline-engine.o') != sha(CURRENT / 'build-attempt-1/selected-engine.o'):
            raise RuntimeError('baseline engine bytes changed')
        baseline_link = [str(output / 'baseline-engine.o') if a == str(CURRENT / 'build-attempt-1/selected-engine.o') else a for a in link]
        command(baseline_link + ['-o', output / 'baseline.elf'], output / 'baseline-link.log')
        if sha(output / 'baseline.elf') != manifest['selected_elf_sha256']:
            raise RuntimeError('baseline ELF bytes changed')
        for name, receipt, path, index, patcher in (
                ('kernel.c', latest, 'build-attempt-1/source/kernel.c', 145, patch_kernel),
                ('thread_pool.c', previous, 'previous-build/source/thread_pool.c', 187, patch_tpool)):
            original = CURRENT / path
            source = output / name
            changed, edits = patcher(original.read_text())
            if entropy and name == 'kernel.c':
                changed, entropy_edits = patch_entropy(changed)
                edits += entropy_edits
            if allocation and name == 'kernel.c':
                changed, allocation_edits = patch_alloc_kernel(changed)
                edits += allocation_edits
            if resources and name == 'kernel.c':
                changed, resource_edits = patch_resources(changed)
                edits += resource_edits
            if startup and name == 'kernel.c':
                changed, startup_edits = patch_startup(changed)
                edits += startup_edits
            if volume and name == 'kernel.c':
                from openzfs_volume import patch_kernel as patch_volume
                changed, volume_edits = patch_volume(changed, physical=volume_spa_physical, open_trace=volume_open_trace, write=volume_write)
                edits += volume_edits
            if pool_diagnostics:
                changed, sites = instrument(changed, 'kernel' if name == 'kernel.c' else 'tpool')
                record['failure_catalogue'] += sites
            source.write_text(changed)
            record['functions'][name] = edits
            recipe = cmd(receipt, name + '-selected')
            prefix = recipe[:recipe.index('-c')]
            target = next(r['historical_macro_path'] for r in receipt['replacements'] if r['index'] == index)
            prefix += ['-fmacro-prefix-map=' + str(source) + '=' + target,
                       '-fmacro-prefix-map=' + str(original) + '=' + target]
            old = output / (name + '-original.o')
            command(prefix + ['-c', original, '-o', old], output / (name + '-original.log'))
            old_object = Path(recipe[recipe.index('-o') + 1])
            if sha(old) != sha(old_object):
                raise RuntimeError('original object bytes changed: ' + name)
            if allocation:
                prefix.insert(1, '-I' + str(alloc_dir))
            if resources:
                prefix.insert(1, '-I' + str(resource_dir))
            if startup:
                prefix.insert(1, '-I' + str(OWNED))
            if volume:
                prefix.insert(1, '-I' + str(ROOT / 'user/storage/openzfs-volume'))
            if pool_diagnostics:
                dependencies = output / (name + '-diagnostic-dependencies.log')
                command(prefix + ['-M', '-MT', 'object', source], dependencies)
                if (str(alloc_dir / 'sys/time.h') not in dependencies.read_text() or
                        str(CURRENT / 'build-attempt-5/guarded-include/sys/time.h') in dependencies.read_text()):
                    raise RuntimeError('diagnostic time header not selected: ' + name)
                record.setdefault('diagnostic_time_dependencies', {})[name] = sha(dependencies)
                dependencies.unlink()
            selected = output / (name + '-selected.o')
            command(prefix + ['-c', source, '-o', selected], output / (name + '-selected.log'))
            record['objects'][name] = {'source_sha256': sha(source), 'original_sha256': sha(old), 'selected_sha256': sha(selected), 'index': index}
            if index < 177:
                if base[index] != str(old_object): raise RuntimeError('wrong kernel replacement slot')
                base[index] = str(selected)
            else:
                if support[index - 177 + 1] != str(old_object): raise RuntimeError('wrong tpool replacement slot')
                support[index - 177 + 1] = str(selected)
            test_source = source
            if name == 'thread_pool.c':
                # Probe the exact deadline/initializer blocks, not tpool lifecycle.
                start = changed.index('\t\t\t\tstruct timespec ts;')
                end = changed.index('\n\n\t\t\t\tint wait_error', start)
                fragment = changed[start:end]
                appended = '\nvoid aether_tpool_init_probe(pthread_cond_t *cv) { aether_tpool_cond_init(cv); }\n'
                appended += 'struct timespec aether_tpool_deadline_probe(unsigned linger) { tpool_t pool = {.tp_linger=linger}; tpool_t *tpool=&pool;\n' + fragment + '\nreturn ts; }\n'
                test_source = output / 'thread_pool-probe.c'
                test_source.write_text(changed + appended)
            for tag, src in [('native', test_source), ('old-native', original)]:
                if tag == 'old-native' and name != 'kernel.c': continue
                if entropy and tag == 'old-native':
                    src = output / 'kernel-entropy-old-clock.c'
                    original_clock = patch_entropy(original.read_text())[0]
                    if allocation:
                        original_clock = patch_alloc_kernel(original_clock)[0]
                    if resources:
                        original_clock = patch_resources(original_clock)[0]
                    if startup:
                        original_clock = patch_startup(original_clock)[0]
                    src.write_text(original_clock)
                command(prefix + ['-fmacro-prefix-map=' + str(src) + '=' + target, '-ffunction-sections', '-fdata-sections', '-c', src, '-o', output / (name + '-' + tag + '.o')], output / (name + '-' + tag + '.log'))
                record['objects'][name][tag] = {'source_sha256': sha(src), 'object_sha256': sha(output / (name + '-' + tag + '.o'))}
        if allocation:
            from openzfs_alloc import rebuild
            record['allocation_consumers'] = rebuild(output, base, support, command, resources, arc, pool_diagnostics)
        if volume:
            from openzfs_volume import build
            record['volume'] = build(output, base, command, workers=volume_workers, spa_utc=volume_spa_utc, utc=volume_utc, spa_active=volume_spa_active, utc_runtime=utc_runtime, spa_physical=volume_spa_physical, write=volume_write, pool=volume_pool, diagnostics=pool_diagnostics, pool_data=volume_pool_data, pool_interrupt=volume_pool_interrupt, pool_uncommitted=volume_pool_uncommitted, pool_recovery_check=volume_pool_recovery_check, pool_namespace=volume_pool_namespace, namespace_ipc=volume_namespace_ipc, pool_zpl_write=volume_pool_zpl_write, pool_zpl_recover=volume_pool_zpl_recover, pool_zpl_repeat=volume_pool_zpl_repeat, pool_zpl_stages=volume_pool_zpl_stages, pool_zpl_write_stages=volume_pool_zpl_write_stages, pool_zpl_txg_stages=volume_pool_zpl_txg_stages, pool_zpl_sync_stages=volume_pool_zpl_sync_stages, pool_fs_bridge=volume_fs_bridge, pool_recovery_diagnostic=volume_recovery_diagnostic, pool_recovery_writer_60s=volume_recovery_writer_60s, pool_zpl_zero=volume_pool_zpl_zero, pool_namespace_mutation=volume_namespace_mutation, pool_fs_service=volume_fs_service, pool_fs_service_case=volume_fs_service_case, pool_fs_lifetimes=volume_fs_lifetimes, pool_fs_namespace=volume_fs_namespace, pool_fs_mixed=volume_fs_mixed, pool_fs_mixed_empty=volume_fs_mixed_empty, namespace_wait=namespace_wait, pool_fs_bulk=volume_fs_bulk,pool_fs_runtime=volume_fs_runtime,pool_fs_names=volume_fs_names,pool_fs_directories=volume_fs_directories,pool_storage_lifetime=volume_storage_lifetime)
        if resources:
            recipe = cmd(latest, 'kernel.c-selected')
            prefix = recipe[:recipe.index('-c')]
            resource_object = resource_dir / 'resources.o'
            resource_source = OWNED / 'resources.c'
            if pool_diagnostics:
                text, sites = instrument(resource_source.read_text(), 'resources')
                record['failure_catalogue'] += sites
                resource_source = resource_dir / 'resources.c'
                resource_source.write_text(text)
            command(prefix + ['-Wall', '-Wextra', '-Werror', '-c', resource_source, '-o', resource_object], resource_dir / 'resources.log')
            record['resource_object_sha256'] = sha(resource_object)
            support.append(str(resource_object))
        if startup:
            recipe = cmd(latest, 'kernel.c-selected')
            prefix = recipe[:recipe.index('-c')] + ['-I' + str(OWNED)]
            startup_object = output / 'startup-provider.o'
            startup_source = OWNED / 'startup.c'
            if pool_diagnostics:
                text, sites = instrument(startup_source.read_text(), 'startup')
                record['failure_catalogue'] += sites
                startup_source = output / 'startup-provider.c'
                startup_source.write_text(text)
            command(prefix + ['-Wall', '-Wextra', '-Werror', '-c', startup_source, '-o', startup_object], output / 'startup-provider.log')
            record['startup_object_sha256'] = sha(startup_object)
            support.append(str(startup_object))
        if pool_diagnostics:
            failure_object = output / 'pool-failure.o'
            command(diagnostic_cc + ['-c', ROOT / 'user/storage/openzfs-volume/pool-failure.c', '-o', failure_object], output / 'pool-failure.log')
            support.append(str(failure_object))
            record['failure_object_sha256'] = sha(failure_object)
        command([tool, '-r', *(['--wrap=aether_zpl_close'] if service_case == 3 else []), *(['-Map=' + str(output / 'bridge-partial.map')] if volume_fs_bridge is not None or volume_fs_service is not None else []),
                 *base, '-o', output / 'selected-libzpool.o'], output / 'selected-libzpool.log')
        if volume_fs_bridge is not None:
            from openzfs_fs_bridge import partial_origins, recheck
            record['fs_bridge_origins'] = partial_origins((output / 'bridge-partial.map').read_text())
            recheck(volume_fs_bridge)
        if volume_fs_service is not None:
            from openzfs_fs_service import partial_origins as service_origins, recheck as service_recheck
            close_symbols = None
            if service_case == 3:
                nm = Path(cmd(latest, 'kernel.c-selected')[0]).parent / 'llvm-nm'
                command([nm, '--print-size', '--defined-only', output / 'selected-libzpool.o'], output / 'service-partial-symbols.log')
                close_symbols = (output / 'service-partial-symbols.log').read_text()
                record['fs_service_partial_symbols_sha256'] = sha(output / 'service-partial-symbols.log')
            if volume_fs_mixed:
                from openzfs_fs_mixed_service import partial_origins as mixed_origins
                record['fs_service_origins']=mixed_origins((output/'bridge-partial.map').read_text(),close_symbols,service_case==3,namespace_wait,volume_fs_bulk,volume_fs_runtime,volume_fs_service.get('activation',False),volume_fs_service.get('names',False),volume_fs_service.get('directories',False))
            elif volume_fs_namespace is not None:
                from openzfs_fs_namespace import partial_origins as namespace_origins
                record['fs_service_origins']=namespace_origins((output/'bridge-partial.map').read_text(),close_symbols,service_case==3)
            else:
                record['fs_service_origins'] = service_origins((output / 'bridge-partial.map').read_text(), volume_fs_service_case, close_symbols, volume_fs_lifetimes)
            service_recheck(volume_fs_service)
        support[0] = str(output / 'selected-libzpool.o')
        command([tool, '-r', *support, '-o', output / 'selected-engine.o'], output / 'selected-engine.log')
        selected_link = [str(output / 'selected-engine.o') if a == str(CURRENT / 'build-attempt-1/selected-engine.o') else a for a in link]
        if volume:
            selected_link += [str(output / 'libaether_volume.a')]
        if startup:
            # This intermediate legacy-startup link is geometry only. The
            # maintained runner replaces its entry point before any engine use.
            record['legacy_startup_unbound'] = True
        command(selected_link + ['-o', output / 'selected.elf'], output / 'selected-link.log')
        # Use the compiler's pinned LLVM tools directory, not a PATH substitute.
        nm = Path(cmd(latest, 'kernel.c-selected')[0]).parent / 'llvm-nm'
        command([nm, '--undefined-only', output / 'selected.elf'], output / 'selected-imports.log')
        imports = (output / 'selected-imports.log').read_text()
        check_intermediate_imports(imports, physical=volume_spa_physical, worker_stages=volume_pool_zpl_txg_stages)
        command([nm, output / 'selected.elf'], output / 'selected-symbols.log')
        symbols = (output / 'selected-symbols.log').read_text()
        if any(s not in symbols for s in (' cv_init', ' cv_timedwait_hires', ' delay', ' tpool_worker')) or 'aether_tpool_' in symbols or 'aether_bad_auxv' in symbols:
            raise RuntimeError('missing actual callers or leaked test observer')
        if entropy:
            # Only the native error control changes the authority getter.
            recipe = cmd(latest, 'kernel.c-selected')
            prefix = recipe[:recipe.index('-c')]
            if allocation:
                prefix.insert(1, '-I' + str(alloc_dir))
            if resources:
                prefix.insert(1, '-I' + str(resource_dir))
            if startup:
                prefix.insert(1, '-I' + str(OWNED))
            if volume:
                prefix.insert(1, '-I' + str(ROOT / 'user/storage/openzfs-volume'))
            source = output / 'kernel.c'
            command(prefix + ['-ffunction-sections', '-fdata-sections', '-Dgetauxval=aether_bad_auxv', '-c', source,
                              '-o', output / 'kernel.c-future-native.o'], output / 'kernel.c-future-native.log')
            record['entropy_future_control_sha256'] = sha(output / 'kernel.c-future-native.o')
        record.update(status='pass', baseline_elf_sha256=sha(output / 'baseline.elf'),
                      selected_elf_sha256=sha(output / 'selected.elf'), selected_elf_bytes=(output / 'selected.elf').stat().st_size,
                      original_ordered_inputs=[sha(Path(p)) for p in base_cmd[2:base_cmd.index('-o')]] + [sha(Path(p)) for p in original_support])
    except BaseException as error:
        record.update(status='failed', error=str(error))
        raise
    finally:
        (output / 'port-results.json').write_text(json.dumps(record, indent=2) + '\n')
    return output


def declarations(entropy=False):
    """Copy actual types/prototypes into a private probe header, never an ABI."""
    source = (CURRENT / 'baseline/source/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1/include/sys/zfs_context.h').read_text()
    time = (CURRENT / 'build-attempt-5/guarded-include/sys/time.h').read_text()
    patterns = [r'typedef struct kmutex \{.*?\} kmutex_t;',
                r'typedef pthread_cond_t\s+kcondvar_t;',
                r'#define\s+CALLOUT_FLAG_ABSOLUTE\s+0x2',
                *[r'extern void ' + n + r'\([^;]+;' for n in ('cv_init', 'mutex_enter', 'mutex_exit', 'delay')],
                r'extern int cv_timedwait\([^;]+;', r'extern int cv_timedwait_hires\([^;]+;']
    pieces = []
    if entropy:
        patterns += [r'extern void random_init\(void\);', r'extern void random_fini\(void\);',
                     r'extern int random_get_bytes\([^;]+;', r'extern int random_get_pseudo_bytes\([^;]+;']
    for pattern in patterns:
        found = re.findall(pattern, source, re.DOTALL)
        if len(found) != 1:
            raise RuntimeError('OpenZFS declaration context changed: ' + pattern)
        pieces += found
    found = re.findall(r'typedef\s+long long\s+hrtime_t;', time)
    if len(found) != 1:
        raise RuntimeError('OpenZFS time declaration context changed')
    # Keep the upstream CDDL and attribution with copied definitions.
    notice = source[:source.index('#ifndef _SYS_ZFS_CONTEXT_H')]
    return notice + '\n' + found[0] + '\n' + '\n'.join(pieces) + '\n'


def adapt_runtime(source):
    """Select actual CV/mutex callers without changing the qualified base client."""
    changes = [
        ('static pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;',
         '#include "zfs-waits.inc"\n'
         'static kmutex_t zfs_mutex = {.m_lock = PTHREAD_MUTEX_INITIALIZER};\n'
         '#define mutex zfs_mutex.m_lock'),
        ('pthread_mutex_lock(&mutex)', 'zfs_lock(&zfs_mutex)'),
        ('pthread_mutex_unlock(&mutex)', 'zfs_unlock(&zfs_mutex)'),
        ('pthread_cond_init(&condition, &attr)', 'zfs_cond_init(&condition)'),
        ('pthread_cond_timedwait(&condition, &mutex, &deadline)',
         'zfs_wait(&condition, &zfs_mutex, &deadline)'),
    ]
    for old, new in changes:
        if source.count(old) != 1:
            raise RuntimeError('OpenZFS runtime witness context changed: ' + old)
        source = source.replace(old, new)
    return source, [{'old': a, 'new': b} for a, b in changes]


def adapt_fixture(source):
    changes = [
        ('static pthread_mutex_t timed_mutex = PTHREAD_MUTEX_INITIALIZER;',
         '#include "zfs-declarations.h"\n#include "zfs-bridge.inc"\n'
         'static kmutex_t zfs_mutex = {.m_lock = PTHREAD_MUTEX_INITIALIZER};\n'
         '#define timed_mutex zfs_mutex.m_lock'),
        ('!pthread_cond_init(&timed_condition, &attr)', '!zfs_cond_init(&timed_condition)'),
        ('pthread_cond_timedwait(&timed_condition, &timed_mutex, &timed_deadline)',
         'zfs_timedwait(&timed_condition, &zfs_mutex, &timed_deadline)'),
        ('    return 0;\n}\nstatic unsigned service_time_parked(',
         '    unsigned zfs_result = zfs_extra(i, &timed_condition, &zfs_mutex);\n'
         '    CHECK(!zfs_result, zfs_result);\n    return 0;\n}\nstatic unsigned service_time_parked(')]
    for old, new in changes:
        if source.count(old) != 1:
            raise RuntimeError('OpenZFS witness context changed: ' + old)
        source = source.replace(old, new)
    pattern = r'pthread_cond_timedwait\(&(timed_condition|utc), &timed_mutex,\s+&(bad|overflow|far)\)'
    source, count = re.subn(pattern, r'zfs_raw_wait(&\1, &zfs_mutex, &\2)', source)
    if count != 4:
        raise RuntimeError('OpenZFS raw error-wait context changed')
    changes.append((pattern, 'zfs_raw_wait (four raw POSIX counterexamples)'))
    # These are all uses of the one test mutex, not arbitrary upstream calls.
    for old, new in [('pthread_mutex_lock(&timed_mutex)', 'zfs_lock(&zfs_mutex)'),
                     ('pthread_mutex_unlock(&timed_mutex)', 'zfs_unlock(&zfs_mutex)')]:
        count = source.count(old)
        if count != 3:
            raise RuntimeError('OpenZFS witness mutex context changed: ' + old)
        source = source.replace(old, new)
        changes.append((old, new))
    return source, [{'old': a, 'new': b} for a, b in changes]


def adapt_exit(source):
    # The original join witness handles only successful thread exit. A selected
    # port failure terminates the owner via its existing native exit operation.
    old = '    if (n == SYS_exit && a == 0 && !b && !c && !d && !e && !f) {'
    new = ('    if (n == SYS_exit_group && a == 125 && !b && !c && !d && !e && !f) {\n'
           '        memtrap(0x10000 + SYS_exit_group, 125, 0, 0, 0);\n'
           '        __builtin_trap();\n    }\n' + old)
    if source.count(old) != 1:
        raise RuntimeError('OpenZFS fail-closed exit context changed')
    return source.replace(old, new), {'old': old, 'new': new}


def adapt_entropy_fixture(source):
    changes = [('#include "zfs-bridge.inc"', '#include "zfs-bridge.inc"\n#include "entropy-bridge.inc"'),
               ('    CHECK(timed_now() >= 0, 380);',
                '    CHECK(timed_now() >= 0, 380);\n    unsigned entropy_error = zfs_entropy_initialize();\n    CHECK(!entropy_error, entropy_error);'),
               ('    CHECK(!zfs_result, zfs_result);',
                '    CHECK(!zfs_result, zfs_result);\n    zfs_result = zfs_entropy_worker();\n    CHECK(!zfs_result, zfs_result);'),
               ('    CHECK(!pthread_cond_destroy(&timed_condition)',
                '    unsigned entropy_error = zfs_entropy_cleanup();\n    CHECK(!entropy_error, entropy_error);\n    CHECK(!pthread_cond_destroy(&timed_condition)')]
    for old, new in changes:
        if source.count(old) != 1:
            raise RuntimeError('OpenZFS entropy witness context changed: ' + old)
        source = source.replace(old, new)
    return source, [{'old': a, 'new': b} for a, b in changes]
