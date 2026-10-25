# Native 8-MiB backing experiment — 2026-09-06

[Contract, commands and result](../../NATIVE-MEMORY.md#extended-backing-result--2026-09-06).
Explicit native-memory-large selects 2048 eager private pages per slot; default
remains 128. No ELF admission expansion, threads, native OpenZFS or consumer
adoption is claimed. No sibling or immutable pin changed.

## Final qualification

qualified/results.json records frozen runtime/build inputs, exact top-level argv,
UTC intervals and exit codes. All five top-level commands exit 0: host test,
Zig format, large memory suite, default memory suite and default two-core boot.
qualified/sources.tar.gz preserves those sources. review-inputs.json and the
retained new oracle test/workflow files identify supplementary review inputs.
The strict musl archive/compiler/linker identities are checked by the existing
producer builder and recorded in each target suite's evidence. Kernel uses Zig
0.16.0 Debug; C producer uses the retained strict native musl/Clang tool closure.

Twelve large cases and eleven default cases pass. Large positive and replacement
admissions report 24 used/2024 free pages, and default reports 24/104. The native
query and allocation checks agree. Large tests cover full byte verification,
cross-leaf permissions, middle-leaf release/reuse, retained neighbors, real faults
on the second leaf with peer completion, missing/stale grants, full quota, metadata
retry, unmap-zeroing rejection and stop with live allocations followed by reuse.
Three saturation rounds bound the large workload; default retains forty rounds.

The inverted middle-leaf placement expectation must reject at worker result 129.
Skipped protection must reject at the new cross-leaf denial check, result 123.
Other semantic negatives keep their original expected reasons; watchdog/boot
failure and unrelated panics cannot satisfy them. Host checks pass all kernel
models and 88 Python tests, including wide slot 2047/quota and three diagnostic
oracle checks. Standards/workflow and formatting pass. The default two-core boot
passes with framebuffer capture. invalid-profile.json/log records rejection of
large backing without the required native memory option.

## Attempts and triage

before.tar.gz retains the initially selected files, and attempt-1-sources.tar.gz
retains the first large target implementation. Initial host checks passed before
the inventory update. host-2.log then rejected --large incorrectly listed among
native_smoke's envelope selectors. It belongs to the existing memory suite; the
AT-MEMORY test-group entry now records both modes. The checker was not weakened.
workflow-attempt-1.json preserves the erroneous inventory.

The first large target suite passed its twelve oracles. A subsequent frozen run
(final/) passed both modes and boot, but inspection found the admission logger
still subtracted from 128. Runtime query/allocation were correct; the log was not.
That earlier run is not final acceptance. qualified/ repeats all checks after
correcting the logger and adding admission-budget validation. old-log-rejection.json
shows the final oracle rejects the retained incorrect large log for the exact
budget reason. The large fault probes were also moved to the second leaf before
final qualification, instead of relying on first-leaf faults for wider coverage.

All five target suites and both complete boot directories are retained in
target-attempts.tar.gz, including kernels, ISOs, envelopes, build receipts, serial
logs and framebuffer evidence. No previous attempt is overwritten. qualified/ is
the authoritative final run; raw setup/development commands lack individual UTC
receipts, and inherited suite internals retain commands/hashes without per-command
UTC intervals. Top-level qualified intervals are complete. The one-off qualify
wrappers are evidence, not new supported developer entry points.

## Boundaries

Only the opt-in profile reserves four 8-MiB backing bundles and expands kernel
alias coverage to 64 MiB and its BSP interrupt stack to 64 KiB. Fixed stack and
memory limits are experimental bounds, not measured high-water or an engine cache
budget. No heap/global pool, lazy allocation, file mappings or SMP memory grants.
The existing static ELF file/image/TLS caps still apply. Default quotas and marker
schemas remain stable; the new profile is explicitly selected, not consumer adoption.
Independent review, optimized-mode/extended evidence, native engine integration
and the assembled shell/package release remain open. SHA256SUMS covers all files
except itself. Original work remains BSD-2-Clause and third-party terms unchanged.
