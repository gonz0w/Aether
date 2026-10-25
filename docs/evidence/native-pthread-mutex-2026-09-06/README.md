# Actual bounded pthread mutex contention — 2026-09-06

The conformance adapter now links source-rebuilt musl normal mutex lock, trylock,
timedlock fallback and unlock. Four unmodified mutex translation units come from
the pinned musl 1.2.6 archive. The existing private syscall adapter maps untimed
wait/wake to capability-scoped native operations. No kernel or ABI changed.

Each mutex fixture runs four actual 256 KiB pthread lifecycles. The parent locks
before releasing the child, verifies trylock returns EBUSY, and observes the child's
attempt and wait call on the actual mutex word while protected state stays intact.
Unlock permits the child to update that state. Join/reap must recover backing;
mutex lock/waiter fields return to zero and trylock/unlock succeed after each cycle.
The same mutex is reused across all four children. The fixture that skips locking
must fail specifically at assertion 242. Coordination yields count toward the
unchanged 64-parent-yield protocol.

## Qualification

The preimplementation contract is recorded in contract.md and docs/NATIVE-C.md.
Final commands, UTC boundaries and hashes are retained in final/results.json;
final/sources.tar.gz binds frozen sources checked before/after every command and
before archival. All 162 selected target cases pass: fifteen lifecycle cases per
memory profile plus 132 older thread-family cases. Host checks pass 97 Python tests,
Zig tests, offline standards/workflow and pinned C/Zig formatting.

The new cases are mutex contention, supervised replacement and lock bypass. Existing
lifecycle allocation-pressure, attributes, stale IDs, budget, authority, pin and
fault cases remain selected. Both profiles run the same semantic rejection oracle.
Kernel and build hashes match native-pthread-reuse-2026-09-06; its 25 memory, 9 image
and 7 M4 passes are reused by identity, not rerun or counted as fresh cases here.

## Retention and remaining work

Two initial attempts failed the final kernel oracle after both workers completed:
the added coordination yields exceeded the required total. The second edit missed
the counter increment and preserved that failure. The explicit correction passes
all fifteen initial cases; both failed attempts and the final runs are retained.
There are 25 target directories, 22 from final qualification. Source verification
covers 22 final lifecycle producers, their upstream object hashes, original/adapted
manifests and existing exact admission patch. Mutex sources compare unchanged
against the verified upstream archive. Disassembly, before snapshot, implementation
diff and SHA256SUMS are retained.

This qualifies normal process-private untimed mutex contention in the bounded
parent/child adapter. It does not qualify timed/robust/PI/process-shared mutexes,
condition variables, concurrent child pools, cancellation, fairness or all races.
Independent review, companion adoption and optimized/stress/hardware coverage
remain outstanding. No sibling or immutable pin changed. Next: actual condition
wait/signal and its required semantics, then concurrent resources for libzpool.
The native filesystem and assembled serial shell/package release remain unfinished.
