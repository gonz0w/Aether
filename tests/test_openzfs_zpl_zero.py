# SPDX-License-Identifier: BSD-2-Clause
"""Truncate-to-zero control/ownership oracles; API doubles are not native proof."""
import ast
import inspect
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import openzfs_zero as zero
import openzfs_fs_bridge as bridge
import openzfs_volume as volume
import openzfs_elapsed as elapsed
import service_runtime_smoke as runtime
import zpl_pair as pair
import test_zpl_pair as controls


class ZeroProbe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-zpl-zero-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.out = Path(cls.temp.name)
        cls.body = '\n'.join(line for line in (ROOT / 'user/storage/openzfs-volume/zpl-zero-probe.c').read_text().splitlines() if not line.startswith('#include')) + '\n'
        cls.sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        cls.binary = cls.compile(cls.body, 'zero')

    @classmethod
    def compile(cls, body, name):
        (cls.out / 'zero-probe.inc').write_text(body)
        binary = cls.out / name
        result = subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-isysroot', cls.sdk,
            '-std=gnu11', '-O2', '-Wall', '-Wextra', '-Werror', '-I' + str(cls.out),
            '-I' + str(ROOT / 'user/storage/openzfs-volume'), str(ROOT / 'tests/fixtures/openzfs_zpl_zero.c'),
            '-o', str(binary)], capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        return binary

    def test_success_and_denials_reopen_consume_and_retain_progress(self):
        for mode in range(20):
            with self.subTest(mode=mode):
                result = subprocess.run([str(self.binary), str(mode)], capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_all204_reachable_api_errors_stop_without_replay_and_balance_ownership(self):
        for mode in range(101, 305):
            with self.subTest(mode=mode):
                result = subprocess.run([str(self.binary), str(mode)], capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_compiling_omissions_fail_independent_oracle97(self):
        for name, old, new, mode in (
                ('hash', 'memcmp(digest, pristine, sizeof(digest))', '((void)pristine, 0)', 6),
                ('progress', '*assigned = result.txg;', '*assigned = 0;', 8),
                ('state', 'result.state != AETHER_ZPL_SYNCED', '0', 18),
                ('size', 'if (size ||', 'if (0 ||', 14),
                ('time', 'mtime[0] != (uint64_t)utc->tv_sec', '0', 17),
                ('former-eof', 'i < 2', 'i < 1', 13),
                ('close', '\n    aether_zpl_close(&view);\n', '\n    if (0) aether_zpl_close(&view);\n', 0)):
            with self.subTest(name=name):
                self.assertEqual(self.body.count(old), 1)
                binary = self.compile(self.body.replace(old, new, 1), name)
                result = subprocess.run([str(binary), str(mode)], capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 97, result.stdout + result.stderr)
                self.assertIn('HOST ZPL ZERO oracle97', result.stderr)


class ZeroRecovery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-zero-recovery-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.out = Path(cls.temp.name)
        seed = (ROOT / 'user/storage/openzfs-volume/zpl-recovery.c').read_text()
        cls.body = '\n'.join(line for line in zero.recovery(seed).splitlines() if not line.startswith('#include')) + '\n'
        prefix = (ROOT / 'tests/fixtures/openzfs_zpl_recovery.c').read_text().split('#include "zpl-recovery.inc"')[0]
        start = prefix.index('int aether_zpl_read(')
        end = prefix.index('static void SHA2Init', start)
        prefix = prefix[:start] + r'''int aether_zpl_read(aether_zpl_view *v, uint64_t obj, uint64_t gen,
                    uint64_t off, void *buf, size_t len, size_t *count)
{
    CHECK(v == &view && owned && obj == 2 && gen == 47 && len == 4096 && buf);
    CHECK(position < 2 && off == (position ? 780248 : 0));
    *count = 0;
    if (tick()) return EIO;
    if ((!position && mode == 9) || (position && mode == 10)) *count = 1;
    ++position;
    return 0;
}
''' + prefix[end:]
        start = prefix.index('static void SHA2Update')
        end = prefix.index('static void SHA2Final', start)
        prefix = prefix[:start] + prefix[end:]
        prefix = prefix.replace('(aether_zpl_node){2, 47, 780248,', '(aether_zpl_node){2, 47, 0,')
        prefix = prefix.replace('hash->count == 780248', 'hash->count == 0')
        prefix = prefix.replace('position == 780248', 'position == 2')
        prefix = prefix.replace('*p = mode == 12 ? 1 : 780248;', '*p = mode == 12 ? 1 : 0;')
        prefix = prefix.replace('p[0] = 1791290071;', 'p[0] = 1791290101;')
        main = r'''
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
    CHECK(argc == 2); mode = atoi(argv[1]);
    int error = aether_pool_namespace_recover(&pool);
    CHECK((error == 0) == (mode == 0));
    CHECK(!owned && !handles && closes == ((mode == 1 || mode == 101) ? 0 : 1));
    if (!error) CHECK(calls == 7 && position == 2 && !observed_count);
    else {
        CHECK(observed_count == 6 && observed[0] == 'E');
        uint32_t code = 0;
        for (unsigned i = 0; i < 4; ++i) code |= (uint32_t)observed[2+i] << (8*i);
        CHECK(code == (uint32_t)error);
        unsigned stage = mode >= 101 ?
            (mode == 101 ? 2 : mode == 102 ? 3 : mode == 103 ? 4 :
             mode <= 105 ? 7 : mode == 106 ? 8 : 9) :
            mode == 1 ? 1 : mode <= 4 ? 3 : mode <= 8 ? 4 :
            mode <= 10 ? 7 : mode == 11 ? 6 : mode == 12 ? 10 :
            mode <= 14 ? 11 : mode == 15 ? 13 : mode == 16 ? 14 :
            mode == 17 ? 15 : 12;
        CHECK(observed[1] == stage);
    }
    return 0;
}
'''
        (cls.out / 'host.c').write_text(prefix + main)
        cls.sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        cls.binary = cls.compile(cls.body, 'reader')

    @classmethod
    def compile(cls, body, name):
        (cls.out / 'zpl-recovery.inc').write_text(body)
        binary = cls.out / name
        value = ','.join('0x' + zero.EMPTY_SHA256[i:i+2] for i in range(0,64,2))
        result = subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-isysroot', cls.sdk,
            '-std=gnu11', '-O2', '-Wall', '-Wextra', '-Werror', '-DEXPECTED_HASH_BYTES=' + value,
            '-I' + str(cls.out), '-I' + str(ROOT / 'user/storage/openzfs-volume'),
            str(cls.out / 'host.c'), '-o', str(binary)], capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        return binary

    def test_empty_hash_two_eof_metadata_denials_and_seven_api_failures(self):
        for mode in [*range(19), *range(101,108)]:
            with self.subTest(mode=mode):
                result = subprocess.run([str(self.binary), str(mode)], capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_compiling_missing_former_eof_hash_time_or_close_fails98(self):
        for name, old, new, mode in (
                ('former-eof', 'aether_zpl_read(view, 2, 47, 780248, buffer, sizeof(buffer), &count)', '0', 10),
                ('hash', 'memcmp(digest, expected, sizeof(expected))', '((void)expected, 0)', 11),
                ('time', 'mtime[0] > UINT64_C(1791290100)', '0', 16),
                ('close', 'aether_zpl_close(&view);', 'if (0) aether_zpl_close(&view);', 0)):
            with self.subTest(name=name):
                self.assertEqual(self.body.count(old), 1)
                binary = self.compile(self.body.replace(old, new, 1), name)
                result = subprocess.run([str(binary), str(mode)], capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 98, result.stdout + result.stderr)
                self.assertIn('HOST ZPL RECOVERY oracle98', result.stderr)


class ZeroControls(unittest.TestCase):
    def test_invalid_profiles_and_cli_mixes_reject_before_intake(self):
        for function, args, kwargs in (
                (runtime.suite, (Path('/absent'),), {'_zpl_zero': True}),
                (elapsed.prepare, (Path('/absent'), None), {'volume_pool_zpl_zero': True}),
                (volume.build, (Path('/absent'), None, None), {'pool_zpl_zero': True}),
                (pair.pair, (Path('/absent'), Path('/absent')), {'truncate_zero': True, 'repeated_writes': True})):
            with self.assertRaisesRegex(ValueError, 'truncate zero'):
                function(*args, **kwargs)
        for flags in (['--repeated-writes'], ['--filesystem-bridge', '/absent'], ['--sync-stages']):
            result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/zpl_pair.py'),
                '--delivery', '/absent', '--utc-delivery', '/absent', '--truncate-zero', *flags],
                capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 64)

    def test_source_identity_default_and_fixed_empty_oracle(self):
        seed = (ROOT / 'user/storage/openzfs-volume/zpl-recovery.c').read_text()
        selected = zero.recovery(seed)
        self.assertEqual(zero.EMPTY_SHA256, hashlib.sha256(b'').hexdigest())
        self.assertIn('size != 0', selected)
        self.assertIn('file.size != 0', selected)
        self.assertIn('mtime[0] > UINT64_C(1791290100)', selected)
        self.assertIn('aether_zpl_read(view, 2, 47, 780248,', selected)
        self.assertIn('aether_zpl_read(view, 2, 47, 0,', selected)
        self.assertNotIn('while (!error', selected)
        self.assertEqual(bridge.recovery_source(seed), seed)
        with self.assertRaises(ValueError):
            zero.recovery(seed + '\n')

    def test_free_transaction_origins_cannot_be_missing_substituted_or_duplicate(self):
        node = ast.parse(inspect.getsource(runtime.check_engine_bindings)).body[0]
        # Execute the actual profile requirement construction, then independently
        # require the four original free APIs and exercise the real map validator.
        # Parsing/validation begins at the seen dictionary after requirements.
        stop = next(i for i, item in enumerate(node.body) if isinstance(item, ast.Assign) and
                    any(isinstance(t, ast.Name) and t.id == 'seen' for t in item.targets))
        scope = {name: parameter.default for name, parameter in inspect.signature(runtime.check_engine_bindings).parameters.items() if name != 'mapping'}
        scope.update(pool=True, pool_zpl_write=True, pool_namespace=True, pool_import=True, zpl_zero=True)
        exec(compile(ast.Module(body=node.body[:stop], type_ignores=[]), '<actual origin requirements>', 'exec'), scope)
        required = scope['required']
        names = ('aether_zpl_shrink', 'dmu_free_range', 'dmu_tx_hold_free', 'dmu_tx_mark_netfree')
        for name in names:
            self.assertEqual(required[name], 'selected-engine.o')
        self.assertNotIn('aether_zpl_write', required)
        mapping = '\n'.join('0 0 0 1 /private/' + owner + ':(.text)\n0 0 0 1 ' + name for name, owner in required.items())
        options = dict(pool=True, pool_zpl_write=True, pool_namespace=True, pool_import=True, zpl_zero=True)
        runtime.check_engine_bindings(mapping, **options)
        for name in names:
            for changed in (mapping.replace('0 0 0 1 ' + name, ''),
                            mapping.replace('/private/selected-engine.o:(.text)\n0 0 0 1 ' + name, '/private/forged.o:(.text)\n0 0 0 1 ' + name),
                            mapping + '\n0 0 0 1 /private/selected-engine.o:(.text)\n0 0 0 1 ' + name):
                with self.subTest(name=name), self.assertRaises(ValueError):
                    runtime.check_engine_bindings(changed, **options)

    def test_prepared_zero_selection_and_distinct_reader_source_required(self):
        f = controls.PairControls(); f.setUp(); self.addCleanup(f.doCleanups)
        shutil.copytree(f.output / 'reader', f.output / 'baseline')
        f.builds['baseline'] = copy.deepcopy(f.builds['reader'])
        f.builds['baseline']['pool_zpl_recover'] = False
        for role in ('writer', 'reader'):
            f.builds[role]['pool_zpl_zero'] = True
        f.builds['writer']['pool_zpl_writer_budget'] = True
        f.builds['writer']['commands'] = [{'argv': ['zig', 'build', '-Dnative-service-zpl-budget=true']}]
        f.builds['reader'].update(pool_recovery_writer_60s=True, pool_recovery_diagnostic=True)
        seed = (ROOT / 'user/storage/openzfs-volume/zpl-recovery.c').read_text()
        f.builds['reader']['port'] = {'volume': {'namespace_objects': {
            'recovery-selected-source': hashlib.sha256(zero.recovery(seed).encode()).hexdigest()}}}
        options = dict(writer_ticks_6000=True, recovery_diagnostic=True, writer_60s=True, truncate_zero=True)
        with patch.object(runtime, 'sealed'):
            pair.verify_prepared(f.output, f.builds, **options)
            for role in ('baseline', 'writer', 'reader'):
                changed = copy.deepcopy(f.builds)
                changed[role]['pool_zpl_zero'] = role == 'baseline'
                with self.subTest(role=role), self.assertRaises(ValueError):
                    pair.verify_prepared(f.output, changed, **options)
            changed = copy.deepcopy(f.builds)
            changed['reader']['port']['volume']['namespace_objects']['recovery-selected-source'] = hashlib.sha256(bridge.recovery_source(seed, True, True).encode()).hexdigest()
            with self.assertRaisesRegex(ValueError, 'selected source'):
                pair.verify_prepared(f.output, changed, **options)


if __name__ == '__main__':
    unittest.main()
