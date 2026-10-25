# Actual musl reader/writer lock witness

Implement the accepted OPENZFS-FEASIBILITY next witness in Aether's restricted
lifecycle adapter. Keep production libc with userland and all kernel grants,
quotas, admission limits, source pins and sibling files unchanged. Rebuild the
seven upstream rwlock operation sources against the same private syscall seam;
retain original source identities and notices. No timed/shared lock API claim.

Batch one: both children hold read locks; parent try-write rejects without lock
mutation, then a real writer wait triggers readers to unlock. Batch two: parent
holds write lock; both readers must wait, try-read rejects without mutation,
unlock releases them. Observe shared readers/exclusive writer, wait counts,
TLS/masks/join/retirement and clean lock/wait/quota state across batches and
supervisor replacement. Deliberately bypass the parent write lock in batch two;
require exact exclusion failure status 251, never generic timeout as success.

Use existing --pthread-lifecycle commands for both memory sizes, all older cases,
Zig/host/standards/workflow, pinned clang-format and upstream adaptation checks.
Freeze sources during qualification; preserve every failure. No runtime memory
allocation except the existing bounded musl child lifecycle; no new kernel lock.
