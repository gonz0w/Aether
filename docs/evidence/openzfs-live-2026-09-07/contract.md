# Active worker and event-sampled allocator observation

Extend only the existing host-only libzpool observer. Under LIVE_THREADS, reserve
a fixed record before pthread_create, publish success under the observer lock,
and release through pthread cleanup on routine return or pthread_exit. A held
observer lock prevents a child completing before successful creation is counted.
Creation failure returns its reservation; never change engine worker policy.

Measure overlapping registered worker intervals and associated requested stack/
guard bytes. Cleanup precedes TLS destructors and actual pthread/kernel exit, so
these counts are not OS-live-thread census, native stop proof, resident stacks or
stack high-water. Sample mallinfo2 at successful create, cleanup and lifecycle
snapshots. Report event-sampled maxima separately; no true heap peak claim.
The fixed observer records and mutex perturb scheduling and consume host memory.
No host authority, production policy or kernel ABI changes.

Use the retained OpenZFS archive/static engine, pinned offline container and fresh
owned media. Compare unchanged host CPU view and modeled one-CPU view. Warmup plus
ten processes per view, all original storage checks, read-only zdb, byte-corruption
and existing-file controls. Add two simultaneously gated workers with return and
explicit pthread_exit, exact peak/cleanup-bypass controls. Sources freeze during
qualified runs; preserve all attempts. Run host/pin/workflow and scoped formatting.
Record counters by stage, raw samples and summaries; do not choose a native budget
or claim production filesystem acceptance from these measurements alone.
