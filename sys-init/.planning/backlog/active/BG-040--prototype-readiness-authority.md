---
id: BG-040
title: Prototype readiness transport and launch authority
status: active
created: 2026-09-05
source_type: research-follow-on
area: research
---

## Problem and acceptance criteria

Compare newline and bounded versioned frames on a POSIX host. Define per-generation channel ownership, helper delegation, parser bounds, timeout and cancellation behavior. Execute the transport race cases in the readiness handoff, including inherited writers, early messages, stale generations and terminal/deadline races. Record platform assumptions and an experiment decision before implementation. Native transport remains dependent on BG-032.

## Evidence

[BG-007/BG-022 readiness handoff](../../../docs/research/READINESS-AND-HEALTH.md) supplies alternatives and the required scenario matrix. Research completion does not select a production architecture.

## Readiness/ownership follow-up

[Decision 0003](../../../docs/decisions/0003-host-readiness-fixture.md) and the [host follow-up](../../../docs/HOST-RUNTIME.md) establish the trusted first-frame/direct-parent subset. Twenty macOS host cases pass, including six new framing/descriptor/exit-order cases; an isolated old-parser negative control detects both corrected bugs. This story remains open for its wider cross-host, parent-death, helper/native ownership and contract acceptance scope.

Native decision 0008 confirms that historical readiness remains set after explicit terminal stop; it must not be treated as current readiness. Empty-stream closure/stale-handle/normal-replacement cases pass using a new sys-init-owned policy client. Nonempty-output and actual worker-fault closure remain BG-032/BG-040 follow-ons.

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

## Current host acceptance disposition

[Decision 0013](../../../docs/decisions/0013-host-readiness-acceptance.md) and
[acceptance matrix](../../../docs/HOST-READINESS-ACCEPTANCE.md) reconcile the older
framing criterion: retain the existing first frame for this bounded fixture;
no versioned parser or production protocol selection is claimed. Four new host
test families cover registration, exact deadline, stop and old-writer/replacement
cuts; full checks pass with 42 host tests. The isolated deadline mutation fails
only at the intended boundary. This story is active/partial. Repeated/flooding
writers, joint helper/main-exit behavior and cross-host acceptance remain open.

## Writer/helper acceptance

[Decision 0014](../../../docs/decisions/0014-host-readiness-writers.md) now tests
repeat-write EPIPE, bounded junk pressure and late notification from a real
forked helper after main exit. All 45 host tests pass; a terminal-priority mutant
fails the intended helper test. Orphan release/closed writer is witnessed,
external reaping is not. BG-040 remains partial for diagnostic distinctions,
cross-host and production acceptance. Next distinguish closed/incomplete channel
from malformed-prefix diagnostics while preserving the first-frame contract.

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

[Decision 0020](../../../docs/decisions/0020-native-provider-return.md) binds the
same generation/worker/channel evidence to an actual dependent launch, then
observes provider-originated normal return and invalidates the dependent. Early
reader closure cannot admit a dependent; old evidence cannot admit replacement.
Seventeen target cases and full checks pass with pinned worker and consumer
inputs. Silent/malformed readiness is covered by the next checkpoint. Production framing, exception
handling and general graph policy remain outside this result; story stays partial.

## Readiness rejection — 2026-09-05

[Decision 0021](../../../docs/decisions/0021-native-readiness-failures.md) passes
silent deadline and malformed-frame rejection at distinct target results 920/921.
All 19 cases and full development checks pass; seventeen prior raw clients remain
unchanged. Next specify and demonstrate stopping/reclaiming a rejected provider,
retrying in a fresh generation, and admitting a dependent only from new evidence.
The current negative cases terminate before cleanup, so they do not establish
that follow-on. Production framing and deadlines remain open; story stays partial.

## Cleanup and one retry — 2026-09-05

[Decision 0022](../../../docs/decisions/0022-native-readiness-retry.md) passes
silent/malformed rejection, stop/close/reclaim before slot reuse, and fresh-frame
admission before a real dependent launch. Both positive paths reclaim three
workers; missing cleanup or fresh evidence rejects at 927/929 with one reclaim.
All 23 target cases pass; nineteen older clients remain byte-identical.

Next define a finite retry budget and exhausted outcome: repeated failed attempts
must each clean up, stop launching at the bound and never launch a dependent.
Specify exact success/rejection controls and resource budgets before implementing.
No general backoff, production clock, graph or recovery claim; this story stays
partial. The scoped retry witness does not resolve those remaining contracts.

## Finite attempt exhaustion — 2026-09-06

[Decision 0023](../../../docs/decisions/0023-native-retry-budget.md) passes three
silent/malformed attempts with complete cleanup and denied fourth admission.
Extra-admission and early-termination controls reject at exact 931/934 contexts.
All 27 cases pass; twenty-three older supervisors remain byte-identical.

Next map the existing model T16 stop-cancels-retry rule into native policy:
local cancellation between attempts must close admission, preserve cleanup and
prevent late readiness from reviving the activation. Specify the observation cut,
identity and positive/negative oracle before coding. A real operator control
transport, production clocks/backoff and broader graphs remain separate contracts.
The initial local-intent fixture has no known kernel blocker; story stays partial.

## Local retry cancellation and policy review — 2026-09-06

[Decision 0024](../../../docs/decisions/0024-native-retry-cancellation.md) passes
cancellation after rejected-readiness cleanup and before collected-frame admission.
The two controls reject at 936/937 with one/zero reclaims; all 31 cases pass and
twenty-seven previous raw supervisors are unchanged. No real control transport.

[Policy review](../../../docs/NATIVE-POLICY-REVIEW.md) identifies the next concrete
alignment: R-07 keeps an admitted consumer running after provider loss; earlier
native fixtures intentionally stop it. Add a native R-07 witness with an
incorrect-auto-stop control, then explicit consumer stop and complete cleanup.
Coordinate BG-042 for dependency-loss observation and BG-050 for operation IDs,
intent cuts, duplicate requests and late launch ownership before real transport.
Production clocks/backoff and broader framing remain open; story stays partial.

## Model-aligned dependency loss — 2026-09-06

[Decision 0025](../../../docs/decisions/0025-native-dependency-loss.md) passes
provider stop and normal return with the admitted dependent retained live and new
admission blocked. Loss remains attached to the old binding; fresh replacement
evidence permits its new binding. Incorrect automatic stop and admission controls
reject at 940/941 with zero reclaims. All 35 cases pass; thirty-one older raw
supervisors remain unchanged. BG-042's broader evidence/graph criteria remain open.

Next move to BG-050's minimal operation/control specification using existing
R-11–R-16 model behavior. Define identity, joins/conflicts, cancellation cut and
late launch ownership before transport. This local specification work is unblocked;
real native control delivery needs an explicit producer/consumer contract. No
operator status stream, persistent enablement or complete runtime conformance.
