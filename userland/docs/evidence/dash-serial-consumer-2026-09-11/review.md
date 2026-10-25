# UL-007 serial shell intake — pre-execution review

Select shell-resume-2026-09-11, manifest
edf9e13d6097fb22a686b7d4e113cda7f47372b8789ffbdcbdcb36812e7a71d1.
Verify all 35 files before consumption; use run-sources, not post-run prose.
Compared against local 431-case helper consumer: 50 changed/new paths include
kernel freeze/private copy/exec publication, signal-copy/reset candidates,
AENMX002/003 profiles, private libc process hooks, descriptor dispatch, configured
dash jobs/input objects and separate UART backend. This is not an installed SDK.
The scoped intake review is not independent security or reader approval.

Ownership/bounds: kernel factory and generation-bound worker/channel capabilities
control freeze/copy/image publication. PID/path metadata conveys no grants. Copy
requires parked source, fresh destination, owned empty channel endpoints and token;
rollback keeps generation and zeroes unpublished backing. Exec uses validated
immutable images under supervisor CR3 and publishes after descriptor settlement.
Signal copy excludes pending occurrences; exec preserves pending/mask, clears
caught pointers and retains ignore. Native UART remains exclusive to backend,
shared across two sessions; reused slots must be denied its still-open grant.
New ABI17/18 owners allow 16 KiB; old envelopes keep 8 KiB. No local quota change.

Actual dash selects separately pinned jobs/input objects: fork/exec instead of
vfork and existing one-byte input fallback instead of Linux tee read-ahead.
Existing 32 imported objects and enabled main stay pinned; preserve licenses.
Original objects remain controls. The private healthy parent cleanup checks
captured PID plus initialized/unpoisoned transport rather than fixed exit code;
copied-child error gates remain. No TTY, line editing or job-control claim.

Select full 241 connections, five launch, two ABI18 console and 55 composed-init
regressions because kernel/profile changes affect loader/mapping bounds. Run host
Zig/tests. No fresh SMP/M4 or whole-kernel qualification is claimed. Exact source
and SDK hashes must match before and after; musl archive required by private libc
source builds is verified against SDK evidence. Tool/compiler/flags/ABI identity
comes from pinned locks and native receipts. Source trust remains UL-016.

Native oracles: all case counts/status/order; serial resume requires four prompts,
six ordered host writes, actual child72 before continuation, printed72 twice,
parent0 then7, exact six reclaims. Old cleanup must reject parent0/owner2131 with
zero reclaims; wrong second exit parent8/owner2130 preserves only two earlier
reclaims. Tee and wrong-input controls reject their named boundaries. Retain every
attempt, serial log and host exchange receipt. QEMU direct child has 30-second
watchdog and terminate/kill cleanup; forced teardown cannot pass. Outer process
owner adds complete descendant cleanup and per-stream 512 MiB limit. Deadlines:
connections1800, launch/console300 each, composed-init900, host600 seconds.
Use controlled PATH/LC_ALL/private TMPDIR and private build root; no sibling edits,
real-prefix writes, default/published pins or background monitors.

O-01–05, I-01–06, E-01–08; Distribution NC/PX/TX/OB/TR and approved quality TD/TE/CP
apply in scoped form. Experience pins read; preserve upstream prompt and machine
markers, do not claim renderer/TTY conformance. Local quality inventory and syntax/
whitespace checks required. Python 3.14.7 execution, no minimum-version claim.

SE questions: reuse the sealed owner experiment and existing process wrapper is
the simplest adequate intake. Adding a separate terminal/process framework would
not help qualify this input. No existing compatibility path is removed; preserve
old fixtures and evidence. This run does not close full M3, source trust,
independent review or UL-081 integration. One external child per shell, finite
waits, general pipelines/redirection and sys-init/persistent assembly remain open.

Actual results: pending.

## Retained selection correction

The first outer attempt stopped on its expected-count assertion after successful
241 connections, five launch, two console and 32 composed-init cases. I incorrectly
assigned the producer's aggregate 55 init-capacity cases to composed-init alone.
The sealed console-process-profile qualification and exact native inventories show
32 composed-init plus 23 init-large. This is an intake planning/check error, not a
native failure. Original run.py and results.json remain unchanged. The completion
driver rechecks source/SDK/tool integrity, binds the passing composed receipt to
its exact producer case order, then runs the missing 23 init-large cases and host
checks. It writes qualification.json separately and binds the initial failure.
No native/oracle behavior was changed, no passed suite is silently retried, and
no threshold was relaxed. Final target selection remains 303 cases in five suites.


The completion driver passed the 23 missing init-large cases, then its host
invocation was rejected before process launch: the local process helper requires
an absolute executable. Retain qualification.json and complete.py unchanged.
finish-host.py selects the already pinned absolute Zig path, verifies its digest,
rechecks source/SDK bytes and writes final-qualification.json separately. This is
a second intake-driver error, not a native or host-test failure. No host test ran
in that rejected invocation; cleanup correctly records not-started.


The absolute host run executed and failed six workflow-test outcomes because
`docs/NATIVE-INIT-COMMAND.md` was absent from the composed runtime/scaffold tree.
Its 90 Zig tests passed; 99 Python tests ran with five failures and one error, all
reported under the inventory mismatch. Preserve host-absolute streams and
final-qualification.json. The workflow oracle is unchanged. Pin the missing
current documentation input in host-inputs/ and copy the original pinned tree to
a separate host-only root; add that one file, rerun host checks, and verify all
original bytes remain identical. No native input or sealed producer packet is
rewritten. Host coverage applies to this explicitly completed document inventory.


## Actual disposition

All 303 native cases and six independent serial protocols pass. The host-only
inventory completion passes Zig/workflow and 99 Python tests. Retain all three
intake/host failures exactly; none is represented as successful. No native reruns
or behavior changes. Raw logs/host events and configured object provenance retained.
Update README, PLAN, WORKLOADS, current backlog, ROADMAP, STATE and gap record;
coverage stays draft with independent review pending. Full M3 remains incomplete.

Final [acceptance record](acceptance.json) passes identity, native receipt, source/SDK,
serial protocol, syntax and tracked-whitespace checks. [Local quality output](quality.log)
passes the documentation/pin inventory gate; publication and independent reviews
remain separate. SHA256SUMS binds retained bytes, including failed attempts.
