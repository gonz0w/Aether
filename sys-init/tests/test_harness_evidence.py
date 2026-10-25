"""Foundations E-06: success must prove a nonempty, fully executed host suite."""
import importlib.util
import json
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('host_check', Path(__file__).resolve().parents[1] / 'scripts/check-host-runtime.py')
host_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(host_check)


class EvidenceTests(unittest.TestCase):
    def test_actual_count_is_returned(self):
        self.assertEqual(host_check.validate_suite_result(json.dumps(
            dict(discovered=19, tests=19, successful=True, skipped=0))), 19)

    def test_zero_partial_failed_skipped_and_forged_counts_reject(self):
        for override in [dict(discovered=0, tests=0), dict(tests=1), dict(successful=False),
                         dict(skipped=2), dict(tests=True), dict(successful=1), dict(discovered=-1)]:
            with self.subTest(override=override), self.assertRaises(ValueError):
                host_check.validate_suite_result(json.dumps(
                    dict(dict(discovered=14, tests=14, successful=True, skipped=0), **override)))

    def test_missing_malformed_and_extra_evidence_reject(self):
        for raw in ['', 'OK', '{}', '[]', '{"tests":14}',
                    '{"discovered":14,"tests":14,"successful":true,"skipped":0,"extra":1}']:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                host_check.validate_suite_result(raw)


if __name__ == '__main__':
    unittest.main()
