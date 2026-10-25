# Owner-local service workers

Status: private producer qualification passes, 2026-10-04; expanded clock
qualification added2026-10-05. [Clock scope/command](NATIVE-CLOCKS.md) enables
`native-clock` with the existing worker profile after full-owner native timeout,
wake/requeue/pin and stop/replacement controls. The native wait scan remains
bounded by92 pointers across four owners; source-observed maximum scan intervals
include serial timeout output and are not physical WCET or measured stack peaks.
Actual expanded musl timing and OpenZFS startup remain separate.
`-Dnative-service-workers=true` requires service memory and thread origin/reuse.
Only domain 0 borrows 82 child records; three companions borrow two each from
separate static pools. Views are derived from checked domain identity at boot and
generation reset. Existing State grants, 512 lifetime admissions, exact IDs,
thread storage/pins, wait/mask/entropy semantics and stop/reclaim remain.

The 82-worker choice follows the recorded host workload peak and its 20.5 MiB
requested stack lower bound. It does not establish the native engine peak or
sufficiency of the 32 MiB trial. Bare stack/FS-cookie witnesses do not implement
a production musl TCB, provider or native taskq/engine startup. Companion/supervisor
memory and live slots remain small; no quota API, CPU identity or SDK change.

Temporary context-pointer lists contain only the actual owner contexts and live
within their synchronous IF-clear callers. The largest list has 83 pointers plus
count on the existing 64 KiB exception stack; it never escapes into wait storage
or a global cache. Permission checks use the existing range cursor only for this
profile; legacy typed checks retain their ordering. Default embedded child arrays
remain. The actual omitted reset rebind is a release-excluded negative control.

[Before-code scope and recipes](evidence/native-service-workers-2026-10-04/README.md)
select native simultaneous storage/exhaustion/retirement/stop/replacement and old
context consumer regressions. Run `zig build test`; retain compact outcomes/hashes/logs and
remove generated outputs under the maintainer's2026-10-05 retention decision.
Historical archive/setup recipes are retired. Full engine, measured native demand/stack peaks,
production latency, independent reader/SDK and R1 assembly remain open.

201 fresh target cases qualify this snapshot: 162 maintained memory/thread, 14
origin/reuse/entropy, seven M4, ten larger-owner memory, two ordinary storage,
three worker capacity/stop/rebind controls, two full-owner park/wake/stop and one
unsupported envelope. Full 137 Python/Zig/Rust/pin/workflow and eleven selected
build guards pass. The actual compiled arrays occupy 64,288 bytes for the service
and 4,704 bytes for all three small owners (784 bytes per child, FX alignment 16).
The context list bound is 672 bytes; this is not a measured stack high-water.

All 82 workers hold 256 KiB requested stacks and 4 KiB cookies simultaneously;
one spare stack/cookie is reserved for the failed full-slot/next-ID check. Small
peer uses 4 KiB stacks, fills two slots and rejects the third without spending
an ordinal. Initial IDs 3/4 recur only under each fresh generation's new grant.
Running retirement/pin checks and final clear-TID/status/retirement/quota checks
pass. Indefinite compare-wait parks all children on an owner-local word; counted
wake returns exactly 82/two. Stop/replacement also passes with all parked. Stop
reason is checked by the compiled supervisor's (144,3) observation; this profile
emits no serial stop-terminal row.

The first stop fixture was compiled without the helper's per-case stop macro;
its normal exit correctly caused supervisor rejection. Failed source/commands/
images remain, and all final worker cases ran fresh after that fixture correction.
Actual omitted reset rebind fails admission check 262, and release excludes it.
This supplies a private live-worker trial, not upstream native taskq/engine
execution. Next native musl storage/stack/allocation demand and provider identity/
configuration/feature closure before actual engine startup/fini/restart.
