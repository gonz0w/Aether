# SPDX-License-Identifier: BSD-2-Clause
"""Exact service intake, real C adaptation and guarded native composition."""
import ast
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
import openzfs_fs_service as service
import openzfs_volume as volume
import openzfs_elapsed as elapsed
import service_runtime_smoke as runtime
import zpl_pair as pair
import test_zpl_pair as controls

DELIVERY = ROOT / 'userland/build/service-deliveries/filesystem-service-2026-10-19-v1'


class ServiceIntake(unittest.TestCase):
    def test_exact_delivery_consumed_inputs_and_drift(self):
        selected = service.intake(DELIVERY)
        service.recheck(selected)
        self.assertEqual(selected['manifest_sha256'], service.SEAL)
        self.assertGreater(len(selected['inputs']), 340)
        for field in ('manifest_sha256', 'object', 'pointer', 'missing-hash'):
            changed = copy.deepcopy(selected)
            if field == 'manifest_sha256':
                changed[field] = '0' * 64
            elif field == 'object':
                changed['inputs'][changed[field]] = '0' * 64
            elif field == 'pointer':
                changed['object'] = str(DELIVERY / 'source/owner.rs')
            else:
                changed['inputs'] = {}
            with self.assertRaises(ValueError): service.recheck(changed)
        with tempfile.TemporaryDirectory(prefix='aether-service-intake-') as temp:
            target = Path(temp).resolve() / 'delivery'
            shutil.copytree(DELIVERY, target)
            for name, content in [('extra', b'x'), ('source/native-service.h', b'drift')]:
                member = target / name
                old = member.read_bytes() if member.exists() else None
                member.write_bytes(content)
                with self.assertRaises(ValueError): service.intake(target)
                if old is None: member.unlink()
                else: member.write_bytes(old)
            member = target / 'source/native-service.h'; member.unlink()
            member.symlink_to(DELIVERY / 'source/native-service.h')
            with self.assertRaises(ValueError): service.intake(target)
        original = service.sha
        for target in (ROOT / 'user/storage/openzfs-volume/zpl-write.h',
                       Path('/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang')):
            def drift(path): return '0' * 64 if Path(path) == target else original(path)
            with patch.object(service, 'sha', side_effect=drift), self.assertRaisesRegex(ValueError, 'drift'):
                service.intake(DELIVERY)

    def test_invalid_or_mixed_profiles_reject_before_any_build(self):
        with patch.object(runtime, 'intake', side_effect=AssertionError('runtime intake')):
            for kwargs in ({'_zpl_fs_service': DELIVERY},
                           {'_zpl_fs_service': DELIVERY, '_zpl_fs_bridge': DELIVERY}):
                with self.assertRaisesRegex(ValueError, 'filesystem service'):
                    runtime.suite(Path('/absent'), **kwargs)
        with self.assertRaisesRegex(ValueError, 'filesystem service'):
            volume.build(Path('/absent'), None, None, pool_fs_service={})
        with self.assertRaisesRegex(ValueError, 'filesystem service'):
            elapsed.prepare(Path('/absent'), None, volume_fs_service={})
        with patch.object(service, 'intake', side_effect=AssertionError('service intake')):
            for kwargs in ({'filesystem_bridge': DELIVERY}, {'repeated_writes': True}, {'truncate_zero': True}):
                with self.assertRaisesRegex(ValueError, 'exclusive'):
                    pair.pair(Path('/absent'), Path('/absent'), filesystem_service=DELIVERY, **kwargs)
        for arg in ('--repeated-writes', '--truncate-zero', '--filesystem-bridge'):
            options = [arg, str(DELIVERY)] if arg == '--filesystem-bridge' else [arg]
            r = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/zpl_pair.py'),
                '--filesystem-service', str(DELIVERY), *options, '--delivery', '/absent', '--utc-delivery', '/absent'],
                capture_output=True, text=True, timeout=5)
            self.assertEqual(r.returncode, 64, r.stderr)

    def test_sealed_rust_native_entry_with_typed_host_ffi_and_transport_faults(self):
        selected = service.intake(DELIVERY)
        source = DELIVERY / 'source'
        rust = json.loads((DELIVERY / 'inputs.json').read_text())['tools']['rustc']['path']
        with tempfile.TemporaryDirectory(prefix='aether-service-rust-') as temp:
            out = Path(temp)
            commands = []
            for crate, filename, dependencies in (
                ('filesystem_policy', 'owner.rs', []),
                ('filesystem_bridge', 'bridge.rs', ['filesystem_policy']),
                ('filesystem_service', 'service.rs', ['filesystem_policy'])):
                cmd = [rust, '--edition=2021', '-Dwarnings', '-Dunsafe_op_in_unsafe_fn',
                       '--crate-type=rlib', '--crate-name=' + crate, str(source / filename),
                       '-Ldependency=' + str(out), '-o', str(out / ('lib' + crate + '.rlib'))]
                for dep in dependencies: cmd += ['--extern', dep + '=' + str(out / ('lib' + dep + '.rlib'))]
                commands.append(cmd)
            sdk = subprocess.check_output(['xcrun','--show-sdk-path'],text=True).strip()
            commands.append(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang','-isysroot',sdk,
                '-std=gnu11','-Wall','-Wextra','-Werror','-I'+str(DELIVERY/'ffi'),'-I'+str(source),
                '-c',str(source/'bridge-fixture.c'),'-o',str(out/'fixture.o')])
            commands.append([rust,'--edition=2021','-Dwarnings','-Dunsafe_op_in_unsafe_fn','--test',
                str(source/'native-service.rs'),'-Ldependency='+str(out),
                '--extern','filesystem_bridge='+str(out/'libfilesystem_bridge.rlib'),
                '--extern','filesystem_service='+str(out/'libfilesystem_service.rlib'),
                '-Clink-arg='+str(out/'fixture.o'),'-o',str(out/'native-tests')])
            commands.append([str(out/'native-tests'),'--test-threads=1'])
            for cmd in commands:
                result = subprocess.run(cmd,capture_output=True,text=True,timeout=30)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn('test result: ok',result.stdout)
            service.recheck(selected)

    def test_partial_original_symbols_cannot_be_missing_wrong_or_duplicate(self):
        symbols = ['aether_fs_service_run', 'aether_zpl_open_write', 'aether_zpl_close',
                   'aether_zpl_root', 'aether_zpl_lookup', 'aether_zpl_read', 'aether_zpl_write']
        lines = []
        for symbol in symbols:
            owner = 'filesystem-service.o' if symbol == symbols[0] else 'zpl-write.o'
            lines += [f'0 0 0 0 /selected/{owner}:(.text.{symbol})', f'0 0 0 0 {symbol}']
        text = '\n'.join(lines)
        self.assertEqual(len(service.partial_origins(text)), 7)
        for bad in (text.replace('filesystem-service.o', 'other.o'), '\n'.join(lines[:-1]), text + '\n' + lines[-1]):
            with self.assertRaises(ValueError): service.partial_origins(bad)

    def test_actual_native_partial_wrap_preserves_original_close_definition(self):
        selected = service.intake(DELIVERY)
        recipe = next(c['argv'] for c in json.loads((elapsed.CURRENT / 'build-attempt-5/results.json').read_text())['commands']
                      if c['name'] == 'input-176-checked')
        prefix = [elapsed.route(a) for a in recipe[:recipe.index('-c')]]
        prefix[1:1] = ['-I' + str(volume.OWNED), '-I' + selected['header_directory']]
        prefix += ['-isystem', str(Path(prefix[0]).parents[1] / 'lib/clang/21/include'),
                   '-DAETHER_ZPL_ORDERED_WRITE=1', '-std=gnu11', '-Wall', '-Wextra', '-Werror',
                   '-ffunction-sections', '-fdata-sections']
        with tempfile.TemporaryDirectory(prefix='aether-service-native-link-') as temp:
            out = Path(temp); probe = out / 'probe.c'
            probe.write_text(service.probe((volume.OWNED / 'zpl-write-probe.c').read_text(), 'close-failure'))
            commands = [prefix + ['-c', str(source), '-o', str(out / (name + '.o'))] for name, source in
                        [('zpl-write', volume.OWNED / 'zpl-write.c'), ('zpl-write-probe', probe)]]
            commands.append(['/opt/homebrew/Cellar/lld@21/21.1.8_1/bin/ld.lld', '-r', '--wrap=aether_zpl_close',
                '-Map=' + str(out / 'partial.map'), str(out / 'zpl-write.o'), str(out / 'zpl-write-probe.o'),
                selected['object'], '-o', str(out / 'partial.o')])
            for cmd in commands:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            result = subprocess.run(['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/llvm-nm', '--print-size',
                '--defined-only', str(out / 'partial.o')], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            found = service.partial_origins((out / 'partial.map').read_text(), 'close-failure', result.stdout)
            self.assertEqual(len(found), 8)
            self.assertTrue(found['aether_zpl_close'].endswith('/zpl-write.o'))
            service.recheck(selected)

    def test_wrapped_close_requires_original_section_and_exact_defined_symbol(self):
        symbols = ['aether_fs_service_run', 'aether_zpl_open_write', 'aether_zpl_root',
                   'aether_zpl_lookup', 'aether_zpl_read', 'aether_zpl_write', '__wrap_aether_zpl_close']
        lines = []
        for symbol in symbols:
            owner = 'filesystem-service.o' if symbol == symbols[0] else 'zpl-write-probe.o' if symbol == symbols[-1] else 'zpl-write.o'
            lines += [f'0 0 0 0 /selected/{owner}:(.text.{symbol})', f'0 0 0 0 {symbol}']
        section = '0 0 32 16 /selected/zpl-write.o:(.text.aether_zpl_close)'
        text = '\n'.join(lines + [section]); nm = '00000000 00000032 T aether_zpl_close'
        self.assertEqual(len(service.partial_origins(text, 'close-failure', nm)), 8)
        for bad_map, bad_nm in ((text, None), (text, ''), (text, nm+'\n'+nm),
                (text, nm.replace(' T ', ' W ')), (text, nm.replace('00000032', '00000031')),
                (text, nm.replace('00000032', '00000000')), (text+'\n'+section, nm),
                (text.replace(section, section.replace('zpl-write.o', 'other.o')), nm)):
            with self.assertRaises(ValueError): service.partial_origins(bad_map, 'close-failure', bad_nm)

    def fixture(self):
        f = controls.PairControls(); f.setUp(); self.addCleanup(f.doCleanups)
        shutil.copytree(f.output / 'reader', f.output / 'baseline')
        f.builds['baseline'] = copy.deepcopy(f.builds['reader']); f.builds['baseline']['pool_zpl_recover'] = False
        b = f.builds['writer']; selected = service.intake(DELIVERY)
        b.update(fs_service=selected, namespace_ipc=True, pool_zpl_writer_budget=True, fs_service_case='normal')
        b['commands'] = [{'argv': ['zig', 'build', '-Dnative-service-channel=true', '-Dnative-service-zpl-budget=true']}]
        b['commands'] += [{'argv': ['rustc', '-Clink-arg=--oformat=binary']}, {'argv': ['ld.lld', '-r', '-Map=/test/bridge-partial.map']}]
        b['cases'][0]['kernel_profile'] = 'AENBD003/ABI25'
        source = ROOT / 'user/storage/openzfs-volume'
        b['port'] = {'volume': {'namespace_objects': {
            'fs-service-consumer': service.sha(selected['object']),
            'fs-service-owner-source': service.sha(source / 'fs-service-owner.inc'),
            'fs-service-probe-source': hashlib.sha256(service.probe((source / 'zpl-write-probe.c').read_text()).encode()).hexdigest()}}}
        import openzfs_fs_bridge as bridge
        reader = f.builds['reader']; reader.update(pool_recovery_writer_60s=True, pool_recovery_diagnostic=True)
        reader['port'] = {'volume': {'namespace_objects': {'recovery-selected-source': hashlib.sha256(
            bridge.recovery_source((source / 'zpl-recovery.c').read_text(), True, True).encode()).hexdigest()}}}
        return f

    def verify(self, f):
        with patch.object(runtime, 'sealed'):
            pair.verify_prepared(f.output, f.builds, writer_ticks_6000=True, writer_60s=True,
                recovery_diagnostic=True, filesystem_service=DELIVERY)

    def test_actual_emitted_driver_and_partial_link_commands_pass_admission(self):
        tree = ast.parse(Path(runtime.__file__).read_text())
        driver = next(n for n in ast.walk(tree) if isinstance(n, ast.Expr) and
            isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name) and
            n.value.func.id == 'command' and 'link-arg=--oformat=binary' in ast.unparse(n))
        tree = ast.parse(Path(elapsed.__file__).read_text())
        partial = next(n for n in ast.walk(tree) if isinstance(n, ast.Expr) and
            isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name) and
            n.value.func.id == 'command' and 'bridge-partial.map' in ast.unparse(n))
        for case in service.CASES:
            f = self.fixture(); b = f.builds['writer']; number = service.case_number(case)
            b['fs_service_case'] = case
            b['port']['volume']['namespace_objects']['fs-service-probe-source'] = hashlib.sha256(service.probe(
                (ROOT / 'user/storage/openzfs-volume/zpl-write-probe.c').read_text(), case).encode()).hexdigest()
            emitted = []
            def command(argv, log): emitted.append(list(map(str, argv)))
            scope = {n.id: False for n in ast.walk(driver) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
            scope.update(command=command, str=str, volume_readonly=runtime.volume_readonly, SOURCE=runtime.SOURCE, name='pool-import',
                namespace_ipc=True, service_case=number, volume=True, engine_native=True, _zpl_fs_namespace=None,
                pool_create=True, pool_zpl_write=True, WRITE_CASES=runtime.WRITE_CASES,
                driver_source=f.output/'writer/supervisor.rs', dest=f.output/'writer')
            exec(compile(ast.Module(body=[driver],type_ignores=[]),'<actual driver command>','exec'),scope)
            scope=dict(command=command, tool='ld.lld', service_case=number, volume_fs_bridge=None,
                volume_fs_service={}, output=f.output/'writer', base=[])
            exec(compile(ast.Module(body=[partial],type_ignores=[]),'<actual partial command>','exec'),scope)
            b['commands'] = b['commands'][:1] + [{'argv': args} for args in emitted]
            with patch.object(runtime,'sealed'):
                pair.verify_prepared(f.output,f.builds,writer_ticks_6000=True,writer_60s=True,
                    recovery_diagnostic=True,filesystem_service=DELIVERY,filesystem_service_case=case)

    def test_fixed_case_source_cfg_partial_wrap_and_no_service_denials(self):
        for bad in ('other', '', True, 3, None):
            with self.assertRaises(ValueError): service.case_number(bad)
        for case in service.CASES[1:]:
            with self.subTest(case=case):
                f = self.fixture(); b = f.builds['writer']; b['fs_service_case'] = case
                b['port']['volume']['namespace_objects']['fs-service-probe-source'] = hashlib.sha256(service.probe(
                    (ROOT / 'user/storage/openzfs-volume/zpl-write-probe.c').read_text(), case).encode()).hexdigest()
                option = 'fs_lost_reply' if case == 'lost-reply' else 'fs_partial_request'
                if case != 'close-failure': b['commands'][1]['argv'] += ['--cfg', option]
                else: b['commands'][2]['argv'] += ['--wrap=aether_zpl_close']
                def verify():
                    with patch.object(runtime, 'sealed'):
                        pair.verify_prepared(f.output, f.builds, writer_ticks_6000=True, writer_60s=True,
                            recovery_diagnostic=True, filesystem_service=DELIVERY, filesystem_service_case=case)
                verify()
                index = 2 if case == 'close-failure' else 1
                b['commands'][index]['argv'].pop()
                with self.assertRaisesRegex(ValueError, 'driver/wrap'): verify()
            with self.assertRaisesRegex(ValueError, 'requires its exact selection'):
                runtime.suite(Path('/absent'), _zpl_fs_service_case=case)
            with self.assertRaisesRegex(ValueError, 'requires its exact selection'):
                pair.pair(Path('/absent'), Path('/absent'), filesystem_service_case=case)

    def test_prepared_service_requires_exact_sources_profile_both_flags_and_role(self):
        f = self.fixture(); self.verify(f); original = copy.deepcopy(f.builds)
        for mutation in ('selection', 'source', 'channel', 'budget', 'namespace', 'abi', 'foreign-reader'):
            f.builds = copy.deepcopy(original); b = f.builds['writer']
            if mutation == 'selection': b['fs_service'] = None
            elif mutation == 'source': b['port']['volume']['namespace_objects']['fs-service-probe-source'] = '0' * 64
            elif mutation in ('channel', 'budget'): b['commands'][0]['argv'].remove('-Dnative-service-' + ('channel' if mutation == 'channel' else 'zpl-budget') + '=true')
            elif mutation == 'namespace': b['namespace_ipc'] = False
            elif mutation == 'abi': b['cases'][0]['kernel_profile'] = 'AENBD002/ABI14'
            else: f.builds['reader']['fs_service'] = b['fs_service']
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): self.verify(f)


FAKE = r'''
#include "native-service.h"
static unsigned long getauxval(unsigned long key) { CHECK(key == 0xa004 || key == 0xa005); return key == 0xa004 ? 0x10001 : 0x20002; }
static int callbacks;
int aether_fs_service_run(void *spa, const unsigned char *dataset, size_t length,
                         uint64_t reader, uint64_t writer, uint64_t rights,
                         struct aether_fs_service_result *out)
{
    CHECK(!owned && closes == 1 && !callbacks++);
    CHECK(spa == &pool && length == 20 && !memcmp(dataset, "testpool_zstd/x86_64", 21));
    CHECK(reader == 0x10001 && writer == 0x20002 && rights == 7);
    aether_zpl_view *context = NULL;
    aether_zpl_write_result result = {0};
    unsigned char bytes[16];
    for (unsigned i = 0; i < sizeof(bytes); ++i) bytes[i] = (unsigned char)(17*i+91);
    int error = aether_zpl_open_write(spa, "testpool_zstd/x86_64", &context);
    if (!error) error = aether_zpl_write(context, 2, 47, 37, bytes, 16, 1234, 5678, &result);
    *out = (struct aether_fs_service_result){.ready=1, .requests=11, .txg=result.txg, .bytes_staged=result.bytes_staged, .state=result.state};
    aether_zpl_close(&context);
    if (mode == 19 && !error) error = EIO;
#if AETHER_FS_SERVICE_CASE == 1
    if (!error) { out->requests = 5; out->stop = 2; out->error = -32; error = 5; }
#elif AETHER_FS_SERVICE_CASE == 2
    if (!error) { out->requests = 10; out->stop = 1; out->error = -5; error = 5; }
#elif AETHER_FS_SERVICE_CASE == 3
    if (!error) { out->reader_close = -13; out->error = -13; error = 5; }
#endif
    if (mode == 20) out->ready = 0;
    if (mode == 21) out->requests ^= 1;
    if (mode == 22) out->stop ^= 1;
    if (mode == 23) out->reader_close ^= 1;
    if (mode == 24) out->writer_close = -5;
    if (mode == 25) out->error ^= 1;
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
    if (!mode) CHECK(writes == 1 && callbacks == 1 && closes == 3 && reads == 382 && calls == 392);
    if (mode == 13 || (mode >= 19 && mode <= 25)) CHECK(writes == 1 && callbacks == 1 && assigned == 42 && diagnostic[1] == 6);
    return 0;
}
'''


class ServiceProbe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-service-probe-'); cls.addClassCleanup(cls.temp.cleanup)
        cls.out = Path(cls.temp.name)
        cls.seed = (ROOT / 'user/storage/openzfs-volume/zpl-write-probe.c').read_text()
        cls.body = '\n'.join(l for l in service.probe(cls.seed).splitlines() if not l.startswith('#include'))
        owner = '\n'.join(l for l in (ROOT / 'user/storage/openzfs-volume/fs-service-owner.inc').read_text().splitlines() if not l.startswith('#include'))
        cls.body = owner + '\n' + cls.body
        prefix = (ROOT / 'tests/fixtures/openzfs_zpl_write_probe.c').read_text().split('#define clock_gettime probe_clock_gettime')[0]
        prefix = prefix.replace('    CHECK(owned && *out == &view);', '    if (!out || !*out) return;\n    CHECK(owned && *out == &view);')
        cls.prefix = prefix
        cls.sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        cls.binary = cls.compile(cls.body, 'probe')

    @classmethod
    def compile(cls, body, name, case=0):
        prefix = cls.prefix
        if case == 3:
            prefix = '#define aether_zpl_close fixture_original_close\n' + prefix + r'''
#undef aether_zpl_close
static int callbacks, injected_closes;
extern void __wrap_aether_zpl_close(aether_zpl_view **);
void __real_aether_zpl_close(aether_zpl_view **view) { fixture_original_close(view); }
static int64_t host_channel_close(uint64_t cap) { CHECK(!owned && callbacks == 1 && closes == 2 && cap == 0x10001 && !injected_closes++); return mode == 28 ? -5 : 0; }
#define AETHER_FS_HOST_CLOSE host_channel_close
#define aether_zpl_close __wrap_aether_zpl_close
'''
        (cls.out / 'host.c').write_text('#define AETHER_FS_SERVICE_CASE ' + str(case) + '\n' + prefix + FAKE)
        (cls.out / 'write-probe.inc').write_text(body); binary = cls.out / name
        cmd = ['/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang', '-isysroot', cls.sdk,
               '-std=gnu11', '-O2', '-Wall', '-Wextra', '-Werror', '-I' + str(cls.out),
               '-I' + str(ROOT / 'user/storage/openzfs-volume'), '-I' + str(DELIVERY / 'source'), str(cls.out / 'host.c'), '-o', str(binary)]
        result = subprocess.run(cmd,capture_output=True,text=True,timeout=30)
        if result.returncode: raise RuntimeError(result.stdout+result.stderr)
        return binary

    def test_success_api_faults_and_malformed_service_outcomes_preserve_progress(self):
        for mode in [0,*range(1,8),*range(9,26),*range(101,493)]:
            with self.subTest(mode=mode):
                p = subprocess.run([str(self.binary),str(mode)],capture_output=True,text=True,timeout=5)
                self.assertEqual(p.returncode,0,p.stdout+p.stderr)

    def test_fixed_failure_dispositions_and_context_close_fault_arm(self):
        for case in (1, 2, 3):
            binary = self.compile(self.body, 'case-' + str(case), case)
            for mode in [0, 19, *range(20, 26), *([28] if case == 3 else [])]:
                with self.subTest(case=case, mode=mode):
                    result = subprocess.run([str(binary), str(mode)], capture_output=True, text=True, timeout=5)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for name, old, new, mode in (
            ('no-injection', 'if (fs_close_reader)', 'if (0)', 0),
            ('ignore-injection-error', 'fs_injected != FS_CLOSES || fs_injection_error', 'fs_injected != FS_CLOSES', 28),
            ('early-injection', '    __real_aether_zpl_close(view);', '', 0)):
            body = self.body
            self.assertEqual(body.count(old), 1)
            # Keep referenced declarations valid in intentional broken controls.
            if name == 'early-injection': new = '    if (0) __real_aether_zpl_close(view);'
            binary = self.compile(body.replace(old, new, 1), name, 3)
            result = subprocess.run([str(binary), str(mode)], capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 96, result.stdout + result.stderr)
            self.assertIn('HOST ZPL PROBE oracle96', result.stderr)

    def test_compiling_context_call_progress_and_full_readback_omissions_fail96(self):
        changes = [
            ('preclose','        aether_zpl_close(&view);','        if (0) aether_zpl_close(&view);',0),
            ('invoke','error = aether_fs_owner_probe(spa, &result);','error = 0; if (0) error = aether_fs_owner_probe(spa, &result);',0),
            ('assigned','    *assigned = result.txg;','    if (!error) *assigned = result.txg;',19),
            ('hash','memcmp(actual, predicted, sizeof(actual))','0',18),
            ('cleanup','completion.reader_close || completion.writer_close || completion.error','0',23),
        ]
        for name,old,new,mode in changes:
            with self.subTest(name=name):
                self.assertEqual(self.body.count(old),1)
                binary = self.compile(self.body.replace(old,new,1),name)
                p = subprocess.run([str(binary),str(mode)],capture_output=True,text=True,timeout=5)
                self.assertEqual(p.returncode,96,p.stdout+p.stderr)
                self.assertIn('HOST ZPL PROBE oracle96',p.stderr)


if __name__ == '__main__': unittest.main()
