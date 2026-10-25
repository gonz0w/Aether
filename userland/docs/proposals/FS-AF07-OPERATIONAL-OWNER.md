# Separate AF07 operational owner — UL-082, 2026-10-21

Aether's AF07 positive/inherited transport/context/metadata-loss/four-provider
gates now pass for the exact77-member dependency. The approved provider batch is
consumed; its prior retirement timeout remains unexplained. This handoff supplies
the next separately selected Rust owner. It does not authorize another guest,
change AF06 defaults, or constitute operational/native/sys-init acceptance.

## Exact consuming input

Use `experiments/filesystem-service/launch-metadata-owner.rs` and its sealed native
object from `build/service-deliveries/filesystem-af07-owner-2026-10-21-v1`.
Read SHA256SUMS/build.json/inputs.json for exact source/tool/flag/object identities.
The owner exports `main` and `aether_fs_launch_serve`, imports
`aether_fs_engine_run`, `getauxval` and **aether_fs_metadata_run**. It cannot be
linked with the old owner: both main/callback definitions intentionally conflict.
An old AF06 service definition cannot resolve the new metadata import.

The only service dependency is the existing
`build/service-deliveries/filesystem-service-metadata-2026-10-21-v1`:
77 members, seal98a9fd12db4ecd1c736fe3ce332c9b69c631e043d4d87313827145675ba230a8,
objectb5729862346409392064045af6f953484d3d6fbf9cad2b279840907003222f7b.
Keep the old67-member AF06 service, AF06 launch-owner.rs and active30-member
executable selected until a separately qualified replacement is ready. The new
packet references the verified service dependency; it does not duplicate its
engine/SDK or claim an independent/hermetic standalone build.

The actual executable is still missing. This owner object is relocatable code,
not an ELF process image. Aether's current fs_launch.py admits only the old AF06
preparation and fixes its source/service/partial-link origins. Implement a separate
explicit AF07 composition/intake there; do not feed this packet through AF06
guards or patch a running/old ELF. No C engine/init implementation is duplicated
here, and no sibling source changes/messages were made.

## Provisioning, protocol and lifecycle

Use the original nine-argument AF07 entry, AFSRPC07, explicit METADATA16/root
rights31, fixed immutable dataset`testpool_zstd/x86_64` and trusted uid/gid1000.
Labels/metadata/paths confer no authority. Native holders, endpoint directions
and generations remain enforced by the kernel. Inherit request-reader/reply-writer
from the existing auxv keys0xa004/0xa005; use existing block grant0xf101. No new
grant, discovery, ownership transfer, network or client-ID authority is introduced.

The process-local LaunchState remains136 bytes, service result72 at offset48,
engine error40 and startup close results120/128, all alignment8. It is not the
different136-byte metadata record or a client RPC. The trusted engine retains
the sole live exclusive SPA/state/code through the synchronous callback and all
original ordered drain/export/helper/block/UTC/runtime teardown. No reentry,
external mutation/properties/export or pointer retention may overlap the callback.
The new owner uses the original callback and phase ABI, not a new engine protocol.

Before service acquisition, malformed bootstrap/startup failure attempts each
nonzero inherited endpoint once, with duplicate-token suppression. After an
entered service or any observed service report, the owner cannot reacquire endpoint
ownership merely because final phase evidence is contradictory. Missing/unknown
phases still fail; such a result cannot imply stop/reclamation or permit replay.
The sole original service consumes context/endpoints before returning. These
actions are distinct from native supervisor terminal/stop/quiescence/reclaim.

Zero exit requires exact version1/extent136/all13 completion bits8191, no engine
error, real ready1, at least one request, clean disconnect, no service error and
both successful endpoint closes. Known no-transaction history requires state0/
TXG0/staged0; successful transaction history requires state2/nonzero TXG/staged<=4096
(namespace success may stage0). Unknown/committed/impossible clean progress is
failure, never durability. Read-only and many-request sessions remain valid;
there is no success conversion tied to finite conformance work counts. Preserve
real engine error1..255; other nonzero values become failure5, never success.
Readiness generation/identity must still be observed live by the consuming owner.

## Required Aether and sys-init gate

Link this Rust owner and the exact77-member AF07 object with the original
metadata-capable C provider/engine/runtime/UTC/core/CRT closure, preserving engine
code residency and each initialized/exclusive borrow. `zpl-metadata.c` replaces
the old directory/mutation/write/read provider; never duplicate those definitions.
Verify actual main/callback/service/getter/import/startup origins, no retained
old service/owner, unresolved imports or runtime relocations, and exact executable
bytes before admitting the image. Native object/C ABI controls here do not prove
whole-stack, image/page/segment/TLS/W^X, memory/quiescence or resource fit.

Retain existing native watchdogs/authority/code/backing/workers/channels/I/O/poll/
observation/cleanup bounds. No reused120s idle allowance, extra guest, larger
SESSION lifetime or reset/replay is inferred from this handoff. Any operational
native campaign needs its own exact owner-scoped input/workload/disposition.

Qualify real inherited provisioning, root/UTC readiness and AF07 client greeting/
metadata with explicit authority, then clean disconnect/export and separate fresh
recovery. Denied bootstrap, wrong/stale readiness, lost header/body/EOF/close,
provider/engine failures must never admit dependent work, fabricate cleanup or
restart/replay an unknown write. Preserve complete compact oracle capture and
current independent full-file/metadata/namespace/media/guard/drain/reclaim checks.
Sys-init then consumes the exact executable/provisioning/readiness/shutdown input;
its existing AF06 peer cannot silently become AF07. No sys-init policy is added here.

This input does not complete UL-082/M3/R1, independent owner/reader review,
ordinary mode/cross-directory promotion, filesystem-backed loader/runner/packages,
ABI29 shell/PID/FD integration or the requested persistent Zsh/TTY ISO.
