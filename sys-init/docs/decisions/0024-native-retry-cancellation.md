# 0024 — Cancellation closes retry and readiness admission

Accepted for a bounded BG-040 experiment, 2026-09-06. Apply the existing model
T16 stop-cancels-retry expectation to local native activation state. An activation
owns its attempt budget and a monotonic cancelled flag. Cancellation is idempotent;
it does not reset attempts or erase ownership. Reserve and readiness admission
both refuse cancelled state. Cancellation does not itself claim completed cleanup.

Two controlled schedules: cancel after malformed readiness has been rejected and
the provider reclaimed; or collect an actual valid frame from a live provider,
cancel before admission, and reject that frame before stopping/reclaiming it.
The latter tests readiness already collected when cancellation wins, not a new
asynchronous transport. Neither schedule launches a dependent or a retry.

Run three separately created activations, one provider each, to satisfy the native
fixture's exact three-reclaim completion. Each activation permits three attempts
but uses only one; cancellation must refuse repeated reservations and preserve
the used count. The preceding cancelled activation must remain closed after a
new activation starts. New activation creation is explicit fixture intent, not
automatic restart or reset of the old activation. Worker/reader identities differ
between generations. At most one worker is live; no allocation or new unsafe code.

Controls: ignoring cancellation in reservation rejects at 936 after one reclaim;
ignoring cancellation in readiness admission rejects the collected valid frame at
937 with zero reclaims. Both fail before any unintended launch. Identity failures
use 938; wrong rejection/cleanup uses 939. All twenty-seven earlier native cases
remain required. Expected rejection must be exact, never a timeout or boot failure.

Use existing one-byte worker modes, 10-interrupt rejection and 100-interrupt ready
deadlines, existing bounded polls and guest watchdog. No kernel ABI, shared rule,
dependency, persistent enablement or operator transport changes. The local intent
cut is explicit; concurrent command delivery, late launch completion and production
shutdown remain unimplemented. Preserve model semantics and historical receipts.

After this slice, review the accumulated native service policy as one coverage
matrix against model R-09–R-16 before adding more fixtures. Identify the smallest
missing control/observation contract for real cancellation, including in-flight
launch ownership; do not infer it from this local boolean experiment. BG-040 and
BG-050 own those follow-ons. Full checks and fresh target receipts are required.

## Result

[Target evidence](../evidence/native-retry-cancellation-2026-09-06/README.md)
passes all 31 cases. Retry/frame cancellation controls reject at 936/937 with
one/zero reclaims. The two positive clients are 1,232/1,344 bytes; all twenty-seven
prior raw supervisors are unchanged and all 178 frozen inputs remain stable.
The [policy review](../NATIVE-POLICY-REVIEW.md) identifies R-07 dependency-loss
alignment as the next native policy witness, followed by a real operation/control
contract. This cancellation result remains local intent under controlled ordering.
