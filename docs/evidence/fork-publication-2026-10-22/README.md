# Bounded fork publication and comparison fit

UL-007/081/082, BG-070/073;2026-10-22. Implementation-agent review, not independent
or native acceptance. No guest ran, release/sealed pin changed or limit increased.
[Dependency/unsafe review](../../../sys-init/docs/decisions/0208-owner-compare-fit.md),
[publication review](../../../sys-init/docs/decisions/0209-fork-publication.md),
[contract and commands](../../../sys-init/prototypes/native-filesystem-session/FORK.md).

| Check | Actual result |
| --- | --- |
| Unchanged in-place producer |35 tests/15 compiling semantic controls, borrow denial, strict format/Clippy and host/native libraries pass; exact producer source/library/tool hashes reused by consumers |
| Consuming owner/transport |34 tests (26 previous plus8 publication/refusal), host/native libraries and test Clippy pass |
| Semantic omissions |Unchecked ready, opening parent admission before delivery, and opening refusal admission before delivery each compile and fail the named assertion test |
| New musl leaf |All65536 one-byte pairs, equality/prefix/outside-range,16x16 alignments, lengths through4096, guard page and zero-length inaccessible pointers pass under host UBSan; signed-byte omission fails ordering |
| Target leaf |One41-byte memcmp, no undefined symbols/recursion/other definitions; source/header/COPYRIGHT pins verified before build; no libc archive linked |
| Original constructor roots + musl |16008/16384, compared with prior compiler-builtins16544; only this older selected subset fits |
| Positive-publication roots |16984/16384, explicitly blocked |
| Final positive + refusal roots |17440/16384 with musl,17976 with compiler-builtins on identical roots/libraries;536-byte saving, still code-fit blocked (exit2) |
| Stack observations |Largest final fixed subtraction504; boot reservation192 plus24 pushes. These are not a full call graph, peak stack or interrupt/context proof |

New transport uses actual FILE/AF07 policy and existing stream cores, with injected
storage/native channel outcomes. Positive tests continue shared FILE reads as ab/cd
and preserve CLOEXEC. Tests cover all304 startup,32 ready and32 parent output
truncated prefixes, malformed/stale ready and activation failure, bad routes/
startup labels, wrong/Idle admission, short/EAGAIN/raw wait/count/budget and host
unwind. Known refusal uses original errno after injected raw thaw-11, unchanged
parent flags/offsets, all32 negative-reply prefixes and interrupted delivery.
Raw source closes(-9,-5) happen once; no process endpoint close or copy/thaw replay.
Host unwind is not native abort cleanup or actual endpoint authentication.

Final receipt is attempt-7.json. Each earlier attempt, including failed checks,
retains its complete result/commands/hashes as compact JSON; records.json binds
original captures to lossless JSON serialization. Short failures are separate.
No source/build archive, copied SDK, binary or disk image is retained.

Failures and corrections:

1. First patch application found an incorrect exact source anchor; atomic apply
   made no source changes. Correct the patch before the first run.
2. Initial comparison harness passes UBSan but its new first-party C style fails
   the prescribed clang-format check. Format only that harness; upstream musl is
   byte-identical. Final checker requires the format check.
3. First publication omission really fails its custom semantic assertion; the
   checker wrongly required the literal word `assertion`. Require the exact
   semantic message and exact failed test instead; no compiler/timeout oracle.
4. Adding refusal creates a second generic disposition anchor. The mutation
   runner correctly stops; narrow each positive/refusal anchor rather than
   altering both or accepting a missing control.
5. New malformed-startup cases reach a test's old unreachable default. Add only
   their intended no-route-change cases; runtime library did not change for this
   harness repair. All34 tests and all three controls then pass.
6. The expanded quality inventory oracle exceeds its unchanged4096-character
   field limit. Compact the current summary while preserving historical detail
   in decisions/evidence. One correction initially uses the wrong cwd and makes
   no edit; the repeated failed process result remains recorded.
7. Aggregate static checks find the active boundary inventory still describes
   the earlier0206 gate, before committed0207 in-place initialization. Review
   current projections/partial failure/drop obligations and tests before updating
   this active index. No immutable pin or historical evidence is rewritten.

The final checker also verifies frozen measurement inputs and Rust target-runtime
hashes before linking. Source freeze is checked after the run. The separate
compiler-builtins baseline relinks only the same final roots, reusing34 unchanged
host tests by exact source hashes; its argv and artifact identity are in baseline.json.

Remaining BG-070 work is local: coherent complete native entry/transaction/routing/
copy/exec/wait/terminal/readiness/shutdown and actual code/peak-stack/resource fit,
then fresh matched native positive/failure/cleanup/readback acceptance. Independent
roots are not a lower-bound theorem for every unified owner; do not infer a quota
increase from this specimen. Persistent Zsh/TTY/packages/runner/ISO remain open.
The former constructor-only excess is resolved in the separate selection, but
native admission remains blocked under the unchanged16KiB code ceiling.

Final documentation/process selection: root workflow175 groups/41 references/
34 tools; root Experience; userland quality/all three offline pins; all nine
sys-init `check-all.py --current` stages pass. That includes255 harness tests,
287 model cases/23 negative controls/1000 traces and54 host lifecycle tests;
historical native replay is explicitly NOT RUN. These existing development checks
do not include the new Rust component cases (qualified separately above) or grant
native acceptance. Simplicity snapshot manifest/four files and1092 touched-document
file destinations verify. Four CLI help/version/usage cases preserve0/64, ASCII
and no preparation. Python syntax and prescribed C/Rust formatting pass.
No broad kernel/QEMU/storage suite is selected before a complete admitted owner.

The aggregate's passing source hashes describe its frozen run. Subsequent changes
are result/progress prose and a correction from "speculative byte loads" to
"wider loads" in the boundary review, with no executable/inventory/path effect;
the affected quality/pin/inventory checks are rechecked without replaying unrelated
passing runtime cases. Native sources/checkers match attempt-7 exactly.

Cleanup removes12 exact owned generated roots,105849162 logical bytes; physical
reclamation is not measured. Current dependencies and sealed inputs remain. The
aggregate result keeps current source hashes and represents its historical
evidence/archive source index by full canonical manifest digest/count, rather
than repeating that long historical index. This is compact POC evidence, not a
complete replay bundle. No new binaries, images, SDK copies or source trees remain.
