
## Bounded concurrent native children contract — 2026-09-06

Before implementation: opt-in native-thread-pair requires native-threads and
native-memory and remains limited to AENATC01/AENSUP01. Default builds retain one
child record. Pair builds have two owner-local records, one parent, four successful
admissions total and no cross-core migration. Parent-only creation chooses the
first unused record; exited records require retirement before reuse. Failed
admission consumes no ID/budget. IDs keep the existing ordinal stride and exact
domain-grant scope. No ambient authority, shared global table or pool policy.

New pair-only operation 0x2800b: RDI=current thread cap, RSI=exact child ID,
RDX/R10/R8/R9 zero. Parent only; authority/role -13, invalid ID/reserved -22,
no retained children -2, unmatched ID with retained children -9. Success returns
0 for running or status+1 for stopped; RDX is pending-wait boolean. Old 0x28002
continues observing slot zero. Retirement 0x2800a selects exact ID across records;
no children -2, unmatched -9, running/pending/uncleared -16. No budget replenishment.
Outside pair mode 0x2800b returns -38 after authority validation.

Rotate runnable parent/children in bounded local round-robin order, skipping stopped
or waiting children. Wake retains existing wake-all-at-address semantics and counts
all matched contexts; this is not a futex wake-one/requeue extension. Each live
child's stack/TLS/FS/exit word and every pending wait stay protected against unmap
or protect. New declared stack/TLS ranges cannot overlap another live child's
stack/TLS range (-22 before publication). Same-domain data and a shared exit word
remain allowed; threads are not mutually isolated protection domains.

Stop/fault/parent exit must cancel all waits, handle all exit words and stop every
child before existing domain reclaim/zeroing. Reclaim resets every record; a fresh
domain grant resets the admission budget. Test two independent native children,
per-ID observation/rights/stale/live retirement, second-record pins, full slots,
four admissions, reuse, selective wake, FS/SIMD preservation, parent exit, child
fault/peer completion and supervisor stop/replacement. A disabled pair and pin
bypass must hit exact assertions. This first native fixture uses raw child contexts,
not concurrent musl pthread_create or condition broadcast acceptance.

Selected checks: host scheduler/retirement/alignment, all old thread suites, new
pair on both backing profiles, memory/image/M4 and init v1/v2 regressions on frozen
sources plus standards/workflow and pinned format. No sibling, immutable pin or
service policy changes. Retain all attempts and exact artifacts before completion.
