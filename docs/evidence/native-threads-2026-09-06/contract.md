
## Bounded shared-address-space thread contract — 2026-09-06

Preimplementation requirement: the engine runtime needs independently scheduled
execution within one domain. Add opt-in `-Dnative-threads=true`, requiring native
memory and only AENATC01/AENSUP01. Keep other profiles and the default ABI unchanged.
This is a kernel conformance extension, not musl pthread adoption. Aether owns the
mechanism; userland owns libc adaptation, sys-init domain policy, pkg-mgr artifacts.

Each worker receives a separate holder/generation-bound thread grant at auxv
0xa001. It authorizes exactly one additional context for that domain lifetime;
no child-slot reuse or implicit allocation. The supervisor gets no such grant.
Both contexts share domain memory/grants/streams. Creation from the child is denied.
Operations use int 0x81, rax opcode, rdi grant, return signed rax:

| Operation | Inputs and outcome |
| --- | --- |
| 0x28000 create | rsi executable entry, rdx page-aligned anonymous RW/NX stack page, r10 writable FS pointer, r8 opaque argument, r9 aligned writable 4-byte clear-TID. Return 1. Initial rdi=argument, rsp=stack+4096-8, zero return address, fresh FP state. All validation precedes writing TID=1 or publishing the context. |
| 0x28001 child exit | rsi status 0..255, all other inputs zero; child only. Clear TID and stop this context, retaining status. Never returns on success. |
| 0x28002 inspect | All inputs zero; parent only. Return -2 before creation, 0 while running, status+1 after exit. Observation does not reclaim or re-enable creation. |

Invalid/foreign/stale/missing grant or forbidden caller returns -13; malformed
inputs -22, invalid pointer/permissions -14, consumed creation budget -28.
Parent exit, exit-group, child fault and supervisor stop terminate the entire
domain; both TIDs clear before reuse. No pthread cancellation, signals, blocking
wait, migration or independent child fault recovery is implied. Each domain keeps
one owner on the BSP; interrupt exclusion serializes validation/publication/stop.

Round-robin domain selection alternates its runnable contexts, preserving each
frame, FS and FX area. Child yields do not change the existing parent-yield
fixture counter. Pin both live contexts' FS page plus predecessor and TID range,
and the entire child stack page against protect/unmap. Pins end only after child
exit or whole-domain stop. The fixed primary image stack remains immutable by the
existing memory contract. Caller-provided FS is a bounded pointer contract, not
validation of a complete libc TCB. Child code in the witness does not call libc.

Forbidden: cross-domain creation, parent/child CPU-state confusion, partial launch
on rejection, reuse while runnable, removing live context storage, false pthread
success or widening supervisor policy. No dependencies, heap or FFI are added.
The existing assembly switch consumes the selected aligned save area with IF clear.
Kernel copies validated user bytes through private aliases; entry and stack are
checked before a runnable context exists. Returning from child entry faults the
domain; the entry must explicitly exit. Resource cost is one fixed execution
record and bounded metadata per domain; stack/TLS consume existing user quota.

Validation: native strict-musl parent plus freestanding child; shared memory,
distinct TLS/XMM across yields, pointer/authority/quota rejection, retained exit,
TID clear, all-context pins, supervised stop/replacement and child fault containment.
A deliberately skipped pin must fail at its named assertion. Run old memory suites,
large-image suite, M4 regressions, host and format checks on frozen final inputs.
Record every failed attempt. Independent consumer review, optimized/stack bounds,
thread reuse and blocking wait remain open. New C uses the pinned Clang formatter;
existing compact adapter/harness style is not mechanically migrated.
