# SPDX-License-Identifier: BSD-2-Clause
"""Current-source selection must never silently replace historical acceptance."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    'current_checks', Path(__file__).resolve().parents[1] / 'scripts/check-all.py')
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)


class CurrentSelection(unittest.TestCase):
    def test_explicit_selection_keeps_current_gates_and_default_keeps_history(self):
        with tempfile.TemporaryDirectory() as directory:
            for current in (False, True):
                args = ['check-all.py', '--output-root', directory]
                if current:
                    args.append('--current')
                with patch('sys.argv', args), patch.object(checks, 'run_suite', return_value=0) as run:
                    self.assertEqual(checks.main(), 0)
                names = [name for name, _ in run.call_args.args[1]]
                self.assertEqual('native-evidence' in names, not current)
                self.assertEqual(run.call_args.kwargs['historical'], not current)
                self.assertEqual(set(names) - {'native-evidence'}, {
                    'standards', 'experience', 'distribution', 'quality-process',
                    'static', 'evidence', 'sample-receipts', 'model', 'host'})

    def test_current_report_explicitly_excludes_native_history(self):
        with tempfile.TemporaryDirectory() as directory:
            import json
            with patch.object(checks, 'source_hashes', return_value={}):
                self.assertEqual(checks.run_suite(Path(directory), [], historical=False), 0)
            report = json.loads((Path(directory) / 'results.json').read_text())
            self.assertEqual(report['historical_native_evidence'], 'not-run')
            self.assertEqual(report['native'], 'not-run')
