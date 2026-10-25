# 0147 — Local EHT-01 runner

BG-054 implementation slice, 2026-09-07; Foundations E-01–08 and the internal
Experience exception apply. Implement check-extended-host.py around the existing
aggregate run_check capture/cleanup and atomic report primitives. Validate the
fixed EHT-01 plan, exact discovered IDs and complete corpus input map before
running tests. Each worker independently verifies plan/source identity, records
actual startTest order/counts and runs one seeded class-contiguous suite. Parent
checks full evidence, source hashes and seed/order, never exit zero alone.

Eight fresh workers sequentially, 60 seconds/4 MiB each, 600-second campaign;
existing run_check provides one-second cooperative/forced owned-group cleanup.
Record cleanup scope honestly; escaped descendants remain outside guarantees.
Private reports retain commands, logs/hashes, ordered IDs, outcomes, omissions and
implementation hashes. Source drift or invalid worker evidence fails closed.
--seed replays one manifest seed and is labeled replay, not full qualification.
No automatic retries/scheduling or inclusion of the campaign in the ten gates.

Test deterministic ordering, malformed plan/worker evidence, source drift and
supervisor failure paths using controlled workers; reuse and run existing real
capture/interruption tests. Run full checks, then all eight real host seeds.
Preserve all native/sibling/standards/corpus bytes. This is host order/repetition
qualification, not exhaustive scheduling, native or production acceptance.

## Validation

Decision 0147 implements the bounded local EHT-01 runner and exact-seed replay.
All eight real workers passed all 54 cases (432 executions, zero skips); six
focused runner tests and all ten gates pass in `out/checks/run-546kedgj`.
Native audit output, catalog, 24 native inputs and release pins remain unchanged.
No scheduling or other-platform qualification is claimed. Next: review the
campaign evidence and qualify on the next available supported host; independent
technical/reader review and release cadence/platform decisions remain open.
Evidence: `docs/evidence/extended-host-runner-2026-09-07/`.

Failure paths use controlled capture outcomes; existing real capture/cleanup tests
run in the full evidence gate. The campaign ran before final documentation and
harness-test additions; its implementation and all 16 corpus identities still
match. Manual reflow after full checks changes no runner or corpus bytes.
