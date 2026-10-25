# Bounded writable owner placement — BG-072

**Current status — decision0206:** Aether supplied the exact AENFS004/ABI30
mapping contract and all seven source hashes verify. The missing input below is
resolved; new entry/region/fieldwise gate helpers pass host/build checks. Native
mapping acceptance and full owner fit remain open. Continued construction exposes
[BG-073's separate opaque broker constructor seam](BROKER-INITIALIZATION-HANDOFF.md).
The original request and evidence below are retained as history.


2026-10-22. Local unsent handoff to the Aether kernel owner. No sibling repository
was changed and no message was sent. Sys-init owns composition and actual use;
Aether owns mapping, initial authority and its opt-in profile contract. Userland
has supplied FILE metadata and corrected real TLS; no new userland runtime input
is requested by this handoff.

## Concrete requirement

Provide an opt-in **8192-byte private, initially zeroed RW/NX data region** for the
filesystem init owner, drawn from its existing128-page backing partition. Preserve
the old ABI29 profile, image bytes,16KiB code bound,4KiB stack and global/per-owner
backing quotas. This is a proposed mapping/authority contract, not an allocated
ABI, selected address or permission to change limits. Kernel owner chooses the
versioned mechanism and exact trusted startup binding; a numeric pointer alone is
not proof of mapping or authority. No general supervisor allocator is requested.

Two data pages hold the measured2968-byte concrete gate plus4096-byte RPC workspace
(7064 bytes), leaving1128 bytes for bounded metadata. This is a concrete initial
placement request, not proof that all remaining peer bookkeeping will fit. Sys-init
must reuse the RPC workspace for transient fork buffers where lifetimes permit,
finish the complete layout and prove all data/code/call-frame bounds before native
acceptance. If the bounded region is insufficient, first simplify/measure locally;
no automatic larger region or quota increase follows.

## Evidence for the block

[Decision0205](decisions/0205-gated-fork-capture-and-placement.md),
[exact target layout and source excerpts](evidence/gated-fork-capture-2026-10-22/placement.json).
Pinned Rust1.98 x86_64-unknown-none LLVM output, concrete native Framed/Endpoints:

| Resident object | Bytes |
| --- | ---: |
| ProcessFiles with actual native channel type | 2208 |
| Owned two-pipe/console State | 736 |
| Complete gate including those objects | 2968 |
| Existing required RPC workspace | 4096 |
| Parsed Plan (transient) | 216 |
| Two fork buffers (transient, can reuse workspace) | 608 |

The gate plus workspace requires7064 bytes. Even ProcessFiles plus its workspace
alone requires6304 bytes. Current owner has one mapped4096-byte stack page and
entry RSP0x801000-8 (4088 bytes below entry); the mapped code pages are RO/executable.
The raw owner linker rejects writable .data/.bss, consistent with the kernel
mapping. Actual memoryOperation rejects supervisor mapping even if a numeric
capability is supplied. A16KiB code allowance therefore does not provide writable
placement. This is a static typed-layout and actual-policy proof of an unavailable
placement, not a measured complete executable/call-stack estimate or native run.

Sources: current Aether kernel/arch/x86_64/native_c.zig startSupervised and
memoryOperation, native_fs_roles.zig pages(owner6)=128 and backing_pool.zig
filesystemSession; local native-filesystem-af07/owner.ld; actual fd_dispatch
serve_one workspace signature/clearing. Exact whole-file hashes and excerpts are
retained. The backing-pool alias is kernel-only: root/table entries omit the user bit,
and its address is in the higher half. Do not assume unused physical backing
or a writable kernel alias is already a user mapping/grant.

## Alternatives checked

The4096-byte fixed array is part of the selected library/dispatcher contract, not
an arbitrary local read request. Smaller transfers do not shrink that array.
A kernel stack adjustment, writable code/BSS, guessed arena capability, borrowing
another process's backing or a second filesystem owner would change obligations
or violate existing authority. Moving/reconstructing private file/holder state
from client assertions would lose the single authoritative ledger. None is used.
A separately versioned userland API reducing resident workspace could be a future
alternative, but it is not a second simultaneous dependency/request here.

## Matching delivery and acceptance

Aether should provide a separately sealed opt-in contract and actual mapping code:
region bounds/alignment, zeroing, private RW/NX permissions, lifetime/ownership,
startup identification and failure/cleanup. Preserve old selected input bytes and
all existing limits; show it uses the existing owner partition without aliasing
engine/process/code/stack pages or granting additional allocation. Include actual
kernel mapping/permission/old-profile denial/zeroing controls and reproducible pins.
Do not silently give the old profile writable globals.

Sys-init then consumes that exact contract, adds the smallest reviewed placement
boundary, assembles the actual owner with one FS service and stable source state,
measures complete data/code/stack/TLS/backing/channel peak fit and obtains fresh
matched Aether copy/refusal/unknown/greeting/ready/parent/wait/cleanup/readback
witnesses. This owner-placement gate blocks full native composition; the earlier
FILE, stream and TLS input blockers are resolved. No release or native acceptance
is implied by either this request or passing component host tests.
