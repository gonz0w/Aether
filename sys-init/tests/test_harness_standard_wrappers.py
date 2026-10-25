# SPDX-License-Identifier: BSD-2-Clause
"""Synthetic offline releases; no mutation of published pins or vendor bytes."""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class StandardWrapperTests(unittest.TestCase):
    def fixture(self, directory, kind='experience', failing=False):
        root = Path(directory)
        docs = root / 'docs'
        release = docs / 'vendor' / ('aether-' + kind) / 'v0.1.0'
        (release / 'conformance').mkdir(parents=True)
        shutil.copy(ROOT / 'docs' / ('check-' + kind + '.py'), docs)
        code = ('import os,sys\nfrom pathlib import Path\n'
                + ('assert False, "required assertion witness"\n' if failing else
                   'assert sys.flags.optimize == 0, "assertions disabled"\n')
                + 'assert os.environ["SYS_INIT_TEST_PRESERVE"] == "preserved"\n'
                + 'Path(os.environ["SYS_INIT_TEST_MARKER"]).write_text("ran")\n'
                + 'print("fixture reference passed")\n')
        (release / 'conformance/check.py').write_text(code)
        self.seal(docs, release, kind)
        return docs, release, root / 'executed'

    def seal(self, docs, release, kind='experience', rows=None):
        if rows is None:
            rows = [hashlib.sha256(p.read_bytes()).hexdigest() + '  '
                    + str(p.relative_to(release)) for p in sorted(release.rglob('*'))
                    if p.is_file() and p.name != 'SHA256SUMS']
        manifest = release / 'SHA256SUMS'
        manifest.write_text('\n'.join(rows) + ('\n' if rows else ''))
        digest = hashlib.sha256(manifest.read_bytes()).hexdigest()
        (docs / (kind + '.lock')).write_text(
            'format=aether-' + kind + '-pin-v1\nversion=v0.1.0\n'
            'source_project=Aether-standards\nsource_release=' + kind + '/v0.1.0\n'
            'manifest_sha256=' + digest + '\n')

    def invoke(self, docs, marker, kind='experience', optimize='0', flags=()):
        return subprocess.run(
            [sys.executable, *flags, str(docs / ('check-' + kind + '.py')), '--ignored'],
            capture_output=True, text=True, timeout=10,
            env=dict(os.environ, PYTHONOPTIMIZE=optimize, PYTHONDONTWRITEBYTECODE='1',
                     SYS_INIT_TEST_MARKER=str(marker), SYS_INIT_TEST_PRESERVE='preserved'))

    def denied(self, docs, marker, message):
        result = self.invoke(docs, marker)
        self.assertEqual(result.returncode, 1, result)
        self.assertFalse(marker.exists(), 'unverified checker executed')
        self.assertEqual(result.stdout, '')
        self.assertIn(message, result.stderr)

    def test_valid_inputs_and_assertion_modes(self):
        for kind in ('experience', 'distribution'):
            for optimize, flags in [('0', ()), ('1', ()), ('2', ()), ('0', ('-O',)), ('2', ('-OO',))]:
                for failing in (False, True):
                    with self.subTest(kind=kind, optimize=optimize, flags=flags, failing=failing):
                        with tempfile.TemporaryDirectory() as directory:
                            docs, _, marker = self.fixture(directory, kind, failing)
                            result = self.invoke(docs, marker, kind, optimize, flags)
                            if failing:
                                self.assertEqual(result.returncode, 1)
                                self.assertIn('required assertion witness', result.stderr)
                                self.assertFalse(marker.exists())
                            else:
                                self.assertEqual(result.returncode, 0, result.stderr)
                                self.assertEqual(result.stdout, 'fixture reference passed\n')
                                self.assertEqual(marker.read_text(), 'ran')

    def test_invalid_lock_fields_reject_before_execution(self):
        mutations = [
            (lambda s: s + 'version=v0.1.0\n', 'duplicate pin field'),
            (lambda s: s + 'extra=value\n', 'unexpected pin fields'),
            (lambda s: s.replace('version=v0.1.0\n', ''), 'unexpected pin fields'),
            (lambda s: s.replace('aether-experience-pin-v1', 'wrong'), 'unsupported pin'),
            (lambda s: s.replace('Aether-standards', 'other'), 'unsupported pin'),
            (lambda s: s.replace('version=v0.1.0', 'version=../outside'), 'unsafe version'),
            (lambda s: s.replace('source_release=experience/', 'source_release=wrong/'), 'invalid release'),
            (lambda s: s.replace('manifest_sha256=', 'manifest_sha256=G'), 'invalid release'),
            (lambda s: s + 'broken\n', 'not enough values'),
        ]
        for mutation, message in mutations:
            with self.subTest(message=message), tempfile.TemporaryDirectory() as directory:
                docs, _, marker = self.fixture(directory)
                pin = docs / 'experience.lock'
                pin.write_text(mutation(pin.read_text()))
                self.denied(docs, marker, message)

    def test_manifest_and_inventory_reject_before_execution(self):
        for case in ('bad-pin', 'changed-file', 'extra-file', 'missing-file',
                     'empty', 'duplicate', 'traversal', 'absolute', 'noncanonical',
                     'malformed', 'self', 'missing-checker'):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory:
                docs, release, marker = self.fixture(directory)
                manifest = release / 'SHA256SUMS'
                row = manifest.read_text().strip()
                digest = row.split('  ')[0]
                message = 'release inventory mismatch'
                if case == 'bad-pin':
                    manifest.write_text(row + '\n\n'); message = 'manifest pin mismatch'
                elif case == 'changed-file':
                    (release / 'conformance/check.py').write_text('raise SystemExit(0)\n')
                    message = 'file mismatch'
                elif case == 'extra-file':
                    (release / 'extra').write_text('extra')
                elif case == 'missing-file':
                    (release / 'conformance/check.py').unlink(); message = 'No such file'
                elif case == 'missing-checker':
                    (release / 'conformance/check.py').unlink()
                    (release / 'reference.txt').write_text('reference')
                    self.seal(docs, release)
                else:
                    rows = {'empty': [], 'duplicate': [row, row],
                            'traversal': [digest + '  ../outside'],
                            'absolute': [digest + '  /outside'],
                            'noncanonical': [digest + '  conformance/./check.py'],
                            'malformed': ['not a manifest row'],
                            'self': [digest + '  SHA256SUMS']}[case]
                    self.seal(docs, release, rows=rows)
                    message = ('release inventory mismatch' if case == 'empty' else
                               'malformed manifest' if case == 'malformed' else
                               'unsafe or duplicate release path')
                self.denied(docs, marker, message)

    def test_symlink_roots_and_files_reject_before_execution(self):
        for case in ('release', 'vendor', 'manifest', 'checker'):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory:
                docs, release, marker = self.fixture(directory)
                path = {'release': release, 'vendor': docs / 'vendor',
                        'manifest': release / 'SHA256SUMS',
                        'checker': release / 'conformance/check.py'}[case]
                moved = Path(directory) / 'relocated'
                path.rename(moved)
                path.symlink_to(moved, target_is_directory=moved.is_dir())
                self.denied(docs, marker, 'symlink')
