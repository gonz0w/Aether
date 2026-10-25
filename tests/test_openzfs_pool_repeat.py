# SPDX-License-Identifier: BSD-2-Clause
"""Append-only two-TXG graph/provider/wait witness; no native durability claim."""
from pathlib import Path
import subprocess
import tempfile
import unittest

import test_openzfs_volume as volume_tests
from openzfs_pool import repeated_write_hooks

ROOT, OWNED = volume_tests.ROOT, volume_tests.OWNED


class RepeatedTransactions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base = volume_tests.OpenZfsPoolFlow
        base.setUpClass()
        cls.addClassCleanup(base.doClassCleanups)
        cls.base = base
        cls.hooks = repeated_write_hooks((OWNED / 'pool-vdev-hooks.inc').read_text())
        cls.flow = (OWNED / 'pool-repeat.inc').read_text()
        original = (ROOT / 'tests/fixtures/openzfs_pool_flow.c').read_text()
        cls.driver = original.replace('int main(int argc, char **argv)',
                                      'int repeat_prior_flow_main(int argc, char **argv)', 1)
        spa = (volume_tests.CURRENT / 'baseline/source/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1/module/zfs/spa_misc.c').read_text()
        start = spa.index('boolean_t\nspa_writeable(')
        writable = spa[start:spa.index('\n}', start) + 2]
        cls.file = base.file.replace('#include "pool-vdev-hooks.inc"',
                                      writable + '\n#include "pool-vdev-hooks.inc"', 1)
        cls.binary = cls.compile(cls.hooks, cls.flow, 'repeat')

    @classmethod
    def compile(cls, hooks, flow, name):
        out = cls.base.output
        (out / 'repeat-flow-base.inc').write_text(cls.driver)
        (out / 'pool-bodies.inc').write_text(cls.file)
        (out / 'pool-graph-bodies.inc').write_text(cls.base.graph)
        (out / 'pool-vdev-hooks.inc').write_text(hooks)
        (out / 'pool-repeat.inc').write_text(flow)
        binary = out / name
        sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        result = subprocess.run([
            '/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-std=gnu11',
            '-O2', '-Wall', '-Wextra', '-Werror', '-pthread', '-isysroot', sdk,
            '-I' + str(out), '-I' + str(OWNED), '-I' + str(ROOT / 'tests/fixtures'),
            str(OWNED / 'pool-witness.c'), str(ROOT / 'tests/fixtures/openzfs_pool_repeat.c'),
            '-o', str(binary),
        ], capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        return binary

    def modes(self, modes):
        for mode in modes:
            with self.subTest(mode=mode):
                result = subprocess.run([str(self.binary), str(mode)], capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                if result.stdout:
                    print(result.stdout.strip())

    def test_two_independent_complete_transaction_records_and_retained_target(self):
        self.modes([0, 7, 12])

    def test_duplicate_backward_early_foreign_third_and_retired_binding_reject(self):
        self.modes([1, 2, 3, 4, 5, 6, 14, 15, 16])

    def test_old_success_late_tokens_and_missing_new_wait_do_not_qualify_second(self):
        self.modes([8, 9, 10, 11, 13])

    def test_hook_derivation_rejects_duplicate_and_drifted_contexts(self):
        source = (OWNED / 'pool-vdev-hooks.inc').read_text()
        for changed in (source + source, source.replace('return EALREADY;', 'return EINVAL;'),
                        source.replace('#include "pool-flow.inc"', '/* removed flow */')):
            with self.assertRaises(ValueError):
                repeated_write_hooks(changed)

    def test_compiling_missing_free_target_slot_or_wait_checks_fail_semantically(self):
        variants = (
            ('reused-slot', 'pool_repeat_records[n].txg', 'pool_repeat_records[0].txg', 0),
            ('missing-record', 'count != POOL_REPEAT_LIMIT', '0', 0),
            ('previous-wait', 'atomic_load_explicit(&previous->synced, memory_order_acquire) <\n                old', '0', 15),
            ('late-token', 'unsigned index = token / 8;', 'unsigned index = 1;', 0),
            ('old-wait', 'if (requested < target)', 'if (0 && requested < target)', 11),
            ('no-new-wait', 'if (atomic_load_explicit(&record->synced, memory_order_acquire) <\n            atomic_load(&record->txg))', 'if (0)', 10),
        )
        for name, old, new, mode in variants:
            with self.subTest(omission=name):
                self.assertEqual(self.flow.count(old), 1)
                binary = self.compile(self.hooks, self.flow.replace(old, new, 1), name)
                result = subprocess.run([str(binary), str(mode)], capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn('pool hook rejection:', result.stderr)
