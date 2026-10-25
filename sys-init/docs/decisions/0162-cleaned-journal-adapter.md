# 0162 — Cleaned-cut journal integration

BG-057, 2026-09-07. Connect Cleaned observations to the actual policy model and
journal after Terminal application. The adapter retains the exact reclaim token
produced by that Terminal transition; an executed acknowledgment for that token
and a fresh, exact-source empty resource inspection are both required. Neither
an acknowledgment nor a fixture boolean independently establishes cleanup.

Bounded profile: two attempts, six registered sources, four resource ownership
flags per inspection, fixed model time and no replacement admission. Reuse the
existing reserved-batch and effect-capture path. Resource inspection is a trusted,
read-only synthetic callback under the coordinator's reentry guard; it does not
perform native cleanup. Retain inspected data and reclaim identity on failure.
No new dependency, shared ABI, release pin or sibling edit is required.

Before model mutation, validate all members, source identity, generation/context,
terminal ownership, exact executed reclaim and empty reader/writer/worker/wait
state with no unresolved disposition. After mutation require cleanup complete,
no ownership or deadline, and the same generation. Exact receipt replay must not
inspect or apply again. Unknown and rejected reclaim cannot authorize Cleaned.

Test successful admission and replay, reserved/issued/unknown/rejected reclaim,
all live resource positions, malformed/foreign inspections, stale context,
missing transition, callback failure/reentry, and two-member preflight. Source
omission controls must detect removal of reclaim and resource checks. Run the
full local gates; native behavior is unchanged and needs no new target claim.
Native provenance/disposal and combining real journal admission with pending
release/retirement remain BG-058/BG-057. Reuse remains BG-060, recovery BG-033.

## Validation and handoff

Decision 0162 integrates Cleaned admission with the actual lifecycle model and
journal. It retains the exact reclaim token emitted by Terminal and requires its
executed disposition independently of a fresh, exact-source resource inspection.
Reader, writer, worker and wait ownership must all be empty, with no unresolved
cleanup. All cut members are preflighted before model mutation. Completion leaves
the same generation unowned with cleanup complete and no deadline; exact receipt
replay neither inspects nor applies again. Retry policy can schedule a future
attempt but this fixed-time cut does not launch a replacement.

All 280 model tests pass, including nine Cleaned tests and two source omission
controls. All ten local gates pass in `run-wpld9nvb`, with unchanged checked
inputs. All twelve native consumer sources, three release locks and catalog bytes
match the preceding checkpoint. Resource inspection and executed acknowledgments
remain trusted synthetic inputs; this is actual policy-model/journal integration,
not native resource disposal. No independent reviewer sign-off is claimed.

Next BG-057: combine the actual three-phase journal adapter with pending release
and retirement, including mixed cuts. BG-058 retains native provenance/disposal;
BG-060 retains sustained reuse and BG-033 recovery. The 185-case native checkpoint
and BG-056 producer source-closure limitation remain unchanged.

Review: an executed acknowledgment is insufficient when any resource remains;
empty-resource metadata is insufficient after a rejected reclaim. Exact-token
retention is independent of subsequent runtime.pending changes. Both member
inspections precede application, and returned observations remain diagnostic on
denial. Callback reentry and exceptions close without implicit cleanup/retry.
Post-transition verification and full journal capture retain separate oracles.
The trusted single-owner callback is not a concurrency or native authority proof.
Documentation impact: adapter contract/reference, model count, source list,
command digest/line references, quality surface and BG-057 handoff.
Evidence: `docs/evidence/cleaned-journal-adapter-2026-09-07/`.
