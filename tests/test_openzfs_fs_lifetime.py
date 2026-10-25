# SPDX-License-Identifier: BSD-2-Clause
"""Actual observer bodies for the opt-in16-byte service retirement profile."""
import subprocess
import unittest

import test_openzfs_write_lifetimes as original
from openzfs_fs_lifetime import service_lifetime_hooks, service_lifetime_record

ROOT, OWNED = original.ROOT, original.OWNED


class ServiceLifetime(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prior = original.WriteLifetimes
        cls.prior.setUpClass()
        cls.addClassCleanup(cls.prior.doClassCleanups)
        cls.flow = service_lifetime_record((OWNED / 'pool-lifetime.inc').read_text())
        cls.hooks = service_lifetime_hooks((OWNED / 'pool-vdev-hooks.inc').read_text())
        cls.binary = cls.compile(cls.flow, 'service16')

    @classmethod
    def compile(cls, flow, name, size=16):
        out = cls.prior.base.base.output
        (out / 'pool-vdev-hooks.inc').write_text(cls.hooks)
        (out / 'pool-service-lifetime.inc').write_text(flow)
        fixture = (ROOT / 'tests/fixtures/openzfs_pool_lifetime.c').read_text()
        fixture = fixture.replace('aether_pool_lifetime_retire', 'aether_pool_service16_retire')
        fixture = fixture.replace('4096', str(size))
        source = out / 'service16-fixture.c'
        source.write_text(fixture)
        binary = out / name
        sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        result = subprocess.run([
            '/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-std=gnu11',
            '-O2', '-Wall', '-Wextra', '-Werror', '-pthread', '-isysroot', sdk,
            '-I' + str(out), '-I' + str(OWNED), '-I' + str(ROOT / 'tests/fixtures'),
            str(OWNED / 'pool-witness.c'), str(source), '-o', str(binary),
        ], capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        return binary

    def run_mode(self, mode, binary=None, expected=0):
        result = subprocess.run([str(binary or self.binary), str(mode)],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        if expected:
            self.assertIn('pool hook rejection:', result.stderr)
        return result

    def test_actual_eight_and64_reuse_stays_within_original_budget(self):
        result = self.run_mode(0)
        self.assertIn('observer bytes=7596 records=1 completed=8', result.stdout)
        self.run_mode(75)

    def test_original_pins_graph_requests_wait_stale_failure_and_overflow_cases(self):
        for mode in range(1, 75):
            if mode == 72:
                continue
            with self.subTest(mode=mode):
                self.run_mode(mode)

    def test_wrong_profile_staging_rejects_both_directions(self):
        self.run_mode(0, self.compile(self.flow, 'service16-wrong4096', 4096), 1)
        legacy = (OWNED / 'pool-lifetime.inc').read_text().replace(
            'aether_pool_lifetime_retire', 'aether_pool_service16_retire')
        self.run_mode(0, self.compile(legacy, 'legacy4096-wrong16'), 1)

    def test_exact_derivation_rejects_drift_duplicates_or_an_already_selected_body(self):
        source = (OWNED / 'pool-lifetime.inc').read_text()
        for changed in (source + '\n', source + source, self.flow,
                        source.replace('operation_error || !target', '!target', 1)):
            with self.subTest(changed=changed[:30]):
                with self.assertRaisesRegex(ValueError, 'source identity'):
                    service_lifetime_record(changed)
        hooks = (OWNED / 'pool-vdev-hooks.inc').read_text()
        for changed in (hooks + hooks, hooks.replace('#include "pool-flow.inc"', '')):
            with self.assertRaises(ValueError):
                service_lifetime_hooks(changed)

    def test_actual_compiling_failed_disposition_epoch_and_counter_omissions_fail(self):
        variants = [
            ('error', 'operation_error || !target', '!target', 41),
            ('epoch', 'index != atomic_load(&pool_epoch)', '((void)index,0)', 57),
            ('counter', 'atomic_fetch_add(&pool_completed, 1);', '(void)0;', 0),
        ]
        for name, old, new, mode in variants:
            with self.subTest(name=name):
                self.assertEqual(self.flow.count(old), 1)
                self.run_mode(mode, self.compile(self.flow.replace(old, new, 1), name), 1)

    def test_same_layout_distinct_entry_and_explicit_opt_in_preserve_default_api(self):
        self.assertIn('int aether_pool_service16_retire(', self.flow)
        self.assertNotIn('int aether_pool_lifetime_retire(', self.flow)
        self.assertIn('staged != 4096', (OWNED / 'pool-lifetime.inc').read_text())
        self.assertIn('int aether_pool_lifetime_retire(', (OWNED / 'pool-lifetime.h').read_text())
        import inspect
        import openzfs_volume as volume
        import openzfs_elapsed as elapsed
        import service_runtime_smoke as runtime
        for function, option in ((volume.build, 'pool_fs_lifetimes'),
                                 (elapsed.prepare, 'volume_fs_lifetimes'),
                                 (runtime.suite, '_zpl_fs_lifetimes')):
            self.assertIs(inspect.signature(function).parameters[option].default, False)
        builder = (ROOT / 'scripts/openzfs_volume.py').read_text()
        self.assertIn('if pool_fs_lifetimes:', builder)
        self.assertIn('hook_source = service_lifetime_hooks', builder)


if __name__ == '__main__':
    unittest.main()
