# Native execution-state separation — 2026-09-06

The native runtime now keeps its saved interrupt frame, aligned floating-point
state, FS base and clear-TID pointer in a separate execution object. Mappings,
backing, grants and domain lifecycle remain domain-owned. There is still one
execution context per domain; no thread-creation or wait ABI is introduced.
Explicit supervised worker reclaim resets the whole execution object after TID
and mapping cleanup. A zero context must be initialized before running again.

The kernel-owned native musl producer checks distinct XMM0 values and TLS across
64 yields. Deliberately omitting FP restoration must produce status 174, with
matching terminal records and task summaries. Either scheduling order is valid.

## Final results

All commands in [final/results.json](final/results.json) passed against the
[frozen sources](final/sources.tar.gz):

- Host build/tests: 94 Python cases plus kernel tests, including two new execution
  layout/reset cases, and offline standards/workflow checks.
- Zig formatting for the changed Zig files.
- Default native memory: 12 cases; large native memory: 13 cases.
- Large static executable admission/replacement: nine cases.
- Two-core regression: seven cases, including framebuffer and six negative controls.

Exact arguments, UTC command boundaries and source hashes are in the results.
Native producers use the existing strict musl build at
`/Users/cam/DEV/Aether-userland/build/native-c-5olokhku` and its tools lock,
recorded by the target builders. No companion source or consumer pin changed.
Commands remain the existing memory, image and regression entry points documented
in [NATIVE-C](../../NATIVE-C.md). The local wrapper records the selected sequence.

## Retained attempts

`before.tar.gz`, `contract.md` and `attempt-1-sources.tar.gz` retain the initial
state and contract. Initial host and default memory checks passed. The first
full sequence in `qualified/` failed during the large-memory negative because
its oracle incorrectly required slot 0 to detect the missing FP restore. The
actual target detected it in slot 1 with status 174 while slot 0 completed.
[The triage record](old-run-triage.json) identifies the original log by digest.
That sequence remains failed/incomplete; the later image/regression checks did
not run in it.

The corrected oracle validates both unique terminal records, generation/kind,
matching task summaries, output lengths and nonzero FS bases. It accepts a 174
failure in either or both contexts, and rejects unrelated failures or missing
records. Two host tests cover valid orders and malformed witnesses. The complete
fresh sequence in `final/` passed. `target-attempts.tar.gz` retains initial,
failed and final target artifacts and logs. `SHA256SUMS` covers this packet.

## Scope and remaining work

This is a prerequisite for bounded shared-address-space threads, then thread
exit/wait/wake, all-context mapping pins and whole-domain quiescence. It does not
provide pthreads, run OpenZFS natively, or assemble the shell/package release.
Independent reader/consumer review, optimized modes and stack-high-water evidence
remain open. The wrapper records top-level UTC boundaries; inherited memory/libc
builders do not provide every internal command timestamp. These results do not
claim full draft standards conformance or owner sign-off.
