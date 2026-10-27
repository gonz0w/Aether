# SPDX-License-Identifier: BSD-2-Clause
"""Exercise the approved AF09 build graph only; --help constructs no native image."""
import ast
import hashlib
from pathlib import Path
import sys
import tempfile
import time
import unittest

from test_build_policy import NEGATIVE
from test_native_cleanup import compiler_file_limit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'sys-init/scripts'))
from bounded_capture import run_capture

CASES = ('file_prefix', 'exec_prefix', 'fork_prefix', 'stream', 'no_ack',
         'partial_ack', 'exit_deadline', 'pending_fragment')


class Af09BuildGuard(unittest.TestCase):
    records = []

    @classmethod
    def setUpClass(cls):
        cls.deadline = time.monotonic() + 300
        cls.addClassCleanup(cls.finish)
        cls.file_limit = compiler_file_limit(cls)
        cls.directory = tempfile.TemporaryDirectory(prefix='aether-af09-build-')
        cls.addClassCleanup(cls.directory.cleanup)
        cls.out = Path(cls.directory.name)
        cls.image = cls.out / 'unexecuted-envelope.bin'
        cls.image.write_bytes(b'\0')
        tree = ast.parse((ROOT / 'scripts/fs_session.py').read_text())
        flags = [n.value for n in tree.body if isinstance(n, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id == 'FLAGS' for t in n.targets)]
        if len(flags) != 1:
            raise AssertionError('one existing filesystem closure required')
        cls.flags = ast.literal_eval(flags[0].func.value).split()
        cls.flags += ['native-fs-session-init', 'native-fs-owner-data', 'native-fs-owner-stack']
        cls.inputs = {n: hashlib.sha256((ROOT / n).read_bytes()).hexdigest() for n in
                      ('build.zig', 'kernel/native_af09_drain.zig', 'scripts/fs_session.py',
                       'tests/test_af09_build_guard.py', 'tests/test_build_policy.py')}

    @classmethod
    def finish(cls):
        if hasattr(cls, 'inputs'):
            for name, value in cls.inputs.items():
                if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != value:
                    raise AssertionError('AF09 guard source changed: ' + name)
        if time.monotonic() > cls.deadline:
            raise AssertionError('AF09 build-guard aggregate expired after cleanup')

    def invoke(self, extras=(), *, remove=(), selected='file_prefix', wanted=0, marker=None):
        flags = [n for n in self.flags if n not in remove]
        options = {'smp': 'false', 'native-c-image': str(self.image),
                   **{name: 'true' for name in flags}}
        if selected is not None:
            options['native-af09-drain'] = selected
        for item in extras:
            if not item.startswith('-D') or '=' not in item:
                raise AssertionError('one explicit build option required')
            key, value = item[2:].split('=', 1)
            options[key] = value
        command = ['zig', 'build', '--help', '--cache-dir', str(self.out / 'cache'),
                   '--global-cache-dir', str(ROOT / '.zig-cache/global'),
                   *['-D' + key + '=' + value for key, value in options.items()]]
        remaining = self.deadline - time.monotonic()
        self.assertGreater(remaining, 0)
        result = run_capture(command, cwd=ROOT, timeout=min(180, remaining), limit=4 * 1024**2)
        self.records.append(dict(argv=command, exit=result.returncode,
                                 stdout_sha256=hashlib.sha256(result.stdout.encode()).hexdigest(),
                                 stderr=result.stderr[-7000:]))
        if wanted:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        if marker:
            self.assertIn(marker, result.stdout + result.stderr)
        return result

    def test_closed_cases_and_explicit_omitted_none(self):
        for name in (None, 'none', *CASES):
            with self.subTest(case=name):
                self.invoke(selected=name, marker='native-af09-drain')
        for name in ('', 'FILE_PREFIX', 'unknown', '1'):
            with self.subTest(case=name):
                self.invoke(selected=name, wanted=1, marker='unknown native-af09-drain case')

    def test_selected_profile_release_application_smp_and_lifetime_denials(self):
        for name in ('native-fs-owner-stack', 'native-fs-owner-data',
                     'native-fs-session-init', 'native-fs-session'):
            with self.subTest(missing=name):
                self.invoke(remove=(name,), wanted=1)
        for args in (['-Drelease-artifact=true'], ['-Dnative-fs-application-profile=true'],
                     ['-Dsmp=true'], ['-Dnative-service-lifetime=true']):
            with self.subTest(args=args):
                self.invoke(args, wanted=1)

    def test_every_intentional_negative_control_is_rejected(self):
        for name in sorted(NEGATIVE):
            with self.subTest(control=name):
                self.invoke(['-D' + name + '=true'], wanted=1,
                            marker='AF09 diagnostic rejects negative-test option: ' + name)


if __name__ == '__main__':
    unittest.main()
