# Native terminal evidence v0

Accepted local experimental contract, 2026-09-06; decision 0075, BG-058 ND-02.
Specified behavior and future tests, not an implemented observer. Preserve the
[binding](NATIVE-DRIVER-BINDING-V0.md) and [receipt](NATIVE-RECEIPT-OWNERSHIP-V0.md)
contracts. This is a private trusted-owner boundary, not a public wire format,
POSIX wait status or a new kernel interface.

## Frozen source findings

The [reviewed producer](../evidence/native-terminal-contract-2026-09-06/source/Aether/kernel/arch/x86_64/native_c.zig)
is byte-identical to the producer source in decision 0074's executed witness.
The fixed profile is aether-init-abi6, producer summary
`3a399587b34010302d25838d9f8e1cc73e2b93bec1ac673321326494bde1f155`.
Its `control`, `waitOperation`, `finish`, `lookup` and `rotate` functions establish:

| Read or transition | Meaning in this producer |
| --- | --- |
| 0x20001, RDI=actual worker handle | RAX=0 while live, otherwise detail+1; R8=terminal kind; RDX=historical readiness; RCX=yield count |
| 0x25001, RDI=0xe001, RSI=actual worker handle | RAX=revision; RDX=0 while live, otherwise detail+1; R8=historical readiness |
| Normal finish | Kind 1, exit detail masked to 8 bits under this launch profile; terminal transition increments revision |
| Fault finish | Kind 2, detail=128+exception vector; the selected invalid-opcode vector 6 gives detail 134/result 135 |
| Explicit stop | Kind 3, detail 143/result 144, revision increment only if previously nonterminal; stopping an already terminal target preserves its original terminal kind |
| Handle lookup/reclaim | Lookup requires admitted state and full generation-encoded handle; reclaim retires admission. A stale lookup returns -9, not a receipt for a reclaim occurrence |

Control status is restricted to the supervisor. Observation additionally checks
the observer capability value and reserved argument fields. Names, expected handle
numbers and token bytes do not confer native authority. The current Adapter trap
already captures RAX/RDX/R8; a future distinctly named worker-status method can
use it without changing the unsafe primitive or existing wait `status` method.
Yield count is not needed for this contract and is not part of terminal evidence.

The [current Adapter](../../prototypes/native-supervisor/adapter.rs) exposes only
revision, encoded terminal result and historical readiness through observe. The
[model registry](../../prototypes/runtime_model/target_registry.py) qualifies kind
and result together, accepting kind 1/results 1–256, kind 2/result 135 and kind 3/
result 144. Its replies are synthetic and it does not implement native multi-read
coherence. Preserve its narrow fault profile: other fault vectors may be valid
producer results but are unsupported by this initial consumer mapping.

The inspected scheduler never runs a terminal worker. Only that worker can publish
readiness, and repeated stop does not rewrite a terminal result. Thus terminal
fields and revision are stable while this single owner retains the target without
reclaim. This is a source-based invariant for the pinned BSP profile, not an atomic
multi-read ABI or a guarantee for future producers, SMP or replacement owners.

## Identity, ownership and read sequence

One trusted live owner retains at most two attempts and their actual admitted
workers/readers. Require the exact original full launch token, fixed context and
matching actual Worker with applied launch receipt before any read. Deny wrong
owner, unknown/retired index, unapplied launch or wrong target without a syscall
or replacement of pending evidence. The caller cannot substitute an expected
numeric target for an actual retained worker wrapper.

Use one serialized sampling position across attempts. Each sample has space for
at most two observations and one worker-status result, including received native
errors or a separate local failure cause. Reserve it before reading; no allocation,
unbounded retry loop or concurrent local stop/reclaim/application is permitted.
This position also blocks new conflicting driver effects while sampling. Preserve
at most one qualified terminal fact per attempt until a named consumer accepts it;
ND-03 supplies that consumer and retirement, not this contract.

1. Read observation O1 on the retained actual worker. Preserve its result first.
   A valid live result (terminal=0) yields no terminal fact and releases only the
   sampling position. It does not say the worker remains live after the read or
   establish readiness, completion, cleanup or a stop outcome.
2. If O1 is terminal, require a positive decoded revision, retain the worker and
   read status S for the same handle.
   Capture its decoded signed result, kind and historical readiness before any
   interpretation. Never discard prior O1 on failure.
3. Read O2 on the same handle. Require O1 and O2 to agree in revision, nonzero
   encoded terminal result and historical readiness. Require S.result to equal
   that encoded result and S.readiness to agree with both observations. Validate
   boolean encodings and accepted kind/result pairs before constructing a fact.
4. Record the original owner/profile/producer/token, actual target, agreed revision,
   exact kind, decoded detail and historical readiness. The fact is read-only
   evidence; it does not consume the launch token or acknowledge stop/reclaim.

An O1 live result costs one read; a candidate terminal sample costs three reads.
No automatic resampling after an inconsistent candidate. The second observation
is a bounded consistency check; it cannot create snapshot atomicity for a producer
whose terminal state may mutate. The pinned terminal-stability invariant remains
required. No native lifecycle mutation or handle release may interleave locally.

## Kind mapping and failure rules

| Kind/result pair | Qualified meaning |
| --- | --- |
| 1, 1–256 | Normal exit, detail=result−1 (0–255) |
| 2, 135 | Selected invalid-opcode fault, detail 134 |
| 3, 144 | Native explicit-stop terminal state, detail 143; not a POSIX signal or proof which stop occurrence caused it |

For example, (1,135) and (2,135) have equal result and different meanings; so do
(1,144) and (3,144). Never derive kind from 134/143 or 135/144 alone. A normal exit
with nonzero detail remains a normal terminal kind; later policy decides whether
it is successful. Historical readiness does not imply a terminal worker is ready.

Negative native results keep operation/errno identity and close this bounded
sampling owner with partial receipts and resources retained. Invalid boolean,
unsupported pair, contradictory live status after terminal O1, changed revision,
wrong result/readiness or local interruption after sampling begins likewise close
admission, preserving the observed data and a local cause without invented errno.
Read failure is not evidence of target death, reclaim or unknown-effect execution.
This slice does not translate any sampling error into lifecycle policy.

If a qualified fact already occupies the attempt's pending position, an identical
fully bound fact is idempotent; it must not append another event or perform effects.
A conflicting candidate retains the first fact plus the bounded conflicting sample
and closes admission. An untrusted mismatched request is preflight denial, not a
reason to replace the first fact. Consumer acceptance and late/retired delivery
must be specified by ND-03 before clearing/replenishing this history.

Interruption retains only reads actually received. Closing the owner never supplies
a missing S or O2. No actual never-returning syscall is simulated by discarding its
return; a synthetic interruption schedule must be labelled as such. Unknown owner
recovery remains BG-033. Fixture disposal of positively known resources is not an
implementation of this recovery path.

## Acceptance plan

These are future cases, with exact native assertions to be recorded before their
implementation run. Model/local injected samples cannot qualify an actual producer
kind or a real interrupt schedule. Preserve all previous native case oracles.

| ID | Required oracle |
| --- | --- |
| NT-01 | Consume normal exit 134 versus invalid-opcode fault 134, and normal exit 143 versus explicit stop 143; equal encoded results retain distinct kinds. Negative control omits kind and must fail the distinction assertion |
| NT-02 | O1/S/O2 reads of the same retained terminal worker agree; a live O1 produces no terminal fact. Capture actual native kind/result/readiness/revision without inferring kind from numbers |
| NT-03 | Wrong owner/token/worker, unapplied launch and reserved sampling position deny before reads; stale actual handle after explicit fixture reclaim produces native -9 without a replacement fact or invented reclaim acknowledgment |
| NT-04 | Inject invalid kind/result, boolean, result mismatch, changed revision and contradictory readiness into retained samples; preserve original data/resources, close and emit no fact. Label each injected reply separately from producer return coverage |
| NT-05 | Synthetic interruption after O1 or S retains partial evidence with no retry/application; no fabricated terminal fact or cleanup. Returned resource authority remains owned |
| NT-06 | Same fully bound terminal fact is idempotent; conflicting candidate and equal-generation cross-service substitution cannot replace prior pending history. Omission control detects overwrite |
| NT-07 | Two-service sampling capacity and pending-fact bounds deny before additional reads/effects; consumer retirement/replenishment remains ND-03 |

First implement NT-01–02 as small producer-status/observation probes with explicit
numeric collisions. A worker fixture may need new normal-exit modes; retain its
source/build pin and new consuming witness. Then integrate the qualified fact with
binding identity, bounded retention and NT-03–07. A standalone status reader is not
full ND-02 integration. Split probes to fit the 4 KiB experiment limit; do not alter
kernel evidence, widen fault acceptance or relax an oracle to fit the image.

## Alternatives and standards scope

Inferring kind from an integer contradicts the producer. A single status read has
kind but no observation revision. An O1/S/O2 sample gives an inspectable consistency
check under retained terminal stability; no kernel API change is required for the
first slice. A new atomic snapshot ABI would require separate producer/consumer
coordination and is not justified by this fixed single-owner experiment.

Foundations O-01/O-03/O-04, I-01/I-03–06 and E-01–08 apply under
[STANDARDS](../STANDARDS.md); Distribution identity/recovery limits remain intact.
Shared standards stay in Aether-standards. No pin, existing output, error contract,
unsafe primitive, dependency or external API changes. This does not select a
POSIX/BSD/illumos/Linux wait translation or production language. ND-01 gaps remain
in the [acceptance review](../research/NATIVE-BINDING-ACCEPTANCE-REVIEW.md); ND-03–05
and BG-033 remain open. No exception or independent sign-off is claimed.

## Standalone implementation — decision 0076

[Decision 0076](../decisions/0076-native-terminal-collisions.md) consumes actual
normal/fault and normal/stop numeric collisions, a live first observation and
three-read terminal coherence, with a kind omission control. The native run also
covers all prior base cases and existing optional-worker modes using the rebuilt
worker. This qualifies a standalone NT-01–02 slice. It does not implement retained
binding identity, partial failure history, conflicting pending facts or journal
acceptance. NT-03 sampling reservation/identity is next; NT-04 must separate local
Adapter guard origin and retain raw failure evidence before stronger claims.
NT-05–07 and remaining NB/ND/recovery work stay open. Earlier future-work wording
records the original design checkpoint.

## Bounded sampling implementation — decision 0077

[Decision 0077](../decisions/0077-native-bound-sampling.md) adds actual sampling
behind retained owner/token/Worker/phase checks and a single Driver reservation.
It retains a terminal fact or the tested first-read native stale error. Fixtures
seed admitted state from actual handles; full Driver launch-to-sampling composition
remains unqualified under BG-058/ND-02. The local one-sample-per-attempt limit is
stricter than ongoing polling: live releases the position but not sample budget.
NT-04 raw prefixes and native/local error-origin separation are next. NT-05–07,
full journal consumption/retirement and remaining NB/ND/recovery remain open.
Earlier checkpoint next-work wording is historical.

## Synthetic receipt qualification — decision 0078

[Decision 0078](../decisions/0078-terminal-receipt-validator.md) implements a pure
Rust accumulator for three raw signed-RAX/RDX/R8 returns. It preserves each return
before interpreting it, distinguishes native operation/errno from a local enum
cause, and seals live/terminal/failed samples against overwrites. Synthetic malformed
booleans, pair/coherence failures, native errors at each position and interruption
prefixes are host-tested with retention/origin omission controls. Received-count
tracks actual supplied returns, not attempted syscalls. Local boolean validation
occurs on receipt; terminal O1 requires positive revision; pair/coherence validation
occurs after O2. Native negative RAX takes precedence over auxiliary-field validation.

The module owns no Worker, token or resources and is not linked into the current
native consumer. It is an NT-04 logic slice with synthetic NT-05 schedules, not
native raw-capture, resource-retention or full NT-04/05 completion. Next: capture
raw returns in Adapter and retain this accumulator behind Driver identity and
reservation checks, then consume a fresh target witness. Current native boolean
errors still use the old Adapter shape until that migration. NT-06/07, full launch
composition, journal/retirement and recovery remain open.

## Actual raw capture — decision 0079

[Decision 0079](../decisions/0079-native-raw-sample-retention.md) consumes actual
O1/S/O2 register triples with the validator. Native stale errors at all three
positions preserve successful prefixes; a native prefix-omission control rejects.
These are standalone fixture probes with deliberate known reclaim/replacement
between reads, not production concurrency or lost-reply recovery. Binding still
uses the previous decoded sampler: combined raw-history probes exceeded the fixed
4 KiB image limit and their snapshots are retained. A size-bounded composition
strategy is next; no old oracle or image limit was relaxed. Native malformed
injections, NT-05–07, journal/retirement and remaining NB/ND/recovery remain open.

## Build feasibility — decision 0080

[The size study](../research/NATIVE-COMPOSITION-SIZE.md) finds a retained-session
candidate that fits all 120 compiler configurations at 4048 bytes maximum with
recorded optimization/inlining/path mapping. Its host validator tests pass, but
native execution and profile/default compatibility acceptance remain pending.
The current native driver still uses decoded sampling. BG-058 next qualifies the
exact candidate on the pinned producer with all 125 previous case oracles and two
bound prefix cases. Seeded admission does not complete full launch composition;
NT-04 malformed native injections, NT-05–07 and journal/recovery remain open.

## Retained session qualification — decision 0081

Decision 0081 passes all 127 native cases under retained-sampling-v1, including
all 125 prior oracles and two bound stale-prefix cases. The exact size-study
candidate now composes Driver with fixed raw-receipt storage through an exclusive
Sampling borrow. S/O2 native -9 preserves successful prefixes, original diagnostic
target, closed admission and pending state; positive probes finish 100/3.
All 183 frozen inputs unchanged; largest image 4048 bytes (48 bytes headroom).
All 121 comparable native images match the study bytes; six cases omitted by the study
have fresh native coverage and no claimed study baseline.

This qualifies bounded retained sampling with fixture-seeded admission. It does
not qualify full launch composition, malformed native injection, NT-05–07,
journal/history retirement or recovery. Next: NT-04 labelled malformed-reply
injection through the bound session with retained resources and exact local causes;
then NT-05 interruption and NT-06/07 pending-history bounds. BG-057 owns consumer
retirement and BG-033 retains unknown-owner recovery.

The harness now uses the explicit local retained-sampling-v1 build profile.
Prior future-work wording above belongs to its original checkpoints. Invariant
assertion 1042 applies to the new session paths; native/local distinction stays
in Sample::state and raw receipts. Lifetime after the borrowed session and a
named history consumer remain pending obligations.

## Bound malformed sampling — decision 0082

Decision 0082 passes 136 native cases: all 127 prior oracles plus six labelled
malformed-reply probes and three omission controls. Each probe omits exactly one
selected S/O2 syscall and injects a synthetic raw triple; other received samples
are real. Exact data and local causes survive while Driver closes admission and
retains worker, reader, token, pending index and generation, with no terminal fact
or invented native errno. Further sampling denies without another read.

Six positives finish 100/reclaimed=3 after asserted retention and known fixture
cleanup. Skip closure, forget reader and invent errno controls reach 1043/0,
1044/0 and 1045/0. All 183 frozen inputs unchanged; 90 of 127 previous images
are identical. Largest image remains 4048 bytes; new images fit 3760–3872 bytes.
The first run's one-reclaim completion was rejected by the kernel and is retained;
the corrected run preserves the required three-reclaim positive oracle.

This is synthetic NT-04 qualification executed in the native fixture, not malformed
kernel output or a lost reply. Admission is still fixture-seeded. Next: NT-05
explicit synthetic interruption after O1/S, retaining resources and partial history
without retry/application; NT-06/07 pending-history bounds, full launch composition,
BG-057 consumer retirement and BG-033 recovery remain open.

## Interrupted sampling — decision 0083

Decision 0083 passes 143 native cases: all 136 prior oracles, empty-sample
interruption denial, two partial interruptions and four omission controls.
The partial probes retain actual O1 or O1/S returns, then invoke a private synthetic
interruption between reads. Local(Interrupted), exact prefix/count, closed admission,
pending identity, worker/reader, full token and generation remain. Repeated interrupt
and read calls deny without additional reads, invented fact/error or application.

Three positives finish 100/reclaimed=3 after retention checks and known fixture
cleanup. Omission controls reach 1046/0 (closure), 1047/0 (prefix), 1048/0 (fact)
and 1049/0 (reader). All 183 frozen inputs unchanged; 90 of 136 previous
images match byte-for-byte. Largest image remains 4048 bytes; partial interruption
probes are 3904/3952 bytes. Four earlier size revisions are retained, including
failed strict links; the fifth keeps all assertions by separating empty denial
and sharing the full-prefix predicate before and after denied calls.

This is synthetic NT-05 disposition in a native fixture, not syscall cancellation,
asynchronous delivery or lost-return recovery. Admission remains fixture-seeded.
Next: define/qualify NT-06/07 pending-history identity, conflict and capacity rules
with BG-057 consumer retirement. Full launch composition, additional NT-04 O1
injections and BG-033 unknown-owner recovery remain open.


## Pending-history follow-through — decision 0084

[Native pending history v0](NATIVE-PENDING-HISTORY-V0.md) supplies the local
NT-06/07 identity, comparison and capacity design (PH-01–06), with retirement
reserved to BG-057 PH-07. It is not yet implemented or target-qualified. The
current native checkpoint remains decision 0083's 143 cases.
