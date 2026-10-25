# 0083 — Retain interrupted native samples

Accepted bounded experiment, 2026-09-06; BG-058 NT-05. Extend the decision 0081 retained
session and decision 0082 malformed-data work under the existing terminal contract.

## Behavior and acceptance

Add a private, explicitly synthetic Sampling interruption method that runs only
between received returns. It performs no syscall and cannot interrupt a blocked
synchronous kernel call. Require the active pending session and a partial Awaiting
sample; the existing pure Sample interruption records Local(Interrupted). Close
Driver admission and retain every received raw triple, worker/reader, token,
pending index and generation. Do not fabricate the missing S/O2, a terminal fact,
native errno, cleanup or retry. Reject empty, already closed or sealed samples
without new reads or state changes. This is a local disposition, not a cancellation
transport, real asynchronous signal, unknown kernel outcome or recovery mechanism.

Two native fixtures use real terminal worker O1 or O1/S returns, then invoke the
synthetic interruption. Check empty interruption denial first, actual raw shape,
exact preserved prefix/count, local cause, closed/pending state, original resources
and identity, no fact/error, and repeated interrupt/read denial with unchanged
read counts and issuance/generation/acquisition/launch state. Retention assertions
precede explicit known fixture cleanup and the existing two ordinary worker cycles.
Positive oracle: 100/reclaimed=3 and unchanged native PASS marker.

Four separately compiled controls interrupt after O1: skip closure must fail
1046/reclaimed=0; forget the prefix 1047/0; fabricate a terminal fact 1048/0;
forget reader 1049/0. Preserve all 136 prior oracles and execute 142 native cases
on the same pinned producer and worker in a fresh private root, BSP only. Preflight
strict 4096-byte links; preserve failures/maps and recheck frozen inputs. Run the
host validator controls and all nine development checks before acceptance.

Foundations O-01/O-03/O-04, I-01/I-03–06 and E-01–08 apply. Keep current
Distribution fixture/recovery exclusions and Experience developer-output scope.
No shared ABI/pin, unsafe primitive, allocation, compiler-profile, CLI/schema or
kernel-marker changes. Assertion numbers are local fixture oracles. Full launch
composition, NT-06/07 pending-history bounds, BG-057 consumer retirement, additional
NT-04 O1 native injections and BG-033 unknown-owner recovery remain open. No
independent sign-off, exhaustive scheduling, POSIX or production conformance claim.

## Preflight revisions

Initial positive images measured 4192/4256 bytes; some mutation controls reached
6800 bytes. Inlining the new interruption method shrank controls; extracting a
shared full-prefix predicate reduced repeated checks. A void assertion-helper
variant regressed and was not selected. All versions/maps remain retained.
Keep the predicate helper and move the empty-sample denial into its own native
fixture, preserving the same assertion and explicit cleanup. Partial O1/S cases
retain both before/after prefix checks and every ownership/counter assertion.
The final acceptance suite is therefore **143 cases**: 136 prior plus empty denial,
two partial interruptions and four controls. The empty denial also requires 100/3.
No kernel limit, compiler profile, previous oracle or semantic requirement changes.

## Results and review

Decision 0083 passes 143 native cases: all 136 prior oracles, empty-sample
interruption denial, two partial interruptions and four omission controls.
The partial probes retain actual O1 or O1/S returns, then invoke a private synthetic
interruption between reads. Local(Interrupted), exact prefix/count, closed admission,
pending identity, worker/reader, full token and generation remain. Repeated interrupt
and read calls deny without additional reads, invented fact/error or application.

Three positives finish 100/reclaimed=3 after retention checks and known fixture
cleanup. Omission controls reach 1046/0 (closure), 1047/0 (prefix), 1048/0 (fact)
and 1049/0 (reader). All 183 frozen inputs unchanged; 90 of 136 previous
images match byte-for-byte. Largest image remains 4048 bytes; partial interruption
probes are 3904/3952 bytes. Four earlier size revisions are retained, including
failed strict links; the fifth keeps all assertions by separating empty denial
and sharing the full-prefix predicate before and after denied calls.

This is synthetic NT-05 disposition in a native fixture, not syscall cancellation,
asynchronous delivery or lost-return recovery. Admission remains fixture-seeded.
Next: define/qualify NT-06/07 pending-history identity, conflict and capacity rules
with BG-057 consumer retirement. Full launch composition, additional NT-04 O1
injections and BG-033 unknown-owner recovery remain open.

The final inline interruption method calls the unchanged pure Sample validator;
its active-session/partial-state guards precede any mutation. The shared predicate
checks the full fixed prefix, count and local cause both before and after denied
follow-up calls. No authority is released by interruption. The fixture disposes
known resources only after those checks; it does not implement history retirement.
Reviewed ownership/lifetime, short-circuit denial, bounded reads/storage, local
versus native error identity, synthetic scheduling and exact semantic controls.
No new unsafe block, allocation, dependency, external ABI or compiler profile.
Independent review, other scheduling orders and production conformance are not
claimed. Documentation impact: terminal status, coverage/catalog, quality inventory,
standards scope and owning backlog/STATE. Evidence: `docs/evidence/native-interrupted-sampling-2026-09-06/`.

Validation: all nine development gates pass in `out/checks/run-5546ai87`.
The offline audit covers 2058 historical native outcomes across 44 bundles;
this is separate from the fresh 143-case target witness. Ten current consumer
inputs and unchanged worker/builder sources match their executed/build snapshots.
All 38 harness tests and nine named host validator tests with two omission
controls pass. Validation artifacts, current adoption records and all preflight
revisions are retained with the evidence.
