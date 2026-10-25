#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Keep firmware exclusion separate from extraction path protection."""
import io
from pathlib import Path
import runpy
import tarfile
import tempfile
import unittest

extract = runpy.run_path('experiments/qemu-termios/extract-source.py')['extract']


class ExtractionTests(unittest.TestCase):
    def test_excluded_firmware(self):
        self.check(False)

    def test_unsafe_selected_link(self):
        self.check(True)

    def check(self, unsafe):
        work = Path(tempfile.mkdtemp(prefix='qemu-extract-control-', dir='build'))
        archive = work / 'source.tar'
        dest = work / 'output'
        dest.mkdir()
        with tarfile.open(archive, 'w') as stream:
            member = tarfile.TarInfo('qemu-10.0.11/roms/absolute')
            member.type = tarfile.SYMTYPE
            member.linkname = '/outside'
            stream.addfile(member)
            member = tarfile.TarInfo('qemu-10.0.11/source.c')
            member.size = 2
            stream.addfile(member, io.BytesIO(b'ok'))
            if unsafe:
                member = tarfile.TarInfo('qemu-10.0.11/unsafe')
                member.type = tarfile.SYMTYPE
                member.linkname = '/outside'
                stream.addfile(member)
        if unsafe:
            with self.assertRaises(tarfile.AbsoluteLinkError):
                extract(archive, dest)
        else:
            self.assertEqual(extract(archive, dest), ['qemu-10.0.11/roms/absolute'])
            self.assertEqual((dest / 'qemu-10.0.11/source.c').read_bytes(), b'ok')
            self.assertFalse((dest / 'qemu-10.0.11/roms').exists())


if __name__ == '__main__':
    unittest.main()
