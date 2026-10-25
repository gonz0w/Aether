#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Check terminal, cleanup and panic oracles without booting or owner files."""
import importlib.util
import json
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location('consumer', Path(__file__).with_name('native-command-integration.py'))
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)
ORACLES = json.loads(Path(__file__).with_name('native-command-oracles.json').read_text())['cases']


class Outcomes(unittest.TestCase):
    def test_outcomes_and_mutations(self):
        for name, expected in ORACLES.items():
            lines = expected['terminals'] + expected['supervisor']
            lines += ['AETHER PANIC: native C profile rejected'] if expected['negative'] else [M.MARKER]
            text = '\n'.join(lines)
            with self.subTest(case=name):
                M.outcome(text, expected, name)
                bad = [text.replace(expected['supervisor'][0], 'NATIVE supervisor result=999 reclaimed=0'),
                       text + '\n' + M.MARKER,
                       text + '\nNATIVE terminal slot=0 generation=9 kind=1 detail=0']
                if expected['negative']:
                    bad.append(text.replace('native C profile rejected', 'unrelated failure'))
                else:
                    bad.append(text.replace(M.MARKER, ''))
                for changed in bad:
                    with self.assertRaises(ValueError):
                        M.outcome(changed, expected, name)

    def test_admission_scheduling(self):
        name = 'uncertain-admission-lost'
        expected = ORACLES[name]
        text = '\n'.join(expected['terminals'] + expected['supervisor'] + ['AETHER PANIC: native C profile rejected'])
        child = 'NATIVE terminal slot=2 generation=1 kind=1 detail=0'
        M.outcome(child + '\n' + text, expected, name)
        with self.assertRaises(ValueError):
            M.outcome(child + '\n' + child + '\n' + text, expected, name)


if __name__ == '__main__':
    unittest.main()
