# Native process/descriptor handoff (UL-037)

The canonical shared proposal is
[Aether-standards PD-01–PD-12](../../../Aether-standards/drafts/distribution-v0.2.0/PROCESS-FD.md).
Its [owner-review record](../../../Aether-standards/drafts/distribution-v0.2.0/PROCESS-FD-REVIEW.json)
is pending, with no approvals. The draft names four affected owners and unresolved
placement, bounds, vfork, atomic flag, signal/close/lifetime and namespace decisions.
This local page tracks consumer work; it does not repeat the shared contract.

The proposal links UL-034's dash reference, UL-035's process/descriptor witness and
UL-036's fallback comparison. It also accounts for the kernel's newer bounded
[NATIVE-LAUNCH](../../aether/docs/NATIVE-LAUNCH.md) and
[NATIVE-CHANNEL](../../aether/docs/NATIVE-CHANNEL.md) mechanisms. Those source
contracts were read and hashed; their reported runtime suites were not rerun.
They explicitly exclude POSIX fork/exec/wait, descriptor inheritance/duplication,
blocking pipes and a shell. No kernel/sys-init implementation changed here.

## Ordered local work

1. UL-038 completed [six native channel cases](../experiments/native-channel/README.md).
   Its scoped work was to recheck launch/channel producer interfaces and build an
   independent userland consumer using existing kernel-owned profile semantics.
   Exercise copied arguments, bounded ordered data, EOF/EPIPE, endpoint-transfer
   denial/rollback and cleanup/reuse. Retain matching artifacts and exact negative
   oracles. Use isolated kernel copies and owner-produced supervision artifacts;
   do not silently edit sibling implementations to fit the harness.
2. Obtain affected-owner review of the shared draft's implementation assignments,
   authority, limits and open gates. User authorization to draft is not owner
   acceptance of a new native ABI. Record actual reviews in the canonical record.
3. After agreed mechanisms exist, extend userland adapters and run the pinned
   dash script workload with direct native executable replacement, inherited FDs,
   files, pipes, wait/reap and cleanup. M3 remains open until its native cases pass.

UL-038 consumed the existing bounded mechanisms without claiming adoption of
the new shared proposal. Missing mechanism support remains an explicit gap;
unsupported semantics must not become successful stubs. The checked fallback
patch remains experimental and unadopted. Broader UL-003/007/015/016 work persists.

No immutable release, standards registry or consumer pin changed. Standards
checks validate release integrity, local links and existing offline cases; the
new pending record additionally passed its structural validator. No new runtime
or synthetic process implementation is claimed by this documentation checkpoint.

UL-039 completed [four read-only file-service cases](../experiments/native-files/README.md).
UL-040 completed [writable scratch and read-only regressions](../experiments/native-files/WRITABLE.md).
UL-041 completed [four bounded descriptor cases](../experiments/native-files/DESCRIPTORS.md)
and eight fresh file-client regressions over those mechanisms. UL-042 completed [seven injected reply/close cases](../experiments/native-files/FAILURES.md)
and twelve regressions. UL-043 completed [four bounded libc cases](../experiments/native-files/LIBC.md)
and nineteen regressions. UL-044 completed [four bounded FILE cases](../experiments/native-files/STDIO.md)
and twenty-three regressions. UL-045 completed the [current dash/companion gap refresh](NATIVE-DASH-GAPS.md)
and three inspected requester ELFs. UL-046 completed [six independent broker cases](../experiments/native-process/RUNTIME.md).
UL-047 completed [six coexistence cases plus six ABI 5 regressions](../experiments/native-process/COEXIST.md).
UL-049 completed [six independent ABI 9 multi-client cases](../experiments/native-process/CONNECTIONS.md),
with ABI 8 reviewed only. UL-050 completed [six fixed-alias shared-file cases](../experiments/native-process/SHARED.md).
UL-051 completed [nine admission/collection cases](../experiments/native-process/INHERITED.md).
UL-052 completed the [bounded libc/FD integration review](INHERITED-LIBC-PLAN.md).
UL-053 completed [fourteen inherited musl read/close cases](../experiments/native-process/INHERITED-LIBC.md).
UL-054 reviewed the delivered [file-I/O extension](GENERAL-FILE-IO-REVIEW.md);
UL-055 completed [ten libc read/write/EOF cases](../experiments/native-process/FILEIO-LIBC.md).
UL-056 prepared the [real bytecount command](../experiments/command-runner/README.md)
and [candidate contract review](COMMAND-IO-REVIEW.md). UL-057 completed [nine native command cases](../experiments/command-runner/NATIVE.md).
UL-058 next tests the two-binding command failure boundaries;
reconnection and general native process/TTY support remain separate.
These checkpoints do not imply native fork/exec inheritance, POSIX VFS, persistence
or packaged service support.
