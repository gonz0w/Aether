# Concurrent musl fixture contract

Use the existing two-child kernel profile with the pinned source-rebuilt musl
create/exit/join path. Two adapter records own startup callback/argument, native
ID and join handle until successful join/retirement. Parent-only admission;
reject unsupported attributes before libc mutation. Four total admissions and
two retained slots; failures preserve quota, output handle and thread-list state.
Exercise two batches, opposite join orders, distinct TLS/errno/return values,
exact-ID retirement, quota/list restoration and fifth-create rejection. Disabled
pair and repeated-ID controls must fail for the exact named reason. Preserve old
single-child modes and unchanged kernel bytes. No cancellation, detach, condition
multiwaiter, requeue or production userland adoption. The existing wake-all adapter
is sufficient only for this bounded lifecycle experiment, not general futex wake-one.

Affected owner: Aether conformance fixture, AENATC01/AENSUP01, both memory sizes.
No new upstream patch, dependency, sibling or pin change. Raw startup storage stays
live through join; never dereference an unmapped pthread handle after upstream join.
Preselected checks: host/format, full pthread lifecycle on both profiles and raw
pair regressions; frozen sources, retained failures, source patch verification.
Update NATIVE-C, workflow and STATE; independent review remains open.
