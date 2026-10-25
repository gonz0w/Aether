# Quiescent SI-07 request-loop consumer — 2026-10-03

The matched-input and fixed-five-cycle blockers are closed for bounded development.
Sys-init owns the new ABI22 loop; userland independently checks its exact delivered
images and existing v2 runner/bytecount. This checkpoint does not claim full SI-07,
public/authenticated operator access, arbitrary cancellation or supported SDK release.

[Before-code plan](review.md), [intake](preparation.json), [native cases](native-results.json),
[technical findings](findings.md), [oracle controls](oracle-results.json),
[owner/stack bindings](inspection.json). Producer manifest
2115a58e13d5632c48cc4a9cf4d69cc74d5ffc81555aee743307a4126f3bfb62
pins115 packet members;343 frozen source members are verified before consumption.
Three selected ISOs are copied by declared artifact hashes; their actual native
payloads are extracted and bound to the exact AENSI001 sizes/reserved fields,
userland v2 parent/child hashes and sys-init owner raw bytes. No source build claim.

Seven fresh QEMU replays cover halt before work; one cycle; six cycles/18 reclaims;
buffered rh requiring a complete cycle/three reclaims before halt; invalid request
before admission; omitted UART close with explicit busy-halt rejection; forced65536
request rejection before admission. Terminal0/0/17 order and every completion/
request boundary are independently checked. Input waits200ms after complete prompts;
rh is one write. Buffered intent does not imply mid-effect cancellation coverage.
The unchanged30-second idle fixture probe is test behavior, not product startup time.

Seven host comparisons reject179 corrupted traces, including missing, duplicate,
reordered, wrong-terminal/reclaim and extra admission/worker facts. Backend6\n bytes
remain asserted by the inspected owner before completion, rather than directly
exposed in UART. Rejection requires its exact semantic proof; generic panic/timeout
or missing tools cannot pass. Every child stays in process.py's owned group;
90sec inner/120sec outer deadlines,2MiB serial and16MiB file bounds plus cleanup
receipts apply. Fresh firmware variables per VM; tools/environment/inputs retained.

Normal owner10152bytes, omitted-close control10184 and exhaustion1077 remain below
16384. Static ELF inspections and sealed raw/ELF identities match; reused scoped
stack estimates are2696/4088 for normal/control and336/4088 for exhaustion. These
are producer estimates with immutable-builtin assumptions, not independent all-path
or kernel-stack verification. Five legacy compatibility rebuilds remain producer
coverage; this consumer does not claim five additional legacy native executions.

Reproduction: `python3 -B docs/evidence/si07-loop-consumer-2026-10-03/run.py prepare`
and `.../run.py replay`; `.../check-oracle.py` checks the retained producer traces.
Drivers reject reused output roots; select a fresh packet or restore the complete
retained work archive for inspection. Native results and source/stream/process
receipts distinguish all attempts. Original harness BSD-2-Clause; borrowed driver
lifecycle derives from the earlier sealed SI-07 consumer with provenance retained.

No current external blocker is established for the next bounded work. Sys-init
continues focused partial/unknown reply, cleanup-failure and broader idle/wakeup
controls, then useful-session composition. Userland native child-profile/malformed/
stale/foreign and partial/poisoned-close qualification, reader/SDK disposition and
full M3/R1 acceptance remain open. No sibling writes/messages, authority transfer,
standard pin changes or cross-project completion decisions were made here.

All573 completed work files were archived and read back with hash/size/mode/namespace
checks before removing redundant build outputs;31,207,424 allocated build bytes
were reclaimed. [Retention](retention.json) records the recoverable archive/index.
Selected source, producer metadata and native/host cleanup receipts remain in this
packet. The oracle also supports the retained packet after compaction and verifies
each trace pin before comparison. Earlier producer packets and sibling outputs
remain untouched. Local quality, syntax and whitespace gates pass.
