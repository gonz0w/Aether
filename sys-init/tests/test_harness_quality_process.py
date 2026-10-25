# SPDX-License-Identifier: BSD-2-Clause
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'quality_process', ROOT / 'scripts/check-quality-process.py')
QUALITY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(QUALITY)


class QualityProcessTests(unittest.TestCase):
    def test_command_contract(self):
        for argument, expected in [('--help', 0), ('--version', 0), ('--unknown', 64)]:
            result = subprocess.run(
                [sys.executable, str(ROOT / 'scripts/check-quality-process.py'), argument],
                capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, expected)
            self.assertTrue(result.stdout if expected == 0 else result.stderr)
            self.assertFalse(result.stderr if expected == 0 else result.stdout)

    def test_checkout_records(self):
        self.assertEqual(QUALITY.check()['result'], 'pass')

    def test_invalid_records_cannot_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'docs').mkdir()
            (root / 'snapshot').mkdir()
            (root / 'snapshot/source.md').write_text('reviewed draft\n')
            (root / 'snapshot/SHA256SUMS.json').write_text(json.dumps({
                'source.md': QUALITY.digest(root / 'snapshot/source.md')}))
            (root / 'reference.md').write_text('fixture reference\n')
            record = dict(schema='sys-init-quality-inventory-v1',scope='fixture',
                          snapshot='snapshot', snapshot_manifest_sha256=QUALITY.digest(
                              root / 'snapshot/SHA256SUMS.json'),
                          process=['reference.md'], surfaces=[dict(
                              id='Q', owner='fixture', status='experimental',
                              layer='host', reference='reference.md',
                              evidence='reference.md', tests=['reference.md'],
                              oracle='exact fixture result', stage='local')],
                          gaps=[dict(id='G', owner='fixture', status='open',
                                     topic='pending', milestone='before release',
                                     backlog='reference.md')])

            def write(value):
                (root / 'docs/quality-inventory.json').write_text(json.dumps(value))

            write(record)
            self.assertEqual(QUALITY.check(root)['result'], 'pass')
            mutations = []
            for field in ('process', 'surfaces', 'gaps'):
                changed = copy.deepcopy(record)
                changed[field] = []
                mutations.append(changed)
            for field, value in [('owner', ''), ('oracle', ''),
                                 ('reference', '../outside.md'),
                                 ('reference', 'missing.md'),
                                 ('status', 'conformant')]:
                changed = copy.deepcopy(record)
                changed['surfaces'][0][field] = value
                mutations.append(changed)
            changed = copy.deepcopy(record)
            changed['gaps'][0]['id'] = 'Q'
            mutations.append(changed)
            for changed in mutations:
                write(changed)
                with self.assertRaises(ValueError):
                    QUALITY.check(root)
            write(record)
            (root / 'snapshot/source.md').write_text('changed\n')
            with self.assertRaisesRegex(ValueError, 'reviewed source changed'):
                QUALITY.check(root)
            (root / 'snapshot/SHA256SUMS.json').write_text('{}')
            with self.assertRaisesRegex(ValueError, 'manifest changed'):
                QUALITY.check(root)
