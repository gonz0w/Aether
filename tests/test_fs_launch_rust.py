# SPDX-License-Identifier: BSD-2-Clause
"""Actual userland owner, strict host/native compilation and semantic omissions."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
OWNER = ROOT / 'userland/experiments/filesystem-service/launch-owner.rs'


class RustLaunchOwner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-launch-rust-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.out = Path(cls.temp.name)
        cls.source = OWNER.read_text()

    def command(self, argv, expected=0):
        run = subprocess.run(list(map(str, argv)), capture_output=True, text=True, timeout=60)
        self.assertEqual(run.returncode, expected, run.stdout+run.stderr)
        return run.stdout+run.stderr

    def test_actual_owner_tests_format_clippy_and_native_object(self):
        self.command(['rustfmt', '+1.98.0', '--edition=2021', '--check', OWNER, OWNER.with_name('launch-owner-tests.rs')])
        for tool in ('rustc', 'clippy-driver'):
            self.command(['rustup', 'run', '1.98.0', tool, '--edition=2021', '-Dwarnings',
                          '-Dunsafe_op_in_unsafe_fn', '--test', OWNER, '-o', self.out/tool])
        log = self.command([self.out/'rustc', '--test-threads=1'])
        self.assertIn('5 passed; 0 failed', log)
        self.command(['rustc', '+1.98.0', '--edition=2021', '--target=x86_64-unknown-none',
                      '--crate-type=lib', '--emit=obj', '-Cpanic=abort', '-Copt-level=2',
                      '-Crelocation-model=static', '-Cno-redzone=yes', '-Dwarnings',
                      '-Dunsafe_op_in_unsafe_fn', OWNER, '-o', self.out/'owner.o'])
        llvm = Path('/opt/homebrew/Cellar/llvm@21/21.1.8/bin')
        names = self.command([llvm/'llvm-nm', '--defined-only', self.out/'owner.o'])
        for name in ('main', 'aether_fs_launch_serve'):
            self.assertEqual(sum(line.split()[-1:] == [name] for line in names.splitlines()), 1)
        imports = self.command([llvm/'llvm-nm', '-u', self.out/'owner.o'])
        for name in ('aether_fs_engine_run', 'aether_fs_directories_run', 'getauxval'):
            self.assertIn(name, imports)

    def test_compiling_omissions_fail_actual_owner_tests(self):
        for old, new in (
            ('if error != 0 {', 'if error != 0 { return 0;'),
            ('state.phases != FINISHED', '(state.phases != FINISHED && false)'),
            ('service.writer_close != 0', '(service.writer_close != 0 && false)'),
            ('if state.phases & ENTERED == 0 {', 'if state.phases & ENTERED != 0 {'),
            ('|| state.phases & ENTERED == 0', '|| (state.phases & ENTERED == 0 && false)'),
        ):
            with self.subTest(omission=old):
                self.assertEqual(self.source.count(old), 1)
                # Preserve the trusted test module location without copying a tree.
                source = self.source.replace(old, new, 1).replace(
                    '#[path = "launch-owner-tests.rs"]', '#[path = "'+str(OWNER.with_name('launch-owner-tests.rs'))+'"]')
                path = self.out/'changed.rs'
                path.write_text(source)
                # Intentional dead-code controls remain compiled, but warning
                # lint is separate from this semantic rejection witness.
                self.command(['rustc', '+1.98.0', '--edition=2021', '--test', path, '-o', self.out/'broken'])
                log = self.command([self.out/'broken', '--test-threads=1'], expected=101)
                self.assertIn('test result: FAILED.', log)


if __name__ == '__main__':
    unittest.main()
