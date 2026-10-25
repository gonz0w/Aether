/* SPDX-License-Identifier: BSD-2-Clause */
ENTRY(_start)
SECTIONS {
    . = 0x400000;
    .text : { KEEP(*(.text.entry)) *(.text .text.*) *(.rodata .rodata.*) }
    .data : { *(.data .data.*) *(.got .got.*) }
    .bss : { *(.bss .bss.*) *(COMMON) }
    /DISCARD/ : { *(.eh_frame*) *(.comment*) *(.note*) }
    ASSERT(_start == 0x400000, "entry must be image byte zero")
    ASSERT(SIZEOF(.text) > 0 && SIZEOF(.text) <= 8192, "activation fixture exceeds two code pages")
    ASSERT(SIZEOF(.data) == 0 && SIZEOF(.bss) == 0, "fixture must have no writable statics")
}
