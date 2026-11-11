#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Build the seed or note sys-init Owner from tracked Rust source."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys

from bounded_tools import run_tool

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from owner_stack import inspect
INPUTS = {
    'terminfo': (1268, '512924dc4f0c9d70e6628d63615884aa93fad7d7fc7a9f62ba3536db24702dc1'),
    'probe': (3548, '15d1a20d584543555420effcdb28fac2ca1f188dc2e1a88684e86f177a017de3'),
}
CODE_LIMITS = {'seed': 81920, 'note': 90112}
LINKER = """ENTRY(_start)
PHDRS { code PT_LOAD FLAGS(5); }
SECTIONS {
  . = 0x400000;
  .text : { KEEP(*(.text.entry)) *(.text .text.*) *(.rodata .rodata.*) *(.got .got.*) } :code
  .data : { *(.data .data.*) } :code
  .bss : { *(.bss .bss.*) *(COMMON) } :code
  /DISCARD/ : { *(.eh_frame*) *(.comment*) *(.note*) }
}
"""


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_inputs(args):
    result = {}
    for name, (length, checksum) in INPUTS.items():
        path = getattr(args, name).resolve(strict=True)
        with path.open('rb') as stream:
            raw = stream.read(length + 1)
        if len(raw) != length or digest(raw) != checksum:
            raise ValueError(f'{name} does not match the qualified source payload')
        result[name] = path
    return result


def extract_rx(raw, limit):
    if raw[:7] != b'\x7fELF\x02\x01\x01' or len(raw) < 120:
        raise ValueError('expected ELF64 little-endian Owner')
    kind, machine, _, entry, phoff = struct.unpack_from('<HHIQQ', raw, 16)
    phentsize, phnum = struct.unpack_from('<HH', raw, 54)
    if (kind, machine, entry, phentsize, phnum) != (2, 62, 0x400000, 56, 1) or phoff + 56 > len(raw):
        raise ValueError('invalid Owner ELF or entry')
    kind, flags, offset, address, physical, size, memory, align = struct.unpack_from('<IIQQQQQQ', raw, phoff)
    if ((kind, flags, address, physical, align) != (1, 5, entry, entry, 4096)
            or size != memory or not 0 < size <= limit or offset % align or offset + size > len(raw)):
        raise ValueError('Owner RX mapping exceeds the selected role geometry')
    return raw[offset:offset + size]


def build(args):
    inputs = load_inputs(args)
    rustc, linker = (tool.resolve(strict=True) for tool in (args.rustc, args.linker))
    work = args.work.resolve()
    work.mkdir(mode=0o700)
    (work / 'tmp').mkdir()
    (work / 'owner.ld').write_text(LINKER)
    for name, path in inputs.items():
        (work / name).write_bytes(path.read_bytes())
    environment = {
        'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'TMPDIR': str(work / 'tmp'),
        'AETHER_ZSH_TERMINFO': str(work / 'terminfo'),
        'AETHER_ZSH_FILE_EXEC_ELF': str(work / 'probe'),
    }
    profiles = json.loads((HERE / 'r1-zsh-owner-profiles.json').read_text())
    shared = {row[0]: row for row in profiles['shared']}
    libraries = {}
    for row in profiles['roles'][args.role]:
        name, source, edition, cfg, dependencies = shared[row] if isinstance(row, str) else row
        output = work / (f'lib{name}.rlib' if name else 'owner.elf')
        argv = [str(rustc), '--edition=' + edition, '-Dwarnings', '-Dunsafe_op_in_unsafe_fn',
                '--target=x86_64-unknown-none', '-Cpanic=abort', '-Crelocation-model=static',
                '-Ccodegen-units=1', '-Cjump-tables=no', '-Ldependency=' + str(work),
                f'--remap-path-prefix={work}=/build/aether/owner',
                f'--remap-path-prefix={ROOT}=/src/aether']
        for option in cfg:
            argv.extend(('--cfg', option))
        for dep in dependencies:
            argv.extend(('--extern', f'{dep}={libraries[dep]}'))
        if name:
            argv.extend(('-Copt-level=2', '--crate-name=' + name, '--crate-type=rlib'))
            libraries[name] = output
        else:
            argv.extend(('-Copt-level=z', '-Clto=fat', '-Clinker=' + str(linker),
                         '-Clink-arg=--no-dynamic-linker', '-Clink-arg=-static',
                         '-Clink-arg=-T' + str(work / 'owner.ld'), '-Clink-arg=--gc-sections',
                         '-Clink-arg=-u_start'))
        argv.extend((str(ROOT / source), '-o', str(output)))
        run_tool(argv, environment, work / f'{name or "owner"}.log', timeout=30, cwd=work)
    elf = work / 'owner.elf'
    image = extract_rx(elf.read_bytes(), CODE_LIMITS[args.role])
    disassembly = run_tool([str(args.objdump.resolve(strict=True)), '-d', '--no-show-raw-insn',
                            '--x86-asm-syntax=intel', str(elf)], environment,
                           work / 'stack.log', timeout=30, cwd=work)
    stack = inspect(disassembly.decode('ascii'), elf=elf, stack_bytes=12288)
    layout = work / 'runtime-layout.rs'
    layout.write_text('''#![no_std]
type Runtime = native_app_runtime::Runtime<af07_transport::native::Native>;
#[used]
#[unsafe(no_mangle)]
#[unsafe(link_section = ".rodata.runtime_layout")]
pub static LAYOUT: [u64; 2] =
    [core::mem::size_of::<Runtime>() as u64, core::mem::align_of::<Runtime>() as u64];
''')
    layout_object, layout_bytes = work / 'layout.o', work / 'layout.bin'
    run_tool([str(rustc), '--edition=2024', '--target=x86_64-unknown-none',
              '--crate-type=lib', '--emit=obj', '-Cpanic=abort', '-Ldependency=' + str(work),
              '--extern', f'native_app_runtime={libraries["native_app_runtime"]}',
              '--extern', f'af07_transport={libraries["af07_transport"]}',
              str(layout), '-o', str(layout_object)], environment,
             work / 'layout.log', timeout=30, cwd=work)
    run_tool([str(args.objcopy.resolve(strict=True)),
              '--dump-section=.rodata.runtime_layout=' + str(layout_bytes),
              str(layout_object)], environment, work / 'layout-copy.log', timeout=30, cwd=work)
    runtime, alignment = struct.unpack('<QQ', layout_bytes.read_bytes())
    if not 0 < runtime <= 4096 or alignment != 8:
        raise ValueError('Owner Runtime layout exceeds its workspace')
    (work / 'owner.bin').write_bytes(image)
    result = dict(role=args.role, owner_bytes=len(image), owner_sha256=digest(image),
                  runtime_bytes=runtime, runtime_alignment=alignment,
                  stack_bytes=stack['entry_stack_bytes'])
    (work / 'owner.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('role', choices=CODE_LIMITS)
    for name in ('work', 'rustc', 'linker', 'terminfo', 'probe', 'objcopy', 'objdump'):
        parser.add_argument('--' + name, required=True, type=Path)
    try:
        build(parser.parse_args())
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        parser.exit(1, f'Owner build failed: {error}\n')


if __name__ == '__main__':
    main()
