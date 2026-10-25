# SPDX-License-Identifier: BSD-2-Clause
"""Eleven consuming boundary traces and strict semantic corruption controls."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
GROUPS = {}
for name in ('session-limits-2026-10-04', 'session-final-controls-2026-10-04'):
    packet = ROOT / 'docs/evidence' / name
    spec = importlib.util.spec_from_file_location(name, packet / 'check.py')
    oracle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oracle)
    GROUPS[name] = packet, oracle


class BoundaryTests(unittest.TestCase):
    def cases(self):
        for name, (packet, oracle) in GROUPS.items():
            for label, expected in json.loads((packet / 'results.json').read_bytes()).items():
                root = packet / label
                yield name, label, oracle, expected, (root / 'serial.log').read_bytes(), \
                    json.loads((root / 'smoke.json').read_bytes()), json.loads((root / 'variant.json').read_bytes())

    def test_eleven_actual_native_boundaries(self):
        cases = list(self.cases())
        self.assertEqual(len(cases), 11)
        for name, label, oracle, expected, raw, record, variant in cases:
            with self.subTest(group=name, label=label):
                self.assertEqual(oracle.check(raw, record, variant), expected)
                self.assertEqual(expected['status'], 'pass-expected-rejection')

    def test_empty_wrong_failure_cleanup_timeout_and_false_halt_reject(self):
        for name, label, oracle, _, raw, record, variant in self.cases():
            for bad in (b'', raw.replace(b'AETHER PANIC: ', b'OTHER PANIC: '),
                        raw + b'NATIVE init halted ticks=1 idle=0 reclaimed=0\n'):
                with self.subTest(group=name, label=label), self.assertRaises(ValueError):
                    oracle.check(bad, record, variant)
            for key, value in (('cleanup', 'not-reaped'), ('error', "TimeoutError('native deadline')"), ('status', 'pass')):
                with self.subTest(label=label, key=key), self.assertRaises(ValueError):
                    oracle.check(raw, dict(record, **{key: value}), variant)

    def test_typed_result_identity_admission_and_fragment_mutations_reject(self):
        for _, label, oracle, _, raw, record, variant in self.cases():
            if label.startswith('loader-'):
                with self.assertRaises(ValueError):
                    oracle.check(raw.replace(variant['expected_reason'].encode(), b'unrelated boot failure'), record, variant)
                with self.assertRaises(ValueError):
                    oracle.check(raw + b'NATIVE MEMORY admitted slot=0 generation=1 used=73 remaining=55\n', record, variant)
                continue
            marker = oracle.MARKERS[label]
            for bad in (raw.replace(marker, b''), raw.replace(b'result=', b'other='),
                        raw.replace(b'generation=1 used=73', b'generation=2 used=73'),
                        raw.replace(b'vector=6', b'vector=13')):
                with self.subTest(label=label), self.assertRaises(ValueError):
                    oracle.check(bad, record, variant)
            bad = copy.deepcopy(record); bad['events'][0]['writes'][0]['accepted'] = 0
            with self.assertRaises(ValueError): oracle.check(raw, bad, variant)
            with self.assertRaises(ValueError): oracle.check(raw, record, dict(variant, ud2_addresses=[0]))

    def test_lifetime_sixteenth_admission_and_parent_completion_reject(self):
        packet, oracle = GROUPS['session-limits-2026-10-04']
        root = packet / 'lifetime-exhausted'
        raw = (root / 'serial.log').read_bytes()
        record = json.loads((root / 'smoke.json').read_bytes())
        variant = json.loads((root / 'variant.json').read_bytes())
        for added in (b'NATIVE MEMORY admitted slot=2 generation=16 used=24 remaining=104\n',
                      b'NATIVE terminal slot=0 generation=1 kind=1 detail=0\n'):
            bad = raw.replace(oracle.MARKERS['lifetime-exhausted'], added + oracle.MARKERS['lifetime-exhausted'])
            with self.assertRaises(ValueError): oracle.check(bad, record, variant)


if __name__ == '__main__':
    unittest.main()
