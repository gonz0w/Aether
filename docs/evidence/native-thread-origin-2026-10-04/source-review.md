# Static OpenZFS caller-origin evidence

The sealed OpenZFS2.4.4 commit71a9f9578616a90c3c14bb59629fb4d31bfd68d1 archive
SHA256 is bd042e3e172d3194c5c5230bf427a54acaf8718f9981789ddd81ad18e8ab46a8.
Four exact original source files and their identities are retained under the
owned source-review tree in artifacts.tar.gz, with source-review.json. CDDL
notices are preserved. No upstream algorithm is modified by this source review.

| Source | Concrete path |
| --- | --- |
| module/zfs/txg.c:520,602 | txg_sync_thread calls spa_sync(spa, txg). |
| module/zfs/spa.c:11029 | spa_sync finishes by calling spa_async_dispatch(spa). |
| module/zfs/spa.c:9985,9991 | Pending unsuspended async work with no existing async thread creates one via thread_create. |
| include/sys/zfs_context.h:221 | The user-space thread_create macro invokes zk_thread_create. |
| lib/libzpool/kernel.c:98,144 | zk_thread_create sets real pthread attributes and invokes pthread_create. |

This establishes a real worker-origin path that a primary-only adapter cannot
preserve by increasing its child count. It is conditional reachability, not a
recorded native engine execution, complete call graph, frequency or allocation
measurement. The independently retained host profile is still the demand baseline.

Kernel review: permission gates depend on the explicit origin flag and the same
validated domain grant. Free-slot selection excludes the running creator; copying
its execution mask cannot alias candidate reset. Exact-ID retirement refuses any
running record, so a caller cannot erase its own current context. A different live
context may retire a confirmed stopped peer; result publication then targets the
unchanged caller context. Existing clear-TID/wait/stack/TLS obligations and IF-clear
serialization remain. No TID, entry address or software parenthood grants authority.
Legacy creation/retirement and slot-zero observation roles remain unchanged.

Nested tests use bare stack/FS-cookie contexts and trap boundaries; they do not
prove production musl TCB, libc allocator concurrency, general process parentage,
cancellation or full engine startup. Existing actual pthread lifecycle regressions
qualify their unchanged bounded adapter, not new public worker-origin adoption.
