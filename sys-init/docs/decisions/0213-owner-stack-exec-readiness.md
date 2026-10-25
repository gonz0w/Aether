# 0213: Guarded owner stack, immutable exec and startup readiness

2026-10-23 / BG-070 / UL-007/081/082. Pre-code integration review.

The maintainer approved the separate8KiB guarded stack proposed in0212. Implement
an explicit build selection and AENFS005/ownerABI31, not an enlargement of ABI30.
Stack[0x800000,0x802000) is zeroed RW/NX with initial RSP0x802000-8 and unmapped
0x7ff000/0x802000 guards; it consumes one extra page from the same128-page owner
backing. Keep8192 owner data,35MiB/seven domains/twelve channels,workload9/96,
watchdogs,poll/I/O/authority/cleanup and old profiles/pins exact. Code allowance
remains provisional and unadmitted until the complete owner is measured. The
stack inspector accepts only explicitly selected4096/8192 stack sizes, retaining
all dynamic/recursive/unknown-edge denials and conservative safety margins.

Finish the actual new FILE-channel exec provider and owner together. Use the
existing immutable image commit23007, receipt23008 and publish23009, with exact
observed native freeze tokens distinct from application sequences. Authenticate
the actual process/Peer and compare the full captured FD/stream map to sole-owner
state before effects. Commit CLOEXEC only after the exact image receipt confirms
commit; then publish a fresh context/file generation and check actual readiness.
Known denied exec preserves the old context/flags/offsets and original errno;
unknown commit, cleanup or partial publication stays closed without replay or
invented rollback. Paths are policy selectors, never image/capability authority.
Unsupported general executable loading remains explicit, not a successful stub.

Initial readiness means a decoded, admitted startup context and an actual worker
ready observation, not launch, channel delivery or mere liveness. Keep source/
binding/generation and native grant checks; do not reuse fork-ready as application
readiness. Final code budget with page-aligned headroom follows complete target
measurement and matching parser/loader/entry/stack checks, not partial roots.

Apply Foundations O-01–05/I-01–06/E evidence, adopted CE/CD/CA/unsafe rules and
SE-01–05. Simpler choice: reuse existing kernel commit/lifetime mechanisms and
actual FILE/pipe/context codecs, with one serialized owner and fixed workspace.
The old unrelated exec wire cannot represent this current full binding context;
silently grafting it would weaken validation. Add no broker/cache/allocator/global
table or generic VFS framework. Remove no consumed old profile. Keep component
policy responsibilities and immutable release bytes distinct from experiments.

Tests: focused actual mapping/PTE/zeroing/guards/isolation/entry/parser/selector
and compiling omission controls; old-profile rejections; typed exec validation,
known refusal/unknown/commit/CLOEXEC/stream retention/partial receipt/no replay;
actual producer/consumer frame and startup-ready mismatches; target static link,
resident and conservative whole-stack inspection. Host doubles are not native
authority or scheduler evidence. Freeze qualified inputs, preserve short failures,
commands/hashes/results and remove owned outputs. No archive/image/source bundles.
Fresh changed-composition native acceptance still follows the existing persistence
stop-and-review rule; independent review and R1/ISO acceptance remain separate.

## Measured selection and current qualification

Completed bounded immutable-helper exec and actual initial/exec readiness now
measure39376 code bytes. Select49152 bytes (12 RX pages), leaving9776 bytes/about25
percent headroom. This is a separate AENFS005/AENMX010/ABI31 profile. Old budgets
and sealed bytes are exact. Kernel/Rust binding review corrected the selected
cleanup entry to e002; historical ABI30 validator bytes remain separate.
Runtime3408+4096 workspace fits8192, leaving688. Inspected conservative stack8000
fits8184 usable. No safety margin, denied edge or resource check was removed.

Seven exec failure schedules plus malformed/stale/forged-context and terminal-ready
cases pass; three compiling receipt/CLOEXEC/readiness omissions fail the semantic
oracle. Actual C provider tests cover partial/corrupt replies, exact original errno,
unchanged refused context and readiness; two compiling sequence/return omissions
fail. The C608 frame is decoded by the actual Rust consumer. Both complete static
shell/helper links pass the unchanged ELF/TLS/WX parser. Debug/ReleaseSafe kernels
build with actual engine/shell/helper/owner geometry; no VM or native acceptance.
[Compact results](../../../docs/evidence/owner-exec-2026-10-23/README.md) preserve
failed attempts as well as final results. Native scoped qualification, independent
review and later persistent execution/Zsh/TTY/packages/ISO remain required.
