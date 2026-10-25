# UL-007/081/082 AF07 read-only client change review

Pre-code plan,2026-10-21. Current sys-init decision0194 consumes corrected ABI29
v2 and implements startup/child/wait policy, not full dispatcher. Its next input
is userland filesystem translation. Implement the transport-facing read-only
client against the sealed77-member AF07 service, not a second live Owner/SPA.
No sibling changes, native campaign, SDK/pin promotion or old evidence mutation.

Foundations O-01–05/I-01/03–06/E-01–08, Distribution PX and CR/TD/SE apply.
Trusted caller supplies retained authenticated Channel endpoints, nonreused epoch
and delegated read-only rights. Wire IDs and paths confer no native authority.
Use existing Channel/Framed (64-byte frames,16-byte transfers, wait/error bounds),
AFSRPC07 magic, lookup1/read2/close3/disconnect4/stat6 and padded name/data bodies.
No new opcodes, mutable rights, service policy or user-facing output changes.
One serialized allocation-free client,16 retained tokens including root,1–255-byte
single components and4096-byte reads with signed64 request bounds. Private handles
include epoch; local membership and delegated rights checked before transfer.
Root remains until disconnect; tokens never reused. Zero reads are local after
handle/right/range validation because AF07 rejects zero-length wire requests.

Validate greeting, all response/reserved/status/epoch/token/count/body fields.
Read reply count may be0..requested; server owns coherent up-to-EOF semantics.
Known canonical negative errno retains connection, except conservative fatal EIO/
EBADF. Invalid frames, stale epoch, partial/failed send/receive or uncertain
completion retire once, discard all tokens, close both local endpoints once and
never replay. Full/failed read outputs remain zero. Retain both close outcomes;
endpoint close is not service disconnect, engine export or native reclaim proof.
Drop closes local endpoints only; explicit disconnect requires full success reply.
No clocks, writes, metadata/POSIX stat, FD/fork sharing, path traversal policy,
immutable executable authorization or loader. Existing owner-local descriptors
remain separate until reviewed transport-backed integration.

Pin dependency seal and Rust1.98/native libraries/helper before compiling. Host
interoperability executes actual sealed service/Owner with synthetic storage and
bounded in-memory channels. Scripted malformed replies and short-transfer framing
exercise no replay, zeroing, stale handle/token/capacity/rights and cleanup errors.
Compile semantic omissions and require assertion failures. Rust2021 no_std,
-Funsafe-code, warnings denial/default Clippy/rustfmt; native generic rlib only,
not executed monomorphized code or fit. Actual minimum/current Python drivers;
compile60s/test30s,16MiB streams, clean env/build-only roots, no network. Retain
failed attempts and read back compact retention before build cleanup. Quality,
syntax and whitespace required before completion; independent review pending.

Simplicity: use existing sealed Channel/Framed and synchronous request/reply
instead of a second service, async framework or generic RPC. A raw frame builder
alone cannot retain validated handles or prevent continued use after unknown I/O;
fixed arrays and consuming failure state are needed. Remove nothing now because
accepted legacy wires/evidence remain immutable. No performance/security/native
conformance claim follows from safe Rust or host passes. Next FD/path/immutable
image translation and matching sys-init/native qualification remain incomplete.

Final technical source review by implementation agent: local private-handle
membership, attenuated read-only rights, capacity-before-lookup, nonreused
server token sequence, operation-specific reserved fields and checked read
framing are enforced. Whole read outputs clear before validation and again on
partial-body failure. Failed final close, malformed/unknown I/O and conservative
EIO/EBADF retire once; Drop never retransmits or retries close. Both close
results remain observable, including failed acknowledged-disconnect cleanup.
No raw handle/size/readonly claim authorizes immutable exec. No separate Owner
or SPA context is constructed by client code. Independent affected-owner/reader
review remains pending; no native integration acceptance follows.

Eleven tests/eight compiling semantic omissions pass on both Python versions;
format/default Clippy/warnings/unsafe denial, identical native generic rlib and
minimum/current Python syntax pass. Repository quality/pin/inventory checks and
tracked whitespace pass. Failed fixture EOF count and strict mutation-oracle
assertion evidence are retained. Four exact owned roots were archived and each
file read back/hash/size verified before removal:58640463 logical bytes removed,
19924687 archive bytes retained. Physical disk reclamation was not measured.
Existing build dependencies and historical/sibling evidence remain untouched.
