# Native service policy versus the runtime model

Reviewed 2026-09-06 against [R-07–R-16](specs/RUNTIME-V0.md), the
[model tests](../tests/test_runtime_model.py), [native policy source](../prototypes/native-supervisor/service.rs)
and decisions 0019–0025. These are local source comparisons, not a new shared
standard or independent review. The model and native fixture profiles differ;
passing their tests does not make them interchangeable.

| Requirement | Native evidence/scope | Remaining work |
| --- | --- | --- |
| R-07 dependency loss | Decision 0025 keeps the admitted consumer running, records provider loss and blocks new admission under native stop and normal return | Bounded alignment now passes. Older 0019/0020 stop-on-loss profiles remain historical; no real operator loss reporting, queued-consumer launch or general graph rebinding is claimed. |
| R-09 fresh readiness | Decisions 0019/0021/0022 bind one-byte frames to worker/reader/generation and reject terminal/expired evidence | Production framing, helper delegation and a monotonic wall-clock contract remain open. |
| R-10 restart classification | Separate native normal-return, forced-stop and readiness-failure fixtures | No unified never/on-failure policy, one-shot/configuration distinction or full launch-error classification. |
| R-11 finite retry | Decision 0023 uses three total attempts, equivalent to two automatic replacements; decision 0024 adds local cancellation | No fixed retry delay, persistent desired-running state or request-join semantics. Explicit fixture activation is not an operator start request. |
| R-12 operation failure | Failed readiness is cleaned before one retry/exhaustion | No partial graph transaction, operation deadline or separately reported incomplete cleanup. |
| R-13 stop scope | Local cancellation closes admission; cleanup is explicit | No graph scope validation, real caller authority or inventory of asynchronous in-flight launches. |
| R-14 stop completion | Native stop, terminal observation, close and reclaim are separate | No cooperative stop or production cleanup-failure recovery; unexpected errors remain fatal fixture assertions. |
| R-15 operation identity | Worker/generation identity is observed; cancellation is local state | No request ID, deduplication/join, transport or supersession of a pending asynchronous launch. |
| R-16 shutdown scope | Earlier owner-exit/fault fixtures exercise kernel-owned domain cleanup; decision 0024 closes local activation admission | No full-machine shutdown policy, graph-wide in-flight inventory or ordinary control-transport witness. |

## Work order

1. Completed bounded BG-040/BG-042 witness: decision 0025 demonstrates R-07 under
   stop and normal return, with incorrect-auto-stop and new-admission controls.
   Keep decisions 0019/0020 and their evidence as historical scoped fixtures.
2. BG-040/BG-050: specify a minimal activation/control contract with operation
   identity, explicit desired intent, cancellation observation cut, duplicate
   requests and ownership of late launch completion before implementing transport.
   [Control v0](specs/CONTROL-V0.md) now records that logical contract and fixes
   stop/shutdown joining in the model. Decision 0027 adds tested in-process
   receipts and logical client waits. External encoding, caller/session authority
   and real native transport remain unimplemented boundaries.
3. BG-032: review any resulting missing native clock/wait/control mechanism against
   current companion evidence. A local policy test does not prove the mechanism
   exists or that a kernel change is needed.

This review does not alter model semantics, kernel contracts, shared pins or
historical target results. Existing model evidence is the starting point for
policy alignment; a real control interface remains contract-gated. No external
source is needed to establish these repository-local differences.
