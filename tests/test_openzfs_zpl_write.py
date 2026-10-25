#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Unselected original-API write helper under faulting doubles/native headers."""
import hashlib
import ast
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
OWNED = ROOT / 'user/storage/openzfs-volume'
sys.path.insert(0, str(ROOT / 'scripts'))
from openzfs_elapsed import CURRENT, route
import openzfs_elapsed as elapsed


def prepare_resource_headers(output):
    tree = ast.parse(Path(elapsed.__file__).read_text())
    prepare = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'prepare')
    body, started = [], False
    for node in prepare.body:
        if isinstance(node, ast.Assign) and ast.unparse(node.targets[0]) == 'resource_dir':
            started = True
        if started:
            if isinstance(node, ast.FunctionDef) and node.name == 'cmd':
                break
            body.append(node)
    if not body:
        raise RuntimeError("missing native header preparation block")
    output.mkdir()
    record = {}
    scope = dict(output=output, resources=True, allocation=True, pool_diagnostics=True,
                 OWNED=elapsed.OWNED, CURRENT=CURRENT, record=record,
                 patch_alloc_header=elapsed.patch_alloc_header,
                 sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest())
    exec(compile(ast.Module(body=body, type_ignores=[]), '<actual native header preparation>', 'exec'), scope)
    return record


class ZplWriter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-zpl-write-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.out = Path(cls.temp.name)
        cls.clang = Path('/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang')
        cls.sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        common = (ROOT / 'tests/fixtures/openzfs_zpl_read.c').read_text().split('#include "zpl-adapter.inc"', 1)[0]
        for old, new in (
            ('ro == B_TRUE &&', 'ro == (own_attempts ? B_FALSE : B_TRUE) &&'),
            ('*out = &dataset;', '++own_attempts; if (!ro) ++writable_owns; *out = &dataset;'),
            ('++allocated;', '++allocated; ++allocations;'),
            ('--allocated;', '--allocated; ++frees;'),
            ('int error = fail();\n    if (!error) {\n        owned = 1;',
             'int error = snapshot && !ro ? EROFS : fail();\n    if (!error) {\n        owned = 1;'),
            ('CHECK(p == &handle && handles == 1);',
             'CHECK(p == &handle && handles == 1 && !tx_live);'),
            ('static int sa_bulk_lookup(', 'static int reader_sa_bulk_lookup('),
            ('HOST ZPL oracle92', 'HOST ZPL WRITE oracle93'),
            ('exit(92);', 'exit(93);'),
        ):
            if common.count(old) != 1:
                raise RuntimeError('write common fixture context changed: ' + old)
            common = common.replace(old, new, 1)
        (cls.out / 'zpl-test-common.inc').write_text(common)
        cls.read_body = '\n'.join(line for line in (OWNED / 'zpl-read.c').read_text().splitlines()
                                  if not line.startswith('#include')) + '\n'
        cls.write_body = '\n'.join(line for line in (OWNED / 'zpl-write.c').read_text().splitlines()
                                   if not line.startswith('#include') and not line.startswith('#define AETHER_ZPL_WRITE_PROVIDER')) + '\n'
        cls.binary = cls.compile(cls.write_body, 'writer')

    @classmethod
    def compile(cls, body, name, ordered=False):
        (cls.out / 'zpl-adapter.inc').write_text('#define AETHER_ZPL_WRITE_PROVIDER 1\n' + cls.read_body + body)
        binary = cls.out / name
        argv = [str(cls.clang), '-isysroot', cls.sdk, '-std=gnu11', '-O2', '-Wall', '-Wextra', '-Werror',
                *(['-DAETHER_ZPL_ORDERED_WRITE=1'] if ordered else []),
                '-I' + str(cls.out), '-I' + str(OWNED), str(ROOT / 'tests/fixtures/openzfs_zpl_write.c'),
                '-o', str(binary)]
        result = subprocess.run(argv, capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        print('ZPL WRITE compiled:', name, binary.stat().st_size, hashlib.sha256(binary.read_bytes()).hexdigest())
        return binary

    def modes(self, modes):
        for mode in modes:
            with self.subTest(mode=mode):
                result = subprocess.run([str(self.binary), str(mode)], capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_overwrite_append_extension_zero_maximum_and_preassignment_snapshot(self):
        self.modes([0, 1, 2, 3, 4, 66])

    def test_bounds_time_type_flags_generation_and_readonly_reject_before_effects(self):
        self.modes(range(10, 35))

    def test_every_write_preflight_api_failure_balances_sa_and_has_no_tx(self):
        self.modes(range(50, 55))

    def test_assignment_abort_and_all_committed_error_progress_are_truthful(self):
        self.modes(range(60, 66))

    def test_writable_factory_property_snapshot_and_all_api_failures(self):
        self.modes([*range(100, 113), *range(120, 147)])

    def test_compiling_omissions_fail_semantic_write_oracles(self):
        for name, old, new, mode in (
            ('stale', 'node.generation != generation', '((void)generation, 0)', 17),
            ('flags', 'flags & (ZFS_IMMUTABLE | ZFS_APPENDONLY | ZFS_READONLY | ZFS_XATTR)', '0', 21),
            ('readonly', 'if (!error && readonly)', 'if (0 && !error && readonly)', 101),
            ('snapshot-open', 'if (!error && dmu_objset_is_snapshot(view->os))',
             'if (0 && !error && dmu_objset_is_snapshot(view->os))', 103),
            ('accounting-upgrade', 'dmu_objset_userobjspace_upgradable(view->os) ||',
             '(0 && dmu_objset_userobjspace_upgradable(view->os)) ||', 109),
            ('accounting-disabled', '!dmu_objset_userused_enabled(view->os) ||',
             '(0 && !dmu_objset_userused_enabled(view->os)) ||', 112),
            ('snapshot', 'length, staged, tx,', 'length, buffer, tx,', 66),
            ('sa-hold', 'dmu_tx_hold_sa(tx, handle, B_FALSE);', 'if (0) dmu_tx_hold_sa(tx, handle, B_FALSE);', 0),
            ('assigned-abort', 'dmu_tx_commit(tx);', 'if (0) dmu_tx_commit(tx); dmu_tx_abort(tx);', 63),
            ('progress', 'out->state = AETHER_ZPL_COMMITTED;',
             'out->state = AETHER_ZPL_COMMITTED; if (error) memset(out, 0, sizeof(*out));', 63),
            ('early-wait', 'if (!error && spa_last_synced_txg(spa) < out->txg)',
             'if (0 && !error && spa_last_synced_txg(spa) < out->txg)', 65),
            ('early-success', 'out->state = AETHER_ZPL_COMMITTED;', 'out->state = AETHER_ZPL_SYNCED;', 64),
        ):
            with self.subTest(omission=name):
                self.assertEqual(self.write_body.count(old), 1)
                binary = self.compile(self.write_body.replace(old, new, 1), name)
                result = subprocess.run([str(binary), str(mode)], capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 93, result.stdout + result.stderr)
                self.assertIn('HOST ZPL WRITE oracle93', result.stderr)
                print('ZPL WRITE compiling omission rejected:', name, mode, result.stderr.strip())

    def test_ordered_variant_all_old_cases_and_bind_failure_progress(self):
        binary = self.compile(self.write_body, 'ordered-writer', ordered=True)
        modes = [0, 1, 2, 3, 4, 66, *range(10, 35), *range(50, 55),
                 *range(60, 66), 68, 69, 70, *range(100, 113), *range(120, 147)]
        self.assertEqual(len(modes), 85)
        for mode in modes:
            with self.subTest(mode=mode):
                result = subprocess.run([str(binary), str(mode)], capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_ordered_variant_compiling_transaction_omissions_are_rejected(self):
        call = 'error = aether_pool_hooks_bind_transaction(tx);'
        self.assertEqual(self.write_body.count(call), 1)
        for name, body, mode in (
            ('missing-bind', self.write_body.replace(call, '{ error = 0; if (0) aether_pool_hooks_bind_transaction(tx); }'), 0),
            ('wrong-transaction', self.write_body.replace(call, 'error = aether_pool_hooks_bind_transaction(NULL);'), 0),
            ('ignored-bind-error', self.write_body.replace(call, '{ error = aether_pool_hooks_bind_transaction(tx); error = 0; }'), 68),
            ('late-bind', self.write_body.replace(call, 'error = 0;').replace(
                'out->bytes_staged = length;', call + '\n        out->bytes_staged = length;'), 0),
        ):
            with self.subTest(omission=name):
                binary = self.compile(body, name, ordered=True)
                result = subprocess.run([str(binary), str(mode)], capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 93, result.stdout + result.stderr)
                self.assertIn('HOST ZPL WRITE oracle93', result.stderr)
                print('ZPL WRITE ordered omission rejected:', name, mode, result.stderr.strip())

    def test_pinned_native_headers_exact_imports_dependencies_and_stack_usage(self):
        receipt = json.loads((CURRENT / 'build-attempt-5/results.json').read_text())
        recipe = next(c['argv'] for c in receipt['commands'] if c['name'] == 'input-176-checked')
        prefix = [route(a) for a in recipe[:recipe.index('-c')]]
        llvm = Path(prefix[0]).parent
        obj = self.out / 'native-writer.o'
        deps = self.out / 'native-writer.d'
        argv = prefix + ['-isystem', str(llvm.parent / 'lib/clang/21/include'), '-std=gnu11',
                         '-Wall', '-Wextra', '-Werror', '-fstack-usage', '-MD', '-MF', str(deps),
                         '-c', str(OWNED / 'zpl-write.c'), '-o', str(obj)]
        result = subprocess.run(argv, capture_output=True, text=True, timeout=180)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(hashlib.sha256(obj.read_bytes()).hexdigest(),
                         'e9265dffa274f45267674c33175be42f1afbdc28e0367fd80b6665499d40f116')
        symbols = subprocess.check_output([str(llvm / 'llvm-nm'), '-u', str(obj)], text=True)
        imports = {line.split()[-1] for line in symbols.splitlines() if line.strip()}
        self.assertEqual(imports, {
            '__stack_chk_fail', 'dmu_object_info', 'dmu_objset_disown', 'dmu_objset_own', 'dmu_objset_spa',
            'dmu_read', 'memcpy', 'memset', 'sa_bulk_lookup', 'sa_handle_destroy', 'sa_handle_get', 'sa_setup',
            'spa_writeable', 'free', 'calloc', 'zap_lookup', 'zfs_attr_table', 'zfs_get_zplprop',
            'dsl_prop_get_integer', 'dmu_tx_create', 'dmu_tx_hold_write', 'dmu_tx_hold_sa', 'dmu_tx_assign',
            'dmu_tx_abort', 'dmu_tx_get_txg', 'dmu_write', 'sa_bulk_update', 'dmu_tx_commit',
            'txg_wait_synced_flags', 'spa_get_dsl', 'spa_last_synced_txg',
            'dmu_objset_is_snapshot', 'dmu_objset_userobjspace_upgradable',
            'dmu_objset_projectquota_upgradable', 'dmu_objset_userused_enabled',
            'dmu_objset_userspace_present',
        })
        pins = json.loads((CURRENT / 'current-inputs.json').read_text())['files']
        inputs = {}
        for name in deps.read_text().split(':', 1)[1].replace('\\\n', ' ').split():
            path = Path(name)
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            inputs[str(path)] = digest
            if path.is_relative_to(CURRENT):
                self.assertEqual(pins[str(path.relative_to(CURRENT))], digest, str(path))
        stack = obj.with_suffix('.su').read_text()
        self.assertIn('aether_zpl_write\t', stack)
        self.assertNotIn('dynamic', stack)
        writer_frame = next(int(line.split('\t')[1]) for line in stack.splitlines()
                            if line.split('\t')[0].endswith(':aether_zpl_write'))
        self.assertLessEqual(writer_frame, 8192)  # Local helper bound, not full native call-chain qualification.
        # Independently measured before extracting the private writer factory.
        # Updating this control requires an explicit reader-impact/native review.
        read_obj, read_deps = self.out / 'readonly.o', self.out / 'readonly.d'
        read_argv = [str(read_obj) if a == str(obj) else str(read_deps) if a == str(deps)
                     else str(OWNED / 'zpl-read.c') if a == str(OWNED / 'zpl-write.c') else a for a in argv]
        read_result = subprocess.run(read_argv, capture_output=True, text=True, timeout=180)
        self.assertEqual(read_result.returncode, 0, read_result.stdout + read_result.stderr)
        read_sha = hashlib.sha256(read_obj.read_bytes()).hexdigest()
        self.assertEqual(read_sha, 'eb49d91abb7fe7a514e40dc6b54bbe27d97299baa56ae304128e9951c4af8623')
        print('ZPL WRITE NATIVE ' + json.dumps({'argv': argv, 'bytes': obj.stat().st_size,
              'object_sha256': hashlib.sha256(obj.read_bytes()).hexdigest(), 'imports': sorted(imports),
              'dependency_sha256': inputs, 'stack_usage': stack,
              'readonly_control': {'argv': read_argv, 'bytes': read_obj.stat().st_size, 'sha256': read_sha},
              'tools': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (llvm / 'clang', llvm / 'llvm-nm')},
              'scope': 'Unlinked native headers, not resource-aware link, runtime stack fit or disk decoding'}))

    def test_selected_readonly_resource_object_matches_qualified_native_profile(self):
        # Execute the maintained builder's actual header preparation block, not
        # a copied approximation of allocation/time/resource overrides.
        output = self.out / 'selected'
        prepare_resource_headers(output)
        receipt = json.loads((CURRENT / 'build-attempt-5/results.json').read_text())
        recipe = next(c['argv'] for c in receipt['commands'] if c['name'] == 'input-176-checked')
        prefix = [route(a) for a in recipe[:recipe.index('-c')]]
        prefix[1:1] = ['-I' + str(output / 'resources'), '-I' + str(output / 'allocation'), '-I' + str(OWNED)]
        prefix += ['-isystem', str(Path(prefix[0]).parents[1] / 'lib/clang/21/include')]
        obj = output / 'zpl-read.o'
        argv = prefix + ['-std=gnu11', '-Wall', '-Wextra', '-Werror', '-ffunction-sections',
                         '-fdata-sections', '-c', str(OWNED / 'zpl-read.c'), '-o', str(obj)]
        result = subprocess.run(argv, capture_output=True, text=True, timeout=180)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        digest = hashlib.sha256(obj.read_bytes()).hexdigest()
        self.assertEqual(digest, 'a0220af661b1689f30186039c4dbbe78425ec4c9eb33d051e13dc348c61c42ac')
        print('ZPL WRITE READONLY SELECTED ' + json.dumps({'argv': argv, 'bytes': obj.stat().st_size,
              'object_sha256': digest, 'headers': {str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in output.rglob('*.h')}, 'scope': 'Exact current readonly resource object; no writer link or guest'}))


if __name__ == '__main__':
    unittest.main()
