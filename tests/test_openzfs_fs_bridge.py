# SPDX-License-Identifier: BSD-2-Clause
"""Pinned Rust intake and actual C adaptation; doubles do not qualify Rust or media."""
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
import openzfs_fs_bridge as bridge
import openzfs_volume as volume
import openzfs_elapsed as elapsed
import service_runtime_smoke as runtime
import zpl_pair as pair
import test_zpl_pair as controls

DELIVERY = ROOT / 'userland/build/service-deliveries/filesystem-bridge-2026-10-18-v1'


class BridgeIntake(unittest.TestCase):
    def test_real_delivery_and_all_consumed_inputs_recheck(self):
        selected = bridge.intake(DELIVERY)
        bridge.recheck(selected)
        self.assertEqual(selected['manifest_sha256'], bridge.SEAL)
        self.assertNotEqual(selected['builder_provenance'], selected['adaptation_builders'])
        self.assertGreater(len(selected['inputs']), 320)
        changed = copy.deepcopy(selected)
        changed['inputs'][selected['object']] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'consumed input drift'):
            bridge.recheck(changed)
        changed['manifest_sha256'] = '0' * 64
        with self.assertRaises(ValueError): bridge.recheck(changed)

    def test_member_drift_extra_and_symlink_reject(self):
        with tempfile.TemporaryDirectory(prefix='aether-bridge-intake-') as directory:
            target = Path(directory).resolve() / 'delivery'
            shutil.copytree(DELIVERY, target)
            selected = bridge.intake(target)
            member = target / 'source/native-probe.rs'
            original = member.read_bytes()
            member.write_bytes(original + b'\n')
            with self.assertRaisesRegex(ValueError, 'member identity'): bridge.intake(target)
            member.write_bytes(original)
            extra = target / 'extra'; extra.write_bytes(b'x')
            with self.assertRaisesRegex(ValueError, 'closure'): bridge.intake(target)
            extra.unlink()
            member.unlink(); member.symlink_to(DELIVERY / 'source/native-probe.rs')
            with self.assertRaises(ValueError): bridge.intake(target)
            with self.assertRaisesRegex(ValueError, 'consumed input drift'): bridge.recheck(selected)
            alias = Path(directory) / 'alias'; alias.symlink_to(DELIVERY)
            with self.assertRaisesRegex(ValueError, 'real delivery'): bridge.intake(alias)
            seal = target / 'SHA256SUMS'; seal.write_bytes(b'drift')
            with self.assertRaisesRegex(ValueError, 'manifest'): bridge.intake(target)

    def test_partial_symbol_origins_are_required_and_not_duplicates(self):
        symbols = ['aether_fs_policy_write_probe', 'aether_zpl_open_write',
                   'aether_zpl_close', 'aether_zpl_root', 'aether_zpl_lookup',
                   'aether_zpl_read', 'aether_zpl_write']
        lines = []
        for symbol in symbols:
            owner = 'filesystem-consumer.o' if symbol == symbols[0] else 'zpl-write.o'
            lines += [f'0 0 0 0 /selected/{owner}:(.text.{symbol})', f'0 0 0 0 {symbol}']
        text = '\n'.join(lines)
        self.assertEqual(len(bridge.partial_origins(text)), 7)
        for changed in (text.replace('filesystem-consumer.o', 'substitute.o'),
                        text.replace('zpl-write.o', 'other.o'),
                        '\n'.join(lines[:-1]), text + '\n' + lines[-1]):
            with self.assertRaises(ValueError): bridge.partial_origins(changed)

    def test_c_and_tool_drift_are_not_treated_as_builder_adaptation(self):
        original = bridge.sha
        for target in (ROOT / 'user/storage/openzfs-volume/zpl-write.h', Path('/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang')):
            def changed(path):
                return '0' * 64 if Path(path) == target else original(path)
            with self.subTest(target=str(target)), patch.object(bridge, 'sha', side_effect=changed):
                with self.assertRaisesRegex(ValueError, 'drift'): bridge.intake(DELIVERY)

    def test_prepared_bridge_cannot_move_to_reader_downgrade_or_mix_modes(self):
        fixture = controls.PairControls(); fixture.setUp(); self.addCleanup(fixture.doCleanups)
        root, builds = fixture.output, fixture.builds
        shutil.copytree(root / 'reader', root / 'baseline')
        builds['baseline'] = copy.deepcopy(builds['reader'])
        builds['baseline']['pool_zpl_recover'] = False
        builds['writer']['fs_bridge'] = bridge.intake(DELIVERY)
        builds['writer']['pool_zpl_writer_budget'] = True
        builds['writer']['commands'] = [{'argv': ['zig', 'build', '-Dnative-service-zpl-budget=true']}]
        builds['reader']['pool_recovery_writer_60s'] = True
        source = bridge.recovery_source((ROOT / 'user/storage/openzfs-volume/zpl-recovery.c').read_text(), True)
        builds['reader']['port'] = {'volume': {'namespace_objects': {
            'recovery-selected-source': hashlib.sha256(source.encode()).hexdigest()}}}
        with patch.object(runtime, 'sealed'):
            pair.verify_prepared(root, builds, writer_60s=True, writer_ticks_6000=True, filesystem_bridge=DELIVERY)
            for role in ('baseline', 'writer', 'reader'):
                changed = copy.deepcopy(builds)
                changed[role]['fs_bridge'] = None if role == 'writer' else builds['writer']['fs_bridge']
                with self.subTest(role=role), self.assertRaisesRegex(ValueError, 'bridge selection'):
                    pair.verify_prepared(root, changed, writer_60s=True, writer_ticks_6000=True, filesystem_bridge=DELIVERY)
            for options in ({'writer_ticks_6000': False}, {'repeated_writes': True}, {'sync_stages': True}):
                with self.assertRaisesRegex(ValueError, 'exclusive fixed-budget'):
                    pair.verify_prepared(root, builds, **({'writer_60s': True, 'writer_ticks_6000': True, 'filesystem_bridge': DELIVERY} | options))

    def test_invalid_profiles_and_mixed_cli_fail_before_intake(self):
        with patch.object(runtime, 'intake', side_effect=AssertionError('runtime intake')):
            with self.assertRaisesRegex(ValueError, 'exclusive paired'):
                runtime.suite(Path('/absent'), _zpl_fs_bridge=DELIVERY)
        with self.assertRaisesRegex(ValueError, 'filesystem bridge'):
            elapsed.prepare(Path('/absent'), None, volume_fs_bridge={})
        with self.assertRaisesRegex(ValueError, 'filesystem bridge'):
            volume.build(Path('/absent'), None, None, pool_fs_bridge={})
        with patch.object(bridge, 'intake', side_effect=AssertionError('bridge intake')):
            with self.assertRaisesRegex(ValueError, 'exclusive'):
                pair.pair(Path('/absent'), Path('/absent'), repeated_writes=True, filesystem_bridge=DELIVERY)
        for flag in ('--repeated-writes', '--stage-diagnostic', '--sync-stages'):
            result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/zpl_pair.py'),
                '--filesystem-bridge', str(DELIVERY), flag, '--delivery', '/absent',
                '--utc-delivery', '/absent'], capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 64, result.stderr)

    def test_three_case_dispatch_preserves_full_oracles_and_fixed_limits(self):
        fixture = controls.PairControls(); fixture.setUp(); self.addCleanup(fixture.doCleanups)
        result = fixture.execute(filesystem_bridge=str(DELIVERY), writer_60s=True, writer_ticks_6000=True)
        self.assertEqual(fixture.launched, ['baseline', 'writer', 'reader'])
        self.assertEqual([c['watchdog_seconds'] for c in result['cases']], [30, 60, 30])
        self.assertEqual([c['kernel_tick_limit'] for c in result['cases']], [3000, 6000, 3000])
        self.assertTrue(result['fresh_vm_readback_qualified'])
        for bad in (controls.serial().replace('phase=7', 'phase=6', 1),
                    controls.serial().replace('detail=0', 'detail=873', 1)):
            with self.assertRaises(ValueError):
                fixture.execute(filesystem_bridge=str(DELIVERY), writer_60s=True,
                                writer_ticks_6000=True, writer_text=bad)
            self.assertEqual(fixture.launched, ['baseline', 'writer'])


CALLBACK = r'''
#include "native-probe.h"
static int callbacks;
int aether_fs_policy_write_probe(struct spa *spa, aether_fs_probe_result *out)
{
    CHECK(!owned && closes == 1 && !callbacks++);
    aether_zpl_view *context = NULL;
    aether_zpl_write_result result = {0};
    unsigned char bytes[16];
    for (unsigned i = 0; i < sizeof(bytes); ++i) bytes[i] = (unsigned char)(17*i+91);
    int error = aether_zpl_open_write(spa, "testpool_zstd/x86_64", &context);
    if (!error) error = aether_zpl_write(context, 2, 47, 37, bytes, 16, 1234, 5678, &result);
    *out = (aether_fs_probe_result){result.txg, result.bytes_staged, result.state};
    aether_zpl_close(&context);
    if (mode == 19 && !error) error = EIO;
    return error;
}
#define clock_gettime probe_clock_gettime
#include "write-probe.inc"
int main(int argc, char **argv)
{
    CHECK(argc == 2); mode = atoi(argv[1]);
    uint64_t assigned = 99;
    int error = aether_pool_namespace_write(&pool, &assigned);
    CHECK((error == 0) == (mode == 0));
    CHECK(!owned && writes <= 1 && callbacks <= 1);
    CHECK(assigned == (writes && mode != 15 ? 42 : 0));
    if (error && mode != 9) {
        CHECK(diagnostic_count == 6 && diagnostic[0] == 'E');
        uint32_t observed = 0;
        for (unsigned i = 0; i < 4; ++i) observed |= (uint32_t)diagnostic[i+2] << (8*i);
        CHECK(observed == (uint32_t)error);
    } else CHECK(!diagnostic_count);
    if (!mode) CHECK(writes == 1 && callbacks == 1 && closes == 3 && reads == 382 && calls == 392);
    if (mode == 13 || mode == 19) CHECK(writes == 1 && callbacks == 1 && assigned == 42 && diagnostic[1] == 6);
    return 0;
}
'''


class BridgeProbe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-bridge-probe-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.out = Path(cls.temp.name)
        cls.seed = (ROOT / 'user/storage/openzfs-volume/zpl-write-probe.c').read_text()
        cls.body = '\n'.join(line for line in bridge.probe(cls.seed).splitlines() if not line.startswith('#include')) + '\n'
        prefix = (ROOT / 'tests/fixtures/openzfs_zpl_write_probe.c').read_text().split('#define clock_gettime probe_clock_gettime')[0]
        prefix = prefix.replace('    CHECK(owned && *out == &view);', '    if (!out || !*out) return;\n    CHECK(owned && *out == &view);')
        (cls.out / 'host.c').write_text(prefix + CALLBACK)
        cls.sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        cls.binary = cls.compile(cls.body, 'probe')

    @classmethod
    def compile(cls, body, name):
        (cls.out / 'write-probe.inc').write_text(body)
        binary = cls.out / name
        command = ['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-isysroot', cls.sdk,
                   '-std=gnu11', '-O2', '-Wall', '-Wextra', '-Werror', '-I' + str(cls.out),
                   '-I' + str(ROOT / 'user/storage/openzfs-volume'), '-I' + str(DELIVERY / 'source'),
                   str(cls.out / 'host.c'), '-o', str(binary)]
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        if result.returncode: raise RuntimeError(result.stdout + result.stderr)
        return binary

    def test_seed_drift_denied(self):
        with self.assertRaisesRegex(ValueError, 'original probe drift'): bridge.probe(self.seed + '\n')

    def test_success_and_contract_failures_preserve_lifetimes_and_progress(self):
        for mode in [0, *range(1, 8), *range(9, 20)]:
            with self.subTest(mode=mode):
                result = subprocess.run([str(self.binary), str(mode)], capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_every_392_api_failure_closes_without_retry_and_retains_txg(self):
        for mode in range(101, 493):
            with self.subTest(mode=mode):
                result = subprocess.run([str(self.binary), str(mode)], capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_compiling_lifetime_progress_and_full_readback_omissions_fail96(self):
        changes = [
            ('preclose', '        aether_zpl_close(&view);', '        if (0) aether_zpl_close(&view);', 0),
            ('callback', 'error = aether_fs_policy_write_probe(spa, &completion);', 'error = 0;', 0),
            ('duplicate', 'error = aether_fs_policy_write_probe(spa, &completion);', 'error = aether_fs_policy_write_probe(spa, &completion); if (!error) error = aether_fs_policy_write_probe(spa, &completion);', 0),
            ('fallback', 'error = aether_fs_policy_write_probe(spa, &completion);', '''error = aether_zpl_open_write(spa, "testpool_zstd/x86_64", &view);
        unsigned char direct[16];
        for (unsigned i=0; i<16; ++i) direct[i] = (unsigned char)(17*i+91);
        if (!error) error = aether_zpl_write(view, 2, 47, 37, direct, 16, 1234, 5678, &result);
        aether_zpl_close(&view);
        completion = (aether_fs_probe_result){result.txg, result.bytes_staged, result.state};''', 0),
            ('second-write', 'error = aether_fs_policy_write_probe(spa, &completion);', '''error = aether_fs_policy_write_probe(spa, &completion);
        unsigned char direct[16];
        for (unsigned i=0; i<16; ++i) direct[i] = (unsigned char)(17*i+91);
        if (!error) error = aether_zpl_open_write(spa, "testpool_zstd/x86_64", &view);
        if (!error) error = aether_zpl_write(view, 2, 47, 37, direct, 16, 1234, 5678, &result);
        aether_zpl_close(&view);''', 0),
            ('postopen', 'error = aether_zpl_open_write(spa, "testpool_zstd/x86_64", &view);', 'error = 0;', 0),
            ('progress', 'result.txg = completion.txg;', 'result.txg = 0;', 19),
            ('bytes', 'result.bytes_staged = completion.bytes_staged;', 'result.bytes_staged = 0;', 0),
            ('state', 'result.state = completion.state;', 'result.state = 0;', 0),
            ('assigned', '    *assigned = result.txg;', '    if (!error) *assigned = result.txg;', 19),
            ('readback', 'memcmp(actual, predicted, sizeof(actual))', '0', 18),
        ]
        for name, old, new, mode in changes:
            with self.subTest(name=name):
                # postopen matches the initial declaration too; choose the exact indented callback successor.
                body = self.body
                if name == 'postopen':
                    old = '        if (!error)\n            ' + old
                    new = '        if (!error)\n            ' + new
                self.assertEqual(body.count(old), 1)
                binary = self.compile(body.replace(old, new, 1), name)
                result = subprocess.run([str(binary), str(mode)], capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 96, result.stdout + result.stderr)
                self.assertIn('HOST ZPL PROBE oracle96', result.stderr)


if __name__ == '__main__': unittest.main()
