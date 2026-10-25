#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Private framing/admission controls; host models do not authenticate a peer."""
import hashlib
import ast
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from service_runtime_smoke import namespace_ipc_driver, suite
import service_runtime_smoke as runtime


class NamespaceIpc(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-namespace-ipc-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.out = Path(cls.temp.name)
        cls.rustc = subprocess.check_output(['rustup', 'which', '--toolchain', '1.98.0', 'rustc'], text=True).strip()

    def compile(self, source, name, native=False):
        output = self.out / name
        flags = ['--crate-type=lib', '--target=x86_64-unknown-none', '--emit=obj', '-Cpanic=abort'] if native else ['--test']
        result = subprocess.run([self.rustc, '--edition=2024', '-Dwarnings', '-Copt-level=2', *flags,
                                 str(source), '-o', str(output)], capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        print('IPC compiled:', name, output.stat().st_size, hashlib.sha256(output.read_bytes()).hexdigest())
        return output

    def run_binary(self, binary, method=None, oracle=None):
        args = [str(binary), '--test-threads=1', '--nocapture']
        if method:
            args += ['--exact', method]
        result = subprocess.run(args, capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 101 if oracle else 0, result.stdout + result.stderr)
        if oracle:
            self.assertIn(oracle, result.stderr)
            print('IPC compiling omission rejected:', binary.name, oracle)
        return result

    def test_actual_wire_owner_lifetime_rights_and_canonical_denials(self):
        binary = self.compile(ROOT / 'tests/fixtures/namespace_wire.rs', 'wire')
        result = self.run_binary(binary)
        self.assertIn('14 passed; 0 failed', result.stdout)

    def wire_variant(self, body, name):
        wire = self.out / (name + '_wire.rs')
        wire.write_text(body)
        owner = self.out / (name + '_owner.rs')
        owner.write_text((ROOT / 'user/storage/namespace.rs').read_text().replace(
            'namespace-wire.rs', str(wire)).replace('../../tests/fixtures/namespace_owner.rs',
                                                  str(ROOT / 'tests/fixtures/namespace_owner.rs')))
        fixture = self.out / (name + '.rs')
        fixture.write_text((ROOT / 'tests/fixtures/namespace_wire.rs').read_text().replace(
            '../../user/storage/namespace.rs', str(owner)))
        return self.compile(fixture, name)

    def test_compiling_wire_omissions_fail_named_oracles(self):
        body = (ROOT / 'user/storage/namespace-wire.rs').read_text()
        for name, old, new, method, oracle in (
            ('padding', '|| raw[40 + length..].iter().any(|b| *b != 0)', '|| false',
             'canonical_rejection_precedes_provider_and_never_echoes_request', 'WIRE_AUTHORITY'),
            ('length', 'count > PAYLOAD ||', 'false ||',
             'failed_partial_provider_output_is_canonical_and_overlength_never_calls_it', 'WIRE_AUTHORITY'),
            ('disconnect', 'self.closed = true;', 'self.closed = false;',
             'close_disconnect_and_provider_epoch_reject_replays', 'WIRE_DISCONNECT'),
            ('reply', 'put(&mut reply, 0, code as u64);',
             'put(&mut reply, 0, code as u64); reply[40] = 0xa5;',
             'failed_partial_provider_output_is_canonical_and_overlength_never_calls_it', 'WIRE_FAILED_REPLY'),
        ):
            with self.subTest(omission=name):
                self.assertEqual(body.count(old), 1)
                self.run_binary(self.wire_variant(body.replace(old, new, 1), name), method, oracle)

    def frame_source(self, body, name):
        source = self.out / (name + '.rs')
        # Replace only the privileged syscall boundary; execute the actual frame
        # loop and the deterministic trap oracle together on the host.
        source.write_text((ROOT / 'tests/fixtures/namespace_channel.rs').read_text() + '\n' + body)
        return source

    def test_actual_frame_partial_progress_backpressure_eof_and_timeout(self):
        body = (ROOT / 'user/storage/namespace-channel.rs').read_text().split('pub fn frame(', 1)[1]
        source = self.frame_source('pub fn frame(' + body, 'frames')
        result = self.run_binary(self.compile(source, 'frames'))
        self.assertIn('3 passed; 0 failed', result.stdout)

    def test_compiling_transport_omissions_reject_partial_eof_and_dirty_failure(self):
        body = 'pub fn frame(' + (ROOT / 'user/storage/namespace-channel.rs').read_text().split('pub fn frame(', 1)[1]
        for name, changed, oracle in (
            ('clear', body.replace('bytes.fill(0);', ''), 'FRAME_CLEAR'),
            ('eof', body.replace('if count == -11 {', 'if count == 0 { return Ok(()); } else if count == -11 {'), 'FRAME_TERMINAL'),
        ):
            self.run_binary(self.compile(self.frame_source(changed, name), name),
                            'terminal_or_invalid_completion_erases_partial_frame', oracle)

    def test_opt_in_selection_and_context_rejection_precede_external_intake(self):
        with self.assertRaisesRegex(ValueError, 'namespace IPC requires namespace profile'):
            suite(Path('/unused'), namespace_ipc=True)
        text = (ROOT / 'user/storage/service-runtime/engine-supervisor.rs').read_text().replace('abi == 1', 'abi == 14')
        selected = namespace_ipc_driver(text)
        self.assertIn('abi == 25', selected)
        self.assertIn('connection.admit(factory)', selected)
        self.assertIn('connection.finish()', selected)
        with self.assertRaisesRegex(ValueError, 'context changed'):
            namespace_ipc_driver(text.replace('let owner = call(0x20000, factory, 0).0;', ''))

    def test_native_adapter_and_original_zpl_composition_codegen(self):
        source = self.out / 'adapter.rs'
        source.write_text('#![no_std]\n#[path = "' + str(ROOT / 'user/storage/namespace-channel.rs') + '"]\npub mod channel;\n')
        self.compile(source, 'adapter.o', native=True)
        output = self.out / 'zpl.o'
        result = subprocess.run([self.rustc, '--crate-name', 'namespace_zpl', '--edition=2024',
                                 '--crate-type=lib', '--target=x86_64-unknown-none', '--emit=obj',
                                 '-Dwarnings', '-Copt-level=2', '-Cpanic=abort', '--cfg', 'namespace_ipc',
                                 str(ROOT / 'user/storage/openzfs-volume/namespace-zpl.rs'), '-o', str(output)],
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_actual_adapted_supervisor_preserves_one_page_and_no_statics(self):
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
        scope = dict(_zpl_storage_lifetime=False, SOURCE=runtime.SOURCE, spa_physical=False, pool_create=True,
                     engine_utc=True, pool_data=False, pool_diagnose='run',
                     pool_recovery_check=None, pool_namespace=True, namespace_ipc=True, namespace_wait=False,
                     pool_zpl_write=False, pool_zpl_recover=False, namespace_driver=runtime.namespace_driver,
                     _zpl_stages=False, _zpl_write_stages=False,
                     _zpl_txg_stages=False, _zpl_sync_stages=False,
                     pool_diagnostic_driver=runtime.pool_diagnostic_driver,
                     namespace_ipc_driver=runtime.namespace_ipc_driver)
        cases = [(case, False, None) for case in (None, 'normal', 'lost-reply', 'partial-request', 'close-failure')]
        cases += [(case, True, None) for case in ('normal', 'lost-reply', 'partial-request', 'close-failure')]
        cases += [(case, False, operation) for operation in ('create','rename','remove')
                  for case in ('normal','lost-reply','close-failure')]
        cases += [(case, False, 'mixed') for case in ('normal','lost-reply','partial-request','close-failure')]
        cases += [(None, False, 'wait')]
        cases += [(case, False, 'mixed-wait') for case in ('normal','lost-reply','partial-request','close-failure')]
        cases += [(case, False, 'bulk') for case in ('normal','lost-reply','partial-request','close-failure')]
        cases += [(case, False, 'runtime') for case in ('normal','lost-reply','partial-request','close-failure')]
        for case, lifetimes, operation in cases:
            writable = case is not None
            selected = dict(scope, service={} if writable else None, pool_zpl_write=writable,namespace_wait=operation in ('wait','mixed-wait','bulk','runtime'))
            exec(compile(ast.Module(body=body, type_ignores=[]), '<actual IPC adapter>', 'exec'), selected)
            source = self.out / ('service-supervisor-' + case + ('-lifetimes' if lifetimes else '-namespace-'+operation if operation else '') + '.rs' if writable else 'supervisor.rs')
            source.write_text(selected['driver_text'])
            binary = source.with_suffix('.raw')
            # Same rustup proxy/toolchain/flags as the runner; no input copy.
            result = subprocess.run(['rustc', '+1.98.0', '--edition=2024', '--target=x86_64-unknown-none', '-Dwarnings',
                                     '-Copt-level=z', '-Clto=fat', '-Ccodegen-units=1', '-Cpanic=abort',
                                     '-Crelocation-model=static', '-Clink-arg=-Tuser/protection/linker.ld',
                                     '-Clink-arg=--oformat=binary', '-Clink-arg=-Map=' + str(source.with_suffix('.map')), '--cfg', 'pool_create', '--cfg', 'pool_import',
                                     *([] if writable else ['--cfg', 'block_readonly']),
                                     *(['--cfg', 'fs_eight_writes'] if lifetimes else []),
                                     *(['--cfg', 'fs_mixed'] if operation in ('mixed','mixed-wait','bulk','runtime') else ['--cfg','fs_namespace_'+operation] if operation not in (None,'wait') else []),
                                     *(['--cfg','namespace_wait'] if operation in ('wait','mixed-wait','bulk','runtime') else []),
                                     *(['--cfg','fs_bulk'] if operation in ('bulk','runtime') else []),
                                     *(['--cfg','fs_runtime'] if operation=='runtime' else []),
                                     *(['--cfg', 'fs_lost_reply'] if case == 'lost-reply' else ['--cfg', 'fs_partial_request'] if case == 'partial-request' else []),
                                     str(source), '-o', str(binary)],
                                    cwd=ROOT, capture_output=True, text=True, timeout=60)
            if source.with_suffix('.map').is_file():
                for line in source.with_suffix('.map').read_text().splitlines():
                    if line.split()[-1:] in (['.text'], ['.data']): print('IPC image section:', line.strip())
                if result.returncode:
                    entries=[line.split() for line in source.with_suffix('.map').read_text().splitlines()]
                    entries=[f for f in entries if len(f)>=5 and all(c in '0123456789abcdefABCDEF' for c in f[2]) and f[-1].startswith('_R')]
                    for f in sorted(entries,key=lambda f:int(f[2],16),reverse=True)[:15]:print('IPC failed image function:',f[2],f[-1])
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertLessEqual(binary.stat().st_size, 4096)
            print('IPC adapted supervisor:', case if writable else 'readonly-wait' if operation=='wait' else 'readonly',
                  binary.stat().st_size, hashlib.sha256(binary.read_bytes()).hexdigest())



if __name__ == '__main__':
    unittest.main()
