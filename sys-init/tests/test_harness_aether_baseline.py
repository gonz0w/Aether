# SPDX-License-Identifier: BSD-2-Clause
"""Focused input/ownership controls for the offline ABI22 recipe."""
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
SPEC = importlib.util.spec_from_file_location('aether_baseline', ROOT / 'scripts/build-aether-baseline.py')
BASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BASE)


def archive(entries):
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode='w:gz') as output:
        for name, data, kind in entries:
            member = tarfile.TarInfo(name)
            member.type = kind
            member.size = len(data) if kind == tarfile.REGTYPE else 0
            member.linkname = 'outside'
            output.addfile(member, io.BytesIO(data) if member.size else None)
    return stream.getvalue()


class BaselineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='baseline-control-', dir=ROOT / 'out')
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def test_archive_rejects_changed_missing_duplicate_and_link_members(self):
        expected = {'user/main.rs': BASE.digest(b'source')}
        good = [('user/main.rs', b'source', tarfile.REGTYPE)]
        self.assertEqual(BASE.archive_files(archive(good), expected), {'user/main.rs': b'source'})
        variants = [[], good + good, [('user/main.rs', b'changed', tarfile.REGTYPE)],
                    [('user/main.rs', b'', tarfile.SYMTYPE)],
                    [('user/main.rs', b'', tarfile.LNKTYPE)],
                    [('user/../main.rs', b'source', tarfile.REGTYPE)],
                    [('/user/main.rs', b'source', tarfile.REGTYPE)]]
        for entries in variants:
            with self.subTest(entries=entries), self.assertRaises(ValueError):
                BASE.archive_files(archive(entries), expected)

    def test_source_budget_rejects_before_staging(self):
        with patch.object(BASE, 'MAX_INPUT', 2), self.assertRaises(ValueError):
            BASE.archive_files(archive([('a', b'abc', tarfile.REGTYPE)]), {'a': BASE.digest(b'abc')})

    def test_input_link_and_changed_pin_reject(self):
        original = self.directory / 'input'
        original.write_bytes(b'old')
        link = self.directory / 'link'
        link.symlink_to(original)
        with self.assertRaises(ValueError):
            BASE.ordinary(link)
        original.write_bytes(b'new')
        with self.assertRaises(ValueError):
            BASE.verified(original, BASE.digest(b'old'))

    def test_envelope_rejects_truncation_profile_reserved_and_size(self):
        import struct
        raw = b'AENSI001' + struct.pack('<6I', 1, 1, 1, 1, 0, 0) + bytes(48) + b'abcd'
        self.assertEqual(BASE.envelope(raw, b'owner')[-5:], b'owner')
        for bad in [raw[:-1], b'AENMX001' + raw[8:], raw[:24] + b'\1' + raw[25:]]:
            with self.subTest(raw=bad), self.assertRaises(ValueError):
                BASE.envelope(bad, b'owner')
        with self.assertRaises(ValueError):
            BASE.envelope(raw, bytes(16385))

    def test_existing_output_is_preserved(self):
        output = self.directory / 'existing'
        output.mkdir()
        sentinel = output / 'keep'
        sentinel.write_text('existing')
        with patch.object(BASE, 'preflight') as preflight, self.assertRaises(BASE.Blocked):
            BASE.build(output, self.directory)
        preflight.assert_not_called()
        self.assertEqual(sentinel.read_text(), 'existing')

    def test_output_parent_traversal_rejects_before_preflight(self):
        output = ROOT / 'out' / '..' / 'escaped-baseline'
        with patch.object(BASE, 'preflight') as preflight, self.assertRaises(BASE.Blocked):
            BASE.build(output, self.directory)
        preflight.assert_not_called()
        self.assertFalse(output.exists())

    def test_preflight_failure_creates_no_output(self):
        output = self.directory / 'new'
        with patch.object(BASE, 'preflight', side_effect=ValueError('changed input')), self.assertRaises(BASE.Blocked):
            BASE.build(output, self.directory)
        self.assertFalse(output.exists())

    def test_tool_failure_retains_failed_phase_and_stops(self):
        output = self.directory / 'failed'
        tools = {n: {'path': '/usr/bin/false', 'sha256': 'unused'} for n in ['rustc', 'python', 'xorriso', 'zig', 'qemu']}
        captured = {'docs/evidence/si07-loop-2026-10-03/normal/native-c.bin': b'not used',
                    'docs/evidence/si07-owner-2026-10-03/positive-2/startup.bin': b'startup'}
        prepared = ({'profile': 'AENSI001/ABI22', 'consumed_sha256': 'fixture'}, captured,
                    {'user/native-command/placeholder': b'x'}, {}, tools)
        error = subprocess.CalledProcessError(1, ['false'])
        with patch.object(BASE, 'preflight', return_value=prepared), patch.object(BASE, 'run_tool', side_effect=error) as run, self.assertRaises(subprocess.CalledProcessError):
            BASE.build(output, self.directory)
        self.assertEqual(run.call_count, 1)
        report = json.loads((output / 'result.json').read_text())
        self.assertEqual(report['status'], 'fail')
        self.assertEqual(report['commands'][0]['status'], 'fail')
        self.assertNotIn('artifacts', report)

    def test_service_table_compiler_rejects_unsupported_policy(self):
        pin = json.loads(BASE.ordinary(BASE.LOCK))['tools']['rustc']
        BASE.verified(Path(pin['path']), pin['sha256'], 256 * 1024 * 1024)
        table = (ROOT / 'prototypes/native-command/service_table.rs').read_text()
        backend = 'Service { role: Role::Backend, image_slot: 1, order: 0, retries: 0 },'
        cases = [
            ('valid', table, None),
            ('image', table.replace('image_slot: 1, order: 0', 'image_slot: 0, order: 0'), 'role/image mismatch'),
            ('role', table.replace(backend, backend.replace('Role::Backend', 'Role::Runner')), 'role/image mismatch'),
            ('order', table.replace('image_slot: 1, order: 0', 'image_slot: 1, order: 1'), 'unsupported service order'),
            ('retry', table.replace('order: 0, retries: 0', 'order: 0, retries: 1'), 'unsupported automatic retry budget'),
            ('missing', table.replace(backend, ''), 'expected an array with a size of 3'),
        ]
        cases += [
            ('supervised-valid', table, None),
            ('supervised-command-two', table.replace('retries: if cfg!(init_supervised) { 1 } else { 0 }', 'retries: 2'), 'unsupported automatic retry budget'),
            ('supervised-backend', table.replace('order: 0, retries: 0', 'order: 0, retries: 1'), 'unsupported automatic retry budget'),
            ('supervised-runner', table.replace('order: 1, retries: 0', 'order: 1, retries: 1'), 'unsupported automatic retry budget'),
        ]
        environment = dict(os.environ)
        environment['DYLD_LIBRARY_PATH'] = str(Path(pin['path']).parent.parent / 'lib')
        for name, source, diagnostic in cases:
            with self.subTest(name=name):
                directory = self.directory / name
                directory.mkdir()
                (directory / 'service_table.rs').write_text(source)
                main = directory / 'control.rs'
                main.write_text('#[derive(Clone, Copy)] pub enum Role { Backend, Runner, Command }\nmod service_table;\n')
                artifact = directory / 'control.rlib'
                argv = [pin['path'], '--edition=2024', '--crate-type=lib', str(main), '-o', str(artifact)]
                if name.startswith('supervised-'):
                    argv += ['--cfg', 'init_supervised']
                log = directory / 'compiler.log'
                if diagnostic is None:
                    BASE.run_tool(argv, environment, log)
                    self.assertTrue(artifact.is_file())
                else:
                    with self.assertRaises(subprocess.CalledProcessError):
                        BASE.run_tool(argv, environment, log)
                    self.assertIn(diagnostic, log.read_text())
                    self.assertFalse(artifact.exists())

    def test_supervised_cli_requires_explicit_table_selection(self):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/build-aether-baseline.py'),
                                 str(self.directory / 'new'), '--dependencies', str(self.directory), '--supervised'],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 64)
        self.assertIn('--supervised requires --service-table', result.stderr)
        self.assertFalse((self.directory / 'new').exists())

    def test_cli_help_version_and_usage(self):
        for args, code in [(['--help'], 0), (['--version'], 0), ([], 64)]:
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/build-aether-baseline.py'), *args],
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, code)
            self.assertTrue(result.stdout if code == 0 else result.stderr)


if __name__ == '__main__':
    unittest.main()
