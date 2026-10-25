# Native child lifetime record — 2026-09-06

One owner-local Child record now contains execution, identity, used/running state,
terminal status and stack bounds. Domain mappings, capability and lifetime
admission budget remain outside it. This prepares bounded concurrent slots; it
does not enable a second child, change scheduling order or allocate a new ABI.

Retirement still requires native authority, parent role and valid arguments before
record access. It rejects absent, stale and live/pending records in the existing
order, then clears the complete record on success. Save/restore, tick/wake, pinning,
exit and reclaim use its embedded Execution. Reclaim clears child metadata after
stop, clear-TID and mapping cleanup, while preserving retained domain observations.

## Qualification

The preimplementation contract is retained in contract.md and docs/NATIVE-C.md.
New Zig checks preserve all fields on rejected retirement, clear complete CPU/TLS/
wait/mask/identity/stack state on success, leave a neighboring record intact and
verify array FP alignment. Final results bind exact commands, UTC boundaries and
frozen source hashes in final/sources.tar.gz, checked before/after each command
and archival.

All 209 selected target cases pass: 168 thread, 25 memory, 9 image and 7 M4 cases.
Host checks pass 97 Python tests, Zig tests, offline standards/workflow and pinned
formatting. This is a fresh broader kernel qualification, not reuse of earlier
memory/image/M4 results. Existing same-ID, stale retirement, exhaustion, live-pin,
fault, mutex and condition tests preserve their semantic rejection oracles.

## Retention and limits

Initial host checks and final qualification pass with no failed attempts. All
26 target directories are retained in target-attempts.tar.gz. Source verification
covers 26 final lifecycle producers against the unchanged pinned musl archive;
original/adapted manifests, exact existing admission patch, upstream object hashes
and disassembly remain available. before.tar.gz, implementation.diff and SHA256SUMS
bind the change and evidence.

The system still permits one live child and four sequential admissions per domain.
Next: implement bounded concurrent slots, per-child observation and selection, and
prove stop/reclaim covers every child before adding multiple condition waiters.
No sibling or immutable pin changed. Independent review, companion adoption,
optimized/stress/hardware coverage, libzpool integration, native filesystem and
assembled serial shell/package release remain outstanding.
