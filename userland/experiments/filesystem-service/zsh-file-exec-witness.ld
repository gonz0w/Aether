/* SPDX-License-Identifier: BSD-2-Clause */
/* Complete copied ET_EXEC: one immutable load containing headers/code/TLS. */
ENTRY(_start)
PHDRS {
    headers PT_PHDR PHDRS FLAGS(4);
    code PT_LOAD FILEHDR PHDRS FLAGS(5);
    tls PT_TLS FLAGS(4);
    stack PT_GNU_STACK FLAGS(6);
}
SECTIONS {
    . = 0x200000 + SIZEOF_HEADERS;
    .text : { KEEP(*(.text.entry)) *(.text .text.*) *(.rodata .rodata.*) *(.got .got.*) } :code
    .tdata : { LONG(1) } :code :tls
    .data : { *(.data .data.*) } :code
    .bss : { *(.bss .bss.*) *(COMMON) } :code
    /DISCARD/ : { *(.eh_frame*) *(.comment*) *(.note*) }
    ASSERT(SIZEOF(.data) == 0 && SIZEOF(.bss) == 0, "witness has no writable image statics")
    ASSERT(. <= 0x201000, "complete loaded witness exceeds one page")
}
