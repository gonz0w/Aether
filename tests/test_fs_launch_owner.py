# SPDX-License-Identifier: BSD-2-Clause
"""Actual launch lifecycle/import control flow, faults and compiling omissions."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SERVICE = ROOT / 'user/storage/service-runtime'
VOLUME = ROOT / 'user/storage/openzfs-volume'
DELIVERY = ROOT / 'userland/build/service-deliveries/filesystem-service-directories-2026-10-20-v1'


class LaunchOwner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-fs-launch-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.out = Path(cls.temp.name)
        cls.clang = '/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang'
        cls.sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        cls.bodies = {
            'engine': (SERVICE / 'filesystem-engine.c').read_text(),
            'import': '\n'.join(line for line in (VOLUME / 'filesystem-import.c').read_text().splitlines()
                                if not line.startswith('#include')) + '\n'}
        cls.binaries = {kind: cls.compile(kind, body, kind) for kind, body in cls.bodies.items()}

    @classmethod
    def compile(cls, kind, body, name):
        (cls.out / (kind + '-under-test.inc')).write_text(body)
        binary = cls.out / name
        args = [cls.clang, '-isysroot', cls.sdk, '-std=gnu11', '-O2', '-Wall', '-Wextra', '-Werror',
                '-I'+str(cls.out), '-I'+str(SERVICE), '-I'+str(VOLUME), '-I'+str(DELIVERY/'source'),
                '-I'+str(ROOT/'user/storage/openzfs-elapsed'),
                '-I'+str(ROOT/'.deps/native-service-runtime-v3/runtime'),
                '-I'+str(ROOT/'.deps/native-utc-v3/runtime'),
                str(ROOT/'tests/fixtures'/('filesystem_'+kind+'.c')), '-o', str(binary)]
        result = subprocess.run(args, capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        return binary

    def run_case(self, kind, *args, binary=None, expected=0):
        result = subprocess.run([str(binary or self.binaries[kind]), *map(str, args)],
                                capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, expected, result.stdout+result.stderr)
        if expected == 94:
            self.assertIn('oracle94', result.stderr)

    def test_actual_engine_lifecycle_each_fallible_stage_and_no_reentry(self):
        for fault in (0, 1, 2, 3, 4, 7, 8, 10, 11, 12, 20, 21, 23, 24, 25, 26, 28):
            with self.subTest(fault=fault): self.run_case('engine', fault)

    def test_actual_import_all_api_faults_metadata_and_readonly_clean_disconnect(self):
        for fault in range(9):
            with self.subTest(fault=fault): self.run_case('import', fault, 0)
        for mode in range(1, 14):
            with self.subTest(mode=mode): self.run_case('import', 0, mode)

    def test_compiling_omissions_fail_the_semantic_oracle(self):
        for kind, old, new, args in (
            ('engine', 'error = close_volume(grant);', 'error = 0;', (0,)),
            ('engine', 'error = aether_utc_close();', 'error = 0;', (0,)),
            ('engine', 'return service_error;', '(void)service_error; return 0;', (20,)),
            ('engine', 'if (consumed)', 'if (0)', (0,)),
            ('import', 'spa_close(spa, FTAG);', 'if (0) spa_close(spa, FTAG);', (0, 0)),
            ('import', 'dmu_buf_user_evict_wait();', 'if (0) dmu_buf_user_evict_wait();', (0, 0)),
            ('import', 'spa->spa_uberblock.ub_txg >= 782', '1', (0, 4)),
            ('import', 'return service_error;', '(void)service_error; return 0;', (0, 10)),
        ):
            with self.subTest(kind=kind, omission=old):
                self.assertEqual(self.bodies[kind].count(old), 1)
                # Keep removed static provider bodies typechecked under -Werror.
                changed = self.bodies[kind].replace(old, new, 1)
                if kind == 'engine' and 'close_volume' in old:
                    changed = changed.replace('error = 0;', 'error = ((void)close_volume, 0);', 1)
                binary = self.compile(kind, changed, 'omission')
                self.run_case(kind, *args, binary=binary, expected=94)


if __name__ == '__main__':
    unittest.main()
