# Independent native read-only file client (UL-039)

The default read-only mode has four passing native QEMU cases with an independent
userland C protocol client and
startup bridge linked to Aether's existing Rust file-service experiment. This
consumes the read-only AENFS001 profile. The service's optional writable mode is
not enabled. No kernel/sys-init working-tree implementation, libc file facade,
POSIX VFS, shell execution or package installation is added.

## Consumer and owner boundary

The owner Rust service and raw conformance supervisor are rebuilt unchanged for
the positive case from an isolated source snapshot. The userland-authored
service-start.c supplies musl startup, initialized TLS and the bridge functions
required by that service. The client uses the existing userland channel adapter,
gets two explicitly transferred endpoint grants from auxv, and verifies they are
distinct. A replacement client launched without endpoints must observe neither
grant and must be denied channel-factory authority.

Request/reply frames are 32 bytes in the owner's little-endian format. The client
sends at most 5 bytes and receives at most 9 per operation, accumulating a complete
frame and yielding on EAGAIN. It rejects zero/oversized intermediate transfers,
bounds retries, verifies reserved reply fields and explicitly decodes signed
results. This is a test protocol client, not public read/open syscalls or a new
shared filesystem protocol. One already-delegated connection is the authority
boundary; no multi-client authentication or reconnection is inferred.

The owner supervisor checks channel-pool limits, invalid startup-record rollback
preserving both endpoints, duplicate-endpoint rejection and loss of supervisor
access after pair transfer. Successful completion requires client 29, service 17,
replacement 33 and supervisor result 100 with three reclaims. Sys-init's producer
was not used or extended; this is kernel-conformance integration, not sys-init
service adoption or production supervision policy.

## Reproduce and evidence

```sh
python3 experiments/native-files/check.py \
  --aether /Users/cam/DEV/aether \
  --sdk build/native-c-xhkdw6jv
```

The runner verifies the strict native libc receipt/archive and pinned LLVM/make
executables, records the complete SDK inventory before use and checks it afterward.
It captures a private kernel source tree and rejects source changes during capture.
All compilation and QEMU activity use that copy; there is no fetch, real-prefix
install, activation or sibling source mutation. Rust 1.98.0, Zig/QEMU versions,
boot dependency manifest, commands and smoke parameters are retained. Host tools'
shared-library closure and source authentication remain separate limitations.

The final run is `build/native-files-userland-utz95ewe`, using the kernel snapshot
first captured at `build/native-files-userland-ozqzu6cd`. The service snapshot had
been formatted after the initial read; the exact corruption anchor was refreshed
before reuse. The runner links target startup/libc explicitly, rejects unresolved
symbols/Linux syscall instructions and checks the native profile's required TLS
segment before boot. Native loader admission tests the actual resulting ELFs.
The unstripped Rust-linked service stays subject to the existing image/page limits;
no kernel quota was increased to accommodate it.

[Durable evidence](../../docs/evidence/native-files-userland-2026-09-05/summary.json)
retains exact source/SDK/tool/ELF/supervisor/envelope/ISO identities, link maps,
commands and four serial logs. The pinned owner's native_smoke helper records the
QEMU invocation in source: BSP TCG, one core, 256 MiB, no network, private firmware
variables and 30-second watchdog. Build commands have 180-second timeouts.

Three incomplete development runs are preserved under build/: the first rejected
an outdated source-mutation anchor; the second hit the native loader's mandatory
TLS requirement; the third rejected the client's incorrect 16-byte script-size
assumption. They are not counted as passing cases. The startup bridge now creates
and checks TLS; the client verifies the full 17-byte script including its final
newline and EOF. No unrelated failure was substituted for an acceptance oracle.

## Results

| Case | Exact required outcome |
| --- | --- |
| positive | All protocol/authority/data/lifetime checks below; service 17, client 29, grant-free replacement 33; supervisor 100 with three reclaims; AETHER NATIVE FILE SERVICE PASS |
| wrong-data | Owner service's wrong_data build corrupts reply bytes; independent client exits 171; supervisor 611 before reclaim; exact native C profile-rejection panic |
| truncated | Client sends only 5 bytes of a request then consumes its output endpoint; service exits 121 for partial frame, client drains to EOF; supervisor 611 before reclaim and exact profile-rejection panic |
| wrong-root | Test-only private service variant incorrectly accepts root handle zero; client rejects the successful unauthorized open with exit 150; supervisor 611 before reclaim and exact profile-rejection panic |

The last variant changes one checked source anchor and records original/mutated
source hashes. The first data mutation uses the existing owner build option.
Neither control modifies the sibling service source or weakens the positive image.
Negative cases cannot pass on timeout, unrelated panic or mere nonzero status;
they require the specified terminal context and no success marker.

Positive client assertions cover:

- Read-only bootstrap root with no write-root grant, distinct endpoint grants and
  wrong-direction channel denial.
- Invalid root, write-rights escalation, missing file, traversal, dot/empty names,
  nonzero open offset, unterminated name, nonzero name padding and unknown opcode.
- Two simultaneous open records, exhaustion without losing live handles, read
  length/padding errors and malformed close preserving the open record.
- Write denial followed by unchanged exact content: all 18 bytes of message.txt
  in 4/9/5-byte application reads, all 17 bytes of hello.sh in 16/1-byte reads,
  EOF at/beyond length and zero reply padding after short reads.
- Consuming close, stale/double-close rejection, fresh generation identities,
  three-generation retirement of each record, and final EMFILE despite free but
  retired records. Earlier malformed requests do not consume these generations.
- Request-endpoint closure, service EOF shutdown, response drain/EOF and the
  supervisor's final channel/child cleanup and grant-free replacement checks.

Negative runs intentionally end at the conformance rejection before reclaim;
only the positive case establishes this fixture's full final cleanup. The suite
has no concurrent clients, replay/restart, interrupted RPC, arbitrary malformed
reply fuzzing, native descriptor offsets/duplication or disk-backed namespace.
The protocol uses explicit read offsets and embedded immutable seed files.
Default SMP, prior channel/memory and sys-init suites were not rerun because their
implementations were unchanged; no cross-project acceptance is inferred.

## Follow-on

UL-040 completed [four writable cases and four fresh read-only regressions](WRITABLE.md): write-root
separation, failed-create publication, capacity/overflow rejection, read-only
aliases, sparse zero fill and truncate/extend clearing. That is a separate scope;
the original UL-039 checkpoint enabled no write authority. UL-041 next
prototypes a bounded local descriptor layer; native process/exec support remains open. Shared PD ownership review and M3
process/exec/FD requirements remain open.

The [bounded descriptor layer](DESCRIPTORS.md) separately tests shared positions,
duplication and last-close lifetime over the writable protocol (UL-041).
