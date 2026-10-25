# SPDX-License-Identifier: BSD-2-Clause
"""Reject plausible-but-incomplete real-clock native traces."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from libc_clock_smoke import check_clock_trace, selected_cases


class LibcClockTraceTests(unittest.TestCase):
    def test_case_selection_preserves_profiles_and_rejects_empty_coverage(self):
        self.assertEqual([r[0] for r in selected_cases()],
                         ['real', 'repeat', 'early', 'disabled', 'legacy'])
        self.assertEqual([r[0] for r in selected_cases(True)],
                         ['real', 'repeat', 'early', 'old-bound'])
        self.assertEqual(selected_cases(True, 'old-bound')[0][-1], 341)
        for long_waits, name in ((False, 'old-bound'), (True, 'legacy'),
                                 (True, ''), (False, 'unknown')):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'unavailable'):
                selected_cases(long_waits, name)

    def trace(self):
        lines = []
        for owner in (0, 1):
            for generation in (1, 2):
                deadline = generation * 100000000
                for start in (1000, 2000):
                    lines.append(f'NATIVE CLOCK park task={owner} start={start} deadline={deadline}')
                for _ in range(2):
                    lines.append(f'NATIVE CLOCK timeout task={owner} now={deadline} elapsed=100000')
        return '\n'.join(lines)

    def test_actual_retry_receipts(self):
        self.assertEqual(check_clock_trace(self.trace())['same_deadline_retries'], 4)

    def test_restarted_deadline_cannot_pass(self):
        broken = self.trace().replace('start=2000 deadline=100000000',
                                      'start=2000 deadline=100002000')
        with self.assertRaisesRegex(RuntimeError, 'spurious retries'):
            check_clock_trace(broken)

    def test_one_owner_cannot_substitute_for_two(self):
        with self.assertRaisesRegex(RuntimeError, 'clock owner'):
            check_clock_trace(self.trace().replace('task=1', 'task=0'))

    def test_marker_without_timeouts_cannot_pass(self):
        broken = '\n'.join(line for line in self.trace().splitlines()
                           if 'timeout task=1' not in line) + '\nAETHER NATIVE C PASS'
        with self.assertRaises(RuntimeError):
            check_clock_trace(broken)

    def test_invalid_admission_cannot_pass(self):
        for replacement in ('0', '1000002001'):
            with self.subTest(deadline=replacement), self.assertRaisesRegex(RuntimeError, 'deadline'):
                check_clock_trace(self.trace().replace('start=2000 deadline=100000000',
                                                       'start=2000 deadline=' + replacement))

    def test_impossible_timeout_observation_cannot_pass(self):
        with self.assertRaisesRegex(RuntimeError, 'timeout observation'):
            check_clock_trace(self.trace().replace('elapsed=100000', 'elapsed=0'))
