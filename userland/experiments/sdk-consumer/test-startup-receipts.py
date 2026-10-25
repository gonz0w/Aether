#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Check retention of unavailable or malformed startup prerequisite receipts."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path.cwd()
spec = importlib.util.spec_from_file_location(
    'sdk_startup', ROOT / 'experiments/sdk-consumer/check-startup.py')
startup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(startup)


class ReceiptFailureTests(unittest.TestCase):
    def check_failure(self, case):
        work = Path(tempfile.mkdtemp(prefix='sdk-receipt-control-', dir=ROOT / 'build'))
        pin = work / 'pin.json'
        layout = work / 'layout.json'
        if case == 'missing-layout':
            pin.write_text('{}\n')
        elif case == 'malformed-pin':
            pin.write_text('{')
        stderr = io.StringIO()
        with mock.patch.object(startup, 'PIN', pin), \
                mock.patch.object(startup, 'LAYOUT', layout), \
                mock.patch.object(startup.tempfile, 'mkdtemp', return_value=str(work)), \
                mock.patch.object(startup, 'run', side_effect=AssertionError(
                    'process started with unavailable receipt')) as command, \
                contextlib.redirect_stderr(stderr):
            result = startup.main()
        self.assertEqual(result, 1)
        command.assert_not_called()
        report = json.loads((work / 'summary.json').read_text())
        self.assertEqual(report['status'], 'incomplete')
        self.assertEqual(report['commands'], [])
        self.assertEqual(report['work'], str(work))
        # Bind the diagnostic to the actual prerequisite failure, rather than
        # allowing an unrelated setup/compilation failure to satisfy the test.
        failed_path = layout if case == 'missing-layout' else pin
        try:
            json.loads(failed_path.read_text())
        except (OSError, ValueError) as expected:
            self.assertEqual(report['error'], str(expected))
        else:
            self.fail('fixture did not produce its intended receipt failure')
        self.assertIn('[ERROR] ' + json.dumps(report['error'], ensure_ascii=True),
                      stderr.getvalue())
        print(f'{case}: retained {work / "summary.json"}')

    def test_missing_pin(self):
        self.check_failure('missing-pin')

    def test_missing_layout(self):
        self.check_failure('missing-layout')

    def test_malformed_pin(self):
        self.check_failure('malformed-pin')


if __name__ == '__main__':
    unittest.main()
