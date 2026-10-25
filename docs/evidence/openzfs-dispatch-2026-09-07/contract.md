# Fixed-queue dispatch observation

Before code: add a Linux-only observer for external taskq dispatch/delay/entry,
wait/wait-id/wait-outstanding and cancellation calls targeting the exact fixed
system/delay queue instances. Register identities after real system_taskq_init,
retain them through real system_taskq_fini, then retire them. No engine source,
queue count, callback, scheduling, native quota, sibling or pin changes.

Keep counters under a private pthread mutex; never hold it across an engine call
or callback. Copy only opaque identities under lock, never dereference a retired
queue. Two fixed identities suffice because the unchanged lifecycle creates one
system pair at a time. Record calls/accepted/rejected and pending differences at
lifecycle snapshots. An accepted dispatch is not callback completion. Link-wrap
counts cover external references only, not same-object/internal calls; explicitly
exclude taskq_destroy's internal drain. No callback trampoline or allocation.

A synthetic check initializes the real system queues, dispatches normal and
preallocated work to each, drains through actual wait APIs, verifies four callback
completions, rejected delayed dispatch/no delayed callback and ENOENT cancellation.
Dropped dispatch counts and fabricated delayed success must fail at exact exit2
oracles. Retain all old worker/role/CPU/storage controls and warmup plus10 processes
per CPU view. Review unchanged caller/dependency source before proposing pool
reductions; counts alone cannot establish safe concurrency or native capacity.

Use the existing pinned offline Linux image, read-only engine and frozen /inputs,
owned /out/media, no network/capabilities,2GiB/512pids and existing90/120s bounds.
Check complete original engine/static-library identity before/after. Apply scoped
C21.1.8 formatting and Foundations O/I/E, DEVELOPMENT and unchanged Experience
machine-output exception. Existing JSON records stay unchanged; add a separate
observer record. Run host/Zig/pins/workflow; host-only change needs no new QEMU
kernel qualification. Retain all attempts before edits, then update feasibility,
workflow and STATE. No production filesystem acceptance is implied.
