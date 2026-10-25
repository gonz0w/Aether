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

1. **Maintained ABI22 build/run entry point — complete for developer scope.**
   The [offline recipe](AETHER-BASELINE.md) verifies frozen sources, payloads,
   dependencies and tools, uses fresh private output and retains failures.
   Raw owner and linked ELF reproduce exactly; a fresh useful-cycle/halt witness
   passes. [Evidence](evidence/abi22-baseline-recipe-2026-10-03/README.md) records
   source identities and host controls. This does not accept a product console,
   installer, dynamic configuration or complete v1 release.
2. **Static service table and startup-probe separation — complete in scope.**
   The explicit --service-table profile uses a compile-time checked constant
   Backend/Runner/Command role-image-order table, with zero automatic retries.
   It skips the old 3005-tick startup/grant probe; the default baseline preserves
   its tested artifacts. [Decision](decisions/0179-abi22-inert-service-table.md) and
   [evidence](evidence/service-table-2026-10-03/README.md) retain compiler negatives,
   fresh native command/halt and pre-admission halt, plus linked-stack inspection.
   Fixed-output assertions and fatal fixture errors remain test machinery; no
   dynamic descriptor, arbitrary topology or production recovery is claimed.
3. **Bounded pre-effect command supervision — qualified in scope.** The explicit
   supervised profile allows one replacement only before command backend I/O and
   after complete known cleanup of all three roles. Actual failure/replacement,
   exhaustion, after-read no-replay and cleanup Unknown/Closed are witnessed;
   failed requests cannot admit more work and permit halt only after known cleanup.
   [Decision](decisions/0180-abi22-bounded-pre-effect-retry.md) and
   [evidence](evidence/supervised-retry-2026-10-03/README.md) preserve limitations,
   failed attempts and older profile compatibility. Fixed bytecount assertions,
   partial-startup/malformed transport failure and backend/runner recovery are not
   general product policy or arbitrary-command restart acceptance.
4. **Qualify the selected usable environment and finish the guide.** ABI17 Dash
   script execution, ABI22 command reuse and userland ABI23 interactive sessions
   are distinct witnessed profiles, not interchangeable payloads. A shell product
   needs an explicit matching composition and its ownership/input/cleanup evidence.
   The [serial composition review](SERIAL-BOOT-COMPOSITION.md) now records that
   boundary: one sys-init owner with matched SESSION runtime. The [ABI24 intake](decisions/0182-abi24-producer-intake.md)
   verifies qualified kernel mechanisms. Matched wait-aware userland009 is now
   verified, and the [owned entry candidate](decisions/0183-owned-serial-session-entry.md)
   boots real dash with bounded immediate/delayed witnesses. An initial delayed
   failure remains unclassified; composition qualification/maintained recipe are open.
   Finish one assembled boot/configure/
   failure/retry/shutdown scenario and independent review before publication.

Step4 and the named protocol/production-policy gaps are remaining work, not a new commitment to a shell, filesystem, login,
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

Simplicity review at the original disposition: keeping only dated experiment scripts was smaller but
makes the working baseline difficult to reproduce and maintain. Choose one pinned
local recipe, now completed, preserving those records while removing dependence on temporary
scripts for future iteration. Reuse current owners rather than another supervisor
framework. Foundations O-01–05, I-01/03–06 and E-01–08 apply; Distribution boot,
service and release clauses keep assembled claims separate. Existing internal
Experience output limits remain. No shared rule/pin or runtime change was made by that disposition review.
