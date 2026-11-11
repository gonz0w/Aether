# SPDX-License-Identifier: BSD-2-Clause
"""Focused controls for the sealed persistent Zsh image inputs."""

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

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


class SourceInputs(unittest.TestCase):
    def test_exact_role_payloads_and_envelope_are_both_required(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            blobs = {'filesystem.elf': b'engine', 'zsh.elf': b'Zsh',
                     'helper.elf': b'helper', 'owner.bin': b'owner'}
            for name, raw in blobs.items():
                (root / name).write_bytes(raw)
            with patch.object(IMAGE, 'digest', return_value='expected'):
                envelope = IMAGE.pack_envelope('seed', blobs['filesystem.elf'], blobs, 'expected')
            lock = root / 'lock.json'
            role = {'members': {name: IMAGE.digest(raw) for name, raw in blobs.items()},
                    'envelope': IMAGE.digest(envelope)}
            lock.write_text(json.dumps({'schema': 'aether-r1-source-zsh-v1',
                                        'roles': {'seed': role}}))
            with patch.object(IMAGE, 'SOURCE_ARTIFACT_LOCK', lock):
                self.assertEqual(IMAGE.source_envelope('seed', root)[0], envelope)
                (root / 'helper.elf').write_bytes(b'changed helper')
                with self.assertRaisesRegex(ValueError, 'source-built seed input differs'):
                    IMAGE.source_envelope('seed', root)
                (root / 'helper.elf').write_bytes(blobs['helper.elf'])
                role['envelope'] = '0' * 64
                lock.write_text(json.dumps({'schema': 'aether-r1-source-zsh-v1',
                                            'roles': {'seed': role}}))
                with self.assertRaisesRegex(ValueError, 'envelope'):
                    IMAGE.source_envelope('seed', root)


if __name__ == '__main__':
    unittest.main()
