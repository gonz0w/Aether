# SPDX-License-Identifier: BSD-2-Clause
"""Rebuild checked inline allocation-header consumers; no engine execution."""
import hashlib
import json
from pathlib import Path
from openzfs_elapsed import CURRENT, route, patch_arc_adapter, patch_arc_initializer


def rebuild(output, base, support, command, resources=False, arc=False, pool_diagnostics=False):
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    receipt = json.loads((CURRENT / 'build-attempt-5/results.json').read_text())
    if receipt['status'] != 'pass':
        raise RuntimeError('missing selected header consumer receipt')
    rows = receipt['objects']
    if len(rows) != 272 or len({r['index'] for r in rows}) != len(rows):
        raise RuntimeError('changed checked header consumer inventory')
    directory = output / 'allocation'
    header = directory / 'umem.h'
    results = []
    for row in rows:
        index = row['index']
        # Actual kernel.c has already been reconstructed and ported with the
        # current elapsed/entropy functions and removed dead callback.
        if index == 145:
            continue
        checked = next((c['argv'] for c in receipt['commands'] if c['name'] == f'input-{index}-checked'), None)
        recipe = checked or next(c['argv'] for c in receipt['commands'] if c['name'] == f'input-{index}-original')
        prefix = [route(a) for a in recipe[:recipe.index('-c')]]
        source = Path(route(recipe[recipe.index('-c') + 1]))
        selected = Path(base[index] if index < 177 else support[index - 177 + 1])
        expected_sha256 = row.get('checked_sha256', row['original_sha256'])
        if sha(selected) != expected_sha256:
            # Nonconsuming libtpool is the separate elapsed port at index187.
            if index == 187 and not any(Path(n).name == 'umem.h' for n in row['dependencies']):
                continue
            raise RuntimeError('wrong allocation consumer slot: ' + str(index))
        dependency_log = directory / f'input-{index}-dependencies.log'
        command(prefix + ['-M', '-MT', 'object', source], dependency_log)
        dependency_text = dependency_log.read_text()
        consumed = str(CURRENT / 'build-attempt-5/guarded-include/umem.h') in dependency_text
        time_consumer = pool_diagnostics and str(CURRENT / 'build-attempt-5/guarded-include/sys/time.h') in dependency_text
        resource_consumer = resources and '/include/sys/zfs_context.h' in dependency_text
        recorded = any(Path(n).name == 'umem.h' for n in row['dependencies'])
        if consumed != recorded:
            raise RuntimeError('allocation dependency inventory drift: ' + str(index))
        if pool_diagnostics and time_consumer != row['consumes_time_header']:
            raise RuntimeError('diagnostic time dependency inventory drift: ' + str(index))
        dependency_sha256 = sha(dependency_log)
        # These are generated header inventories, not retained test evidence.
        dependency_log.unlink()
        if not consumed and not resource_consumer and not time_consumer:
            results.append({'index': index, 'consumes_header': False, 'dependency_sha256': dependency_sha256})
            continue
        original = directory / f'input-{index}-original.o'
        command(prefix + ['-c', source, '-o', original], directory / f'input-{index}-original.log')
        if sha(original) != sha(selected) or sha(original) != expected_sha256:
            raise RuntimeError('allocation original bytes changed: ' + str(index))
        new_prefix = prefix.copy()
        new_prefix.insert(1, '-I' + str(directory))
        if resources:
            new_prefix.insert(1, '-I' + str(output / 'resources'))
        command(new_prefix + ['-M', '-MT', 'object', source], dependency_log)
        if consumed and (str(header) not in dependency_log.read_text() or str(CURRENT / 'build-attempt-5/guarded-include/umem.h') in dependency_log.read_text()):
            raise RuntimeError('allocation header not selected: ' + str(index))
        if time_consumer and (str(directory / 'sys/time.h') not in dependency_log.read_text() or
                              str(CURRENT / 'build-attempt-5/guarded-include/sys/time.h') in dependency_log.read_text()):
            raise RuntimeError('diagnostic time header not selected: ' + str(index))
        new_dependencies_sha256 = sha(dependency_log)
        if resource_consumer and str(output / 'resources/sys/zfs_context.h') not in dependency_log.read_text():
            raise RuntimeError('resource wrapper not selected: ' + str(index))
        dependency_log.unlink()
        selected_source = source
        if resources and index == 1:
            old = 'sysconf(_SC_NPROCESSORS_ONLN)'
            text = source.read_text()
            if text.count(old) != 1:
                raise RuntimeError('taskq CPU resource context changed')
            selected_source = output / 'resources/taskq.c'
            selected_source.write_text(text.replace(old, 'aether_zfs_assigned_cpus()', 1))
        sites = []
        if pool_diagnostics and index == 285:
            if source != CURRENT / 'engine/assert-native.c':
                raise RuntimeError('diagnostic assertion source slot changed')
            from openzfs_failure import instrument
            changed, sites = instrument(source.read_text(), 'assertion')
            selected_source = directory / 'assert-native.c'
            selected_source.write_text(changed)
        if arc and (index == 0 or source.name == 'arc.c'):
            patcher = patch_arc_adapter if index == 0 else patch_arc_initializer
            changed, edits = patcher(source.read_text())
            if pool_diagnostics and index == 0:
                from openzfs_failure import instrument
                changed, sites = instrument(changed, 'arc')
                edits.append({'failure_catalogue': sites})
            selected_source = output / 'resources' / source.name
            selected_source.write_text(changed)
            (output / 'resources' / (source.name + '.patch.json')).write_text(json.dumps(edits, indent=2) + '\n')
        if selected_source != source:
            macro_path = str(source)
            for arg in prefix:
                if arg.startswith('-fmacro-prefix-map='):
                    left, right = arg.removeprefix('-fmacro-prefix-map=').split('=', 1)
                    if str(source).startswith(left):
                        macro_path = right + str(source)[len(left):]
                        break
            new_prefix += ['-fmacro-prefix-map=' + str(selected_source) + '=' + macro_path]
        obj = directory / f'input-{index}-selected.o'
        command(new_prefix + ['-c', selected_source, '-o', obj], directory / f'input-{index}-selected.log')
        if index < 177:
            base[index] = str(obj)
        else:
            support[index - 177 + 1] = str(obj)
        results.append({'index': index, 'source': str(source.relative_to(CURRENT)), 'consumes_header': consumed, 'consumes_resource_wrapper': resource_consumer,
                        **({'consumes_diagnostic_time': time_consumer} if pool_diagnostics else {}),
                        'dependency_sha256': dependency_sha256, 'selected_dependencies_sha256': new_dependencies_sha256,
                        'original_sha256': sha(original), 'selected_sha256': sha(obj), 'selected_source_sha256': sha(selected_source),
                        'bytes_changed': sha(original) != sha(obj), **({'failure_catalogue': sites} if sites else {})})
    consumers = sum(r['consumes_header'] for r in results)
    if consumers != 197:
        raise RuntimeError('changed allocation header consumer count')
    if pool_diagnostics and sum(r.get('consumes_diagnostic_time', False) for r in results) != 232:
        raise RuntimeError('changed diagnostic time consumer count')
    return {'kernel_separately_rebuilt': 145, 'other_consumers_rebuilt': consumers,
            'resource_consumers_rebuilt': sum(r.get('consumes_resource_wrapper', False) for r in results),
            **({'diagnostic_time_consumers_rebuilt': 232, 'time_kernel_tpool_separately_rebuilt': [145, 187]} if pool_diagnostics else {}),
            'objects_changed': sum(r.get('bytes_changed', False) for r in results), 'objects': results}
