# 0071 — Retain native returns before local application

Accepted local experimental design, 2026-09-06, BG-058/BG-057 NB-09.

Adopt [Native invocation and receipt ownership v0](../specs/NATIVE-RECEIPT-OWNERSHIP-V0.md).
Separate reservation, non-repeatable invocation, retained return and local
application. One driver-owned position holds the exact call identity and any
returned resources. Closure preserves evidence and consumption; receipt application
does not acknowledge a journal occurrence or prove lifecycle cleanup.

The current synchronous driver has no lossy reply transport. Its pending index
alone will not guard a future split invocation/application path. The source review
therefore selects a channel-return pause with retained ownership as the next
native slice. A missing-return schedule is synthetic; actual kernel reply loss
and owner recovery remain unqualified. Launch follows separately because its
successful return transfers the writer and must retain the actual worker before
application. IR-01–07 define positive, denial and semantic omission oracles.

Immediate application cannot expose the pending-receipt boundary; caller-owned
reply objects risk losing resources; durable receipt/recovery infrastructure is
unsupported by this research. The bounded private position needs no ABI change,
new dependency or production-language choice. The linked contract records the
source comparison, limits and standards review. BG-058/BG-057 remain active for
IR-01–07 and remaining NB/ND work; BG-033 retains unknown-effect reconciliation.

This decision changes documentation only. The seven native consumer inputs match
the executed decision 0070 snapshot; its 75-case witness is unchanged. It does not
prove the new phases or add native cases. Fresh native evidence is required for
the next implementation. Retained review: `docs/evidence/native-receipt-contract-2026-09-06/`.

## Validation — 2026-09-06

`python3 scripts/check-all.py` passes all eight gates in
`out/checks/run-jxyxd88h`: 228 model tests, 23 negative controls, 1000 traces,
48 host tests and 37 harness tests. The unchanged native catalog verifies 1040
historical outcomes across 35 bundles; this run does not execute native cases.
All seven current native consumer sources match the decision 0070 witness.
New contract/decision links resolve and `git diff --check` passes. Review and
validation are retained in `docs/evidence/native-receipt-contract-2026-09-06/`.
Only validation notes and evidence copies follow the checks; implementation,
contracts, pins and inventory remain as checked. IR-01–04 implementation is next.
