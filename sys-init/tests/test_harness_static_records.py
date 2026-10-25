# SPDX-License-Identifier: BSD-2-Clause
"""Contract cases for documented static-record scope and boundary selection."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('static_records', Path(__file__).resolve().parents[1]/'scripts/check-static.py')
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


def boundary_fixture(records):
    complete = [dict(review='fixture', reference='docs/review.md', owner='test',
                     follow_up='BG-056', **record) for record in records]
    return json.dumps(dict(schema='sys-init-native-boundaries-v1', scope='test', records=complete))


class StaticRecordTests(unittest.TestCase):
    def sources_fixture(self, root):
        for name, data in [('scripts/sub/tool.py', b'x=1\n'), ('docs/check.py', b'y=2\n'),
                           ('docs/nested/ignored.py', b'not valid Python !'), ('tests/probe.rs', b'fn main() {}')]:
            path = root/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        return dict(python_roots=['scripts'], python_top_level=['docs'],
                    rust_sources=['tests/probe.rs'], clippy_modules=[])

    def test_recursive_and_immediate_scope_do_not_execute_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            settings = self.sources_fixture(root)
            settings['python_roots'].append('missing')
            data = check.sources(root, settings)
            self.assertEqual({str(p.relative_to(root)) for p in data},
                             {'scripts/sub/tool.py', 'docs/check.py', 'tests/probe.rs'})
            self.assertEqual(data[root/'docs/check.py'], b'y=2\n')

    def test_source_symlink_and_resolved_escape_reject(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)/'root'
            root.mkdir()
            settings = self.sources_fixture(root)
            path = root/'docs/check.py'
            path.unlink()
            path.symlink_to(root/'scripts/sub/tool.py')
            with self.assertRaisesRegex(ValueError, 'owned ordinary file'):
                check.sources(root, settings)
            path.unlink()
            path.write_bytes(b'y=2\n')
            outside = root.parent/'outside.rs'
            outside.write_bytes(b'fn main() {}')
            settings['rust_sources'] = ['../outside.rs']
            with self.assertRaisesRegex(ValueError, 'owned ordinary file'):
                check.sources(root, settings)

    def test_combined_budget_counts_selected_bytes_once(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            settings = self.sources_fixture(root)
            settings['python_roots'].append('scripts')
            expected = len(b'x=1\n') + len(b'y=2\n') + len(b'fn main() {}')
            with patch.object(check, 'MAX_TOTAL', expected):
                self.assertEqual(sum(map(len, check.sources(root, settings).values())), expected)
            with patch.object(check, 'MAX_TOTAL', expected-1):
                with self.assertRaisesRegex(ValueError, 'total exceeds'):
                    check.sources(root, settings)

    def test_boundary_comments_and_multiple_matches_are_one_textual_site(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'prototypes').mkdir()
            (root/'docs').mkdir()
            raw = b'// introduction\n  // unsafe unsafe extern "C"  \nfn ordinary() {}\n'
            source = root/'prototypes/probe.rs'
            source.write_bytes(raw)
            record = dict(file='prototypes/probe.rs', sha256=check.digest(raw),
                          sites=[dict(line=2, text='// unsafe unsafe extern "C"')])
            inventory = root/'docs/native-boundaries.json'
            inventory.write_text(boundary_fixture([record]))
            self.assertEqual(check.check_boundaries(root), 1)
            record['sites'][0]['line'] = 1
            inventory.write_text(boundary_fixture([record]))
            with self.assertRaisesRegex(ValueError, 'source changed'):
                check.check_boundaries(root)

    def test_duplicate_boundary_record_rejects_even_if_identical(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'docs').mkdir()
            record = dict(file='prototypes/probe.rs', sha256='0'*64, sites=[dict(line=1, text='unsafe')])
            (root/'docs/native-boundaries.json').write_text(boundary_fixture([record, record]))
            with self.assertRaisesRegex(ValueError, 'duplicate native boundary record'):
                check.check_boundaries(root)
