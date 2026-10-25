#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Approved source/patch gate controls using retained upstream bytes."""
from pathlib import Path
import runpy
import tempfile
import unittest

apply = runpy.run_path('experiments/qemu-termios/apply-cmspar.py')['apply']
SOURCE = Path('build/qemu-translation-j5hf1b1a/original/linux-user/syscall.c').read_bytes()
PATCH = Path('experiments/qemu-termios/cmspar.patch').read_bytes()


class PatchTests(unittest.TestCase):
    def test_exact_patch_and_rejections(self):
        for variant in ('good', 'source-drift', 'patch-drift'):
            with self.subTest(variant=variant):
                work = Path(tempfile.mkdtemp(prefix='qemu-patch-control-', dir='build'))
                source, patch = work / 'syscall.c', work / 'change.patch'
                original = SOURCE + (b'\n' if variant == 'source-drift' else b'')
                source.write_bytes(original)
                patch.write_bytes(PATCH + (b'\n' if variant == 'patch-drift' else b''))
                if variant == 'good':
                    apply(source, patch)
                    self.assertEqual(source.read_bytes().count(
                        b'{ TARGET_CMSPAR, TARGET_CMSPAR, CMSPAR, CMSPAR },'), 1)
                else:
                    with self.assertRaises(RuntimeError):
                        apply(source, patch)
                    self.assertEqual(source.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
