# SPDX-License-Identifier: BSD-2-Clause
"""Concrete offline owner observation; selected ABI31 budget is not native acceptance."""
import hashlib
import importlib.util
from pathlib import Path
import re
import struct


def measure(system, work, rust, tools, run, dependencies, extra_link, guarded_stack=False, extra_cfg=(), file_layout=False):
    source = system / 'sys-init/prototypes/native-filesystem-session/native_owner.rs'
    linker = work / 'owner.ld'
    linker.write_text('''ENTRY(_start)
PHDRS{code PT_LOAD FLAGS(5);}
SECTIONS{ . = 0x400000; .text : { KEEP(*(.text.entry)) *(.text .text.*) *(.rodata .rodata.*) *(.got .got.*) } :code
.data : { *(.data .data.*) } :code .bss : { *(.bss .bss.*) *(COMMON) } :code
/DISCARD/ : { *(.eh_frame*) *(.comment*) *(.note*) } }
''')
    elf = work / 'owner.elf'
    lld = rust.parent.parent / 'lib/rustlib/aarch64-apple-darwin/bin/rust-lld'
    run('owner-link', [rust, '--edition=2024', '-Dwarnings', '--cfg', 'fs_in_place', *extra_cfg,
        *(['--cfg', 'owner_stack'] if guarded_stack else []),
        '--target=x86_64-unknown-none', '-Cpanic=abort', '-Copt-level=z', '-Clto=fat',
        '-Cjump-tables=no',
        '-Ccodegen-units=1', '-Crelocation-model=static', '-Clinker=' + str(lld),
        '-Clink-arg=--no-dynamic-linker', '-Clink-arg=-static', '-Clink-arg=-T' + str(linker),
        '-Clink-arg=--gc-sections', '-Clink-arg=-u_start', *extra_link, *dependencies,
        source, '-o', elf])
    llvm = Path(tools['readelf']['path']).parent
    sizes = run('owner-size', [llvm / 'llvm-size', '-A', elf]).decode()
    sections = {m[0]: int(m[1]) for m in re.findall(r'^(\.\S+)\s+(\d+)\s+\d+', sizes, re.M)}
    if sections.get('.data', 0) or sections.get('.bss', 0):
        raise ValueError('owner writable image statics')
    raw = elf.read_bytes()
    if raw[:6] != b'\x7fELF\x02\x01' or struct.unpack_from('<Q', raw, 24)[0] != 0x400000:
        raise ValueError('owner entry/ELF')
    offset, stride, count = struct.unpack_from('<Q', raw, 32)[0], *struct.unpack_from('<HH', raw, 54)
    if stride != 56 or offset + stride * count > len(raw):
        raise ValueError('owner program bounds')
    loads = []
    for i in range(count):
        kind, flags, at, address, _, length, memory, _ = struct.unpack_from('<IIQQQQQQ', raw, offset + i * stride)
        if kind in (2, 3):
            raise ValueError('dynamic owner')
        if kind == 1:
            if flags != 5 or address != 0x400000 or memory != length or at + length > len(raw):
                raise ValueError('owner executable segment')
            loads.append(length)
    if loads != [sections['.text']]:
        raise ValueError('owner segment/section mismatch')
    code = None
    # Non-LOAD headers may follow; locate the one validated LOAD explicitly.
    for i in range(count):
        header = struct.unpack_from('<IIQQQQQQ', raw, offset + i * stride)
        if header[0] == 1:
            code = raw[header[2]:header[2]+header[5]]
    if code is None or len(code) != sections['.text']:
        raise ValueError('missing owner code')
    (work/'owner.bin').write_bytes(code)
    if run('owner-undefined', [tools['nm']['path'], '--undefined-only', elf]).strip():
        raise ValueError('owner unresolved symbols')
    assembly = run('owner-disassembly', [llvm / 'llvm-objdump', '-d', '--no-show-raw-insn',
        '--x86-asm-syntax=intel', elf]).decode()
    spec = importlib.util.spec_from_file_location('owner_stack', system / 'scripts/owner_stack.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        stack = dict(status='pass', **module.inspect(assembly, elf=elf, stack_bytes=8192 if guarded_stack else 4096))
    except ValueError as error:
        stack = dict(status='blocked', error=str(error), observation=getattr(error, 'observation', None))
    layout = work / 'runtime-layout.rs'
    fields = ['core::mem::size_of::<Owner>() as u64', 'core::mem::align_of::<Owner>() as u64']
    if file_layout:
        fields += ['core::mem::size_of::<owner_dispatch::Event>() as u64',
                   'core::mem::align_of::<owner_dispatch::Event>() as u64',
                   'core::mem::size_of::<fd_dispatch::Exchange>() as u64',
                   'core::mem::align_of::<fd_dispatch::Exchange>() as u64']
    layout.write_text('#![no_std]\ntype Owner=owner_runtime::Runtime<af07_transport::native::Native>;\n'
        '#[used]#[unsafe(no_mangle)]#[unsafe(link_section=".rodata.runtime_layout")]\n'
        'pub static LAYOUT:[u64;' + str(len(fields)) + ']=[' + ','.join(fields) + '];\n')
    run('runtime-layout-build', [rust, '--edition=2024', '-Dwarnings', '--cfg', 'fs_in_place', *extra_cfg,
        '--target=x86_64-unknown-none', '-Cpanic=abort', '--crate-type=lib', '--emit=obj',
        *dependencies, layout, '-o', work / 'runtime-layout.o'])
    text = run('runtime-layout-readelf', [tools['readelf']['path'], '-x', '.rodata.runtime_layout',
        work / 'runtime-layout.o']).decode()
    data = bytes.fromhex(''.join(''.join(re.findall(r'\b[0-9a-fA-F]{8}\b', line.split(maxsplit=1)[1])[:4])
        for line in text.splitlines() if line.lstrip().startswith('0x')))
    if len(data) != len(fields) * 8:
        raise ValueError('runtime layout observation missing')
    observed = struct.unpack('<' + 'Q' * len(fields), data)
    size, alignment = observed[:2]
    budget = None
    if guarded_stack:
        roles = system / 'kernel/arch/x86_64/native_fs_roles.zig'
        match = re.search(r'pub const owner_stack_code_limit = (\d+);', roles.read_text())
        if not match or int(match[1]) != 49152:
            raise ValueError('unreviewed ABI31 code budget')
        budget = int(match[1])
    result = dict(code_bytes=sections['.text'], code_pages=(sections['.text'] + 4095) // 4096,
        elf_sha256=hashlib.sha256(raw).hexdigest(), sections=sections,
        raw_sha256=hashlib.sha256(code).hexdigest(),
        runtime_bytes=size, alignment=alignment, workspace_bytes=4096, mapped_bytes=8192,
        resident_fits=0 < size <= 4096 and alignment <= 4096, stack=stack,
        code_budget=budget, code_fits=budget is not None and sections['.text'] <= budget,
        native_executed=False,
        scope='Concrete entry/boot/FILE/fork/streams/immutable-helper exec/readiness/wait/terminal/shutdown. Build and host doubles only; native acceptance, persistent executable loading and Zsh/R1 remain open.')

    if file_layout:
        result['file_event_layout'] = dict(event_size=observed[2], event_alignment=observed[3],
            exchange_size=observed[4], exchange_alignment=observed[5])
    return result
