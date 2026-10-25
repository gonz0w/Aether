# SPDX-License-Identifier: BSD-2-Clause
"""Reader attribution preserves the original oracle; no guest acceptance here."""
import hashlib
import json
from pathlib import Path
import copy
import shutil
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
import test_zpl_pair as controls


MAIN = r'''
static unsigned char observed[6];
static unsigned observed_count;
void aether_engine_utc_phase(unsigned char value)
{
    CHECK(!owned && !handles && observed_count < 6);
    observed[observed_count++] = value;
}
#include "zpl-recovery.inc"
static unsigned expected_stage(void)
{
    if (mode >= 101) {
        unsigned call = mode - 100;
        return call == 1 ? 2 : call == 2 ? 3 : call == 3 ? 4 :
               call < 195 ? 5 : call == 195 ? 7 : call == 196 ? 8 : 9;
    }
    if (mode == 1) return 1;
    if (mode <= 4) return 3;
    if (mode <= 8) return 4;
    if (mode == 9) return 7;
    if (mode == 10) return 5;
    if (mode == 11) return 6;
    if (mode == 12) return 10;
    if (mode == 13 || mode == 14) return 11;
    if (mode == 15) return 13;
    if (mode == 16) return 14;
    if (mode == 17) return 15;
    return 12;
}
int main(int argc, char **argv)
{
    CHECK(argc == 2); mode = atoi(argv[1]);
    int error = aether_pool_namespace_recover(&pool);
    CHECK((error == 0) == (mode == 0));
    CHECK(!owned && !handles && closes == ((mode == 1 || mode == 101) ? 0 : 1));
    if (error) {
        CHECK(observed_count == 6 && observed[0] == 'E' && observed[1] == expected_stage());
        uint32_t code = 0;
        for (unsigned i=0; i<4; ++i) code |= (uint32_t)observed[2+i] << (8*i);
        CHECK(code == (uint32_t)error);
    } else CHECK(!observed_count && calls == 197 && position == 780248);
    return 0;
}
'''


class RecoveryDiagnostic(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-recovery-diagnostic-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.out = Path(cls.temp.name)
        cls.seed = (ROOT / 'user/storage/openzfs-volume/zpl-recovery.c').read_text()
        cls.body = '\n'.join((line for line in bridge.recovery_probe(cls.seed).splitlines() if not line.startswith('#include'))) + '\n'
        prefix = (ROOT / 'tests/fixtures/openzfs_zpl_recovery.c').read_text().split('#include "zpl-recovery.inc"')[0]
        (cls.out / 'host.c').write_text(prefix + MAIN)
        oracle = json.loads((ROOT / 'docs/evidence/zpl-recovery-oracle-2026-10-18.json').read_text())
        value = oracle['oracle']['expected_sha256']
        cls.hash_bytes = ','.join(('0x' + value[i:i + 2] for i in range(0, 64, 2)))
        cls.sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        cls.binary = cls.compile(cls.body, 'probe')

    @classmethod
    def compile(cls, body, name):
        (cls.out / 'zpl-recovery.inc').write_text(body)
        binary = cls.out / name
        result = subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-isysroot', cls.sdk, '-std=gnu11', '-O2', '-Wall', '-Wextra', '-Werror', '-DEXPECTED_HASH_BYTES=' + cls.hash_bytes, '-I' + str(cls.out), '-I' + str(ROOT / 'user/storage/openzfs-volume'), str(cls.out / 'host.c'), '-o', str(binary)], capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        return binary

    def test_original_denials_and_all197_api_failures_keep_cleanup_and_exact_stage(self):
        for mode in [*range(19), *range(101, 298)]:
            with self.subTest(mode=mode):
                result = subprocess.run([str(self.binary), str(mode)], capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_wrong_stage_errno_or_weakened_time_guard_fails98(self):
        for name, old, new, mode in (('missing', "aether_engine_utc_phase('E');", "if (0) aether_engine_utc_phase('E');", 16), ('stage', '*stage = 14;', '*stage = 13;', 16), ('errno', '(8 * i))', '(8 * i + 1))', 16), ('upper', 'mtime[0] > UINT64_C(1791290070)', 'mtime[0] > UINT64_C(1791290100)', 16), ('lower', 'mtime[0] < UINT64_C(1791290040)', '0', 15), ('nanos', 'mtime[1] >= 1000000000', '0', 17), ('hash', 'memcmp(digest, expected, sizeof(expected))', '((void)expected,0)', 11), ('close', 'aether_zpl_close(&view);', 'if (0) aether_zpl_close(&view);', 16)):
            with self.subTest(name=name):
                self.assertEqual(self.body.count(old), 1)
                binary = self.compile(self.body.replace(old, new, 1), name)
                result = subprocess.run([str(binary), str(mode)], capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 98, result.stdout + result.stderr)
                self.assertIn('HOST ZPL RECOVERY oracle98', result.stderr)

    def test_seed_drift_and_invalid_profile_reject_before_intake(self):
        with self.assertRaisesRegex(ValueError, 'original probe drift'):
            bridge.recovery_probe(self.seed + '\n')
        with patch.object(runtime, 'intake', side_effect=AssertionError('intake')):
            with self.assertRaisesRegex(ValueError, 'recovery diagnostic'):
                runtime.suite(Path('/absent'), _zpl_recovery_diagnostic=True)
        with self.assertRaisesRegex(ValueError, 'recovery diagnostic'):
            elapsed.prepare(Path('/absent'), None, volume_recovery_diagnostic=True)
        with self.assertRaisesRegex(ValueError, 'recovery diagnostic'):
            volume.build(Path('/absent'), None, None, pool_recovery_diagnostic=True)
        with self.assertRaisesRegex(ValueError, 'recovery diagnostic'):
            pair.pair(Path('/absent'), Path('/absent'), recovery_diagnostic=True)
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/zpl_pair.py'), '--recovery-diagnostic', '--delivery', '/absent', '--utc-delivery', '/absent'], capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 64)

    def test_prepared_diagnostic_cannot_be_omitted_or_moved_to_writer(self):
        fixture = controls.PairControls()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        root, builds = (fixture.output, fixture.builds)
        shutil.copytree(root / 'reader', root / 'baseline')
        builds['baseline'] = copy.deepcopy(builds['reader'])
        builds['baseline']['pool_zpl_recover'] = False
        delivery = ROOT / 'userland/build/service-deliveries/filesystem-bridge-2026-10-18-v1'
        builds['writer']['fs_bridge'] = bridge.intake(delivery)
        builds['writer']['pool_zpl_writer_budget'] = True
        builds['writer']['commands'] = [{'argv': ['zig', 'build', '-Dnative-service-zpl-budget=true']}]
        builds['reader']['pool_recovery_diagnostic'] = True
        builds['reader']['pool_recovery_writer_60s'] = True
        source = bridge.recovery_source(self.seed, True, True)
        builds['reader']['port'] = {'volume': {'namespace_objects': {
            'recovery-selected-source': hashlib.sha256(source.encode()).hexdigest()}}}
        with patch.object(runtime, 'sealed'):
            pair.verify_prepared(root, builds, writer_60s=True, writer_ticks_6000=True, filesystem_bridge=delivery, recovery_diagnostic=True)
            for role, value in (('reader', False), ('writer', True), ('baseline', True)):
                changed = copy.deepcopy(builds)
                changed[role]['pool_recovery_diagnostic'] = value
                with self.subTest(role=role), self.assertRaisesRegex(ValueError, 'profile or seal'):
                    pair.verify_prepared(root, changed, writer_60s=True, writer_ticks_6000=True, filesystem_bridge=delivery, recovery_diagnostic=True)
            with self.assertRaises(ValueError):
                pair.verify_prepared(root, builds, writer_60s=True, writer_ticks_6000=True, filesystem_bridge=delivery)

    def test_same25_row_error_decoder_identifies_exact_reader_predicate(self):
        tags = b'BIUVWLPabcdefghOAMTE' + bytes([14]) + bytes([5, 0, 0, 0])
        text = '\n'.join((f'NATIVE observation slot=0 generation=1 offset={i * 8} byte={b}' for i, b in enumerate(tags))) + '\n'
        text += 'NATIVE terminal slot=0 generation=1 kind=1 detail=873\n'
        text += 'NATIVE CLEANUP v=1 slot=0 generation=1 phase=1 selected=0 pages=8192 reclaimed=0\n'
        text += 'NATIVE CLEANUP v=1 slot=0 generation=1 phase=2 selected=2 pages=8192 reclaimed=0\n'
        text += 'NATIVE supervisor result=401 reclaimed=0\n'
        result = pair.decode_zpl_error(text, recovery=True)
        self.assertEqual((result['operation'], result['errno']), ('UTC-upper-bound', 5))
        for changed in (text + pair.MARKER, text.replace('byte=14', 'byte=16'), text.replace('offset=192', 'offset=200')):
            with self.assertRaises(ValueError):
                pair.decode_zpl_error(changed, recovery=True)
        with self.assertRaises(ValueError):
            pair.decode_zpl_error(text)
if __name__ == '__main__':
    unittest.main()
