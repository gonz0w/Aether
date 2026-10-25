---
id: BG-033
title: Define bootstrap and supervisor recovery responsibilities
status: captured
created: 2026-09-05
source_type: research-follow-on
area: research
---

## Problem

First service launch and recovery after its failure are not supplied by the current worker fixture.

## Evidence and scope

[BG-025 runtime checklist](../../../docs/research/AETHER-RUNTIME-CONTRACT.md) supplies current evidence, AR question IDs, and experiment boundaries. Aether owns native mechanisms; sys-init owns lifecycle policy. Companion acceptance is not implied. Coordinate BG-020, BG-022 and BG-028 for policy and prototype work.

## Acceptance criteria

- Answer AR-01, AR-02, AR-10 and AR-12 through AR-15 with bootstrap grants, image/configuration identity, ABI/version checks and failure behavior.
- Assign ownership of tasks, backing and terminal records after supervisor death; specify recovery authority or an explicit unsupported outcome for the first experiment.
- Identify required user console/logging, filesystem/device and shutdown services, including how diagnostics work when dependencies fail.
- Locate any future POSIX compatibility layer for process ancestry, signals, descriptors and shell execution without imposing it on the native kernel POC.
- Coordinate BG-003, BG-024, BG-027 and BG-030; record an agreement proposal and unresolved work, distinguishing proposed from accepted companion obligations.

## Result

Pending.

## Lifecycle v1 subset

BG-034 now consumes and tests the fixed-image, single-worker v1 seam; see [report](../../../docs/LIFECYCLE-V1.md). This story remains open for the general contract and unsupported recovery/event/runtime facilities.

## Native integration update

[Ownership review](../../../docs/OWNERSHIP-REVIEW.md) now includes retained two-slot C supervision and AENFD001 byte-stream evidence beyond lifecycle v1. BG-055 refreshes those existing suites against current inputs; historical receipts do not establish current-tree execution. Native service deadlines and supervisor recovery remain open. BG-032/BG-040 own subsequent explicit-stop/fault stream-closure cases under existing contracts.

## ABI-6 consumer acceptance

[Decision 0017](../../../docs/decisions/0017-native-init-consumer.md) and
[consumer evidence](../../../docs/NATIVE-INIT.md) now consume the Aether SI-01–03
producer with independently authored sys-init policy. Seven target cases pass.
Accept the bounded interrupt-time registered-wait, existing helper-channel and
fail-closed whole-domain shutdown scope; do not call it calibrated timing,
arbitrary delegation or supervisor restart. Broader story acceptance stays partial.
Next local work is ABI-6 evidence audit and a bounded adapter workload; the older
blanket producer-input wait is superseded for this seam.

## Control effect acknowledgment follow-on — 2026-09-06

[Control authority A05/A06](../../../docs/specs/CONTROL-AUTHORITY-V0.md) requires
separate effect transfer, confirmed execution, terminal observation and reclaim.
Define bounded obligation identities and matching acknowledgment; test stale/
duplicate results, failure before/after invocation, driver death and failed
cleanup. Retain unknown ownership on lost execution result. Current producer
fatal/fail-closed profiles do not establish replacement-driver recovery. OQ-022
tracks this question; no persistent ledger or acknowledgment API is selected yet.

## Isolated effect-ledger result — 2026-09-06

[Decision 0036](../../../docs/decisions/0036-effect-acknowledgment-model.md) tests
bounded effect identity, issued/unknown/terminal acknowledgment, retention and
driver-loss closure. This does not assign a recovery owner or confirm native
execution. Next coordinate BG-050's pre-dispatch capacity gate and producer-result
mapping; unknown reconciliation and replacement-driver authority remain unresolved.

## Submission accounting follow-through — 2026-09-06

Decision 0037 integrates ledger admission with an opt-in delivery class. Next
specify observation-generated obligations and producer-result mapping, including
unknown acknowledgment/reconciliation and capacity under cleanup/cancellation.
This is sequential model accounting, not replacement-driver recovery or native
execution. Stream/authority composition remains unimplemented.

## Event accounting boundary — 2026-09-06

Decision 0038 characterizes twelve-effect cuts, repeated force occurrences and
background effects without a related active operation. Six tests retain these
integration constraints. BG-057 is captured for a separate event journal with
whole-cut capacity and lifecycle cause. BG-032/BG-033 retain exact native result
mapping and recovery. The submission-only ledger and native code are unchanged.

## Event journal checkpoint — 2026-09-06

Decision 0039 implements an isolated twenty-credit occurrence journal. Supplied
cause survives operation-history eviction; repeated force occurrences are distinct.
BG-057 is active for lifecycle-owned cause and Model.batch admission, with retained
observations on denial and unknown-progress policy. Native mapping remains open.

## Journal-owned lifecycle checkpoint — 2026-09-06

Decision 0040 integrates a separate JournalRuntime with existing Model hooks:
retained per-service cause, whole-cut reservation before mutation and token-only
transfer. Ten tests cover bounds, history-independent cause, restart/retry and
failure ownership. Capacity-denied observations remain caller-owned and unchanged.
Unknown currently blocks terminal observations too. BG-057 remains active with
BG-033 for bounded unknown-observation/reconciliation policy before liveness or
recovery claims; control composition and BG-032 producer mapping remain separate.

## Observation inbox checkpoint — 2026-09-06

Decision 0041 supplies four-cut trusted retention, FIFO whole-cut application and
fail-closed overflow without dropping accepted data. Unknown is not reconciled;
commands cannot pass queued observations. Nine tests and a capacity omission
control cover the bounds and failures. BG-033/BG-032 next review exact producer
reconciliation evidence; BG-057 remains active for that policy and control
composition. No native queue, progress guarantee or replacement owner is claimed.

## Reconciliation evidence review — 2026-09-06

Decision 0042 freezes fifteen selected sources and distinguishes confirmed ABI-6
returns from terminal/wait observations and command reply uncertainty. The reviewed
profiles do not implement general lost-result or replacement-owner reconciliation.
BG-058 is captured for qualified confirmed-result mapping and rejection tests;
BG-033/BG-032 retain actual recovery and fresh native consumer witnesses. No journal
unknown transition, shared pin, native source or sibling backlog was changed.

## Confirmed-result qualifier checkpoint — 2026-09-06

Decision 0043 adds pure owner/profile/target/issued-token qualification and exact
selected ABI-6 return classification. Eight cases plus an issued-state omission
control pass without journal or lifecycle mutation. BG-058 is active for serialized
application, separate terminal/cleanup observations and native target acceptance.
Unknown recovery and native force mapping remain unsupported.

## Result application checkpoint — 2026-09-06

Decision 0044 applies qualified returns under a trusted serialized guard, requiring
the exact retained call and fresh qualification. Eight tests plus a binding
omission control cover stale results, reentry and before/after-ack failures.
Acknowledgment never synthesizes observations; uncertain apply closes the owner.
BG-058 retains exact native terminal/cleanup mapping, target bookkeeping and
fresh witnesses. Existing bypass APIs/threads are outside this trusted experiment;
unknown recovery and native force remain unsupported.

## Native target registry checkpoint — 2026-09-06

Decision 0045 adds two-slot trusted target reservation, independent generations,
confirmed launch/reclaim adoption and native terminal-kind/detail projection.
Nine tests and a generation omission control pass. Unknown reservations remain
held; retirement requires separately observed model cleanup. BG-058 remains active
for actual fact-to-lifecycle mapping, stopped-kind and rejected-launch cleanup,
plus fresh native witnesses. The first selected fault is #UD; broader fault vectors,
native force and unknown recovery remain unsupported.
