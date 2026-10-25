/* SPDX-License-Identifier: BSD-2-Clause */
/* Statically resolved GOT entries are read-only, like the ABI-6 producer map. */
ENTRY(_start)
SECTIONS {
    . = 0x400000;
    .text : { KEEP(*(.text.entry)) *(.text .text.*) *(.rodata .rodata.*) *(.got .got.*) }
    .data : { *(.data .data.*) }
    .bss : { *(.bss .bss.*) *(COMMON) }
    /DISCARD/ : { *(.eh_frame*) *(.comment*) *(.note*) }
    ASSERT(_start == 0x400000, "entry must be first byte")
    ASSERT(SIZEOF(.text) > 0 && SIZEOF(.text) <= 4096, "code exceeds lifecycle v1 page")
    ASSERT(SIZEOF(.data) == 0 && SIZEOF(.bss) == 0, "writable globals unsupported")
}
