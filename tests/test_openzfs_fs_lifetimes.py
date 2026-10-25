# SPDX-License-Identifier: BSD-2-Clause
"""Sealed lifetime service, exact profile admission and original outer C oracles."""
import ast
import copy
import hashlib
import re
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import test_openzfs_fs_service as old
import openzfs_fs_service as service
import openzfs_volume as volume
import openzfs_elapsed as elapsed
import service_runtime_smoke as runtime
import zpl_pair as pair

ROOT = old.ROOT
DELIVERY = ROOT / 'userland/build/service-deliveries/filesystem-service-lifetimes-2026-10-20-v1'


class LifetimesIntake(unittest.TestCase):
    def test_emitted_commands_and_consumed_sources_gate_all_four_profiles(self):
        def statement(module, marker):
            return next(node for node in ast.walk(ast.parse(Path(module.__file__).read_text()))
                        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
                        and isinstance(node.value.func, ast.Name) and node.value.func.id == 'command'
                        and marker in ast.unparse(node))
        driver = statement(runtime, 'link-arg=--oformat=binary')
        partial = statement(elapsed, 'bridge-partial.map')
        for case in service.CASES:
            helper = old.ServiceIntake()
            self.addCleanup(helper.doCleanups)
            f = helper.fixture()
            selected = service.intake(DELIVERY, True)
            writer = f.builds['writer']
            writer.update(fs_service=selected, fs_service_lifetimes=True, fs_service_case=case)
            source = ROOT / 'user/storage/openzfs-volume'
            objects = writer['port']['volume']['namespace_objects']
            objects['fs-service-consumer'] = service.sha(selected['object'])
            objects['fs-service-probe-source'] = hashlib.sha256(service.probe(
                (source / 'zpl-write-probe.c').read_text(), case, True).encode()).hexdigest()
            from openzfs_fs_lifetime import service_lifetime_hooks, service_lifetime_record
            for name, function, filename in (
                    ('service-lifetime-hooks-source', service_lifetime_hooks, 'pool-vdev-hooks.inc'),
                    ('service-lifetime-record-source', service_lifetime_record, 'pool-lifetime.inc')):
                objects[name] = hashlib.sha256(function((source / filename).read_text()).encode()).hexdigest()
            writer['port']['fs_service_origins'] = {'aether_pool_service16_retire': '/native/vdev-selected.o'}
            if case != 'lost-reply':
                reader = f.builds['reader']
                reader['fs_service_lifetimes'] = True
                reader['port']['volume']['namespace_objects']['recovery-selected-source'] = hashlib.sha256(
                    service.lifetime_recovery((source / 'zpl-recovery.c').read_text()).encode()).hexdigest()
            emitted = []
            def command(argv, log):
                emitted.append(list(map(str, argv)))
            scope = {node.id: False for node in ast.walk(driver)
                     if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)}
            scope.update(command=command, str=str, volume_readonly=runtime.volume_readonly,
                SOURCE=runtime.SOURCE, name='pool-import', namespace_ipc=True,
                service_case=service.case_number(case), service=selected, _zpl_fs_lifetimes=True, _zpl_fs_namespace=None,
                volume=True, engine_native=True, pool_create=True, pool_zpl_write=True,
                WRITE_CASES=runtime.WRITE_CASES, driver_source=f.output/'writer/supervisor.rs',
                dest=f.output/'writer')
            exec(compile(ast.Module(body=[driver], type_ignores=[]), '<actual driver>', 'exec'), scope)
            scope = dict(command=command, tool='ld.lld', service_case=service.case_number(case),
                volume_fs_bridge=None, volume_fs_service=selected, output=f.output/'writer', base=[])
            exec(compile(ast.Module(body=[partial], type_ignores=[]), '<actual partial>', 'exec'), scope)
            writer['commands'] = writer['commands'][:1] + [{'argv': argv} for argv in emitted]
            def verify():
                with patch.object(runtime, 'sealed'):
                    pair.verify_prepared(f.output, f.builds, writer_ticks_6000=True,
                        writer_60s=True, recovery_diagnostic=True, filesystem_service=DELIVERY,
                        filesystem_service_case=case, filesystem_service_lifetimes=True)
            verify()
            for field in ('service-lifetime-hooks-source', 'service-lifetime-record-source'):
                saved = objects[field]
                objects[field] = '0' * 64
                with self.assertRaisesRegex(ValueError, 'observer/origin'):
                    verify()
                objects[field] = saved
            writer['commands'][1]['argv'].remove('fs_eight_writes')
            with self.assertRaisesRegex(ValueError, 'driver/wrap'):
                verify()

    def test_exact_new_candidate_and_profile_cannot_cross_or_forge_the_old_selection(self):
        selected = service.intake(DELIVERY, True)
        service.recheck(selected)
        self.assertEqual(selected['manifest_sha256'], service.LIFETIMES_SEAL)
        self.assertTrue(selected['lifetimes'])
        for directory, flag in ((DELIVERY, False), (old.DELIVERY, True)):
            with self.assertRaisesRegex(ValueError, 'manifest identity'):
                service.intake(directory, flag)
        for field in ('lifetimes', 'object', 'inputs'):
            changed = copy.deepcopy(selected)
            changed[field] = False if field == 'lifetimes' else str(DELIVERY / 'source/owner.rs') if field == 'object' else {}
            with self.assertRaises(ValueError):
                service.recheck(changed)

    def test_independent_pristine_file_predicts_all_eight_splices_and_reader_constant(self):
        original = (ROOT / '.deps/openzfs-namespace-reference-v1/zstd.bin').read_bytes()
        self.assertEqual(len(original), 780248)
        self.assertEqual(hashlib.sha256(original).hexdigest(), 'cc9bfddedd664b9a5334581af786516d149c3fbd2c7e65735985acf17bce5935')
        expected = bytearray(original)
        expected[37:165] = bytes((i * 17 + 91) % 256 for i in range(128))
        self.assertEqual(hashlib.sha256(expected).hexdigest(), service.LIFETIMES_DIGEST)
        text = service.lifetime_recovery((ROOT / 'user/storage/openzfs-volume/zpl-recovery.c').read_text())
        array = text.split('static const unsigned char expected[32]', 1)[1].split('};', 1)[0]
        self.assertEqual(bytes(int(value, 16) for value in re.findall(r'0x([0-9a-f]{2})', array)).hex(), service.LIFETIMES_DIGEST)
        seed = (ROOT / 'user/storage/openzfs-volume/zpl-write-probe.c').read_text()
        self.assertIn('ZPL_PROBE_OFFSET + 128)', service.probe(seed, 'normal', True))
        self.assertNotIn('ZPL_PROBE_OFFSET + 128)', service.probe(seed, 'lost-reply', True))

    def test_invalid_selector_or_wrong_role_stops_before_any_build(self):
        for bad in (1, 'yes', True):
            with self.subTest(selector=bad):
                with self.assertRaisesRegex(ValueError, 'lifetimes'):
                    volume.build(Path('/absent'), None, None, pool_fs_lifetimes=bad)
                with self.assertRaisesRegex(ValueError, 'lifetimes'):
                    elapsed.prepare(Path('/absent'), None, volume_fs_lifetimes=bad)
                with patch.object(runtime, 'intake', side_effect=AssertionError('runtime intake')):
                    with self.assertRaisesRegex(ValueError, 'lifetimes'):
                        runtime.suite(Path('/absent'), _zpl_fs_lifetimes=bad)
        with self.assertRaisesRegex(ValueError, 'lifetimes'):
            pair.pair(Path('/absent'), Path('/absent'), filesystem_service_lifetimes=True)

    def test_actual_primitive_origin_is_required_in_addition_to_original_c_and_rust(self):
        symbols = {'aether_fs_service_run': 'filesystem-service.o',
                   'aether_pool_service16_retire': 'vdev-selected.o'}
        symbols.update({name: 'zpl-write.o' for name in ('aether_zpl_open_write',
            'aether_zpl_close', 'aether_zpl_root', 'aether_zpl_lookup',
            'aether_zpl_read', 'aether_zpl_write')})
        lines = []
        for name, obj in symbols.items():
            lines += [f'0 0 0 0 /selected/{obj}:(.text.{name})', f'0 0 0 0 {name}']
        mapping = '\n'.join(lines)
        self.assertEqual(len(service.partial_origins(mapping, lifetimes=True)), 8)
        for bad in (mapping.replace('vdev-selected.o', 'wrong.o'),
                    mapping.replace('aether_pool_service16_retire', 'absent')):
            with self.assertRaises(ValueError):
                service.partial_origins(bad, lifetimes=True)


class LifetimeOuterProbe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prior = old.ServiceProbe
        cls.prior.setUpClass()
        cls.addClassCleanup(cls.prior.doClassCleanups)
        cls.out = cls.prior.out
        cls.seed = cls.prior.seed
        cls.owner = '\n'.join(line for line in (ROOT / 'user/storage/openzfs-volume/fs-service-owner.inc').read_text().splitlines() if not line.startswith('#include'))
        cls.binaries = {}
        for case in range(4):
            body = '\n'.join(line for line in service.probe(cls.seed, service.CASES[case], True).splitlines() if not line.startswith('#include'))
            cls.binaries[case] = cls.compile(cls.owner + '\n' + body, 'lifetime-case-' + str(case), case)

    @classmethod
    def compile(cls, body, name, case):
        prefix = cls.prior.prefix.replace('offset < 53', 'offset < 37 + FS_TEST_WRITES * 16')
        prefix = prefix.replace('offset == 37 && length == 16 && !writes', 'offset == 37u + (unsigned)writes * 16u && length == 16 && writes < FS_TEST_WRITES')
        prefix = prefix.replace('pattern(37 + i, 1)', 'pattern(37 + writes * 16 + i, 1)')
        prefix = prefix.replace('{42, 16, AETHER_ZPL_COMMITTED}', '{42 + writes, 16, AETHER_ZPL_COMMITTED}')
        prefix = prefix.replace('mode == 15 ? 0 : 42,', 'mode == 15 ? 0 : 41 + writes,')
        if case == 3:
            prefix = '#define aether_zpl_close fixture_original_close\n' + prefix + r'''
#undef aether_zpl_close
static int callbacks, injected_closes;
extern void __wrap_aether_zpl_close(aether_zpl_view **);
void __real_aether_zpl_close(aether_zpl_view **v) { fixture_original_close(v); }
static int64_t host_channel_close(uint64_t cap) { CHECK(!owned && callbacks == 1 && (closes == FS_TEST_WRITES + 2 || (mode >= 101 && closes == FS_TEST_WRITES + 1)) && cap == 0x10001 && !injected_closes++); return mode == 28 ? -5 : 0; }
#define AETHER_FS_HOST_CLOSE host_channel_close
#define aether_zpl_close __wrap_aether_zpl_close
'''
        fake = old.FAKE
        begin = fake.index('    unsigned char bytes[16];')
        end = fake.index('    if (mode == 19', begin)
        fake = fake[:begin] + r'''
    int error = 0;
    for (unsigned part = 0; part < FS_TEST_WRITES && !error; ++part) {
        unsigned char bytes[16];
        for (unsigned i = 0; i < 16; ++i) bytes[i] = (unsigned char)(17*(16*part+i)+91);
        error = aether_zpl_open_write(spa, "testpool_zstd/x86_64", &context);
        if (!error) error = aether_zpl_write(context, 2, 47, 37+part*16, bytes, 16, 1234, 5678, &result);
        if (context) aether_zpl_close(&context);
        if (result.state != 2 || result.bytes_staged != 16 || !result.txg) break;
    }
    if (!error && writes == FS_TEST_WRITES && result.state == 2 && result.bytes_staged == 16 && result.txg) {
        error = aether_zpl_open_write(spa, "testpool_zstd/x86_64", &context);
        if (context) aether_zpl_close(&context);
    }
    *out = (struct aether_fs_service_result){.ready=1, .requests=7+4*FS_TEST_WRITES, .txg=result.txg, .bytes_staged=result.bytes_staged, .state=result.state};
''' + fake[end:]
        fake = fake.replace('out->requests = 10;', 'out->requests = 6+4*FS_TEST_WRITES;')
        fake = fake.replace('writes <= 1', 'writes <= FS_TEST_WRITES')
        fake = fake.replace('mode != 15 ? 42 : 0', 'mode != 15 ? 41u+(unsigned)writes : 0u')
        fake = fake.replace('    if (!mode) CHECK(writes == 1 && callbacks == 1 && closes == 3 && reads == 382 && calls == 392);',
            '    if (!mode) { CHECK(writes == FS_TEST_WRITES && callbacks == 1 && closes == FS_TEST_WRITES+3 && reads == 382); printf("CALLS=%d\\n",calls); }')
        fake = fake.replace('CHECK(writes == 1 && callbacks == 1 && assigned == 42 && diagnostic[1] == 6);',
            'CHECK(writes > 0 && callbacks == 1 && assigned == 41u+(unsigned)writes && diagnostic[1] == 6);')
        (cls.out / 'host.c').write_text('#define AETHER_FS_SERVICE_LIFETIMES 1\n#define AETHER_FS_SERVICE_CASE ' + str(case) + '\n#define FS_TEST_WRITES ' + str(1 if case == 1 else 8) + '\n' + prefix + fake)
        (cls.out / 'write-probe.inc').write_text(body)
        binary = cls.out / name
        command = ['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-isysroot', cls.prior.sdk,
            '-std=gnu11', '-O2', '-Wall', '-Wextra', '-Werror', '-I' + str(cls.out),
            '-I' + str(ROOT / 'user/storage/openzfs-volume'), '-I' + str(DELIVERY / 'source'),
            str(cls.out / 'host.c'), '-o', str(binary)]
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        return binary

    def run_mode(self, case, mode, binary=None, expected=0):
        result = subprocess.run([str(binary or self.binaries[case]), str(mode)], capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        if expected:
            self.assertIn('oracle96', result.stderr)
        return result

    def test_actual_outer_stream_metadata_eof_progress_and_all_reachable_api_failures(self):
        for case in range(4):
            result = self.run_mode(case, 0)
            calls = int(result.stdout.split('CALLS=')[1].split()[0])
            for mode in [*range(1, 8), *range(9, 26), *range(101, 101 + calls), *([28] if case == 3 else [])]:
                with self.subTest(case=case, mode=mode):
                    self.run_mode(case, mode)

    def test_compiling_wrong_full_span_or_missing_last_close_injection_fails96(self):
        body = '\n'.join(line for line in service.probe(self.seed, 'normal', True).splitlines() if not line.startswith('#include'))
        self.assertIn('ZPL_PROBE_OFFSET + 128)', body)
        wrong = body.replace('ZPL_PROBE_OFFSET + 128)', 'ZPL_PROBE_OFFSET + 16)', 1)
        self.run_mode(0, 0, self.compile(self.owner + '\n' + wrong, 'wrong-span', 0), 96)
        body = '\n'.join(line for line in service.probe(self.seed, 'close-failure', True).splitlines() if not line.startswith('#include'))
        self.assertEqual(self.owner.count('if (fs_close_reader)'), 1)
        missing = self.owner.replace('if (fs_close_reader)', 'if (0)', 1)
        self.run_mode(3, 0, self.compile(missing + '\n' + body, 'no-last-injection', 3), 96)


if __name__ == '__main__':
    unittest.main()
