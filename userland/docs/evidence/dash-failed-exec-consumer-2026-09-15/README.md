# UL-007 unchanged failed-exec consumer qualification

The unchanged DASH-failed-exec script is locally qualified on2026-09-15 UTC.
All6 focused cases,322 connections and431 command-runner cases pass sequentially:
**759 native case executions**, with matching252 harness source hashes for the
full suites. All208 startup cases and37 selected transcript observations pass.
Host checks pass, including101 Python tests plus Zig/offline checks. All613
source/support files and4311 SDK files remain unchanged.

Two separate fresh VM positives (focus and full connections) each observe actual
child127 generation1, child126 generation2, parent0/backend17 and four reclaims.
The owner reads back exactly exec errors ok newline. This distinguishes an absent
path from an owner-backed present non-executable object, without granting image
authority from a pathname or POSIX mode. Two scripts in a single VM are not claimed.

All five controls reject as required in both runs: missing-as-denied gives child126/
owner2130 with zero reclaims; denied-as-missing gives second child127/owner2130 with
one reclaim; skipped second request gives child226/owner2130 with one reclaim;
false output success rejects2310 after two reclaims; retained first child rejects
2153 with zero reclaims. These are exact native outcomes, not timeouts or host
simulation. Readback and internal state are native fixture assertions; transcript
comparison is not an independent implementation or a separate stdout capture.

[Plan](review.md), [acceptance](acceptance.json), [preparation](preparation.json),
[trace checks](trace-checks.json), [startup inventory](startup-cases.json) and
[artifact hashes](artifact-hashes.json) retain scope and identity. Final producer
seal:63eaa8b6147673750027471b918b912b0af0c85c9f569f3b9d5f6ce9d6e09611.
Only final attempt-6 sources were executed, after support restore and before the
pinned documentation overlay. Earlier producer failures remain retained. No local
native/host/retention retry was needed. All owned commands record complete cleanup.

The full connections run took1019.35seconds and command-runner1423.47seconds,
both within the1800-second review ceiling and3600-second outer limit. Per-case
watchdogs were unchanged. Timings are qualification observations, not benchmarks.
The opt-in kernel completion verdict is included in the matched suites; the
producer's scheduler regression is prior evidence, not a fresh local scheduler run.

All759 serial logs and available QEMU logs are retained under cases. Full suite
outputs are compacted after byte-for-byte archive readback and unchanged-source
verification. [Compaction record](compaction.json) maps original build paths to
archives/indexes under build/retained-artifacts; use it for restoration. Completed
unpacked suites and their compiler cache are removed, while source/SDK inputs and
sealed historical evidence remain intact. See actual compaction status for completion.

Python syntax and local quality checks pass. Self-review covered input pairing,
script contracts, complete inventories, error/status/cleanup oracles, sequential
limits and verified artifact relocation. Independent technical/security/reader
review and UL-081 public SDK acceptance remain pending. No sibling was changed.

**Six of twelve unchanged scripts now have bounded local native evidence.** The
remaining scripts are fd-leak-control, redirection, denied-redirection, pipeline,
substitution and early-reader. Next qualify owner-backed scratch descriptors through
actual dash fork/exec/wait for the unchanged leak and redirection scripts. Existing
C scratch proofs and owner host tests are prerequisites, not those script results.
General signals/TTY, persistence and package/sys-init/R1 assembly remain open;
this does not complete M3, full POSIX or release readiness.
