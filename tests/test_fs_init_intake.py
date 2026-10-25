# SPDX-License-Identifier: BSD-2-Clause
"""Actual linked owner intake; host inspection never executes candidate code."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import fs_init_intake as gate


class OwnerIntake(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='aether-init-intake-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.out = Path(cls.temp.name)
        cls.tools = json.loads((ROOT/'.deps/native-current/sdk/tools.lock.json').read_text())['tools']
        source = '''.section .text.entry,"ax",@progbits
.global _start
.type _start,@function
_start:
push %rbp
sub $16,%rsp
call worker
ud2
.size _start, .-_start
.section .text.worker,"ax",@progbits
.type worker,@function
worker:
sub $32,%rsp
add $32,%rsp
ret
.size worker, .-worker
.section .rodata,"a",@progbits
.fill 13000,1,17
.section .debug_probe,"",@progbits
.ascii "inspection metadata"
'''
        cls.source = source
        cls.elf, cls.raw = cls.build(source, 'good')
        cls.elf_bytes, cls.raw_bytes = cls.elf.read_bytes(), cls.raw.read_bytes()
        cls.expected = (gate.digest(cls.elf_bytes), gate.digest(cls.raw_bytes))

    @classmethod
    def build(cls, source, name):
        assembly = cls.out/(name+'.S')
        assembly.write_text(source)
        obj, elf, raw = (cls.out/(name+extension) for extension in ('.o', '.elf', '.raw'))
        for argv in (
            [cls.tools['clang']['path'], '--no-default-config', '--target=x86_64-unknown-none', '-c', str(assembly), '-o', str(obj)],
            [cls.tools['lld']['path'], '-T', str(ROOT/'user/storage/session/init-linker.ld'), str(obj), '-o', str(elf)],
            [str(Path(cls.tools['clang']['path']).resolve().parent/'llvm-objcopy'), '--only-section=.text', '-O', 'binary', str(elf), str(raw)],
        ):
            run = subprocess.run(argv, capture_output=True, text=True, timeout=30)
            if run.returncode:
                raise RuntimeError(run.stdout + run.stderr)
        return elf, raw

    def intake(self, elf=None, raw=None, expected=None):
        return gate.intake(elf or self.elf, raw or self.raw, *(expected or self.expected))

    def changed(self, data):
        path = self.out/'changed.elf'
        path.write_bytes(data)
        return path

    def sections(self, data):
        offset = struct.unpack_from('<Q', data, 40)[0]
        count = struct.unpack_from('<H', data, 60)[0]
        return [(offset+i*64, struct.unpack_from('<IIQQQQIIQQ', data, offset+i*64)) for i in range(count)]

    def test_real_four_page_pair_fit_stack_and_no_execution_claim(self):
        report = self.intake()
        self.assertEqual(report['status'], 'pass')
        self.assertEqual(report['code_pages'], 4)
        self.assertEqual(report['raw_bytes'], len(self.raw_bytes))
        self.assertEqual(report['stack']['reachable_functions'], 2)
        self.assertEqual(report['stack']['entry_stack_bytes'], 320)
        self.assertIs(report['executed'], False)
        self.assertIs(report['native_acceptance'], False)
        self.assertIs(report['abi_compatibility_verified'], False)

    def test_identity_size_symlink_and_exact_text_fail_before_disassembly(self):
        other = self.out/'wrong.raw'
        other.write_bytes(self.raw_bytes[:-1] + b'\x12')
        link = self.out/'alias.raw'
        link.symlink_to(self.raw)
        fifo = self.out/'pipe.raw'
        os.mkfifo(fifo)
        with patch.object(gate.subprocess, 'run', side_effect=AssertionError('must not disassemble')):
            for expected in (('0'*64, self.expected[1]), (self.expected[0], '0'*64), ('X'*64, self.expected[1])):
                with self.assertRaises(ValueError):
                    self.intake(expected=expected)
            with self.assertRaisesRegex(ValueError, 'text/raw'):
                self.intake(raw=other, expected=(self.expected[0], gate.digest(other.read_bytes())))
            with self.assertRaisesRegex(ValueError, 'nonsymlink'):
                self.intake(raw=link)
            with self.assertRaisesRegex(ValueError, 'regular'):
                self.intake(raw=fifo)
            for data in (b'', b'x'*16385):
                other.write_bytes(data)
                with self.assertRaisesRegex(ValueError, 'size bound'):
                    self.intake(raw=other)
            with self.assertRaisesRegex(ValueError, 'size bound'):
                self.intake(elf=self.changed(b'x'*1048577))

    def test_malformed_header_program_sections_imports_entry_and_function_extents(self):
        cases = [self.elf_bytes[:63]]
        for offset, fmt, value in ((0, 'I', 0), (4, 'B', 1), (5, 'B', 2), (7, 'B', 3),
                (16, 'H', 3), (18, 'H', 183), (24, 'Q', 0x400001),
                (32, 'Q', len(self.elf_bytes)), (40, 'Q', len(self.elf_bytes)),
                (52, 'H', 0), (54, 'H', 0), (56, 'H', 33), (58, 'H', 0),
                (60, 'H', 0), (62, 'H', 999)):
            raw = bytearray(self.elf_bytes)
            struct.pack_into('<'+fmt, raw, offset, value)
            cases.append(bytes(raw))
        phoff = struct.unpack_from('<Q', self.elf_bytes, 32)[0]
        for kind in (2, 3, 7):
            raw = bytearray(self.elf_bytes)
            struct.pack_into('<I', raw, phoff, kind)
            cases.append(bytes(raw))
        text = next((at, s) for at, s in self.sections(self.elf_bytes) if s[2] & 2 and s[5])
        for offset, fmt, value in ((0, 'I', 0xffffffff), (4, 'I', 8), (8, 'Q', 2),
                                   (16, 'Q', 0x400001), (24, 'Q', len(self.elf_bytes)),
                                   (32, 'Q', 16385)):
            raw = bytearray(self.elf_bytes)
            struct.pack_into('<'+fmt, raw, text[0]+offset, value)
            cases.append(bytes(raw))
        sym = next((at, s) for at, s in self.sections(self.elf_bytes) if s[1] == 2)
        for stype in (4, 6, 9, 11):
            raw = bytearray(self.elf_bytes)
            struct.pack_into('<I', raw, sym[0]+4, stype)
            cases.append(bytes(raw))
        function = next(at for at in range(sym[1][4], sym[1][4]+sym[1][5], 24)
                        if self.elf_bytes[at+4] & 15 == 2)
        for offset, fmt, value in ((6, 'H', 0), (8, 'Q', 0x399999), (16, 'Q', 0), (16, 'Q', 16384)):
            raw = bytearray(self.elf_bytes)
            struct.pack_into('<'+fmt, raw, function+offset, value)
            cases.append(bytes(raw))
        for data in cases:
            with self.subTest(sha=gate.digest(data)):
                with self.assertRaises(ValueError):
                    gate.text_image(data)

    def test_compiling_missing_checks_admit_the_named_bad_input(self):
        source = (ROOT/'scripts/fs_init_intake.py').read_text()
        wrong = self.out/'omission.raw'
        wrong.write_bytes(self.raw_bytes[:-1] + b'x')
        expected = self.expected[0], gate.digest(wrong.read_bytes())
        malformed = bytearray(self.elf_bytes)
        debug = next((at, s) for at, s in self.sections(malformed) if s[1] == 1 and not s[2] & 2 and s[5])
        struct.pack_into('<I', malformed, debug[0]+4, 4)
        # Each compiling omission must actually admit its bad input. These are
        # semantic controls against the positive inspection, not syntax checks.
        for name, old, new in (
            ('text', 'if text_image(elf) != raw:', 'if False:'),
            ('imports', 'if (stype in (4, 9) and size) or stype in (6, 11):', 'if False:'),
            ('stack', 'stack = inspect(result.stdout, Path(elf_path))', 'stack = {}'),
        ):
            self.assertEqual(source.count(old), 1)
            module = types.ModuleType('intake_omission')
            exec(compile(source.replace(old, new, 1), name, 'exec'), module.__dict__)
            if name == 'text':
                with self.assertRaisesRegex(ValueError, 'text/raw'):
                    self.intake(raw=wrong, expected=expected)
                self.assertEqual(module.intake(self.elf, wrong, *expected)['status'], 'pass')
            elif name == 'imports':
                with self.assertRaisesRegex(ValueError, 'relocations/imports'):
                    gate.text_image(malformed)
                self.assertEqual(module.text_image(malformed), self.raw_bytes)
            else:
                elf, raw = self.build(self.source.replace('call worker', 'call *%rax'), 'omitted-stack')
                hashes = gate.digest(elf.read_bytes()), gate.digest(raw.read_bytes())
                with self.assertRaisesRegex(ValueError, 'indirect'):
                    self.intake(elf, raw, hashes)
                self.assertEqual(module.intake(elf, raw, *hashes)['status'], 'pass')

    def test_actual_indirect_recursive_and_excess_stack_code_is_rejected(self):
        for name, source, reason in (
            ('indirect', self.source.replace('call worker', 'call *%rax'), 'indirect'),
            ('recursive', self.source.replace('call worker', 'call _start'), 'recursive'),
            ('deep', self.source.replace('sub $16,%rsp', 'sub $4096,%rsp'), 'exceeds4088'),
            ('enter', self.source.replace('sub $16,%rsp', 'enter $4096,$0'), 'implicit stack'),
            ('leave', self.source.replace('sub $16,%rsp', 'leave'), 'implicit stack'),
            ('exchange', self.source.replace('sub $16,%rsp', 'xchg %rax,%rsp'), 'stack exchange'),
            ('partial', self.source.replace('sub $16,%rsp', 'mov %eax,%esp'), 'partial stack'),
            ('restore', self.source.replace('sub $16,%rsp', 'mov %rbp,%rsp'), 'unknown stack'),
            ('large-add', self.source.replace('sub $16,%rsp', 'add $8192,%rsp'), 'unknown stack'),
            ('conditional', self.source.replace('call worker', 'jne worker').replace('sub $32,%rsp', 'sub $4096,%rsp'), 'exceeds4088'),
        ):
            elf, raw = self.build(source, name)
            with self.assertRaisesRegex(ValueError, reason):
                self.intake(elf, raw, (gate.digest(elf.read_bytes()), gate.digest(raw.read_bytes())))

    def test_immutable_static_linker_flags_and_flag_push_are_accounted(self):
        text = next(at for at, s in self.sections(self.elf_bytes) if s[2] & 2 and s[5])
        for flags in (6, 7, 0x36, 0x37):
            data = bytearray(self.elf_bytes)
            struct.pack_into('<Q', data, text+8, flags)
            self.assertEqual(gate.text_image(data), self.raw_bytes)
        data = bytearray(self.elf_bytes)
        struct.pack_into('<Q', data, text+8, 0x407)
        with self.assertRaises(ValueError):
            gate.text_image(data)
        elf, raw = self.build(self.source.replace('push %rbp', 'pushfq'), 'flag-push')
        report = self.intake(elf, raw, (gate.digest(elf.read_bytes()), gate.digest(raw.read_bytes())))
        self.assertEqual(report['stack']['entry_stack_bytes'], 320)

    def test_changed_input_tool_failure_and_output_limit_never_publish_success(self):
        original = gate.subprocess.run
        temporary = self.out/'changing.elf'
        temporary.write_bytes(self.elf_bytes)

        def drift(argv, **kwargs):
            result = original(argv, **kwargs)
            temporary.write_bytes(self.elf_bytes + b'x')
            return result

        with patch.object(gate.subprocess, 'run', side_effect=drift):
            with self.assertRaisesRegex(ValueError, 'changed during'):
                self.intake(elf=temporary)
        for code, text in ((1, ''), (0, 'x'*4194305)):
            with patch.object(gate.subprocess, 'run', return_value=subprocess.CompletedProcess([], code, text, '')):
                with self.assertRaisesRegex(ValueError, 'disassembler'):
                    self.intake()
        def wrong_clang(data):
            value = hashlib.sha256(data).hexdigest()
            return '0'*64 if value == self.tools['clang']['sha256'] else value
        with patch.object(gate, 'digest', side_effect=wrong_clang):
            with self.assertRaisesRegex(ValueError, 'toolchain identity'):
                self.intake()
        original_digest = gate.digest
        seen = 0
        def changed_tool(data):
            nonlocal seen
            value = original_digest(data)
            if value == self.tools['objdump']['sha256']:
                seen += 1
                if seen > 1:
                    return '0'*64
            return value
        with patch.object(gate, 'digest', side_effect=changed_tool):
            with self.assertRaisesRegex(ValueError, 'input/tool changed'):
                self.intake()

    def test_cli_streams_usage_help_version_and_escaped_failure(self):
        entry = [sys.executable, '-B', str(ROOT/'scripts/fs_init_intake.py')]
        for flag in ('--help', '--version'):
            result = subprocess.run(entry+[flag], capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(result.stdout)
            self.assertFalse(result.stderr)
        result = subprocess.run(entry, capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 64)
        self.assertFalse(result.stdout)
        args = ['--elf', str(self.elf), '--raw', str(self.raw), '--elf-sha256', self.expected[0], '--raw-sha256', self.expected[1]]
        result = subprocess.run(entry+args, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(result.stderr)
        self.assertIs(json.loads(result.stdout)['executed'], False)
        with patch.object(sys, 'argv', ['fs_init_intake.py', *args]), patch.object(gate, 'intake', side_effect=ValueError('bad\n\x1b[31m')):
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                self.assertEqual(gate.main(), 1)
            self.assertFalse(out.getvalue())
            self.assertNotIn('\x1b', err.getvalue())
            self.assertEqual(err.getvalue().count('\n'), 1)


if __name__ == '__main__':
    unittest.main()
