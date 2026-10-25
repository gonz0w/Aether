# 0219: Native clock reattachment assertion rejects the hardware Accessed bit

2026-10-23 / BG-070. Root [review](../../../docs/reviews/2026-10-23-af07-kernel-panic.md)
records the diagnostic, pre-code constraints and test selection. Root STATE owns
integration; [compact attempts](../../../docs/evidence/af07-owner-native-2026-10-23/README.md)
retain every approval, failure, nonrecurrence, exact artifact and bounded inspection.

Approved three-sequence batch stops at its first writer (attempt5): pristine
reader passes, generic debug.assert panic, both VMs stopped, no recovery or remaining
sequences. PCffffffff80004afe maps without warnings to std.debug.assert:420.
Matching ELF confirms the generic call; this alone cannot identify its caller.
Source inspection finds clock.attach's exact non-leaf comparison as a candidate.
It must not be silently weakened. A selected ABI31 diagnostic preserves the same
predicate and records source readiness/observed/expected words before failure.

The maintainer directly instructs continued clock diagnostics, a fix once cause is
known, batching and unchanged limits. Attempt6 passes all three guests without
recurrence; no attribution follows. Two additional same-runtime sequences are
prepared and announced, bounding this clock diagnostic to three sequences/nine
guests total. The continuation stops on its first writer (attempt7); final clock
sequence does not run, no retry or recovery. Both VMs stopped. Failure record:

```
NATIVE CLOCK ALIAS ready=1 have=917a023 want=917a003
NATIVE PANIC pc=ffffffff80004afe
```

Difference is exactly0x20 (bit5). Source is ready, physical frame and every other
flag match. Exact matching ELF/source shows the diagnostic then assert(valid),
confirming clock.attach is the failed assertion in attempt7. Intel SDM Volume3
section4.8 identifies the CPU-maintained Accessed bit on translation entries.
The existing kernel exec path clears low tables but retains kpdp, then load calls
mapKernel/clock.attach again. A legitimate retained Accessed bit therefore fails
the old predicate. Earlier generic-only attempts remain individually unattributed;
none is retroactively accepted. Import/export metadata effects remain bounded to
stopped media hashes/outside canaries; failed attempts lack confirmed engine export/
reclaim and fresh original-file recovery.

Host diagnostic tests execute actual Debug/ReleaseSafe attach:70 selected/old cases
per mode plus two compiling record omissions (282 child invocations). All64 bit
changes, absent source/wrong frame and unchanged memory on failure are checked.
Initial scaffold shadowing failure is retained;33 other clock/elapsed methods in
that run pass. Corrected new method, six mapping/panic/framing consumers, five Zig
clock models and11 fresh qualifier methods pass. Workflow/experience/standards/
component static/format pass. No second broad suite is claimed for diagnostic code.
Fresh enginev9/activationv5/guardedv4 preserve owner39376 code/7504 resident/8000
stack and every existing profile limit. Old seals/released pins remain exact.

Next: correct only the allowed hardware Accessed variation, preserving exact frame,
flags, supervisor/device authority and source readiness; remove temporary selected
clock diagnostic after preserving its source in Git/evidence. Retain the assertion,
add actual reattachment/flag/identity/no-source/no-write tests and compiling semantic
omissions, refresh matching final inputs and verify the fixed native composition
under the maintainer's conditional fix/continuation instruction. This is a scoped
runtime correction, not approval of the first persistent Zsh ISO. Public CWD/paths,
persistent executable loading/writes, further process cases, packages and Zsh/TTY/
ISO acceptance remain open. Same writer60s6000/readers30s3000,35MiB/seven domains/
twelve channels,49152 owner code/8192 stack/data and64KiB capture. Zero filesystem
mutation requests; existing9/96 storage qualification remains separate.

## Scoped correction and final verification

The common kernel attach now permits only hardware Accessed bit5 when matching
the existing physical|3 entry, retains source/frame/every-other-flag assertion and
preserves its observed Accessed state. Temporary selected logger removed; historical
source remains commit2348402be. No owner/worker/authority/resource change.

Actual Debug/ReleaseSafe tests cover repeated attach with simulated hardware bit,
all64 bit alterations with Accessed both states, absent source/wrong frames, no
failed writes and four compiling controls. Initial ineffective frame-mask control
fails in both modes and is retained; corrected control/final method passes. Final
full checkpoint931 Python/all Zig test roots/pins and11 fresh qualifier methods pass.
Fresh enginev10/activationv6/guardedv5 retain39376/7504/8000 measurements. Under the
maintainer's conditional fix instruction, one prepared unchanged-limits native
sequence passes all three guests: helper7/parent0/engine0,21 cleanup,220 paired
waits/halt1894, full780248-byte original-file recovery and unchanged recovery media.
All VM stops confirmed; outside canaries match, import/export metadata changed.
No FS mutation requests/retry or old failure waiver. This verifies the scoped
clock correction in the fixed composition, without independent persistence/release
acceptance. Root STATE owns remaining process refusal/continued-parent/copy-exhaustion,
public CWD/persistent paths/FDs/ELF loading, packages and Zsh/TTY/ISO work.
