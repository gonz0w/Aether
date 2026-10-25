# UL-066 mawk musl change review

- Requirement, scope and plan: static Linux-reference build and upstream/consumer
  validation under experiments/awk-reference/MUSL-PLAN.md; source and plan copies
  in harness/, digests in SHA256SUMS. No native acceptance or shared API change.
- Standards and owners: local E-01–08, PX, CD/CP, TD/TE and DP; Aether-userland
  owns this harness. Existing pkg-mgr consumer bytes are hash-checked; no sibling
  implementation or standards release/pin change.
- Ownership/authority/lifetimes: build phases own a process group and private
  directory; runtime owns UUID-named containers, private writable scratch and
  read-only repository mount. Cleanup status is part of acceptance. Commands use
  argument arrays; fixed shell scripts use positional arguments for paths.
- Dependencies: pinned mawk GPLv2 archive, musl SDK, Clang/LLD and wrapper receipts;
  immutable Linux helper image. First-party Python/C are BSD-2-Clause. Python host
  build requires 3.12+; runtime interpreter/version and QEMU bytes are recorded.
  No installation, download or package activation. Entire host OS/tool transitive
  closure is not hermetically pinned; byte identity does not authenticate upstream.
- Budgets: 240 seconds per build phase with process-group kill; 180 seconds per
  suite container, 15 seconds per consumer, 15-second cleanup; 512 MiB/32 PIDs per
  container. Fixed source-pinned fixtures limit workload; no performance claim.
- Tests/oracles: exact consumer stdout/stderr/exit, unordered update rows only;
  10 functional and 40 diagnostic upstream groups plus FPE completion; no skip,
  positive discovery counts and clean container removal. Independent math probe
  classifies NaN, infinity and finite values. All 33 host fixtures rerun; empty
  providers, wrong provider and changed digest reject. Initial real NaN failure
  demonstrates that upstream errors propagate to incomplete acceptance.
- Findings: configure checks external isnan/isinf symbols, missing musl macros.
  Target compile/link probe justifies explicit cache answers; QEMU probe and the
  original upstream suite validate behavior. No upstream patch or expected-output
  adjustment. Upstream's existing sign-only NaN allowance is observed, not waived.
- Attempts: initial NaN failure, corrected build, probe formatting correction and
  rebuilt result retained. First inventory implementation missed an indented Begin;
  corrected counting and final complete rerun retained. Early builder/runner exact
  revisions were not copied before revision; their original digests/commands/logs
  remain in receipts. Final source bytes are retained; no reconstructed old-source
  snapshot is asserted. Initial clang-format rejection was formatting only; final
  non-mutating check passes.
- Documentation: README, plan, BACKLOG, STATE and coverage updated. This is an
  experimental contributor surface, not a shipped CLI/manual or renderer change.
- Evidence freshness: final source/config/binary/tool/runtime hashes bind this run.
  Rebuild/rerun after affecting changes. Earlier host evidence remains immutable;
  a fresh host regression supports the shared consumer-runner edits.
- Review: technical inspection and execution by this task; independent source
  review, reader walkthrough, fuzz/sanitizer and release-security review pending.
  No reviewer identity or whole-project compliance is inferred from the checker.
- Decision: mawk musl reference slice passes. UL-066 remains active for GNU/BusyBox
  tr/stty builds. Native filesystem/process/TTY interfaces and source authentication
  remain separate work; no final system-awk selection or distribution claim.
