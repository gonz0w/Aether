/* SPDX-License-Identifier: BSD-2-Clause */
ENTRY(_start)
SECTIONS {
    . = 0x400000;
    .text : { KEEP(*(.text.entry)) *(.text .text.*) *(.rodata .rodata.*) *(.got .got.*) }
    .data : { *(.data .data.*) }
    .bss : { *(.bss .bss.*) *(COMMON) }
    /DISCARD/ : { *(.eh_frame*) *(.comment*) *(.note*) }
    ASSERT(_start == 0x400000, "entry must be image byte zero")
    ASSERT(SIZEOF(.text) > 0 && SIZEOF(.text) <= 16384, "filesystem init owner exceeds four code pages")
    ASSERT(SIZEOF(.data) == 0 && SIZEOF(.bss) == 0, "owner must have no writable statics")
}
