# Runtime demand observation contract

Measure the unchanged retained OpenZFS 2.4.4 Linux/x86_64 owned-file workload,
using the pinned offline cross-tool image and original static engine archives.
A separate link-time observer wraps pthread_create and kernel_init/kernel_fini;
no engine source, default worker count, native kernel capacity or sibling changes.
Original BSD fixture and upstream licenses stay intact.

Record cumulative successful create calls, detached calls, requested stack and
guard bytes (sum/min/max), and glibc mallinfo2 snapshots around engine lifecycle.
Thread sums are lifetime requests, not simultaneous live mappings or residency.
Allocator fields describe this guest glibc process, including libraries, excluding
stack mappings not counted by malloc; snapshots are not peak or native budgets.
Wrapper locking makes counter snapshots coherent; allocator and counters are not
one atomic system snapshot. No child trampoline, changed exit policy or fake lock.
Only executable link references are intercepted, not internal shared-library calls.
No selected memory/thread limit follows from this exploratory demand baseline.

Before workload runs, an observer self-check creates/joins two threads requesting
128/256 KiB stacks with 4 KiB guards and verifies exact totals. A count-bypass
variant must exit 2 with the precise observer-count diagnostic. It must not execute
the storage workload or create media. Preserve build/run failures and frozen
source/artifact hashes. Use existing owned-file positive and wrong-byte oracles;
new private regular-file media per run, no host devices/network. One warmup plus
10 measured fresh-process runs, two writable import cycles each. Report every
sample; no latency comparison or allocator high-water claim. The observer does
not qualify power loss, native engine execution, namespace or Rust service policy.

Applicable process: Foundations O/I/E and Distribution PF-01–03 (identified
population, repeated observations, baseline before budgets). Existing Experience
machine-output rules: observer records are versioned JSON lines on stdout, errors
on stderr; unchanged owned-file markers remain. R1 persistence/service acceptance
and independent owner reviews remain open. Run host/inventory/pin and scoped C
format checks; no new native ABI requires QEMU kernel regressions in this slice.
