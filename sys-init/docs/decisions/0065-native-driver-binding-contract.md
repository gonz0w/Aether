# 0065 — Bound issued identity before native acquisition

Accepted local experimental contract, 2026-09-06, BG-058/BG-057 ND-01.

Adopt [Native driver binding v0](../specs/NATIVE-DRIVER-BINDING-V0.md) as the
implementation/test contract. Preserve the full existing event-effect token,
trusted live owner and fixed producer/profile. Reserve attempt/slot capacity before
native acquisition and retain effects through later binding failure. Distinguish
preflight denial from an ambiguous post-invocation result.

The first fixture uses at most two attempts, one channel invocation at a time and
one retained synthetic issuance cut of at most 20 entries. It cannot reset consumed
entries or retire/replenish attempts. This bounded table permits native identity
tests before a journal port; it is explicitly not actual journal issuance or an
external authority boundary. ND-02 terminal qualification and ND-03 cut acceptance
remain prerequisites for full event integration.

Using only generation/slot would conflate different issued launches. Wiring a full
journal now would combine identity, resource and cut semantics. A private retained
binding establishes the next boundary without altering ABI/model tokens, choosing
a production language or importing Linux-only facilities. NB-01–09 specify future
positive/negative oracles; none is claimed implemented by this documentation.

The source comparison in decision 0064 is the research basis. Review considered
capacity, stale identity, errors before/after effects, resource retention, replay,
owner closure and fixture-only trust. No independent sign-off is claimed. New
native source must receive a separately recorded fresh consuming witness.

## Validation — 2026-09-06

All eight gates pass with `python3 scripts/check-all.py` in
`out/checks/run-u5vfsq1z`: 228 model tests, 23 negative controls, 48 host tests
and 37 harness tests. Native catalog verification retains 702 historical outcomes
across 30 bundles; no new target execution. Six native consumer sources match
the executed decision 0063 manifest. New local document links and
`git diff --check` pass. Evidence is retained in
`docs/evidence/native-binding-contract-2026-09-06/`. Only validation notes and
evidence copies follow checks; implementation, tests and quality inventory are
unchanged. ND-01 implementation remains the next unblocked step.
