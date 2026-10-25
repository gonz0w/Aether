# Contributing to sys-init

For contributors working on the experimental model, host tools and native Aether
fixtures. Start with the pinned [method](../.agent-temper/METHOD.md), root
[engineering policy](../PROJECT.md), root [work selection](../.planning/STATE.md),
[repository rules](AGENTS.md) and [standards review](docs/STANDARDS-UPDATE-REVIEW.md).
Production init, operator commands and general POSIX sessions are not implemented.

1. Follow the bounded record selected by root STATE and update its owning BG story
   where applicable; local candidates and historical summaries do not assign work.
   Before behavior changes, record the requirement, affected interfaces, success
   and forbidden outcomes, execution
   layer, resource bounds and test selection in the owning record. Prefer meaningful
   test-first work. Reproduce bugs before fixing them, or record why deterministic
   reproduction is unavailable and the alternative evidence. Record the actual
   sequence without inventing a red result after implementation.
2. Read applicable pinned standards and the reviewed draft topics listed in the
   review. Shared changes belong in Aether-standards. Drafts are review inputs;
   adopting a runtime interface requires owner review and consuming evidence.
   For substantial changes, answer the three simplicity questions in the existing
   change description; see [the local adoption](docs/SIMPLICITY-ADOPTION.md) and
   [quality process](docs/QUALITY-PROCESS.md). Small fixes need no separate review form.
3. Implement the bounded change. Review ownership, partial failure, cancellation,
   error identity, authority and concurrency. Document unsafe/FFI obligations.
   Review new dependencies, tool versions, license, offline setup and resource
   costs. Preserve generated, third-party and immutable evidence bytes.
4. Run relevant tests while iterating and affected checks on final bytes under
   root's focused cadence. For a required current aggregate, run `make check-init`
   from the system root, or `python3 scripts/check-all.py --current` from `sys-init/`.
   Follow [test selection](docs/QUALITY-PROCESS.md) for native or interface changes.
   The default historical audit remains separate and unavailable closure stays
   blocked; current host checks do not replace a fresh target witness.
5. Update the canonical reference and [coverage inventory](docs/quality-inventory.json),
   or explain why the change has no documentation impact. Keep tutorials,
   procedures, reference and explanation identifiable without mandatory folders.
6. Retain compact commands, source/tool/artifact pins, outcomes and short failure
   logs under root policy; remove owned generated outputs after the run. Review the
   final diff and any unresolved findings. Do not claim independent review,
   portability, release readiness or scheduled execution without actual evidence.

The check command reports an absolute results path. On failure, inspect that
directory's results and named logs; repair the cause and keep the failed attempt
when making a new run. Unsupported platforms and missing tools are coverage gaps.

Original contributions use BSD-2-Clause; preserve upstream terms and provenance.
There is no published release. The maintainer supplied the contact in
[SECURITY.md](SECURITY.md); delivery and response times are not independently
verified. Independent reader/technical and release reviews remain publication
gates, not invented approvals.
