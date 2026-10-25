# SPDX-License-Identifier: BSD-2-Clause
"""Counterexamples for the repository's offline workflow gate."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'workflow', ROOT / 'scripts/check_workflow.py')
workflow = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(workflow)


class Workflow(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / 'docs/standards-review',
                        self.root / 'docs/standards-review')
        for source in (ROOT / 'docs').glob('*.md'):
            shutil.copy2(source, self.root / 'docs' / source.name)
        shutil.copy2(ROOT / 'docs/workflow.json',
                     self.root / 'docs/workflow.json')
        # Integration references can live in component directories or a machine
        # contract. Copy only inventoried local files; do not weaken validation.
        inventory = json.loads((ROOT / 'docs/workflow.json').read_text())
        for group in inventory['test_groups']:
            source = workflow.local(ROOT, group['reference'])
            destination = self.root / group['reference']
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        (self.root / 'scripts').mkdir()
        for source in (ROOT / 'scripts').glob('*.py'):
            shutil.copy2(source, self.root / 'scripts' / source.name)

    def change(self, edit):
        path = self.root / 'docs/workflow.json'
        record = json.loads(path.read_text())
        edit(record)
        path.write_text(json.dumps(record))

    def reject(self, message):
        with self.assertRaisesRegex(ValueError, message):
            workflow.check(self.root)

    def test_complete_current_inventory(self):
        counts = workflow.check(self.root)
        self.assertTrue(all(n > 0 for n in counts))

    def test_new_native_reference_requires_disposition(self):
        (self.root / 'docs/NATIVE-UNREVIEWED.md').write_text('# New ABI')
        self.reject('reference coverage drift')

    def test_new_entrypoint_requires_disposition(self):
        (self.root / 'scripts/unreviewed.py').write_text(
            'if __name__ == "__main__": pass\n')
        self.reject('tool coverage drift')

    def test_new_profile_requires_test_selection(self):
        path = self.root / 'scripts/launch_smoke.py'
        path.write_text(path.read_text() +
                        '\nprofiles.add_argument("--unreviewed")\n')
        self.reject('test-selection drift')

    def test_changed_draft_rejected(self):
        record = json.loads((self.root / 'docs/workflow.json').read_text())
        path = (self.root / record['review_manifest']).parent / 'README.md'
        path.write_text(path.read_text() + '\nchanged\n')
        self.reject('reviewed draft changed')

    def test_empty_test_inventory_rejected(self):
        self.change(lambda r: r.update(test_groups=[]))
        self.reject('empty test inventory')

    def test_release_claim_rejected(self):
        self.change(lambda r: r.update(status='fully-compliant'))
        self.reject('released conformance')

    def test_reference_escape_rejected(self):
        self.change(lambda r: next(iter(r['tools'].values())).update(
            reference='../outside.md'))
        self.reject('unsafe inventory path')

    def test_duplicate_fields_rejected(self):
        path = self.root / 'docs/workflow.json'
        path.write_text('{"status":"local-process-pilot",' +
                        path.read_text()[1:])
        self.reject('duplicate field')

    def test_boolean_budget_rejected(self):
        self.change(lambda r: r['test_groups'][0].update(budget_seconds=True))
        self.reject('invalid test budget')

    def test_same_content_symlink_rejected(self):
        record = json.loads((self.root / 'docs/workflow.json').read_text())
        path = (self.root / record['review_manifest']).parent / 'README.md'
        target = self.root / 'outside.txt'
        path.rename(target)
        path.symlink_to(target)
        self.reject('symlink in inventory path')
