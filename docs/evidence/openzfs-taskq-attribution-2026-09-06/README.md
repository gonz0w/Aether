# Named OpenZFS worker attribution

The [contract](contract.md) records the bounded observer before implementation.
The [assessment](../../OPENZFS-FEASIBILITY.md#named-worker-attribution-and-service-policy-boundary--2026-09-06)
routes counts to source and defines the next topology experiment.

One warmup plus ten fresh Linux/x86_64 storage processes pass. Each first init
records 102 named requests; all 49 completed groups reconcile to 740 successful
creates. attribution.json records the stable per-group counts. Names may combine
roles: arc_evict is eight taskq workers plus one coordinator, established from
source. The observer does not identify unique queues or simultaneously live threads.

The engine's only pthread_setname_np call follows successful creation in
lib/libzpool/kernel.c. THREAD_NAMES interposes that call, preserving its real
return and recording the requested name even if Linux rejects naming. No retained
pthread_t is used for identity. A fixed 96-entry table copies names of up to 63
printable JSON-safe ASCII bytes; invalid names or capacity overflow fail the
measurement instead of silently dropping data. The table uses 6912 bytes of
static records on this target, plus its count; this is observer overhead, not a
production engine allocation. Counter and name snapshots are separately locked.
No worker trampoline, exit policy or engine task count is changed.

The new aether-libzpool-thread-names-v1 JSON line carries sequence, stage and a
groups array of name/requests pairs. Sequence/stage match demand-v1 records;
inter-record values are not an atomic snapshot during concurrent activity. The
final completed total must reconcile. Existing demand-v1 bytes/fields and the
owned-file pass/failure markers are retained. The feature is opt-in at compile
time; older evidence retains its exact original sources separately.

Controls pass: known name/attribute records, exact observer-count and observer-names
bypass failures (exit 2), test-only count-ceiling rejection, existing-file denial
without mutation, wrong-byte rejection, and read-only zdb checksum/space-map
traversal with unchanged media digest. Host checks pass (98 Python tests, Zig,
three pins and workflow), as does pinned Clang 21.1.8 formatting. All final
runtime sources and measured artifacts remain frozen. No failed build or runtime
attempt occurred in this slice. These are host-engine results; native kernel
QEMU regression results are not rerun or claimed here.

## Inputs and reproduction

Use the retained OpenZFS source/build and pinned cross-tool image from the
[preceding baseline](../openzfs-runtime-budget-2026-09-06/README.md).
engine-identity.json freshly verifies all 4063 original sources and link archives
against its exact engine-inputs.json. Original notices and licenses are unchanged.
The new observer is BSD-2-Clause. artifacts.tar.gz retains sources, build.mk,
objects and four binaries; qualified/sources.tar.gz and results.json retain exact
repository/artifact hashes, sample data, commands and UTC receipts.

Build with build.mk in the same pinned offline container. Mount retained engine
work at /work:ro, source copies/recipe at /inputs:ro, fresh owned outputs at /out:rw;
from the engine source directory run `timeout 120 make -f /inputs/build.mk observe`.
Expanded compiler/link commands are in build-attempt-1.log. THREAD_NAMES and the
fifth --wrap=pthread_setname_np are explicit; no source-engine patch is applied.
The image ID is c48ba36c2b92494aa7ebfb957cce38a26792507e26ed24ae1fa010038da53c74
(GCC 14.2.0, QEMU 10.0.11). The local image remains a prerequisite, not an exported
or newly installed toolchain.

qualify.py is a retained one-off runner with exact local input/output paths. It
requires matching artifacts and an absent qualified output directory. Preserve
any existing attempt under a distinct name before a new run; never overwrite it.
It uses --pull=never, --network=none, --read-only, dropped capabilities,
no-new-privileges, bounded tmpfs, 2-GiB memory and 512 pids. No host devices are
passed through. Each invocation has a 90-second guest/120-second subprocess
bound. Every workload creates its own private regular-file media; raw media stay
in the owned zig-out tree and their hashes are retained. Setup/build is excluded;
one warmup is explicit, ten later processes are fresh, host caches are not flushed.

This changes no worker-count policy. Fixed system workers, file-vdev floor,
compile-time max_ncpus and ZIO sizing remain. Next is a separately labeled one-CPU
service-view experiment, followed by dependency/live-resource measurements before
selecting capacity. No native persistent filesystem, Rust service, consumer
acceptance, release readiness or safe shared-executor claim follows.
