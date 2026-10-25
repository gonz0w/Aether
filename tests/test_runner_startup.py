# SPDX-License-Identifier: BSD-2-Clause
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from runner_startup import encode


class RunnerStartup(unittest.TestCase):
    def test_wire_layout(self):
        record = encode(['aether-run', 'bytecount', '--decimal'])
        self.assertEqual(len(record), 224)
        self.assertEqual(record[:32], b'AERUN001' + b'\3' + bytes(23))
        self.assertEqual(record[64:96], b'bytecount' + bytes(23))
        self.assertEqual(record[128:], bytes(96))

    def test_six_strings_and_empty(self):
        record = encode(['aether-run', '--', 'bytecount', '--decimal', '', 'x' * 31])
        self.assertEqual(record[160:192], bytes(32))
        self.assertEqual(record[192:], b'x' * 31 + b'\0')

    def test_count_bounds(self):
        for values in ([], ['aether-run'] + ['x'] * 6):
            with self.assertRaises(ValueError):
                encode(values)

    def test_bytes_not_characters(self):
        self.assertEqual(len(encode(['aether-run', 'é' * 15])), 224)
        with self.assertRaises(ValueError):
            encode(['aether-run', 'é' * 16])

    def test_no_truncation_or_embedded_nul(self):
        for value in ('x' * 32, 'a\0b'):
            with self.assertRaises(ValueError):
                encode(['aether-run', value])

    def test_identity(self):
        with self.assertRaises(ValueError):
            encode(['client'])
