# 0041 — Bounded observation retention behind unresolved effects

Accepted for BG-057/BG-033 on 2026-09-06. Add an opt-in QueuedRuntime over
JournalRuntime. Separate accepting trusted observation data from applying its
lifecycle cut. Retention never acknowledges an effect or resolves unknown state.
Foundations I-01/04–06 and E-04–08 apply through STANDARDS.md.

batch validates and copies one complete cut, then returns a monotonic uint64
intake ID. Keep at most four cuts, each with at most four observations, preserving
within-cut tuples and FIFO cut order. Retained generation is 0..2^64-1;
integer values are signed 64-bit (exit remains 0..255). Strings must be exact
built-in str values under the existing model length bounds; subtype payloads
reject. These narrower intake bounds do not alter the base Model contract. Equal logical times are allowed; time must
not precede the last accepted cut or current model time. None means the last
accepted time (or current model time initially). Reserve the remaining 256-event
model budget for queued cuts as well. Invalid input, time/budget or ID exhaustion
reject without queue, journal or lifecycle mutation. Extract Model's existing
validation into a shared pure method to avoid duplicating event rules; Model.batch
continues to validate at application too.

The fixed four-cut capacity is an experimental resource bound, not a measured
native queue or production service budget. A fifth otherwise-valid cut sets the
sticky intake_lost flag and closes the owner via driver_lost, retaining the four
accepted cuts and existing ownership. The fifth cut is not accepted and remains
caller-owned. This conservative closure reflects inability to guarantee continued
retention, not proof the caller lost its copy. No drop-oldest, merge, implicit
terminal processing, unbounded queue or automatic restart is permitted.

apply_next returns None when empty or blocked by unresolved journal work; it
returns the intake ID only after a whole cut applies and its effects are captured.
peek returns the immutable oldest (ID, time, observations) tuple. Failure after
mutation retains the head for diagnosis and closes further application; it is
not retryable. Normal journal acknowledgments can reopen application after
confirmed execution; unknown cannot. No automatic native result mapping occurs.
New start/stop requests reject while any cut is queued, preventing commands from
passing earlier observations. Explicit driver loss retains the queue; no recovery
owner or replay after replacement is supplied. Direct private model access bypasses
this trusted fixture and is excluded.

This establishes bounded evidence retention and explicit overflow failure, not
liveness behind unknown effects. BG-033/BG-032 must specify authoritative producer
reconciliation and its exact identity/terminal/cleanup witness before any unknown
slot can be released. BG-057 remains active for that policy and control composition.
Existing JournalRuntime, Control and submission-token contracts remain unchanged;
QueuedRuntime has a separate intake/application API, not an external wire protocol.

Test retained payload bounds, unknown plus retained terminal cuts, valid acknowledgment then FIFO application,
cut immutability, invalid/full/budget/clock rejection, sticky overflow closure,
command ordering, serial exhaustion and post-mutation failure retention. Add a
queue-bound omission control. Run model/full checks and retain source/log hashes.
No new dependency, native code, shared pin, CLI output or production timing claim.

Validation passes: 165 model tests, fifteen distinct mutation controls, 48 host
tests, 37 harness tests and all offline gates. [Retained evidence](../evidence/observation-inbox-2026-09-06/README.md)
includes the earlier 164-test checkpoint and the final retained-payload bounds.
The base validation extraction preserves existing tested semantics. Native code
and shared pins are unchanged; no fresh native execution was performed.
