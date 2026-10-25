# Sustained command profile proposal (UL-059 / UL-081)

2026-09-25 proposal baseline; updated2026-10-03. The maintained client and bounded
native consumer checkpoints below now pass. The original required-check table
records the historical baseline; [current disposition](../../docs/SI07-DISPOSITION.md)
tracks evidence and remaining gaps. Existing AERIO001/two-generation consumers
and historical evidence remain unchanged.

## Private v2 wire contract for owner review

This profile serves the existing sequential runner/bytecount/backend workload.
It is not a public POSIX API, a shared SDK release or general long-running process
service. Aether owns native enforcement; sys-init owns sustained session policy.

- Parent role carrier:160 bytes, magic `AERIO002`; count4, epoch at offset12,
  zero header padding16–31. Four32-byte rows retain exact ordered roles,
  descriptors, rights and capacities from AERIO001. Only the magic and permitted
  epoch domain change. Validate every field before publishing any binding.
- Private epoch: unsigned16-bit nonzero,1 through65535. Keep it conceptually
  separate from native instance/channel identity. In this initial profile, every
  runner/child/backend launch in a cycle must have native generation equal to the
  private cycle epoch; the owner must prove this cohort invariant. If slots have
  diverged, reject the profile rather than truncating, resetting or guessing a map.
  The native generation query must be checked in its full return width before
  narrowing. A future decoupled mapping requires a separate contract.
- References retain their current namespace layout: runner stdout/stderr
  `0x75010000|epoch` / `0x75020000|epoch`, runner file roles
  `0x71000000|epoch` / `0x71010000|epoch`, child bindings
  `0x72000000|epoch` / `0x72010000|epoch`. Bits16–23 belong to the role, never
  to the epoch. These are owner-connection-local selectors, not native grants.
- Child two-binding bootstrap:32 bytes, existing status and two exact triples
  unchanged, but offset28 must equal `0x324f494e` (ASCII `NIO2`). Old bootstrap
  requires zero there. Require the tag; do not auto-detect or fall back to v1.
- Admission/collection receipt: `0x7b000000|epoch`, with bits16–23 zero. This
  new private tag deliberately differs from legacy `0x73000001/2`. It is scoped
  to the authenticated owner connection, not a globally assigned capability type.
  All three reply consumers must use the new domain: admission, collection and
  terminal-to-exit policy. Existing32-byte status/kind/detail/reserved-byte rules
  remain unchanged, including negative-error padding and EAGAIN only as pending
  collection. Invalid inputs leave output unchanged; normal exits require complete
  cleanup and a representable0–255 status. No receipt alone proves ownership.
- Existing startup parser,384-byte request, data-transfer sizes and I/O reply
  framing remain unchanged. Fresh v2 binaries select the entire v2 profile;
  default binaries remain v1. No mixed-profile link or wire fallback is accepted.

## Lifetime and retirement

One fresh native process bootstrap consumes its connection on success or failure.
The owner authenticates endpoint and full native instance before interpreting a
private reference or receipt. A successful child collection consumes that receipt;
repeat collection returns ECHILD, and old references cannot address a new cycle.
Do not release channel/backing state on stop acceptance alone: observe terminal,
finish or abandon pending replies according to owner policy, close all references,
then reclaim. Preserve poisoned-transport and failed-close behavior.

After epoch65535 completes, retire the profile cohort and its namespace. A request
for epoch65536 must fail before any child admission or side effect; it must not
wrap to1 or reuse a selector on a still-live namespace. The kernel's larger native
lifetime is not permission to extend this private wire format. Creating another
cohort is a separately authorized fresh native domain/connection, never a reset
inside the old one. Sys-init owns exhaustion notification/restart policy; this
proposal supplies no new user-visible error number or implicit restart authority.

## Required checks and delivery

| ID | Required witness | Current status |
| --- | --- | --- |
| SUSTAIN-01 | v2 role/bootstrap/admission/collection/terminal-policy boundaries at1,2,3,5,255,256,65534,65535; no partial publication | NOT RUN in a v2 decoder |
| SUSTAIN-02 | Reject0,65536, native28-bit maximum, UINT32_MAX, wrong full-width identity, wrong role/tag/version, padding and malformed size; no side effects | Identity arithmetic checked only |
| SUSTAIN-03 | Old/new profile mismatch in both directions; legacy1/2 behavior preserved; no silent fallback | Legacy controls only |
| SUSTAIN-04 | Consumed receipt, old epoch, foreign endpoint and divergent native cohort rejected; interruption/partial-reply/poisoned-close cleanup | NOT RUN natively |
| SUSTAIN-05 | Five actual runner/bytecount/backend cycles, including generation3; exact `6\n`, statuses0/0/17, no leaked references/children and final authorized shutdown | NOT RUN |
| SUSTAIN-06 | Last-epoch completion and pre-effect exhaustion; malformed/error reply checks in all three result paths; matching legacy regressions and sealed inputs | NOT RUN |

Before runtime edits, finish the affected UL-063 source review and reconcile this
proposal with Aether and sys-init. Implementation must cover `four-role.c`,
`four-role-io.c`, `native-io.c`, all result functions in `runner-result.c`, runner
selection, build flags and both rebuilt runner and bytecount. Updating just the
first observed rejection cannot close the dependency. Preserve old compile defaults
and old fixture bytes; retain each new build/test attempt separately.

Deliver source/flags/tool/SDK pins, native object/link inspection, explicit profile
manifest, rebuilt payload hashes, malformed/stale/exhaustion controls and matching
owner-native observations. No source count or host success substitutes for SI-07
native qualification or independent sys-init acceptance. The dash recovery handoff
remains a separate ready workload; neither workstream silently supersedes it.

## Executable decoder proposal checkpoint — 2026-09-25

The [isolated host experiment](../../docs/evidence/sustained-decoder-2026-09-25/README.md)
now exercises a small patch against copied role/result decoders. All65,535 epochs,
2,592 role cases,37,716 result assertions, old/new wire rejection, unchanged legacy
controls and an intentional mixed-link rejection pass under host UBSan. This is
pure-decoder coverage for SUSTAIN-01–03/06, not completion of those integration
cases. The table above retains the original proposal baseline. Default runtime
sources are unchanged; bootstrap/transport, full-width native identity, rebuilt
runner/bytecount, owner reconciliation and native execution remain pending.

## Maintained client checkpoint — 2026-10-03

The opt-in `NATIVE_SUSTAINED_V2` profile now implements both bootstrap adapters
and the role/result decoders. Parent startup remains AERUN001 followed by AERIO002;
child requires NIO2. Both adapters validate the full native syscall result in
1..65535 before narrowing or reading records. Complete bindings/startup publish
only after validation. The profile versions public client symbols; mixed objects
fail linking. It uses the existing four-role runner selection and bytecount entry,
with no negotiation or automatic fallback. Default compilation retains legacy bytes.

Run `python3 -B experiments/command-runner/check-sustained.py` with the provisioned
strict SDK. The [client packet](../../docs/evidence/sustained-runtime-2026-10-03/README.md)
records host controls, mutations, static ELF inspections, exact tool/SDK/source/flag
pins and rebuilt parent/child. Historical copied-decoder experiment inputs remain
frozen; its baseline-bound checker targets those old inputs, not revised sources.

Aether's 2026-09-29 design review clears this private protocol under full-width
cohort equality and finite retirement. Native SUSTAIN-01–06 still requires matching
Aether carrier/receipt/cohort hooks, five actual cycles, exhausted-ID rejection,
cleanup and authorized shutdown, followed by independent consumer qualification.
The client build is a handoff candidate, not native acceptance or sys-init readiness.

## Matched native replay checkpoint — 2026-10-03

Aether delivered matched hooks and userland independently replayed nine frozen
AENSI001/ABI22 images; [consumer evidence](../../docs/evidence/si07-consumer-2026-10-03/README.md)
records five actual useful cycles1–5, seeded255/256/65534/65535, finite exhaustion,
both parent profile mismatches and full-width cohort divergence. The positive run
has15 reclaims,0/0/17 terminals and authorized halt;242 independent trace corruptions
reject. Exact backend6\n is asserted by the inspected owner, not exposed directly
as an independent UART byte stream. All native runs passed first attempt.

The bounded SUSTAIN-05 useful-cycle core is established. SUSTAIN-01–04/06 retain
missing native malformed/stale/foreign/child-profile/partial/poisoned-close coverage;
seeded exhaustion is not65535-cycle endurance. sys-init-owned interruption/shutdown
policy and its consumer acceptance remain separate. No full SI-07 closure is claimed.

## Quiescent loop consumer — 2026-10-03

Sys-init now handles r/h at the initial and every completed-cycle boundary;
[seven independent userland replays](../../docs/evidence/si07-loop-consumer-2026-10-03/README.md)
pass, including six real cycles/18 reclaims and buffered rh. Invalid input, omitted
UART close/busy halt and exhausted r reject with exact semantic evidence.179 host
trace corruptions reject. The unchanged v2 runner/bytecount are bound into every
selected ISO. There is no current external blocker for bounded continuation;
partial/unknown reply, cleanup-failure, broader schedules and useful-session policy
remain sys-init work. No full SUSTAIN/SI-07 or SDK release acceptance is implied.

## Failure controls consumed — 2026-10-03

[Four independent native runs](../../docs/evidence/si07-errors-consumer-2026-10-03/README.md)
qualify actual16-byte reply fragments, accepted write/reply-reader loss, real
EACCES13close and EBADF9reclaim. Only split succeeds and halts with3reclaims;
loss/cleanup cases intentionally fail with exact assertion952/1406, retained
Unknown resources and no replay/completion/halt.183host trace corruptions reject.
No maintained client/runtime changes or production recovery acceptance. The
[current disposition](../../docs/SI07-DISPOSITION.md) identifies remaining native
malformed/stale/foreign/child-profile schedules, wait/useful-session integration
and independent reader/SDK requirements without declaring a dependency blocker.
