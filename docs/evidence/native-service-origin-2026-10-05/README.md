# Real musl worker-origin creation

Status: private producer qualification passes,2026-10-05.
[Before-code scope](contract.md) and [reference](../../NATIVE-SERVICE-ORIGIN.md)
preserve existing native authority, owner-local quotas and published ABI/SDK/pins.
No kernel, maintained user source or sibling changes. Production musl/runtime
remains userland-owned; native engine startup has not run.

Ten final native cases run fresh in attempt2: joinable TSD and worker-reaper
regressions, concurrent origin, single-creator origin, descending origin cleanup,
parked stop/replacement, restored parent-only admission359, actual wrong-grant
clone360, premature unmap352 and omitted primary join-park356. Each control must
emit its exact terminal plus supervisor401/reclaimed0 and the named rejection
panic; generic nonzero, unrelated fault or timeout cannot pass. Stop retains the
compiled (144,3), exact stale authority and three confirmed reclaim checks.

The primary creates only two joinable service creators. Both enter actual musl
pthread_create preflight before either proceeds; each creates40 detached peers.
They count within82 live records. A single-creator variant creates81; the small
companion uses one creator/one peer. Callback identity comes from the current
native ID and atomically published record, not concurrent application argument
order. Exact recorded native creator IDs account for every descendant. Distinct
creator masks survive actual create/start and every descendant inherits the
correct mask; the primary retains its independent zero mask.

Actual musl's thread-list lock serializes clone/publication. The private adapter
asserts the actual current libc lock owner; this is bookkeeping, not authority.
Used/admission counters are atomic for reads by concurrent preflight callers.
All creators finish creation before all-worker release or cleanup. Thus metadata
publication and later cleanup have explicit separate ownership phases. This is
single-core concurrent calls, not simultaneous multicore creation or dynamic
creation overlapping retirement/reuse.

After all82/two workers park, counted wake reaches exactly82/two. The primary
blocks in actual pthread_join of creator0 while that worker cleans every detached
peer. Creator1 waits for cleanup completion, then is separately joined/retired.
The cleanup worker selects any pending request, checks running/pinned state,
permits exit, confirms exact native stop, unmaps and retires with held grants,
never reading an unmapped TCB. Descending completion qualifies reverse selection.
The primary must have completed a real zero-result native compare-and-park;
yielding/local flags alone fail356. Failure settlement permits surviving peers to
exit but leaves their mappings/records allocated before reporting the exact error.

Actual1024-byte TSD, two/four destructor calls, deleted/recreated key isolation,
parent state, independent TLS/errno and synthetic240 KiB/4 KiB stack touches pass.
Mapping costs remain66/34 eager-backed pages; the fixture image admits30 pages/
120 KiB. Bounded malloc and failed64 MiB realloc preserve old bytes/grant count;
two allocator pages remain after successful complete cleanup. Wrong-grant native
clone returns EACCES and actual upstream failure reports EAGAIN without changing
caller output, admission count or mapping budget in the single-creator control.
These are fixture reservations, not observed engine ARC/heap/stack high-water.

All attempts are retained. Attempt1 passes both regressions, then fails compilation
of the new origin case: clone_denial was declared outside its negative-only scope.
Attempt2 guards that variable, checks list-lock ownership and removes an unused
copied observation-denial branch, then passes all ten on final bytes. The compile
failure is not target rejection coverage. Full137 Python/Zig/Rust/pins/workflow,
scoped formatter, simplicity snapshot, link and frozen source/review checks pass.
Historical runtime suites bind unchanged source bytes and are not fresh targets.

Offline reproduction from a fresh owned root:

```sh
python3 docs/evidence/native-service-origin-2026-10-05/sdk-setup.py
python3 docs/evidence/native-service-origin-2026-10-05/qualify.py 1
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

Setup verifies every sealed SDK/upstream input member; no mutable sibling builds
are followed. Receipts freeze the actual pinned compiler/linker/LLVM library and
SDK/source/recipe bytes. `checks.py` verifies the original two attempts, exact
controls, final artifacts and current review bindings. `archive.py` reads back
every owned artifact before removing only verified duplicates. Commands, raw
logs, source snapshots, failed inputs and upstream notices remain preserved.

Next required dynamic lifetime/creation-cleanup overlap and production reaper
placement/resource accounting, actual providers/identity/configuration, calibrated
monotonic/UTC and engine feature closure, then measured native startup/fini/restart
before grant-bound volume/Rust filesystem/packages. Two creators count against82;
this does not admit82 detached engine workers or measure full engine demand.
Independent SDK/consumer/reader acceptance and assembled R1 remain open. Wider
companion SESSION delivery is separate; no completed production handoff is claimed.
