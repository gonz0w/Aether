# SPDX-License-Identifier: BSD-2-Clause
"""Static checks must distinguish failed source from missing prerequisites."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    'static_check', Path(__file__).resolve().parents[1] / 'scripts/check-static.py')
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


def boundary_fixture(records):
    complete = [dict(review='fixture', reference='docs/review.md', owner='test',
                     follow_up='BG-056', **record) for record in records]
    return json.dumps(dict(schema='sys-init-native-boundaries-v1', scope='test', records=complete))


class StaticTests(unittest.TestCase):
    def test_compile_rejects_context_error_without_execution(self):
        with self.assertRaises(SyntaxError):
            check.check_python(b'return 1\n', 'bad.py')
        check.check_python(b'raise RuntimeError("must not execute")\n', 'safe.py')

    def test_format_difference_rejected(self):
        with patch.object(check, 'command', return_value=b'fn main() {}\n'):
            with self.assertRaisesRegex(ValueError, 'changes required'):
                check.check_rust(b'fn main(){}\n', Path('host.rs'), Path('tool'), [])

    def test_empty_scope_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, 'empty'):
                check.sources(Path(directory), dict(python_roots=[], python_top_level=[],
                                                    rust_sources=[]))

    def test_oversized_input_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'a.py').write_bytes(b'x' * (check.MAX_FILE + 1))
            (root / 'a.rs').write_bytes(b'')
            with self.assertRaisesRegex(ValueError, '1 MiB'):
                check.sources(root, dict(python_roots=['.'], python_top_level=[],
                                         rust_sources=['a.rs']))

    def test_digest_mismatch_denies_before_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            tool = Path(directory) / 'tool'
            tool.write_bytes(b'changed executable')
            with patch.object(check, 'command') as execute:
                with self.assertRaises(check.Blocked):
                    check.identify_tool(tool, '0' * 64, 'version')
                execute.assert_not_called()

    def test_missing_and_wrong_version_are_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            tool = Path(directory) / 'tool'
            with self.assertRaises(check.Blocked):
                check.identify_tool(tool, '', '')
            tool.write_bytes(b'tool')
            with patch.object(check, 'command', return_value=b'wrong version'):
                with self.assertRaises(check.Blocked):
                    check.identify_tool(tool, check.digest(b'tool'), 'expected version')

    def test_timeout_is_blocked_and_nonzero_is_failure(self):
        with self.assertRaises(check.Blocked):
            check.command([check.sys.executable, '-c', 'import time; time.sleep(30)'], timeout=0.1)
        with self.assertRaisesRegex(ValueError, 'tool failed'):
            check.command([check.sys.executable, '-c', 'raise SystemExit(1)'])

    def test_output_limit_and_literal_input(self):
        with self.assertRaisesRegex(ValueError, 'output exceeds'):
            check.command([check.sys.executable, '-c', 'print("x" * 2000)'], limit=100)
        data = b'$(must remain literal)\n'
        self.assertEqual(check.command([check.sys.executable, '-c',
                         'import sys; sys.stdout.buffer.write(sys.stdin.buffer.read())'], data), data)

    def test_clippy_rejects_real_lint_in_private_tree(self):
        tool = Path(check.command(['rustup', 'which', '--toolchain', '1.98.0',
                                   'clippy-driver']).decode().strip())
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'tests/probe.rs'
            settings = dict(rust_sources=['tests/probe.rs'], clippy_modules=[],
                            clippy_args=['--edition=2024', '--test', '--emit=metadata',
                                         '-D', 'clippy::all'])
            invalid = b'#[test] fn probe() { let x = 1u32; let y = x.clone(); assert_eq!(y, 1); }'
            with self.assertRaisesRegex(ValueError, 'clone_on_copy'):
                check.check_clippy(root, {source: invalid}, tool, settings)
            valid = b'#[test] fn probe() { let x = std::hint::black_box(1); assert_eq!(x, 1); }'
            self.assertEqual(check.check_clippy(root, {source: valid}, tool, settings),
                             {'tests/probe.rs': ''})
            self.assertFalse(source.exists(), 'fixture must not write the original source')

    def test_boundary_source_and_coverage_changes_require_review(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'prototypes').mkdir()
            (root / 'docs').mkdir()
            source = root / 'prototypes/probe.rs'
            raw = b'unsafe { boundary(); }\n'
            source.write_bytes(raw)
            record = dict(file='prototypes/probe.rs', sha256=check.digest(raw),
                          sites=[dict(line=1, text='unsafe { boundary(); }')])
            inventory = root / 'docs/native-boundaries.json'
            inventory.write_text(boundary_fixture([record]))
            self.assertEqual(check.check_boundaries(root), 1)
            source.write_bytes(raw + b'// changed obligation\n')
            with self.assertRaisesRegex(ValueError, 'source changed'):
                check.check_boundaries(root)
            source.write_bytes(raw)
            inventory.write_text(boundary_fixture([]))
            with self.assertRaisesRegex(ValueError, 'invalid record list'):
                check.check_boundaries(root)

    def test_help_version_and_usage(self):
        for option, code in [('--help', 0), ('--version', 0), ('--unknown', 64)]:
            result = subprocess.run([check.sys.executable, check.__file__, option],
                                    capture_output=True, timeout=5)
            self.assertEqual(result.returncode, code)
            self.assertTrue(result.stdout if code == 0 else result.stderr)
            self.assertFalse(result.stderr if code == 0 else result.stdout)
