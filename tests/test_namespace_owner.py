# SPDX-License-Identifier: BSD-2-Clause
"""Private actual Rust owner controls; no authenticated IPC or original-C proof."""
import hashlib
from pathlib import Path
import re
import struct
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'user/storage/namespace.rs'
FIXTURE = ROOT / 'tests/fixtures/namespace_owner.rs'
TARGET = ROOT / 'tests/fixtures/namespace_owner_target.rs'
READELF = Path('/opt/homebrew/Cellar/llvm@21/21.1.8/bin/llvm-readelf')


class NamespaceOwner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-namespace-owner-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.out = Path(cls.temp.name)
        cls.compiler = Path(subprocess.check_output(
            ['rustup', 'which', '--toolchain', '1.98.0', 'rustc'], text=True).strip())
        cls.version = subprocess.check_output([str(cls.compiler), '--version'], text=True).strip()
        if not cls.version.startswith('rustc 1.98.0 '):
            raise RuntimeError('namespace owner requires pinned Rust1.98.0')

    @classmethod
    def compile(cls, source, name, extra=()):
        binary = cls.out / name
        result = subprocess.run([str(cls.compiler), '--edition=2024', '-Dwarnings',
                                 '-Copt-level=2', *extra, str(source), '-o', str(binary)],
                                capture_output=True, text=True, timeout=60)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        print('NAMESPACE compiled:', name, 'source sha256:', hashlib.sha256(source.read_bytes()).hexdigest(),
              'artifact bytes:', binary.stat().st_size,
              'sha256:', hashlib.sha256(binary.read_bytes()).hexdigest())
        return binary

    def test_actual_owner_contract(self):
        binary = self.compile(SOURCE, 'owner', ['--test'])
        result = subprocess.run([str(binary), '--nocapture'], capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('10 passed; 0 failed', result.stdout)

    def test_compiling_omissions_fail_named_semantic_assertions(self):
        body = SOURCE.read_text().replace('../../tests/fixtures/namespace_owner.rs', str(FIXTURE)).replace('namespace-wire.rs', str(ROOT / 'user/storage/namespace-wire.rs'))
        mutations = (
            ('peer', 'if self.connections[index].is_none_or(|c| c.peer != peer)',
             'if false && self.connections[index].is_none_or(|c| c.peer != peer)',
             'peer_session_and_service_epoch_never_alias', 'AUTHORITY'),
            ('session', 'if self.handles[index].is_none_or(|h| h.session != session.serial)',
             'if false && self.handles[index].is_none_or(|h| h.session != session.serial)',
             'peer_session_and_service_epoch_never_alias', 'AUTHORITY'),
            ('rights', '|| !parent.rights.contains(rights)', '|| false',
             'rights_are_attenuated_and_types_checked_before_provider', 'RIGHTS_CEILING'),
            ('serial', 'last.checked_add(1).unwrap_or(0)', 'last.checked_add(1).unwrap_or(1)',
             'serial_exhaustion_is_atomic_and_never_wraps', 'SERIAL_EXHAUSTION'),
            ('reply', 'other => {\n                reply.fill(0);', 'other => {',
             'invalid_names_lengths_offsets_and_partial_backend_errors', 'FAILED_REPLY'),
            ('completion', 'Ok(count) if count == expected =>', 'Ok(count) if count <= expected + 1 =>',
             'invalid_names_lengths_offsets_and_partial_backend_errors', 'READ_COMPLETION'),
            ('cleanup', 'drop(self.backend.take());', 'let _ = &self.backend;',
             'whole_file_relative_lookup_and_exact_eof_tail', 'BACKEND_LIFETIME'),
            ('metadata', 'if !node.valid()', 'if false && !node.valid()',
             'provider_admission_failure_and_drop_own_one_cleanup', 'FAILED_LOOKUP'),
        )
        for name, old, new, method, oracle in mutations:
            with self.subTest(mutation=name):
                self.assertEqual(body.count(old), 1)
                source = self.out / ('omit_' + name + '.rs')
                source.write_text(body.replace(old, new, 1))
                binary = self.compile(source, 'omit-' + name, ['--test'])
                result = subprocess.run([str(binary), '--exact', 'tests::' + method, '--nocapture'],
                                        capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 101, result.stdout + result.stderr)
                self.assertIn(oracle, result.stderr)
                self.assertIn('1 failed', result.stdout)
                print('NAMESPACE omitted guard rejected:', name, 'oracle:', oracle, 'exit:', result.returncode)

    def test_native_no_std_codegen_and_layout_budget(self):
        binary = self.compile(TARGET, 'owner.o', ['--crate-type=lib', '--target=x86_64-unknown-none',
                                               '-Cpanic=abort', '--emit=obj'])
        version = subprocess.check_output([str(READELF), '--version'], text=True)
        self.assertIn('21.1.8', version)
        header = subprocess.check_output([str(READELF), '-h', str(binary)], text=True)
        self.assertIn('Advanced Micro Devices X86-64', header)
        raw = subprocess.check_output([str(READELF), '--hex-dump=.rodata.NAMESPACE_OWNER_LAYOUT',
                                       str(binary)], text=True)
        chunks = []
        for line in raw.splitlines():
            match = re.match(r'\s*0x[0-9a-f]+\s+((?:[0-9a-f]{8}\s+){1,4})', line)
            if match:
                chunks.append(bytes.fromhex(match[1]))
        layout = struct.unpack('<4Q', b''.join(chunks))
        self.assertLessEqual(layout[0], 2048)
        self.assertEqual(layout[1:], (8, 16, 16))
        print('NAMESPACE native table bytes/alignment/session/handle:', layout,
              'object bytes:', binary.stat().st_size,
              'sha256:', hashlib.sha256(binary.read_bytes()).hexdigest())


if __name__ == '__main__':
    unittest.main()
