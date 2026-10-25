# UL-059 / M3 independent four-role native execution

The independent userland parent now executes with the captured producer. The real
startup parser selects `bytecount --decimal`; the existing bytecount implementation
and legacy child adapter are rebuilt against the matching 231-file SDK. Both
generations exit zero. The producer independently reads `6\n` from the child output,
checks unchanged `abcdef` input and empty parent stdout/stderr, consumes collection
once, checks ECHILD and shared-output EOF, closes backend handles and denies stale
handles. All six native tasks are reclaimed. This is the new four-role integration
witness, not the first native bytecount run or a functioning shell claim.

| Case | Observed result |
| --- | --- |
| Positive | Child/parent/backend terminal details 0/0/17 in each generation; supervisor100, reclaimed6, native connections PASS |
| Wrong role | Private adapter flips first role before validation; parent110, no child terminal, supervisor1401/reclaimed0 and exact expected profile rejection |
| Omitted close | Private parent omits stdout close; child0/parent0, supervisor1403/reclaimed0 and exact expected profile rejection |

The negative cases demonstrate rejection; their zero reclaims are not a recovery
claim. Ordinary successful execution requires six. Decoder host controls from
[preparation](../four-role-consumer-2026-09-07/README.md) remain distinct evidence.

[Final receipt](final/summary.json) retains exact argv, tools/environment, deadlines,
process cleanup, source/SDK/artifact hashes and all three case oracles. Raw serial
and QEMU logs are retained under each case. The source-built producer remains in
`build/m3-producer-_7hbg9fd/producer`; payloads and ISOs remain under the build path
recorded in the receipt, with hashes. [Backend oracle](sources/producer-success.rs)
is copied unchanged for review. No live sibling implementation or consumer pin
was changed.

[Attempt 1](attempt-1/summary.json) stopped before boot: the private PATH lacked
rustc for the kernel's nested builders. Its source and logs are retained. The rerun
adds the established private wrapper selecting the pinned compiler and library
path. Native source/oracles were unchanged. All three rerun cases pass, and every
owned process receipt reports complete cleanup.

Reproduce with `python3 -B experiments/command-runner/run-four-role.py` after
provisioning the exact captured producer, SDK, prepared parent and locked host
tools at its declared paths. This is a checkout-local experimental harness.
It verifies captured sources, SDK and tools before building. Each build is bounded
at 180 seconds; pinned native_smoke retains its 30-second guest watchdog and
termination/wait cleanup inside the outer 180-second process group boundary.
No target installation or network fetch is performed.

Next roadmap work: independently pin and adopt the newer Toybox cat producer
delivery (UL-067), then native dash external-command/pipeline integration. Public
runner local-output/denial handling, wider failure coverage, independent review
and M3 acceptance remain open. Optional utility tuning stays deferred.

## Change review

Scope/requirements: UL-059 four-role command-success slice under the existing
[plan](sources/FOUR-ROLE-PLAN.md); Foundations O/I/E and quality C/CP/TD/TE apply.
No shared interface or ownership changes. Source-built owner/backend retain all
native authority, admission and resource oracles. Private controls never replace
the normal parent. C17/strict pinned Clang, Rust owner recipe and SDK identities
are recorded. Original source BSD-2-Clause; imported source/SDK notices unchanged.

Technical review by Codex: checked role validation before publication, parser
argument copy, inherited refs, once-only collection, status mapping, explicit
closes and independent backend readback against captured owner source; compared
all six terminal lines and exact rejection contexts. Harness invokes owned argv
processes with a clean environment; producer helper remains pinned and bounded.
Prepared parent/control object reuse is from the retained successful build; the
normal parent ELF is hash-checked. This is not a malicious-cache validation claim.
An independent reader/maintainer review is pending; no sign-off is inferred.

Documentation: STATE, BACKLOG, NATIVE and coverage point here. The earlier
preparation and failed attempts remain unchanged. Source/tool/SDK changes invalidate
reuse. Broader UL-059 completion and native shell acceptance remain incomplete.
