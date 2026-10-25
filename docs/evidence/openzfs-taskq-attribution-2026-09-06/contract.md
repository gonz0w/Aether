# Named worker attribution

Extend the Linux-only demand observer with an opt-in wrapper around
pthread_setname_np. The retained engine has one such call site, immediately after
successful pthread_create in zk_thread_create. Record requested names, even if
Linux naming fails, and preserve the real function's return unchanged. Count
names rather than retaining pthread_t values; detached IDs can be reused and are
not safe object identities. Counts are cumulative naming requests, not a live
worker census. Final count equality with successful creates plus the reviewed
single call site establishes attribution for this workload, not a generic tracer.

Use 96 fixed groups with names of at most 63 printable JSON-safe ASCII bytes;
reject overflow/unsupported names explicitly. Copy names while valid, hold the
observer mutex for table access, no allocation or worker trampoline. Emit separate
versioned JSON records at existing lifecycle snapshots, preserving demand-v1.
Counter and name records are not an atomic cross-record snapshot while workers
may create other workers. Final completed totals must match; no count is dropped.

Self-check two distinct naming requests with exact counts; an omitted-name
variant must exit 2 with the precise observer-names diagnostic. Keep the prior
counter control and storage oracles. Run one warmup and ten fresh-process samples,
existing-file/wrong-byte controls and read-only zdb with the unchanged engine,
private regular files and pinned offline container. Preserve failures and freeze
runtime sources. Host/pin/workflow and scoped formatting checks remain required.

This observes defaults, does not cap queues, substitute joins, alter worker counts,
change kernel capacity, or select a native service budget. Follow Foundations
ownership/evidence and Distribution PF baseline rules. Record source routing and
which knobs are plausible experiments versus unsupported hard-coded changes.
Evaluate dependency/deadlock constraints before any shared-pool or worker-count
policy; do not assume a one-worker queue is safe. Native ABI, sibling repositories,
release pins, mature-engine direction and Rust service ownership stay unchanged.
