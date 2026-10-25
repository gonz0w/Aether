# SPDX-License-Identifier: BSD-2-Clause
"""Pinned accounting selection and resource-aware unlinked native preparation."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import test_openzfs_zpl_write as writer
import openzfs_namespace as namespace

ROOT, CURRENT, OWNED = writer.ROOT, writer.CURRENT, writer.OWNED
SOURCE = CURRENT / ('baseline/source/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1/'
                    'module/zfs/zfs_quota.c')


class ZplAccounting(unittest.TestCase):
    def test_original_callback_and_notices_preserved_without_quota_policy(self):
        original = SOURCE.read_text()
        selected = namespace.accounting_source(original)
        self.assertIn('CDDL HEADER START', selected)
        self.assertIn('Copyright (c) 2005, 2010, Oracle', selected)
        self.assertEqual(writer.elapsed.function(selected, 'zpl_get_file_info'),
                         writer.elapsed.function(original, 'zpl_get_file_info'))
        self.assertNotIn('fuidstr_to_sid', selected)

    def test_original_source_and_selection_drift_reject(self):
        original = SOURCE.read_text()
        for text in (original + '\n', original.replace('zpl_get_file_info', 'other', 1)):
            with self.assertRaisesRegex(ValueError, 'source hash mismatch'):
                namespace.accounting_source(text)
        changed = original.replace('\nstatic void\nfuidstr_to_sid', '\nstatic void\nchanged')
        with patch.object(namespace, 'ACCOUNTING_SOURCE_SHA256', hashlib.sha256(changed.encode()).hexdigest()):
            with self.assertRaisesRegex(ValueError, 'prefix context changed'):
                namespace.accounting_source(changed)
        with patch.object(namespace, 'ACCOUNTING_PREFIX_SHA256', '0' * 64):
            with self.assertRaisesRegex(ValueError, 'prefix hash mismatch'):
                namespace.accounting_source(original)

    def test_native_callback_initializer_and_ordered_writer_composition(self):
        with tempfile.TemporaryDirectory(prefix='aether-zpl-native-write-') as temp:
            output = Path(temp)
            headers = output / 'selected'
            writer.prepare_resource_headers(headers)
            recipe = next(c['argv'] for c in json.loads((CURRENT / 'build-attempt-5/results.json').read_text())['commands']
                          if c['name'] == 'input-176-checked')
            prefix = [writer.route(a) for a in recipe[:recipe.index('-c')]]
            prefix[1:1] = ['-I' + str(headers / 'resources'), '-I' + str(headers / 'allocation'), '-I' + str(OWNED)]
            llvm = Path(prefix[0]).parent
            tool_pins = json.loads((CURRENT / 'build-attempt-5/results.json').read_text())['tools']
            for tool in [llvm / 'clang', llvm / 'llvm-nm']:
                self.assertEqual(hashlib.sha256(tool.read_bytes()).hexdigest(), tool_pins[str(tool)])
            prefix += ['-isystem', str(llvm.parent / 'lib/clang/21/include'), '-std=gnu11',
                       '-Wall', '-Wextra', '-Werror', '-ffunction-sections', '-fdata-sections', '-fstack-usage']
            original = output / 'original-accounting.c'
            original.write_text(namespace.accounting_source(SOURCE.read_text()))
            pins = json.loads((CURRENT / 'current-inputs.json').read_text())['files']
            metadata = []
            objects, imported = [], []
            for name, source, extra in (
                ('callback', original, ['-Wno-error=sign-compare']),
                ('initializer', OWNED / 'zpl-accounting.c', []),
                ('ordered', OWNED / 'zpl-write.c', ['-DAETHER_ZPL_ORDERED_WRITE=1']),
            ):
                obj, dep = output / (name + '.o'), output / (name + '.d')
                argv = prefix + extra + ['-MD', '-MF', str(dep), '-c', str(source), '-o', str(obj)]
                result = subprocess.run(argv, capture_output=True, text=True, timeout=180)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                symbols = subprocess.check_output([str(llvm / 'llvm-nm'), '-u', str(obj)], text=True)
                imports = {line.split()[-1] for line in symbols.splitlines() if line.strip()}
                imported.append(imports)
                dependencies = {}
                for path_string in dep.read_text().split(':', 1)[1].replace('\\\n', ' ').split():
                    path = Path(path_string)
                    digest = hashlib.sha256(path.read_bytes()).hexdigest()
                    dependencies[str(path)] = digest
                    if path.is_relative_to(CURRENT):
                        self.assertEqual(pins[str(path.relative_to(CURRENT))], digest, str(path))
                stack = obj.with_suffix('.su').read_text()
                self.assertNotIn('dynamic', stack)
                metadata.append({'argv': argv, 'bytes': obj.stat().st_size,
                                 'object_sha256': hashlib.sha256(obj.read_bytes()).hexdigest(),
                                 'imports': sorted(imports), 'dependency_sha256': dependencies,
                                 'stack_usage': stack, 'compiler_stderr': result.stderr})
                objects.append(obj)
            print('ZPL ACCOUNTING NATIVE ' + json.dumps(metadata))
            self.assertEqual(imported[0], {'sa_hdrsize', '__set_error', '__stack_chk_fail'})
            self.assertEqual(imported[1], {'dmu_objset_register_type', 'zpl_get_file_info'})
            self.assertEqual(imported[2], {
                '__stack_chk_fail', 'aether_pool_hooks_bind_transaction', 'calloc', 'free',
                'dmu_object_info', 'dmu_objset_disown', 'dmu_objset_is_snapshot', 'dmu_objset_own',
                'dmu_objset_projectquota_upgradable', 'dmu_objset_spa', 'dmu_objset_userobjspace_upgradable',
                'dmu_objset_userspace_present', 'dmu_objset_userused_enabled', 'dmu_read', 'dmu_tx_abort',
                'dmu_tx_assign', 'dmu_tx_commit', 'dmu_tx_create', 'dmu_tx_get_txg', 'dmu_tx_hold_sa',
                'dmu_tx_hold_write', 'dmu_write', 'dsl_prop_get_integer', 'memcpy', 'memset',
                'sa_bulk_lookup', 'sa_bulk_update', 'sa_handle_destroy', 'sa_handle_get', 'sa_setup',
                'spa_get_dsl', 'spa_last_synced_txg', 'spa_writeable', 'txg_wait_synced_flags', 'zap_lookup',
                'zfs_attr_table', 'zfs_get_zplprop',
            })
            for record, limit in zip(metadata, [1024, 1024, 8192]):
                self.assertTrue(record['stack_usage'])
                self.assertTrue(all(int(line.split('\t')[1]) <= limit for line in record['stack_usage'].splitlines()))
            linked = output / 'prepared.o'
            linker = next(Path(path) for path in tool_pins if Path(path).name == 'ld.lld')
            self.assertEqual(hashlib.sha256(linker.read_bytes()).hexdigest(), tool_pins[str(linker)])
            argv = [str(linker), '-r', *map(str, objects), '-o', str(linked)]
            result = subprocess.run(argv, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            symbols = subprocess.check_output([str(llvm / 'llvm-nm'), '-u', str(linked)], text=True)
            remaining = {line.split()[-1] for line in symbols.splitlines() if line.strip()}
            self.assertEqual(remaining, set.union(*imported) - {'zpl_get_file_info'})
            defined = subprocess.check_output([str(llvm / 'llvm-nm'), '--defined-only', str(linked)], text=True)
            self.assertFalse(any(line.split()[-2] in {'B', 'b', 'D', 'd', 'C'}
                                 for line in defined.splitlines() if len(line.split()) >= 3), defined)
            print('ZPL ACCOUNTING LINK ' + json.dumps({'argv': argv, 'bytes': linked.stat().st_size,
                  'object_sha256': hashlib.sha256(linked.read_bytes()).hexdigest(), 'imports': sorted(remaining),
                  'tools': {str(tool): hashlib.sha256(tool.read_bytes()).hexdigest()
                            for tool in [llvm / 'clang', llvm / 'llvm-nm', linker]},
                  'scope': 'Relocatable objects only; not final engine, runtime initialization/drain, stack fit or ordered durability'}))


if __name__ == '__main__':
    unittest.main()
