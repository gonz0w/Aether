"""Measurement summaries must not silently accept missing or invalid samples."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('host_measurements', Path(__file__).resolve().parents[1] / 'scripts/measure-host-runtime.py')
measurement = importlib.util.module_from_spec(spec)
spec.loader.exec_module(measurement)


class MeasurementEvidence(unittest.TestCase):
    def test_nearest_rank_p95_and_even_median(self):
        self.assertEqual(measurement.summarize(list(range(1, 21))),
                         dict(count=20, median=10.5, p95=19, maximum=20))

    def test_unsorted_ten_samples_are_preserved_for_summary(self):
        values = [10, 1, 9, 2, 8, 3, 7, 4, 6, 5]
        before = list(values)
        self.assertEqual(measurement.summarize(values), dict(count=10, median=5.5, p95=10, maximum=10))
        self.assertEqual(values, before)

    def test_empty_nonfinite_negative_and_forged_samples_reject(self):
        for values in ([], [float('nan')], [float('inf')], [-1], [True], ['1']):
            with self.subTest(values=values), self.assertRaises(ValueError):
                measurement.summarize(values)


if __name__ == '__main__':
    unittest.main()
