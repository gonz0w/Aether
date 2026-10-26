# SPDX-License-Identifier: BSD-2-Clause
"""Host identity binding controls; no synthetic qualification claims."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import af09_drain_inputs as D


class DrainInputs(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.TemporaryDirectory(prefix='aether-drain-inputs-')
        self.addCleanup(self.work.cleanup)
        self.root = Path(self.work.name)
        source = self.root / 'source'
        source.write_bytes(b'current input')
        self.source = self.identity(source)
        self.records = {}
        for role in D.ROLES:
            path = self.root / role
            path.write_text('opaque retained record for ' + role)
            self.records[role] = self.identity(path)
        self.report = dict(schema=D.SCHEMA, cases=list(D.CASES),
                           inputs={str(source): self.source['sha256']}, records=self.records)

    @staticmethod
    def identity(path):
        return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

    def manifest(self):
        path = self.root / 'manifest.json'
        path.write_text(json.dumps(self.report))
        return self.identity(path)

    def test_closed_selection(self):
        self.assertEqual([D.selection(c) for c in ('none', *D.CASES)], list(range(9)))
        for case in (None, '', 1, 'NONE', 'unknown'):
            with self.subTest(case=case), self.assertRaises(ValueError):
                D.selection(case)

    def test_all_cases_bind_current_inputs_and_raw_records_without_pass_claim(self):
        identity = self.manifest()
        for case in D.CASES:
            result = D.host_inputs(identity, case)
            self.assertEqual(result['identity'], identity)
            self.assertEqual(result['records'], self.records)
            self.assertEqual(result['inputs'][self.source['path']], self.source['sha256'])
            self.assertEqual(len(result['inputs']), len(D.ROLES) + 3)
            self.assertNotIn('qualified', result)
        with self.assertRaises(ValueError):
            D.host_inputs(identity, 'none')

    def test_changed_source_receipt_and_manifest_reject(self):
        for key in ('source', 'receipt', 'manifest'):
            with self.subTest(key=key):
                identity = self.manifest()
                path = Path({'source': self.source, 'receipt': self.records['kernel'],
                             'manifest': identity}[key]['path'])
                original = path.read_bytes()
                path.write_bytes(original + b'changed')
                with self.assertRaisesRegex(ValueError, 'changed'):
                    D.host_inputs(identity, D.CASES[0])
                path.write_bytes(original)

    def test_missing_role_wrong_family_extra_fields_and_relative_input_reject(self):
        original = json.dumps(self.report)
        for change in ('role', 'family', 'extra', 'relative'):
            self.report = json.loads(original)
            if change == 'role':
                del self.report['records']['kernel']
            elif change == 'family':
                self.report['cases'].reverse()
            elif change == 'extra':
                self.report['qualified'] = True
            else:
                self.report['inputs'] = {'relative': self.source['sha256']}
            with self.subTest(change=change), self.assertRaises(ValueError):
                D.host_inputs(self.manifest(), D.CASES[0])

    def test_oversized_manifest_rejects_before_hash_or_content_read(self):
        identity = self.manifest()
        with Path(identity['path']).open('ab') as stream:
            stream.truncate(4 * 1024**2 + 1)
        with patch.object(D, '_digest', side_effect=AssertionError('must not read')):
            with self.assertRaisesRegex(ValueError, 'manifest size'):
                D.host_inputs(identity, D.CASES[0])

    def test_manifest_growth_after_initial_identity_check_is_bounded_and_rejected(self):
        identity = self.manifest()
        original = D._identity
        def grow(item, **kwargs):
            checked = original(item, **kwargs)
            if item == identity:
                with Path(identity['path']).open('ab') as stream:
                    stream.truncate(4 * 1024**2 + 1)
            return checked
        with patch.object(D, '_identity', side_effect=grow):
            with self.assertRaisesRegex(ValueError, 'manifest size'):
                D.host_inputs(identity, D.CASES[0])

    def test_manifest_rehash_after_record_binding_keeps_the_same_bound(self):
        identity = self.manifest()
        original = D._identity
        checked_manifest = 0
        def grow(item, **kwargs):
            nonlocal checked_manifest
            if item == identity:
                checked_manifest += 1
                if checked_manifest == 2:
                    with Path(identity['path']).open('ab') as stream:
                        stream.truncate(4 * 1024**2 + 1)
            return original(item, **kwargs)
        with patch.object(D, '_identity', side_effect=grow):
            with self.assertRaisesRegex(ValueError, 'manifest size'):
                D.host_inputs(identity, D.CASES[0])

    def test_symlink_missing_noncanonical_hash_and_duplicate_json_reject(self):
        identity = self.manifest()
        link = self.root / 'link'
        link.symlink_to(identity['path'])
        for item in ({**identity, 'path': str(link)},
                     {**identity, 'path': str(self.root / 'missing')},
                     {**identity, 'sha256': identity['sha256'].upper()},
                     {**identity, 'extra': 1}):
            with self.subTest(identity=item), self.assertRaises(ValueError):
                D.host_inputs(item, D.CASES[0])
        path = Path(identity['path'])
        path.write_text('{"schema":1,"schema":2}')
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            D.host_inputs(self.identity(path), D.CASES[0])


if __name__ == '__main__':
    unittest.main()
