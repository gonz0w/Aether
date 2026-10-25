# SPDX-License-Identifier: BSD-2-Clause
"""Read-only static linkage resolution; mutable/unknown indirect edges deny."""
from pathlib import Path
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import owner_stack


class ConstantEdges(unittest.TestCase):
    def test_explicit_stack_budget_preserves_conservative_margins(self):
        assembly='''0000000000400000 <_start>:
 400000: call 0x400010 <worker>
 400005: ret
0000000000400010 <worker>:
 400010: sub rsp, 0xf00
 400017: add rsp, 0xf00
 40001e: ret
'''
        with self.assertRaises(owner_stack.StackLimit):
            owner_stack.inspect(assembly)
        result=owner_stack.inspect(assembly,stack_bytes=8192)
        self.assertEqual(result['usable_stack_bytes'],8184)
        self.assertEqual(result['entry_stack_bytes'],4104)
        for size in (0,4088,6000,16384,True,8192.0):
            with self.assertRaisesRegex(ValueError,'unknown owner stack profile'):
                owner_stack.inspect(assembly,stack_bytes=size)

    def test_only_exact_immutable_linkage_edges_resolve(self):
        raw = bytearray(1024)
        raw[:6] = b'\x7fELF\x02\x01'
        struct.pack_into('<QQQ', raw, 24, 0x400000, 64, 512)
        struct.pack_into('<HHHHHH', raw, 52, 64, 56, 1, 64, 2, 0)
        struct.pack_into('<IIQQQQQQ', raw, 64, 1, 5, 256, 0x400000, 0, 256, 256, 4096)
        raw[256:262] = b'\xff\x15\x1a\x00\x00\x00'
        struct.pack_into('<Q', raw, 288, 0x400040)
        struct.pack_into('<IIQQQQIIQQ', raw, 576, 0, 2, 0, 0, 768, 48, 0, 0, 8, 24)
        struct.pack_into('<IBBHQQ', raw, 768, 0, 2, 0, 0, 0x400000, 6)
        struct.pack_into('<IBBHQQ', raw, 792, 0, 2, 0, 0, 0x400040, 1)
        assembly = '''0000000000400000 <_start>:
 400000: call qword ptr [rip + 0x1a] # comments are not evidence
0000000000400040 <worker>:
 400040: ret
'''
        with tempfile.TemporaryDirectory(prefix='aether-stack-constants-') as directory:
            elf = Path(directory) / 'owner.elf'
            elf.write_bytes(raw)
            result = owner_stack.inspect(assembly, elf=elf)
            self.assertEqual(result['entry_stack_bytes'], 264)
            self.assertEqual(result['readonly_constant_edges'], 1)
            for label, at, data in [
                ('writable', 68, struct.pack('<I', 7)),
                ('wrong-opcode', 257, b'\x25'),
                ('outside-pointer', 258, struct.pack('<i', 1024)),
                ('unknown-target', 288, struct.pack('<Q', 0x400041)),
                ('recursive', 288, struct.pack('<Q', 0x400000)),
                ('truncated-load', 96, struct.pack('<Q', 2000)),
            ]:
                with self.subTest(label=label):
                    changed = raw.copy()
                    changed[at:at+len(data)] = data
                    elf.write_bytes(changed)
                    with self.assertRaises(ValueError):
                        owner_stack.inspect(assembly, elf=elf)
            elf.write_bytes(raw)
            changed = raw.copy()
            struct.pack_into('<H', changed, 56, 2)
            # A writable zero-file-byte BSS alias is still mutable memory.
            struct.pack_into('<IIQQQQQQ', changed, 120, 1, 6, 1024, 0x400000, 0, 0, 256, 4096)
            elf.write_bytes(changed)
            with self.assertRaisesRegex(ValueError, 'writable owner constant alias'):
                owner_stack.inspect(assembly, elf=elf)
            elf.write_bytes(raw)
            for indirect in ['call rax', 'jmp qword ptr [8*rdx + 0x400020]']:
                with self.assertRaises(ValueError):
                    owner_stack.inspect(assembly.replace(
                        'call qword ptr [rip + 0x1a] # comments are not evidence', indirect), elf=elf)


if __name__ == '__main__':
    unittest.main()
