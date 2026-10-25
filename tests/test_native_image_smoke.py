# SPDX-License-Identifier: BSD-2-Clause
"""Verify producer-owned ELF rejection controls modify their intended boundary."""
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from native_image_smoke import mutate


def fixture():
    data = bytearray(256)
    struct.pack_into('<Q', data, 32, 64)
    struct.pack_into('<H', data, 56, 2)
    struct.pack_into('<IIQQQQQQ', data, 64, 1, 6, 0, 0x600000, 0, 4, 8192, 4096)
    struct.pack_into('<IIQQQQQQ', data, 120, 7, 4, 0, 0x600100, 0, 4, 8, 8)
    return bytes(data)


class ImageControls(unittest.TestCase):
    def test_relocation_preserves_tls_relationship(self):
        raw = fixture()
        for mode, target in [('stack', 0x08000000), ('arena', 0x10000000)]:
            changed = mutate(raw, mode)
            self.assertEqual(struct.unpack_from('<Q', changed, 80)[0], target)
            self.assertEqual(struct.unpack_from('<Q', changed, 136)[0], target + 256)
            self.assertEqual(changed[96:112], raw[96:112])

    def test_structural_controls(self):
        raw = fixture()
        self.assertEqual(struct.unpack_from('<H', mutate(raw, 'pie'), 16)[0], 3)
        self.assertEqual(struct.unpack_from('<I', mutate(raw, 'wx'), 68)[0], 7)
        self.assertEqual(struct.unpack_from('<Q', mutate(raw, 'quota'), 104)[0], 2048 * 4096)
        oversized = mutate(raw, 'file-limit')
        self.assertEqual(len(oversized), 8 * 1024 * 1024 + 1)
        self.assertEqual(oversized[:len(raw)], raw)

    def test_separate_relro_segment_is_not_mutated(self):
        raw = bytearray(fixture())
        struct.pack_into('<H', raw, 56, 3)
        struct.pack_into('<IIQQQQQQ', raw, 176, 1, 6, 0, 0x500000, 0, 4, 16, 4096)
        changed = mutate(raw, 'wx')
        self.assertEqual(struct.unpack_from('<I', changed, 68)[0], 7)
        self.assertEqual(changed[176:232], raw[176:232])

    def test_unknown_control_rejects(self):
        with self.assertRaises(ValueError):
            mutate(fixture(), 'unknown')
