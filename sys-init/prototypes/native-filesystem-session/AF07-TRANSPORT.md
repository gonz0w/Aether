# Owned AF07 client endpoint adapter

[Decision0195](../../docs/decisions/0195-af07-endpoint-adapter.md) adds the actual
ABI29 native channel adapter in af07_transport.rs/af07_native.rs. It consumes the
separate five-member userland client seal
`050aef4bede9bcaacfc6f07e590a6c1aa4b4d39cb8fc81b3bc0138daea7d367a`
and unchanged77-member service seal
`98a9fd12db4ecd1c736fe3ce332c9b69c631e043d4d87313827145675ba230a8`.
No second Owner/SPA or framing/parser copy is added. Existing lib.rs startup/child
checks and all accepted native owners/pins remain unchanged; the new adapter is a
separate crate candidate with explicit sealed dependencies.

Trusted provisioning must bind actual live distinct counterpart endpoints,
nonreused service epoch and delegated read-only rights. `Endpoints::new` checks
only nonzero/distinct shape. Rejection returns K and leaves cleanup to the caller;
it does not close unknown/aliased labels. Successful construction owns both close
obligations. Numbers/frame bytes do not establish admission, holder or authority.
The kernel enforces holder/direction/live state on every trap.

Read/write select reader/0x24001 or writer/0x24002. Wait0x24004 selects that same
endpoint and clears unused syscall arguments. The exact sealed Framed retains
short offsets, <=16-byte chunks,100000 poll bound and result-bearing EAGAIN waits.
The native wrapper borrows initialized exclusive buffers synchronously, retains
no pointer and makes no nomem/preserves_flags claim. Native build uses panic=abort;
cleanup is tested for returned scalar failures, not unwinding Kernel adapters.

Explicit close independently attempts reader and writer, caches BOTH raw results
and never retries. Drop is best effort, not confirmed closure. The real client's
partial/unknown/protocol retirement clears bindings/output and closes once without
request replay. Its `disconnect() == Ok([-9,-5])` is an acknowledged wire reply
with failed local cleanup. Require explicit Ok([0,0]) for local settlement; even
that does not prove engine terminal, export/device quiescence, EOF/EPIPE, native
reclaim, console closure or halt. Future composition must preserve those separate
conditions from the accepted AF07 lifecycle.

[Preparation evidence](../../docs/evidence/af07-endpoint-adapter-2026-10-21/README.md)
retains exact Rust1.98.0/2024 adapter and Rust2021 dependency commands, tools,
all82 pinned members, sources and outputs. Six actual Client/Framed tests cover
short/EAGAIN, both wait directions, all64 partial greeting/disconnect prefixes,
wait error/exhaustion, wrong rights/AF06 greeting, stale reply epoch, close errors,
no post-retirement I/O and independent once-only closure. Three compiling omissions
(wait direction, second close, close cache) fail their selected tests. Strict
format/default Clippy and x86-64 no_std object/disassembly pass. The emitted native
methods show fixed channel operations and zero unused arguments; neither trap
execution nor final linked-code/stack/heap fit is claimed. No new guest was run.

## Reproduction and remaining handoff

The new adapter is not imported by the existing standalone startup lib.rs.
Compile exact metadata/policy/service/client rlibs with the fs_namespace/lifetimes/
mixed/wait/bulk/runtime/activation/names/directories/metadata flags, then build
or host-test af07_transport.rs with explicit filesystem_service/filesystem_client
extern paths. Exact reproducible argv and frozen source copies are in preparation.json;
preparation-driver.txt is inert evidence, not an automatic sibling build command.
Use a new owned output root; verify pins before copying/compiling dependencies.
The Rust-adjacent DYLD_LIBRARY_PATH is scoped to Rust tools only.

Next userland must connect transport-backed shared FD/path/binding messages and
immutable executable authorization to this client. The earlier local descriptor
core still owns a dedicated Owner and cannot be grafted onto it. Require exact
process/instance/description generations and rights, partial/error/unknown/final-
close outcomes and failed-exec parent/FD preservation; readonly open/cached size
or a digest alone cannot authorize immutable execution. The request is local/unsent.
Sys-init then integrates its full dispatcher, startup/FD/copy/exec/wait/endpoint
transport and engine shutdown, supplies fit and obtains fresh Aether command/
error/cleanup/readback witnesses. Existing profiles, limits, released pins and
sibling files remain fixed. No RAM-backed shell substitute or shared SDK promotion.

## Subsequent shared-description compatibility

The new ten-member combined remote-description input is now verified and composes
with this unchanged endpoint adapter in [two host tests](../../docs/evidence/af07-remote-adapter-2026-10-21/README.md):
shared offsets/final-close and all64 partial-body retirements over scripted native
replies. It creates no Owner/SPA. This supersedes the missing transport-backed
shared-description algorithm above, but not the remaining authenticated process/
FD/binding/path messages, cross-process/fork lifetime and immutable executable/
failed-exec contract. The old native-client preparation stays fixed; this newer
Client::abort/remote composition is host-only and needs fresh native preparation/
fit with the final dispatcher. Do not confuse local dup aliases with fork sharing.

The remaining bridge contract must also name placement and workspace ownership.
A connection greeting is consumed once: do not run Client::connect after the old
activation path has already received it, or import unknown existing handles into
the fresh-connect remote table. Specify who retains/delegates the endpoints and
how readiness is observed without a second greeting/Owner. Its4096-byte read
output plus tables/call frames cannot simply be assumed to fit init's4088 usable
stack. Choose bounded caller-owned workspace in the intended domain and supply
concrete linked stack/heap/backing evidence; no owner-stack/quota expansion is
approved by this host interoperability result.

Decision0211 adds scalar `Native::cancel_freeze(source, token)`:0x23005 with
rdi=actual owned source/rsi=observed token and all remaining operands zero. The
supervisor receives raw0 on success; parent-11 is a distinct kernel-set result.
The explicit gate native-result method accepts only0 and preserves actual raw
results. No new pointer/asm option/authority or automatic reconciliation follows;
see [current fork contract](FORK.md) and the decision0211 review.
