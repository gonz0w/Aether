
## Bounded native child retirement and repeated pthread contract — 2026-09-06

Before implementation: add parent-only opcode 0x2800a, RDI=thread grant,
RSI=expected native child ID, other argument registers zero. Validate authority
and parent context (-13), reserved fields/zero or oversized ID (-22), absent
child (-2), mismatched ID (-9), then live child (-16), before any mutation. A
completed child must have no wait registration or clear-TID pointer. Retirement
resets its Execution and stack/status metadata and frees the execution slot; it
does not unmap user-owned memory or reset the domain's admission budget.

Assign IDs from a bounded admission ordinal: first IDs remain unchanged; later
IDs add eight per successful admission. The ordinal advances only on successful
publication, never failed create or retirement. At most four admissions per domain
lifetime; exhaustion returns -28 even after retirement. Domain replacement resets
the ordinal under a new thread grant. Preserve existing inspect status/blocked-bit
results and one-live-child bound. New IDs are scoped to the domain grant, not global
POSIX identities. No global table, new memory allocation or authority expansion.

For a repeated-lifecycle producer, compile upstream __pthread_join under a renamed
symbol and wrap public pthread_join. Call actual join first; it observes clear-TID
completion and unmaps backing. Then retire by the ID saved at clone admission,
never by dereferencing the freed pthread handle or its zeroed tid. Only a successful
retirement permits the adapter's next creation. An unexpected retirement failure
returns EIO and leaves admission closed. Other lifecycle producers delegate join
unchanged. Source remains unmodified; record the compile-time symbol adaptation.

Run four actual 256 KiB pthread lifecycles per domain, with fresh TLS, masks,
stack data, native IDs, join values and quota recovery each time. Check live
retirement denial, stale-ID rejection while a replacement runs and after it exits,
duplicate retirement/empty inspect, failed-create retry and exact fourth-admission
exhaustion. Retain the original one-successful-child behavior until explicit
retirement. A same-ID mutant must reject at assertion 233. Do not claim safety
for reusing a joined C pthread_t: it is invalid even if a later allocation has
the same address. Native retirement tokens, not stale C pointers, are tested.

Add repeated, supervised repeated and same-ID rejection cases to both lifecycle
profiles; preserve older cases. Host tests check ID bounds/exhaustion and reset.
Run all thread-family, memory/image and M4 regressions plus host/standards/format
on frozen sources. Record every attempt. Kernel owns admission/retirement; this
is a conformance userland adapter, with no sibling adoption or standards-pin change.
No concurrent pool expansion, cancellation, detached cleanup or release claim.
