# SPDX-License-Identifier: BSD-2-Clause
"""Fixed writer UTC horizons; compiled C doubles do not qualify native media."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import openzfs_fs_bridge as bridge
import openzfs_volume as volume
import openzfs_elapsed as elapsed
import service_runtime_smoke as runtime
import zpl_pair as pair
import test_zpl_tick_budget as controls


MAIN = r'''
static unsigned char observed[6];
static unsigned observed_count;
void aether_engine_utc_phase(unsigned char value)
{
    CHECK(!owned && !handles && observed_count < 6);
    observed[observed_count++] = value;
}
#include "zpl-recovery.inc"
int main(int argc, char **argv)
{
    CHECK(argc == 5);
    supplied_seconds = strtoull(argv[1], NULL, 10);
    supplied_nanos = strtoull(argv[2], NULL, 10);
    mode = atoi(argv[3]);
    int expected = atoi(argv[4]);
    int error = aether_pool_namespace_recover(&pool);
    CHECK((error == 0) == expected);
    CHECK(!owned && !handles && closes == ((mode == 1 || mode == 101) ? 0 : 1));
    if (!error) CHECK(position == 780248 && calls == 197 && !observed_count);
    if (observed_count) {
        CHECK(error && observed_count == 6 && observed[0] == 'E');
        uint32_t code = 0;
        for (unsigned i = 0; i < 4; ++i) code |= (uint32_t)observed[2+i] << (8*i);
        CHECK(code == (uint32_t)error);
    }
    return 0;
}
'''


class RecoveryWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-recovery-window-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.out = Path(cls.temp.name)
        cls.seed = (ROOT / 'user/storage/openzfs-volume/zpl-recovery.c').read_text()
        prefix = (ROOT / 'tests/fixtures/openzfs_zpl_recovery.c').read_text().split('#include "zpl-recovery.inc"')[0]
        prefix = prefix.replace('static int mode,', 'static uint64_t supplied_seconds, supplied_nanos;\nstatic int mode,')
        prefix = prefix.replace('p[0] = 1791290041;', 'p[0] = supplied_seconds;').replace('p[1] = 12345;', 'p[1] = supplied_nanos;')
        oracle = json.loads((ROOT / 'docs/evidence/zpl-recovery-oracle-2026-10-18.json').read_text())
        value = oracle['oracle']['expected_sha256']
        hash_bytes = ','.join('0x' + value[i:i+2] for i in range(0, 64, 2))
        sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        cls.binaries = {}
        for extended in (False, True):
            for diagnostic in (False, True):
                source = bridge.recovery_source(cls.seed, extended, diagnostic)
                body = '\n'.join(line for line in source.splitlines() if not line.startswith('#include'))
                (cls.out / 'zpl-recovery.inc').write_text(body + '\n')
                # Existing mode16 must remain just outside the selected contract.
                (cls.out / 'host.c').write_text(prefix.replace('p[0] = 1791290071;',
                    'p[0] = 1791290101;' if extended else 'p[0] = 1791290071;') + MAIN)
                binary = cls.out / f'window-{extended}-{diagnostic}'
                result = subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang',
                    '-isysroot', sdk, '-std=gnu11', '-O2', '-Wall', '-Wextra', '-Werror',
                    '-DEXPECTED_HASH_BYTES=' + hash_bytes, '-I' + str(cls.out),
                    '-I' + str(ROOT / 'user/storage/openzfs-volume'), str(cls.out / 'host.c'),
                    '-o', str(binary)], capture_output=True, text=True, timeout=30)
                if result.returncode:
                    raise RuntimeError(result.stdout + result.stderr)
                cls.binaries[extended, diagnostic] = binary

    def run_case(self, binary, seconds, nanos, mode, expected):
        result = subprocess.run([str(binary), str(seconds), str(nanos), str(mode), str(int(expected))],
                                capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_independent_inclusive_endpoints_and_just_outside_each_writer_window(self):
        for (extended, diagnostic), binary in self.binaries.items():
            for seconds, short_ok, long_ok in (
                    (1791290039, False, False), (1791290040, True, True),
                    (1791290070, True, True), (1791290071, False, True),
                    (1791290100, False, True), (1791290101, False, False)):
                with self.subTest(extended=extended, diagnostic=diagnostic, seconds=seconds):
                    self.run_case(binary, seconds, 999999999, 0, long_ok if extended else short_ok)
            self.run_case(binary, 1791290040, 1000000000, 0, False)

    def test_all_existing_metadata_hash_eof_and197_api_denials_preserve_cleanup(self):
        for key, binary in self.binaries.items():
            for mode in [*range(1, 19), *range(101, 298)]:
                with self.subTest(profile=key, mode=mode):
                    self.run_case(binary, 1791290041, 12345, mode, False)

    def test_default_bytes_seed_identity_and_invalid_selectors(self):
        self.assertEqual(bridge.recovery_source(self.seed), self.seed)
        self.assertEqual(bridge.recovery_source(self.seed, diagnostic=True), bridge.recovery_probe(self.seed))
        old = 'mtime[0] > UINT64_C(1791290070)'
        selected = bridge.recovery_source(self.seed, True)
        expected = self.seed.replace(old, 'mtime[0] > UINT64_C(1791290100)', 1).replace(
            'unchanged30-second watchdog', 'selected60-second writer watchdog')
        self.assertEqual(selected, expected)
        for value in (30, 60, None, 'true'):
            with self.assertRaises(ValueError):
                bridge.recovery_source(self.seed, value)
        with self.assertRaisesRegex(ValueError, 'original probe drift'):
            bridge.recovery_source(self.seed + '\n', True)
        for function, kwargs in ((runtime.suite, {'_zpl_recovery_writer_60s': True}),
                                 (elapsed.prepare, {'volume_recovery_writer_60s': True}),
                                 (volume.build, {'pool_recovery_writer_60s': True})):
            args = (Path('/absent'),) if function == runtime.suite else (Path('/absent'), None) if function == elapsed.prepare else (Path('/absent'), None, None)
            with self.assertRaisesRegex(ValueError, 'recovery writer window'):
                function(*args, **kwargs)

    def test_pair_build_derives_window_from_watchdog_not_ticks_or_diagnostic(self):
        import shutil
        for extended, ticks in ((False, False), (True, False), (True, True)):
            selected = {}
            def build(*args, **kwargs):
                role = Path(kwargs['_zpl_stage']).name
                selected[role] = kwargs
                root = Path(tempfile.mkdtemp(prefix='thread-suite-service-runtime-test-', dir=ROOT / 'zig-out'))
                (Path(kwargs['_zpl_stage']).parent / (role + '-build.json')).write_text(
                    json.dumps({'output': str(root), 'report': {'status': 'pass'}}))
            with patch.object(runtime, 'suite', side_effect=build), patch.object(pair, 'execute_pair'):
                output = pair.pair(Path('/unused'), Path('/unused'), repeated_writes=True,
                                   txg_worker_diagnostic=True, sync_stages=True,
                                   writer_60s=extended, writer_ticks_6000=ticks)
            try:
                for role in ('baseline', 'writer', 'reader'):
                    self.assertIs(selected[role]['_zpl_recovery_writer_60s'], extended and role == 'reader')
                    self.assertIs(selected[role]['_zpl_writer_budget'], ticks and role == 'writer')
                report = json.loads((output / 'results.json').read_text())
                self.assertEqual(report['readonly_watchdog_seconds'], 30)
                self.assertEqual(report['readonly_kernel_tick_limit'], 3000)
                self.assertEqual(report['recovery_writer_window_seconds'], 60 if extended else 30)
            finally:
                shutil.rmtree(output)

    def test_prepared_horizon_and_source_cannot_downgrade_move_or_disagree(self):
        helper = controls.ZplTickBudget()
        f = helper.fixture()
        self.addCleanup(f.doCleanups)
        helper.verify(f)
        for role in ('baseline', 'writer', 'reader'):
            changed = copy.deepcopy(f.builds)
            changed[role]['pool_recovery_writer_60s'] = role != 'reader'
            with self.subTest(role=role), patch.object(runtime, 'sealed'), self.assertRaises(ValueError):
                pair.verify_prepared(f.output, changed, True, True, False, True, True, True, writer_60s=True)
        changed = copy.deepcopy(f.builds)
        changed['reader']['port']['volume']['namespace_objects']['recovery-selected-source'] = hashlib.sha256(self.seed.encode()).hexdigest()
        with patch.object(runtime, 'sealed'), self.assertRaisesRegex(ValueError, 'selected source'):
            pair.verify_prepared(f.output, changed, True, True, False, True, True, True, writer_60s=True)
        with patch.object(runtime, 'sealed'), self.assertRaisesRegex(ValueError, 'writer60'):
            pair.verify_prepared(f.output, f.builds, True, True, False, True, True, True)


if __name__ == '__main__':
    unittest.main()
