#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Inspect a 16 KiB filesystem/init owner ELF/raw pair without executing it."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import struct
import subprocess
import sys

from deps import ROOT
from owner_stack import inspect


def digest(data):
    return hashlib.sha256(data).hexdigest()


def bounded_read(path, limit):
    path = Path(path)
    if path.is_symlink():
        raise ValueError('owner input must be a regular nonsymlink file')
    # Do not block on a FIFO or follow a leaf swapped to a symlink between
    # inspection and open. Only the opened descriptor's type is authoritative.
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError('owner input must be a regular nonsymlink file')
        data = stream.read(limit + 1)
    if not data or len(data) > limit:
        raise ValueError('owner input size bound')
    return data


def text_image(elf):
    """Check the raw-owner link contract, not the native process ELF contract.

    The kernel maps raw bytes RX itself. A statically resolved GOT may give
    .text ELF write flags; no separate nonempty allocated section is allowed.
    Producer review must still exclude self-modification/hidden mutable data.
    """
    if len(elf) < 64 or elf[:7] != b'\x7fELF\x02\x01\x01' or elf[7:16] != bytes(9):
        raise ValueError('owner ELF64 little-endian identity')
    kind, machine, version, entry, phoff, shoff, flags, ehsize, phsize, phnum, shsize, shnum, names = struct.unpack_from('<HHIQQQIHHHHHH', elf, 16)
    if (kind != 2 or machine != 62 or version != 1 or entry != 0x400000
            or flags or ehsize != 64 or phsize != 56 or shsize != 64
            or not 0 < phnum <= 32 or not 0 < shnum <= 256 or not 0 < names < shnum
            or phoff < 64 or phoff + phnum * phsize > len(elf)
            or shoff < 64 or shoff + shnum * shsize > len(elf)):
        raise ValueError('owner ELF header/layout')
    for at in range(phoff, phoff + phnum * phsize, phsize):
        ptype, _, offset, _, _, size, _, _ = struct.unpack_from('<IIQQQQQQ', elf, at)
        if ptype not in (0, 1, 6, 0x6474e551, 0x6474e552) or offset + size > len(elf):
            raise ValueError('owner unsupported program segment')
    sections = [struct.unpack_from('<IIQQQQIIQQ', elf, shoff + i * shsize) for i in range(shnum)]

    def contents(section):
        offset, size = section[4:6]
        if section[1] == 8 or offset + size > len(elf):
            raise ValueError('owner section bytes')
        return elf[offset:offset + size]

    def string(table, offset):
        if offset >= len(table) or table.find(b'\0', offset) < 0:
            raise ValueError('owner string table')
        return table[offset:table.index(b'\0', offset)]

    if sections[names][1] != 3:
        raise ValueError('owner section-name table')
    table = contents(sections[names])
    text = None
    text_index = None
    start = False
    start_section = None
    functions = []
    symbols = 0
    for index, section in enumerate(sections):
        name, stype, sflags, address, _, size, link, _, _, stride = section
        name = string(table, name)
        if stype != 8:
            contents(section)
        if (stype in (4, 9) and size) or stype in (6, 11):
            raise ValueError('owner runtime relocations/imports')
        if sflags & 2 and size:
            # LLD unions input flags: immutable GOT and merged Rust string
            # constants can leave WRITE/MERGE/STRINGS on this raw code section.
            # They do not change the kernel's separately enforced RX mapping.
            if (name != b'.text' or stype != 1 or sflags & 6 != 6 or sflags & ~0x37
                    or address != 0x400000 or not 0 < size <= 16384 or text is not None):
                raise ValueError('owner immutable text/layout bound')
            text = contents(section)
            text_index = index
        if stype != 2:
            continue
        symbols += 1
        if symbols != 1 or stride != 24 or size % 24 or link >= shnum or sections[link][1] != 3:
            raise ValueError('owner symbol table')
        strings = contents(sections[link])
        data = contents(section)
        for at in range(0, size, stride):
            name, info, _, defined, value, length = struct.unpack_from('<IBBHQQ', data, at)
            name = string(strings, name)
            if name and defined == 0:
                raise ValueError('owner undefined symbol')
            if info & 15 == 2:
                functions.append((defined, value, length))
            if name == b'_start':
                if (start or info & 15 != 2 or defined >= shnum
                        or sections[defined][0] >= len(table)
                        or string(table, sections[defined][0]) != b'.text'
                        or value != entry or not length or length > sections[defined][5]):
                    raise ValueError('owner entry symbol')
                start = True
                start_section = defined
    if text is None or not start or symbols != 1 or start_section != text_index:
        raise ValueError('owner missing text/entry/symbols')
    extents = set()
    for defined, value, length in functions:
        if defined != text_index or not length or not 0x400000 <= value < value + length <= 0x400000 + len(text):
            raise ValueError('owner function bounds')
        extents.add((value, value + length))
    ordered = sorted(extents)
    if any(a[1] > b[0] for a, b in zip(ordered, ordered[1:])):
        raise ValueError('owner overlapping function extents')
    return text


def intake(elf_path, raw_path, expected_elf, expected_raw):
    if any(not isinstance(value, str) or re.fullmatch('[0-9a-f]{64}', value) is None
           for value in (expected_elf, expected_raw)):
        raise ValueError('owner expected SHA256 identity')
    elf = bounded_read(elf_path, 1048576)
    raw = bounded_read(raw_path, 16384)
    if digest(elf) != expected_elf or digest(raw) != expected_raw:
        raise ValueError('owner expected file identity mismatch')
    if text_image(elf) != raw:
        raise ValueError('owner ELF text/raw identity mismatch')
    lock_path = ROOT/'.deps/native-current/sdk/tools.lock.json'
    lock = lock_path.read_bytes()
    tools = json.loads(lock)['tools']
    clang = tools['clang']
    if digest(Path(clang['path']).read_bytes()) != clang['sha256']:
        raise ValueError('owner LLVM toolchain identity')
    tool = Path(tools['objdump']['path']).resolve()
    tool_hash = digest(tool.read_bytes())
    if tool_hash != tools['objdump']['sha256']:
        raise ValueError('owner disassembler identity')
    argv = [str(tool), '-d', '--no-show-raw-insn', '--x86-asm-syntax=intel', str(Path(elf_path).resolve())]
    result = subprocess.run(argv, capture_output=True, text=True, timeout=30)
    if result.returncode or len(result.stdout) > 4194304:
        raise ValueError('owner disassembler failed/output bound')
    # Both the external disassembler and the existing inspector read this file.
    # Check inputs between those reads and again before publishing the result.
    if bounded_read(elf_path, 1048576) != elf or bounded_read(raw_path, 16384) != raw:
        raise ValueError('owner input changed during inspection')
    stack = inspect(result.stdout, Path(elf_path))
    if (bounded_read(elf_path, 1048576) != elf or bounded_read(raw_path, 16384) != raw
            or lock_path.read_bytes() != lock or digest(tool.read_bytes()) != tool_hash
            or digest(Path(clang['path']).read_bytes()) != clang['sha256']):
        raise ValueError('owner input/tool changed during inspection')
    return dict(schema='aether-fs-init-intake-v1', status='pass', executed=False,
                native_acceptance=False, abi_compatibility_verified=False,
                elf_sha256=expected_elf, raw_sha256=expected_raw, raw_bytes=len(raw),
                code_limit_bytes=16384, code_pages=(len(raw)+4095)//4096,
                stack=stack, tool=dict(path=str(tool), sha256=tool_hash),
                tool_lock_sha256=digest(lock), command=argv,
                disassembly_sha256=digest(result.stdout.encode()),
                scope='Host structural identity/fit and scoped stack only; sys-init ABI29, authority, lifecycle and native acceptance remain required')


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(64, '[FAIL] '+ascii(message)+'\n')


def main():
    parser = Parser(description=__doc__, epilog='Example: python3 scripts/fs_init_intake.py --elf owner.elf --raw owner.raw --elf-sha256 ELF_HASH --raw-sha256 RAW_HASH. Read-only; no guest, ABI/lifecycle qualification or launch authorization. See docs/NATIVE-C.md.')
    parser.add_argument('--version', action='version', version='aether-fs-init-intake 1')
    parser.add_argument('--elf', required=True, type=Path, help='matched symbol-bearing ELF (at most 1 MiB)')
    parser.add_argument('--raw', required=True, type=Path, help='raw owner image (1..16384 bytes)')
    parser.add_argument('--elf-sha256', required=True, help='expected producer ELF digest')
    parser.add_argument('--raw-sha256', required=True, help='expected producer raw digest')
    args = parser.parse_args()
    try:
        print(json.dumps(intake(args.elf, args.raw, args.elf_sha256, args.raw_sha256), indent=2))
    except (OSError, ValueError, KeyError, struct.error, subprocess.SubprocessError) as error:
        print('[FAIL] '+ascii(str(error)), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
