# AENMX007 process/channel lifetime profile

2026-09-24. Private ABI21 resource qualification. This is not SESSION-01–06,
a published SDK handoff or bootable-shell completion.

## Implementation

Exact AENMX007 with the existing native-pipeline-capacity build option accepts the
112-byte envelope,80 entropy bytes, three images and up to24576 owner-code bytes.
It selects fifteen process/channel lifetimes through a common kernel bound and
the already-tested channel createSession path. AENMX004–006 retain three uses;
004 retains its16-KiB owner ceiling. Native argument/grant layout, six domain backing
slots, ten32-byte channels and memory quotas are unchanged.007 has no UART grant
and direct UART operations return unsupported(-38) for owner and workers.

The bound is applied to fresh launch, process copy, nonlaunch creation and channel
selection. Only fresh launch and channel reuse above generation3 are exercised in
this packet. Higher-generation copied-child execution, pipe lifetimes and persistent
parent job dispatch remain unqualified; do not infer those from a shared predicate.

The existing capacity worker/owner qualifies two workers for fifteen generations:
30 launches,30 normal exits and30 reclaims, with actual native PID reports bound to
the admitted slot/generation and authentic endpoint. Both channels per worker use
canonical identity/epoch tags. Stale task references and forbidden adjacent-endpoint
operations reject. After60 channel creates, the61st must use previously unused
object4/generation1, proving objects0–3 retired at15. Both spare ends close.

This resource workload deliberately differs from the consumer script's three
persistent shell parents,27 copies and21 helper exec replacements. Its30 reclaims
are not SESSION acceptance. There is no fake script output, helper or shell result.

## Controls and evidence

Eight added capacity cases cover the positive, stale worker generation (owner2608,
6 prior reclaims), legacy005 bound (owner2603,6 prior reclaims), disabled007,
truncated/reserved/oversized007 and an old owner rejecting ABI21 (2600,0 reclaims).
Parser host checks include007 in the size/reserved/truncation matrix, preserve old
bundle rejection and reject unknown008. Specific expected panics are negative
outcomes, not positive success; ordinary output and cleanup oracles remain intact.

The pre-execution linked owner audit binds .text to actual native raw bytes.
The007 resource owner is2416 bytes with a conservative632/4088-byte stack bound;
the legacy-control owner is2240 bytes with600/4088. Fixed immutable GOT targets,
transient arguments, end/call frames and returns are included. This is scoped
inspection, not a formal whole-program proof or an audit of the future session owner.
All148 prior worker/owner binaries are unchanged;105 existing kernel ELFs change.

The first preliminary owner build failed Rust E0308 because the shared loop bound
made the final slot argument usize. An explicit u64 conversion fixes the trap call.
Its exact source, command and error are retained. Preliminary compile duration was
not recorded; qualified native runs record UTC and monotonic times. No native result
is inferred from that compilation or from host checks.

## Reproduce

```sh
python3 scripts/pipeline_capacity.py --case session-lifetime --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py --connections --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py --command-runner --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

No sibling, released standard pin or old evidence is modified. The existing dirty
worktree is preserved. Sources/support including tests/test_build_policy.py, compiler
flags, tool/SDK digests, transcripts and artifacts are retained; archive verification
precedes duplicate-output removal. Sources remain frozen through qualified native
runs, and those suites execute sequentially. See verification.json for timings and
archive counts; this packet does not imply independent userland acceptance.

Next integrate reusable pipe/copy lifetimes, authenticated child identity and the
request-driven dispatcher around one live dash parent, then execute the unchanged
consumer script and its semantic controls. No further resource witness substitutes
for that composed workload. Shared SDK/runtime, serial assembly, filesystem,
packages and sys-init integration remain separate gates.

## Final qualification

Qualification: all113 capacity,358 connections and431 command-runner cases pass
(902 distinct native cases), plus one focused resource rerun,110 Python and configured
Zig/Rust host checks. All287 runtime inputs and306 host/support inputs remain frozen;
full suites share tool and SDK identities. Both qualified raw/linked resource owners
match the inspected stack artifacts. All148 legacy worker/owner binaries are unchanged.
The failed preliminary Rust compilation is retained with source and diagnosis.
Archive readback and original-file verification precede duplicate cleanup. No new
higher-generation copied child or SESSION case has run. Continue with reusable
pipes/copies and one-parent dispatch under the existing composed-session contract.
