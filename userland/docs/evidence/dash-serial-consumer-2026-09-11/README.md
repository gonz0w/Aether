# UL-007 serial shell consumer — 2026-09-11

**PASS: 303 native QEMU cases and six independent serial-protocol checks.** Actual
dash launches `/next`, collects child status 72, returns to its prompt, accepts a
later host command, prints 72 and exits 0 then 7 in two sessions with six reclaims.
The completed host-only tree also passes Zig/host/workflow checks, including 99
Python tests. Intake-driver and host-inventory failures are retained below.

| Native suite | Passing cases |
| --- | ---: |
| Connections, copy/fork/wait/exec and dash | 241 |
| Launch | 5 |
| Serial console ABI18 | 2 |
| Composed-init bounds | 32 |
| Init-large bounds | 23 |

[Independent serial checks](serial-checks.json) bind exact terminal/supervisor/panic
records and ordered host events for six cases. The resumed positive requires four
prompts, six separate host writes, child termination before continuation and two
printed statuses. The old cleanup gate rejects parent 0/owner 2131 with zero
reclaims; wrong second exit rejects parent 8/owner 2130 after only two earlier
reclaims. Original tee input and wrong child input are detected. Normal one-line
serial execution remains a regression. Fixed fixture strings do not grant authority.

One UART backend lives across both sessions; its reused slot is denied the still
open grant. Owner assertions check 22/27/4 input/output/diagnostic bytes per resumed
session, shared descriptor closes and retained wait collection. Final serial checks
are independent of those internal assertions. The [six serial owner images](owner-sizes.json)
fit the selected ABI18 16 KiB bound; maximum 9528 bytes. Earlier 8 KiB profiles keep
their original limits. No userland or sibling implementation limit was changed.

## Inputs and reproduction

Selected producer: shell-resume-2026-09-11, manifest SHA256
`edf9e13d6097fb22a686b7d4e113cda7f47372b8789ffbdcbdcb36812e7a71d1`.
All 35 entries verified before consumption; use frozen run-sources, not later prose.
producer-packet/ retains sources, receipts and logs; the target archive was verified
at its producer location and omitted here. [Retention record](packet-retention.json).
All 578 assembled source and 4311 SDK file hashes remained unchanged. The musl source
archive matches the SDK source receipt. No installed SDK patch or new source fetch.

Compared with the 431-case consumer, [50 changed/new paths](changed-inputs.json)
include freeze/private copy/exec publication, signal-state candidates, ABI17/18,
private libc hooks, dispatcher and UART backend. The [configuration histories](configuration-history/inventory.json)
retain source patches, object evidence and producer failures for jobs.o/input.o.
The explicit native jobs configuration uses upstream forkshell/shellexec in place
of vfork; input configuration selects the existing one-byte fallback. Original
objects remain controls. This is a private candidate, not general libc vfork or
installed SDK support. Independent source/security/reader signoff remains pending.

[Pre-execution review and corrections](review.md) record authority, lifetimes,
recovery, bounds and test selection. Native receipts bind exact flags, tool/ABI and
artifacts. Python 3.14.7, fixed PATH/LC_ALL/private TMPDIR, original QEMU watchdogs,
512 MiB per-stream output limits and owned process cleanup are recorded. Native
work: `build/dash-serial-consumer-jqf9hnm6`; host-only completion:
`build/dash-serial-host-m__yc2nj`. No real-prefix installation or sibling edits.

## Retained failures and completion

1. [Initial driver](run.py) ran successful connections/launch/console/composed-init,
   then rejected its incorrect expected count 55. The actual producer split is
   32 composed-init plus 23 init-large. [Initial receipt](results.json) is unchanged.
2. [Completion driver](complete.py) verified the exact 32-case inventory and ran
   the missing 23 cases. Its host command was rejected before launch because the
   process wrapper requires an absolute executable. [Receipt](qualification.json).
3. [Absolute host invocation](finish-host.py) ran and failed workflow inventory
   tests because the copied tree lacked docs/NATIVE-INIT-COMMAND.md. The selected
   runtime packet omitted that document. Ninety Zig tests passed, while 99 Python
   tests reported five failures and one error. [Receipt](final-qualification.json)
   and host-absolute logs preserve the failure; they are not passing whole-run receipts.
4. [Host-only completion](check-host.py) copied the original pinned inputs into a
   separate tree and added exactly one [pinned documentation input](host-inputs/pin.json).
   Host tests then passed with the workflow oracle unchanged. [Passing host receipt](host-completion.json).

Every native suite ran once and passed. All started processes have complete owned
cleanup; the rejected host invocation correctly records not-started. No native
source/oracle was changed and no failure was discarded. The final acceptance record
combines individually verified native receipts and the completed host-only result;
it does not relabel the earlier failed records. The original run.py preserves its
count error for audit; use its commands with the corrected split described above,
or review the completion drivers when reproducing this exact historical sequence.

## Remaining acceptance

The fixture permits one external child per shell, two finite serial sessions, no
editing/echo/TTY job control and a fixed delegated `/next` image. It does not qualify
the full twelve unchanged workload scripts, general pipelines/redirection, repeated
external commands, persistent executable loading or sys-init/package assembly.
Next review a completed repeated-child lifecycle delivery, or prepare its consumer
requirements while Aether separates collected-child reclamation from shell lifetime.
Full M3 and UL-016/061–063/081 remain open; no fresh SMP/M4 or release qualification.

Final [acceptance record](acceptance.json) passes identity, native receipt, source/SDK,
serial protocol, syntax and tracked-whitespace checks. [Local quality output](quality.log)
passes the documentation/pin inventory gate; publication and independent reviews
remain separate. SHA256SUMS binds retained bytes, including failed attempts.
