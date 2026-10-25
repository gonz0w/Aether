# 0066 — First native issued-binding admission slice

Accepted experiment plan, 2026-09-06, BG-058/BG-057 ND-01.

Implement the first subset of decision 0065: two fixed synthetic issued launch
tokens, one immutable trusted context, two retained attempts and one outstanding
channel reservation. The complete ten-field token is compared; fixed symbol tables
represent schema/epoch/revision/service/action/cause. Context identity binds the
pinned producer/profile and live owner. This is trusted fixture issuance, not an
executing journal or an authentication boundary.

Launch two actual workers at equal service generation one, retain each reader and
worker, and qualify a launched event against its original token and worker.
Reject changed token fields, foreign context, duplicate service/occurrence, invalid
slot, reserved slot and a second reservation while creation is pending. Denial
preserves the retained reservation and acquisition count. After both workers have
terminated, explicit fixture teardown closes readers/reclaims workers; tokens stay
consumed. An independent third worker supplies the existing 100/reclaimed=3 oracle.

Two omission controls: ignore token binding during launched-event qualification
and detect cross-service substitution at 1014/reclaimed=0; omit the pending-create
guard and detect premature second reservation at 1015/reclaimed=0. Both require
the designated native profile panic/context, not build failure or timeout.

Run all 57 preceding cases and four new cases with pinned SI-04, Rust 1.98.0/2024,
BSP-only and existing 4 KiB clients. Retain every attempt and compare prior clients,
then all repository checks. No new dependency, unsafe operation or shared ABI.

This slice covers NB-01 and selected NB-02/03/07 checks. NB-04–06/08/09 remain
open, including post-acquisition injected failure, selected errors, predicted
target/result qualification, exhaustion and lost replies. Typed native fixture
tokens do not test a wire parser or Boolean/type rejection. ND-02 terminal kind,
ND-03 journal application/retirement and ND-04/05 composition remain separate.
The implementation must not expose replacement or receipt-history reset.

## Build review and scoped implementation

Preflight and admitted-worker sequences are separate positives. Seven retained
size attempts exceeded the unchanged 4 KiB bound before final builds fit. The
link map identified generic bounds-panic formatting and comparison support costs.
Final code retains references to immutable complete tokens, uses checked indexing,
compares all ten scalars, and keeps shared driver methods out of line. No identity
field, guard or native acceptance limit was removed. The split preserves both
negative oracles. Diagnostic map reruns are retained with their source attempt.

`launched` is a read-only qualification predicate over the retained worker/token,
not an event queue or journal submission. Mutable pending-event preservation is
not covered by this slice. Error branches conservatively close admission and retain
records; they do not yet implement selected pre-effect rejection transitions from
the full contract. No invocation replay, replacement or retirement API exists.
The live immutable context fixes producer/profile; foreign-context substitution
is local trusted-owner checking, not a native transport-authentication witness.

Review notes: the seven added/updated consumer inputs include the new private
module and runner selection. There is no added unsafe block, allocation, dependency
or output protocol. Immutable context borrowing prevents mutation through this
owner reference; public bypass and concurrency remain excluded. Private unwraps
follow fixed issuance/index/reservation invariants and retain the existing fixture
panic handler; they are not a production error-handling contract. The acquisition
count cannot exceed the two non-resettable issued entries. This fixture's producer
identity is the selected SI-04 summary pin; success on an arbitrary other producer
would need a separate identity/compatibility review. No authentication or timing
property is inferred from scalar comparison or local pointer identity.

## Validation — 2026-09-06

All 61 native cases pass with all 178 frozen inputs unchanged. Forty-four of 57
preceding raw clients match; thirteen changed clients pass their previous oracles
and are individually listed in witness/comparison.json. New sizes are 2,512 bytes
(preflight), 3,904 (admission), 3,744 (token control), 2,496 (pending control).
Both designated negative contexts pass; no native execution failed.

All eight gates pass in `out/checks/run-27l0zrbn`: 228 model tests, 23 negative
controls, 48 host tests and 37 harness tests. The catalog verifies 763 historical
outcomes across 31 bundles and 11,199 listed files. The two targeted native-input
harness tests also pass. Current seven native consumer source entries match the
executed snapshot; `git diff --check` and new document references pass.

Evidence: `docs/evidence/native-binding-admission-2026-09-06/`, including seven
failed size versions, successful preflight builds and final consuming artifacts.
Only validation notes and retained evidence copies follow checks; runtime sources,
tests, catalog and quality inventory remain unchanged. Next: NB-04 retained
post-acquisition failure plus an ownership-loss control; full ND-01 remains open.
