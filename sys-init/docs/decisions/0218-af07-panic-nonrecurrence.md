# 0218: Passing caller-site diagnostic does not resolve the previous kernel panic

2026-10-23 / BG-070. Root STATE owns integration. The existing
[panic review](../../../docs/reviews/2026-10-23-af07-kernel-panic.md) now includes
the bounded follow-up proposal; [compact results](../../../docs/evidence/af07-owner-native-2026-10-23/README.md)
bind approval4, attempt4, frozen inputs and any pending diagnostic receipts.

The maintainer approved exactly one caller-site diagnostic against receipt
686900a24f6ce5471608c4d82abc827cd82f3d09601d6b650ddf9e3d5cc7522d.
It passed all three guests: pristine reader verifies the full780248-byte original
file with unchanged media; writer executes the fixed immutable helper, observes
exit7 then parent0/engine0, all21 cleanup rows,220 paired waits and halt1958/6000;
fresh read-only recovery verifies the complete original file and unchanged stopped
writer media. All three VM stops confirmed. Outside-region canaries match. Writer
media differs from pristine; import/export metadata writes were possible. No
filesystem mutation requests or newly written application-file recovery claim.
Source-bound engine return/shutdown and native reclaim are distinguished from an
independent original-OpenZFS export witness. No conformance observation was added.

The panic did not recur. No caller PC exists to symbolize, so attempt3 remains
unattributed, including unknown metadata effects and unconfirmed engine teardown.
Do not claim this instrumentation fixed it, infer a cause from the last wait, accept
the earlier failure, or promote the passing diagnostic to persistence acceptance.
The one-sequence approval is consumed. No automatic retry or further guest ran.

Proposed next diagnostic: exactly three fresh sequences, serially, maximum nine
guests total. Each unchanged sequence uses new guarded disposable media: pristine
reader → fixed-script writer → fresh recovery only after strict writer success.
Stop the entire batch on its first unexpected result; no retry, replacement trial
or acceptance waiver. Prepare all three matching input receipts before disposition.
Check equal kernel ELF/harness/provider/tool/source closure and each exact ISO hash;
use the already checked PC/failed-capture path if the panic recurs. No new harness,
logger, scheduling modification, native feature, dependency or authority. Three
nonrecurrences would still not establish a root cause or a reliability bound.

Same writer60s6000/readers30s3000,35MiB/seven domains/twelve channels,49152 owner
code/8192 stack/data,64KiB transcript and separate9/96 storage qualification. Keep
old seals and released pins exact. Only pending selected ISOs/ELFs/receipts remain;
confirmed stop/lookup disposes them/media, retaining compact results. Unknown stop
retains affected resources. Prior host930 Python/162 Zig/11 component results are
reused only after exact frozen source/tool/artifact comparison; no runtime bytes
changed. Run documentation/process checks, not another unrelated full suite.
Fresh batch disposition is required by the existing persistence recurrence rule.
Public CWD/persistent loading/writes, native failure/continued-parent cases,
packages, interactive Zsh/TTY and the actual R1 ISO remain open.
