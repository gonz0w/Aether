#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Consumed receipt fields: reject malformed inputs before copy or execution."""
import contextlib
import copy
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


class SchemaTests(unittest.TestCase):
    def test_invalid_inputs_before_effects(self):
        baseline = {name: json.loads(getattr(startup, name.upper()).read_text())
                    for name in ('pin', 'layout', 'binding')}
        cases = [
            ('pin', [], 'pin'),
            ('layout', None, 'layout'),
            ('binding', False, 'binding'),
            ('pin.libc_receipt_sha256', 'A' * 64, 'pin.libc_receipt_sha256'),
            ('layout.imported_root', True, 'layout.imported_root'),
            ('layout.imported_root', 'relative/path', 'layout.imported_root'),
            ('layout.imported_root', '/bad\x00path', 'layout.imported_root'),
            ('layout.target_sha256', 12, 'layout.target_sha256'),
            ('binding.target_sha256', '0' * 63, 'binding.target_sha256'),
            ('pin.tools', [], 'pin.tools'),
            ('pin.tools.clang', None, 'pin.tools.clang'),
            ('pin.tools.clang.path', '', 'pin.tools.clang.path'),
            ('pin.tools.nm.sha256', {}, 'pin.tools.nm.sha256'),
            ('pin.sdk_inputs', [], 'pin.sdk_inputs'),
            ('pin.sdk_inputs', {}, 'pin.sdk_inputs'),
            ('pin.sdk_inputs', {'stage/usr/lib/libc.a': None}, 'pin.sdk_inputs.digest'),
        ]
        for path in ('/absolute', '../outside', 'stage/usr/../../outside',
                     'stage/usr//lib/a', 'stage/usr/./lib/a',
                     'stage/usr/lib/a\\b', 'stage/usr/lib/a\x00b'):
            cases.append(('pin.sdk_inputs', {path: '0' * 64}, 'pin.sdk_inputs.path'))
        # Missing consumed fields must produce the same bounded diagnostic.
        missing = copy.deepcopy(baseline['pin']['tools'])
        del missing['lld']
        cases.append(('pin.tools', missing, 'pin.tools.lld'))
        for field, value, expected in cases:
            with self.subTest(field=field, value=value):
                data = copy.deepcopy(baseline)
                target = data
                parts = field.split('.')
                for part in parts[:-1]:
                    target = target[part]
                target[parts[-1]] = value
                work = Path(tempfile.mkdtemp(prefix='sdk-schema-control-',
                                             dir=ROOT / 'build'))
                for name, payload in data.items():
                    (work / (name + '.json')).write_text(json.dumps(payload))
                with mock.patch.object(startup, 'PIN', work / 'pin.json'), \
                        mock.patch.object(startup, 'LAYOUT', work / 'layout.json'), \
                        mock.patch.object(startup, 'BINDING', work / 'binding.json'), \
                        mock.patch.object(startup.tempfile, 'mkdtemp', return_value=str(work)), \
                        mock.patch.object(startup.shutil, 'copy2', side_effect=AssertionError(
                            'copy reached with invalid receipt')) as copying, \
                        mock.patch.object(startup, 'run', side_effect=AssertionError(
                            'process reached with invalid receipt')) as running, \
                        contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(startup.main(), 1)
                copying.assert_not_called()
                running.assert_not_called()
                report = json.loads((work / 'summary.json').read_text())
                self.assertEqual(report['status'], 'incomplete')
                self.assertEqual(report['commands'], [])
                self.assertEqual(report['error'], 'invalid receipt field: ' + expected)
        print(f'{len(cases)} malformed input scenarios exercised')

    def test_unknown_owner_fields_allowed(self):
        values = [json.loads(path.read_text()) for path in
                  (startup.PIN, startup.LAYOUT, startup.BINDING)]
        for value in values:
            value['future_owner_metadata'] = {'data': ['opaque', 1]}
        startup.validate_inputs(*values)

    def test_libc_fields(self):
        receipt = json.loads((ROOT / 'build/native-c-xhkdw6jv/evidence.json').read_text())
        startup.validate_libc_receipt(receipt)
        cases = [(None, 'libc'), ({}, 'libc.probe_sha256')]
        for field, value in [('probe_sha256', True), ('io_adapter_sha256', 'bad'),
                             ('memory_sources', []),
                             ('memory_sources', {'native_memory.c': '0' * 64})]:
            altered = copy.deepcopy(receipt)
            altered[field] = value
            expected = 'libc.' + field
            if isinstance(value, dict):
                expected += '.memory_probe.c'
            cases.append((altered, expected))
        for altered, expected in cases:
            with self.subTest(expected=expected):
                with self.assertRaises(RuntimeError) as error:
                    startup.validate_libc_receipt(altered)
                self.assertEqual(str(error.exception), 'invalid receipt field: ' + expected)
        print(f'{len(cases)} libc structure controls exercised')


if __name__ == '__main__':
    unittest.main()
