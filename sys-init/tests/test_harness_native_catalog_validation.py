# SPDX-License-Identifier: BSD-2-Clause
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import test_harness_native_audit as fixtures


audit = fixtures.audit


class NativeCatalogValidationTests(unittest.TestCase):
    def catalog(self):
        current = json.loads((fixtures.ROOT / 'docs/native-coverage.json').read_text())
        bundle = copy.deepcopy(next(b for b in current['bundles'] if b['schema'] == 'sys-init-native-init-v1'))
        bundle['cases'] = [bundle['cases'][0]]
        return dict(schema=current['schema'], scope=current['scope'], bundles=[bundle])

    def test_invalid_fields_reject_before_bundle_access(self):
        changes = [lambda r: r.update(extra=1), lambda r: r.update(scope=False),
                   lambda r: r.update(bundles={}),
                   lambda r: r['bundles'][0].update(schema='unknown'),
                   lambda r: r['bundles'][0].update(directory='../escape'),
                   lambda r: r['bundles'][0].update(manifest_sha256='G'*64),
                   lambda r: r['bundles'][0].update(native_profile='unknown'),
                   lambda r: r['bundles'][0].update(cases=[]),
                   lambda r: r['bundles'][0]['cases'][0].update(name='a/b'),
                   lambda r: r['bundles'][0]['cases'][0].update(first_image='other'),
                   lambda r: r['bundles'][0]['cases'][0].update(assertion=None),
                   lambda r: r['bundles'][0]['cases'][0].update(context=True),
                   lambda r: r['bundles'][0]['cases'].append(copy.deepcopy(r['bundles'][0]['cases'][0]))]
        for index, change in enumerate(changes):
            with self.subTest(index=index), tempfile.TemporaryDirectory() as directory:
                root = Path(directory); (root/'docs').mkdir()
                record = self.catalog(); change(record)
                (root/'docs/native-coverage.json').write_text(json.dumps(record))
                with patch.object(audit, 'ROOT', root), patch.object(audit.sys, 'argv', ['check']), patch.object(audit, 'audit_bundle') as bundle:
                    with self.assertRaises(ValueError): audit.main()
                bundle.assert_not_called()

    def test_json_limits_and_duplicate_keys(self):
        for raw in (b'{"a":1,"a":2}', b'{"a":NaN}', b'\xff', b'['*33+b'0'+b']'*33,
                    b' '*(audit.MAX_CATALOG+1)):
            with self.subTest(prefix=raw[:20]), self.assertRaises(ValueError): audit.parse_catalog(raw)
        self.assertEqual(audit.parse_catalog(b'{"quoted":"[[["}'), {'quoted': '[[['})

    def test_maintained_catalog_and_io_type_controls(self):
        current = json.loads((fixtures.ROOT/'docs/native-coverage.json').read_text())
        audit.validate_catalog(current)
        for value in (False, -1, 256, '0'):
            record = copy.deepcopy(current); record['bundles'][0]['cases'][0]['smoke_exit'] = value
            with self.subTest(value=value), self.assertRaises(ValueError): audit.validate_catalog(record)

    def test_late_catalog_change_prevents_success(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root/'docs').mkdir()
            path = root/'docs/native-coverage.json'; path.write_text(json.dumps(self.catalog()))
            def bundle(base, entry):
                path.write_text('{}')
                return dict(directory=entry['directory'], cases=1, files=1, result='pass')
            output = io.StringIO()
            with patch.object(audit, 'ROOT', root), patch.object(audit.sys, 'argv', ['check']), patch.object(audit, 'audit_bundle', side_effect=bundle), patch.object(audit, 'verify_manifest'), contextlib.redirect_stdout(output):
                with self.assertRaisesRegex(ValueError, 'catalog changed during audit'): audit.main()
            self.assertEqual(output.getvalue(), '')

    def test_collection_and_text_budgets(self):
        base = self.catalog()
        for field in ('bundles', 'cases', 'scope'):
            record = copy.deepcopy(base)
            if field == 'bundles': record['bundles'] *= 1001
            elif field == 'cases': record['bundles'][0]['cases'] *= 1001
            else: record['scope'] = 'x' * 4097
            with self.subTest(field=field), self.assertRaises(ValueError): audit.validate_catalog(record)
        record = copy.deepcopy(base)
        template = record['bundles'][0]
        template['cases'] = [dict(template['cases'][0], name='case-' + str(i)) for i in range(1000)]
        record['bundles'] = [dict(template, directory='bundle-' + str(i)) for i in range(11)]
        with self.assertRaisesRegex(ValueError, '10000 cases'): audit.validate_catalog(record)
