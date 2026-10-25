# Research guide

Updated: 2026-09-05. The [completed boundary handoff](research/BOUNDARY-HANDOFF.md) is the current synthesis, with rechecked primary-source passages, corrections, access limitations, and follow-on work. Other entries below preserve earlier research.

| Topic | Evidence |
| --- | --- |
| Executed deterministic policy model | [BG-053 results](RUNTIME-MODEL.md) and source hashes |
| Test strategy and semantic review | [BG-017 matrix](specs/TEST-STRATEGY.md), [BG-052 decision](decisions/0002-runtime-model-profile.md) |
| Operator commands and initial runtime semantics | [BG-016 comparison](research/OPERATOR-INTERFACE.md), [BG-023 draft](specs/RUNTIME-V0.md) |
| Security, resource scopes and device/event integration | [BG-009/BG-015 handoff](research/SECURITY-RESOURCES-AND-EVENTS.md) |
| Shutdown, bounded logging and failure diagnostics | [BG-024/BG-008 handoff](research/SHUTDOWN-AND-DIAGNOSTICS.md) |
| Readiness evidence, authority, health and race scenarios | [BG-007/BG-022 handoff](research/READINESS-AND-HEALTH.md) |
| Boot stages, profiles, layout and target implementation gates | [BG-003/BG-014 handoff](research/BOOT-AND-LAYOUT.md) |
| Package artifacts, enablement and lifecycle coordination | [Current BG-027 proposal](research/PACKAGE-SERVICE-CONTRACT.md) with source manifest |
| Aether native runtime and integration gaps | [Current BG-025 checklist](research/AETHER-RUNTIME-CONTRACT.md) with source manifest |
| Original goals and DO IDs | [Intent](archive/2026-09-05-planning-reset/.planning/INTENT.md) |
| Initial survey, PID 1, service/package/portability contracts | [Research Intake closeout](archive/2026-09-05-planning-reset/.planning/milestones/research-intake-v0-CLOSEOUT.md) and its referenced phase artifacts |
| Supervision, ordering, readiness, failure propagation | [Runtime research summary](archive/2026-09-05-planning-reset/.planning/research/SUMMARY.md) and adjacent runtime-semantics notes |
| Shell and compiled component tradeoffs | [Boundary evidence](archive/2026-09-05-planning-reset/.planning/phases/phase-1-prior-art-and-boundary-evidence/RESEARCH.md) |
| Proposed layer responsibilities | [Layer matrix](archive/2026-09-05-planning-reset/.planning/phases/phase-2-layer-classification-testing-and-recovery/specs/contracts/layer-boundary-contract.md) |
| Failure and recovery scenarios | [Testing scenarios](archive/2026-09-05-planning-reset/.planning/phases/phase-2-layer-classification-testing-and-recovery/specs/scenarios/layer-testing-and-recovery-scenarios.md) |
| Unfinished synthesis | [Phase 3 skeleton](archive/2026-09-05-planning-reset/.planning/phases/phase-3-decision-handoff-and-follow-on-backlog/SKELETON.md), completed through BG-026; see the current handoff |

Useful directions to investigate include direct-parent supervision, bounded restart policy, separating ordering from readiness, validating metadata before activation, and keeping recovery inspectable. These are earlier research recommendations, not accepted implementation choices.

BG-026 revisited and replaced categorical labels such as `tiny-C-required`; its current synthesis takes precedence over those archived classifications. The distinction between precise runtime semantics and convenient shell policy needs evidence for each responsibility; an old label alone does not establish the required language. Compare alternatives against current Aether task/capability semantics and a clearly stated POSIX host baseline.

For new research, cite primary manuals or source, record the observation date, compare relevant prior art only as needed for the Aether requirement, state Aether gaps, and link unresolved questions to backlog items before completion. Recheck external citations before basing implementation decisions on them.

## Unknown effect evidence — 2026-09-06

[Producer reconciliation review](research/UNKNOWN-EFFECT-RECONCILIATION.md) separates
confirmed ABI-6 execution/cleanup, retained worker/wait facts and newer command
reply-failure containment. Decision 0042 keeps unknown outcomes unresolved and
captures BG-058 for confirmed-result qualification. Frozen sources and concurrent
producer-document changes are retained; no new native recovery is claimed.
