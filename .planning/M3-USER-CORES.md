# M3 second slice: one Rust worker per CPU

After the existing kernel-message probe drains, each CPU prepares its own user
runtime: private lower-half page tables, an RX copy of the pinned fixture, an
RW/NX stack, a saved register frame, runnable state, and timer/progress counters.
The shared x86 context layout/restore mechanism is reused from M2; the M2 test
orchestrator and its mutable capability/lifetime state remain boot-CPU-only.

Each CPU has its own GDT/TSS/IDT, kernel stack, and double-fault stack. Interrupt
entry saves all general registers. CPU identity comes from CPUID and immutable
bootstrap routing metadata, never from a user argument. There is one runnable
user task per participating core in this slice; timer returns resume that local
context, and a fault stops only that local task. No task migration or shared
user address space is introduced.

Map only the local APIC register page at a supervisor-only, uncached, NX virtual
address. Read its physical base from IA32_APIC_BASE and require the pinned q35
xAPIC baseline. Re-enable the BSP's APIC, mask the legacy PIC before starting
multi-core user execution, and use local periodic timers on both CPUs. The
initial count is one million with divide-by-16. This is a tested emulator
interval, not a calibrated wall-clock guarantee or physical-hardware timing API.

Both workers check general-register sentinels and different values in their
private stack pages. The AP worker runs a bounded busy loop and deliberately
reads the supervisor-only APIC page after repeated timer interrupts. The CPU
must report a user protection fault, verifying MMIO is not exposed to the worker. The BSP must have already reported timer-observed user progress before the
AP fault. The BSP worker keeps looping; its counter must advance after the AP reports the fault, over three
additional local timer interrupts. A masked-AP-timer negative image must fail;
BSP timer activity cannot substitute for AP timer activity.

Only explicit bootstrap readiness and terminal result fields are shared. User
workers receive no APIC/transport mappings or ambient kernel operations; the
following IPC slice supplies explicit endpoint handles. The [mapping slice](M3-MAPPINGS.md) replaces inherited boot mappings with explicit
kernel and transport mappings. Kernel data remains visible to trusted peer kernels:
this is user-task isolation, not containment of a compromised kernel instance. The [following IPC slice](M3-IPC.md) adds cross-core grants and user IPC with
authority/backpressure checks. The final mapping slice supplies narrow kernel transport mappings. No memory is reused in this slice.

References: [Intel SDM](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html)
(local APIC, paging, interrupts/TSS) and the pinned Limine protocol's MP and PAT
contracts in [boot dependencies](../boot/DEPENDENCIES.md).
