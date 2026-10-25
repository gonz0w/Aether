# Actual taskq dependency and draining

The [contract](contract.md) precedes implementation. The
[assessment](../../OPENZFS-FEASIBILITY.md#actual-taskq-dependency-and-drain-result--2026-09-06)
records results, allocation limits and the next native bridge contract.

The new BSD-2-Clause C fixture links the unchanged OpenZFS 2.4.4 engine archives.
It initializes the real system taskqs/TSD and runs three cycles with separate
single-worker A/B queues. A waits for work on B; a joined observer thread calls
actual taskq_wait_id(A, 1). Gates keep B and then a later A callback unfinished.
The drainer cannot complete until both finish. Callback queue-TSD checks, actual
cv_wait entry observation, nonblocking admission rejection without state changes,
post-drain entry reuse and queue teardown all pass. No inline-dispatch mode is used.

One warmup plus ten repeated positive processes pass (30 measured fixture cycles,
three warmup cycles). Exact exit-2 controls pass with only these diagnostics:

- TASKQ FAIL: premature drain
- TASKQ FAIL: delayed dispatch unsupported

The first variant returns immediately from wait_id. The second calls real delayed
dispatch but lies about success; it does not synthesize a delayed callback. A
timeout or generic error would fail qualification. Gate deadlines are five seconds;
the outer QEMU/process bounds are 30/120 seconds. Actual delayed dispatch returns
zero and never runs its callback; cancel remains ENOENT. TQ_SLEEP behavior is not
tested and its maxalloc is not a hard ceiling. The fixture uses only TQ_NOSLEEP.

The observer forwards cv_wait unchanged and tracks only an atomic watched-CV
pointer; it clears that pointer before queue destruction and never dereferences
freed queue storage. Atomics synchronize gates and callback completion. Internal
queue fields are inspected under the upstream mutex. Destruction checks refer to
queue state, not confirmed pthread termination or safe native stack/TLS reuse.
The system queues still start their default workers. This is a Linux/glibc witness,
not a two-thread whole engine, a native Aether runtime or safe general executor
consolidation. There is no storage media or filesystem workload in this slice.

## Evidence and reproduction

Build and qualification pass on their first attempts. All 98 Python tests, Zig
host checks, immutable pins, workflow inventory and pinned Clang formatting pass.
engine-identity.json freshly verifies all 4063 original engine files and static
archives against the preceding exact engine-inputs.json. No upstream source or
notice was changed. No kernel, sibling, capacity or release-pin change is included;
no new native QEMU regression or full storage qualification is claimed here.

artifacts.tar.gz retains source, build recipe, objects and three executables.
qualified/sources.tar.gz and results.json bind frozen source/artifact digests,
exact argv, expected/observed exits, UTC receipts and raw logs. Use the pinned
local cross-tool image c48ba36c2b92494aa7ebfb957cce38a26792507e26ed24ae1fa010038da53c74
and retained engine work from the [baseline](../openzfs-runtime-budget-2026-09-06/README.md).
Compiler/emulator are GCC 14.2.0 and QEMU 10.0.11. The local image remains a
prerequisite, not an exported toolchain or newly installed dependency.

For build.mk, mount retained engine work at /work:ro, source/recipe at /inputs:ro
and a fresh owned output at /out:rw. From the engine source directory run
`timeout 120 make -f /inputs/build.mk observe`; expanded commands are retained in
build-attempt-1.log. Only cv_wait, taskq_wait_id and taskq_dispatch_delay link
references are wrapped. The production engine implementation stays unchanged.

qualify.py is the one-off runner with exact local paths. It requires matching
artifacts and a new qualified directory; retain existing attempts under distinct
names instead of overwriting. Runtime mounts only the private probe tree read-only;
there are no writable media or host-device mounts. Containers use --pull=never,
--network=none, --read-only, dropped capabilities, no-new-privileges, bounded tmpfs
and 2-GiB/512-pid limits. Repetitions are functional evidence, not a throughput or
memory-peak benchmark. Build/setup and warmup are separate.

Next is the native taskq platform contract: TSD initialization, explicit admission/
allocation failure and stop/reap ownership under existing grants. Live resource
peaks, broader dependency closure, native execution and production service/consumer
acceptance remain unqualified.
