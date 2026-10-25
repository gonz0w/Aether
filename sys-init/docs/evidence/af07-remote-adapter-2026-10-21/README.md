# AF07 remote-description/endpoint interoperability — 2026-10-21

The ten-member combined userland source delivery arrived during decision0195
preparation. review.json verifies seal
`21639ae14bde1f1e82cdc9c8c6af683a256a238403c517bd8e5c66acf6919a95`
and all ten members before/after use. It contains shared description logic,
local/remote adapters and the additive Client::abort implementation. Original
five-member client/descriptor and77-member service releases remain immutable.
No native/default/SDK pin is replaced; this is a separate host composition.

Two direct host tests compose the actual remote-description table, updated client,
sealed Framed and unchanged sys-init owned-endpoint adapter with scripted kernel
replies. Real generated wire requests verify lookup/read explicit shared offsets,
no close for a nonfinal alias, exactly one final close, clean wire disconnect with
both raw local close failures preserved. Every64 partial read-body prefix retires
once, clears a deliberately dirty4096-byte output, performs no wire replay or
post-retirement I/O and closes both endpoints once. Strict Rust/default Clippy/
format pass. Existing service rlib byte hashes are recorded before/after reuse;
exact prior build commands/sources/tools are in the
[endpoint packet](../af07-endpoint-adapter-2026-10-21/README.md).

This is actual-library host compatibility over a scripted kernel double. No
OpenZFS/server/Owner/native IPC or process/fork/path/exec behavior runs here.
Producer's12 client/12 local/eight remote host suites and omissions retain their
own evidence scope; they are not repeated or relabeled as this test. No native
stack/heap/authority/fit claim. Host source/commands/results and raw library pins
are in review.json; host-tests.rs.txt freezes the new test. The native endpoint
adapter itself and its already sealed70-member preparation stay unchanged.

The dedicated local Owner restriction is no longer the only route: the new remote
adapter creates no Owner/SPA and can consume our endpoint adapter. Remaining
blocking input is authenticated process/FD/binding/path messages, cross-process/
fork lifetime and immutable executable/failed-exec contract. Sys-init still owes
full transport/engine shutdown/fit, then Aether native consuming witnesses.
Guide/handoff: ../../../prototypes/native-filesystem-session/AF07-TRANSPORT.md.
Request remains local/unsent. No sibling change/message or guest.

local-checks.json records final full local checks; sha256.json seals this packet
except itself. Sources: remote-contract.md (exact sealed producer contract),
remote-manifest.txt and pinned delivery path in review.json. Existing runtime,
standards/default pins and historical evidence are unchanged.
