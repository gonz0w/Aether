# SPDX-License-Identifier: BSD-2-Clause
"""Pinned original early sync prefixes and strict private profile admission."""
import copy
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import test_openzfs_zpl_txg_worker as worker
import test_openzfs_zpl_stages as outer
import test_service_runtime as runtime_tests
import test_zpl_pair as controls
from openzfs_pool import (patch_sync_spa, patch_sync_dsl, sync_stage_body,
                         sync_stage_flow, worker_flow, function)
from openzfs_elapsed import CURRENT
import openzfs_elapsed as elapsed
import openzfs_volume as volume
import zpl_pair as pair

ROOT, OWNED, runtime = worker.ROOT, worker.OWNED, worker.runtime
UPSTREAM = CURRENT / 'baseline/source/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1/module/zfs'


class SyncPrefixes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-sync-stages-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.out = Path(cls.temp.name)
        cls.originals = {n: (UPSTREAM / f).read_text() for f, n in
                         (('spa.c', 'spa_sync'), ('dsl_pool.c', 'dsl_pool_sync'))}
        cls.selected = {n: patch(cls.originals[n]) for n, patch in
                        (('spa_sync', patch_sync_spa), ('dsl_pool_sync', patch_sync_dsl))}
        spa = function(cls.selected['spa_sync'], 'spa_sync')
        end = spa.index("\n\taether_pool_worker_progress(spa->spa_dsl_pool, txg, 'r');")
        spa = spa[:spa.index('\n', end + 1)] + '\n}'
        dsl = function(cls.selected['dsl_pool_sync'], 'dsl_pool_sync')
        end = dsl.index("\n\tif (spa_sync_pass(dp->dp_spa) == 1) aether_pool_worker_progress(dp, txg, 'v');")
        dsl = dsl[:dsl.index('\n', end + 1)] + '\n\t(void)dd; (void)mos;\n}'
        cls.prefixes = dsl.replace('void\ndsl_pool_sync', 'static void\ndsl_pool_sync', 1) + '\n' + spa
        cls.sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        cls.binary = cls.compile(cls.prefixes, 'sync')

    @classmethod
    def compile(cls, body, name):
        (cls.out / 'sync-prefixes.inc').write_text(body)
        binary = cls.out / name
        r = subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-isysroot', cls.sdk,
                            '-std=gnu11', '-O2', '-Wall', '-Wextra', '-Werror', '-I' + str(cls.out),
                            str(ROOT / 'tests/fixtures/openzfs_sync_stages.c'), '-o', str(binary)],
                           capture_output=True, text=True, timeout=30)
        if r.returncode:
            raise RuntimeError(r.stdout + r.stderr)
        return binary

    def test_actual_pinned_prefixes_distinguish_blocked_io_lock_dataset_and_convergence(self):
        for mode in range(6):
            r = subprocess.run([str(self.binary), str(mode)], capture_output=True, text=True, timeout=5)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_compiling_missing_early_marker_and_later_pass_duplication_fail94(self):
        for name, old, new, mode in (
            ('missing', "\taether_pool_worker_progress(spa->spa_dsl_pool, txg, 'e');", '', 0),
            ('early-io', "\taether_pool_worker_progress(spa->spa_dsl_pool, txg, 'i');", "\taether_pool_worker_progress(spa->spa_dsl_pool, txg, 'e');", 0),
            ('later-pass', 'if (spa_sync_pass(dp->dp_spa) == 1)', 'if (spa_sync_pass(dp->dp_spa) >= 1)', 0),
        ):
            binary = self.compile(self.prefixes.replace(old, new), name)
            r = subprocess.run([str(binary), str(mode)], capture_output=True, text=True, timeout=5)
            self.assertEqual(r.returncode, 94, r.stdout + r.stderr)
            self.assertIn('SYNC STAGE oracle94', r.stderr)

    def test_existing_spa_import_wrapper_and_pool_worker_floor_are_preserved(self):
        from openzfs_volume import patch_pool_workers
        source, _ = patch_pool_workers(self.originals['spa_sync'])
        suffix = '\n#define AETHER_POOL_ZPL_WRITE 1\n#include "spa-pool.inc"\n#include "spa-stage-import.inc"\n'
        changed = patch_sync_spa(source + suffix)
        self.assertTrue(changed.endswith(suffix))
        self.assertIn('ZTI_SCALE(8)', changed)
        self.assertEqual(changed.count("txg, 'e');"), 1)

    def test_original_body_pins_duplicate_drift_and_inverse_insertions(self):
        for name, patcher in (('spa_sync', patch_sync_spa), ('dsl_pool_sync', patch_sync_dsl)):
            original = sync_stage_body(self.originals[name], name)
            selected = function(self.selected[name], name)
            restored = '\n'.join(l for l in selected.splitlines() if 'aether_pool_worker_progress(' not in l)
            self.assertEqual(restored, original)
            for bad in (self.originals[name] * 2, self.originals[name].replace(original, original.replace('uint64_t txg)', 'uint64_t other)', 1), 1)):
                with self.assertRaises((ValueError, RuntimeError)):
                    patcher(bad)


class Controller(outer.StageController):
    @classmethod
    def setUpClass(cls):
        class Candidate(runtime_tests.PoolNamespaceWriteDriver):
            pool_zpl_stages = True
            pool_zpl_txg_stages = True
            pool_zpl_sync_stages = True
        Candidate.setUpClass()
        cls.addClassCleanup(Candidate.doClassCleanups)
        cls.candidate = Candidate


def success():
    return worker.success().replace(outer.observations(pair.TXG_WORKER_TAGS[:19] + (788).to_bytes(8, 'little') + b'SDJFR'),
                                    outer.observations(pair.SYNC_STAGE_TAGS[:19] + (788).to_bytes(8, 'little') + b'SDJFR'), 1)


class Decoding(unittest.TestCase):
    def test_all_prefixes_early_wait_error_and_complete_trace_stay_diagnostic(self):
        text = pair.SYNC_STAGE_TAGS[:19] + (788).to_bytes(8, 'little') + b'SDJFR'
        for n in range(1, 33):
            r = pair.decode_zpl_stages(outer.observations(text[:n]), txg_worker=True, sync_stages=True)
            self.assertFalse(r['qualification'])
        for path in pair.SYNC_STAGE_PATHS[1:]:
            r = pair.decode_zpl_stages(outer.observations(b'BIUVWLPOAMT' + path), txg_worker=True, sync_stages=True)
            self.assertEqual(r['last_boundary'], 'wait-return')
        for n in range(8):
            data = b'BIUVWLPOAMT' + b'beicpvr'[:n] + b'E' + bytes([6, 5, 0, 0, 0])
            r = pair.decode_zpl_stages(outer.observations(data), txg_worker=True, sync_stages=True)
            self.assertEqual(r['error_projection'], {'stage': 6, 'errno': 5})
        for bad in (b'BIUVWLPOAMTbqs', b'BIUVWLPOAMTbie', b'BIUVWLPOAMTbee'):
            with self.assertRaises(ValueError):
                pair.decode_zpl_stages(outer.observations(bad), txg_worker=True, sync_stages=True)

    def test_full_oracles_cleanup_and_media_admission_gate_recovery(self):
        r = runtime.check_zpl_write_trace(success(), True, False, True, True)
        self.assertEqual(r['stage_boundaries_observed'], 'beicpvrw')
        f = controls.PairControls(); f.setUp(); self.addCleanup(f.doCleanups)
        f.execute(writer_text=success(), txg_worker_diagnostic=True, sync_stages=True)
        self.assertEqual(f.launched, ['baseline', 'writer', 'reader'])
        for bad in (outer.observations(b'BIUVWLPOAMTbeicp'), worker.success(), success().replace('phase=7', 'phase=6', 1)):
            with self.assertRaises(ValueError):
                f.execute(writer_text=bad, txg_worker_diagnostic=True, sync_stages=True)
            self.assertEqual(f.launched, ['baseline', 'writer'])

    def test_invalid_selection_rejects_before_intake_and_prepared_flags_cannot_downgrade(self):
        for args in (['--sync-stages'], ['--sync-stages', '--repeated-writes']):
            r = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/zpl_pair.py'), *args, '--delivery', '/absent', '--utc-delivery', '/absent'], capture_output=True, text=True, timeout=5)
            self.assertEqual(r.returncode, 64)
        for owner, kwargs in ((runtime.suite, {'_zpl_sync_stages': True}), (volume.build, {'pool_zpl_sync_stages': True}), (elapsed.prepare, {'volume_pool_zpl_sync_stages': True})):
            with self.assertRaisesRegex(ValueError, 'sync stages require'):
                owner(Path('/absent'), None, None, **kwargs) if owner is volume.build else owner(Path('/absent'), None, **kwargs) if owner is elapsed.prepare else owner(Path('/absent'), **kwargs)
        f = controls.PairControls(); f.setUp(); self.addCleanup(f.doCleanups)
        f.builds['writer'].update(pool_zpl_repeat=True, pool_zpl_stages=True, pool_zpl_txg_stages=True)
        f.builds['baseline'] = copy.deepcopy(f.builds['reader']); f.builds['baseline']['pool_zpl_recover'] = False
        (f.output / 'baseline').mkdir()
        for name in ('aether.iso', 'engine.elf'):
            (f.output / 'baseline' / name).write_bytes((f.output / 'reader' / name).read_bytes())
        with patch.object(runtime, 'sealed'):
            with self.assertRaises(ValueError): pair.verify_prepared(f.output, f.builds, True, True, False, True, True)
            f.builds['writer']['pool_zpl_sync_stages'] = True
            pair.verify_prepared(f.output, f.builds, True, True, False, True, True)
            with self.assertRaises(ValueError): pair.verify_prepared(f.output, f.builds, True, True, False, True)

    def test_sync_flow_preserves_gate_binding_and_ordered_witness_without_old_markers(self):
        text = (OWNED / 'pool-repeat.inc').read_text()
        selected = sync_stage_flow(text)
        self.assertIn("if (!n) aether_pool_worker_progress(dp, target, 'b');", selected)
        self.assertIn('dp != pool_dp || target != atomic_load(&pool_repeat_records[0].txg)', selected)
        self.assertNotIn("local == 1 ? 'l'", selected)
        self.assertIn('pool_problem();', selected)
        self.assertEqual(selected.count('aether_pool_worker_progress('), 2)


class Flow(unittest.TestCase):
    compile = classmethod(worker.Flow.compile.__func__)

    @classmethod
    def setUpClass(cls):
        base = worker.repeat.RepeatedTransactions
        base.setUpClass(); cls.addClassCleanup(base.doClassCleanups)
        cls.base = base; cls.out = base.base.output
        cls.flow = sync_stage_flow(base.flow)
        driver = (ROOT / 'tests/fixtures/openzfs_pool_repeat.c').read_text()
        callback = """static unsigned worker_events;
void aether_pool_worker_phase(unsigned char event) {
    if (!(event == 'b' && !worker_events)) { fprintf(stderr, "pool hook rejection: sync-stage owner/event\\n"); exit(1); }
    ++worker_events;
}
"""
        driver = driver.replace('static unsigned repeat_mode;', callback + '\nstatic unsigned repeat_mode;', 1)
        driver = driver.replace('    REQUIRE(!aether_zfs_volume_bind(17));', "    aether_pool_worker_progress(&dp,7,'v');\n    REQUIRE(!aether_zfs_volume_bind(17));", 1)
        driver = driver.replace('    REQUIRE(!aether_pool_hooks_bind_transaction(&selected_tx));', '    REQUIRE(!aether_pool_hooks_bind_transaction(&selected_tx));\n    REQUIRE(worker_events == 1);', 1)
        driver = driver.replace('    REQUIRE(!repeat_phases(0, 7));', "    aether_pool_worker_progress(&foreign_dp,7,'v');\n    aether_pool_worker_progress(&dp,8,'v');\n    REQUIRE(!repeat_phases(0, 7));", 1)
        driver = driver.replace('    vdev_file_close(&leaf);', "    vdev_file_close(&leaf);\n    if (atomic_load(&pool_publication) == POOL_CLOSED) aether_pool_worker_progress(&dp,7,'v');\n    REQUIRE(worker_events == 1);", 1)
        cls.driver = driver
        cls.binary = cls.compile(cls.flow, 'sync-flow')

    def test_original_two_record_graph_and_all17_denials_keep_scope_and_witness(self):
        for mode in range(17):
            r = subprocess.run([str(self.binary), str(mode)], capture_output=True, text=True, timeout=10)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_compiling_foreign_scope_or_missing_binding_observation_fails_semantically(self):
        for i, old, new in ((0, 'dp != pool_dp ||', '((void)dp,0) ||'),
                             (1, "if (!n) aether_pool_worker_progress(dp, target, 'b');", '')):
            self.assertEqual(self.flow.count(old), 1)
            binary = self.compile(self.flow.replace(old, new, 1), 'sync-flow-bad' + str(i))
            r = subprocess.run([str(binary), '7'], capture_output=True, text=True, timeout=10)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn('pool hook rejection:', r.stderr)
