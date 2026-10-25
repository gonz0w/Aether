# UL-007 matched suspend-recovery consumer qualification

The completed recovery handoff passes local sequential native replay on2026-09-14:
**316 connections and431 command-runner cases,747 total**, with matching250 harness
source hashes. All208 startup cases are indexed; ten phase-one and fifteen
wait/recovery transcript comparisons pass. Host checks pass, including101 Python
tests plus Zig/offline checks. All611 restored source/support files and4311 SDK
files remain unchanged. No private adapter was installed and no sibling changed.

Connections took1072.68seconds; command-runner took1463.65seconds. Both are within
the1800-second review ceiling and the preselected3600-second outer bound. Suites
ran sequentially, with unchanged per-case watchdogs and complete owned cleanup.
The producer's earlier timeout remains historical incomplete evidence; it is not
reclassified. Both local native runs and retention passed on their first attempts.

The unchanged wait script uses actual background helper7, parent0, backend17 twice
and six reclaims. Failed-stack entry rejects three times with no handler delivery,
then normal-stack retry delivers the retained occurrence once and restores state.
The false-valid-stack control produces child72/parent238/owner1950 and zero
reclaims. The remaining ordering/stop/ignore/block/repeat/stale-parent controls
retain their exact selected terminal and supervisor sequences. Native program
assertions establish canary/mask/handler internals; transcript comparison is not
an independent signal implementation or separate host stdout capture.

[Plan](review.md), [acceptance](acceptance.json), [preparation](preparation.json),
[connection timing](connections-timing.json), [runner timing](command-runner-timing.json),
[trace checks](trace-checks.json), [startup inventory](startup-cases.json) and
[artifact hashes](artifact-hashes.json) retain scope and identity. All747 serial
logs and available QEMU logs are under cases. Producer seal:
a7ef78065da6fd35883295ba3ce520a2835f4dbe980f1b62de7a43ceae9ab903.
Its source dependency is the sealed suspend-recovery packet; all inputs were
verified before restore. Source/SDK/tool versions and build flags are in the
preparation, original tool receipt and complete native command receipts.

To preserve the user's cleanup preference, full suite outputs are archived under
build/retained-artifacts. [Compaction](compaction.json) maps original suite paths
to archives and per-file indexes. Every archived member is verified against the
unchanged original before removing unpacked copies; the local compiler cache is
then removed. Use those mappings to restore absent historical build paths. The
source tree, SDK, original receipts and sealed historical packets remain intact.
See compaction status for actual completion; an archive's existence alone is not
proof of successful relocation.

Self-review covered matched identity, script bytes, exact case/trace inventories,
sequential deadlines, cleanup and verified artifact relocation. Python syntax and
local quality checks pass. Independent technical/security/reader reviews and
UL-081 public SDK acceptance remain pending. This is a bounded BSP single-context,
handler-only private fixture; default termination during suspension, general nested
delivery and eventual unblock remain gaps.

The five previously qualified unchanged scripts remain the qualified workload
count. Failed-exec is still an owner contract awaiting native implementation;
seven of twelve scripts remain unqualified. Next consume its unchanged script
with missing127/non-executable126 and independent denial/cleanup controls. General
TTY, writable filesystem/persistence and package/sys-init/R1 assembly remain open.
This does not complete M3 or establish release readiness.
