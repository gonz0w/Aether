# Process and file transport coexistence v1

AENCO001 / ABI 7 is a separate BSP experiment using the existing two-ELF launch
envelope. It supplies four 32-byte channels (identities 0–3), two worker slots and
the existing supervisor bootstrap grants. No extra task, executable or memory
quota is introduced. Existing channel/file/init profiles retain one/two channels,
ABIs and markers. Exact kernel operations and endpoint transfer are unchanged.

Four channels are needed now: the requester/broker pair plus the broker/file-service
pair. Creation searches the profile's pool in identity order, returning the first
free nonretired channel; EBUSY if none is available but some end is still owned,
ENOSPC if all channels are retired. Each identity allows three generations, no
wrap. Holder checks include identity and generation. Failed paired launch keeps
both endpoints with the broker; its rollback closes all newly allocated ends.
Worker termination closes all its ends across the whole active pool; completion
requires no owned endpoints or residual bytes in any active channel.

The Aether Rust broker is a conformance fixture, not a selected production POSIX
server. It routes one caller's file requests through an explicitly owned backend
connection. It does not copy userland's descriptor implementation. Userland owns
FD tables, shared offsets and libc adoption. The canonical process/FD proposal
remains unreleased and owner review is pending. Shared inherited descriptors,
fork/exec, a general namespace service, native dash and persistence are not supplied.

## Broker protocol extension

Use NATIVE-PROCESS v1 framing, restricted worker namespace and empty requested
inheritance. The worker is now the Rust writable-file service. Broker-assigned
service channels are explicit service dependencies, not inherited requester FDs.
The requester never owns backend endpoints. On launch, the broker receives the
service greeting before replying; success reply fields 8/12 carry its read/write
root handles. Their scope is the newly returned broker ticket plus connection.

Operation 3 has the ordinary 32-byte request header followed by exactly one
32-byte NATIVE-FILES request body. Every op-3 header consumes a body, including
invalid-version/header/ticket requests, so rejected frames cannot desynchronize
later requests. Inherit/name fields must be zero. The broker validates the live
owned ticket before forwarding; stale/foreign tickets return ECHILD without
backend effects. A valid reply is the exact 32-byte file-service reply.
Only one request is outstanding. Lost/malformed replies remain unknown outcomes,
not retry-safe mutations. Root/file numbers alone never select a backend.

Collect closes the broker's backend request writer, observes the service's EOF
exit, closes its response reader and reclaims the child before consuming its ticket.
Requester failure closes backend endpoints and stops/reclaims any remaining child.
A subsequent service generation gets fresh channels and empty scratch; old
(ticket, file-handle) tuples cannot route to it. Numeric file handles may repeat
across independent service connections and are not global capabilities.

The separate completion marker is `AETHER NATIVE COEXIST PASS`. Supervisor death
retains the fatal ABI-5-style outcome; ABI 6 fail-closed shutdown and its clock/wait
API are not implicitly included. Four local channels imply no SMP support.

## Reproduction and witness

```sh
python3 scripts/launch_smoke.py --coexist \
  --libc-build /absolute/strict-musl-sdk \
  --tools-lock /absolute/compiler-tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

The runner builds the existing Rust file service with writable scratch enabled,
a C requester/service-entry bridge, and the Rust broker with size optimization,
fat LTO and one codegen unit. The immutable one-page/no-writable-statics linker
bound remains enforced; the broker is 3944 bytes in this capture. This is not a
production footprint or throughput measurement.

The positive case keeps both connection pairs live, verifies fifth-channel EBUSY,
checks invalid paired-launch ownership preservation on the backend identities,
and rejects old-holder/foreign endpoint use. The requester reads exact seed bytes,
creates/writes/reads scratch, closes its records, collects the service and repeats
with a new ticket/channel generation. The old ticket is denied and scratch is
absent in the replacement. Both service generations exit 17, requester exits 29,
and the kernel verifies three reclaims and all four channels closed/zeroed.

Designated controls: repeated collection (requester 207 / broker 903 after two
reclaims); partial request (41 / 903 after one reclaim); requester exit with an
owned backend (42 / 903 after two reclaims); a deliberately two-channel kernel
pool (204 / 903 after one reclaim); corrupt file-read data (223 / 903 after two
reclaims). Those unsuccessful workloads require exact contexts; generic timeout,
unrelated panic or build failure is not acceptance. Host tests additionally check
all four identities' independent holder bindings, buffered drain and stale reuse.

The protocol is single-connection, single-request and volatile. No native file
FD facade is imported from a mutable sibling checkout. Existing NATIVE-PROCESS
failure/EOF limits apply. Full requester/proxy/service failure recovery and
reconciling lost mutation replies remain unsupported. A native shell will also
need capacity for an independently executing program beside its file backend,
and an accepted inherited-file/reference ownership contract; this slice proves
transport coexistence only.
