# SPDX-License-Identifier: BSD-2-Clause
"""Counterexamples for the independent failed-exec native oracle."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from failed_exec_smoke import check_failed_exec, consumer_inputs


def serial():
    inputs = consumer_inputs()
    lines = []
    for g in range(1, 4):
        lines.append(f'NATIVE MEMORY admitted slot=0 generation={g} used=23 remaining=105')
        for slot, epoch, status in [(2, 5*g-4, 127), (2, 5*g-3, 126),
                                    (2, 5*g-2, 0), (2, 5*g-1, 0),
                                    (3, g, 0), (4, g, 0), (2, 5*g, 0), (0, g, 0)]:
            if slot in (3,4) or (slot == 2 and epoch in (3,5,8,10,13,15)):
                lines.append(f'NATIVE MEMORY admitted slot={slot} generation={epoch} used=23 remaining=105')
            lines.append(f'NATIVE terminal slot={slot} generation={epoch} kind=1 detail={status}')
        lines.append(f'NATIVE SESSION generation={g} copies=7 execs=4 stdout={inputs["expected.stdout"].hex()} stderr={inputs["expected.stderr"].hex()}')
    lines += ['NATIVE supervisor result=100 reclaimed=24', 'AETHER NATIVE CONNECTIONS PASS']
    return '\n'.join(lines)


class FailedExecOracleTests(unittest.TestCase):
    def check(self, value):
        check_failed_exec(value, 'composed', consumer_inputs())

    def test_complete_bounded_witness(self):
        self.check(serial())

    def test_authority_status_admission_and_identity_counterexamples(self):
        good = serial()
        for bad in [good.replace('detail=127', 'detail=126', 1),
                    good.replace('generation=15 kind=1', 'generation=16 kind=1'),
                    good.replace('NATIVE MEMORY admitted slot=0 generation=1 used=23 remaining=105\n', '', 1),
                    good.replace('admitted slot=0 generation=1', 'admitted slot=2 generation=1', 1),
                    good + '\nNATIVE terminal slot=9 generation=1 kind=1 detail=0',
                    good + '\nNATIVE terminal malformed']:
            with self.assertRaises(RuntimeError):
                self.check(bad)

    def test_stream_and_phase_counterexamples(self):
        good = serial()
        rows = good.splitlines()
        a = next(i for i, row in enumerate(rows) if 'slot=2 generation=1 kind' in row)
        rows[a], rows[a+1] = rows[a+1], rows[a]
        for bad in ['\n'.join(rows), good.replace('stdout=65', 'stdout=64', 1),
                    good.replace('execs=4', 'execs=6', 1),
                    good.replace('reclaimed=24', 'reclaimed=23')]:
            with self.assertRaises(RuntimeError):
                self.check(bad)

    def test_closed_stderr_requires_cleanup_failure_not_guessed_shell_exit(self):
        prefix = b'exec errors ok\nargv ok\npipe data\nclosed ok\n'
        lines = ['NATIVE MEMORY admitted slot=0 generation=1 used=23 remaining=105']
        for slot, epoch, status in [(2,1,127),(2,2,126),(2,3,0),(2,4,0),
                                    (3,1,0),(4,1,0),(2,5,0),(0,1,141)]:
            if (slot,epoch) in {(2,3),(2,5),(3,1),(4,1)}:
                lines.append(f'NATIVE MEMORY admitted slot={slot} generation={epoch} used=23 remaining=105')
            lines.append(f'NATIVE terminal slot={slot} generation={epoch} kind=1 detail={status}')
        lines += [f'NATIVE SESSION generation=1 copies=7 execs=4 stdout={prefix.hex()} stderr=',
                  'NATIVE supervisor result=2865 reclaimed=8',
                  'AETHER PANIC: native C profile rejected']
        text='\n'.join(lines)
        check_failed_exec(text, 'stderr-error', consumer_inputs())
        for bad in [text.replace('detail=141','detail=57'),
                    text.replace('reclaimed=8','reclaimed=7'),
                    text + '\nAETHER NATIVE CONNECTIONS PASS']:
            with self.assertRaises(RuntimeError):
                check_failed_exec(bad, 'stderr-error', consumer_inputs())
