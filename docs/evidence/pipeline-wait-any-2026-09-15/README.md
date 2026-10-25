# Multi-child wait-any intake — 2026-09-15

The private multi-child parent now uses archive-derived public musl wait3/wait4
alongside waitpid. The same narrow substitutions and non-null resource-usage
rejection used by the existing native-connections candidate are reused here.
No SDK or upstream archive is modified. Build inputs and upstream copyright are
retained in the generated artifact archive.

Before workers are released, the parent checks an unrelated capacity-peer PID
(ECHILD), live wait-any (zero) and live exact-child wait (zero). Each leaves its
status sentinel unchanged. The owner independently observes live native handles
and confirms no collection occurred. After data dispatch it collects via wait3
with WNOHANG, blocking waitpid(-1), then exact wait4, each once. Exhausted wait-any
returns ECHILD. Non-null resource usage returns ENOTSUP with unchanged status and
usage buffers. Private wait replies are validated under the existing mask before
status publication; malformed transport poisons further wait calls.

Only authenticated Parent requests reach the three current child handles. A PID
alone cannot select another process. The owner retains three collection flags,
scans exact native terminal records and returns a terminal child, zero while a
matching child is live with WNOHANG, or ECHILD when none remain. Normal exit status
is derived from the record. The bounded blocking scan is not a general scheduler.

## Attempts and qualification

Attempt1 failed during private wait4 compilation: the build lacked the explicit
internal syscall header needed by __syscall_ret. No target cases ran. The existing
native-connections build includes that header; the capacity build now does too.
The failed source snapshot, compilation diagnostics, incomplete target report,
artifacts and passing first host run are retained. This was a build integration
failure, not a runtime failure or accepted negative case.

Attempt2 passed31 earlier target cases, then failed the new positive with
owner2610 before reclaim. The completed third early wait reply could still fill
the parent channel when the owner attempted its next one-byte release token.
This was a runtime backpressure defect. The new profile now uses the existing
bounded send helper to await space, without retransmitting replies or enlarging
the channel. Failed sources, native logs/artifacts and passing host run are retained.

Commands:

- `python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json`
- `zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`

Attempt3 passes33 native cases on278 frozen inputs; target case total is88.947
seconds. Positive retains exact data/EOF and fifteen normal reclaims across three
generations. False early completion returns a child PID while that child is live;
the parent rejects123, then owner2730 with zero reclaims. All three host runs pass104 checks. Final formatting/pin/workflow checks, frozen input
verification and exact command/artifact identity accompany the seal.

## Scope and compatibility

The final comparison finds41 of43 previous top-level ELF/raw images byte-identical.
The parent/interleave client images changed with the shared local wait call
refactoring; their existing target cases remain required regressions. New positive
owner13536 bytes and negative owner13584 fit16384. Five private capacity
source/harness files change. Kernel, shared adapter/pipe core, SDK, dependencies,
quotas, sibling repositories and released pins remain unchanged.

This still uses fixed early-poll and post-dispatch collection phases. Actual dash
execution, concurrent blocking wait/data scheduling, signal interruption,
nonzero/signal terminal statuses and usage accounting are not qualified here.
Scoped standard streams and child-driven builtin/exec scheduling remain the next
integration work before unchanged pipeline/early-reader scripts, SIGPIPE/status
composition, matching full suites and independent SDK/userland intake. Persistent
storage/OpenZFS, packages, recovery and sys-init assembly remain R1 requirements.
No full-dash or release acceptance is claimed.

Preimplementation review and outcome are in NATIVE-SHELL-STARTUP. Source/review
archives preserve inputs, guidance and test support. collect.py verifies every
owned output file against its archive before duplicate cleanup; cleanup.json
records it. Prior sealed evidence is untouched. SHA256SUMS excludes only itself.
