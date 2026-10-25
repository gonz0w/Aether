# Real TLS shell relink qualification — 2026-10-22

UL-007/081/082. [Contract](../../proposals/FS-FORK-TLS.md) and [pre-code review](review.md).
Corrects a reproduced loader defect: stage81 had no PT_TLS after removing old
runtime.c. New live C17 initialized volatile thread-local canary checks initial
startup, pre-fork and post-copy_rebind child transition, without production reset.
Four-byte TLS template73736573 and actual native FS-relative access are inspected.
Startup rejects -EIO before greeting, preserving errno; existing entry143/fork116/
child114 failure contracts remain. Existing boot BSS5040/default4952 unchanged.

Final Python3.10.21/3.14.7 runs pass1010 stage cases/nine compiling semantic
omissions, frame5847, default libc78 and opt-in libc78 including corrupted TLS
startup/no greeting effects. Actual host fork checks child-only canary corruption
and unchanged parent; scripted native rebind checks corrupted child114. Hardware/
auxv/rebind observations remain injected; no Aether TLS execution is claimed.
Strict pinned Clang21.1.8 C17/format/UBSan. Complete pinned dash32/CRT/libc/public
fork/copy_rebind static link is byte-identical across the final runs.

Actual unchanged Aether native_elf.zig parser (snapshot hash in parser-input.json)
accepts this exact shell under unchanged default1MiB/128-page limits. Seven Zig
host tests pass: corrected shell/template, original stage81 denial, malformed
TLS/WX rejection and four retained parser tests. Four PT_LOAD segments/63 image
pages plus16 main-stack pages =79 parser-accounted pages. This is actual parser
acceptance, not native loading, whole code/stack/TLS/heap/backing/channel peak fit,
boot execution or affected-owner acceptance. No kernel/parser modification.

One initial full attempt passes1010/nine/regressions/link but fails compilation
of our new Zig test helper because u32/u64 shadow primitives. Renamed only our
helpers; final runs pass. Added the opt-in startup corruption regression before
final runs. Initial attempt and every command/input/source/tool/artifact hash/raw
log/process cleanup retained with final attempts; no hidden retry or source drift.

Separate delivery `build/service-deliveries/filesystem-fork-tls-2026-10-22-v1`,
85 members; manifest SHA256 `f14badab992cf50de4b3443093ccd4b65aa01b1ba1bcf4fa7447672d26b962d4`.
ELF279568 bytes, SHA256 `366287d33cff71c33db24247fb214dd6099bcb6359d28b3f6866e9de11dc2b96`.
Includes exact source/checker/parser snapshot, new/old local contracts, dependency/
command receipts, original licenses and new ELF; no SDK/source-tree duplication.
Checker snapshot requires maintained repository layout and pinned offline inputs.
Stage81/older candidate/evidence/default/release pins remain unchanged.

Next: sys-init consumes corrected shell/file-view18, enforces actual complete
FILE/stream/source/history comparison and native copy/refusal/unknown/greeting/
ready/parent plus terminal/endpoint/holder/readiness/shutdown. Whole fit and fresh
Aether continued-parent/child/wait/error/cleanup/readback follow. Full UL-007/082/
M3/R1, immutable exec/public dup2/wider shell/Zsh/TTY/packages/ISO and independent
owner/reader remain open. No sibling edits/messages, native guest, install,
quota/default/release-pin change or monitoring. Quality/retention receipts follow.

All three exact owned attempts archived and streaming hash/size checked before
removal: 162,887,306 logical bytes removed; 46,327,360 archive bytes
retained. Physical reclamation not measured. Local quality and all three embedded
standards checks pass; minimum/current syntax checks pass. No owner/reader sign-off.
