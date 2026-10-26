# SPDX-License-Identifier: BSD-2-Clause
"""Prospective decoder denials; synthetic rows are not native witnesses."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from af09_drain_trace import CASES, FIELDS, Row, parse_trace


def encoded(**changes):
    values = dict(case=1, row=0, phase=1, slot=6, gen=0, seq=0, tick=0,
                  deadline=0, status=0, count=0, aux=0)
    values.update(changes)
    return ('AF09-DRAIN v=1 ' + ' '.join(f'{name}={values[name]}' for name in FIELDS) + '\n').encode()


class DrainTrace(unittest.TestCase):
    def test_all_closed_cases_and_verbatim_unparsed_uart(self):
        other = b'AETHER boot\npartial\x00tail'
        for case, selection in enumerate(CASES, 1):
            with self.subTest(selection=selection):
                trace = parse_trace(encoded(case=case) + other, selection)
                self.assertEqual(trace.rows[0].case, case)
                self.assertEqual(b''.join(trace.unparsed), other)
                self.assertFalse(hasattr(trace, 'qualified'))

    def test_saved_and_completed_sequences_are_not_row_ordinals(self):
        rows = (encoded(seq=9) + encoded(row=1, phase=10, seq=7, deadline=501, tick=1)
                + encoded(row=2, phase=11, seq=8, deadline=501, tick=501, status=-110))
        trace = parse_trace(rows, 'file_prefix')
        self.assertEqual([r.seq for r in trace.rows], [9, 7, 8])

    def test_unsigned_and_signed_boundaries(self):
        trace = parse_trace(encoded(gen=2**64-1, seq=2**64-1, tick=2**64-1,
                                    deadline=2**64-1, status=-(2**63), count=2**64-1,
                                    aux=2**64-1), 'file_prefix')
        self.assertIsInstance(trace.rows[0], Row)
        for field in FIELDS:
            if field in ('case', 'phase', 'slot', 'row'):
                continue
            with self.subTest(field=field):
                value = 2**63 if field == 'status' else 2**64
                with self.assertRaisesRegex(ValueError, 'numeric range'):
                    parse_trace(encoded(**{field: value}), 'file_prefix')
        with self.assertRaisesRegex(ValueError, 'numeric range'):
            parse_trace(encoded(status=-(2**63)-1), 'file_prefix')

    def test_noncanonical_machine_rows_fail(self):
        original = encoded()
        bad = [original[:-1], original.replace(b'\n', b'\r\n'),
               original.replace(b'v=1', b'v=2'), original.replace(b'case=1', b'case=01'),
               original.replace(b'status=0', b'status=-0'), original.replace(b'count=0', b'count=+0'),
               original.replace(b' slot=6', b'  slot=6'), original.replace(b' gen=0', b''),
               original.replace(b' count=0', b' count=0 count=0'), original[:-1] + b' extra=0\n',
               original.replace(b'tick=0 deadline=0', b'deadline=0 tick=0'),
               original.replace(b'count=0', b'count=\x1b[0m0')]
        for value in bad:
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, 'grammar'):
                    parse_trace(value, 'file_prefix')

    def test_no_suffix_promotion_or_empty_acceptance(self):
        for capture in (b'', b'AETHER boot\n', b'prefix ' + encoded(), b' ' + encoded()):
            with self.subTest(capture=capture):
                with self.assertRaisesRegex(ValueError, 'missing trace'):
                    parse_trace(capture, 'file_prefix')
        suffix = b'prefix ' + encoded()
        trace = parse_trace(encoded() + suffix, 'file_prefix')
        self.assertEqual(len(trace.rows), 1)
        self.assertEqual(trace.unparsed, (suffix,))

    def test_identity_reset_gap_unknown_failure_and_duplicate_denials(self):
        bad = [encoded(case=2), encoded(row=1), encoded(phase=2), encoded(phase=0),
               encoded(phase=30), encoded(phase=255), encoded(phase=29), encoded(slot=7),
               encoded() + encoded(row=1), encoded(tick=1) + encoded(row=1, phase=10),
               encoded() + encoded(row=1, phase=10, gen=1)]
        for capture in bad:
            with self.subTest(capture=capture):
                with self.assertRaises(ValueError):
                    parse_trace(capture, 'file_prefix')
        for selection in ('none', 'FILE_PREFIX', '', 'unknown'):
            with self.assertRaisesRegex(ValueError, 'selection'):
                parse_trace(encoded(), selection)

    def test_capture_row_and_diagnostic_limits(self):
        for capture in (b'x' * 65537, bytearray(encoded()), 'text'):
            with self.assertRaisesRegex(ValueError, 'capture'):
                parse_trace(capture, 'file_prefix')
        with self.assertRaisesRegex(ValueError, 'budget'):
            parse_trace(encoded()[:-1] + b' ' * 256 + b'\n', 'file_prefix')
        rows = encoded() + b''.join(encoded(row=i, phase=10) for i in range(1, 350))
        with self.assertRaisesRegex(ValueError, 'budget'):
            parse_trace(rows, 'file_prefix')


if __name__ == '__main__':
    unittest.main()
