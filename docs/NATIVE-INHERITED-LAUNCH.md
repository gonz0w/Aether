# Parent-requested launch with one inherited reference

A separate opt-in [file-I/O mode](NATIVE-FILE-IO.md) adds ordinary bounded reads,
EOF and writable-parent behavior; this profile retains its existing semantics.

The `inherited-launch` producer mode extends the user-space shared-file witness
on unchanged AENMX001 / ABI 9. The kernel, six-channel quota, three worker slots,
8192-byte immutable supervisor bound and completion marker are unchanged. This
is a bounded spawn experiment, not fork, vfork, in-place exec or a POSIX parent/
child process API. Userland retains production process/FD ownership; shared PD
review, sys-init policy and package transport remain separately owned.

## Request and authority

The broker launches the file backend and parent-like client first. Only the
parent receives its bootstrap reference. After reading `ab` from the broker-owned
scratch handle, that client explicitly requests the child and one read-only
inherited alias. No child worker or child reference exists before that request
successfully admits it.

The request is one 32-byte frame of eight little-endian u32 values:

| Offset | Field | Accepted value |
| --- | --- | --- |
| 0 | operation | 4, admitted child launch |
| 4 | source reference | caller-bound live parent reference |
| 8 | source descriptor | 3 |
| 12 | entry count | 1 |
| 16 | child descriptor | 10 |
| 20 | child rights | 1, read-only |
| 24 | executable selector | 1, immutable third executable grant |
| 28 | reserved | 0 |

This is a one-entry inheritance format, not a variable-length descriptor list.
Multiple entries, another index, executable selector or reserved value return
EINVAL before native allocation. Invalid/stale/foreign source references return
EBADF. Only the parent's authenticated connection may request admission; the child
receives EACCES. Child rights other than the agreed read-only subset return EACCES,
including a request for the parent's read/write rights. Once admitted, another
valid request returns EBUSY for the remainder of that round, even if the child has
already exited. No second child or duplicate side effect is published.

Success returns status 0 and a connection-local receipt `0x53000000 | generation`
at offset 4; the remaining reply bytes are zero. This receipt is not a kernel
capability, waitpid handle or recovery token. The collection extension below uses
it only within its original parent connection. Failed replies do not mint a receipt.
The child receives its distinct read-only reference at index 10 on its private
bootstrap connection. The request cannot select a kernel handle or supply caller
identity, and no backend raw handle is exposed.

## Admission and rollback

The broker validates the complete fixed request before reserving a private
request/reply pair. If allocation of the second channel fails, it closes both
ends of the first. Native paired launch then validates the executable/startup and
transfers the child endpoints atomically on success. On native rejection, all
four reserved endpoints remain broker-owned and are closed. Neither the child
reference nor route is published; parent position and ownership remain intact.
Only successful launch commits the child route and live reference. The broker
commits those before sending child bootstrap or servicing any child request.

The targeted rejection test submits invalid argc through the real native launch
operation on the first attempt of the first round. Its EINVAL response is followed
by a successful parent retry; the admitted child remains native generation 1.
Another test temporarily reserves one channel, leaving only one available. Child
reservation obtains that last channel but cannot obtain its pair; it rolls back,
the test reservation is removed, and retry succeeds. Neither failure is a public
request option. Both tests repeat normal lifecycle work in a second round, using
the remaining bounded channel generations rather than resetting pools.

The broker checks rejection leaves the parent offset at 2 and no child reference.
Subsequent actual child `cd` and survivor `ef` reads, successful retry and final
resource accounting provide target evidence for those effects. Existing invalid
request probes occur before admission and must not consume enough generations to
prevent those successful rounds.

A successful launch followed by lost bootstrap/reply delivery remains an owned,
unresolved child, not a rejected launch to replay. The current fixture aborts on
such transport failures; reconciliation and arbitrary failure cleanup are not
implemented or claimed. No transparent retry, cancellation or supervisor recovery.

## Lifetime witness and validation

### Connection-owned terminal collection

Operation 5 collects one retained child result. Offsets 4 and 8 echo the parent's
bootstrap reference/index; offset 12 carries the admission receipt, and bytes
16–31 must be zero. The native connection selects the caller. The child cannot
collect; a foreign/stale/unadmitted/already-consumed receipt returns ECHILD. A
valid receipt whose terminal result has not yet been observed returns EAGAIN.
The caller may poll that read-only operation; it does not replay admission.

Success returns the receipt at 4, actual observed terminal detail at 8 and native
terminal kind at 12, then consumes the result once. The fixture requires its
normal child exit 29/kind 1; it does not establish all signal/fault/waitpid cases.
Kernel reclaim remains the broker's separate teardown operation. The result is
consumed before reply delivery, so a lost successful reply is unresolved and a
repeat receives ECHILD; no exactly-once delivery or result recovery is promised.

Collection ownership is independent of the parent's file alias. After close,
file operations return EBADF, while a pending child result still returns EAGAIN
or an already-collected receipt returns ECHILD. The bootstrap fields become
connection-scoped selectors here, not revived file authority. Parent-first exit
can abandon collection; the broker still performs child and reference cleanup.

The existing shared-file data/lifetime rules remain: one authoritative user-space
position, private references, denied child writes, stale references, observed
terminal cleanup and exactly one final backend close verified through EBADF.
Both child-first and parent-first closure/exit orders run two fresh generations;
all clients exit 29, backend 17 and six native reclaims are required. Test-only
ordering gates keep the `ab`/`cd`/`ef` observations deterministic.

```sh
python3 scripts/launch_smoke.py --inherited-launch \
  --libc-build /absolute/strict-musl-sdk \
  --tools-lock /absolute/compiler-tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

Nine cases:

| Case | Required result |
| --- | --- |
| positive | Parent-requested child, child-first lifetime, two rounds and six reclaims |
| parent-first | Parent closes/exits before child reads, same completed cleanup |
| rejected-launch | Actual native EINVAL, full reservation rollback, successful retry and two-round completion |
| partial-reservation | Actual second-channel EBUSY, partial rollback, retry and two-round completion |
| leaked-reservation | Omit partial reservation cleanup; parent rejects failed retry at 245, broker 970/reclaimed 0 |
| leaked-admission | Omit post-rejection endpoint cleanup; same exact retry failure |
| allow-child-write | Accept a disallowed child-rights request; parent rejects unexpected success at 243, broker 970/reclaimed 0 |
| wrong-status | Alter the observed child detail; parent rejects at 249, broker 970/reclaimed 0 |
| repeat-status | Retain an already-collected result; parent rejects duplicate success at 250, broker 970/reclaimed 0 |

The rights control detects incorrect admission policy acceptance; it does not
actually grant write access to the child or claim a successful unauthorized write.
All negative cases require exact ordered worker/broker context and designated
profile rejection. The accepted broker occupies 5288 immutable bytes within the
existing two-page bound. No code limit or loader rule was relaxed.

[Latest collection evidence](evidence/native-inherited-collect-2026-09-05/README.md)
extends the [earlier admission evidence](evidence/native-inherited-launch-2026-09-05/README.md).
This
is an Aether producer handoff. Independent userland consumption, libc FD tables,
multiple inherited entries, arbitrary executable namespaces, POSIX wait/reap,
unknown-effect recovery, shell execution and persistent installation remain open.
The tested one-entry path is concrete input to UP-01; it is not whole-story closure
or approval of the canonical shared PD proposal.
