# SPDX-License-Identifier: BSD-2-Clause
import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import test_harness_static_records as records

check = records.check


class StaticValidationTests(unittest.TestCase):
    def test_maintained_records_validate_without_tool_execution(self):
        with patch.object(check, 'command') as execute:
            self.assertEqual(check.settings_record(check.ROOT/'docs/static-tools.json')['schema'], 'sys-init-static-tools-v1')
            self.assertEqual(len(check.boundary_record(check.ROOT/'docs/native-boundaries.json')['records']), 25)
            execute.assert_not_called()

    def test_malformed_settings_reject_before_tool_lookup(self):
        original = json.loads((check.ROOT/'docs/static-tools.json').read_text())
        mutations = [lambda x: x.pop('clippy_modules'), lambda x: x.update(schema='future'),
                     lambda x: x.update(extra=True), lambda x: x.update(rust_sources='tests/a.rs'),
                     lambda x: x.update(rustfmt_sha256={'Darwin-arm64':'bad'}),
                     lambda x: x.update(rustfmt_args=[1]), lambda x: x.update(python_roots=['../escape']),
                     lambda x: x.update(clippy_modules=['/tmp/x']),
                     lambda x: x.update(python_roots=['scripts','scripts']),
                     lambda x: x.update(rust_toolchain='bad\x00tool'),
                     lambda x: x.update(clippy_version='\ud800')]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);(root/'docs').mkdir();(root/'docs/native-boundaries.json').write_bytes((check.ROOT/'docs/native-boundaries.json').read_bytes());(root/'docs/static-tools.json').write_bytes((check.ROOT/'docs/static-tools.json').read_bytes())
            for index, mutate in enumerate(mutations):
                value = copy.deepcopy(original);mutate(value)
                (root/'docs/static-tools.json').write_text(json.dumps(value))
                with self.subTest(index=index), patch.object(check, 'check_boundaries', return_value=13), patch.object(check, 'command') as execute:
                    with self.assertRaises(ValueError): check.run(root)
                    execute.assert_not_called()

    def test_json_bytes_duplicates_constants_depth_and_size(self):
        cases = [b'\xff', b'{', b'{"x":1,"x":2}', b'{"x":{"a":1,"a":2}}',
                 b'{"x":NaN}', b'{"x":Infinity}', b'['*2000+b'0'+b']'*2000,
                 b' '* (check.MAX_FILE+1)]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'record.json'
            for index, raw in enumerate(cases):
                path.write_bytes(raw)
                with self.subTest(index=index), self.assertRaises(ValueError):check.load_record(path)

    def test_malformed_boundary_records_reject_before_tools(self):
        original=json.loads((check.ROOT/'docs/native-boundaries.json').read_text())
        mutations=[lambda x:x.update(schema='future'),lambda x:x.update(extra=0),
                   lambda x:x['records'][0].pop('owner'),
                   lambda x:x['records'][0]['sites'][0].update(line=True),
                   lambda x:x['records'][0]['sites'][0].update(line=0),
                   lambda x:x['records'][0]['sites'][0].update(extra='x'),
                   lambda x:x['records'][0].update(reference='../escape'),
                   lambda x:x['records'][0].update(sha256='A'*64),
                   lambda x:x['records'][0].update(sites=[])]
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'docs').mkdir();(root/'docs/native-boundaries.json').write_bytes((check.ROOT/'docs/native-boundaries.json').read_bytes());(root/'docs/static-tools.json').write_bytes((check.ROOT/'docs/static-tools.json').read_bytes())
            for index,mutate in enumerate(mutations):
                value=copy.deepcopy(original);mutate(value)
                (root/'docs/native-boundaries.json').write_text(json.dumps(value))
                with self.subTest(index=index),patch.object(check,'command') as execute:
                    with self.assertRaises(ValueError):check.run(root)
                    execute.assert_not_called()

    def test_missing_field_uses_existing_structured_failure_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'docs').mkdir();(root/'docs/native-boundaries.json').write_bytes((check.ROOT/'docs/native-boundaries.json').read_bytes());(root/'docs/static-tools.json').write_bytes((check.ROOT/'docs/static-tools.json').read_bytes());(root/'docs/static-tools.json').write_text('{}')
            stdout,stderr=io.StringIO(),io.StringIO()
            with patch.object(check,'ROOT',root),patch.object(check.sys,'argv',['check-static.py']),patch.object(check,'check_boundaries',return_value=13),patch.object(check,'command') as execute,contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):
                self.assertEqual(check.main(),1)
                execute.assert_not_called()
            result=json.loads(stdout.getvalue())
            self.assertEqual(set(result),{'schema','result','diagnostic'})
            self.assertEqual(result['result'],'fail')
            self.assertTrue(stderr.getvalue())

    def test_depth_limit_ignores_quoted_brackets_and_accepts_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'record.json'
            for raw in [json.dumps({'text':'['*100 + '\"' + ']'*100}).encode(), b'['*32+b'0'+b']'*32]:
                path.write_bytes(raw)
                check.load_record(path)
            path.write_bytes(b'['*33+b'0'+b']'*33)
            with self.assertRaisesRegex(ValueError,'32 levels'):check.load_record(path)
