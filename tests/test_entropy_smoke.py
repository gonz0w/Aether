# SPDX-License-Identifier: BSD-2-Clause
"""Counterexamples for entropy proof markers and the deliberate broken validator."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from entropy_smoke import observe, MARKER, READY


class Running:
    def poll(self):
        return None


class EntropyOracle(unittest.TestCase):
    def check(self, data, label, panic=None):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'serial.log'
            path.write_bytes(data)
            return observe(Running(), path, label, panic)

    def test_positive_and_partial(self):
        self.check(READY + b'\n' + MARKER + b'\n', 'draw')
        self.check(READY + b'\nENTROPY partial completion checked\n' + MARKER + b'\n', 'partial')
        with self.assertRaisesRegex(RuntimeError, 'partial completion evidence missing'):
            self.check(READY + b'\n' + MARKER + b'\n', 'partial')

    def test_duplicate_marker_and_missing_ready(self):
        with self.assertRaisesRegex(RuntimeError, 'duplicate or missing'):
            self.check(READY + b'\n' + MARKER + b'\n' + MARKER + b'\n', 'draw')
        with self.assertRaisesRegex(RuntimeError, 'duplicate or missing'):
            self.check(MARKER + b'\n', 'draw')

    def test_exact_length_and_context(self):
        panic = b'entropy invalid length; DMA retained'
        self.check(READY + b'\nAETHER PANIC: ' + panic + b'\n', 'length', panic)
        with self.assertRaisesRegex(RuntimeError, 'unexpected kernel panic'):
            self.check(READY + b'\nAETHER PANIC: different\n', 'length', panic)
        with self.assertRaisesRegex(RuntimeError, 'ordered execution context'):
            self.check(b'AETHER PANIC: ' + panic + b'\n', 'length', panic)

    def test_mutant_requires_oracle_failure(self):
        panic = b'entropy invalid length; DMA retained'
        result = self.check(READY + b'\n' + MARKER + b'\n', 'accept-length-mutant', panic)
        self.assertEqual(result, 'broken validator rejected by exact length oracle')
        with self.assertRaisesRegex(RuntimeError, 'accepted the broken validator'):
            self.check(READY + b'\nAETHER PANIC: ' + panic + b'\n', 'accept-length-mutant', panic)
