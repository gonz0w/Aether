#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Pure create-profile controls; no container side effects."""
import runpy
import unittest

transform = runpy.run_path('experiments/qemu-termios/build.py')['build_create_args']
BASE = ['create', '--name', 'fixture', '--read-only', '--user=65534:65534',
        '--memory=512m', '--pids-limit=32', '--network=none', '--pull=never',
        '--cap-drop=all', '--security-opt=no-new-privileges', '--mount',
        'type=bind,src=/fixture,dst=/fixture,ro=true', '--entrypoint',
        '/bin/sh', 'image-pin', '/fixture/build.sh']


class ProfileTests(unittest.TestCase):
    def test_selected_changes_only(self):
        result = transform(BASE)
        expected = ['create', '--name', 'fixture', '--user=0:0', '--memory=1536m',
                    '--pids-limit=128', '--network=none', '--pull=never',
                    '--cap-drop=all', '--security-opt=no-new-privileges', '--mount',
                    'type=bind,src=/fixture,dst=/fixture,ro=true', '--cpus=2',
                    '--cap-add=CHOWN,DAC_OVERRIDE,FOWNER,SETUID,SETGID',
                    '--env=LC_ALL=C', '--env=PATH=/usr/sbin:/usr/bin:/sbin:/bin',
                    '--entrypoint', '/bin/sh', 'image-pin', '/fixture/build.sh']
        self.assertEqual(result, expected)
        self.assertIn('--read-only', BASE)

    def test_profile_drift(self):
        for flag in ['--read-only', '--user=65534:65534', '--memory=512m',
                     '--pids-limit=32', '--network=none', '--pull=never',
                     '--cap-drop=all', '--security-opt=no-new-privileges']:
            with self.subTest(flag=flag):
                with self.assertRaises(ValueError):
                    transform([x for x in BASE if x != flag])
                with self.assertRaises(ValueError):
                    transform(BASE + [flag])

    def test_wrong_command(self):
        with self.assertRaises(ValueError):
            transform(['start', 'fixture'])


if __name__ == '__main__':
    unittest.main()
