# Dynamic musl creation and confirmed record reuse

Status: private producer qualification passes,2026-10-05.
[Before-code scope](contract.md) and [reference](../../NATIVE-SERVICE-DYNAMIC.md)
preserve native grants, live pins, owner-local quotas and public ABI/SDK/pins.
No kernel, maintained user source or sibling changes. Production musl/runtime
remains userland-owned; full native engine startup has not run.

Seven final fresh cases pass in attempt11: origin regression, ordinary dynamic
reuse, full-capacity stop/replacement, actual wrong-grant clone360, premature
unmap352, missing overlap proof365 and omitted actual primary park356. Each
control requires its exact primary terminal, supervisor401/reclaimed0 and named
profile rejection; unrelated fault, generic panic or timeout is never acceptance.

The ordinary service has one joinable creator, one joinable cleanup worker and80
detached peers within82 records. Two full rounds produce162 lifetime admissions,
160 detached retirements and80 reused records. After the first old retirement,
cleanup waits until the next actual pthread_create enters preflight before
upstream locks. It then continues servicing pending peers while that creation
call proceeds or waits on musl's list lock. The primary remains in real join.
The small companion uses primary creation, one cleanup worker and one detached
peer reused once (three admissions); it is replaced in this case. This is bounded
one-CPU concurrency; no simultaneous multicore clone or82 engine workers claim.

Atomic FREE/RESERVED/LIVE/PENDING state separates each record's owners. Clone
reserves FREE under upstream list-lock ownership, publishes saved ID/TCB/mapping
metadata only after native admission and rolls back denied reservations. A direct
TLS record pointer avoids racing scans of reused scalar metadata. Real musl TSD
and destructors complete before PENDING publication. The sole cleanup worker
selects any pending peer, verifies its live mapping rejects unmap, permits exit
and wakes its actual native compare-park, confirms exact native stop, unmaps,
retires and rejects the old ID before publishing FREE. It never reads an unmapped
TCB or acquires the list lock while a pending peer holds it.

Actual1024-byte TSD, two/four destructor calls, fresh per-thread TSD/TLS/errno,
creator mask inheritance, monotonic ID/sequence binding,4 KiB stack patterns,
independent parent state and full-slot failed output/admission/budget preservation
pass across reuse. Mapping costs remain66/34 eager-backed pages, with zero allocator
pages retained by this heap-free dynamic witness; its image admits28 pages/112 KiB.
The fresh historical origin regression separately retains240 KiB service stack
patterns, deleted-key and heap/realloc checks and two allocator pages. It also
replaces the full service. Historical201 runtime suites bind unchanged executable
source bytes; they are not counted as fresh targets.

The stop case deliberately uses one full round:82 parked service workers are
stopped, reclaimed and replaced by another full82-worker generation; no dynamic
reuse-after-service-stop claim. Ordinary dynamic reuse executes one full service
plus small-peer replacement. Repeating two dynamic service generations and four
rounds exceeded the unchanged30-second budget and remain unqualified stress.
162 lifetime admissions are less than the observed281 host-engine lifetime;
helper placement/cost, engine memory/latency and full startup/fini/restart remain.

All eleven attempts are preserved:

| Attempt | Outcome and disposition |
| --- | --- |
|1|Origin regression reaches all three worker terminals but final supervision times out. No dynamic case ran; incomplete acceptance, cause unresolved.|
|2|Origin regression passes; dynamic compilation fails because the restricted SDK lacks stdatomic.h. Use pinned Clang C11 atomic builtins instead.|
|3–4|Small dynamic peer terminates; four-round service times out. Reducing only stack touches does not establish the cause.|
|5|Diagnostic reader itself times out at100000 iterations; no workload acceptance.|
|6|Diagnostic-only result725 reaches first round3 publication. Progress observation, not completion.|
|7|Two-round service still times out; small peer terminates.|
|8|Diagnostic-only result724 reaches first round2 retirement with no recorded error.|
|9|Parked detached exit permits a full162-admission service terminal; repeating it times out in generation2.|
|10|Scoped ordinary dynamic guest completes supervisor100/reclaimed3, but recipe still expects service replacement instead of peer replacement; failed receipt assertion.|
|11|Correct per-case replacement assertion; all seven fresh cases pass on final frozen bytes.|

Failure handling wakes phase/preflight/reaped/arrival barriers so rejected creation
cannot strand cleanup awaiting a future call. Original semantic failure remains;
confirmed reclamation does not turn a control into success. Diagnostic trace flags
are absent from every final target command. Diagnostic runs are labelled separately
and never treated as passing concurrency coverage. No deadlines are raised.

Full137 Python/Zig/Rust/pin/workflow checks, scoped formatting, simplicity snapshot,
links, artifacts/tools/SDK/source and accepted-design bindings pass. Archive readback
verifies every member before removing only the owned duplicate output tree. All
failed sources, recipes, logs, binaries, SDK and upstream notices remain sealed.

Offline reproduction from a fresh owned root:

```sh
python3 docs/evidence/native-service-dynamic-2026-10-05/sdk-setup.py
python3 docs/evidence/native-service-dynamic-2026-10-05/qualify.py 1
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

`checks.py` validates the original eleven-attempt receipt set. `diagnose.py` is an
explicit private progress diagnosis, not a conformance suite. `archive.py` performs
all-member readback and removes only verified duplicates. Production SDK/reaper
integration and independent readers/consumers remain open. No companion SESSION,
filesystem, package or assembled R1 acceptance is delivered by this experiment.
