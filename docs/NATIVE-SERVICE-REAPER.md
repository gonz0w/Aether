# Worker-driven native service cleanup

Private producer qualification passes,2026-10-05. The
[packet](evidence/native-service-reaper-2026-10-05/README.md) and
[before-code scope](evidence/native-service-reaper-2026-10-05/contract.md) extend
[actual TSD/retirement](NATIVE-SERVICE-RETIREMENT.md) with one joinable cleanup
worker while the primary blocks in real musl pthread_join. It consumes one of
82 service/two small-peer slots, leaving81/one detached peers. Existing held
domain grants, exact IDs and confirmed stop before unmap/retire remain;
no kernel/public ABI/SDK, quota or pin changes.

Eight fresh final native cases cover joinable/primary-driven regressions, worker-
driven and descending cleanup, parked stop/replacement, wrong-grant355, early-
unmap352 and omitted-primary-park356. Main requires an actual zero native compare-
park result and completed retirement before join returns; local flags or yielding
alone cannot pass. Mapping costs remain66/34 pages per actual pthread with1024-
byte TSD and two retained allocator pages. Full137 Python/Zig/Rust/pins/workflow
and scoped checks pass. All four attempts, including build-guard and direct-Rust-
linker infrastructure failures, remain sealed before owned duplicate cleanup.

From a fresh owned root run the packet's `sdk-setup.py`, `qualify.py 1`, then
`zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`.
Production reaper placement, worker-origin/concurrent creation, dynamic lifetime
schedules, engine providers/configuration, calibrated clocks, runtime closure/
startup/peak and independent consumer acceptance remain separate. Counting the
helper against82 does not admit82 detached engine workers. This witness supplies
no companion SESSION handoff or R1 release.
