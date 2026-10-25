# 0142 — Evidence limits and next operational priority

BG-056 checkpoint, 2026-09-07. Consolidate decisions 0125–0141 into an accessible
current coverage/limits guide. Historical decision text remains historical; do not
reinterpret old next-action statements as new work. Update quality gap milestones
and current planning without altering retained snapshots, runtime or release pins.
Foundations E-04/E-05/E-07/E-08 distinguish host audit evidence from target execution,
provenance, review and release authority. RC1 remains unpublished review input.

Prioritize aggregate source snapshot reads next: scripts/check-all.py source_hashes
currently uses unbounded read_bytes over discovered Python and explicit input paths,
without ordinary-file or read-identity checks. Its initial call precedes gate
watchdogs, and the final call follows them. Native-audit bounds do not protect this
separate path. A bounded host-only change should inventory real source sizes/counts,
set compatible per-file/total/traversal limits, reject special/link inputs under an
explicit root policy, capture stable bytes and preserve successful report hashes.
Test malformed/oversized/changing sources without touching retained evidence.
Keep deadline/hostile-race claims scoped; do not claim a byte bound is an I/O timeout.

Follow with aggregate report publication/error-path review. Extended scheduling
belongs to BG-054 and needs an explicit plan before provisioning. Independent
review, missing artifacts and release authority cannot be manufactured locally.
No new feature or automation is created by this checkpoint. Validation: inventory
reference checks plus all repository gates; no new behavior-specific tests needed.

Validation: all ten gates pass in run-y2t_prwl; new guide links resolve and
git diff --check passes. Native audit implementation/output, catalog, 24 native
inputs and release pins remain fixed. Evidence:
../evidence/evidence-limits-priority-2026-09-07/.
