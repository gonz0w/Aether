# 0163 — Journal admission and retirement integration

BG-057, 2026-09-07. Qualify the existing CutCoordinator, CleanedAdapter and
Retirement together using the actual JournalRuntime and Model. Keep the resource
inspection, pending position and tombstone operations explicitly synthetic. This
is a composition test, not a new native driver or duplicated lifecycle algorithm.

Use two attempts and at most six cuts. Apply Launched, Terminal and Cleaned through
the journal; release a pending position only with its exact Applied Terminal
receipt, then retire only Cleaned members with earlier confirmed release. Exercise
mixed Cleaned/Launched and Cleaned/Terminal cuts. The unrelated member's pending
position and any real journal effect obligations must survive retirement/replay.
No reset, replacement admission, native operation, dependency or shared pin change.

Acceptance: exact history and journal tokens survive successful retirement;
release is required independently of cleanup; changed resource inspection rejects;
uncertain release or tombstone confirmation closes the coordinator without retry
or changing an Applied journal receipt. Retain partial tombstones and unrelated
member state. Exercise source omission controls against this actual journal path.
Run model and full local gates. BG-058 retains native source/resource provenance;
BG-060 retains reuse and BG-033 recovery. Do not infer native integration from this
trusted single-owner model composition.

## Validation and handoff

Decision 0163 qualifies the actual JournalRuntime, CleanedAdapter, CutCoordinator
and Retirement together. Mixed Cleaned/Launched and Cleaned/Terminal cuts retire
only the Cleaned member and preserve the other member's real journal obligation,
synthetic pending position and lifecycle state. Old release/retirement replay is
inert. Cleanup does not substitute for pending release, and retirement performs
a fresh resource inspection. Uncertain release or marking closes the coordinator
while retaining Applied receipts, partial tombstones and actual journal state.

All 287 model tests pass, including seven new integration tests and two source
omission controls. All ten local gates pass in `run-zegjjv6m`, with unchanged
checked inputs. All twelve native consumer sources, three release locks and catalog
bytes match the preceding checkpoint. Runtime algorithms are unchanged: this is a
composition witness using trusted synthetic resource, pending and mark callbacks.
It is not native disposal or independent reviewer sign-off.

Next BG-057/BG-058: review the native adapter mapping against the current 185-case
checkpoint and define a bounded consuming integration witness for the three-phase
cut, pending release and retirement path. Native provenance/resource ownership
remain explicit requirements. BG-060 retains sustained reuse, BG-033 recovery and
BG-056 the producer source-closure limitation; no historical waiver is broadened.

Review: this composition reuses the existing algorithms rather than introducing a
second owner or cleanup implementation. The oracles inspect real journal tokens,
state snapshots and exact receipts independently of synthetic callback returns.
Controls remove the release prerequisite or admit a Terminal member to retirement;
both fail named assertions on this same actual journal path. A closed coordinator
is the execution boundary; raw runtime bypass remains outside its trusted-owner
contract. No runtime code, dependency, CLI or native source changes were needed.
Documentation impact: composition reference, test count, quality coverage and
BG-057/BG-058 handoff. Evidence: `docs/evidence/journal-retirement-integration-2026-09-07/`.
