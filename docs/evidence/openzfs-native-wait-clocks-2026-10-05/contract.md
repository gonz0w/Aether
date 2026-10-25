# Checked OpenZFS wait-clock callers

Before implementation,2026-10-05,R1-03. Correct the remaining three direct clock
reads and deadline arithmetic in cv_timedwait, cv_timedwait_hires and tpool_worker.
Use the already checked wall helper for CV deadlines, preserving microsecond
precision, and check tpool's direct realtime result before linger addition. Reject
failed/malformed clocks and arithmetic overflow with125 before wait submission or
mutex-owner changes. Compare absolute deadlines before subtraction so expired
LLONG_MIN inputs cannot overflow. Keep expired/zero/negative durations returning
-1, existing relative/absolute flag semantics, tick conversion119 and wait result/
mutex restoration behavior. No error retry, fake UTC, virtual-time substitution,
new timer ABI, deadline queue or runtime wait implementation.

Aether owns the private C engine port; userland owns maintained clocks/POSIX/thread
runtime, sys-init owns supervision. No kernel/SDK/public ABI/quota/launch profile/
workflow entry/sibling/released pin change. Full engine entry stays unavailable
until truthful calibrated clocks/UTC, timed waits, other providers and resource/
feature closure qualify. No engine startup, actual pthread timed blocking/progress,
recovery or filesystem/package/R1 acceptance is claimed by arithmetic/caller tests.

Verify the entire previous sealed packet/archive before regular-file selection.
Relink its exact ordered177-object/113-input checked engine baseline byte-identically.
Fresh original compilation of the two actual affected inputs must match prior bytes;
replace only those positions with adapted source. Header/queue/SDK/support bytes
stay fixed. Inspect final ELF counts/imports/relocations, strict discovery denial,
current loader geometry/W+X/TLS controls and frozen source/tool custody.

Tests compile exact function/block slices from actual adapted sources, never a
reimplementation of their arithmetic. Controlled host clock/wait providers test
expiry, relative/absolute/tick conversions, carry/boundary/overflow, failed/invalid
clocks and wait success/timeout/error/owner restoration. Positive modeled waits
are explicitly host-only and are never linked into the engine. Actual old source
controls must fail the intended denial oracle. Native isolated caller cases use the
unchanged SDK for real unavailable-clock125 and no-clock expiry paths, preserving
existing TLS/yield/output/terminal witnesses. Test-only ddi_get_lbolt and wait stubs
allow isolation; they do not qualify a native monotonic source or timed blocking.

Security: clock outputs and deadline arguments cannot wrap or publish a wait after
failure; valid mutex ownership persists through pre-wait denial. No new grant,
shared mutable service state, allocator or unsafe boundary. Port-internal checked
CV addition helper is static to one file; no new general framework. Simpler raw
arithmetic/unchecked calls retain corruption or undefined reads. Borrow original
OpenZFS wait semantics deliberately, adding bounded checks while retaining actual
wait/owner behavior. Remove unsafe direct gettimeofday assumptions without adding
protocols. CDDL source/style and existing licenses remain; original probes/tools
are BSD-2-Clause. Foundations O/I/E, DEVELOPMENT and SE-01–05 apply.

Freeze sources/tools;180-second subprocess/30-second QEMU/3-second teardown bounds;
retain every attempt. Full host/pin/workflow and explicit simplicity hashes plus
scoped syntax/format/links, affected native caller tests and fresh loader models.
Update STATE/ROADMAP/FEASIBILITY; read back all artifacts before removing only
verified owned duplicates. Independent owner/reader/consumer and wider SESSION
acceptance remain separate, and no standards pin follows a mutable sibling tree.

Build attempt1 reproduces the baseline and both original objects, then the moved
tpool copy cannot find its local quoted thread_pool_impl.h. Preserve the failed
compile. Before attempt2 add only -iquote for that same original local directory;
angle-header/SDK search order and all input bytes remain unchanged. No header is
fabricated. Actual original object byte identity remains required.

Host attempt1 passes24 cases then LLONG_MIN tick expiry becomes unsigned under
Darwin clock_t and reaches the clock denial instead of modeled native expiry.
This is a test-platform type mismatch, not a product pass/fail. Before attempt2
model signed64 musl clock_t explicitly and assert signed64 time_t/ticks; preserve
the original failed harness/header/probe and logs. Native compilation uses actual
SDK types unchanged. No deadline input is weakened to avoid the signed boundary.

Native attempt1 passes the two CV clock denials, then the tpool-only probe leaves
its test CV variable unused under -Werror. Preserve that compile failure and all
prior target results. Before attempt2 explicitly mark the unused test variable;
engine source and caller slices are unchanged. Rerun the six cases on final probe
bytes. Host53 cases pass before this test-only change and rerun on the final probe.
