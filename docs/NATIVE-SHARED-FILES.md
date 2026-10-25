# Shared open-file bootstrap witness

A separate opt-in [file-I/O mode](NATIVE-FILE-IO.md) adds ordinary bounded reads,
EOF and writable-parent behavior; this profile retains its existing semantics.

This opt-in user-space fixture uses the existing AENMX001 / ABI 9 kernel profile.
It changes no native syscall, kernel state, quota or bootstrap registers. The
producer mode is `shared-files`, distinct from `connections` despite the same
kernel envelope and completion marker. It is the next bounded UP-01 experiment,
not general POSIX descriptor inheritance or the full shared PD proposal.

## Ownership and protocol

The Rust conformance broker opens one volatile scratch backend handle with read
and write rights and seeds it with `abcdef`. It alone retains the handle and the
shared position. Two separate loaded clients receive fixed bootstrap aliases:
parent-like slot 0 at descriptor index 3, and child-like slot 2 at index 10. These
labels describe this test; the native loader does not establish POSIX parenting.
The child alias is read-only. One live bit per connection accounts for these two
references; there is no general FD table, dynamic inheritance list or alias API.

Each existing private request/reply connection supplies caller identity. No
request field may select a different caller. Internal reference values combine a
connection-specific family (`0x61000000` or `0x62000000`) and the round generation.
The broker checks that reference, its bound descriptor index and live state before
file effects. A client cannot use the peer's reference, an old generation, index
16 or the raw backend root as authority. Kernel endpoint ownership remains the
underlying connection boundary. Numeric values alone do not grant access.

The fixed 32-byte bootstrap response contains u32 status 0, reference, descriptor
index and rights, followed by zeros. Parent rights are 3, child rights 1. This is
explicit supervisor-provided delegation at bootstrap, not a parent-issued spawn
request. Both clients and their channels are admitted before bindings are sent.
Failed inheritance-list admission/rollback and lost admission replies are not
implemented here; the earlier host oracle is separate evidence for those rules.

Requests are 32 bytes: u32 operation, reference, descriptor index, count, then 16
payload bytes. Read operation 1 accepts count 2 and zero payload. Close operation
3 accepts count 0 and zero payload. Write operation 2 rejects the read-only child
with EACCES before backend effects; the parent write path remains ENOTSUP. The
parent's broader underlying rights do not imply that all write calls exist in
this fixture. Unknown operations/malformed supported requests return EINVAL;
foreign, stale, closed or wrong-index references return EBADF. No raw backend
passthrough exists. Replies use signed u32 result at offset 0 and read bytes at
16; backend handles are never published to clients.

## Shared position and lifetime

The broker reads the backend at its owned position and advances only after a
positive read result. No client submits an arbitrary offset. Test-only scheduling
returns EAGAIN until the selected peer operation or terminal observation has
occurred, making the lifetime ordering explicit rather than relying on timing.

- Child-first: parent reads `ab`, child reads `cd` and exits without close; the
  broker observes terminal state and removes its reference. Parent then reads
  `ef`, closes, verifies repeated close/read rejection and exits.
- Parent-first: parent reads `ab`, closes and exits; only after observed parent
  exit does the child read `cd` then `ef` and exit without close.

Terminal observation precedes servicing that client's buffered requests. Explicit
close removes one reference; observed exit removes it only if still live. When
both references are gone, the broker sends one consuming backend close and checks
success. A subsequent backend read through the old handle must return EBADF,
proving actual closure rather than only local bookkeeping. Surviving alias reads
prove the backend stayed open before that point. Both orders run two fresh rounds,
with clients exiting 29, backend 17 and six total native reclaims.

The broker is trusted for file contents, alias policy, offsets and cleanup. It
still uses bounded synchronous backend/reply transfer and aborts on unexpected
transport or client failure. This fixture does not implement poisoned-owner
recovery, uncertain-close reconciliation, arbitrary scheduling fairness or
supervisor recovery. No native shared writable mapping or global file table is
introduced. Userland retains ownership of the eventual POSIX implementation;
sys-init service policy and pkg-mgr artifact transport stay separate.

## Reproduction and controls

```sh
python3 scripts/launch_smoke.py --shared-files \
  --libc-build /absolute/strict-musl-sdk \
  --tools-lock /absolute/compiler-tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

Six native cases pass:

| Case | Required outcome |
| --- | --- |
| positive | Child-first ordering 2/0/1 in both generations; six reclaims and CONNECTIONS PASS |
| parent-first | Parent-first ordering 0/2/1 in both generations; same cleanup completion |
| frozen-offset | Omit position advancement; parent exits 239, broker 970/reclaimed 0 |
| early-close | Close the backend on the child's reference removal; surviving parent read rejects at 239, broker 970/reclaimed 0 |
| wide-rights | Omit the child's read-only guard, returning unsupported instead of denied; child rejects at 237, broker 970/reclaimed 0 |
| leak-close | Omit final backend close; stale-handle probe rejects at broker 975/reclaimed 0 |

The rights control detects a missing denial branch, not successful unauthorized
storage mutation. Each negative case requires exact ordered execution context and
the designated profile rejection; unrelated panics and watchdogs cannot pass.
The first early-close control exposed an ambiguous fixture ordering; gating the
parent's second read on observed child exit made the intended failure deterministic.
The accepted broker is 3968 immutable bytes, within the existing profile limit.

[Retained evidence](evidence/native-shared-files-2026-09-05/README.md) includes
sources, tool/input pins, raw supervisors, ELF helpers and target logs. Existing
connections, program, coexistence and writable-file profiles are fresh regressions.
The kernel is unchanged, so earlier memory/SMP evidence is not presented as a
new run. No independent userland adoption, shared owner sign-off, libc interposition,
fork/exec, native shell or persistent installation follows from this fixture.
