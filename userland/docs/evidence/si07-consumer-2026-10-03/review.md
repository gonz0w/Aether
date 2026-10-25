# UL-058/UL-063 SI-07 independent replay review — 2026-10-03

Before implementation: Codex userland technical review, independent of the supplied
producer trace/oracle within this consumer work; no human reader approval claimed.
Requirement: verify sealed matched AENSI001/ABI22 hooks and exact v2 payloads, then
replay nine final owner images in fresh QEMU instances. Aether owns native authority,
cohort admission/retirement/cleanup and private owner assertions; userland owns this
consumer witness. sys-init policy is not implemented or accepted here.

Pinned producer SHA256SUMS809a1912dd46657001282146cdc22ff593935b822e2fe8623d1208c842107a6a;
archivefbe252838ed32ed0b9c9163a61dd050ae90f34c9ebd2440f18739acf773bf1f6.
Verify every sealed member and indexed archive member before consumption; refuse
unsafe names/duplicates/types, never follow archived symlinks. Copy selected ISOs,
source and tool/firmware pins into private build root; no sibling writes. Fresh
firmware variables per VM. Inputs checked again after replay.

Selected cases: five real cohorts1–5; seeded255/256/65534/65535; both parent profile
mismatches; full-width divergent cohort; pre-admission65536 exhaustion. Require
fresh prompt gating (r only after command-ready, h only after halt-ready), ordered
0/0/17 terminals, exact completion count,15 or3 reclaims and authorized halt. Mismatch
requires110/17 terminals, no successful completion, two reclaims and halt. Divergence
requires explicit reclaimed rejection and zero worker terminals; exhaustion requires
explicit pre-admission denial with no command-ready/terminal. These negative owner
fixtures end with fixture-failure markers; that alone cannot satisfy rejection.

Host oracle must reject corrupt traces: missing/duplicate/out-of-order evidence,
wrong terminal status/generation, low idle/ticks, wrong reclaim, missing halt readiness,
extra admission/terminal and lost boundary rejection. Byte output6\n is checked in
owner code before success; UART does not expose backend bytes directly. Bind this
limitation to inspected source/owner images, not a stronger observation claim.

CP/CE/O/I/E/TD/TE rules from pinned Foundations and approved quality drafts apply.
Reuse process.py unchanged with explicit executable/cwd/env,120sec outer deadline,
16MiB file bound and process-group cleanup. Inner interactive QEMU stays in that
owned group, has90sec monotonic deadline,2MiB serial cap, bounded terminate/kill/wait.
It records actual inputs and full serial/error output even on failure. No detached
process, background monitoring, public CLI presentation or standards adoption changes.

Simpler alternative: replay exact sealed ISOs selected here. Source rebuild adds
scope and does not replace byte-identical replay; freeze/inspect exported sources
and artifact binding, leave source recompilation a separate layer. Remove no path:
old producer/evidence stays immutable. Original Python BSD-2-Clause, no dependency.

Remaining: native child-bootstrap mismatch, wider malformed/stale/foreign schedules,
partial/poisoned-close cleanup, actual interruption/recovery policy, endurance65535,
independent reader, supported SDK disposition and full SI-07/SUSTAIN acceptance.
Select local quality/syntax/whitespace checks after docs changes. Keep failed attempts.
