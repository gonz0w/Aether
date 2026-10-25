# UL-007 change review

- Scope: production startup prerequisite probe, separate host fault harness and
  pinned native link driver. Applicable Foundations O/I/E, CP/CE/C17, TD/TC/TE and
  documentation/evidence clauses; no shared pin/API or sibling implementation edits.
- Authority/lifetime: no identity-based permission, no process launch, no global
  service policy. Probe owns one duplicate and temporarily changes its SIGUSR1
  disposition/mask, then restores them. It is intended for an isolated test task
  without concurrent signal senders; signal delivery/races are not qualified.
- Failure review: distinct stage exits; no unchecked successful fallback; cleanup
  attempted after partial progress; uncertain close never retried. Original failure
  preserved if cleanup also fails. No signal delivery induced by this workload.
- Tooling: existing Python stdlib and owned process helper, exact Clang/LLD/native
  SDK receipts reused and verified, explicit host SDK selection. C17 O2 Wall/Wextra/
  Werror and native freestanding/stack protection flags recorded per command.
  First-party BSD-2-Clause headers; existing SDK terms unchanged. No new dependency.
- Tests: six host cases and native compile/link, 180-second command bounds, isolated
  build outputs, all final receipts complete. Host wrappers deliberately return
  failed or false-success semantics; same production probe must detect them.
- Attempts: missing-host-header compile failure retained; explicit SDK correction
  passes; added restoration/closure assertions pass in final attempt3. No native
  runtime test or failed native invocation claimed. No C sanitizer instrumentation
  selected for this scalar libc contract probe; no memory-safety claim follows.
- Source review: Codex reviewed stage checks, cleanup evaluation/order, varargs
  fcntl forwarding, separate native build without test macros, evidence validation,
  and owned process results. Independent technical and reader review pending.
- Missing coverage: full host SDK closure, signal delivery/concurrency/all mask bits,
  cleanup failure injection, native envelope/identity/denial/cleanup, actual dash
  fork/exec/wait. Runtime remains NOT RUN until matching producer admission exists.
- Docs: PLAN, native gaps, STATE/BACKLOG, coverage and this evidence packet updated.
  No supported public CLI added; internal silent status contract only. Formatting,
  quality and whitespace checks retained. UL-007/M3 remain active, not complete.
