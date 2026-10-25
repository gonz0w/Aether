# UL-007 bounded file-description consumer — 2026-09-09

PASS: all387 original native command cases reproduced locally. The
[native receipt](native-results.json) binds exact commands, tools, artifacts and
case order; the [outer receipt](results.json) records exit0 and complete owned
process cleanup. All549 source/4311 reused SDK hashes remained unchanged. One
local native attempt passed, with no local failure or interruption.

[27 independent completed-receipt serial checks](description-regression-cases.json)
pass for the three new description cases and prior24 admission/main controls.
Expected/observed terminals, supervisor/panic records and serial digests are retained.
All387 serial/QEMU logs are preserved in cases/. The positive description case
reclaims six tasks across two generations; both faulty-owner controls reject114/1501
with zero native reclaims.

## Selected behavior

This consumes shell-file-descriptions-2026-09-09 after the locally qualified
[384-case admission packet](../dash-file-admission-consumer-2026-09-09/README.md).
A conformance client tests file-description semantics separately from the unchanged
real dash command/script cases; these new cases do not execute dash main.

| Control | Required observation |
| --- | --- |
| Two opens plus duplicate at10/CLOEXEC | Independent open offsets, shared alias offset, exact bytes |
| Write denial, full16-FD table, nonfinal alias closes | EACCES/EMFILE or successful local close, no transport calls |
| EOF and final close | Nine-byte remaining suffix including newline; zero at EOF; remote description closes |
| Reopen, stale token, wrong binding | Rotated reference; EBADF/zero payload; valid file offset unchanged |
| CWD root, write rights, missing name | EACCES/EACCES/ENOENT; no authority inferred from directory metadata |
| Six successful opens | Each new open starts at zero; next open EMFILE without poisoning |
| Omitted offset advancement / ignored reference matching | Each fails client114/owner1501 with zero reclaims |

Positive completion requires six opens/nine reads, no live file records, empty
streams and client0/stream17/file17 over two generations/six reclaims. The final
wrapper requires one file F_DUPFD_CLOEXEC allocation at or above10. A test-only
counter observes no-traffic cases. Caller pointers/names are fixed valid objects;
this is not arbitrary pointer validation or a general descriptor service.

The independent final serial checks compare completed receipt digests and exact
terminal/supervisor/panic records for all three new cases and the prior24 admission/
main controls. Guest/owner assertions establish byte/offset/rights/no-traffic behavior.
The two mutants detect errors; their zero reclaims do not qualify native recovery.
Outer process cleanup is separate. The actual dash script remains a regression case.

## Remaining gates

V4 queued-body mismatches, malformed/lost open/read/close replies and confirmed
service-stop recovery for uncertain outcomes remain unqualified. Actual-main ENV
loading/suppression and unsupported -p, existing argv/signal/syntax/external-child/
exec/wait/redirection/pipeline workloads, general filesystem and persistence remain
open. Metadata12-row bounded evidence is unchanged. UL-007/M3, UL-016/063/081 and
independent technical/reader review are not closed.

## Provenance and reproduction

Producer manifest SHA256:
`84eef9ab07136d72315bf0acb38f4112239705a7e4c7258442cd2006dac826f0`.
All15 sealed entries verify before use and retention. producer-packet/ retains
the source archive, final receipts, first failed report/log/source archive and
preflight log. packet-retention.json identifies the verified target archive omitted
from this copy. [Intake](intake.json) verifies source differences and original32
dash object hashes. The producer retains a failed first attempt:
a positive test expected eight suffix bytes, but the17-byte script has nine bytes
remaining after the first eight, including its final newline. It failed114/1501
after11 cases. The corrected expected count/bytes were frozen for qualification;
this is a test-expectation defect, not an accepted negative or a local failure.

Seven selected source files differ: sender/client/harness, optional transport-counter
selection and three documentation records. Kernel/build, normal adapter, service
engine, quotas and pinned original/selected-main objects are unchanged. The source
archive and receipts/failure history are retained; the verified target archive is
identified in packet-retention.json when omitted from this copy. Prior source-build,
M4/host and historical failed-attempt evidence remains in the preceding local packets.
No sibling/default/released-pin change or fresh M4/host-kernel claim.

Run `python3 -B docs/evidence/dash-file-descriptions-consumer-2026-09-09/run.py`
with the pinned SDK/tools on Python3.14.7. Private builds stay under
`build/dash-file-descriptions-consumer-a67zz8pt`. Original receipt binds all387 case
names/order, compiler flags, target ABI, tools and artifacts. Outer receipt binds
controlled PATH/LC_ALL/private TMPDIR,1800-second deadline,512 MiB output bound and
owned-process cleanup. Source/SDK/tool/libc/main-object hashes are checked before
use, source/SDK after. No fresh dash/libc source build or minimum-interpreter claim.

[Review](review.md) records pre-execution scope, ownership, bounds, oracles,
simplicity, test selection and pending independent technical/reader sign-off.

Final quality gate, driver/retention syntax, driver/receipt identity and tracked
document whitespace checks pass. Pins/inventory verification does not supply
pending independent technical or reader sign-off.
