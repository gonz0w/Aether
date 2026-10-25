# Scoped implementation review

Requirement: retain the one-child default and admit two children only under the
explicit pair build option. Domain admission budget remains four. Inspection and
retirement require the parent and exact current capability/child identity.

Reviewed: the owner holds child records, execution frames, FP state, stacks, TLS,
waits and terminal status. No mutable global task authority was added. Creation
validates descriptor/storage and overlap before publication or budget consumption.
The bounded scheduler skips waiting/stopped records. Memory protection checks all
live child storage and all wait addresses. Stop cancels/clears every context before
existing domain reclamation. Default inspection remains slot zero.

Unsafe boundary: raw C children never call libc and use dedicated writable stack
and TLS allocations; FS:0 is fixture data, not a musl TCB. Each child has its own
clear-TID word. XMM0/FS values are observed after actual yields. Descriptor and
thread metadata are stable while children run. Within-domain shared storage is
intentional; thread contexts are not isolation domains. Kernel mutation retains
existing IF=0 owner-local execution and CR3/FP restore rules.

Coverage: first batch proves selective wake while the other child remains parked;
second batch wakes both before awaiting completion. Exact exit status, independent
TLS/SIMD, live/stale retirement, ID stride, admission exhaustion and quota return
are checked. Parent exit and supervisor stop begin with both children parked.
UD2 terminates its owning domain while the peer completes. Pin bypass and disabled
pair controls must fail at the named fixture assertions.

Limitations: self-review only; no independent reader/consumer acceptance. Actual
concurrent musl pthread lifecycle, multiple condition waiters, wake-one/requeue,
preemptive fairness and general POSIX behavior are not qualified by this fixture.
No sibling or release pins changed. Existing native fixtures and larger system
release requirements remain experimental.
