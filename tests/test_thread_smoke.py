# SPDX-License-Identifier: BSD-2-Clause
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from thread_smoke import check_terminals, check_idle


def log():
    return ('NATIVE terminal slot=0 generation=0 kind=2 detail=134\n'
            'NATIVE terminal slot=1 generation=0 kind=1 detail=0\n'
            'NATIVE terminal task=0 status=134 output=0 fs=1234 ticks=1\n'
            'NATIVE terminal task=1 status=0 output=24 fs=5678 ticks=2\n')


class ThreadWitness(unittest.TestCase):
    def test_fault_requires_matching_peer_completion(self):
        check_terminals(log(), [(2, 134), (1, 0)])
        check_terminals('\n'.join(reversed(log().splitlines())) + '\n', [(2, 134), (1, 0)])

    def test_incomplete_or_wrong_outcome_rejected(self):
        valid = log()
        invalid = [valid.replace('detail=134', 'detail=142'),
                   valid.replace('kind=2', 'kind=1'),
                   valid.replace('generation=0', 'generation=1'),
                   valid.replace('status=134', 'status=0'),
                   valid.replace('output=24', 'output=0'),
                   valid.replace('fs=5678', 'fs=0'),
                   valid.replace('slot=1', 'slot=0'),
                   valid.replace('task=1', 'task=0'),
                   '\n'.join(valid.splitlines()[:-1]) + '\n',
                   valid + valid.splitlines()[0] + '\n']
        for text in invalid:
            with self.subTest(text=text), self.assertRaises(RuntimeError):
                check_terminals(text, [(2, 134), (1, 0)])

    def test_idle_evidence_requires_real_unique_timer_progress(self):
        check_idle('NATIVE WAIT idle ticks=30\n')
        for text in ('', 'NATIVE WAIT idle ticks=0\n',
                     'NATIVE WAIT idle ticks=30\nNATIVE WAIT idle ticks=30\n',
                     'NATIVE WAIT idle ticks=unknown\n'):
            with self.subTest(text=text), self.assertRaises(RuntimeError):
                check_idle(text)
