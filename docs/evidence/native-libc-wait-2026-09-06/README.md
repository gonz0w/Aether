# Actual musl internal wait/wake — 2026-09-06

The libc/TLS child now blocks through source-rebuilt musl 1.2.6 __wait and is
released through musl's inline __wake. A narrow conformance adapter translates
private futex wait with a null timeout to native 0x28008, and private wake with
count one to 0x28004, using the supplied thread grant. Unsupported requests return
-ENOSYS. Native authority, pointer and comparison errors remain visible.

The [preimplementation contract](../../NATIVE-C.md#actual-musl-internal-wait-integration-contract--2026-09-06)
defines supported operations, ownership, limits, denied claims and test selection.
Wake count one is valid only because the current domain has two contexts: a
calling waker leaves at most one other context blocked. This adapter must not be
silently extended to a larger pool. No kernel ABI or implementation changed.

## Verification

[Final results](final/results.json) bind exact commands, UTC boundaries and
[frozen sources](final/sources.tar.gz). All selected checks pass:

- Eight new cases per memory profile: positive, supervised replacement,
  descriptor/output aliasing, blocked-child stop/replacement, guard fault with
  peer completion, pin bypass at assertion 194, wrong self-pointer at 291 and
  dropped wake at 289.
- Twelve no-deadline, fourteen libc TLS, twelve storage, twelve stack, twelve
  timed-wait and fourteen older thread cases: 92 target cases total.
- 97 Python tests plus Zig kernel and offline standards/workflow checks, and
  pinned C/Zig formatting.

The parent must observe the child registered as blocked before waking it. Actual
adapter wait/wake calls are counted; musl's waiter count must return to zero after
child completion. Existing TLS cookie, errno, FP, pin and exit checks remain.
Adapter preflight rejects shared/timed futexes, unsupported wake counts and signal
operations. Wrong authority, malformed/unmapped pointers and a signed expected
value preserve native -EACCES/-EINVAL/-EFAULT/-EAGAIN outcomes. A deliberately
dropped wake must produce exact assertion 289 terminals rather than watchdog
timeout. Supervisor replacement reinitializes the user-space adapter state.

## Source identity and retention

The builder verifies the supplied libc and source archive pins, extracts pristine
private headers and __wait.c, then replaces only the disposable syscall_arch.h
with the first-party transport header. The rebuilt __wait object links ahead of
the supplied libc archive. Both original and adapted header manifests, source,
COPYRIGHT, build commands and objects are retained in each producer directory.
[Source verification](source-verification.json) checks all twelve final producers:
upstream __wait.c is unchanged and the only header difference is the intended
transport. `libc-receipt.json`, `review-inputs.json` and
`consumer-source-review.tar.gz` retain upstream identity and original bytes/notices.
The replaced header is an experiment-local adaptation, not a mutated release pin.

`wait-disassembly.txt` and `disassembly.json` retain the final wait loop, native
transport and linked-object/tool identity. First-party C keeps strict warnings
and pinned formatting; upstream source formatting is preserved. No signal or
unsupported-operation success stubs were introduced.

The initial eight-case suite passed. Explicit adapter authority/pointer/signed
comparison rejection checks were then added before final qualification. All
fifteen target directories are retained in `target-attempts.tar.gz` and inventoried
in `target-directories.json`; there were no failed attempts in this change.
`before.tar.gz`, `contract.md`, initial logs and final frozen evidence remain.
No input changed during final qualification; hashes were verified again before
archival. SHA256SUMS covers this packet.

## Remaining work

This is actual internal-wait integration, not pthread_create/join, libc thread-list
publication, general mutex support, signals/cancellation, robust or process-shared
futexes, or timed-futex support. Actual thread creation/start/exit adaptation,
main TLS extents, repeated creation and engine resource budgets remain open.
No sibling source, consumer acceptance or immutable pin changed. Kernel bytes
match the preceding qualification; memory/image/M4 suites were not rerun for this
fixture-only change. Independent review, optimized modes, stack high-water and
extended stress remain missing. Top-level timestamps do not cover every internal
libc-builder command. The native filesystem service and assembled shell/package
release remain unfinished.
