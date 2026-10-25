# SPDX-License-Identifier: BSD-2-Clause
"""Cross-wrapper lock contract controls using private synthetic releases."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = {'standards': 'foundations', 'experience': 'experience', 'distribution': 'distribution'}


class OfflineLockTests(unittest.TestCase):
    def fixture(self, root, suffix):
        family = FAMILIES[suffix]
        docs = root / 'docs'
        release = docs / 'vendor' / ('aether-' + family) / 'v0.1.0'
        (release / 'conformance').mkdir(parents=True)
        checker = release / 'conformance/check.py'
        checker.write_bytes(b'raise SystemExit(0)\n')
        manifest = release / 'SHA256SUMS'
        manifest.write_text(hashlib.sha256(checker.read_bytes()).hexdigest() + '  conformance/check.py\n')
        lock = docs / (suffix + '.lock')
        lock.write_text('format=aether-' + family + '-pin-v1\nversion=v0.1.0\n'
                        'source_project=Aether-standards\nsource_release=' + family + '/v0.1.0\n'
                        'manifest_sha256=' + hashlib.sha256(manifest.read_bytes()).hexdigest() + '\n')
        spec = importlib.util.spec_from_file_location('offline_' + suffix, ROOT / 'docs' / ('check-' + suffix + '.py'))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.__file__ = str(docs / ('check-' + suffix + '.py'))
        return module, lock, manifest, checker

    def test_accepted_field_order_and_line_endings(self):
        for suffix in FAMILIES:
            for separator, final in [('\n', True), ('\r\n', True), ('\n', False)]:
                with self.subTest(suffix=suffix, separator=separator, final=final), tempfile.TemporaryDirectory() as directory:
                    module, lock, _, checker = self.fixture(Path(directory), suffix)
                    rows = list(reversed(lock.read_text().splitlines()))
                    lock.write_bytes((separator.join(rows) + (separator if final else '')).encode('ascii'))
                    with patch.object(module, 'run_reference') as run:
                        module.main()
                    run.assert_called_once()
                    command = run.call_args.args[0]
                    self.assertEqual(command[:4], [module.sys.executable, '-I', '-S', '-B'])
                    self.assertEqual(Path(command[4]).name, 'check.py')
                    self.assertNotEqual(Path(command[4]), checker.resolve())
                    self.assertFalse(Path(command[4]).exists(), 'temporary copy leaked')


    def test_invalid_fields_prevent_child_invocation(self):
        mutations = [lambda s: s + 'version=v0.1.0\n', lambda s: s + 'extra=x\n',
                     lambda s: s.replace('version=v0.1.0\n', ''),
                     lambda s: s.replace('version=v0.1.0', 'version=../outside'),
                     lambda s: s.replace('Aether-standards', 'other'),
                     lambda s: s.replace('manifest_sha256=', 'manifest_sha256=G'),
                     lambda s: s + '\n', lambda s: '# comment\n' + s,
                     lambda s: ' ' + s, lambda s: '\ufeff' + s]
        for suffix in FAMILIES:
            for index, mutate in enumerate(mutations):
                with self.subTest(suffix=suffix, mutation=index), tempfile.TemporaryDirectory() as directory:
                    module, lock, _, _ = self.fixture(Path(directory), suffix)
                    lock.write_text(mutate(lock.read_text()))
                    with patch.object(module, 'run_reference') as run, self.assertRaises(ValueError):
                        module.main()
                    run.assert_not_called()

    def test_manifest_pin_precedes_parsing_and_execution(self):
        for suffix in FAMILIES:
            with self.subTest(suffix=suffix), tempfile.TemporaryDirectory() as directory:
                module, _, manifest, _ = self.fixture(Path(directory), suffix)
                manifest.write_bytes(b'\xffnot ASCII')
                with patch.object(module, 'run_reference') as run, self.assertRaisesRegex(ValueError, 'manifest pin mismatch'):
                    module.main()
                run.assert_not_called()

    def test_changed_payload_prevents_child_invocation(self):
        for suffix in FAMILIES:
            with self.subTest(suffix=suffix), tempfile.TemporaryDirectory() as directory:
                module, _, _, checker = self.fixture(Path(directory), suffix)
                checker.write_text('changed')
                with patch.object(module, 'run_reference') as run, self.assertRaisesRegex(ValueError, 'file mismatch'):
                    module.main()
                run.assert_not_called()
