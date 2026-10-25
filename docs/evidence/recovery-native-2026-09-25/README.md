# Dash recovery composition — 2026-09-25

Status: scoped producer checks pass; independent RECOVERY-01–06 replay pending.
`SHA256SUMS` seals the completed packet. Existing SESSION and SI-07 packets are
immutable. No sibling or release pin changed.

Final:128 capacity cases, five unchanged non-pipeline command cases and119 Python
plus configured Zig/Rust/standards tests pass. Final source export covers319 source
and test files; the complete replay export additionally supplies pinned support,
firmware and consumer inputs. No358-connection/431-runner result is claimed for
this freeze. See the test-selection rationale below. This is a private scripted
recovery handoff, not shared SDK, full interactive filesystem shell or R1 readiness.

Next: userland replays this unchanged recovery composition. Failed-exec, scratch
and real serial session composition need new consumer-owned workloads/oracles.
Their older accepted component fixtures remain valid within their original scope.
SI-07 still needs a versioned sustained userland contract: its three decoders
remain byte-identical and reject generation3 (`sustained-dependency-recheck.json`).


## Requirement and pre-code review

Run userland's unchanged, hash-verified SESSION-RECOVERY input through actual dash
main in three parents. Preserve private AENMX007/ABI21 and all live resource limits.
Userland owns shell/helper semantics; Aether owns the private dispatcher and native
mechanisms. This is not the SDK, sys-init policy or an R1 release.

Expected per parent: recovery pump/one in slots2/3, argv in slot2, healthy pipeline
in slots2/3/4, closure helper in slot2. Parent slot0 generations1–3; child slot2
uses generations1–12, slot3 uses1–6, slot4 uses1–3. Seven copies, six replacements
per parent; totals21 copies,18 replacements,21 image admissions,24 terminal/reclaims.
Each recovery pump exits42; all other positive terminals exit0. Stdout49 bytes,
stderr20 bytes, with the parent's identity unchanged. Before each new phase,
collect/reclaim preceding children and retire their pipe references.

Use existing capability-scoped channel/exec/wait/pipe operations and bounded176-byte
observation records. No new grant, syscall, service, unsafe boundary or heap is
needed. The privileged fixture finish currently hardcodes30 reclaimed processes;
replace that assumption only for three authenticated, cleanup-checked observations
with their kernel-owned cumulative reclaim count. The zero-observation resource
probe retains30. Partial observations, live workers/channels and mismatched cleanup
must never pass. Exact workload totals/status/stream checks remain host-owned.

Simpler alternative: reuse the existing session dispatcher/client with a compile
selection and independent oracle. Chosen over a second owner/ABI or artificial
extra workers to reach30. Existing accepted inputs and controls stay unchanged.
Complexity removed: script-specific final reclaim total from the observation path.
Review linked owner stack against4088 bytes and raw code against24576 before
claiming fit. SIGPIPE remains handled through existing public signal operations.

Required controls: wrong EPIPE/pump result, actual retained reader with bounded
confirmed-stop cleanup, stale recovered-child identity, wrong WITNESS after recovery,
corrupted healthy bytes and an unflagged fd3 leak. No timeout, crash or invented
output qualifies. Host oracle corruption tests, full host suite, selected target
cases and matching affected broad regressions are required for qualified delivery.
Freeze sources per attempt; preserve every failed attempt and its separate output
root. No consumer acceptance, all-attempt qualification or release readiness is
claimed while these gates remain open. No sibling or released pin is modified.


Attempt1: real pump42 and reader0, then argv0 and three child reclaims passed.
Owner2820 then rejected the healthy pipeline: the new phase assertion incorrectly
required no pipe epochs after dash had already created the healthy pipeline's
pipes. Corrected only this assertion; existing pipe create/retirement remains the
enforcement boundary. Entire attempt sources and output directory are retained.
Initial host observer test also found missing-record IndexError; corrected to
explicit observation-count rejection (both attempts retained).


Attempt2: unchanged recovery positive passed all three parent generations, exact
streams,21 image admissions and24 terminals/reclaims. All118 Python tests plus
configured Zig/Rust/standards tests passed. Optimized observation core tests pass.
Linked owner:3688/4088 stack bytes (400 margin), with builtin indirect targets
inspected; see owner-attempt-2-indirect.json. Full capacity suite running as attempt3.
These are scoped producer observations, not independent consumer acceptance.
Clang-format21.1.8 identified only two new conditional-indentation violations;
repair is deferred until the frozen target suite ends, then recheck final bytes.


Attempt3: all128 capacity cases pass (121 existing plus7 recovery). The normal
stale-wait control replays an already collected recovery child into the next
phase and requires ECHILD with unchanged status; it grants no authority.
Retained-reader cleanup has exact parent kind3/detail143 and observed pump
termination, with no timeout accepted. All native negative oracles passed.
The final host observer additionally rejects malformed extra terminal rows and
checks negative phase ordering; replay of every retained recovery log passes its
intended oracle, including rejection of byte corruption after normal guest cleanup.
C formatting was corrected after source freeze ended. Final rerun follows.

Test selection: the runtime change is limited to AENMX007 fixture completion.
The complete capacity suite covers007,005/006 and older-envelope controls, real
shell/descriptor/exec/pipe paths, observation authority and both session scripts.
The unchanged non-pipeline branch additionally receives the five bounded real
command regressions. No new signal, scheduling, mapping, exec or channel mechanism
is introduced. The earlier358-connection/431-runner results are not represented
as matching this source freeze. Independent review and shared SDK remain open.


## Final verification and replay

`attempt-final-run.json` and `final-capacity-results.json` bind all128 target cases
on the final source freeze. `legacy-final-run.json` and the legacy artifact archive
bind five unchanged non-pipeline cases. The host logs retain both118-test preliminary
and119-test final results, including four recovery-observer counterexample tests.
`observation-release-safe.log` covers the optimized completion/record checks.
`source-review.patch` identifies the eight changed/new code/test files against
the prior sustained-core snapshot, without folding unrelated working-tree changes.

`owner-reviews.json`, disassemblies and stack aids inspect all five recovery owner
variants. RIP-relative call targets resolve to immutable memcpy/memset/memcmp.
Register calls were traced to those same loads: r12 in cleanup; r15/r14 in new;
r13 in replace; the extra negative-owner run call uses r13 or rbp loaded with
memset. Final raw hashes match the inspected images (`final-stack-bindings.json`).
Code14824–15336 bytes; stack3624–3688 of4088. This is contributor inspection and a
bounded aid, not an independent reader review or formal whole-program guarantee.
The existing six-page code/one-page stack grants are not widened.

All target attempts have distinct source snapshots and full artifact inventories.
The failed first target run, successful second probe, first128-case run and final
run are retained separately. Each archive is read back and compared with every
live file before deleting its redundant owned output root. Formatter/observer
failures and the two rejected relative-path archive invocations are documented.
The final source tree is checked against the frozen inventory before sealing.

Replay the `replay-inputs.tar.gz` repository export in a fresh directory, verify
its `replay-inputs.json` member hashes, and use the unchanged pinned SDK at
`/Users/cam/DEV/Aether-userland/build/native-c-5olokhku` (receipt and tool hashes
are in the capacity report). The SDK is an external pinned input, not silently
substituted with current sibling bytes. Use the canonical capacity command in
`attempt-final-run.json`; `--case recovery-composed` selects the positive alone.
All seven `recovery-*` cases are listed in `scripts/recovery_smoke.py`. Preserve
separate attempt roots and failure logs. The replay export's host check is a
reproducibility check by this producer, not independent userland acceptance.
