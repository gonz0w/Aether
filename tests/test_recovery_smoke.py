# SPDX-License-Identifier: BSD-2-Clause
"""Counterexamples for the recovery observer; no native acceptance implied."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'scripts'))
import recovery_smoke as recovery


class RecoveryObservationTests(unittest.TestCase):
    def setUp(self):
        self.inputs = recovery.consumer_inputs()
        self.lines = []
        for g in range(1, 4):
            a, b = 4*(g-1), 2*(g-1)
            for slot, epoch, status in [(3,b+1,0),(2,a+1,42),(2,a+2,0),
                                       (2,a+3,0),(3,b+2,0),(4,g,0),(2,a+4,0),(0,g,0)]:
                self.lines.append(f'NATIVE terminal slot={slot} generation={epoch} kind=1 detail={status}')
            self.lines.append(f"NATIVE SESSION generation={g} copies=7 execs=6 stdout={self.inputs['expected.stdout'].hex()} stderr={self.inputs['expected.stderr'].hex()}")
        self.lines += ['NATIVE MEMORY admitted slot=0']*21
        self.lines += ['NATIVE supervisor result=100 reclaimed=24', 'AETHER NATIVE CONNECTIONS PASS']

    def check(self, lines):
        return recovery.check_recovery('\n'.join(lines)+'\n', 'composed', self.inputs)

    def test_complete_recovery_and_lifetimes(self):
        self.assertEqual(len(self.check(self.lines)), 3)

    def test_lost_wrong_duplicate_and_premature_terminals(self):
        for i in range(8):
            bad = self.lines.copy(); bad.pop(i)
            with self.assertRaises(RuntimeError): self.check(bad)
        for change in ('kind=3 detail=143', 'kind=1 detail=0', 'kind=1 detail=99'):
            bad = self.lines.copy(); bad[1] = bad[1].replace('kind=1 detail=42', change)
            with self.assertRaises(RuntimeError): self.check(bad)
        bad = self.lines.copy(); bad[0] = bad[1]
        with self.assertRaises(RuntimeError): self.check(bad)
        for i,j in ((0,2),(2,3),(5,6),(6,7),(8,9)):
            bad = self.lines.copy(); bad[i],bad[j] = bad[j],bad[i]
            with self.assertRaises(RuntimeError): self.check(bad)

    def test_malformed_terminal_cannot_hide_as_unparsed_diagnostic(self):
        with self.assertRaises(RuntimeError):
            self.check(self.lines + ['NATIVE terminal slot=2 generation=oops'])

    def test_streams_observations_and_completion_cannot_be_forged(self):
        for old,new in [('stdout=', 'stdout=00'), ('stderr=', 'stderr=00'),
                        ('copies=7','copies=6'), ('execs=6','execs=5')]:
            bad = self.lines.copy();bad[8] = bad[8].replace(old,new)
            with self.assertRaisesRegex(RuntimeError,'RECOVERY stream mismatch'): self.check(bad)
        for index in (8,17,26,27,len(self.lines)-2,len(self.lines)-1):
            bad = self.lines.copy();bad.pop(index)
            with self.assertRaises(RuntimeError): self.check(bad)
        for extra in ('PANIC', self.lines[-1], self.lines[-2], self.lines[8]):
            with self.assertRaises(RuntimeError): self.check(self.lines+[extra])

if __name__ == '__main__':
    unittest.main()
