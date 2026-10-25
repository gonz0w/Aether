# Shared read/EOF owner review (UL-054)

The requested owner extension is already delivered as the separately identified
`file-io` mode in Aether's NATIVE-FILE-IO contract and completed
native-file-io-2026-09-05 evidence. UL-054 therefore consumes that handoff rather
than publishing a redundant request or changing sibling implementation. Canonical
cross-project standards and pending PD review are unchanged.

The completed mode supplies validated 0–16-byte reads, short reads and repeated
EOF, with one authoritative broker position and no peer-position scheduling gates.
Zero-length reads validate the live reference. Parent writes accept 0–16 bytes,
advance by actual positive results, and report ENOSPC at the 64-byte backend bound.
Child writes require EACCES, including zero count. Final independent storage
readback detects acknowledged writes without effects. Old two-byte modes retain
their contracts and pins.

The selected consumer (UL-055) uses real musl read/write/close through a separate
adapter. It sends zero-length reads to the owner, preserves errno, and permits
larger libc buffers through one capped 16-byte transfer per call. No implicit
multi-request write loop, read-ahead, seek or local offset is introduced. Callers
handle short results explicitly. Invalid descriptor and overflow/null checks
remain local; raw malformed/foreign/zero-count requests independently exercise
owner enforcement.

The exact workload reads `ab` in the parent, admits the read-only child, then reads
`cde`, a one-byte short `f`, and repeated EOF in the child. After collection, the
parent verifies EOF, writes 58 X bytes in bounded transfers, tests ENOSPC and EOF,
and closes. The owner independently checks all 64 stored bytes before final close.
Run two generations, plus frozen-position, consuming-zero, widened-rights and
skipped-storage controls. Retain invalid-FD/errno controls and lost/corrupt reply
poison/no-replay checks. A lost-close reply is injected only after required storage
writes complete, so the actual consuming close can finish before reply suppression.

Broader open/seek/dup/flags, multiple independent records, standard FDs, arbitrary
startup arguments and real command execution remain separate. Aether's CR-01
command-runner proposal is now the next concrete integration candidate: bytecount
needs two inherited records (stdin and stdout), copied argv/env and normal exit 0.
The current one-reference conformance client cannot substitute for it. UL-056 will
review that proposal and prepare the userland workload/contract handoff.

[UL-055 results](../experiments/native-process/FILEIO-LIBC.md) identify the pinned
source archive, runtime outcomes and limits. No sibling files were modified by
this review or its consuming experiment.
