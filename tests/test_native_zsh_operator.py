# SPDX-License-Identifier: BSD-2-Clause
"""Actual operator build selection and denials; no image or guest.

Run python3 -B -m unittest discover -s tests -p test_native_zsh_operator.py -v.
"""
import ast
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ZshOperatorBuild(unittest.TestCase):
    def test_actual_selected_and_default_profiles_and_required_closure(self):
        tree = ast.parse((ROOT / 'scripts/fs_session.py').read_text())
        flags = next(node.value for node in tree.body if isinstance(node, ast.Assign)
                     and any(isinstance(target, ast.Name) and target.id == 'FLAGS'
                             for target in node.targets))
        flags = ast.literal_eval(flags.func.value).split()
        flags += ['native-fs-session-init', 'native-fs-owner-data', 'native-fs-owner-stack',
                  'native-fs-application-profile', 'native-zsh-terminfo',
                  'native-tty-mode-probe', 'native-tty-signal-probe',
                  'native-signal-mask-delivery', 'native-zsh-external',
                  'native-signal-suspend', 'native-zsh-file-exec']
        with tempfile.TemporaryDirectory(prefix='aether-zsh-operator-build-') as directory:
            output = Path(directory)
            image = output / 'unexecuted.bin'
            image.write_bytes(b'\0')
            base = {'smp': 'false', 'native-c-image': str(image),
                    **dict.fromkeys(flags, 'true')}
            selected = {**base, 'native-zsh-operator': 'true'}
            cases = [('default', {}, False), ('old-file-exec', base, False),
                     ('operator', selected, False),
                     ('missing-file-exec', {**selected, 'native-zsh-file-exec': 'false'}, True),
                     ('not-private', {**selected, 'release-artifact': 'true'}, True),
                     ('smp', {**selected, 'smp': 'true'}, True),
                     ('incompatible-drain', {**selected, 'native-af09-drain': 'file_prefix'}, True),
                     ('standalone', {'native-zsh-operator': 'true'}, True)]
            for name, options, rejected in cases:
                with self.subTest(case=name):
                    command = ['zig', 'build', '--help', '--cache-dir', str(output / 'cache'),
                               '--global-cache-dir', str(output / 'global')]
                    command += ['-D' + key + '=' + value for key, value in options.items()]
                    result = subprocess.run(command, cwd=ROOT, capture_output=True,
                                            text=True, timeout=60)
                    self.assertEqual(result.returncode != 0, rejected,
                                     result.stdout + result.stderr)
                    if name in ('missing-file-exec', 'standalone'):
                        self.assertIn('Zsh operator requires the selected private file-exec closure',
                                      result.stdout + result.stderr)
