# SPDX-License-Identifier: BSD-2-Clause
"""Counterexamples for the host SESSION observer, not native execution evidence."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'scripts'))
sys.path.insert(0, str(Path(__file__).parent))
import session_smoke as session

class SessionObservationTests(unittest.TestCase):
    def setUp(self):
        self.inputs = session.consumer_inputs()
        out, err = (self.inputs['expected.' + name].hex() for name in ('stdout', 'stderr'))
        self.rows = [f'NATIVE SESSION generation={g} copies=9 execs=7 stdout={out} stderr={err}' for g in range(1, 4)]
        self.ids = [(0, g) for g in range(1, 4)] + [(2, g) for g in range(1, 16)] + [(s, g) for s in (3, 4) for g in range(1, 7)]
        self.terminals = [f'NATIVE terminal slot={s} generation={g} kind=1 detail=0' for s, g in self.ids]
        self.lines = self.terminals + self.rows + ['NATIVE MEMORY admitted slot=0'] * 24 + ['NATIVE supervisor result=100 reclaimed=30', 'AETHER NATIVE CONNECTIONS PASS']

    def check(self, lines):
        return session.check_session('\n'.join(lines)+'\n', 'composed', self.inputs)

    def test_complete_stream_and_lifetimes(self):
        self.assertEqual(len(self.check(self.lines)), 3)

    def test_missing_duplicate_reordered_and_malformed_observations(self):
        for lines in [self.lines[1:], self.lines[:1] + self.lines, self.lines[:30] + [self.lines[31], self.lines[30]] + self.lines[32:]]:
            with self.assertRaises(RuntimeError): self.check(lines)
        for replacement in ['generation=0', 'generation=4', 'generation=01']:
            with self.assertRaises(RuntimeError): self.check(self.lines[:30]+[self.lines[30].replace('generation=1', replacement)]+self.lines[31:])
        with self.assertRaises(RuntimeError): self.check([self.lines[30]+'a']+self.lines[:30]+self.lines[31:])

    def test_stdout_stderr_and_counter_corruption(self):
        for token, value in [('stdout=', 'stdout=00'), ('stderr=', 'stderr=00'), ('copies=9', 'copies=8'), ('execs=7', 'execs=8')]:
            with self.assertRaisesRegex(RuntimeError, 'SESSION stream mismatch'):
                self.check(self.lines[:30]+[self.lines[30].replace(token, value)]+self.lines[31:])

    def test_guest_success_cannot_hide_incomplete_or_bad_lifetimes(self):
        for index in (3, len(self.lines)-3, len(self.lines)-2, len(self.lines)-1):
            with self.assertRaises(RuntimeError): self.check(self.lines[:index]+self.lines[index+1:])
        for mutation in ['kind=3 detail=143', 'kind=1 detail=91']:
            lines = self.lines.copy();lines[3] = lines[3].replace('kind=1 detail=0', mutation)
            with self.assertRaises(RuntimeError): self.check(lines)
        with self.assertRaises(RuntimeError): self.check(self.lines + ['PANIC'])
        with self.assertRaises(RuntimeError): self.check(self.lines + [self.lines[-2]])
        with self.assertRaises(RuntimeError): self.check([self.lines[-2]] + self.lines[:-2] + self.lines[-1:])

    def test_identity_reuse_and_encoded_marker_cannot_forge_evidence(self):
        lines = self.lines.copy();lines[4] = lines[3]
        with self.assertRaises(RuntimeError): self.check(lines)
        raw = b'NATIVE supervisor result=100 reclaimed=30\n'
        row = 'NATIVE SESSION generation=1 copies=1 execs=1 stdout='+raw.hex()+' stderr='
        self.assertEqual(session.observations(row), [(1, 1, 1, raw, b'')])
        with self.assertRaises(RuntimeError): self.check([row])

if __name__ == '__main__': unittest.main()
