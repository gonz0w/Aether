# UL-069 corrected-emulator consumer regressions

The [preceding build/runtime approval](../qemu-offline-build-2026-09-07/maintainer-review.json)
is recorded with exact source hashes. This new consumer slice uses the same
patched QEMU, GNU/BusyBox binaries, staged GLib/libatomic and pinned Linux image.
It does not establish native Aether behavior or final provider acceptance.

## GNU shell/terminal result

[Extended summary](gnu-extended/summary.json) and [raw report](gnu-extended/guest.stdout)
retain all six script/control results. C-locale tr, eleven row/column checks and
invalid-input checks pass with the earlier exact expectations. The no-terminal
control still skips 77. The ISO-8859-1 locale remains unavailable.

The unchanged option-pair script now exits 0, retains all 9,029 traced stty calls,
and restores both termios and window size exactly. There are zero “unable to
perform” failures; the previous run had 188 CMSPAR failures. No pairs were removed.

The main stty script still exits 0 while changing c_cflag from 191 to 852159.
Window size is unchanged. The independent restoration oracle remains false;
the combined extended result is **INCOMPLETE**. Its final speed checks occur
after upstream's restoration. PTY descriptors close and container absence is
confirmed; endpoint closure is not counted as restoration. Future explicit
recovery must be measured separately, without relabeling natural cleanup.

## Common provider comparisons

[Final common run](common-final/summary.json) repeats seventeen fixtures per
provider. GNU matches 17/17. BusyBox matches 13/17, retaining exactly repeat,
print-class, invalid-class and reversed-range failures. Both providers' terminal
checks pass. Stable BusyBox differences remain incomplete provider acceptance.

The [first common attempt](common-first/summary.json) passed GNU but failed before
BusyBox's final report: staging the multicall executable as stty caused basename
selection plus an explicit stty argument. Its stderr records “no terminal state”.
The adapter now preserves busybox_unstripped and explicit applet argv. The failed
source version and all cleanup receipts are retained; no fixture was weakened.

## Upstream tr rerun

[Final upstream results](upstream-final/summary.json) pass all 134 GNU tr cases,
then correctly reject the exit99 wrapper across the same complete inventory.
All five BusyBox focused tests pass. GNU compares stdout, stderr and exit status;
BusyBox's unchanged upstream harness checks stdout only.

Two infrastructure attempts remain retained: [first](upstream-first/summary.json)
used an unwritable initial directory (exit30 before fixture completion); explicit
cd /scratch corrects it. [Second](upstream-second/summary.json) completed the GNU
inventory but failed two exact stderr comparisons because the binary was renamed
candidate-tr. Preserving bin/tr restores the expected diagnostic prefix. No
upstream comparison or expected output changed. Every created container was
removed with absence confirmed, including all failed attempts.

## Scope and follow-up

All runtime output stays in private build roots and is copied here as evidence.
The unchanged owned adapter uses read-only inputs, no network/capabilities,
uid65534, 512 MiB and 32 PIDs; every created container must be observed absent.
The older guest subprocess implementations are reused within their existing
migration boundary, not newly certified as fully hardened process owners.

Review plans: [GNU shell](CONSUMER-PLAN.md), [common](COMMON-PLAN.md),
[upstream tr](UPSTREAM-PLAN.md). Source and input hashes accompany each attempt;
upstream sources and notices remain unchanged in the referenced private roots.
The maintainer approved this consumer slice; [review receipt](maintainer-review.json)
binds the statement and current sources. Separate reader walkthrough logs were not supplied. UL-069
remains active for recovery/review disposition. UL-066 retains provider differences,
locale/static fault-injection and source review; UL-008 retains native terminals.
