# ARC serial progress trial

Before implementation, 2026-09-07. Resume the selected R1-03 private host trial.
Retain the qualified 1/1 system/delay profile. Compare upstream ARC initializer
0 with 1; preserve all other queues, notices, original source/archive identities,
release pins and native budgets. This is Linux libzpool evidence only.

Instrument the return value of arc_evict_state for resident MRU/MFU/uncached
states using a thread-local counter in a private arc.c copy. The explicit trial
calls arc_flush(NULL, B_FALSE); its delta must be positive. Ghost transitions and
other threads' background activity cannot satisfy this oracle. Count returned
resident eviction bytes, not RSS or physically freed allocations. Force-no-call
control must fail the exact progress assertion, not time out. Run after first
write and each verified read; preserve export/reimport/data integrity workload.
Use bounded nonretry flush; do not risk an unbounded retry with live producers.

Compare auto and serial in modeled one-CPU and normal host CPU views using
existing observer/dispatch accounting. This first trial qualifies the eviction
oracle and selects the next measured matrix; it does not replace full repeated
qualification, pressure/soak, default-profile regression or native acceptance.

Private outputs only, new owned regular-file vdevs, pinned offline container,
no network, device, imported pool or sibling writes. Preserve every attempt and
freeze source hashes during runs. Existing observer code and libc call signatures
are retained. New externally linked observation functions are experiment-only;
no production API or cross-project standard is allocated. Foundations I/E and
DEVELOPMENT evidence/unsafe/resource rules apply. Upstream modified sources retain
CDDL terms; first-party fixture work retains BSD-2-Clause. No dependency is added.

The initial six executions passed. Before the repeated matrix: use one warmup
and ten measured processes for each auto/serial and one-CPU/host view (44 total).
Retain existing live/role/fixed-pool validators, pair accounting and zero final
registered workers. Require ARC creates 9/cycle for auto and 1/cycle for serial.
Real auto output must fail the serial-count oracle. This qualifies the scoped
serial trial, not native support or exhaustive observer-fault regression.
