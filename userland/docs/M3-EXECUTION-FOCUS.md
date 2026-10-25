# Execution focus: native userland first

Maintainer direction,2026-09-07: focus on roadmap delivery and retain nonessential
fine tuning for after release. M3 is the next userland acceptance gate. Aether's
own R1/M4 labels do not imply this userland's M3/M4 completion.

## Ordered work

1. Reassess actual producer deliveries. The live Aether tree now contains
   runner-handoff-2026-09-07 and native Toybox cat integration evidence. Old waiting
   notes are stale for UL-059 intake; cat still needs exact independent intake.
2. Verify/pin the runner return bundle, review its role/startup contract against
   our real parser/frontend, and independently rebuild a native command flow.
   Existing bytecount already has native evidence; do not repeat it as new progress.
3. Adopt the smallest compatible real-utility profile from the cat producer work,
   preserving native output/status/reclaim and rejection checks. Producer tests
   are prerequisites, not independent userland acceptance.
4. Advance native dash external-command execution, then redirection/pipeline/wait
   and cleanup. Resolve actual process/FD blockers with explicit owner proposals.
   Help/version polish is not a prerequisite to proving the command path unless
   the chosen contract makes it one.
5. Follow with M4 TTY/jobs/Zsh, then M5 packaged supervision/recovery according to
   the roadmap. Do not expand utility or benchmark matrices on this critical path.

## Retained post-release work

PRF-01: additional tr/provider corner cases, broad locale/Unicode transformation
features beyond the release's explicit byte subset. Existing limitations documented.
PRF-02: additional Linux-reference performance comparisons, larger benchmark/sample
matrices, optimization and richer metrics beyond checks required by release gates.
PRF-03: optional provider alternatives and documentation polish beyond required
user-facing operation/recovery documentation. New helper review can be deferred
only if those helpers are not consumed by release acceptance.

These are deferred work, not completed tests or waivers. Keep current failed
attempts, source pins and evidence. Source authenticity/licensing, actual data or
status correctness, authority enforcement, native cleanup, required release checks
and defects affecting the chosen path remain release gates. Optional reference
work must not displace a concrete native blocker again.

## Current intake boundary

UL-059's producer offers a regular-file source/evidence bundle, AERIO001 four-role
successful-child flow and logical startup composition. Independently verify it,
keep existing consumer pins intact until compatibility review, and use an isolated
source snapshot. Do not build against a drifting sibling tree. Producer SDK path
native-c-5olokhku must be checked for actual identity and availability.

UL-067's live NATIVE-CAT and toybox-native-* evidence report actual cat_main and
startup/finalization/error work. Its final usage/finalizer and independent consumer
handoff boundaries require inspection; do not assume the runner bundle contains
the later cat sources. Next intake should report the exact missing seam, if any,
instead of selecting unrelated refinement work.
