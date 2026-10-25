# Native per-context signal-mask state — 2026-09-06

Operation 0x28009 stores an eight-byte mask for the calling native execution
context under its existing thread capability. It supports query, block, unblock
and replacement; signals 9 and 19 cannot be masked. Successful child admission
copies the parent mask. Later changes remain local to the calling context, and
reclaim resets masks. This is a prerequisite state primitive, not signal delivery,
pending signals, handler execution, cancellation or POSIX compatibility.

The Linux-numbered signal-mask operation remains ENOSYS. Actual musl
pthread_create still rejects unsupported setup before modifying its state. No
companion files, standards release pins or existing libc archive were changed.
The [preimplementation contract](../../NATIVE-C.md#native-per-context-signal-mask-state-contract--2026-09-06)
defines authority, exact arguments, errors, pointer ownership and acceptance.

## Verification

[Final results](final/results.json) preserve commands and UTC boundaries. Sources
are frozen in final/sources.tar.gz and checked before/after every command and again
before archival. All 173 selected target cases pass:

- Eight mask cases per memory profile: positive, supervised replacement, parent
  exit, stop-live replacement, child fault, pin-bypass rejection, disabled-thread
  rejection and deliberately omitted inheritance (exact assertion 220).
- 116 existing thread-family cases, including actual pthread preflight, libc
  locks/waits/TLS, stack/storage and timed/no-deadline waits.
- 25 memory, nine native-image and seven M4 regression cases.

Host verification passes 97 Python tests, Zig tests and offline standards/workflow
checks; pinned C and Zig formatting pass. New Zig checks cover all permitted mask
bits, transitions, unsupported operations, context independence and reset.

The mask fixture checks fresh zero state, inheritance, per-context/per-domain
isolation across yields, mutations and queries, unmaskable bits, exact and partial
pointer aliasing, successful unaligned cross-page output, stale/missing/wrong
grants, reserved arguments, overflow pointers, read-only output, and inaccessible
second-page input/output. Rejected output leaves the accessible prefix and mask
unchanged. Supervisor stop and synchronous faults remain effective while masks
are nonzero. A timeout is not an acceptable inheritance rejection.

## Retention and limitations

The initial eight-case suite and host run pass. A successful cross-page output
check was added before the final frozen run. There were no failed attempts in
this change. All 25 target directories are inventoried in target-directories.json
and retained in target-attempts.tar.gz. before.tar.gz, implementation.diff and the
preimplementation contract are retained. SHA256SUMS covers this packet.

The [scoped self-review](review.md) covers ownership, copy/commit ordering, common
admission and reset. Nonzero-mask inheritance is target-tested through the legacy
create form; descriptor forms share the same assignment but their older target
checks use zero masks. This does not qualify asynchronous delivery or all signal
races. No independent review, companion acceptance, optimized target/stress or
physical-hardware coverage is inferred.

Next work is a bounded native clone/start/exit/join adapter using real mask state,
with signal sending and cancellation explicitly unsupported. The reviewed default
joinable-thread path manipulates masks but does not itself require handler delivery.
Its memory, clear-TID/thread-list and child-exit translations still need executable
qualification before relaxing the current preflight. Repeated
creation and engine resource budgets remain open. The persistent filesystem and
assembled serial shell/package release remain unfinished.
