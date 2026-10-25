# Independent one-entry inherited launch and collection (UL-051)

Nine native cases pass using independent Clang/musl parent/child clients and the
completed `native-inherited-collect-2026-09-05` producer snapshot. This includes
parent-requested admission of one read-only child alias, rollback after explicit
native rejection, and consuming collection of the child's observed normal exit.
Aether supplies the broker, file backend and startup bridge on unchanged ABI 9.

The parent first reads `ab`, then requests a child referencing the same broker-owned
file position. The child receives a distinct connection-bound reference at index
10 with read-only rights. It reads `cd`; the survivor reads `ef`. Both child-first
and parent-first exit orders repeat across two generations with six reclaims.
The client tests retain shared-file bootstrap, reply padding, malformed read/close,
foreign/stale/reference-index and endpoint/factory checks from UL-050's independent
approach. Older test sources remain unchanged.

Admission probes reject zero/multiple entries, wrong child index, executable selector,
reserved fields, widened rights and foreign/stale/wrong-index source references.
Rejected replies must contain no receipt or metadata. Success must contain the
exact generation-scoped receipt and zero remaining fields. Duplicate admission
returns EBUSY. The child independently requires EACCES for admission and collection.
Only explicit first-round injected EINVAL/EBUSY admission failures are retried;
transport failure or a malformed response aborts rather than replaying admission.

Before admission, collection returns ECHILD. After admission, wrong source selectors,
foreign/stale receipts and nonzero reserved payload reject. Child-first collection
polls only explicit EAGAIN responses and requires receipt, actual detail 29 and
kind 1, then ECHILD on repeat. After the parent closes its file alias, collection
still returns ECHILD if already consumed, or EAGAIN in parent-first mode while the
child awaits parent exit. Closing a file alias does not erase the separate result
ownership or revive file authority. Parent-first may abandon result collection;
broker teardown still removes references and reclaims workers.

| Case | Required independent observation |
| --- | --- |
| Positive | Parent-requested child; terminal order 2/0/1 per round; six reclaims |
| Parent-first | Terminal order 0/2/1 per round; six reclaims |
| Rejected native launch | Explicit EINVAL, then successful retry and both rounds |
| Partial channel reservation | Explicit EBUSY, then successful retry and both rounds |
| Leaked partial reservation | Parent retry assertion 70; supervisor 970/reclaimed 0 |
| Leaked rejected admission | Parent retry assertion 70; supervisor 970/reclaimed 0 |
| Accepted excessive child rights | Parent assertion 66; supervisor 970/reclaimed 0 |
| Altered terminal detail | Parent assertion 75; supervisor 970/reclaimed 0 |
| Repeated successful collection | Parent assertion 76; supervisor 970/reclaimed 0 |

Every positive requires client exits 29, backend exits 17, supervisor 100 and
`AETHER NATIVE CONNECTIONS PASS`. Each negative requires its exact worker/broker
context, designated rejection and no success marker. Rollback controls use actual
native failed launch/second-channel allocation, with owner cleanup checks and
successful independent retry/data/lifetime observations. The rights control detects
incorrect admission acceptance; it does not grant actual child write authority.
The final backend-close/stale-handle probe remains owner code. Timeouts, build
failures and unrelated panics cannot pass a case.

```sh
python3 experiments/native-process/inherited.py --aether ../aether \
  --producer ../aether/docs/evidence/native-inherited-collect-2026-09-05 \
  --sdk build/native-c-xhkdw6jv
```

The producer summary, archive and report are pinned; only hash-matched listed
regular source files are materialized in a private build root. Archive links,
traversal, duplicates and unlisted paths reject. Boot inputs are verified by pinned
owner tools. SDK and compiler inventories match UL-044's tested strict-musl pin.
Six client ELF variants pass static x86-64/TLS/NX/W+X/dynamic/undefined-symbol and
Linux-syscall inspection. Commands and version logs retain Clang/LLD 21.1.8, Rust
1.98.0, Zig 0.16.0 and QEMU 11.1.1. The normal immutable broker is 5288 bytes within
its unchanged two-page bound. QEMU uses TCG, one CPU, 256 MiB, no NIC, private
firmware variables and the pinned 30-second watchdog. Source/SDK stability passes.

[Retained evidence](../../docs/evidence/native-inherited-userland-2026-09-05/README.md)
includes exact sources, producer archive, clients, backend, brokers, receipts and
serial logs. Large images remain in `build/native-inherited-userland-wrwi402h`,
identified by receipt hashes. All nine cases passed on the first build/run. All
three standards checks pass. No kernel, sibling implementation, shared adapter,
older test source or standard changed; unrelated native suites were not rerun.

This is a one-entry bounded spawn/result protocol, not fork, vfork, in-place exec,
POSIX waitpid, a general FD table, libc integration or native shell support.
Successful admission or collection followed by lost reply remains unresolved;
there is no exactly-once delivery, transparent replay or broker recovery. Pending
shared PD review, sys-init policy and pkg-mgr transport remain separate.

UL-052 completed the [libc/FD integration review](../../docs/INHERITED-LIBC-PLAN.md).
UL-053 completed [fourteen bounded musl read/close cases](INHERITED-LIBC.md),
preserving unsupported count/operation limits. UL-054 next specifies general-size
shared reads and EOF with a concrete owner handoff.
M3 still requires real shell/process/pipe behavior.
