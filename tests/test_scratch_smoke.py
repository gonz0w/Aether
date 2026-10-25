# SPDX-License-Identifier: BSD-2-Clause
"""Counterexamples for the independent scratch native oracle."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from scratch_smoke import check_scratch, consumer_inputs


def serial():
    inputs = consumer_inputs()
    lines = []
    for g in range(1, 4):
        lines.append(f'NATIVE MEMORY admitted slot=0 generation={g} used=23 remaining=105')
        for slot, epoch, status in [(2, 5*g-4, 2), (2, 5*g-3, 0),
                                    (2, 5*g-2, 0), (2, 5*g-1, 0),
                                    (3, g, 0), (4, g, 0), (2, 5*g, 0), (0, g, 0)]:
            if slot in (3,4) or (slot == 2 and epoch in (2,3,5,7,8,10,12,13,15)):
                lines.append(f'NATIVE MEMORY admitted slot={slot} generation={epoch} used=23 remaining=105')
            lines.append(f'NATIVE terminal slot={slot} generation={epoch} kind=1 detail={status}')
        lines.append(f'NATIVE SESSION generation={g} copies=7 execs=5 stdout={inputs["expected.stdout"].hex()} stderr={inputs["expected.stderr"].hex()}')
    lines += ['NATIVE supervisor result=100 reclaimed=24', 'AETHER NATIVE CONNECTIONS PASS']
    return '\n'.join(lines)


class ScratchOracleTests(unittest.TestCase):
    def check(self, value):
        check_scratch(value, 'composed', consumer_inputs())

    def test_complete_bounded_witness(self):
        self.check(serial())

    def test_authority_status_admission_and_identity_counterexamples(self):
        good = serial()
        for bad in [good.replace('detail=2', 'detail=0', 1),
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
        b = next(i for i, row in enumerate(rows) if 'slot=2 generation=2 kind' in row)
        rows[a], rows[b] = rows[b], rows[a]
        for bad in ['\n'.join(rows), good.replace('stdout=64', 'stdout=65', 1),
                    good.replace('execs=5', 'execs=6', 1),
                    good.replace('reclaimed=24', 'reclaimed=23')]:
            with self.assertRaises(RuntimeError):
                self.check(bad)

    def test_early_close_requires_exact_diagnostic_and_confirmed_cleanup(self):
        diagnostic = b'sh: 7: printf: printf: I/O error'
        lines = [
            'NATIVE MEMORY admitted slot=0 generation=1 used=73 remaining=55',
            'NATIVE terminal slot=0 generation=1 kind=1 detail=141',
            'NATIVE SESSION generation=1 copies=0 execs=0 stdout= stderr=' + diagnostic.hex(),
            'NATIVE supervisor result=2885 reclaimed=1',
            'AETHER PANIC: native C profile rejected',
        ]
        good = '\n'.join(lines)
        check_scratch(good, 'early-close', consumer_inputs())
        for bad in [good.replace('detail=141', 'detail=63'),
                    good.replace(diagnostic.hex(), ''),
                    good.replace('reclaimed=1', 'reclaimed=0')]:
            with self.assertRaises(RuntimeError):
                check_scratch(bad, 'early-close', consumer_inputs())
