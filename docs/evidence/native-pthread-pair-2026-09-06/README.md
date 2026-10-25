# Concurrent musl pthread lifecycle — 2026-09-06

Actual pinned source-rebuilt musl create/exit/join runs with two live native
children. The conformance adapter has per-child startup and join records instead
of one shared callback/handle. Two batches join in reverse then creation order;
TLS/errno/arguments, blocking joins, quota and thread-list restoration are checked.
The kernel and build files match the prior concurrent-native qualification.

## Evidence

`final/results.json` retains frozen sources, exact commands and passing outcomes:
58 target cases (44 full pthread lifecycle and 14 raw concurrent-child cases),
Zig and 97 Python host tests, offline standards/workflow and scoped formatting.
The new positive and supervised cases pass on both memory profiles. Disabled pair
fails at assertion 202; repeated native IDs fail at 203. Those deliberate failures
are required controls, not successful execution of a broken implementation.

`target-attempts.tar.gz` and `target-directories.json` retain/index all initial and
final runs, including the first compile failure from unused single-child globals.
`final/sources.tar.gz`, `before.tar.gz`, `implementation.diff`, `contract.md` and
`review.md` retain the implementation and self-review. `source-verification.json`
checks all 28 lifecycle producers against pinned musl source and the unchanged
preflight/syscall adaptations. SDK receipt, upstream archive and object identities
are retained with the producers and source-review archive.

Reproduce using `scripts/thread_smoke.py --pthread-lifecycle` and the same command
with `--large`, supplying the pinned SDK/tool lock documented in
[NATIVE-C](../../NATIVE-C.md). Exact input paths are in `final/results.json`.
Post-run reference/status changes are retained separately from frozen evidence.

## Boundaries

Two retained slots and four total admissions; parent-only create/join. No
cancellation, detach, pool, arbitrary thread count, multiple condition waiters,
wake-one/requeue or production userland adoption is claimed. The current wake-all
translation is restricted to this lifecycle experiment. Independent review and
consumer acceptance remain open. No sibling, consumer pin or upstream patch changed.
Next is a bounded multiple-waiter contract and actual musl condition experiment.
