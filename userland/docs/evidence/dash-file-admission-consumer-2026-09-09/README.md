# UL-007 V4 file-root admission consumer — 2026-09-09

PASS: all384 original native command cases reproduced locally. The
[native receipt](native-results.json) binds the exact case inventory, tools,
commands and artifacts; the [outer receipt](results.json) records exit0 and complete
owned-process cleanup. All549 source/4311 SDK file hashes remained unchanged.
One local native attempt passed, with no failure or interruption.

[24 independent final serial checks](admission-main-cases.json) pass: fourteen
malformed-root rejections with six reclaims, one early-publication mutant rejected
with zero reclaims, and the prior nine main/file execution controls. Exact expected/
observed terminals, supervisor/panic records and serial digests are retained.
All384 serial/QEMU logs are preserved under cases/.

## Selected admission controls

This follows the [local actual-main/script qualification](../dash-file-consumer-2026-09-09/README.md)
and consumes the completed shell-file-admission-2026-09-09 packet. Fifteen new
selections exercise the existing file-root admission boundary:

| Input/control | Required observation |
| --- | --- |
| Missing root; aliases to stdin/stdout/stderr/CWD | Client110/stream17/file17, two generations, six reclaims |
| Wrong rights/kind/generation/reserved tail | Same rejection and cleanup |
| EOF after192/208/223 total bootstrap bytes | Same rejection and cleanup; writer closure accounted for |
| Header-only V3/V4 mismatch in both directions | Same rejection and cleanup; V3 receiver has no file facade |
| Early root publication before reserved-tail validation | Client113/owner1501, exact rejection panic, zero reclaims |

Normal rejections require unpublished descriptors/identity/CWD, zero client protocol
requests, no file open/read and empty stream sinks. V4 receivers additionally check
zero root and open EAGAIN before and after rejected admission. The test-only early
publication mutation must fail this oracle; its zero-reclaim result detects a bug
and does not establish successful native recovery. Host process cleanup is separate.

The focused serial checks use completed receipt digests and compare exact terminal,
supervisor and panic records. Guest/owner assertions establish the publication,
request, output and file-operation observations. The prior nine main/file cases
remain selected alongside all15 admission cases; exact output/cleanup requirements
are unchanged. Actual dash command and script execution remain bounded by the
existing explicit read-only basename root and controlled no-ENV environment.

## Remaining scope

This covers selected root fields, EOF points and header-only V3/V4 mismatches.
It does not qualify queued incompatible V4 bodies, arbitrary truncation/fuzzing,
file-description exhaustion, independent opens/shared-offset/stale-reference cases,
malformed/lost replies or confirmed service-stop recovery. Full-main ENV loading/
suppression and unsupported -p, existing argv/signal/syntax/external-child/exec/wait/
redirection/pipeline workloads and persistent filesystem integration remain open.
No general filesystem, interactive shell, full M3 or independent review acceptance.
The12 metadata checklist rows retain their preceding bounded-evidence status.

## Provenance and reproduction

Producer manifest SHA256:
`09cdcd6960d6b6b5d39d1b1664365c87dcb5fc07a391e1d32554795c4856238c`.
All11 sealed files verify before consumption and retention. producer-packet/
retains the source archive and receipts; packet-retention.json identifies the
verified target archive omitted from this copy. [Intake](intake.json) confirms
the source differences and32 original dash object hashes. Seven selected files differ from the
last local file-root snapshot; normal adapter, service engine, kernel/build/shared
transport and upstream objects are unchanged. No sibling/default/released-pin edit.
Prior main-object build, failed producer attempts and M4/host history remain retained
in the preceding local packet; this step claims no fresh local M4/host-kernel run.

Run `python3 -B docs/evidence/dash-file-admission-consumer-2026-09-09/run.py` with
recorded dependencies on Python3.14.7. Build output is private under
`build/dash-file-admission-consumer-ox8e0oqa`. The original native receipt binds
compiler flags, target ABI, tool hashes, artifacts and all384 case names/order.
The outer receipt binds controlled PATH/LC_ALL/private TMPDIR,1800-second deadline,
512 MiB output bound and process cleanup. Source/SDK hashes are checked before and
after. No fresh SDK/dash source build or minimum-interpreter qualification claim.
Original32 reference objects and separately selected guard-enabled main stay pinned.

[Review plan](review.md) records ownership, source assessment, bounds, oracles,
simplicity and pending independent technical/reader sign-off. UL-007/M3 and
UL-016/063/081 remain active; the larger case count is not milestone completion.

Final quality gate, driver/retention syntax, driver/receipt identity and tracked
document whitespace checks pass. Pins/inventory checks do not provide pending
independent technical or reader sign-off.
