# UL-007 malformed-backend consumer qualification — 2026-09-10

PASS: all 401 original native command cases reproduced locally. The
[native receipt](native-results.json) binds exact commands, tools, artifacts and
case inventory; the [outer receipt](results.json) records exit 0 and complete owned
process cleanup. All 549 source/4311 SDK file hashes remained unchanged. One local
native attempt passed, with no failure or interruption.

[41 independent final serial checks](backend-regression-cases.json) pass: three
malformed-backend cases complete client 1/stream 17 twice with supervisor 100/reclaimed 6;
omitted stop rejects 1601 after client 1 with zero reclaims. Prior 37 focused cases
regress. Expected/observed arrays, panic records and digests are retained; all 401
serial/QEMU logs are under cases/.

## Selected recovery

This consumes the completed 401-case shell-file-backend-recovery-2026-09-09 packet,
following the [local 397-case client-reply recovery](../dash-file-recovery-consumer-2026-09-09/README.md).
The final runtime inputs match the [prepared static review](../dash-backend-intake-2026-09-09/README.md);
only captured STATE/contract prose changed. The former pending packet is now sealed.

Three real file-service mutations corrupt reserved reply byte 12 after open/read/
close. Forwarding validates the entire response before publishing a handle, changing
an offset or retiring a record. Uncertainty closes client delivery and rejects later
traffic; no operation is replayed and no unknown handle is guessed. The existing
poison client requires EIO, unchanged buffers, no partial publication, consuming
local close, restored mask and no further channel calls, then exits 1.

After observing that termination, the owner requests scoped file-service stop and
checks encoded 144/kind 3 before clearing descriptions. Later cleanup checks decoded
143/kind 3 again before reclaim. A stop acknowledgment or lack of output is not the
oracle. Forced stop has no normal slot 2 exit line: exact serial records contain
client 1/stream 17 for both generations and supervisor 100/reclaimed 6. The omitted-stop
control must reject 1601 after client 1, with zero reclaims.

The final independent checks cover the four new cases and prior 37 main/admission/
description/reply controls using completed receipt digests and exact terminal,
supervisor and panic records. Semantic publication, validation, masks and terminal
queries remain reviewed guest/owner assertions. Zero-reclaim mutants detect faults,
not successful native recovery. Host process cleanup is separate.

## Provenance and constraints

Producer manifest SHA256:
`8ca0ebb9eaebc3dcea545e7270ec41116dad58dae0b453ac2d93ecab5e363258`.
All 100 sealed entries verify before use and retention. producer-packet/ retains
final sources/receipts and failed image/size/lifecycle attempt history.
packet-retention.json names verified target archives omitted from this copy.
[Intake](intake.json) verifies selected source changes and 32 original dash objects. Seven selected files differ from the prior
runtime: STATE/contract/workflow, harness, owner forwarding/shared exchange and file
service mutation. No kernel/build/shared ABI/quota/default/released-pin change.
Original 32 dash objects and separately selected main remain pinned. No fresh SDK/
dash source build, local M4/host-kernel or minimum-interpreter qualification claim.

Preserve producer image-limit failures, size-only preflights and the incorrect
forced-stop normal-exit expectation with their original reports/sources. An earlier
supervisor 100/reclaimed 6 does not turn a failed full suite into a passing one.
Checked caller-owned zeroed reply storage and out-of-line shared encoding keep the
existing 8192-byte owner bound; verify all four final new image sizes locally.

Run `python3 -B docs/evidence/dash-backend-consumer-2026-09-10/run.py` with recorded
pinned dependencies on Python 3.14.7. Private output remains under
`build/dash-backend-consumer-aacy75li`. Native receipt binds exact 401-case order,
compiler flags/ABI/tools/artifacts; outer receipt binds controlled PATH/LC_ALL/
private TMPDIR, 1800-second deadline, 512 MiB output bound and cleanup. Source/SDK/
tool/libc/main-object hashes are verified before use; source/SDK after. No sibling
writes, runtime-oracle modification, real-prefix installation or monitoring.

## Newer producer deliveries and next intake

[Verified inventory](next-deliveries/inventory.json) records six later completed
producer packets, with retained README/manifest identities. Their target results
have not been reproduced locally in this qualification:

- Backend EOF and timeout/late-reply controls progress beyond complete malformed
  replies. The timeout packet changes all command-backend exchange polling to 4096
  attempts; generic transport remains 100000. Review that behavior change explicitly.
- ENV execution covers guarded loading/suppression and unsupported -p; syntax-error
  execution covers the unchanged consumer script. Neither is yet local acceptance.
- The 431-case helper-child delivery carries forward that command-suite progress.
  It runs the real helper through an explicit image launcher, not dash fork/exec/
  waitpid; unchanged DASH-argv and signal-table still have process dependencies.
- The 143-connection public-fork callback delivery is a separate isolated source-built
  libc candidate. Its real fork/atfork/signal evidence is not installed SDK support,
  wait/exec integration or independent dash acceptance.

Next select and review the consolidated 431-case command packet, including changed
polling and owner controls, instead of treating each intervening producer count as
a mandatory separate rerun. Keep connections/launch/kernel regressions distinct;
public-fork intake needs its own dependency and source review. Current owner next
action is public wait collection, then transactional exec. Producer progress does
not extend consumer acceptance or authorize sibling changes.

Malformed complete replies alone do not qualify missing/partial/silent/late outcomes.
Local ENV/external-process workloads, source trust, independent technical/reader
review, UL-016/063/081, persistence and full M3 remain open. [Review](review.md)
records pre-execution scope, bounds, simplicity and acceptance limits.

[Local owner-size checks](owner-size-checks.json) verify all four new images;
maximum 7976 bytes within 8192. The bound was not increased.

Final validation: local quality inventory check passed; runtime/source-audit/reader/
publication gates remain separately scoped. Exact executed driver and native receipt
hashes match, retained Python drivers compile on 3.14.7, and changed
tracked planning/coverage files pass `git diff --check`. See [verification](verification.json)
and [quality output](quality.log). The packet manifest binds retained bytes.
