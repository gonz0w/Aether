# 0089 — Queue the init image-capacity dependency

2026-09-06; documentation handoff for BG-058, following decision 0088.

Current Aether parser and init reference still retain the 4096-byte init profile.
The companion backlog contained SI-01–04 but no item for the larger init-compatible
fixture. Under the maintainer's standing request to track companion blockers in
Aether, SI-05 is now queued in its existing ROADMAP and STATE. No new status system
or shared standard is introduced. Aether's unrelated R1 priority remains unchanged.

[SI-05](../../../.planning/ROADMAP.md#si-05--init-compatible-supervisor-image-capacity)
links the [consumer request](../research/NATIVE-INIT-IMAGE-CAPACITY-REQUEST.md),
requires a separate producer-selected version/profile, preserves old ABI-6 bounds
and authority, and specifies mapping, second-page execution, boundary rejection,
cleanup and independent consuming evidence. Queuing does not mean the producer
has accepted or implemented the request. The proposed 8192-byte capacity is an
experimental fixture allowance; no production budget or ABI identifier is assigned.

Only companion planning documents change. Local state, backlog, request and quality
references record the handoff. No live runtime, harness, linker, pin or retained
0088 evidence changes. Sys-init remains at its accepted 151 native cases; no new
native execution is claimed. BG-058 waits for the SI-05 producer decision/bundle;
construction denial, closed reoffer and PH-05–07 remain open.

Scoped O-01/I-01/E-04–08 review keeps kernel contracts with Aether, policy with
sys-init and future shared rules with Aether-standards. Required validation is the
Aether documentation workflow/offline pin checks and local-link inspection, plus
all nine sys-init development gates. No unrelated QEMU or pre-merge claim applies
to this planning-only update. No independent owner/reviewer sign-off is invented.

Validation: all nine sys-init development gates pass in `out/checks/run-omsp18hl`
with unchanged checked sources. Aether workflow and all three offline standards
checks pass; new cross-project links and SI-05 anchor resolve. All eleven accepted
consumer inputs and all 523 sealed decision-0088 evidence files remain unchanged.
This is documentation-only validation; no native workload or new ABI was executed.
Full logs, before/after planning snapshots and hashes are retained in
`docs/evidence/init-capacity-handoff-2026-09-06/`.
