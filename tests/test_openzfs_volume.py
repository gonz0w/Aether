# SPDX-License-Identifier: BSD-2-Clause
"""Volume arithmetic, source-selection drift and artifact-origin rejection."""
from pathlib import Path
import hashlib
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from openzfs_volume import OWNED, patch_kernel, patch_vdev
from openzfs_pool import patch_pool_vdev, patch_pool_txg, patch_pool_labels, sync_body, pool_open_mode_body, pool_transaction_body, patch_pool_graph, graph_body, trusted_write_hooks
from openzfs_elapsed import CURRENT, function
from service_runtime_smoke import suite, check_engine_bindings, ROOT


class OpenZfsFlushBodies(unittest.TestCase):
    """Real selected bodies; synthetic backend/queue, no native durability claim."""

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-volume-flush-host-')
        cls.addClassCleanup(cls.temp.cleanup)
        output = Path(cls.temp.name)
        upstream = CURRENT / 'baseline/source/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1/module/zfs'
        callback = function((upstream / 'vdev_file.c').read_text(), 'vdev_file_io_fsync')
        constructor = function((upstream / 'zio.c').read_text(), 'zio_flush')
        (output / 'upstream-flush.inc').write_text(callback + '\n' + constructor + '\n')
        cls.binary = output / 'probe'
        sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        compiled = subprocess.run([
            '/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-std=gnu11',
            '-O2', '-Wall', '-Wextra', '-Werror', '-isysroot', sdk,
            '-I' + str(OWNED), '-I' + str(output),
            str(ROOT / 'tests/fixtures/openzfs_volume_flush.c'), '-o', str(cls.binary),
        ], capture_output=True, text=True, timeout=30)
        if compiled.returncode:
            raise RuntimeError(compiled.stderr)

    def check_modes(self, modes):
        for mode in modes:
            with self.subTest(mode=mode):
                result = subprocess.run([str(self.binary), str(mode)],
                                        capture_output=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_success_and_leaf_errors_are_distinct_from_parent_success(self):
        self.check_modes((0, 1, 2, 3))

    def test_cache_and_nonconcrete_bypasses_issue_no_provider_flush(self):
        self.check_modes((4, 5))

    def test_unsupported_flags_and_invalid_file_do_not_reach_flush(self):
        self.check_modes((6,))


class OpenZfsPoolHooks(unittest.TestCase):
    """Actual file-vdev bodies/provider; synthetic transport, no native claim."""

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-pool-hooks-host-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.output = Path(cls.temp.name)
        source = CURRENT / 'baseline/source/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1/module/zfs/vdev_file.c'
        cls.original = source.read_text()
        cls.selected = patch_pool_vdev(cls.original)
        # Preserve CDDL terms/copyrights in the temporary upstream excerpt too.
        base = source.parent
        cls.transaction_sources = [(base / 'dmu_tx.c').read_text(),
                                   (base / 'spa_misc.c').read_text()]
        cls.getters = cls.transaction_sources[0].split('#include', 1)[0] + '\n'
        cls.getters += '\n'.join(pool_transaction_body(cls.transaction_sources[0], name)
                                for name in ('dmu_tx_get_txg', 'dmu_tx_pool'))
        cls.getters += '\n' + pool_transaction_body(cls.transaction_sources[1], 'spa_get_dsl')
        start = cls.transaction_sources[1].index('boolean_t\nspa_writeable(')
        body = cls.transaction_sources[1][start:cls.transaction_sources[1].index('\n}', start) + 2]
        if hashlib.sha256(body.encode()).hexdigest() != '4f5228e95996e2a93db29319b8792851cd56cb36b419487120c02056f215675a':
            raise RuntimeError('original SPA writeability body changed')
        cls.getters += '\n' + body
        cls.bodies = cls.original.split('#include', 1)[0] + '#include "pool-vdev-hooks.inc"\n' + pool_open_mode_body(cls.original) + '\n' + '\n'.join(
            function(cls.selected, name) for name in
            ('vdev_file_open', 'vdev_file_close', 'vdev_file_io_strategy', 'vdev_file_io_fsync', 'vdev_file_io_start'))
        cls.bodies = cls.getters + '\n' + cls.bodies
        (cls.output / 'pool-bodies.inc').write_text(cls.bodies)
        cls.binary = cls.compile(cls.output, 'probe')

    @classmethod
    def compile(cls, output, name):
        binary = output / name
        sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        result = subprocess.run([
            '/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-std=gnu11',
            '-O2', '-Wall', '-Wextra', '-Werror', '-pthread', '-isysroot', sdk,
            '-I' + str(output), '-I' + str(OWNED), str(OWNED / 'pool-witness.c'),
            str(ROOT / 'tests/fixtures/openzfs_pool_hooks.c'), '-o', str(binary),
        ], capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise RuntimeError(result.stderr)
        return binary

    def check_modes(self, modes):
        for mode in modes:
            with self.subTest(mode=mode):
                result = subprocess.run([str(self.binary), str(mode)],
                                        capture_output=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_original_dispatch_provider_borrows_and_concurrent_completions(self):
        self.check_modes((0, 7, 8))

    def test_bypassed_and_missing_callback_after_an_earlier_healthy_flush(self):
        self.check_modes((1, 2, 6))

    def test_original_partial_and_provider_errors_before_suppression(self):
        self.check_modes((3, 4, 5, 9, 10))

    def test_constructor_errors_and_unprepared_observer_do_not_publish(self):
        self.check_modes((16, 20, 21, 22))

    def test_constructor_reopening_foreign_and_retired_identity_controls(self):
        self.check_modes((11, 13, 14, 15, 17, 19, 23, 24))

    def test_workers_before_constructor_and_competing_publications(self):
        self.check_modes((12, 18))

    def test_selected_transaction_identity_and_terminal_denials(self):
        self.check_modes(range(25, 38))

    def test_import_tree_replacement_reproduces_retired_observer_and_writer_selects_trusted_open(self):
        self.check_modes((38,))
        hooks = (OWNED / 'pool-vdev-hooks.inc').read_text()
        selected = trusted_write_hooks(hooks)
        self.assertIn('if (!spa_writeable(vd->vdev_spa))', selected)
        for changed in (hooks.replace('static void aether_pool_hook_open', 'static void foreign_open'),
                        hooks + hooks):
            with self.assertRaises(ValueError):
                trusted_write_hooks(changed)
        for kind, body, expected in (
                ('fixed', selected, 0), ('omitted', hooks, 1),
                ('inverted', selected.replace('!spa_writeable(vd->vdev_spa)', 'spa_writeable(vd->vdev_spa)'), 1)):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory(prefix='aether-import-lifetime-') as directory:
                output = Path(directory)
                (output / 'pool-bodies.inc').write_text(self.bodies)
                (output / 'pool-vdev-hooks.inc').write_text(body)
                binary = self.compile(output, kind)
                for mode in (39, 40):
                    result = subprocess.run([str(binary), str(mode)], capture_output=True, text=True, timeout=10)
                    self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
                    if expected:
                        self.assertIn('pool hook rejection:', result.stderr)

    def test_transaction_join_guards_and_getter_target_fail_named_oracles(self):
        hooks = (OWNED / 'pool-vdev-hooks.inc').read_text()
        cases = (
            (hooks.replace('dp->dp_spa != pool_spa || spa_get_dsl(pool_spa) != dp',
                           'spa_get_dsl(pool_spa) != dp'), 28,
             b'pool hook rejection: aether_pool_hooks_bind_transaction(&selected_tx) == EXDEV'),
            (hooks.replace('dp->dp_spa != pool_spa || spa_get_dsl(pool_spa) != dp',
                           'dp->dp_spa != pool_spa'), 29,
             b'pool hook rejection: aether_pool_hooks_bind_transaction(&selected_tx) == EXDEV'),
            (hooks.replace('dmu_tx_get_txg(tx)', 'UINT64_C(7)'), 25,
             b'pool hook rejection: atomic_load(&witness.target_txg) == 11'),
            (hooks.replace('bits |= AETHER_POOL_TXG_PENDING;', 'bits |= 0;'), 36,
             b'pool hook rejection: aether_pool_hooks_check(7) == AETHER_POOL_TXG_PENDING'),
        )
        for changed, mode, oracle in cases:
            with self.subTest(mode=mode):
                self.assertNotEqual(changed, hooks)
                with tempfile.TemporaryDirectory(prefix='aether-pool-join-broken-') as directory:
                    output = Path(directory)
                    (output / 'pool-vdev-hooks.inc').write_text(changed)
                    (output / 'pool-bodies.inc').write_text(self.bodies)
                    binary = self.compile(output, 'broken')
                    result = subprocess.run([str(binary), str(mode)], capture_output=True, timeout=10)
                    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                    self.assertIn(oracle, result.stderr)

    def test_original_transaction_getters_reject_drift_and_duplicate_intake(self):
        for text, names in ((self.transaction_sources[0], ('dmu_tx_get_txg', 'dmu_tx_pool')),
                            (self.transaction_sources[1], ('spa_get_dsl',))):
            for name in names:
                body = pool_transaction_body(text, name)
                for changed in (text + '\n' + body, text.replace(body, body.replace('return (', 'return (0 + ', 1))):
                    with self.assertRaises(RuntimeError):
                        pool_transaction_body(changed, name)

    def test_open_close_omission_and_early_publication_fail_named_oracles(self):
        opened = function(self.bodies, 'vdev_file_open')
        closed = function(self.bodies, 'vdev_file_close')
        open_call = '\taether_pool_hook_open(vd);\n'
        close_call = '\taether_pool_hook_close(vd);\n'
        self.assertEqual(opened.count(open_call), 1)
        self.assertEqual(closed.count(close_call), 1)
        attr = '\terror =  zfs_file_getattr(vf->vf_file, &zfa);'
        self.assertEqual(opened.count(attr), 1)
        early = opened.replace(open_call, '').replace(attr, open_call + attr)
        cases = (
            (self.bodies.replace(opened, opened.replace(open_call, '')), 0,
             b'pool hook rejection: aether_pool_hooks_check(0) == initial_bits'),
            (self.bodies.replace(closed, closed.replace(close_call, '')), 17,
             b'pool hook rejection: atomic_load(&pool_publication) == POOL_CLOSED'),
            (self.bodies.replace(opened, early), 16,
             b'pool hook rejection: aether_pool_hooks_check(0) == AETHER_POOL_INCOMPLETE'),
        )
        for body, mode, oracle in cases:
            with self.subTest(mode=mode):
                with tempfile.TemporaryDirectory(prefix='aether-pool-publish-broken-') as directory:
                    output = Path(directory)
                    (output / 'pool-bodies.inc').write_text(body)
                    binary = self.compile(output, 'broken')
                    result = subprocess.run([str(binary), str(mode)], capture_output=True, timeout=10)
                    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                    self.assertIn(oracle, result.stderr)

    def test_removed_provider_or_leaf_hook_fails_named_completion_oracle(self):
        for statement in (
            '\taether_pool_hook_provider(&observation, vf->vf_file, zio->io_error, 0);\n',
            '\taether_pool_hook_finish(&observation, zio);\n',
        ):
            with self.subTest(statement=statement):
                with tempfile.TemporaryDirectory(prefix='aether-pool-hooks-broken-') as directory:
                    output = Path(directory)
                    self.assertIn(statement, self.bodies)
                    # Scope the leaf removal to the fsync body to keep WRITE healthy.
                    flush = function(self.bodies, 'vdev_file_io_fsync')
                    self.assertEqual(flush.count(statement), 1)
                    broken = self.bodies.replace(flush, flush.replace(statement, ''), 1)
                    (output / 'pool-bodies.inc').write_text(broken)
                    binary = self.compile(output, 'broken')
                    result = subprocess.run([str(binary), '0'], capture_output=True, timeout=10)
                    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                    self.assertIn(b'pool hook rejection: aether_pool_hooks_check(7) == expected',
                                  result.stderr)

    def test_leaf_hook_after_interrupt_fails_poisoned_identity_oracle(self):
        flush = function(self.bodies, 'vdev_file_io_fsync')
        hook = '\taether_pool_hook_finish(&observation, zio);\n'
        self.assertEqual(flush.count(hook), 1)
        reordered = flush.replace(hook, '').replace(
            '\tzio_interrupt(zio);', '\tzio_interrupt(zio);\n' + hook.rstrip('\n'), 1)
        with tempfile.TemporaryDirectory(prefix='aether-pool-hooks-lifetime-') as directory:
            output = Path(directory)
            (output / 'pool-bodies.inc').write_text(self.bodies.replace(flush, reordered, 1))
            binary = self.compile(output, 'broken')
            result = subprocess.run([str(binary), '0'], capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn(b'pool hook rejection: aether_pool_hooks_check(7) == expected',
                          result.stderr)

    def test_only_observations_are_added_and_drift_is_rejected(self):
        for name in ('vdev_file_open', 'vdev_file_close', 'vdev_file_io_strategy', 'vdev_file_io_fsync', 'vdev_file_io_start'):
            body = function(self.selected, name)
            restored = '\n'.join(line for line in body.split('\n')
                                 if 'aether_pool_hook_' not in line)
            self.assertEqual(restored, function(self.original, name))
        for malformed in (
            self.selected,
            self.original.replace('vd->vdev_ashift, &resid);', 'vd->vdev_ashift, NULL);'),
            self.original.replace('\t\tzio_interrupt(zio);', '', 1),
            self.original.replace('if (zfs_nocacheflush)', 'if (0)'),
            self.original + '\n' + function(self.original, 'vdev_file_io_fsync'),
            self.original.replace('vf->vf_file = fp;', 'vf->vf_file = NULL;'),
            self.original.replace('if (vf->vf_file != NULL)', 'if (0)'),
            self.original.replace('return (mode | O_LARGEFILE);', 'return (mode);'),
        ):
            with self.assertRaises(RuntimeError):
                patch_pool_vdev(malformed)


class OpenZfsPoolSync(unittest.TestCase):
    """Original waits/label sequencing; synthetic progress and lower transport."""

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-pool-sync-host-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.output = Path(cls.temp.name)
        base = CURRENT / 'baseline/source/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1/module/zfs'
        cls.txg = (base / 'txg.c').read_text()
        cls.labels = (base / 'vdev_label.c').read_text()
        cls.selected_txg = patch_pool_txg(cls.txg)
        cls.selected_labels = patch_pool_labels(cls.labels)
        cls.txg_body = cls.txg.split('#include', 1)[0] + function(cls.selected_txg, 'txg_wait_synced_flags')
        names = ('vdev_label_sync_top_done', 'vdev_label_sync_ignore_done',
                 'vdev_label_sync_list', 'vdev_uberblock_sync_list', 'vdev_config_sync')
        cls.label_bodies = cls.labels.split('#include', 1)[0] + '\n'.join(
            function(cls.selected_labels, name) for name in names)
        (cls.output / 'pool-txg-body.inc').write_text(cls.txg_body)
        (cls.output / 'pool-label-bodies.inc').write_text(cls.label_bodies)
        cls.txg_binary = cls.compile(cls.output, 'txg')
        cls.label_binary = cls.compile(cls.output, 'labels')

    @classmethod
    def compile(cls, output, kind):
        binary = output / kind
        sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        compiled = subprocess.run([
            '/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-std=gnu11',
            '-O2', '-Wall', '-Wextra', '-Werror', '-pthread', '-isysroot', sdk,
            '-I' + str(OWNED), '-I' + str(output),
            str(ROOT / ('tests/fixtures/openzfs_pool_' + kind + '.c')), '-o', str(binary),
        ], capture_output=True, text=True, timeout=30)
        if compiled.returncode:
            raise RuntimeError(compiled.stderr)
        return binary

    def check_modes(self, binary, modes):
        for mode in modes:
            with self.subTest(mode=mode):
                result = subprocess.run([str(binary), str(mode)], capture_output=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_actual_txg_wait_condition_resolution_and_locked_snapshot(self):
        self.check_modes(self.txg_binary, (0, 4, 5))

    def test_original_interruption_and_suspension_errors_survive_progress(self):
        self.check_modes(self.txg_binary, (1, 2, 3))

    def test_original_block_even_uberblock_odd_order_and_early_exits(self):
        self.check_modes(self.label_binary, (0, 1, 2, 3))

    def test_original_retries_failures_and_success_without_flush_is_insufficient(self):
        self.check_modes(self.label_binary, (4, 5, 6, 7, 8))

    def test_observer_or_flush_mutations_fail_named_oracles(self):
        txg_call = '\taether_pool_txg_observe(dp, txg, tx->tx_synced_txg, error);\n'
        ub_call = '\taether_pool_sync_observe(spa, ub->ub_txg, AETHER_POOL_UB_FLUSH_RETURNED, 0);\n'
        cases = (
            ('txg', self.txg_body.replace(txg_call, ''), b'TXG observation rejection:'),
            ('txg', self.txg_body.replace(txg_call, '').replace(
                '\tmutex_exit(&tx->tx_sync_lock);', '\tmutex_exit(&tx->tx_sync_lock);\n' + txg_call.rstrip('\n')),
             b'TXG observation rejection:'),
            ('labels', self.label_bodies.replace(ub_call, ''), b'label ordering rejection:'),
        )
        # Remove one actual original uberblock flush call, preserving all markers.
        ub = function(self.label_bodies, 'vdev_uberblock_sync_list')
        removed = ub.replace('\t\t\tzio_flush(zio, svd[v]);', '')
        self.assertNotEqual(ub, removed)
        cases += (('labels', self.label_bodies.replace(ub, removed), b'label ordering rejection:'),)
        for kind, body, message in cases:
            with self.subTest(kind=kind, message=message):
                with tempfile.TemporaryDirectory(prefix='aether-pool-sync-broken-') as directory:
                    output = Path(directory)
                    name = 'pool-txg-body.inc' if kind == 'txg' else 'pool-label-bodies.inc'
                    (output / name).write_text(body)
                    binary = self.compile(output, kind)
                    result = subprocess.run([str(binary), '0'], capture_output=True, timeout=10)
                    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                    self.assertIn(message, result.stderr)

    def test_exact_original_restoration_and_pinned_source_rejection(self):
        for original, selected, names in (
            (self.txg, self.selected_txg, ('txg_wait_synced_flags',)),
            (self.labels, self.selected_labels,
             ('vdev_config_sync', 'vdev_uberblock_sync_list', 'vdev_label_sync_list')),
        ):
            for name in names:
                restored = '\n'.join(line for line in function(selected, name).split('\n')
                                     if 'aether_pool_' not in line)
                self.assertEqual(restored, sync_body(original, name))
        for patch, source, name in (
            (patch_pool_txg, self.txg, 'txg_wait_synced_flags'),
            (patch_pool_labels, self.labels, 'vdev_config_sync'),
        ):
            for changed in (patch(source), source + '\n' + function(source, name),
                            source.replace('return (error);', 'return (0);')):
                with self.assertRaises(RuntimeError):
                    patch(changed)


class OpenZfsPoolFlow(unittest.TestCase):
    """Original graph/physical/provider bodies; synthetic execution/assignment."""

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-pool-flow-host-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.output = Path(cls.temp.name)
        base = CURRENT / 'baseline/source/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1/module/zfs'
        cls.original = (base / 'zio.c').read_text()
        cls.selected = patch_pool_graph(cls.original)
        cls.graph = cls.original.split('#include', 1)[0] + '\n'.join(
            graph_body(cls.selected, name, checked=False)
            for name in ('zio_add_child_impl', 'zio_destroy', 'zio_write_phys', 'zio_flush'))
        vdev = (base / 'vdev_file.c').read_text()
        selected = patch_pool_vdev(vdev)
        tx = (base / 'dmu_tx.c').read_text()
        spa = (base / 'spa_misc.c').read_text()
        cls.file = tx.split('#include', 1)[0] + '\n'.join(
            pool_transaction_body(tx, name) for name in ('dmu_tx_get_txg', 'dmu_tx_pool'))
        cls.file += '\n' + pool_transaction_body(spa, 'spa_get_dsl')
        cls.file += '\n' + vdev.split('#include', 1)[0] + '#include "pool-vdev-hooks.inc"\n'
        cls.file += pool_open_mode_body(vdev) + '\n' + '\n'.join(
            function(selected, name) for name in
            ('vdev_file_open', 'vdev_file_close', 'vdev_file_io_strategy', 'vdev_file_io_fsync', 'vdev_file_io_start'))
        cls.flow = (OWNED / 'pool-flow.inc').read_text()
        cls.binary = cls.compile(cls.output, cls.graph, cls.flow)

    @classmethod
    def compile(cls, output, graph, flow):
        (output / 'pool-graph-bodies.inc').write_text(graph)
        (output / 'pool-bodies.inc').write_text(cls.file)
        (output / 'pool-flow.inc').write_text(flow)
        # Quoted include resolution must consume the local mutation, not bypass
        # it through the including owned file's directory.
        (output / 'pool-vdev-hooks.inc').write_text((OWNED / 'pool-vdev-hooks.inc').read_text())
        binary = output / 'flow'
        sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        result = subprocess.run([
            '/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-std=gnu11',
            '-O2', '-Wall', '-Wextra', '-Werror', '-pthread', '-isysroot', sdk,
            '-I' + str(output), '-I' + str(OWNED),
            str(OWNED / 'pool-witness.c'), str(ROOT / 'tests/fixtures/openzfs_pool_flow.c'),
            '-o', str(binary),
        ], capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise RuntimeError(result.stderr)
        return binary

    def check_modes(self, modes):
        for mode in modes:
            with self.subTest(mode=mode):
                result = subprocess.run([str(self.binary), str(mode)], capture_output=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_original_requests_provider_completion_and_aggregate_descendants(self):
        self.check_modes((0, 1, 7, 17))

    def test_bypassed_partial_and_failed_phases_cannot_hide_in_prior_success(self):
        self.check_modes((2, 3, 4, 5, 6, 16))

    def test_foreign_overlap_capacity_overflow_retirement_and_wait_controls(self):
        self.check_modes(tuple(range(8, 16)) + (18, 19, 20))

    def test_original_graph_restoration_and_drift_rejection(self):
        for name in ('zio_add_child_impl', 'zio_destroy', 'zio_write_phys', 'zio_flush'):
            body = graph_body(self.selected, name, checked=False)
            restored = '\n'.join(line for line in body.split('\n') if 'aether_pool_' not in line)
            self.assertEqual(restored, graph_body(self.original, name))
            original = graph_body(self.original, name)
            changed = self.original.replace(original, original.replace('{', '{\n/* changed */', 1))
            for text in (self.selected, self.original + '\n' + original, changed):
                with self.assertRaises(RuntimeError):
                    patch_pool_graph(text)

    def test_removed_graph_request_and_sync_guards_fail_named_oracles(self):
        final = b'pool hook rejection: aether_pool_hooks_check_ordered() == expected'
        cases = [
            (self.graph.replace('\taether_pool_zio_child(pio, cio);\n', ''), self.flow, 0, final),
            (self.graph.replace('\taether_pool_zio_retire(zio);\n', ''), self.flow, 0,
             b'pool hook rejection: token == phase'),
            (self.graph.replace('\taether_pool_write_requested(pio, zio);\n', ''), self.flow, 0, final),
            (self.graph.replace('\taether_pool_flush_requested(pio, vd);\n', ''), self.flow, 0, final),
            (self.graph, self.flow.replace('requested != provided', '((void)provided, 0)'), 16, final),
        ]
        for graph, flow, mode, oracle in cases:
            with self.subTest(mode=mode, graph_changed=graph != self.graph):
                self.assertTrue(graph != self.graph or flow != self.flow)
                with tempfile.TemporaryDirectory(prefix='aether-pool-flow-broken-') as directory:
                    binary = self.compile(Path(directory), graph, flow)
                    result = subprocess.run([str(binary), str(mode)], capture_output=True, timeout=10)
                    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                    self.assertIn(oracle, result.stderr)


class OpenZfsPoolWitness(unittest.TestCase):
    """Actual ledger, synthetic host events; no native pool or ordering claim."""

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-pool-witness-host-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.binary = Path(cls.temp.name) / 'probe'
        original = (CURRENT / 'baseline/source/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1/module/zfs/dmu_tx.c').read_text()
        body = function(original, 'dmu_tx_get_txg')
        if hashlib.sha256(body.encode()).hexdigest() != 'c7e3a3891d4f2c2587e7be4c7ccb032f779991fda65da6d77f74e705d508410d':
            raise RuntimeError('pool target getter body changed')
        (Path(cls.temp.name) / 'pool-target-body.inc').write_text(
            original.split('#include', 1)[0] + body)
        sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        compiled = subprocess.run([
            '/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-std=c11',
            '-O2', '-Wall', '-Wextra', '-Werror', '-pthread', '-isysroot', sdk,
            '-I' + str(OWNED), '-I' + cls.temp.name, str(OWNED / 'pool-witness.c'),
            str(ROOT / 'tests/fixtures/openzfs_pool_witness.c'), '-o', str(cls.binary),
        ], capture_output=True, text=True, timeout=30)
        if compiled.returncode:
            raise RuntimeError(compiled.stderr)

    def check_modes(self, modes):
        for mode in modes:
            with self.subTest(mode=mode):
                result = subprocess.run([str(self.binary), str(mode)],
                                        capture_output=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_overlapping_workers_and_matched_observations(self):
        self.check_modes((0, 1))

    def test_duplicate_stale_and_foreign_completion(self):
        self.check_modes((2, 3, 4, 5, 15, 16))

    def test_partial_provider_and_leaf_errors_survive_later_success(self):
        self.check_modes((6, 7, 9))

    def test_missing_completion_capacity_wrap_and_unsynced_txg(self):
        self.check_modes((8, 10, 11, 12, 13, 14))

    def test_deferred_original_getter_target_preserves_early_io_and_errors(self):
        self.check_modes((17, 19, 23, 26, 27))

    def test_missing_zero_repeated_conflicting_and_prebound_targets_reject(self):
        self.check_modes((18, 20, 21, 22, 25))

    def test_contested_binding_has_one_winner_and_sticky_rejection(self):
        self.check_modes((24,))

    def test_unbound_guard_and_overwrite_mutations_fail_target_oracles(self):
        original = (OWNED / 'pool-witness.c').read_text()
        guard = 'if (!target || synced_txg < target)'
        exchange = ('atomic_compare_exchange_strong_explicit(&w->target_txg, &unbound,\n'
                    '                                                 target, memory_order_release,\n'
                    '                                                 memory_order_relaxed)')
        self.assertEqual(original.count(guard), 1)
        self.assertEqual(original.count(exchange), 1)
        cases = (
            (original.replace(guard, 'if (synced_txg < target)'), 18,
             b'pool witness rejection: aether_pool_witness_check(&witness, UINT64_MAX) == AETHER_POOL_TXG_PENDING'),
            (original.replace(exchange, '(atomic_exchange_explicit(&w->target_txg, target, memory_order_release) == unbound)'),
             22, b'pool witness rejection: atomic_load(&witness.target_txg) == target'),
        )
        sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        for body, mode, oracle in cases:
            with self.subTest(mode=mode):
                with tempfile.TemporaryDirectory(prefix='aether-pool-target-broken-') as directory:
                    source = Path(directory) / 'broken.c'
                    binary = Path(directory) / 'broken'
                    source.write_text(body)
                    compiled = subprocess.run([
                        '/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-std=c11',
                        '-O2', '-Wall', '-Wextra', '-Werror', '-pthread', '-isysroot', sdk,
                        '-I' + str(OWNED), '-I' + self.temp.name, str(source),
                        str(ROOT / 'tests/fixtures/openzfs_pool_witness.c'), '-o', str(binary),
                    ], capture_output=True, text=True, timeout=30)
                    self.assertEqual(compiled.returncode, 0, compiled.stderr)
                    result = subprocess.run([str(binary), str(mode)], capture_output=True, timeout=10)
                    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                    self.assertIn(oracle, result.stderr)

    def test_suppressed_provider_error_fails_the_named_oracle(self):
        original = (OWNED / 'pool-witness.c').read_text()
        statement = 'problem(w, AETHER_POOL_PROVIDER_ERROR);'
        self.assertEqual(original.count(statement), 1)
        # Deliberately erase the error before a successful synthetic leaf result.
        mutated = Path(self.temp.name) / 'broken.c'
        mutated.write_text(original.replace(statement, '(void)error;'))
        binary = Path(self.temp.name) / 'broken'
        sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        compiled = subprocess.run([
            '/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-std=c11',
            '-O2', '-Wall', '-Wextra', '-Werror', '-pthread', '-isysroot', sdk,
            '-I' + str(OWNED), '-I' + self.temp.name, str(mutated),
            str(ROOT / 'tests/fixtures/openzfs_pool_witness.c'), '-o', str(binary),
        ], capture_output=True, text=True, timeout=30)
        self.assertEqual(compiled.returncode, 0, compiled.stderr)
        result = subprocess.run([str(binary), '7'], capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(b'pool witness rejection: aether_pool_witness_check(&witness, 7) == expected',
                      result.stderr)


class OpenZfsVolume(unittest.TestCase):
    def test_rust_bounds_rights_partial_effects_and_source_revalidation(self):
        with tempfile.TemporaryDirectory(prefix='aether-volume-host-') as directory:
            binary = Path(directory) / 'volume-tests'
            subprocess.run(['rustc', '+1.98.0', '--edition=2024', '--test',
                            str(OWNED / 'volume.rs'), '-o', str(binary)], check=True,
                           capture_output=True, timeout=30)
            result = subprocess.run([str(binary)], capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_checked_actual_sources_reject_missing_duplicate_and_repeat_patches(self):
        original = (CURRENT / 'build-attempt-1/source/kernel.c').read_text()
        selected, changes = patch_kernel(original)
        self.assertEqual(len(changes), 12)
        self.assertEqual(selected.count('#include "file-functions.inc"'), 1)
        physical, physical_changes = patch_kernel(original, physical=True)
        self.assertEqual(physical.count('#include "file-physical-functions.inc"'), 1)
        self.assertEqual(physical_changes, changes)
        traced, trace_changes = patch_kernel(original, physical=True, open_trace=True)
        self.assertEqual(trace_changes, changes)
        switch = '#define AETHER_PHYSICAL_OPEN_TRACE 1\n'
        self.assertEqual(traced.count(switch), 1)
        self.assertEqual(traced.replace(switch, ''), physical)
        self.assertNotIn('AETHER_PHYSICAL_OPEN_TRACE', selected + physical)
        writable, write_changes = patch_kernel(original, physical=True, write=True)
        self.assertEqual(write_changes, changes)
        self.assertEqual(writable.replace('#define AETHER_PHYSICAL_WRITE 1\n', ''), physical)
        for flags in ({'write': True}, {'physical': True, 'write': True, 'open_trace': True}):
            with self.assertRaises(ValueError):
                patch_kernel('', **flags)
        with self.assertRaises(ValueError):
            patch_kernel('', open_trace=True)
        with self.assertRaises(RuntimeError):
            patch_kernel(physical, physical=True)
        for source in (selected, original.replace('\nzfs_file_open(', '\nchanged_open(', 1),
                       original + '\nint zfs_file_open(void) { return 0; }\n',
                       original.replace('uint64_t physmem;', 'uint64_t other;')):
            with self.assertRaises(RuntimeError):
                patch_kernel(source)
        source = (CURRENT / 'profile/source/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1/module/zfs/vdev_file.c').read_text()
        selected = patch_vdev(source)
        writable = patch_vdev(source, write=True)
        callback = function(source, 'vdev_file_io_fsync')
        self.assertIn(callback.replace('vdev_file_io_fsync(', 'aether_physical_fsync_callback_original(', 1), writable)
        self.assertIn('aether_physical_flush_callback(zio->io_vd, zio->io_type == ZIO_TYPE_FLUSH);', writable)
        self.assertIn('vd->vdev_has_trim = B_FALSE;', selected)
        for changed in (selected, source.replace('vd->vdev_has_trim = B_TRUE;', ''),
                        source + '\n\tvd->vdev_has_trim = B_TRUE;'):
            with self.assertRaises(RuntimeError):
                patch_vdev(changed)

    def test_pool_create_requires_exclusive_corrected_utc_before_intake(self):
        for kwargs in ({'pool_create': True}, {'case': 'pool-create'},
                       {'pool_create': True, 'engine_utc': True,
                        'utc_delivery': Path('/missing'), 'fixed_reaper': True,
                        'spa_physical': True},
                       {'pool_create': True, 'engine_utc': True,
                        'utc_delivery': Path('/missing'), 'fixed_reaper': True,
                        'case': 'utc-spa'}):
            with self.assertRaises(ValueError):
                suite(Path('/missing'), **kwargs)
        for flags in (['--pool-create'], ['--case', 'pool-create'],
                      ['--pool-create', '--engine-utc', '--utc-delivery', '/missing'],
                      ['--pool-create', '--fixed-reaper', '--engine-utc',
                       '--utc-delivery', '/missing', '--spa-write'],
                      ['--pool-create', '--fixed-reaper', '--engine-utc',
                       '--utc-delivery', '/missing', '--case', 'utc-spa']):
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/service_runtime_smoke.py'),
                                     '--delivery', '/missing', *flags], capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 64, result.stderr)
            self.assertNotIn(b'[RUNNING]', result.stderr)

    def test_pool_create_trace_rejects_missing_reordered_and_foreign_rows(self):
        from service_runtime_smoke import check_pool_create_trace
        phases = b"BIUVWP" + bytes(range(8)) + b"CADJFR"
        records = [(0, 1, i * 8, v) for i, v in enumerate(phases)]
        records += [(0, g, i * 8, v) for g in (2, 3) for i, v in enumerate(b"BNR")]
        render = lambda rows: ''.join(
            f'NATIVE observation slot={s} generation={g} offset={o} byte={v}\n'
            for s, g, o, v in rows)
        result = check_pool_create_trace(render(records))
        self.assertEqual(result['input_xdr_fnv1a64'], '0001020304050607')
        self.assertFalse(result['assigned_DMU_transaction'])
        for rows in (records[:-1], records[::-1],
                     [records[0], (1, *records[1][1:]), *records[2:]],
                     [*records[:15], (0, 1, 120, ord('X')), *records[16:]]):
            with self.assertRaises(ValueError):
                check_pool_create_trace(render(rows))

    def test_volume_profile_rejects_incompatible_cases_before_intake(self):
        for kwargs in ({'case': 'block-verify', 'engine_volume': True},
                       {'case': 'write-mode', 'engine_volume': True},
                       {'engine_volume': True, 'block_region': True},
                       {'engine_volume': True, 'rtc_source': True}):
            with self.assertRaises(ValueError):
                suite(Path('/missing'), **kwargs)
        for flags in (['--engine-volume', '--engine-native'], ['--engine-volume', '--case', 'block-verify'],
                      ['--engine-volume', '--case', 'normal']):
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/service_runtime_smoke.py'),
                                     '--delivery', '/missing', *flags], capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 64)
            self.assertNotIn(b'[RUNNING]', result.stderr)

    def test_queued_worker_selection_rejects_ambiguous_or_wrong_profiles(self):
        for kwargs in ({'case': 'block-workers', 'engine_volume': True},
                       {'case': 'block-write', 'engine_volume_workers': True},
                       {'engine_volume_workers': True, 'engine_volume': True},
                       {'engine_volume_workers': True, 'engine_native': True},
                       {'engine_volume': True, 'engine_native': True}):
            with self.assertRaises(ValueError):
                suite(Path('/missing'), **kwargs)
        for flags in (['--case', 'block-workers'], ['--engine-volume', '--case', 'block-workers'],
                      ['--engine-volume-workers', '--engine-volume'],
                      ['--engine-volume-workers', '--case', 'block-write']):
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/service_runtime_smoke.py'),
                                     '--delivery', '/missing', *flags], capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 64)
            self.assertNotIn(b'[RUNNING]', result.stderr)

    def test_spa_utc_profile_rejects_wrong_or_ambiguous_selection(self):
        for kwargs in ({'case': 'spa-utc'}, {'case': 'block-write', 'engine_spa_utc': True},
                       {'engine_spa_utc': True, 'engine_volume_workers': True},
                       {'case': 'zio-write', 'engine_spa_utc': True}):
            with self.assertRaises(ValueError):
                suite(Path('/missing'), **kwargs)
        for flags in (['--case', 'spa-utc'], ['--engine-spa-utc', '--case', 'zio-write'],
                      ['--engine-spa-utc', '--engine-volume'],
                      ['--engine-spa-utc', '--case', 'block-readonly']):
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/service_runtime_smoke.py'),
                                     '--delivery', '/missing', *flags], capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 64)
            self.assertNotIn(b'[RUNNING]', result.stderr)

    def test_shared_utc_selection_is_explicit_and_preserves_old_profiles(self):
        for kwargs in ({'engine_utc': True}, {'utc_delivery': Path('/missing')},
                       {'engine_utc': True, 'utc_delivery': Path('/missing'), 'case': 'spa-utc'},
                       {'engine_utc': True, 'utc_delivery': Path('/missing'), 'engine_spa_utc': True}):
            with self.assertRaises(ValueError):
                suite(Path('/missing'), **kwargs)
        for flags in (['--engine-utc'], ['--utc-delivery', '/missing'],
                      ['--engine-utc', '--utc-delivery', '/missing', '--case', 'spa-utc'],
                      ['--case', 'utc-spa'], ['--case', 'utc-reuse'], ['--case', 'utc-reuse-short'],
                      ['--engine-volume', '--case', 'utc-reuse'], ['--engine-utc', '--engine-volume']):
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/service_runtime_smoke.py'),
                                     '--delivery', '/missing', *flags], capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 64)
            self.assertNotIn(b'[RUNNING]', result.stderr)

    def test_rust_provider_origin_cannot_be_substituted_by_selected_c_engine(self):
        origins = {
            'engine-startup.o': ['main'],
            'selected-engine.o': ['kernel_init', 'kernel_fini', 'cv_init', 'cv_timedwait_hires',
                'random_init', 'random_get_bytes', 'arc_all_memory', 'arc_available_memory',
                'aether_zfs_granted_pages', 'aether_zfs_assigned_cpus', 'aether_zfs_startup_bind',
                'aether_zfs_hostid', 'aether_zfs_uname', 'aether_zfs_empty_cache', 'vdev_file_ops',
                'zfs_file_open', 'zfs_file_pread', 'zfs_file_pwrite', 'zfs_file_fsync', 'aether_zfs_volume_bind'],
            'libaether_runtime.a(backend.o)': ['aether_runtime_init', 'aether_runtime_finish', '__aether_io'],
            'volume-probe.o': ['aether_volume_start_probe', 'aether_volume_engine_probe', 'aether_volume_finish_probe'],
            'libaether_volume.a(volume.o)': ['aether_volume_bind', 'aether_volume_check', 'aether_volume_io', 'aether_volume_flush'],
        }
        mapping = '\n'.join('0 0 0 1 /private/' + owner + ':(.text)\n' +
                             '\n'.join('0 0 0 1 ' + s for s in symbols)
                             for owner, symbols in origins.items())
        self.assertEqual(len(check_engine_bindings(mapping, startup=True, volume=True)), 31)
        worker_map = mapping + '\n0 0 0 1 /private/selected-engine.o:(.text)\n'
        worker_map += '\n'.join('0 0 0 1 ' + n for n in
                                ('taskq_create', 'taskq_dispatch', 'taskq_wait', 'taskq_destroy', 'taskq_of_curthread'))
        worker_map += '\n0 0 0 1 /private/volume-worker-probe.o:(.text)\n'
        worker_map += '0 0 0 1 aether_volume_workers_probe\n0 0 0 1 aether_volume_workers_finish'
        self.assertEqual(len(check_engine_bindings(worker_map, startup=True, volume=True, workers=True)), 38)
        for changed in (mapping, worker_map.replace('volume-worker-probe.o', 'volume-probe.o'),
                        worker_map.replace('0 0 0 1 taskq_dispatch', '')):
            with self.assertRaises(ValueError):
                check_engine_bindings(changed, startup=True, volume=True, workers=True)

        utc_map = mapping + '\n0 0 0 1 /private/selected-engine.o:(.text)\n'
        utc_map += '\n'.join('0 0 0 1 ' + n for n in
                              ('spa_add', 'spa_remove', 'spa_namespace_enter', '__zfs_dbgmsg'))
        utc_map += '\n0 0 0 1 /private/spa-utc-probe.o:(.text)\n'
        utc_map += '\n'.join('0 0 0 1 ' + n for n in
                              ('aether_volume_spa_utc_probe', '__wrap__Exit', '__wrap_clock_gettime'))
        self.assertEqual(len(check_engine_bindings(utc_map, startup=True, volume=True, spa_utc=True)), 38)
        for changed in (mapping, utc_map.replace('0 0 0 1 __zfs_dbgmsg', ''),
                        utc_map + '\n0 0 0 1 spa_add',
                        utc_map.replace('spa-utc-probe.o', 'fake.o')):
            with self.assertRaises(ValueError):
                check_engine_bindings(changed, startup=True, volume=True, spa_utc=True)

        shared_map = mapping + '\n0 0 0 1 /private/selected-engine.o:(.text)\n'
        shared_map += '\n'.join('0 0 0 1 ' + n for n in
                                ('spa_add', 'spa_remove', 'spa_namespace_enter', '__zfs_dbgmsg',
                                 'taskq_create', 'taskq_dispatch', 'taskq_wait', 'taskq_destroy', 'taskq_of_curthread'))
        shared_map += '\n0 0 0 1 /private/volume-utc-probe.o:(.text)\n'
        shared_map += '\n'.join('0 0 0 1 ' + n for n in
                                ('aether_engine_utc_start', 'aether_engine_utc_probe', 'aether_engine_utc_finish'))
        for owner, names in (('utc.o', ('aether_utc_establish', 'aether_utc_read', 'aether_utc_close')),
                             ('real_time.o', ('clock_gettime',)), ('wrappers.o', ('time', 'gettimeofday'))):
            shared_map += '\n0 0 0 1 /private/libaether_runtime.a(' + owner + '):(.text)\n'
            shared_map += '\n'.join('0 0 0 1 ' + n for n in names)
        self.assertEqual(len(check_engine_bindings(shared_map, startup=True, volume=True, utc=True)), 49)
        for changed in (mapping, shared_map.replace('libaether_runtime.a(utc.o)', 'fake.o'),
                        shared_map.replace('0 0 0 1 clock_gettime', ''),
                        shared_map.replace('libaether_runtime.a(wrappers.o)', 'libc.a(time.o)')):
            with self.assertRaises(ValueError):
                check_engine_bindings(changed, startup=True, volume=True, utc=True)

        for changed in (mapping.replace('libaether_volume.a(volume.o)', 'selected-engine.o'),
                        mapping.replace('0 0 0 1 aether_volume_io', ''),
                        mapping + '\n0 0 0 1 aether_volume_flush',
                        mapping.replace('volume-probe.o', 'fake.o')):
            with self.assertRaises(ValueError):
                check_engine_bindings(changed, startup=True, volume=True)
