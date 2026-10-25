# M2 implementation: protection first

This is the first M2 slice, not completion of the milestone.

## Executable contract

The trusted bootstrap loads one freestanding Rust test image from a Limine boot
module. Its entry is byte zero at virtual address `0x400000`. The image is at
most one page of immutable code/constant data; writable static data and BSS are
rejected by its linker script. Each fixture gets a private copy and a private
zeroed 4 KiB stack at `0x800000`, with unmapped adjacent pages. This intentionally
small flat-image contract avoids adding an ELF loader before services need one.

Twelve fixed task/address-space slots belong to the boot CPU. Each has private
lower-half page tables. Kernel upper-half entries are inherited with their user
bit cleared. Code is user RX; stack is user RW/NX; all other lower-half addresses
are absent. NX, four-level paging, and write protection are checked. The original boot-fixture pages remain reserved; only the separate
[factory worker bundle](M2-LIFETIME.md) is reused. Switching CR3 disables the previous
user mappings; global user mappings and PCID are not used.

Own GDT, TSS, and IDT precede user entry. Exceptions enter on a kernel stack;
double fault uses a separate IST stack and panics. Unexpected kernel exceptions
panic. The first six ring-3 protection fixtures run sequentially with interrupts
disabled. The next two run with timer preemption as specified below, followed by two
[capability/IPC fixtures](M2-CAPABILITIES.md).

The only software interrupt is `int 0x80`: terminate the calling fixture, with
status in RAX. It grants no authority over any other object. There is no user
logging, memory-management, or device syscall. Future object operations require
capabilities and a separately specified ABI.

## Evidence required

Five Rust fixtures deliberately attempt a supervisor read, code write, stack
execution, port I/O, and null read. The kernel checks CPL, exception vector, page
fault address/error bits where applicable, and the active fixture identity. A
sixth task checks its zeroed private stack, computes a result, and exits. Only
all expected outcomes produce `AETHER PROTECTION PASS`. Unexpected exceptions,
exits, or results panic. A negative fixture build must fail the smoke test.

## Later slices

Task/memory object authority and safe teardown are implemented by the
[lifetime contract](M2-LIFETIME.md). Bounded endpoint capabilities
and IPC are now described by the [capability contract](M2-CAPABILITIES.md). Full M2 additionally requires two communicating tasks,
derivation/revocation, stale-handle rejection, resource exhaustion and teardown
checks from ROADMAP. No M2 completion claim follows from this protection test.

References: [Intel SDM, volume 3](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html)
(chapters on paging, protection, TSS, and exception handling),
[Rust freestanding target](https://doc.rust-lang.org/rustc/platform-support/x86_64-unknown-none.html),
and the [pinned Limine ABI](../boot/DEPENDENCIES.md).

## Timer/scheduler slice

Add two boot-reserved domains after the six protection fixtures. Use the q35
legacy PIC and PIT channel 0 at approximately 100 Hz; only IRQ0 is unmasked.
Limine masks LINT0, so this baseline explicitly disables the xAPIC to deliver
legacy PIC interrupts directly. x2APIC mode is rejected. This is the one-core
emulator baseline, not the future SMP timer design.
Interrupt gates keep kernel execution non-preemptible. Save all 15 general
registers and the hardware return frame; FP/SIMD remains unsupported and disabled
in both language targets. Round-robin selects runnable tasks only, with no
allocation, priorities, blocking IPC, or page reuse. Terminated slots are never
scheduled again. CR3 changes before returning to the selected user context.

The busy fixture performs a long register-checked loop then faults. Its peer
spins independently. Require repeated hardware preemption and increasing loop
counters for both, then continued peer progress after the fault. The kernel test
harness stops the experiment; this is not a user-accessible termination API.
A masked-timer negative image must fail when the busy task faults without
any observed preemption; it must never report success.

FP/SIMD has no saved context yet: CR0.EM/TS are set and CR4.OSFXSR/OSXSAVE
remain clear, so unsupported instructions fault instead of sharing live state.
The busy loops check general-register sentinels and distinct stack values;
the post-fault check requires the survivor counter to increase further.
