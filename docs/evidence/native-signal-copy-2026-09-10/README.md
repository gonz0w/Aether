# Native signal-copy experiment — 2026-09-10

An explicit default-off `native-copy-signals` flag now admits the existing native
copy path with private actions. It requires process-copy, private action support
(and its runner-local prerequisite), and single-context execution. Both old
freeze/copy action-profile rejections remain unless this flag is selected.
Native factory/source/token/channel checks and publication order are unchanged.
Before child publication, validated action records are copied privately, child
pending bits start empty, and parent pending bits remain untouched.

The [pre-code selection](../../NATIVE-SHELL-STARTUP.md#native-signal-copy-experiment-selection--2026-09-10)
records requirements, oracles, ownership and simplicity. Reusing the raw copy
fixture, fixed action records and checked user-stack restorer avoids a new service
or snapshot protocol. New fault controls are classified as intentional negatives
and rejected by release-artifact builds. No dependency, quota or sibling API is added.

Seven new target cases select three positives and four semantic rejections:

- `copy-signals`: exact default/ignored/custom dispositions, masks, restorer and
  ignored signal64 survive copy. Duplicate masked parent posts coalesce. Child
  restoration delivers none; a fresh child post invokes the inherited handler.
  Parent restoration delivers the retained occurrence exactly once. A child action
  change precedes readiness and does not change the parent's queried record.
- `copy-signals-handler`: the entire copied continuation runs inside a handler.
  Both parent and child return through their inherited private stack restorers,
  then query the original pre-handler mask. The original raw copy GPR/FP, TLS,
  memory/authority and endpoint checks remain in the continuation.
- `copy-signals-rollback`: injected staged-copy failure preserves parent actions
  and pending occurrence through matching cancellation. The replacement slot keeps
  its expected generation. Existing zeroing/channel ownership checks remain.
- Without the new opt-in, source246 precedes owner1800. Dropped child records yield
  child247/owner1820; copied pending bits child248/owner1820; cleared parent pending
  source248/owner1821. All four require zero reclaims and exact terminal context.

Positive copy cases require dummy29, child72, parent71 across two generations,
with six reclaims. Rollback requires dummy29, parent71, replacement29 twice, also
six reclaims. Final source-matched results and timings record all 98 connections
and five launch cases, plus the host build's 98 Python tests and Zig/pin/workflow
checks. No qualified runtime attempt failed. Five separate build checks reject
missing prerequisites, thread admission and each new negative flag in a release
artifact; logs retain exact diagnostics. These are build rejections, not target
thread-copy or release-readiness evidence.

The experiment is not an installed SDK fork contract. Corrupt inherited-handler
return, nonlocal escape, precise outer-frame register/FP assertions, and composition
with guarded descriptor publication remain separate qualification. Pending external
signals, indefinite I/O/EINTR, job control and multithreaded copying remain outside
this profile. Existing legacy signal dispatch and delivery were not changed.
Prior full command/M4 target evidence remains historical; no broader signal or
scheduler conformance is claimed from this suite.

Only build.zig, native_c.zig, the copy C client and launch harness runtime sources
changed from the preceding staged-state packet. Build policy classification is
retained alongside the runtime patch and frozen inputs. No sibling sources,
released standards pins or independent consumer acceptance changed. Full dash
and R1 are unfinished.

The collector verifies the previous packet, frozen sources, pinned simplicity
snapshot and archive readback. Reports bind tool/SDK/artifact identities and exact
commands; timings include UTC boundaries and status. Native artifacts retain musl
notices. The final manifest seals this packet.

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --connections \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

All 98 connections and five launch cases pass within their review budgets. All
91 previous payloads match outside entropy; the backend image is identical and
maximum copy owner remains 5,880 bytes within the 8,192-byte limit.

Archive readback verified 225 source files and 1,803 native target artifacts.
