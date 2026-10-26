# SPDX-License-Identifier: BSD-2-Clause
"""Small structural denials for the actual AF09 native Rust builder."""
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest import mock

builder = runpy.run_path(str(Path(__file__).with_name('home_engine_build.py')))
PROFILE = tuple('fs_' + name for name in ('namespace', 'lifetimes', 'mixed', 'wait', 'bulk',
    'runtime', 'activation', 'names', 'directories', 'metadata', 'directory_contexts',
    'home', 'home_wire', 'home_native', 'home_activation', 'home_probe_three'))
SERVICE = '0000000000000000 T aether_fs_home_run\n'
LAUNCH = '0000000000000000 T main\n0000000000000010 T aether_fs_home_launch_serve\n'


class NativeBuildContract(unittest.TestCase):
    def test_drain_profile_replaces_only_the_three_count_selection(self):
        cases = ('file_prefix', 'exec_prefix', 'fork_prefix', 'stream', 'no_ack',
                 'partial_ack', 'exit_deadline', 'pending_fragment')
        expected = (*PROFILE[:-1], 'fs_af09_drain')
        self.assertEqual(builder['DRAIN_PROFILE'], expected)
        for case_id, case in enumerate(cases, 1):
            with self.subTest(case=case):
                self.assertEqual(builder['drain_selection'](case), case_id)
                self.assertEqual(builder['validate_profile'](expected, drain_case=case), expected)
                with self.assertRaisesRegex(ValueError, 'AF09 profile'):
                    builder['validate_profile'](PROFILE, drain_case=case)
        self.assertEqual(builder['drain_selection']('none'), 0)

    def test_invalid_case_rejects_before_owned_work_or_process_effects(self):
        for case in (None, '', 'FILE_PREFIX', 'none ', 1, True, [], 'unknown'):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory:
                process = mock.Mock()
                with self.assertRaisesRegex(ValueError, 'AF09 drain case'):
                    builder['build'](Path(directory), process, {}, 0, {}, drain_case=case)
                self.assertEqual(list(Path(directory).iterdir()), [])
                process.assert_not_called()
                process.clean_env.assert_not_called()
                process.run.assert_not_called()

    def test_drain_profile_missing_duplicate_and_mixed_flags_reject(self):
        selected = (*PROFILE[:-1], 'fs_af09_drain')
        values = [selected[:i] + selected[i + 1:] for i in range(len(selected))]
        values += [(*selected, 'fs_home_probe_three'), (*selected, 'fs_af09_drain')]
        for profile in values:
            with self.subTest(profile=profile), self.assertRaisesRegex(ValueError, 'AF09 profile'):
                builder['validate_profile'](profile, drain_case='stream')

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
