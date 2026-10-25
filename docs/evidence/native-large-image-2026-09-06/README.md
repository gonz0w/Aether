# Large static executable admission — 2026-09-06

[Contract, commands and results](../../NATIVE-C.md#large-static-image-result--2026-09-06).
This is a native Aether static-musl fixture, not the Linux OpenZFS executable or
an assembled filesystem/shell. Original sources remain BSD-2-Clause; upstream
SDK terms are unchanged. No companion source or consumer pin changed.

## Inputs and acceptance

contract.md records the preimplementation scope. before.tar.gz retains the
selected files at turn start, including inherited work. qualified/sources.tar.gz
freezes runtime/build sources and tests for full verification. qualified/results.json
records top-level exact argv, UTC intervals and exits for host, Zig/C formatting,
nine image cases, twelve large memory cases, eleven default memory cases and
default two-core boot. Every top-level command exits 0. Host output reports 92
Python tests plus the kernel tests and offline standards/workflow checks.

elf-layout.json records the initial successful fixture's ELF structure: 2,105,728
file bytes, 1541 load pages, plus 16 fixed stack pages. The native admission log
reports 1557 used/491 remaining out of 2048. The producer contains 2 MiB of
initialized data and 4 MiB of BSS, verifies every byte and dirties its writable
image and anonymous allocation. Replacement receives fresh initialized bytes and
zero BSS/backing after stop/reclaim. TLS and 64 yields remain checked in both
contexts. This is not a resident-memory, throughput or stack-high-water measurement.

Nine image cases require specific outcomes:

- Positive and stop/replacement complete their native markers and byte checks.
- Without native-image-large, the same image fails the legacy envelope limit.
- PIE, W+X, mapped-quota excess and ELF file size >8 MiB reject as invalid native ELF.
- Stack and anonymous-arena overlap preserve structural validity and reject as
  invalid native layout. Every rejection requires absence of worker admission.

Host parser tests separately cover the exact 2048-page ceiling and one-page
excess, default quota preservation, bounds on parser limits, larger files and
retained static/permission restrictions. Mutator tests verify the intended header
changes and preservation of separate TLS/RELRO storage. invalid-option.json/log
records exact rejection when the required large backing option is missing.

## All attempts and final tool check

The first target attempt built both producer ELFs, then failed while preparing
controls because it assumed exactly one writable LOAD. The linker emitted separate
TLS/RELRO and large data/BSS LOADs. No kernel workaround was made: the control now
selects the largest writable LOAD and has a regression for the separate segment.
target-1.log and that suite's source snapshot/receipts are retained. target-2.log
records the first complete nine-case pass. Initial host checks also passed.

After full qualified verification, the only source change sent the new runner's
progress messages to stderr as required by Experience. final-scope.json identifies
that sole changed script. final/results.json and final/sources.tar.gz bind the
final sources and repeat host plus all nine image cases successfully. Memory,
boot, build and producer sources are identical to qualified/; repeating unrelated
runtime suites for a progress-stream change was unnecessary.

target-attempts.tar.gz retains all four image attempts, both memory suites and
the complete boot output, including kernels, envelopes, ISOs, build logs, serial
logs and framebuffer evidence. No failed attempt was discarded. The new runner
records per-kernel-build and target UTC intervals; the reused native-musl builder
records commands/tool hashes but lacks per-subcommand timestamps. Initial ad-hoc
commands also lack complete structured intervals; no retroactive full evidence-
standard claim is made. The one-off orchestration wrappers are retained evidence,
not new installation tools. The supported experiment entry point is documented
in NATIVE-C.md and inventoried in workflow.json.

## Boundaries

Only the explicit startup/supervision profile expands; other bundle APIs remain
at their old limits. Generic ELF validation and native geometry preflight precede
user mapping. Copy pointers stay within one validated private backing page; input
image storage remains separate. The kernel retains a bounded 8-MiB supervisor
image buffer and does not introduce a dynamic allocator or ambient file authority.
The 64-MiB kernel alias cap remains enforced before entry.

Native threads/waits, engine platform port, Rust filesystem/namespace, actual
file-backed executable selection, consumer review and assembled shell/package
boot remain required. No independent review, optimized-mode or physical/extended
qualification is implied. SHA256SUMS covers every retained file except itself.
