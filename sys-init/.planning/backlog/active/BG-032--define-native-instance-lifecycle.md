---
id: BG-032
title: Define native instance lifecycle and event contract
status: active
created: 2026-09-05
source_type: research-follow-on
area: research
---

## Problem

AR-03 through AR-09 and AR-11 need a general native contract beyond M2 fixture results.

## Evidence and scope

[BG-025 runtime checklist](../../../docs/research/AETHER-RUNTIME-CONTRACT.md) supplies current evidence, AR question IDs, and experiment boundaries. Aether owns native mechanisms; sys-init owns lifecycle policy. Companion acceptance is not implied. Coordinate BG-020, BG-022 and BG-028 for policy and prototype work.

## Acceptance criteria

- Specify service names versus instance identity and holder-scoped authority, including stale references and exhaustion.
- Define terminal reason/status lifetime, observation and acknowledgment, destruction ordering, and whether multiple observers are allowed.
- Specify notification or bounded polling, deadline/clock semantics, cancellation, stop completion, and explicit failures; distinguish graceful requests from forced destruction.
- Define dependency grant installation/replacement and instance-bound readiness authority without interpreting payload bytes as capabilities.
- Record what is local-only, what requires cross-core cleanup, and what remains unsupported. Propose contract tests, then capture unresolved work before completion.

## Result

Partial: bounded lifecycle, supervision and I/O contracts have target witnesses; general clocks, ownership/recovery and broader runtime contracts remain open.

## Lifecycle v1 subset

BG-034 now consumes and tests the fixed-image, single-worker v1 seam; see [report](../../../docs/LIFECYCLE-V1.md). This story remains open for the general contract and unsupported recovery/event/runtime facilities.

## Native integration update

[Ownership review](../../../docs/OWNERSHIP-REVIEW.md) now includes retained two-slot C supervision and AENFD001 byte-stream evidence beyond lifecycle v1. BG-055 refreshes those existing suites against current inputs; historical receipts do not establish current-tree execution. Native service deadlines and supervisor recovery remain open. BG-032/BG-040 own subsequent explicit-stop/fault stream-closure cases under existing contracts.

## Explicit-stop I/O slice

[Decision 0008](../../../docs/decisions/0008-native-io-stop.md) and [four target cases](../../../docs/evidence/native-io-stop-2026-09-05/README.md) verify live-ready stop, historical terminal kind/detail, EOF on empty outputs, rejected input, stale handles and a normal replacement. New policy/harness code lives only in sys-init; unchanged companion inputs are frozen. Wrong-detail and omitted-zeroing controls reject, original I/O still passes, legacy supervision variants remain byte-identical. Next define a sys-init-owned worker probe for nonempty retained output and actual fault closure, reusing the SDK/ABI; those outcomes are not claimed yet.

## Retained-output slice

[Decision 0009](../../../docs/decisions/0009-native-retained-output.md) and
[four new native cases](../../../docs/evidence/native-io-retained-2026-09-05/README.md)
verify nonempty stdout/stderr across explicit stop and real UD2, historical
readiness, exact terminal kind/detail, input closure, stale-handle denial and
normal replacements with generation-distinct bytes. Wrong-kind/zeroing controls
reject; the previous stop/I/O suite passes. Worker, policy and tooling live here;
companion SDK/kernel inputs remain unchanged. This story stays partial. Next
specify termination-before-readiness and readiness/terminal ordering cases;
general clocks, event contracts and supervisor recovery remain open.

## Readiness ordering checkpoint

[Decision 0010](../../../docs/decisions/0010-native-readiness-ordering.md) now verifies
five controlled terminal/readiness orderings and two rejection controls, with
normal replacement and unchanged legacy bytes. [Evidence](../../../docs/evidence/native-readiness-2026-09-05/README.md)
retains the target/compatibility and full-check results. BG-032/BG-040 remain
partial. Next audit worker-local readiness authority and specify misuse cases;
delegated notifications, external events, deadlines and recovery require separate
contracts. No companion or shared-pin change was needed.

## Caller-local authority checkpoint

[Decision 0011](../../../docs/decisions/0011-native-readiness-authority.md) and
[evidence](../../../docs/evidence/native-authority-2026-09-05/README.md) demonstrate
worker control denial, supervisor local-notification/query denial and duplicate
local notification, with two semantic controls and unchanged older bytes.
BG-032/BG-040 stay partial. Next specify a live-peer noninterference fixture;
guessed values do not prove behavior with known peer handles. Delegation, external
events, deadlines and recovery remain separately owned contract work.

## Live-peer checkpoint

[Decision 0012](../../../docs/decisions/0012-native-peer-readiness.md) and
[evidence](../../../docs/evidence/native-peer-2026-09-05/README.md) verify known-live-peer
control denial, caller-local readiness and survivor progress in both slot orders.
Wrong-readiness and zeroing controls reject; prior authority cases pass.
BG-032/BG-040 remain partial. Next consolidate coverage and remaining native
contract gaps; delegation, event/deadline semantics, SMP and recovery remain
outside the frozen experiment. No companion or shared-pin change was needed.

## Coverage consolidation

[Current coverage and gate matrix](../../../docs/NATIVE-COVERAGE.md) separates consumed
native evidence from local follow-ons and general kernel contracts. Five bundles
are now audited offline in check-all; this does not rerun Aether. BG-032/BG-040
remain partial. Next reconcile BG-040 host acceptance (including its framing
comparison requirement) with decision 0003 and the existing tests before choosing
new code. Shared standards and historical manifests remain unchanged.

## Local acceptance and external gates

[Diagnostic/Linux evidence](../../../docs/evidence/host-diagnostics-linux-2026-09-05/README.md)
passes 48 host tests and the full offline runner on macOS and Linux using matching
recorded source hashes. Stable framing-failure diagnostics preserve existing
logs/policy. This supersedes earlier Linux-unavailable notes for this image/run.
Broader story acceptance remains partial. [Required inputs](../../../docs/INTEGRATION-GATES.md)
are BSD/illumos execution, hosted-CI selection, and accepted native clock/wait,
delegation or recovery contracts. Pause this integration workstream at those
gates; no unsupported platform or contract is declared implemented.

## ABI-6 consumer acceptance

[Decision 0017](../../../docs/decisions/0017-native-init-consumer.md) and
[consumer evidence](../../../docs/NATIVE-INIT.md) now consume the Aether SI-01–03
producer with independently authored sys-init policy. Seven target cases pass.
Accept the bounded interrupt-time registered-wait, existing helper-channel and
fail-closed whole-domain shutdown scope; do not call it calibrated timing,
arbitrary delegation or supervisor restart. Broader story acceptance stays partial.
Next local work is ABI-6 evidence audit and a bounded adapter workload; the older
blanket producer-input wait is superseded for this seam.

## ABI-6 audit and adapter boundary — 2026-09-05

[Audit validation](../../../docs/evidence/native-init-audit-2026-09-05/README.md)
adds all seven init outcomes to check-all; full macOS checks pass with 30 harness
tests. [Decision 0018](../../../docs/decisions/0018-native-adapter-boundary.md)
specifies ownership, interrupt-tick deadlines and bounded wait cleanup. Next:
extract the adapter, preserve seven target outcomes, then define exact readiness
bytes/schedules and implement the service/dependent workload. Story remains
partial; elapsed clocks, general delegation/recovery and portability remain open.

## Adapter extraction and sequential-reuse gate — 2026-09-05

[Native adapter checkpoint](../../../docs/NATIVE-ADAPTER.md) accepts the bounded
extraction with nine passing primary target cases and explicit counter/wait
accounting. All 166 frozen inputs remain unchanged; 3,952-byte policy fits the
original page. Full checks pass, including 38 offline recorded native outcomes.
The separately retained no-wait slot-0/reclaim, slot-1/reclaim, slot-0 sequence
fails with a kernel page fault. Owner: Aether mechanism, BG-032 consuming refresh.
Required follow-on: corrected pinned producer, successful minimal ordering probe,
then all adapter controls and the service/dependent workload. Do not silently
broaden from the passing overlapping-worker order. This story remains partial;
no supervisor recovery, elapsed clock or general portability claim.

Aether backlog handoff added at the maintainer's request: [SI-04](../../../../Aether/.planning/ROADMAP.md#si-04--fix-sequential-cross-slot-reuse-after-reclamation).
Acceptance includes both sequential slot orders, preserved protection/zeroing,
new pinned producer evidence, and sys-init's minimal probe plus nine adapter cases.
Queued only; no kernel fix or new consuming run is claimed.

## SI-04 consuming acceptance — 2026-09-05

[Independent refresh](../../../docs/evidence/native-slot-reuse-consumer-2026-09-05/README.md)
passes both sequential orders plus nine unchanged adapter cases against corrected
producer pin `3a399587b34010302d25838d9f8e1cc73e2b93bec1ac673321326494bde1f155`.
All 175 frozen inputs per run are unchanged; full development checks pass. The
local SI-04 gate is lifted. Next specify exact readiness bytes, generation/deadline
binding and failure schedules, then implement decision 0018's provider/dependent
workload. Story remains partial; production clocks, recovery and portability are
not established by these bounded orderings.

## One native dependency — 2026-09-05

[Decision 0019 and witness](../../../docs/NATIVE-SERVICE.md) pass provider readiness,
actual dependent admission, controlled provider stop, dependent stop/cleanup and a
fresh provider generation. Four exact policy controls reject expired/terminal/
stale evidence or omitted dependent stop. Nine prior adapter binaries remain
unchanged. Full checks pass; 176 frozen inputs remain unchanged. This story stays
partial. Follow-ons: specify a controlled spontaneous provider exit/fault after
actual dependent admission, then add the required worker stimulus and pinned
consuming evidence. Silent/malformed readiness, repeated replacement, general
graphs/backoff and production clocks remain distinct unresolved work. No new
kernel blocker was encountered; fixed dependency ordering is not provider RPC.

## Provider-originated normal return — 2026-09-05

[Decision 0020](../../../docs/decisions/0020-native-provider-return.md) passes a
worker return after actual dependent admission. The supervisor closes the
provider's reader, the independently built worker observes EPIPE and returns 17,
and policy observes detail 18 before dependent cleanup/replacement. Early trigger
and omitted cleanup reject at assertions 912/915. All fourteen prior clients are
unchanged. Worker SDK/tool/source inputs and 178 consumer inputs are pinned and
stable; full checks pass. This is deterministic normal return, not a signal or
exception witness. Story remains partial; next add silent/malformed readiness,
then separately specify any worker exception schedule.

## Control caller-binding follow-on — 2026-09-06

[Producer review](../../../docs/research/CONTROL-AUTHORITY-HANDOFF.md) finds private
owner-bound channels and broker connection namespaces already available. Before
native control composition, choose one exact profile/artifact set and demonstrate
foreign/stale endpoint denial, launch rollback, finite slot/channel budgets and
policy revocation ordering. Do not mix ABI-9 capacity with ABI-6 timer or owner-
death guarantees. Initial reconnect may be explicitly unsupported; reassociation
requires a concrete binding contract. No new syscall is requested by this review.

## Reconciliation evidence review — 2026-09-06

Decision 0042 freezes fifteen selected sources and distinguishes confirmed ABI-6
returns from terminal/wait observations and command reply uncertainty. The reviewed
profiles do not implement general lost-result or replacement-owner reconciliation.
BG-058 is captured for qualified confirmed-result mapping and rejection tests;
BG-033/BG-032 retain actual recovery and fresh native consumer witnesses. No journal
unknown transition, shared pin, native source or sibling backlog was changed.
