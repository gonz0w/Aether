---
id: BG-060
title: Define sustained history retention and reuse
status: captured
created: 2026-09-07
source_type: research-follow-on
area: native
---

## Release disposition

Shelved for a later release by the maintainer on 2026-09-07. The
[accepted v1 scope](../../../docs/V1-SCOPE.md) supersedes previous active/next
statements below. Findings remain available; this work is not complete.

## Scope and acceptance

NC-07 ends live eligibility but retains two lifetime attempt slots, raw samples
and six cut records. This cannot sustain production restart cycles. Research an
explicit bounded retention/archival and fresh-attempt admission policy without
turning stale receipts into authority, evicting uncertainty or resetting a live
owner. Distinguish runtime archival, persistent durability and owner replacement.

Acceptance: justify bounds, exact retirement/reuse ordering and stale/replayed
receipt behavior; record alternatives and failure/overflow/recovery requirements
before implementation. Coordinate BG-057 for applied Cleaned, BG-058 for complete
launch ownership and BG-033 for unknown/replacement-owner recovery. Do not add a
reset API, durable store or post-R1 service feature as part of decision 0156.

Source: decision 0156; owning integration story BG-057.

## Complete pair teardown — decision 0177

Decision 0177 completes provider Terminal, exact reclaim/acknowledgment and
Cleaned after the already-qualified dependent teardown. Both services reach
Cleaned under the original application owner. Provider observations are tied to
the original issued launch record and Launched receipt, captured into its unused
primary sample before interpretation. Foreign owner, unsealed source and local
interruption deny; interruption retains two actual returns and closes History.
The generic close/reclaim executor checks the exact Started key before calls and
retains actual returns through acknowledgment for either service.

A Terminal member may now have a Cleaned peer; the selected member must still
be Launched. Empty dependent-Cleaned retirement releases its effect-pool credits
without erasing the cut. Provider Terminal/Cleaned occupy cuts 5 and 6. Native
checks verify stage receipts and both complete primary samples; the 26-test
core suite explicitly compares all six preserved records. A rollback to the old
peer guard fails the new test as expected. There is no record reset or eviction.

Four new Aether cases pass: full teardown gives 100/reclaimed 3; owner, seal and
interruption controls give 1111/1112/1113 after one reclaim. Both policy-owned
workers are reclaimed before the adapter-empty check. A separate ordinary reuse
probe supplies the kernel fixture's required third reclaim, preserving its PASS
contract; it does not replace either policy teardown or create a seventh cut.

All 224 prior ABI-16 images rebuild: 208 are identical and 16 changed probes are
freshly reexecuted with their exact prior outcomes. All 208 ABI-15 and 151 ABI-6
images remain identical. This is 20 fresh native executions plus 567 unchanged
images, not a fresh 228-case campaign. The maintained composed case catalog now
contains 228 cases with the pinned worker. All ten local gates pass in run-ej7zipxo;
26 core tests, 17 existing core controls and the extra rollback control pass.

All four new probes use the existing explicit fat-LTO/one-codegen-unit profile.
The positive is 16,360 bytes, only 24 bytes below the unchanged 16 KiB bound.
All new/changed paths execute without guest faults on the unchanged 4 KiB stack.
No future code/stack headroom or performance claim follows. 8 earlier bounded
links reject and remain retained; no failed native attempt occurred in this step.
The complete-pair fixture omits repeated dependent-only negative/replay exercises
that remain in separately reexecuted cases. Actual enforcement remains intact.
No allocation, unsafe site, shared release pin, producer/worker pin or sibling
repository change is introduced. The old evidence catalog remains unchanged.

Next BG-060: research bounded history retention and fresh-attempt admission after
a complete cycle. The six-record store cannot sustain restarts, even after its
empty credits are retired. Native final-Cleaned credits remain retained; the core
test additionally retires them and still verifies record exhaustion. Preserve
unknown outcomes and stale-receipt denial; do not introduce a reset as a shortcut.
BG-057/BG-058 remain active for sustained integration; BG-033 recovery, BG-056
new-profile catalog support and independent review remain separate. No current
kernel blocker is established.

## Research checkpoint — decision 0178

Source review and checkpoint/admission contract: [research](../../../docs/research/SUSTAINED-HISTORY-RETENTION.md). BG-062 captures the two-cycle model and negative controls. Remains active: production compaction/loss policy, archive sizing, independent member restart and native storage integration are unresolved. No runtime reset or reuse exists.
