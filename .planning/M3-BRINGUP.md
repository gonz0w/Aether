# M3 first slice: two kernel CPUs

M3 remains incomplete after this slice. Run the complete M2 suite first on the
boot CPU, with the second CPU parked by Limine. Then enter a kernel-only probe
on two CPUs, each with its own Core record, stack, GDT, IDT, and progress counter.
Only the owner writes its local state after bootstrap. The earlier M2 globals
remain boot-CPU-only and are not accessed by the AP.

Limine MP response revision 0 and xAPIC mode are required. Validate two distinct
APIC IDs and check actual CPU identity through CPUID. Initialize the AP's state
and extra_argument before publishing its entry with an atomic release store.
Both CPUs switch to owned stacks before executing the probe.

Two fixed single-producer/single-consumer queues form the only data transport.
Each holds four u64 values, with release/acquire cursor publication; each cursor
has exactly one writer. Bootstrap readiness/failure flags are explicit shared
control state. Fill the request queue before releasing the AP and verify that
an extra request fails without overwriting queued data. Then exchange 100 ordered
request/results; the AP computes `request * 3 + 1`. Only the boot CPU prints.
The AP publishes its final result and waits for the [per-core user phase](M3-USER-CORES.md). Bounded polling fails if the AP
never starts, a result is wrong, or either side stalls. A skip-AP negative build
must never reach the success marker.

This is a trusted kernel transport probe, not capability-controlled cross-core
user IPC. No caller-supplied identities or capability-shaped messages are used.
Kernel memory is still shared through boot mappings: local ownership is not
hardware containment between kernel instances. This initial phase does not establish cross-core user authority or narrow
transport mappings. The later user phase establishes private user address
spaces and AP user-fault containment.

The M2 PIC/PIT path remains unchanged and is used only while the AP is parked.
The probe runs with interrupts disabled on both cores. An unexpected exception
signals failure; there is no recovery claim. The [user phase](M3-USER-CORES.md) now supplies per-core runtime state, APIC
timers, and Rust workers. The [IPC slice](M3-IPC.md) supplies static cross-core grants and transport-authority
checks. The [final mapping slice](M3-MAPPINGS.md) supplies dedicated transport mappings.
