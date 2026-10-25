# SPDX-License-Identifier: BSD-2-Clause
"""Semantic controls for the eight fresh private ABI24 denial traces."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'docs/evidence/serial-session-denials-2026-10-04'
SPEC = importlib.util.spec_from_file_location('serial_denial_oracle', PACKET / 'check.py')
ORACLE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ORACLE)


class DenialTests(unittest.TestCase):
    def case(self, label):
        root = PACKET / label
        return ((root / 'serial.log').read_bytes(), json.loads((root / 'smoke.json').read_bytes()),
                json.loads((root / 'variant.json').read_bytes()), json.loads((PACKET / 'workload.json').read_bytes()))

    def test_eight_retained_native_cases(self):
        results = json.loads((PACKET / 'results.json').read_bytes())
        self.assertEqual(len(results), 8)
        for label, result in results.items():
            with self.subTest(label=label):
                self.assertEqual(ORACLE.check(*self.case(label)), result['oracle'])
                self.assertEqual(result['status'], 'pass-expected-rejection')

    def test_wrong_fault_missing_marker_halt_and_empty_trace_reject(self):
        for label in json.loads((PACKET / 'results.json').read_bytes()):
            raw, record, variant, workload = self.case(label)
            for bad in (b'', raw.replace(b'vector=6', b'vector=13'),
                        raw.replace(b'SESSION owner failed\n', b''),
                        raw + b'NATIVE init halted ticks=1 idle=0 reclaimed=0\n',
                        raw.replace(ORACLE.BOUNDARY, b'')):
                with self.subTest(label=label, trace=bad[-50:]), self.assertRaises(ValueError):
                    ORACLE.check(bad, record, variant, workload)

    def test_infrastructure_and_cleanup_cannot_count_as_denial(self):
        raw, record, variant, workload = self.case('denied-read')
        for key, value in (('status', 'pass'), ('error', "TimeoutError('native deadline')"),
                           ('cleanup', 'not-reaped'), ('events', [{'phase': 1}])):
            bad = dict(record, **{key: value})
            with self.subTest(key=key), self.assertRaises(ValueError):
                ORACLE.check(raw, bad, variant, workload)
        bad = dict(variant, ud2_addresses=[0])
        with self.assertRaises(ValueError): ORACLE.check(raw, record, bad, workload)

    def test_actual_errno_and_late_workload_mutations_reject(self):
        for label in ('denied-read', 'denied-write', 'busy-after-settlement'):
            raw, record, variant, workload = self.case(label)
            for old, new in ((b'result=-13', b'result=-9'), (b'result=-16', b'result=0')):
                if old not in raw: continue
                with self.assertRaises(ValueError): ORACLE.check(raw.replace(old, new), record, variant, workload)
        raw, record, variant, workload = self.case('busy-after-settlement')
        for bad in (raw.replace(b'closed ok', b'closed NO'), raw.replace(b'generation=5', b'generation=6'),
                    raw.replace(b'used=73', b'used=74')):
            with self.assertRaises(ValueError): ORACLE.check(bad, record, variant, workload)
        bad = copy.deepcopy(record); bad['events'][0]['writes'][0]['accepted'] = 0
        with self.assertRaises(ValueError): ORACLE.check(raw, bad, variant, workload)


if __name__ == '__main__':
    unittest.main()
