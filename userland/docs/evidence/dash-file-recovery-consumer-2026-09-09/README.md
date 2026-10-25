# UL-007 known-result file-reply recovery consumer — 2026-09-09

PASS: all397 original native command cases reproduced locally. The
[native receipt](native-results.json) records exact commands, tools, artifacts and
case inventory; the [outer receipt](results.json) records exit0 and complete owned
process cleanup. All549 source/4311 reused SDK hashes remain unchanged. One local
native attempt passed, without failure or interruption.

[37 independent completed-receipt serial checks](recovery-regression-cases.json)
pass for ten additions and prior27 focused cases. Exact expected/observed terminal,
supervisor/panic records and digests are retained. All397 serial/QEMU logs remain
under cases/. Six client-reply failures complete client1/stream17/file17 and six
reclaims; both queued mismatches complete110/17/17 and six reclaims. Omitted record
retirement1599 and wrong witness108/1501 reject with zero native reclaims.

## Recovery boundary

This follows the [local387-case file-description qualification](../dash-file-descriptions-consumer-2026-09-09/README.md).
The owner has a checked backend result before damaging delivery to the client.
Six cases complete an open/read/close, then corrupt a reserved reply byte or send
only16 of32 bytes and close the writer. The client must report EIO, mark the
connection poisoned, preserve16 read-buffer sentinel bytes, avoid partial open
publication, consume its local close, restore its native signal mask and make no
further channel calls. It closes remaining local facade entries and exits1.

Only after that terminal may the owner retire known retained records through the
healthy backend and verify stale-handle EBADF/zero payload. Open/read reply faults
leave one record; close-reply faults leave none because the backend close already
completed. No operation is replayed. Empty streams, exact open/read counts,
client1/stream17/file17 over two generations and six reclaims are required.
Skipped owner retirement rejects1599 after client1, with zero reclaims.

Two V3/V4 mismatch cases acknowledge the header and queue16 body bytes, consume
one tagged witness byte and reject with15 unread. They require unpublished state,
client110/stream17/file17 and six reclaims in two generations. V3 has no file facade.
Wrong witness rejects108/1501 with zero reclaims. These are selected queued-byte
disposal/reuse observations, not direct physical queue-zero inspection or fuzzing.

The final independent serial check covers all ten additions and prior27 main,
admission and description cases, using completed receipt digests and exact terminal/
supervisor/panic records. Semantic byte/mask/no-traffic/file-state assertions remain
original guest/owner oracles. Client1 is controlled fault completion, not successful
shell initialization; zero-reclaim mutants establish detection, not native recovery.
Outer VM/process cleanup remains a separate observation.

## Remaining gates

Lost/malformed backend responses and confirmed service-stop cleanup for unknown
outcomes are NOT qualified here. The owner knows the backend result in every new
reply-fault case. General service restart or replay safety must not be inferred.
Actual-main ENV loading/suppression and unsupported -p, existing argv/signal/syntax/
external-child/exec/wait/redirection/pipeline workloads, general filesystem and
persistence remain open. Metadata12-row bounded evidence is unchanged. UL-007/M3,
UL-016/063/081 and independent technical/reader sign-off remain open.

## Provenance and reproduction

Producer shell-file-reply-recovery-2026-09-09 manifest:
`3669907ac119ece9a9f23d62f24ef906510bb6f2d168e4190219a8cf16a73905`.
All11 sealed entries verify before consumption and retention. producer-packet/
retains the source archive and receipts; packet-retention.json identifies the
verified target archive omitted from this copy. [Intake](intake.json) verifies
the source differences and original32 reference object hashes. Seven source files differ from the
prior snapshot: owner/client/harness/counter selection and three documents. Normal
adapter, kernel/build/service protocol/quota and pinned dash objects remain unchanged.
The source archive/receipts are retained; packet-retention.json identifies verified
target archives omitted from this copy. Predecessor failure history remains retained
in earlier local packets. No sibling/default/released-pin edit, fresh M4/host-kernel
result, new SDK/dash build or minimum-interpreter qualification claim.

The existing owner-image bound is8192 bytes; producer maximum8056. [Local image-size
checks](owner-size-checks.json) retain all ten new owner sizes/hashes; maximum8056 bytes. This constraint
remains visible for the next uncertain-backend implementation; no bound is increased.

Run `python3 -B docs/evidence/dash-file-recovery-consumer-2026-09-09/run.py` with
pinned dependencies on Python3.14.7. Private builds remain under
`build/dash-file-recovery-consumer-vygl8nxh`. Original receipt binds all397 cases,
compiler flags/ABI/tools/artifacts and order; outer receipt binds controlled PATH/
LC_ALL/private TMPDIR,1800-second deadline,512 MiB output bound and owned cleanup.
Source/SDK/tool/libc/main-object hashes are checked before use; source/SDK after.
[Review plan](review.md) records source assessment, ownership, bounds, oracles,
simplicity and pending independent review. No full file-root or M3 acceptance.

Final quality gate, driver/retention syntax, driver/receipt identity and tracked
document whitespace checks pass. Pins/inventory checks do not provide pending
independent technical or reader approval.
