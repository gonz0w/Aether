# 0040 — Journal-owned lifecycle experiment

Accepted for BG-057 on 2026-09-06. Compose the existing lifecycle algorithm with
EventJournal in a separate trusted JournalRuntime. Do not change Model, Control,
AccountedDelivery or their return/wire contracts. This experiment is not a Control
backend, native driver, authorization boundary or recovery implementation.

An internal Model subclass hooks _begin, _operation, _launch and _effect; it does
not duplicate graph or observation algorithms. Existing input validation and the
256-event bound run before journal admission. _begin reserves twenty credits and
marks the cut begun before any model event counter, clock or lifecycle mutation.
The caller owns rejected observations, unchanged; there is no internal event queue.
If any previous obligation is unresolved, the whole cut denies without state or
clock progress. This conservative policy also denies incoming terminal evidence
behind unknown obligations. No observation liveness or reconciliation is claimed.

Retain one cause tuple per service independently of bounded operation history.
A new activation assigns cause only to services it newly queues; an already-owned
or retry-pending generation retains its original cause. Stop assigns its own cause
to its entire accepted scope. At launch, normalize that retained cause to activation:
restart uses the stop/restart operation ID, retry preserves the original activation
ID. Deadline-driven cancellation preserves its activation cause. Effects copy the
current service cause at emission, including background reclaim while an unrelated
operation is active. Generation, operation and cause IDs remain uint64; exhaustion
closes possible mutation rather than wrapping. Cause is trusted policy data, not
native authority or proof of producer identity.

start/stop return the operation ID only; batch returns None. No raw effects are
returned for invocation. After a successful capture, issue_obligations validates
and transfers the whole reserved token batch once. Repeated transfer returns empty.
acknowledge only updates the journal; it cannot synthesize terminal or cleanup.
The raw Model effect list and bounded attributed records remain diagnostic state.
Any exception after begin closes the owner/journal and retains uncertain credits
or tokens. Partial transfer uses driver_lost, preserving issued unknown versus
unissued rejected. There is no retry, rollback or replacement owner after failure.
Private Python access bypasses the wrapper and is outside this trusted experiment.

Test twelve-effect cuts, duplicate force, original cause after history eviction,
unrelated operations, stop/restart cause, retry cause, invalid/capacity denial,
unknown plus terminal evidence, unchanged ownership on acknowledgment, capture and
partial-transfer failures. Add an admission-before-mutation omission control. Run
model/full checks; retain exact inputs and logs. This adds only standard-library
Python model code, with no native, shared pin, wire or user-facing output changes.
BG-057 remains active for a bounded unknown-observation/reconciliation policy and
control composition; BG-032/BG-033 retain native result mapping and recovery.

Validation: 156 model tests, fourteen distinct mutation controls, 48 host tests,
37 harness tests and all offline gates pass. [Retained evidence](../evidence/journal-runtime-2026-09-06/README.md)
binds the new wrapper, tests and runner. The original Model, Control and EventJournal
sources remain identical to decision 0039; no native execution was rerun.
