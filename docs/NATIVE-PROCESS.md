# Connection-bound launch broker experiment v1

Aether-owned Rust conformance fixture over unchanged AENFS001 / ABI 5. This is
producer evidence for a process-service boundary, not selection of a production
POSIX server or adoption of the canonical PD-01–12 draft. Userland retains POSIX
process/FD policy and sys-init retains service policy. No kernel or shared ABI
changes. The broker occupies the existing supervisor domain and is trusted for
the factory/image grants it holds.

## Connection and namespace authority

The broker launches exactly one requester in slot 0, transferring a request
writer and response reader atomically through 0x23002. It retains their peers.
Only that requester owns the request writer. The broker associates that connection
with a namespace containing only `worker`, bound to its second immutable executable
grant. Request bytes contain no caller identity or native capability to trust.
Guessing an executable, endpoint or worker handle cannot bypass kernel owner
checks. There is no multi-client routing, reconnection, reverse grant transfer,
namespace mutation or fallback to the broker's wider authority.

One requested child occupies slot 1 at a time; live and terminal-uncollected
children both retain the slot. The connection's ticket identifies that child in
broker policy, not native authority. Two child generations suffice for this
witness; native slot quotas remain authoritative. Client death/EOF closes admission:
the broker stops and reclaims any remaining child, closes the connection and
reclaims the requester before reporting an incomplete workload. Partial frames
are failures. Supervisor death retains ABI 5's fatal limitation; this is not the
separate ABI 6 fail-closed profile or a recovery service.

## Fixed frame protocol

Each request/reply is exactly 32 little-endian bytes, accumulated across bounded
native short transfers. One outstanding request, no pipelining/replay IDs.
Request: operation u32, ticket u32, inheritance mask u32, version u32 (=1),
then name[16]. Reply: signed result i32, ticket u32, terminal detail u32,
terminal kind u32, then sixteen zero bytes. Failure replies zero other fields.

- Operation 1 launches a new child. Ticket must be zero; name must contain a NUL
  followed only by zeros and obey NATIVE-LOOKUP's relative-name rules. Lookup is
  restricted to this connection's namespace. Missing executable returns ENOENT;
  malformed fields EINVAL; occupied child record EBUSY. Resolve and validate all
  inputs before invoking the kernel; failed requests publish no ticket/child.
- The only supported inheritance mask is zero. Every nonzero value returns
  ENOTSUP(95), before admission; there is no successful silent dropping of required
  descriptors. The child receives no channel endpoints, factory or executable
  grants. This is explicit **empty inheritance**, not FD copying, CLOEXEC or shared
  offset support. Future inheritance must integrate userland's descriptor owner.
- Operation 2 collects the connection-owned ticket. Mask/name must be zero.
  Unknown, stale or native-handle-shaped tickets return ECHILD(10). The bounded
  broker observes/yields until terminal, copies detail/kind, reclaims the native
  child and consumes its ticket exactly once. This is a synchronous experimental
  collection request, not POSIX waitpid/WNOHANG, SIGCHLD or general scheduling.
- Unsupported operations return ENOSYS(38); unsupported version returns EINVAL.

A lost launch reply has unknown launch outcome; a lost collection reply may have
consumed the result. No retry-safe mutation or status recovery is promised. A
failed reply terminates this experiment after owned cleanup. The trusted fixture
uses watchdogs only as failure bounds, never as service completion evidence.

## Reproduce and interpret the evidence

```sh
python3 scripts/launch_smoke.py --process \
  --libc-build /absolute/strict-musl-sdk \
  --tools-lock /absolute/compiler-tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

The runner builds the C requester/worker from the pinned strict-musl SDK and a
separate Rust broker with fat LTO and one codegen unit. The existing linker still
requires an immutable code image of at most 4096 bytes and no writable statics.
The positive broker is 2888 bytes in this capture; size is not a performance or
production memory-footprint claim. Broker state lives on its private stack.

Six target cases use the existing `AETHER NATIVE FILE SERVICE PASS` envelope
completion marker and an explicit `process` report profile:

| Case | Required outcome |
| --- | --- |
| positive | worker slot 1 generations 1/2 exit 17/33, requester exits 29, three reclaims and profile completion |
| allow-inheritance | requester rejects silently accepted inheritance at 202; broker reports 903 after two reclaims |
| wide-scope | requester rejects lookup outside its connection namespace at 203; broker reports 903 after two reclaims |
| repeat-collect | requester rejects a second successful collection at 207; broker reports 903 after two reclaims |
| partial-request | four bytes followed by requester exit 41; incomplete-workload result 903 after one reclaim |
| requester-exit | exit 42 with a child still owned by the broker; result 903 after both reclaims |

A controlled panic after cleanup is an unsuccessful conformance workload, not
successful recovery or a production error-reporting service. Exact client results
and reclaim counts are necessary negative-oracle context; an unrelated panic,
watchdog or compile failure cannot pass. Positive tests additionally cover denied
raw requester launch, unknown operation/version, invalid/missing name, occupied
records, guessed/native-shaped/stale tickets and forbidden child channel use.

The existing per-domain legacy diagnostic output transport remains available;
empty inheritance specifically means no requested descriptor table or transferred
channel endpoints. Requester EOF must be followed by its cooperative exit in
this fixture. A requester that closes its writer and never exits is not covered
by a graceful teardown guarantee; the bounded terminal watchdog fails instead.
There is no general orphan policy or independent recovery owner.

This experiment does not run concurrently with the two-channel file service or
share userland open-file offsets. Supporting inherited files requires a concrete
userland process/descriptor-owner integration and reviewed channel/reference and
resource limits. It cannot be obtained by sending numeric FD or endpoint values
in this protocol. No fork, in-place exec, signals or native shell is established.
