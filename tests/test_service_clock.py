# SPDX-License-Identifier: BSD-2-Clause
"""Reject incomplete or forged full-owner clock qualification observations."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from service_clock_smoke import check_trace


class ServiceClockTraceTests(unittest.TestCase):
    def trace(self, mode=0, stopped=False):
        lines = []
        for owner, generation, count in ((0, 1, 82), (1, 1, 2), (0, 2, 82)):
            total = 8192 if owner == 0 else 128
            lines.append(f'NATIVE MEMORY admitted slot={owner} generation={generation} used=20 remaining={total-20}')
            deadline = 1000000 * (generation + owner)
            for _ in range(count):
                lines.append(f'NATIVE CLOCK park task={owner} start=1000 deadline={deadline}')
            if mode != 1 and not (stopped and owner == 0 and generation == 1):
                for _ in range(count):
                    lines.append(f'NATIVE CLOCK timeout task={owner} now={deadline+1000} elapsed=100000')
        lines += ['NATIVE CLOCK workers scans=100 max_contexts=89 max_ns=8000000 valid=1',
                  'NATIVE supervisor result=100 reclaimed=3']
        return '\n'.join(lines) + '\n'

    def test_full_cohort_wake_and_stopped_replacement(self):
        self.assertEqual(check_trace(self.trace(), 0)['timeouts'], 166)
        self.assertEqual(check_trace(self.trace(1), 1)['timeouts'], 0)
        self.assertEqual(check_trace(self.trace(stopped=True), 0, True)['timeouts'], 84)

    def test_missing_worker_registration(self):
        line = 'NATIVE CLOCK park task=0 start=1000 deadline=1000000\n'
        with self.assertRaisesRegex(RuntimeError, 'registrations'):
            check_trace(self.trace().replace(line, '', 1), 0)

    def test_changed_cohort_deadline(self):
        with self.assertRaisesRegex(RuntimeError, 'cohort deadline'):
            check_trace(self.trace().replace('deadline=1000000', 'deadline=1000001', 1), 0)

    def test_peer_cannot_substitute_service_timeout(self):
        with self.assertRaisesRegex(RuntimeError, 'owner-specific'):
            check_trace(self.trace().replace('timeout task=0', 'timeout task=1', 1), 0)

    def test_early_timeout_with_positive_elapsed(self):
        with self.assertRaisesRegex(RuntimeError, 'early, late'):
            check_trace(self.trace().replace('now=1001000', 'now=999999', 1), 0)

    def test_scan_failure_and_unbounded_cost(self):
        for old, new in (('valid=1', 'valid=0'), ('scans=100', 'scans=0'),
                         ('max_contexts=89', 'max_contexts=93'),
                         ('max_ns=8000000', 'max_ns=1000000000')):
            with self.subTest(value=new), self.assertRaisesRegex(RuntimeError, 'budget rejection'):
                check_trace(self.trace().replace(old, new), 0)

    def test_replacement_cannot_widen_backing(self):
        with self.assertRaisesRegex(RuntimeError, 'accounting'):
            check_trace(self.trace().replace('slot=0 generation=2 used=20 remaining=8172',
                                            'slot=0 generation=2 used=20 remaining=8173'), 0)

    def test_success_marker_cannot_replace_reclamation(self):
        with self.assertRaisesRegex(RuntimeError, 'cleanup/replacement'):
            check_trace(self.trace().replace('reclaimed=3', 'reclaimed=0'), 0)
