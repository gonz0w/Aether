#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Receipt byte/ambiguity and evidence-storage failure controls."""
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


class PreflightTests(unittest.TestCase):
    def test_decoder_boundaries(self):
        work = Path(tempfile.mkdtemp(prefix='sdk-json-control-', dir=ROOT / 'build'))
        receipt = work / 'input.json'
        cap = startup.MAX_RECEIPT_BYTES
        receipt.write_bytes(b'{}' + b' ' * (cap - 2))
        self.assertEqual(startup.load_receipt(receipt), {})
        receipt.write_bytes(b'[' * 64 + b'0' + b']' * 64)
        startup.load_receipt(receipt)
        quoted = {'text': '[{\"\\' * 100 + 'é'}
        receipt.write_text(json.dumps(quoted, ensure_ascii=False), encoding='utf-8')
        self.assertEqual(startup.load_receipt(receipt), quoted)
        cases = [
            (b'{}' + b' ' * (cap - 1), 'receipt exceeds byte limit'),
            (b'{"a":1,"a":2}', 'duplicate receipt JSON key'),
            (b'{"a":{"b":1,"b":2}}', 'duplicate receipt JSON key'),
            (b'{"a":NaN}', 'nonfinite receipt JSON constant'),
            (b'{"a":Infinity}', 'nonfinite receipt JSON constant'),
            (b'{"a":-Infinity}', 'nonfinite receipt JSON constant'),
            (b'[' * 65 + b'0' + b']' * 65, 'receipt exceeds nesting limit'),
            (b'[' * 10000 + b']' * 10000, 'receipt exceeds nesting limit'),
        ]
        for payload, message in cases:
            with self.subTest(message=message, size=len(payload)):
                receipt.write_bytes(payload)
                with self.assertRaises(RuntimeError) as error:
                    startup.load_receipt(receipt)
                self.assertEqual(str(error.exception), message)

    def test_invalid_intake_before_effects(self):
        for payload, message in [
                (b'{"tools":{},"tools":[]}', 'duplicate receipt JSON key'),
                (b' ' * (2 * 1024 * 1024 + 1), 'receipt exceeds byte limit')]:
            with self.subTest(message=message):
                work = Path(tempfile.mkdtemp(prefix='sdk-intake-control-',
                                             dir=ROOT / 'build'))
                pin = work / 'pin.json'
                pin.write_bytes(payload)
                with mock.patch.object(startup, 'PIN', pin), \
                        mock.patch.object(startup.tempfile, 'mkdtemp', return_value=str(work)), \
                        mock.patch.object(startup.shutil, 'copy2', side_effect=AssertionError(
                            'copy reached for invalid JSON')) as copying, \
                        mock.patch.object(startup, 'run', side_effect=AssertionError(
                            'command reached for invalid JSON')) as running, \
                        contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(startup.main(), 1)
                copying.assert_not_called()
                running.assert_not_called()
                report = json.loads((work / 'summary.json').read_text())
                self.assertEqual(report['status'], 'incomplete')
                self.assertEqual(report['commands'], [])
                self.assertEqual(report['error'], message)

    def test_evidence_storage_failure(self):
        for stage in ('create', 'initial-write', 'later-write'):
            with self.subTest(stage=stage):
                work = Path(tempfile.mkdtemp(prefix='sdk-storage-control-',
                                             dir=ROOT / 'build'))
                writes = []
                original_write = Path.write_text

                def write(path, *args, **kwargs):
                    if path == work / 'summary.json':
                        writes.append(path)
                        if stage == 'initial-write' or len(writes) >= 2:
                            raise OSError('simulated evidence write failure')
                    return original_write(path, *args, **kwargs)

                stdout, stderr = io.StringIO(), io.StringIO()
                with mock.patch.object(startup.tempfile, 'mkdtemp',
                                       return_value=str(work),
                                       side_effect=OSError('simulated create failure')
                                       if stage == 'create' else None), \
                        mock.patch.object(Path, 'write_text', new=write), \
                        mock.patch.object(startup, 'run', side_effect=AssertionError(
                            'command reached before failing evidence save')) as running, \
                        contextlib.redirect_stdout(stdout), \
                        contextlib.redirect_stderr(stderr):
                    self.assertEqual(startup.main(), 1)
                running.assert_not_called()
                self.assertEqual(stdout.getvalue(), '')
                self.assertIn('[ERROR] Evidence storage unavailable:', stderr.getvalue())
                summary = work / 'summary.json'
                if stage == 'later-write':
                    report = json.loads(summary.read_text())
                    self.assertEqual(report['status'], 'incomplete')
                    self.assertEqual(report['commands'], [])
                else:
                    self.assertFalse(summary.exists())


if __name__ == '__main__':
    unittest.main()
