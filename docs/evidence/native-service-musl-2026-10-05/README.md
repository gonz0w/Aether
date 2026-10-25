# Native musl service storage

Status: private producer qualification passes, 2026-10-05.
[Before-code scope](contract.md) follows all eleven accepted 2026-10-04 designs;
[reference](../../NATIVE-SERVICE-MUSL.md) records the boundary and remaining work.
VM objects/demand paging and production musl remain future work with their owners.

Four final native cases ran fresh in attempt7: capacity, stop while all workers
are parked, actual corrupted musl self-pointer (exact331), and actual guard write
fault (#PF/error6, terminal142) followed by replacement. The compiled supervisor
checks fault observation143 (detail plus one), stop (144,3), exact four-byte primary
yield accounting, stale handles and three confirmed reclaims. Markers and the
existing native ABI, SDK/pins, quotas and kernel implementation remain unchanged.
No kernel, maintained user source, sibling or released standards bytes changed.
Full137 Python/Zig/Rust/pin/workflow checks pass.

The service simultaneously holds82 real joinable musl pthreads, each with256 KiB
requested stack, actual copied TLS/TCB and a4 KiB inaccessible guard. Each complete
mapping costs66 eager-backed pages:65 accessible stack/TLS pages plus the guard.
The small peer holds two128 KiB-requested threads at34 pages each. Native grant
accounting exactly matches those mappings. Workers touch and verify240 KiB each
(4 KiB on the peer), preserve independent TLS/errno, and all park before counted
wake reaches exactly82/two. This is a synthetic touched-stack workload, not engine
stack high-water. Keys/destructors, detached cleanup, cancellation and broad timed/
multithreaded signal paths are not enabled by this witness.

With all threads live, malloc/free works (512 KiB service,4 KiB peer). A64 MiB
realloc fails ENOMEM with unchanged grant count and all original bytes preserved.
Actual musl join releases stack mappings and native records; only two allocator
pages remain afterward. Parent TLS/list state and exact fresh-generation IDs pass.
The82 thread mappings total5412 pages (21.140625 MiB), leaving2752 pages after the
small112 KiB test image admission. These are this fixture's measured reservations;
the much larger engine image/heap/cache budget still needs native measurement.

All attempts are retained:

- Attempt1: fixture compile failure, missing copied wait-counter declaration;
  no guest ran.
- Attempt2: both guests ran; the primary fixture read result bookkeeping before
  its creator published it (331). Peer expected ENOENT while another child still
  existed; actual EBADF correctly caused339.
- Attempt3: isolated self/cookie/ID/errno checks reproduced the primary publication
  race; the corrected peer completed. This is fixture failure, not a kernel defect.
- Attempt4: publication handshake and exact any-child retirement results fixed;
  capacity/stop/self cases pass. Guard injection mistakenly also faulted replacement,
  correctly rejected after the first fault was reclaimed.
- Attempt5: injection restricted to generation1, but supervisor confused serial
  detail142 with observe-result143 and correctly rejected the first fault.
- Attempt6: all four cases pass. Attempt7 removes an unused copied big-image branch
  and reruns all four on final source bytes; both successful snapshots remain.

Admission can run a child before its creator returns. The private adapter publishes
its slot/ID behind an atomic flag; the child waits for that bookkeeping before
reading it. Upstream musl create/join/wait/map functions remain pinned and source-
rebuilt by the existing builder. Joins save the native ID before upstream unmapping
and never dereference the retired TCB. Per-attempt source/recipe snapshots, actual
commands, images, logs, time bounds and source/tool/SDK hashes remain in the archive.

Offline reproduction in a fresh owned output root:

```sh
python3 docs/evidence/native-service-musl-2026-10-05/sdk-setup.py
python3 docs/evidence/native-service-musl-2026-10-05/qualify.py 1
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

The setup verifies every member of the two sealed upstream/SDK input archives.
It never reads mutable sibling build outputs. `checks.py` validates the original
all-attempt qualification; `archive.py` seals/readbacks and removes only this
run's verified duplicate output. Reproduction may use a new attempt number in an
already staged owned root, but existing attempts are never overwritten.

Next provider identity/configuration and actual engine feature/runtime closure,
including required detached/TSD/stack/heap behavior, then native startup/fini/
restart and grant-bound volume/Rust/filesystem/packages. Calibrated monotonic/UTC,
production port/SDK and independent reader/consumer acceptance remain open.
Continued-shell SESSION expansion remains separate. No engine, filesystem or
assembled release gate closes through this bounded producer experiment.
