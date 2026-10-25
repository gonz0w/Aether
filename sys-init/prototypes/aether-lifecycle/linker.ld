ENTRY(_start)
SECTIONS {
    . = 0x400000;
    .text : { KEEP(*(.text.entry)) *(.text .text.*) *(.rodata .rodata.*) }
    .data : { *(.data .data.*) *(.got .got.*) }
    .bss : { *(.bss .bss.*) *(COMMON) }
    /DISCARD/ : { *(.eh_frame*) *(.comment*) *(.note*) }
    ASSERT(_start == 0x400000, "entry must be first byte")
    ASSERT(SIZEOF(.text) > 0 && SIZEOF(.text) <= 4096, "code exceeds lifecycle v1 page")
    ASSERT(SIZEOF(.data) == 0 && SIZEOF(.bss) == 0, "writable globals unsupported")
}
