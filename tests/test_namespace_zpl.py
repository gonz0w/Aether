# SPDX-License-Identifier: BSD-2-Clause
"""Actual Rust/C-header ABI composition over provider doubles, not ZPL decoding."""
import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
OWNED = ROOT / 'user/storage/openzfs-volume'
SOURCE = OWNED / 'namespace-zpl.rs'
CLANG = Path('/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang')


class NamespaceZpl(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-namespace-zpl-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.out = Path(cls.temp.name)
        cls.rustc = Path(subprocess.check_output(['rustup', 'which', '--toolchain', '1.98.0', 'rustc'], text=True).strip())
        sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True).strip()
        cls.c_prefix = [str(CLANG), '-isysroot', sdk, '-std=c17', '-O2', '-Wall', '-Wextra', '-Werror',
                        '-I' + str(OWNED), '-I' + str(cls.out)]
        cls.c_body = '\n'.join(line for line in (OWNED / 'owner-probe.c').read_text().splitlines()
                               if not line.startswith('#include')) + '\n'
        cls.c_object = cls.compile_c(cls.c_body, 'provider')

    @classmethod
    def compile_c(cls, body, name):
        (cls.out / 'owner-probe-bodies.inc').write_text(body)
        obj = cls.out / (name + '.o')
        result = subprocess.run(cls.c_prefix + ['-c', str(ROOT / 'tests/fixtures/namespace_zpl.c'), '-o', str(obj)],
                                capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        return obj

    @classmethod
    def compile(cls, source, name, c_object=None, native=False):
        output = cls.out / name
        flags = ['--crate-type=lib', '--target=x86_64-unknown-none', '-Cpanic=abort', '--emit=obj'] if native else ['--test', '-Clink-arg=' + str(c_object or cls.c_object)]
        result = subprocess.run([str(cls.rustc), '--crate-name', 'namespace_zpl', '--edition=2024',
                                 '-Dwarnings', '-Copt-level=2', *flags, str(source), '-o', str(output)],
                                capture_output=True, text=True, timeout=60)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        print('ZPL FFI compiled:', name, 'bytes:', output.stat().st_size,
              'sha256:', hashlib.sha256(output.read_bytes()).hexdigest())
        return output

    def test_actual_c_header_composition_failure_cleanup_and_errno(self):
        binary = self.compile(SOURCE, 'bridge')
        result = subprocess.run([str(binary), '--test-threads=1', '--nocapture'], capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('16 passed; 0 failed', result.stdout)

    def test_compiling_ffi_omissions_fail_named_oracles(self):
        body = SOURCE.read_text().replace('../namespace.rs', str(ROOT / 'user/storage/namespace.rs')).replace(
            '../../../tests/fixtures/namespace_zpl.rs', str(ROOT / 'tests/fixtures/namespace_zpl.rs'))
        for name, old, new, method, oracle in (
            ('close', 'unsafe { aether_zpl_close(&mut view) };', 'if false { unsafe { aether_zpl_close(&mut view) }; }',
             'ffi_complete_probe_preserves_stream_and_two_context_cleanup', 'FFI_CLOSE'),
            ('negative', '_ => Err(Error::InvalidCompletion),', '_ => Ok(()),',
             'ffi_open_status_null_and_error_output_ownership', 'FFI_STATUS'),
            ('root-kind', '_ => return Err(Error::InvalidMetadata),', '_ => Kind::Directory,',
             'ffi_metadata_and_negative_status_never_publish_nodes', 'FFI_METADATA'),
        ):
            with self.subTest(mutation=name):
                self.assertEqual(body.count(old), 1)
                source = self.out / (name + '.rs')
                source.write_text(body.replace(old, new, 1))
                binary = self.compile(source, name)
                result = subprocess.run([str(binary), '--exact', 'tests::' + method, '--test-threads=1', '--nocapture'],
                                        capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 101, result.stdout + result.stderr)
                self.assertIn(oracle, result.stderr)
                print('ZPL FFI omitted guard rejected:', name, oracle)
        old = 'memcmp(digest, expected, sizeof(expected))'
        self.assertIn(old, self.c_body)
        obj = self.compile_c(self.c_body.replace(old, '((void)expected, 0)', 1), 'omit-digest')
        binary = self.compile(SOURCE, 'digest', c_object=obj)
        result = subprocess.run([str(binary), '--exact', 'tests::ffi_suppressed_hash_update_must_fail_final_digest',
                                 '--test-threads=1', '--nocapture'], capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 101, result.stdout + result.stderr)
        self.assertIn('FFI_DIGEST', result.stderr)
        print('ZPL FFI omitted guard rejected: digest FFI_DIGEST')

    def test_native_bridge_codegen(self):
        self.compile(SOURCE, 'namespace-zpl.o', native=True)


if __name__ == '__main__':
    unittest.main()
