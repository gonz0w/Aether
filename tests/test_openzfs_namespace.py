# SPDX-License-Identifier: BSD-2-Clause
"""Fixture identity/ownership guards; actual ZPL decoding is a separate host run."""
import hashlib
import io
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import openzfs_namespace as namespace


class NamespaceFixture(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='aether-namespace-')
        self.addCleanup(temp.cleanup)
        self.out = Path(temp.name)

    def archive(self, members):
        path = self.out / 'synthetic.tar.gz'
        with tarfile.open(path, 'w:gz') as archive:
            for name, kind, size in members:
                item = tarfile.TarInfo(name)
                item.type = kind
                item.size = size
                item.linkname = 'elsewhere'
                archive.addfile(item, io.BytesIO(bytes(size)) if item.isfile() else None)
        return path

    def test_actual_upstream_fixture_identity_sparse_copy_and_exclusive_ownership(self):
        result = namespace.prepare_fixture(self.out)
        target = Path(result['output'])
        self.assertEqual(result['archive_sha256'], namespace.FIXTURE_SHA256)
        self.assertEqual(result['image_sha256'], namespace.FIXTURE_IMAGE_SHA256)
        self.assertEqual(target.stat().st_size, 1073741824)
        self.assertEqual(target.stat().st_mode & 0o777, 0o444)
        # A sparse copy must not accidentally allocate a gigabyte of zeroes.
        self.assertLess(target.stat().st_blocks * 512, 64 * 1024 * 1024)
        with self.assertRaises(FileExistsError):
            namespace.prepare_fixture(self.out)
        self.assertTrue(target.exists())

    def test_hash_mismatch_does_not_create_output(self):
        archive = self.archive([('testpool_zstd', tarfile.REGTYPE, 8)])
        with self.assertRaisesRegex(ValueError, 'compressed hash mismatch'):
            namespace.prepare_fixture(self.out, archive)
        self.assertFalse((self.out / 'namespace-pool.img').exists())

    def test_wrong_name_type_size_and_multiple_members_do_not_extract_paths(self):
        for members in (
            [('../escape', tarfile.REGTYPE, 8)],
            [('/escape', tarfile.REGTYPE, 8)],
            [('testpool_zstd', tarfile.SYMTYPE, 0)],
            [('testpool_zstd', tarfile.REGTYPE, 8)],
            [('testpool_zstd', tarfile.REGTYPE, 8), ('extra', tarfile.REGTYPE, 0)],
        ):
            with self.subTest(members=members):
                archive = self.archive(members)
                # Exercise structural guards independently of the real identity
                # guard; synthetic bytes never become an accepted input pin.
                with patch.object(namespace, 'FIXTURE_SHA256', hashlib.sha256(archive.read_bytes()).hexdigest()):
                    with self.assertRaisesRegex(ValueError, 'single pinned regular member'):
                        namespace.prepare_fixture(self.out, archive)
                self.assertFalse((self.out / 'namespace-pool.img').exists())

    def test_existing_symlink_and_referent_are_preserved(self):
        sentinel = self.out / 'sentinel'
        sentinel.write_bytes(b'preserve')
        target = self.out / 'namespace-pool.img'
        target.symlink_to(sentinel)
        with self.assertRaises(FileExistsError):
            namespace.prepare_fixture(self.out)
        self.assertTrue(target.is_symlink())
        self.assertEqual(sentinel.read_bytes(), b'preserve')

    def tiny_copy(self):
        path = self.out / 'tiny.tar.gz'
        data = b'ABCDEFGH'
        with tarfile.open(path, 'w:gz') as archive:
            item = tarfile.TarInfo('testpool_zstd')
            item.size = len(data)
            archive.addfile(item, io.BytesIO(data))
        self.enterContext(patch.multiple(namespace, FIXTURE_BYTES=len(data),
                                        FIXTURE_SHA256=hashlib.sha256(path.read_bytes()).hexdigest(),
                                        FIXTURE_IMAGE_SHA256=hashlib.sha256(data).hexdigest()))
        return path

    def test_interrupted_copy_removes_only_its_partial_output(self):
        archive = self.tiny_copy()
        class FailedRead(io.BytesIO):
            def read(self, size=-1):
                if self.tell():
                    raise OSError('injected copy failure')
                return super().read(4)
        with patch.object(tarfile.TarFile, 'extractfile', return_value=FailedRead(b'ABCDEFGH')):
            with self.assertRaisesRegex(OSError, 'injected copy failure'):
                namespace.prepare_fixture(self.out, archive)
        self.assertFalse((self.out / 'namespace-pool.img').exists())

    def test_suppressed_successful_write_fails_actual_image_oracle(self):
        archive = self.tiny_copy()
        target = self.out / 'namespace-pool.img'
        original = Path.open
        class SuppressedWrite:
            def __init__(self, file):
                self.file = file
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return self.file.__exit__(*args)
            def __getattr__(self, name):
                return getattr(self.file, name)
            def write(self, data):
                return len(data)
        def opened(path, mode='r', *args, **kwargs):
            file = original(path, mode, *args, **kwargs)
            return SuppressedWrite(file) if path == target and mode == 'xb' else file
        with patch.object(Path, 'open', opened):
            with self.assertRaisesRegex(ValueError, 'copied image hash mismatch'):
                namespace.prepare_fixture(self.out, archive)
        self.assertFalse(target.exists())


if __name__ == '__main__':
    unittest.main()
