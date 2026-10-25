OUTPUT_FORMAT(elf64-x86-64)
ENTRY(_start)
PHDRS {
    requests PT_LOAD FLAGS(6);
    text PT_LOAD FLAGS(5);
    rodata PT_LOAD FLAGS(4);
    data PT_LOAD FLAGS(6);
}
SECTIONS {
    . = 0xffffffff80000000;
    kernel_start = .;
    .limine_requests : {
        KEEP(*(.limine_requests_start))
        KEEP(*(.limine_requests))
        KEEP(*(.limine_requests_end))
    } :requests
    . = ALIGN(4096);
    text_start = .;
    .text : { *(.text .text.*) } :text
    . = ALIGN(4096);
    text_end = .;
    . = ALIGN(4096);
    rodata_start = .;
    .rodata : { *(.rodata .rodata.*) } :rodata
    . = ALIGN(4096);
    rodata_end = .;
    . = ALIGN(4096);
    .data : { *(.data .data.*) } :data
    .bss : { *(.bss .bss.*) *(COMMON) } :data
    . = ALIGN(4096);
    transport_start = .;
    .transport : { *(.transport) } :data
    . = ALIGN(4096);
    transport_end = .;
    kernel_end = .;
    /DISCARD/ : { *(.eh_frame*) *(.note*) }
}
