# SPDX-License-Identifier: BSD-2-Clause
"""Offline recipe rejection, retained failures and native oracle controls."""
import ast
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
SPEC = importlib.util.spec_from_file_location('session_recipe', ROOT / 'scripts/build-aether-session.py')
B = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(B)
import serial_session_smoke as S


def archive(entries):
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode='w:gz') as tar:
        for name, data, kind in entries:
            m = tarfile.TarInfo(name)
            m.type, m.linkname = kind, 'outside'
            m.size = len(data) if kind == tarfile.REGTYPE else 0
            tar.addfile(m, io.BytesIO(data) if m.size else None)
    return stream.getvalue()


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='session-control-', dir=ROOT / 'out')
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def main(self, args):
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            code = B.main(args)
        return code, json.loads(out.getvalue())

    def test_archive_membership_links_aliases_hash_and_budget(self):
        data = b'payload'
        pin = {'bytes': len(data), 'sha256': B.digest(data)}
        good = [('normal/native-c.bin', data, tarfile.REGTYPE)]
        expected = {'normal/native-c.bin': pin}
        self.assertEqual(B.archive_files(archive(good), expected), {'normal/native-c.bin': data})
        bad = [[], good + good, [('normal/native-c.bin', b'changed', tarfile.REGTYPE)],
               [('normal/native-c.bin', b'', tarfile.SYMTYPE)], [('normal/native-c.bin', b'', tarfile.LNKTYPE)],
               [('normal/../native-c.bin', data, tarfile.REGTYPE)], [('/normal/native-c.bin', data, tarfile.REGTYPE)],
               [('normal//native-c.bin', data, tarfile.REGTYPE)]]
        for entries in bad:
            with self.subTest(entries=entries), self.assertRaises(ValueError):
                B.archive_files(archive(entries), expected)
        with patch.object(B, 'MAX_INPUT', 2), self.assertRaises(ValueError):
            B.archive_files(archive(good), expected)

    def test_envelope_preserves_clients_and_entropy_rejects_wrong_profile(self):
        raw = struct.pack('<8sIIIIQ', b'AENMX009', 1, 1, 1, 3, 0) + bytes(range(80)) + b'abcold'
        new = B.envelope(raw, b'new-owner')
        self.assertEqual(new[32:115], raw[32:115])
        self.assertEqual(new[115:], b'new-owner')
        self.assertEqual(struct.unpack_from('<I', new, 20)[0], 9)
        for bad in (raw[:-1], b'AENSI001' + raw[8:], raw[:24] + b'\1' + raw[25:]):
            with self.assertRaises(ValueError): B.envelope(bad, b'owner')
        for owner in (b'', bytes(16385)):
            with self.assertRaises(ValueError): B.envelope(raw, owner)

    def test_output_rejects_existing_traversal_link_and_outside(self):
        link = self.directory / 'link'; link.symlink_to(self.directory)
        for path in (self.directory, ROOT / 'out/../escape', link / 'new', ROOT / 'escape'):
            with patch.object(B, 'preflight') as before:
                code, result = self.main([str(path)])
            self.assertEqual((code, result['status']), (2, 'blocked'))
            before.assert_not_called()

    def test_preflight_missing_input_has_no_staging(self):
        output = self.directory / 'new'
        with patch.object(B, 'preflight', side_effect=FileNotFoundError('missing tool')):
            self.assertEqual(self.main([str(output)])[0], 2)
        self.assertFalse(output.exists())

    def test_ordinary_rejects_links_and_changed_hash(self):
        original = self.directory / 'input'; original.write_bytes(b'old')
        link = self.directory / 'link'; link.symlink_to(original)
        with self.assertRaises(ValueError): B.ordinary(link)
        with self.assertRaises(ValueError): B.verified(original, B.digest(b'new'))
        with self.assertRaises(ValueError): B.ordinary(original, 2)

    def test_tool_failure_timeout_cancel_retains_owned_result(self):
        tools = {'rustc': {'path': '/usr/bin/false'}}
        prepared = (b'{}', {'profile': 'fixture'}, {}, {'prototypes/native-session/init.rs': b'x'}, {}, tools)
        for error, expected in ((subprocess.CalledProcessError(1, ['false']), 1),
                                (subprocess.TimeoutExpired(['false'], 1), 1), (KeyboardInterrupt(), 130)):
            output = self.directory / ('failed-' + str(expected) + '-' + type(error).__name__)
            with patch.object(B, 'preflight', return_value=prepared), patch.object(B, 'run_tool', side_effect=error) as run:
                code, result = self.main([str(output)])
            self.assertEqual(code, expected)
            self.assertEqual(run.call_count, 1)
            self.assertEqual(result, json.loads((output / 'result.json').read_bytes()))
            self.assertEqual(result['commands'][0]['phase'], 'compile-elf')

    def test_independent_oracle_is_unchanged_and_rejects_mutations(self):
        lock = json.loads(B.LOCK.read_bytes())
        producer = B.verified(ROOT / lock['oracle'], lock['files'][lock['oracle']]).decode()
        func = lambda source: next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == 'check')
        self.assertEqual(ast.dump(func(producer)), ast.dump(func(Path(S.__file__).read_text())))
        packet = ROOT / 'docs/evidence/terminal-read-race-2026-10-04'
        record = json.loads((packet / 'fixed-immediate.json').read_bytes())
        raw = (packet / 'fixed-immediate-serial.log').read_bytes()
        workload = json.loads((ROOT / lock['workload']).read_bytes())
        self.assertEqual(S.check(raw, record, workload)['terminals'], 10)
        for bad in (b'', raw.replace(b'closed ok', b'closed NO'), raw + b'extra',
                    raw.replace(b'generation=5', b'generation=6')):
            with self.assertRaises(ValueError): S.check(bad, record, workload)

    def test_early_native_exit_is_failure_and_reaped(self):
        kit = self.directory / 'kit'; kit.mkdir(); (kit / 'vars.fd').write_bytes(b'vars')
        command = [sys.executable, '-c', 'import sys;sys.stderr.write("early exit\\n")']
        with patch.object(S, 'qemu_args', return_value=command), self.assertRaises(ValueError):
            S.smoke(self.directory, 'unused', {'expected.uart': '', 'exchange.json': b'{}'.hex()})
        record = json.loads((self.directory / 'smoke.json').read_bytes())
        self.assertEqual((record['status'], record['cleanup']), ('fail', 'emulator-reaped'))
        self.assertEqual(record['emulator_exit'], 0)

    def test_cli_help_version_and_usage(self):
        for args, expected in ((['--help'], 0), (['--version'], 0), ([], 64), (['out/new', '--smoke', 'other'], 64)):
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/build-aether-session.py'), *args],
                                    capture_output=True, timeout=10)
            self.assertEqual(result.returncode, expected)


if __name__ == '__main__':
    unittest.main()
