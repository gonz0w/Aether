# SPDX-License-Identifier: BSD-2-Clause
"""Actual private readiness gate; host observations grant no native authority."""
import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'user/storage/service-runtime/fs-activation-client.rs'


class Activation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-fs-activation-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.out = Path(cls.temp.name)
        cls.rustc = subprocess.check_output(
            ['rustup', 'which', '--toolchain', '1.98.0', 'rustc'], text=True).strip()

    def compile(self, source, name, native=False):
        binary = self.out / name
        flags = (['--crate-type=lib', '--emit=obj', '--target=x86_64-unknown-none',
                  '-Cpanic=abort'] if native else ['--test'])
        result = subprocess.run([self.rustc, '--edition=2024', '-Dwarnings',
                                 *flags, str(source), '-o', str(binary)],
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        print(name, binary.stat().st_size, hashlib.sha256(binary.read_bytes()).hexdigest())
        return binary

    def test_actual_gate_handles_pending_ready_terminal_errors_and_shared_budget(self):
        binary = self.compile(SOURCE, 'positive')
        result = subprocess.run([str(binary), '--test-threads=1'],
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('3 passed; 0 failed', result.stdout)

    def test_scalar_native_assembly_compiles(self):
        source = self.out / 'native.rs'
        source.write_text('#![no_std]\n' + SOURCE.read_text().replace(
            '//! Private retained-instance readiness gate, not supervision or retry policy.',
            '// Private retained-instance readiness gate.'))
        self.compile(source, 'native.o', native=True)

    def test_compiling_omissions_are_rejected_by_executed_gate_oracles(self):
        cases = [
            ('terminal', 'status != 0 || ready > 1', 'status < 0 || ready > 1',
             'tests::terminal_stale_foreign_and_malformed_ready_never_admit'),
            ('malformed', 'status != 0 || ready > 1', 'status != 0',
             'tests::terminal_stale_foreign_and_malformed_ready_never_admit'),
            ('budget', '*remaining -= 1;', '*remaining -= 0;',
             'tests::pending_then_ready_keeps_the_completion_budget'),
        ]
        for name, old, new, test in cases:
            with self.subTest(name=name):
                text = SOURCE.read_text()
                self.assertEqual(text.count(old), 1)
                source = self.out / (name + '.rs')
                source.write_text(text.replace(old, new, 1))
                binary = self.compile(source, name)
                result = subprocess.run([str(binary), '--exact', test, '--test-threads=1'],
                                        capture_output=True, text=True, timeout=60)
                self.assertEqual(result.returncode, 101, result.stdout + result.stderr)
                self.assertIn(test + ' ... FAILED', result.stdout)
                self.assertIn('ACTIVATION_EXTRA_POLL' if name == 'malformed' else 'assertion', result.stdout)

class Controller(unittest.TestCase):
    def driver(self):
        import ast
        import sys
        sys.path.insert(0, str(ROOT / 'scripts'))
        import service_runtime_smoke as runtime
        tree = ast.parse(Path(runtime.__file__).read_text())
        node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'suite')
        volume = next(n for n in ast.walk(node) if isinstance(n, ast.If) and
                      isinstance(n.test, ast.Name) and n.test.id == 'engine_volume' and
                      n.body and isinstance(n.body[0], ast.Assign) and
                      ast.unparse(n.body[0].targets[0]) == 'driver_text')
        body = []
        for n in volume.body:
            if isinstance(n, ast.Assign) and ast.unparse(n.targets[0]) == 'driver_source':
                break
            body.append(n)
        scope = dict(SOURCE=runtime.SOURCE, spa_physical=False, pool_create=True,
                     engine_utc=True, pool_data=False, pool_diagnose='run',
                     pool_recovery_check=None, pool_namespace=True, namespace_ipc=True, namespace_wait=True,
                     pool_zpl_write=True, pool_zpl_recover=False, namespace_driver=runtime.namespace_driver,
                     _zpl_storage_lifetime=False, _zpl_stages=False, _zpl_write_stages=False, _zpl_txg_stages=False, _zpl_sync_stages=False,
                     pool_diagnostic_driver=runtime.pool_diagnostic_driver,
                     namespace_ipc_driver=runtime.namespace_ipc_driver, service={'activation': True})
        selected = dict(scope)
        exec(compile(ast.Module(body=body, type_ignores=[]), '<actual activation adapter>', 'exec'), selected)
        return selected['driver_text']

    def test_actual_adapter_four_controller_roles_and_old_limit_rejection(self):
        with tempfile.TemporaryDirectory(prefix='aether-activation-controller-') as directory:
            out = Path(directory)
            for case in ('normal', 'lost-reply', 'partial-request', 'close-failure'):
                text = self.driver()
                self.assertEqual(text.count('check(activation::ready(owner, &mut polls))'), 1)
                self.assertEqual(text.count('let mut polls = 1000000u32;'), 1)
                self.assertIn('while polls != 0 {\n            polls -= 1;', text)
                source = out / 'supervisor.rs'; source.write_text(text)
                binary = out / (case + '.raw')
                argv = ['rustc', '+1.98.0', '--edition=2024', '--target=x86_64-unknown-none', '-Dwarnings',
                        '-Copt-level=z', '-Clto=fat', '-Ccodegen-units=1', '-Cpanic=abort', '-Crelocation-model=static',
                        '-Clink-arg=-Tuser/storage/service-runtime/activation-linker.ld', '-Clink-arg=--oformat=binary']
                for cfg in ['pool_create', 'pool_import', 'fs_mixed', 'namespace_wait', 'fs_bulk', 'fs_runtime', 'fs_activation']:
                    argv += ['--cfg', cfg]
                if case in ('lost-reply', 'partial-request'):
                    argv += ['--cfg', 'fs_lost_reply' if case == 'lost-reply' else 'fs_partial_request']
                argv += [str(source), '-o', str(binary)]
                result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, timeout=60)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertLessEqual(binary.stat().st_size, 8192)
                print('activation controller', case, binary.stat().st_size, hashlib.sha256(binary.read_bytes()).hexdigest())
                # The legacy selection must still produce the original exact controller.
                import json
                previous = json.loads((ROOT / 'docs/evidence/fs-service-activation-native-2026-10-20.json').read_text())
                legacy_argv = []
                skip = False
                for i, arg in enumerate(argv):
                    if skip:
                        skip = False
                        continue
                    if arg == '--cfg' and argv[i + 1] == 'fs_activation':
                        skip = True
                        continue
                    legacy_argv.append(arg)
                legacy = subprocess.run(legacy_argv, cwd=ROOT, capture_output=True, text=True, timeout=60)
                self.assertEqual(legacy.returncode, 0, legacy.stdout + legacy.stderr)
                reference = previous['builds'][case + '/writer']['cases'][0]
                self.assertEqual(binary.stat().st_size, reference['supervisor_bytes'])
                self.assertEqual(hashlib.sha256(binary.read_bytes()).hexdigest(), reference['supervisor_sha256'])

                if case == 'normal':
                    self.assertEqual(binary.stat().st_size, 4181)
                    rejected = subprocess.run([a.replace('link-arg=-Tuser/storage/service-runtime/activation-linker.ld',
                        'link-arg=-Tuser/protection/linker.ld') for a in argv], cwd=ROOT,
                        capture_output=True, text=True, timeout=60)
                    self.assertNotEqual(rejected.returncode, 0)
                    self.assertIn('fixture exceeds one code page', rejected.stderr)
                    # Same linker retains the no-writable-statics check.
                    source.write_text('''#![no_std]
#![no_main]
static mut DATA:u64=1;
#[unsafe(no_mangle)]
#[unsafe(link_section=".text.entry")]
pub extern "C" fn _start()->! {unsafe{core::ptr::write_volatile(core::ptr::addr_of_mut!(DATA),2)};loop{core::hint::spin_loop();}}
#[panic_handler]
fn panic(_:&core::panic::PanicInfo)->! {loop{}}
''')
                    rejected = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, timeout=60)
                    self.assertNotEqual(rejected.returncode, 0)
                    self.assertIn('fixture must have no writable statics', rejected.stderr)


if __name__ == '__main__':
    unittest.main()
