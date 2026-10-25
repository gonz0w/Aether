# SPDX-License-Identifier: BSD-2-Clause
"""Reject stale admission diagnostics in the native memory evidence oracle."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from memory_smoke import check_budget, check_fp_rejection


class MemoryBudget(unittest.TestCase):
    def test_selected_profile(self):
        for large, free in [(False, 104), (True, 2024)]:
            check_budget(f'NATIVE MEMORY admitted slot=0 generation=1 used=24 remaining={free}\n', large)

    def test_old_large_diagnostic_rejects(self):
        with self.assertRaisesRegex(RuntimeError, 'admission budget differs'):
            check_budget('NATIVE MEMORY admitted slot=0 generation=1 used=24 remaining=104\n', True)

    def test_missing_and_inconsistent_admissions_reject(self):
        for text in ['', 'NATIVE MEMORY admitted slot=0 generation=1 used=24 remaining=103\n',
                     'NATIVE MEMORY admitted slot=0 generation=1 used=0 remaining=128\n']:
            with self.assertRaisesRegex(RuntimeError, 'admission budget differs'):
                check_budget(text, False)


class FloatingPointRejection(unittest.TestCase):
    @staticmethod
    def log(first, second):
        rows = []
        for slot, status in enumerate((first, second)):
            rows.append(f'NATIVE terminal slot={slot} generation=0 kind=1 detail={status}')
        for slot, status in enumerate((first, second)):
            output = 24 if status == 0 else 0
            rows.append(f'NATIVE terminal task={slot} status={status} output={output} fs=206000 ticks=10')
        return '\n'.join(rows) + '\n'

    def test_either_or_both_contexts_detect_missing_restore(self):
        for statuses in [(174, 0), (0, 174), (174, 174)]:
            check_fp_rejection(self.log(*statuses))

    def test_wrong_failure_or_incomplete_execution_rejects(self):
        for text in [self.log(0, 0), self.log(174, 108), '',
                     self.log(174, 0).replace('slot=1', 'slot=0'),
                     self.log(174, 0).replace('generation=0', 'generation=1'),
                     self.log(174, 0).replace('kind=1', 'kind=2'),
                     self.log(174, 0).replace('status=174', 'status=0'),
                     self.log(174, 0).replace('output=24', 'output=0')]:
            with self.assertRaises(RuntimeError):
                check_fp_rejection(text)
