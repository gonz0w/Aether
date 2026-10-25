# 0036 — Bounded effect acknowledgment ledger

Accepted for BG-050/BG-033 A05/A06, 2026-09-06. Build an isolated trusted ledger
before changing Delivery.take_effects or invoking native calls. No ledger state
is a lifecycle observation, authentication or durable commit. Shared I-01–06 and
E-04–06 apply via STANDARDS.md; existing wire/native contracts stay unchanged.

Tokens contain manager epoch, revision, monotonic uint64 serial, operation ID,
service, generation and kind (launch/stop/reclaim). IDs/generations are 1..2^64-1.
Bound the ledger to eight named services, eight unresolved obligations and 64
terminal acknowledgments. Per-service generation high-water and three seen-kind
bits prevent re-reservation even after history eviction. Reject older generations
and replacement generations with unresolved work. This guard does not prove that
lifecycle cleanup permits replacement.

reserve validates an entire 1..8-effect batch before mutation, including capacity,
serial exhaustion, known services and duplicate identities. Tokens start reserved;
issue transitions once to issued and transfers invocation responsibility without
calling anything. A second issue rejects; missing acknowledgment never retries.

acknowledge accepts executed, rejected-before-effects or unknown. Reserved work
may only be rejected-before-effects. Issued work accepts any outcome. Unknown
retains its slot and cannot be changed through ordinary acknowledgment; future
reconciliation needs an explicit contract. Executed/rejected records move to
bounded history. Same token/outcome replays; conflicting fields/outcomes reject.
Evicted records return retired on acknowledgment and unknown on observation,
never a fresh issue. Trusted callers are responsible for truthful producer results.

driver_lost permanently closes reserve/issue/acknowledge. Unissued reserved work
becomes rejected-before-effects, issued work becomes unknown, and existing unknown
remains retained. Observations remain available. No replacement driver is implied.
Tokens confer no native authority; direct Python access bypasses this model.

Executed stop is not terminal observation, and executed reclaim is not cleanup
or zeroing evidence. The ledger never calls Model.batch or releases model ownership.
The future adapter must map exact producer results to separate observations and
reserve capacity before transfer. Delivery's transfer API remains unchanged and
unenforced by this isolated ledger. No crash-safe exactly-once claim follows.

Test atomic reservation denial, token mismatch, duplicate issue/acknowledgment,
unknown retention, generation/history retirement, serial/capacity exhaustion,
driver loss and unchanged model ownership. Add an issued-state mutation control;
run model/full checks and retain evidence. Next specify bounded ledger/delivery
integration and producer-result mapping, including capacity denial before dispatch.

Result: [retained evidence](../evidence/effect-ledger-2026-09-06/README.md) passes
119 model tests/eleven controls, 48 host, 37 harness and all offline gates. The
issued-state mutation fails by assertion. Native audit verifies 215 historical
outcomes; this isolated ledger adds no native execution or delivery integration.
