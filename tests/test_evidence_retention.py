# SPDX-License-Identifier: BSD-2-Clause
"""Cleanup must preserve diagnostics and cannot cross owned output boundaries."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import evidence
import fixture_inputs
import reproduce


class Retention(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / 'zig-out').mkdir()
        self.patch = patch.object(evidence, 'ROOT', self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def run_directory(self, name='thread-suite-fixture'):
        output = self.root / 'zig-out' / name
        output.mkdir()
        (output / 'results.json').write_text('{}')
        return output

    def test_pass_and_failure_keep_results_not_generated_artifacts(self):
        for status in ['pass', 'failed']:
            output = self.run_directory('memory-suite-' + status)
            (output / 'build').mkdir()
            for name in ['aether.iso', 'disk.raw', 'sources.tar.gz', 'probe.o', 'source.c']:
                (output / 'build' / name).write_bytes(b'generated')
            (output / 'build/serial.log').write_text('diagnostic')
            (output / 'build/commands.json').write_text('[]')
            report = {'status': status, 'artifact_hash': 'original-executed-bytes'}
            evidence.compact_run(output, report)
            self.assertEqual(report['status'], status)
            self.assertEqual(report['artifact_retention']['removed_files'], 5)
            self.assertEqual((output / 'build/serial.log').read_text(), 'diagnostic')
            self.assertEqual(json.loads((output / 'results.json').read_text()), report)
            self.assertFalse((output / 'build/aether.iso').exists())

    def test_link_cleanup_does_not_follow_external_files_or_directories(self):
        output = self.run_directory()
        target = self.root / 'external'
        target.mkdir()
        (target / 'secret').write_text('keep')
        (output / 'external').symlink_to(target, target_is_directory=True)
        (output / 'linked.json').symlink_to(target / 'secret')
        evidence.compact_run(output, {})
        self.assertEqual((target / 'secret').read_text(), 'keep')
        self.assertFalse((output / 'external').exists())

    def test_large_log_keeps_tail_and_original_identity(self):
        output = self.run_directory()
        raw = b'x' * (evidence.LOG_LIMIT + 100) + b'last diagnostic'
        (output / 'serial.log').write_bytes(raw)
        report = {}
        evidence.compact_run(output, report)
        self.assertLessEqual((output / 'serial.log').stat().st_size, evidence.LOG_LIMIT)
        self.assertTrue((output / 'serial.log').read_bytes().endswith(b'last diagnostic'))
        self.assertEqual(report['artifact_retention']['shortened_logs']['serial.log']['sha256'],
                         hashlib.sha256(raw).hexdigest())

    def test_reject_unowned_nested_and_symlink_roots(self):
        output = self.run_directory()
        other = self.root / 'other'
        other.mkdir()
        (other / 'results.json').write_text('{}')
        (other / 'keep').write_text('keep')
        link = self.root / 'zig-out/thread-suite-link'
        link.symlink_to(other, target_is_directory=True)
        for path in [other, output / 'nested', link, self.root / 'zig-out']:
            with self.assertRaises(ValueError):
                evidence.compact_run(path, {})
        self.assertEqual((other / 'keep').read_text(), 'keep')

    def test_reject_redirected_output_parent(self):
        (self.root / 'zig-out').rename(self.root / 'real-output')
        (self.root / 'zig-out').symlink_to(self.root / 'real-output', target_is_directory=True)
        output = self.run_directory()
        with self.assertRaises(ValueError):
            evidence.compact_run(output, {})
        self.assertTrue((output / 'results.json').exists())

    def test_five_migrated_fixtures_match_original_pins(self):
        directories = [p for p in (ROOT / 'tests/fixtures').iterdir() if p.is_dir()]
        self.assertEqual(len(directories), 5)
        for directory in directories:
            self.assertFalse(directory.is_symlink())
            pins = json.loads((directory / 'pin.json').read_text())
            result = fixture_inputs.read_inputs(directory.name, pins)
            for name, digest in pins.items():
                self.assertEqual(hashlib.sha256(result[Path(name).name]).hexdigest(), digest)

    def fixture(self, name, pins):
        directory = self.root / 'tests/fixtures' / name
        directory.mkdir(parents=True)
        (directory / 'pin.json').write_text(json.dumps(pins))
        return directory

    def test_fixture_inventory_and_content_drift_reject(self):
        digest = hashlib.sha256(b'original').hexdigest()
        pins = {'input.c': digest}
        directory = self.fixture('drift', pins)
        (directory / 'input.c').write_bytes(b'changed')
        with patch.object(fixture_inputs, 'ROOT', self.root):
            with self.assertRaises(RuntimeError):
                fixture_inputs.read_inputs('drift', {})
            with self.assertRaises(RuntimeError):
                fixture_inputs.read_inputs('drift', pins)

    def test_fixture_traversal_and_external_link_reject(self):
        external = self.root / 'external.c'
        external.write_bytes(b'original')
        digest = hashlib.sha256(external.read_bytes()).hexdigest()
        bad = {'../../../external.c': digest}
        self.fixture('traversal', bad)
        good = {'input.c': digest}
        directory = self.fixture('link', good)
        (directory / 'input.c').symlink_to(external)
        with patch.object(fixture_inputs, 'ROOT', self.root):
            for name, pins in [('traversal', bad), ('link', good)]:
                with self.assertRaises(ValueError):
                    fixture_inputs.read_inputs(name, pins)

    def test_reproduction_failure_disposes_owned_source_and_records_failure(self):
        work = self.root / 'aether-reproduce-fixture'
        work.mkdir()
        with patch.object(reproduce, 'verify'), \
                patch.object(reproduce.tempfile, 'mkdtemp', return_value=str(work)), \
                patch.object(reproduce.shutil, 'copy2', side_effect=RuntimeError('copy failure')):
            with self.assertRaisesRegex(RuntimeError, 'copy failure'):
                reproduce.reproduce()
        result = json.loads((work / 'results.json').read_text())
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['error'], 'copy failure')
        self.assertFalse((work / 'source').exists())
