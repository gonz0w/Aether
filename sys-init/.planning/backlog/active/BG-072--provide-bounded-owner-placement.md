---
id: BG-072
title: Obtain bounded writable placement for the filesystem init owner
status: active
created: 2026-10-22
source_type: measured-native-composition-follow-on
area: native
---

Essential BG-070 input: current ABI29 owner mapping cannot hold the selected
actual native gate2968 + RPC workspace4096 (7064 bytes) in its one4096-byte
stack page; entry usable4088. Writable code/BSS is absent, supervisor memory
allocation explicitly denies, and unused physical backing is not user authority.
Even ProcessFiles2208 plus workspace alone exceeds the page. Target layout/source
proof is retained by Decision0205; not a full linked owner or native run.

[Concrete unsent handoff](../../../docs/OWNER-PLACEMENT-HANDOFF.md): Aether kernel
owner supplies an opt-in8192-byte private zeroed RW/NX data mapping from the existing
128-page owner partition, with explicit versioned startup authority/bounds/lifetime.
Preserve old ABI29/profile/code/stack/global and owner backing limits. No general
allocator, new service, silent release/default pin or guessed pointer permission.
No sibling edit/message or implementation approval is implied.

Acceptance: separately sealed producer contract/mapping and actual permission,
zeroing/disjointness/old-profile controls, followed by exact sys-init consumption,
reviewed local initialization/ownership boundary, full measured placement/code/
stack/heap/TLS/channel fit and fresh matched Aether witnesses. Current two-page
proposal fits known7064-byte base with1128 bytes spare, not an invented complete
owner bound; finish local layout and simplify before requesting more. Reuse
workspace for transient fork buffers where safe. No userland blocker is assigned.


## Producer input received — decision0206, 2026-10-22

Aether supplies AENFS004/ownerABI30 with8192 bytes at0x900000, zeroed RW/NX,
unmapped guard pages, initial r10/r11 bounds, existing grants and owner-lifetime
contract. Exact contract13e4f5bc308a5fc24cdfb9a510cdc968da9ba66feaeb526cb23bc6db081d6d01
and all seven actual source hashes verify. Missing contract input is resolved;
producer build/geometry evidence is not native mapping qualification. Separate
entry bridge/single-slot initialization and four host tests/four compiling controls
pass. Safe backing uses MaybeUninit bytes to preserve padding validity. Full
owner composition/fit and consuming native permission/zeroing/entry/isolation/
old-profile witnesses remain open under BG-070/072. No quota/pin changes.


## 2026-10-22 construction checkpoint — decision0206

Decision0206 consumes verified AENFS004/ABI30 owner mapping and seven exact producer sources. Entry capture/MaybeUninit single-slot workspace/gate fieldwise initialization pass four new host tests/four compiling omissions and20 prior regressions, strict host/native builds. Missing mapping-contract input resolved. Native selected construction now blocks at BG-073: by-value opaque FILE broker reserves6504 bytes in size-z against4096 stack; whole opt3/isolated opt3+size-z subsets require32008/19072 code against16384. No complete-owner lower-bound theorem or native execution claimed. Need safe bounded in-place broker constructor, then full local composition/fit/fresh native witnesses.
See docs/BROKER-INITIALIZATION-HANDOFF.md; request remains local/unsent.
