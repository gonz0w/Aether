# SPDX-License-Identifier: BSD-2-Clause
"""Small structural denials for the actual AF09 native Rust builder."""
from pathlib import Path
import runpy
import unittest

builder = runpy.run_path(str(Path(__file__).with_name('home_engine_build.py')))
PROFILE = tuple('fs_' + name for name in ('namespace', 'lifetimes', 'mixed', 'wait', 'bulk',
    'runtime', 'activation', 'names', 'directories', 'metadata', 'directory_contexts',
    'home', 'home_wire', 'home_native', 'home_activation', 'home_probe_three'))
SERVICE = '0000000000000000 T aether_fs_home_run\n'
LAUNCH = '0000000000000000 T main\n0000000000000010 T aether_fs_home_launch_serve\n'


class NativeBuildContract(unittest.TestCase):
    def test_exact_profile_and_object_exports(self):
        self.assertEqual(builder['validate_profile'](PROFILE), PROFILE)
        builder['validate_symbols'](SERVICE, LAUNCH)

    def test_every_missing_profile_is_rejected(self):
        for index in range(len(PROFILE)):
            with self.subTest(index=index), self.assertRaisesRegex(ValueError, 'AF09 profile'):
                builder['validate_profile'](PROFILE[:index] + PROFILE[index + 1:])

    def test_duplicate_extra_and_old_profiles_reject(self):
        for values in ((*PROFILE, PROFILE[-1]), (*PROFILE, 'fs_cwd'), (*PROFILE[:-1], 'fs_metadata')):
            with self.subTest(values=values), self.assertRaisesRegex(ValueError, 'AF09 profile'):
                builder['validate_profile'](values)

    def test_missing_weak_duplicate_and_wrong_object_exports_reject(self):
        for service, launch in (('', LAUNCH), (SERVICE.replace(' T ', ' W '), LAUNCH),
                (SERVICE + SERVICE, LAUNCH), (SERVICE, ''), (SERVICE + LAUNCH, SERVICE),
                (SERVICE, LAUNCH + SERVICE)):
            with self.subTest(service=service, launch=launch), self.assertRaisesRegex(ValueError, 'AF09 strong'):
                builder['validate_symbols'](service, launch)

    def test_old_service_and_launch_symbols_reject(self):
        for name in ('aether_fs_metadata_run', 'aether_fs_service_run', 'aether_fs_engine_run',
                'aether_fs_launch_serve'):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'AF09 old'):
                builder['validate_symbols'](SERVICE + '0000000000000020 T ' + name + '\n', LAUNCH)


if __name__ == '__main__':
    unittest.main()
