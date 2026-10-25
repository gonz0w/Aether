# Native taskq integration requirement

Bind the seven NATIVE-TASKQ hooks to existing scoped native memory/thread grants
and actual musl detached create/exit, wait/requeue, keys and rwlocks. No kernel
ABI, capacity, sibling or pin changes. Keep the adapter shared with its existing
lifecycle fixtures, excluding their unrelated test bodies from this mode.

The parent owns the arena, worker creation and saved-ID stop/unmap/retire. Two
queues run one worker each; A waits for B while the parent drains A including its
queued tail. B is gated on the exact parent's A-condition wait. Repeat twice,
within four admissions, and prove quota restoration and TSD ownership.

Select full paired lifecycle regression in both memory profiles, supervisor
replacement and exact premature-drain, false-delay, invalid-free, allocation and
early-reap controls. A watchdog or unexpected terminal is a failed attempt, never
an accepted negative. Freeze sources and retain attempts. Update native contract,
workflow and STATE with measured coverage; missing target/consumer acceptance
stays explicit. Pointer lifetimes end only after exact stop; fatal failure ends
the whole fixture domain, avoiding a stranded lock/worker. Production filesystem
policy remains with Rust userland. Source adaptation retains upstream notices.
