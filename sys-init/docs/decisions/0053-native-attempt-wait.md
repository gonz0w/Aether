# 0053 — Native attempt wait ownership and cancellation

Accepted 2026-09-06, BG-058 bounded native extension of decision 0052.

The Attempt record now owns an optional Wait. Registration requires an admitted
worker and no existing attempt wait; store only a successful adapter registration.
The adapter retains its domain-wide one-wait/64-token constraints. Local missing
worker/wait errors use operation=0/errno=9; duplicate registration uses 0/16.
Cancellation returns the adapter Completion while retaining the Wait. This is
cancellation of observation, not service-stop intent, termination or cleanup.
Repeated cancellation may retain the same completion. Release clears the field
only after adapter release succeeds; missing/double release is denied locally.

Complete cleanup closes remaining endpoints, reclaims the terminal worker and
explicitly releases any wait. Clear each field only after success. A failed release
leaves the wait owned even when worker/reader fields are already clear. clean()
includes absence of the wait. Existing no-wait busy retry semantics remain.
No Drop cleanup, concurrent owners, unknown reconciliation or new unsafe operation.

A separate native sequence creates three terminal normal-return attempts in slots
[0,1,0]. For each, register against its current terminal revision with a distant
bounded deadline, verify pending, reject a duplicate registration locally, cancel
twice and verify Cancelled while the token remains owned. Clean the attempt,
require both attempt and adapter clean, verify the old token is stale natively and
reject duplicate release locally. The positive must finish result=100/reclaimed=3.
A pre-launch registration denial also confirms no worker can be invented.

Two controls: forgetting the token on cancel must hit assertion 971/reclaimed=0;
omitting explicit release must hit 973/reclaimed=1. Both require the designated
native profile panic, never a timeout or unrelated failure. Assertions 970–974 use
existing fixture output/stream conventions, not operator UX changes.

Use the pinned SI-04 producer and original helper images, unchanged Rust/toolchain,
4 KiB/BSP-only profile and offline runner. Execute the 20 previous cases plus three
new cases; compare earlier binaries and retain any differences explicitly. Existing
Attempt layout may change; do not promise byte identity before comparison. Run all
repository checks and retain exact source/artifact hashes and raw logs.

The source basis is the frozen native_wait.zig and native_c.zig waitOperation from
decision 0042: cancellation preserves occupancy and release is explicit. Foundations
O-01/O-04, I-03–06, E-01–08 and scoped ownership/partial-error review apply. No shared
ABI/pin, dependency, unsafe primitive or POSIX wait/signal behavior is introduced.
Service cancellation, deadline-selected completion, failures during cleanup and
full native driver composition remain BG-058/BG-040; recovery remains BG-033.

Decision 0053 validation: 23 native cases pass with 177 frozen inputs unchanged.
Eighteen old binaries match; two changed Attempt binaries pass their prior oracles.
Full checks pass: 228 model tests / 23 mutation controls, 48 host tests, 37 harness
tests and all eight offline gates. Catalog: 275 outcomes / 20 bundles / 5,581 files.
Evidence: `docs/evidence/native-attempt-wait-2026-09-06/`.
