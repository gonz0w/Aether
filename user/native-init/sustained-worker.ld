/* SPDX-License-Identifier: BSD-2-Clause */
/* Match the existing native ELF contract: mapped PHDR, TLS template and NX stack.
   The one-byte read-only TLS template is unused by this scalar-only worker. */
ENTRY(_start)
PHDRS {
    headers PT_PHDR PHDRS FLAGS(4);
    readonly PT_LOAD FILEHDR PHDRS FLAGS(4);
    code PT_LOAD FLAGS(5);
    tls PT_TLS FLAGS(4);
    stack PT_GNU_STACK FLAGS(6);
}
SECTIONS {
    . = 0x200000 + SIZEOF_HEADERS;
    .rodata : { *(.rodata .rodata.*) *(.got .got.*) } :readonly
    .tdata : { BYTE(0) } :readonly :tls
    . = ALIGN(4096);
    .text : { KEEP(*(.text.entry)) *(.text .text.*) } :code
    .data : { *(.data .data.*) }
    .bss : { *(.bss .bss.*) *(COMMON) }
    /DISCARD/ : { *(.eh_frame*) *(.comment*) *(.note*) }
    ASSERT(SIZEOF(.text) > 0 && SIZEOF(.text) <= 4096, "worker exceeds code page")
    ASSERT(SIZEOF(.data) == 0 && SIZEOF(.bss) == 0, "worker has writable statics")
}
