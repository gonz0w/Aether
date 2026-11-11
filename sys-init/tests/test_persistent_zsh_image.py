# SPDX-License-Identifier: BSD-2-Clause
"""Focused controls for the sealed persistent Zsh image inputs."""

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location('persistent_zsh_image',
                                             SCRIPTS / 'build-persistent-zsh.py')
IMAGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(IMAGE)


class SealInputs(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name).resolve()
        self.member = self.root / 'payload.bin'
        self.member.write_bytes(b'a sealed test member')
        self.manifest = self.root / 'SHA256SUMS'
        self.manifest.write_text(f'{IMAGE.identity(self.member)}  {self.member.name}\n')
        self.manifest_sha = IMAGE.identity(self.manifest)

    def read(self):
        return IMAGE.read_seal(self.root, self.manifest_sha, {self.member.name})

    def test_exact_member_is_admitted(self):
        self.assertEqual(self.read(), {self.member.name: self.member.read_bytes()})

    def test_other_roles_manifest_is_rejected_before_payload_read(self):
        self.manifest_sha = '0' * 64
        self.member.unlink()
        with self.assertRaisesRegex(ValueError, 'does not match the selected role'):
            self.read()

    def test_modified_member_is_rejected(self):
        self.member.write_bytes(b'changed member')
        with self.assertRaisesRegex(ValueError, 'seal member changed'):
            self.read()

    def test_extra_member_is_rejected(self):
        (self.root / 'extra').write_bytes(b'unexpected')
        with self.assertRaisesRegex(ValueError, 'seal membership'):
            self.read()

    def test_link_to_exact_bytes_is_rejected(self):
        other = self.root / 'other'
        self.member.rename(other)
        self.member.symlink_to(other)
        with self.assertRaisesRegex(ValueError, 'symlink component'):
            self.read()


if __name__ == '__main__':
    unittest.main()
