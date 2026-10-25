# 0157 — Pure cut coordinator core

BG-059, 2026-09-07. Implement a bounded Python model beside the existing journal
models, following decision 0156 NC-01–05 and the ordered-phase subset of NC-03.
This chooses a model implementation, not a production language or native API.
Sources and the application adapter are explicitly trusted synthetic fixtures.
No native History, lifecycle journal, actual resource or reset API is changed.

Retain six cut records and one active reservation. Exact immutable source objects
bind owner, attempt, ten-field token, worker, phase and bounded content; caller
copies cannot replace retained origin. Validate whole membership/order before
reservation and revalidate prior to apply. Reserve twenty synthetic journal
credits through an explicit adapter ticket. Require observed phase transitions
and an exact cut-bound capture result before publishing an immutable receipt.
Busy/full and invalid identity preserve model/source state. Applying failure closes
and retains Unknown; cancellation burns its cut record/serial. Exact Applied replay
returns the same receipt without invoking the adapter or consuming capacity.

Tests cover two-service cuts, three ordered phases, every changed token field,
foreign owner/source/cut, busy/full/exhausted serial, changed preconditions,
cancellation, no-op/incorrect capture and failure after mutation. Three source
mutation controls must fail named assertions for identity, premature application
and repeated application. Required model runner includes this source in its hash
inventory and runs these tests through the existing model gate. Run all ten gates.

NC-06 pending release, NC-07 retirement, resource uncertainty, real journal
reservation integration and native provenance remain BG-059/BG-057 follow-ons.
Python objects use runtime allocation: only logical counts are bounded here; no
native stack/heap or 8 KiB fit claim. Foundations O/I/E scope and Distribution
persistence/recovery exclusions from decision 0156 remain unchanged. No shared
pin, sibling or syscall changes. Record documentation impact and retained evidence.

Review refinement: the initial 237-test/ten-gate snapshot passed but did not
enforce callback reentry denial. The final slice adds an explicit guard around
reserve/apply/cancel callbacks and a three-boundary regression, for 238 model
tests including ten coordinator tests. The preliminary source/check snapshot
is retained; it is not the final acceptance result.

## Validation and handoff

Decision 0157 implements the pure cut-coordinator core: exact immutable synthetic
source/cut identity, six retained records, one active reservation, ordered phases,
pre-application revalidation, explicit callback reentry denial and exact receipt
replay. Uncaptured application closes with Unknown and retains any returned result;
cancellation consumes its serial/record without resurrecting the cut.

All 238 model tests pass, including ten coordinator tests with three embedded
source omission controls. All ten local gates pass in `run-94phzf3m` with unchanged
checked inputs. The controls detect foreign-cut admission, false captured success
and a second actual synthetic adapter application. All twelve native consumer
sources, release locks and catalog bytes remain unchanged. No fresh native
execution is claimed: the 185-case decision 0155 witness remains current, including
its separately tracked BG-056 producer source-closure limitation.

Next BG-059: define and qualify the synthetic resource-disposition/retirement
boundary, including nonempty/partial inventory, stale retirement receipts, premature
retirement, reset omission and post-commit bookkeeping failure. BG-057 retains
real journal/lifecycle and native integration; BG-060 sustained reuse and BG-033
unknown recovery remain open. No resource cleanup, native origin, retirement or
history-reset API is implemented by this pure model slice.

Review: source payloads and receipts contain immutable bounded tuples; origin is
retained object identity within a trusted fixture, not hostile-caller enforcement.
The adapter reserve contract assumes no effects on a raised reservation; this is
not a witness for a real journal. Reentry is rejected during all three adapter
callbacks. Received-but-invalid capture remains diagnostic; Applied is published
only after matching both receipt and observed phase state. Python allocations
remain outside native memory guarantees. No independent sign-off is claimed.
Documentation impact: model reference/count, contract checkpoint, checked runner
source inventory, command-source digest/line references, quality surface and backlog.
Evidence: `docs/evidence/cut-coordinator-core-2026-09-07/`.
