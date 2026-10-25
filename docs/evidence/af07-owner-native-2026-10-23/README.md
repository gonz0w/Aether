# ABI31 native qualification —2026-10-23

Current status: the common clock correction is implemented and the final matching
three-guest sequence passes. Only hardware Accessed bit5 may differ; source, frame
and every other flag remain exact, and observed Accessed is preserved. Temporary
state logging is removed after preservation in commit2348402be.

[Decision0219](../../../sys-init/docs/decisions/0219-clock-attach-assertion.md),
[review](../../reviews/2026-10-23-af07-kernel-panic.md),
[final preparation/check hashes](clock-fix-prepared.json) and [attempt8](attempt8.json)
record verification and limits. Earlier generic-only failures remain individually
unattributed, never waived by later passes. No independent persistence acceptance
or persistent Zsh/ISO claim.

| Attempt | Result | Recovery |
| --- | --- | --- |
| [1](attempt1.json), [approval](approval.json) | Pristine reader passes; writer7/0/0/21 cleanup/halt1842 rejected at wait identity; VMs stopped | Not run |
| [2](attempt2.json), [approval](approval2.json) | Pristine passes; writer7/0/0/21 cleanup/halt1975 rejected at wait framing; complete capture attributes eight prefixed wakes; VMs stopped | Not run |
| [3](attempt3.json), [approval](approval3.json) | Pristine passes; actual generic kernel panic; full capture/media effects unavailable; VMs stopped | Not run |
| [4](attempt4.json), [approval](approval4.json) | Fixed caller diagnostic passes7/0/0/21 cleanup/220 paired waits/halt1958; no panic/PC; VMs stopped | Full780248-byte original file/unchanged recovery media pass |
| [5](attempt5.json), [batch approval](approval5-batch.json) | Batch stops at first writer generic assert; PC only identifies std.debug.assert; full23665-byte transcript/stopped media captured; VMs stopped | Not run; sequences2/3 canceled |
| [6](attempt6.json), [direct instruction](approval6-clock.json) | Selected clock-state diagnostic passes all three guests, no failure row/PC | Full original-file/unchanged recovery media pass |
| [7](attempt7.json), [continuation](approval7-clock-continuation.json) | Second clock diagnostic stops at clock.attach assertion; ready1/have917a023/want917a003; VMs stopped | Not run; final clock sequence canceled |
| [8](attempt8.json), [conditional fix instruction](approval8-clock-fix.json) | Corrected composition passes7/0/0,21 cleanup,220 paired waits/halt1894; all VMs stopped | Full780248-byte original file/unchanged recovery media pass |

Attempt2 framing attribution accounts for220/220 paired waits after diagnostic
producer-newline projection; raw failed text remains rejected by the strict oracle.
Attempt1 lost its full capture. Attempt3 generic panic remains individually
unattributed. Attempt4 nonrecurrence does not identify or resolve that old failure.
Attempts5/7 preserve full bounded failure capture and stopped media; outside-region
canaries match, metadata effects possible, export/reclaim and fresh original-file
recovery unconfirmed. Failed writer disposal follows confirmed VM stop only.
No failed sequence becomes success. Exact traces, media/tool/artifact hashes and
short logs remain in the linked compact JSON records.

Bounded [generic inspection](assert-inspection.json) proves PC points within
std.debug.assert; no kernel caller inference from that alone. Whole-file objdump
hit its existing4MiB host cap; retain the failure/hash, then use bounded function
ranges. [Clock inspection](clock-assert-inspection.json) binds the exact pending
ELF, source and diagnostic-before-assert instruction path to attempt7's values.
The failing diagnostic predicate is preserved in commit2348402be; final source corrects only Accessed.
No unwinder, assertion bypass, new authority or runtime limit change.

[Clock preparation](clock-prepared.json) records fresh enginev9/activationv5/
guardedv4 and focused checks. Owner39376/49152 code,7504/8192 resident and8000/8184
conservative stack fit unchanged. Debug/ReleaseSafe actual attach tests cover all64
bit changes, absent source/wrong frames, no failed writes and compiling observation
omission; initial scaffold shadowing failure is preserved.33 other clock/elapsed,
corrected new method, six owner/panic/framing consumers, five Zig clock models and
11 fresh qualifier methods pass. Workflow/experience/standards/component static/
format checks pass. Earlier930 Python/162 Zig checkpoint retains its own scope;
no repeat broad-suite claim for this diagnostic.

The maintainer directly instructed continuing clock diagnostics, fixing only after
cause is known, batching and current limits. [Clock continuation preparation](clock-followup-prepared.json)
binds the two same-runtime follow-ups: maxthree clock sequences/nine guests total.
It stopped on the first unexpected result; the last sequence did not execute.
No stopped-batch resumption or retry. These receipts/commands are historical and
are not authorization to run another guest. Only current final-fix preparation
may become an active run command after its review.

All current limits stay: writer60s6000/readers30s3000,35MiB/seven domains/twelve
channels,49152 owner code/8192 stack/data,64KiB capture and zero FS mutation requests.
Import/export may write metadata; separate9/96 storage qualification remains.
No release pins/old seals change. Keep compact results and current dependencies,
remove owned generated outputs after stop/inspection. Public persistent paths/CWD,
loader/writes, remaining process cases, packages and Zsh/TTY/ISO remain open.

Final preparation records the initial ineffective frame-mask test-control failure
and corrected pass,931 Python/all Zig final checkpoint,11 qualifier methods and
fresh enginev10/activationv6/guardedv5. Owner measurements/limits remain exact.
Final native success retains compact commands/tool/input/result/media hashes and
short terminal/cleanup summaries; pass transcripts, images, ELF, media and owned
intermediates are disposed after confirmed stop. No full test/build archive.
