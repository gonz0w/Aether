# SI-07 consumer disposition and v1 work order

Reviewed 2026-10-03 under BG-067. The bounded sustained command mechanism is usable
for further sys-init development. Full SI-07/SUSTAIN-01–06 and the v1 product are
not complete. The missing matched inputs, sys-init-owned request loop, and
independent userland replay dependencies are closed within the evidence below.
No new ABI, quota, standards pin or broad recovery framework is needed for the
next local step. Earlier implementation audits and blocked handoff notes remain
historical; this disposition is the current work order.

## Evidence and owner boundaries

- [Matched intake](evidence/si07-intake-2026-10-03/README.md) verifies the frozen
  ABI22/v2 producer/userland inputs and one producer-image replay.
- [Owned integration](evidence/si07-owner-2026-10-03/README.md) supplies four native
  sys-init cases: five useful cycles, early/late cohort rejection and exhaustion.
- [Request loop](evidence/si07-loop-2026-10-03/README.md) supplies seven native cases:
  halt at zero/one/six cycles, buffered intent, invalid input, omitted-close busy
  denial and exhaustion. Five older command images remain byte-identical.
- [Failure qualification](evidence/si07-errors-2026-10-03/README.md) supplies four
  native cases for split replies, lost write reply and real close/reclaim errors.
  These demonstrate failure retention and no replay, not continued recovery.
- [Retained cross-project review](evidence/si07-disposition-2026-10-03/README.md)
  verifies userland's nine independent producer-image replays and seven replays
  of our exact request-loop ISOs. Their records report242 and179 trace-corruption
  controls respectively. Those controls/replays were not rerun in this review.
  Cross-project technical evidence is not independent human reader approval.

Kernel mechanism, userland protocol and sys-init lifecycle acceptance remain
separate. A count of successful cases cannot close untested requirements. The
SUSTAIN IDs below come from userland's captured SUSTAINED.md, including its dated
updates; its original NOT RUN table is a historical proposal baseline.

## SUSTAIN disposition

| Requirement | Evidence available | Remaining scope and owner |
| --- | --- | --- |
| SUSTAIN-01: v2 role/bootstrap/result boundaries through65535, no partial publication | Sys-init actual cycles1–6; producer seeded255/256/65534/65535 independently replayed by userland; complete reply accumulation and cohort checks | Partial. Seeded producer observations do not qualify sys-init at every boundary. Native child-bootstrap/result/admission negative schedules remain userland/Aether protocol work; sys-init consumes matching outcomes. |
| SUSTAIN-02: invalid epochs/full-width identities/roles/tags/versions/padding/size without effects | Local pre-admission65536 and early/late full-width cohort rejection; host decoder and producer controls retain their own scope | Partial. Full native malformed/no-effect matrix is not established by arithmetic checks or one exhaustion case. Userland owns decoder behavior; kernel enforces authority; sys-init preserves admission checks. |
| SUSTAIN-03: both old/new mismatches, unchanged legacy behavior, no fallback | Two parent-carrier mismatch directions independently replayed; five legacy sys-init raw images unchanged | Partial. Child-bootstrap profile mismatch and full composition-level compatibility remain unqualified. No automatic downgrade is implemented. |
| SUSTAIN-04: consumed/stale/foreign/divergent identity, interruption, partial reply and poisoned cleanup | Local divergence stop/cleanup, buffered halt after complete work, split/lost reply tests, actual Unknown close/reclaim retention and denied replay | Partial. Native stale/foreign/consumed-receipt combinations and precise wait/interruption schedules remain open. Fatal fixture rejection is not a product recovery path. |
| SUSTAIN-05: five actual useful cycles, exact output/status, cleanup, authorized shutdown | Bounded useful-cycle core satisfied: sys-init five and six cycles, ordered0/0/17 terminals,15/18 reclaims; seven independent userland request-loop replays | Accepted only for this private bytecount/memory-backend workload. Exact6-newline bytes are asserted inside the owner; UART is not an independent backend output stream. No shell/login/persistence or indefinite uptime follows. |
| SUSTAIN-06: final epoch, pre-effect exhaustion, all three malformed/error result paths and matching regressions/seals | Producer seeded final epoch; local forced65536 rejection; matched legacy/source identities; lost-reply fail-closed behavior | Partial.65535 sequential commands are not demonstrated. All three result-path malformed/error outcomes and consumer final-epoch composition need scoped acceptance before a complete claim. |

The original sys-init handoff also requests wait registration/event ordering,
spurious/cancel outcomes and grant-denial behavior. Current consumer coverage is
startup idle beyond3000 ticks, delayed input, buffered intent, stale worker/reader
checks, wrong grants/unsupported halt, and busy halt. Producer core/older mechanism
tests are supporting evidence, not a fresh sys-init native race matrix. Track the
remaining schedules under BG-067; do not conflate them with absent kernel APIs.

## Smallest v1 delivery path

1. **Next local change: reproducible ABI22 baseline build/run entry point.** Turn
   the successful dated composition into one maintained offline recipe, using exact
   frozen source, three payloads and tool/boot identities. Use fresh private output,
   retain failures, bind the generated ISO to its inputs and document the r/h
   developer contract. Reproduce the current normal raw image before changing
   behavior; run one fresh useful-cycle/halt witness. Do not add an installer,
   general framework, new image format or dynamic configuration parser.
2. **Separate test setup from product policy and bind a small service table.** The
   existing startup helper intentionally idles for3005 ticks and probes denied
   grants; the normal loop still asserts fixed bytecount output and ends fatally
   on errors. Keep these as tests. Make role/image/order/retry intent explicit in a
   build-time validated inert table using existing bounds and grants. A table is
   configuration, not authority. Do not import ABI16 service-pair calls into ABI22
   without its paired-connection mapping and a fresh witness.
3. **Complete bounded supervision on that one useful path.** Reuse retained
   connection ownership for cleanup before replacement and finite retry policy.
   Demonstrate a real service failure, replacement and retry exhaustion without
   replaying an unknown backend effect. Unknown cleanup must stop admission and
   report failure; automatic recovery is not required or justified by this record.
   Add plain diagnostics and preserve the distinction between halted and failed.
4. **Qualify the selected usable environment and finish the guide.** ABI17 Dash
   script execution, ABI22 command reuse and userland ABI23 interactive sessions
   are distinct witnessed profiles, not interchangeable payloads. A shell product
   needs an explicit matching composition and its ownership/input/cleanup evidence.
   Record that boundary before wiring it. Finish one assembled boot/configure/
   failure/retry/shutdown scenario and independent review before publication.

Steps2–4 are remaining work, not a new commitment to a shell, filesystem, login,
TTY, signal API or persistence implementation here. The maintainer's simple v1
scope remains authoritative. Existing service owner/pair and script witnesses are
reusable components; they do not already demonstrate one assembled product.
The fixed-memory backend and r/h console remain a developer baseline. The old
30-second startup probe is not a product boot-time requirement or measurement.

## Completion and stopping rules

Close each local slice on exact sources, appropriate native evidence and full
local checks. Avoid rerunning unaffected platform or legacy campaigns just to
increase counts. Keep the remaining SUSTAIN negatives as bounded protocol work,
not a reason to add lifecycle machinery. A concrete missing producer contract or
payload can block the affected shell/composition step; no such dependency blocks
the maintained ABI22 recipe now. Keep BG-067 open until useful boot acceptance,
with existing BG-054/056 release/process gaps separate. No sibling task is edited
or messaged by this review and no owner sign-off is invented.

Simplicity review: keeping only dated experiment scripts is smaller today but
makes the working baseline difficult to reproduce and maintain. Choose one pinned
local recipe next, preserving those records while removing dependence on temporary
scripts for future iteration. Reuse current owners rather than another supervisor
framework. Foundations O-01–05, I-01/03–06 and E-01–08 apply; Distribution boot,
service and release clauses keep assembled claims separate. Existing internal
Experience output limits remain. No shared rule/pin or runtime change is made.
