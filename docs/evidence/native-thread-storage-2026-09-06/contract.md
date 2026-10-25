 — 2026-09-06

Before implementation: actual musl pthread_create passes separate parent-TID and
clear-TID locations to clone, and allocates TLS/TSD outside the active stack.
Provide these kernel storage semantics under the existing thread grant, without
implementing libc policy or pretending signal/cancellation support exists.
Aether owns validation and lifetime pins; userland owns TLS construction and libc
adaptation. This is an experimental AENATC01/AENSUP01 extension, not owner acceptance.

Opcode 0x28006 uses the same registers as descriptor creation 0x28005 but copies
96 bytes: version=1, size=96, the seven existing u64 fields, then tls_base,
tls_bytes, parent_tid, reserved=0. Stack rules remain unchanged. TLS is a nonempty
page-aligned range wholly in the anonymous arena, with every page already RW/NX;
FS must lie inside it. Stack and TLS may overlap. Parent-TID and clear-TID must
both be nonzero aligned writable four-byte locations. Validate everything before
any writes. Copying the full descriptor permits descriptor/output aliasing.

On success write zero to the supplied return slot, then write the child ID to
parent_tid, and publish the child. Do not initialize clear_tid; it is independently
cleared and wakes matching waiters on exit/stop. If outputs alias, that documented
write order applies. Parent-TID is a one-time output, not a lifetime pin. Clear-TID
and the full TLS/stack ranges remain pinned until child execution stops. This adds
no backing allocation, capability, quota or child-slot reuse.

For this creation mode the ID is slot+3 (3 or 4); the main context retains slot+1.
These are bounded live-context labels, reused after domain replacement, never
authority or stable process identifiers. Opcode 0x28007 with the thread grant and
all other arguments zero returns the current context ID: main slot+1, new child
slot+3, legacy child 1. Legacy creation/TID effects remain unchanged. Existing
set_tid_address on the new child returns its ID and may replace its clear word;
set-FS may move only within the declared TLS span. Other profiles retain behavior.

Creation errors follow 0x28005: -13 authority/caller, -28 consumed child budget,
-22 malformed descriptor/reserved/geometry/alignment/FS outside TLS, -14 unreadable
descriptor or invalid backing/entry/TID. Identity query rejects reserved fields
with -22 and foreign grants with -13. Out-of-span set-FS returns -22 without change.
All copying, validation, writes and publication occur under the existing BSP IF=0
gate; no user pointer escapes validation into scheduler code. Full-span pins are
also enforced while blocked; stop clears registrations before reclaim/replacement.

Select native positive/supervised/alias/stop/fault cases in both memory profiles,
full TLS pins (including pages on either side of FS), separate TID values and
exit clearing, identity, invalid late parent-TID and TLS backing with unchanged
sentinels, FS escape denial and parent-output unmapping. A deliberate pin bypass
must reject at its exact assertion. Re-run older stack/wait/thread/memory/image
and M4 suites plus host/format checks on frozen sources; retain every attempt.
Use the pinned Clang 21.1.8 formatter for the new C fixture. No dependency, shared
standard, sibling source or immutable pin changes. Documentation and workflow
inventory describe the new optional suite; full libc integration remains open.
