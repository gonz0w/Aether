
## Native child stack-range contract — 2026-09-06

Preimplementation consumer review: pinned musl 1.2.6 pthread_create defaults to
128-KiB stacks, 8-KiB guards and additional TLS/TSD allocation; it positions its
initial stack below setup metadata. The retained OpenZFS helper requests 256 KiB.
The one-page native child stack and fixed initial RSP cannot express those layouts.
Aether owns range validation/pins; libc retains construction, TLS, guard and lock
policy. This step does not port pthread_create or fake missing signal operations.

Add 0x28005 under the existing native-threads grant, parent only, sharing the same
one-child creation budget. Rdi=grant, rsi=readable descriptor pointer, all remaining
argument registers zero. Copy all 64 bytes before any user write/publication.
Little-endian descriptor: u32 version=1, u32 size=64, followed by seven u64 values:
entry, stack_base, stack_bytes, initial_rsp, fs_base, clear_tid, argument.
Legacy 0x28000 retains its one-page geometry and exact input/output behavior.

Stack base/bytes must be page-aligned and nonempty within the granted anonymous
arena; every page must already be owned anonymous RW/NX backing. The arena quota
is the bound; this operation allocates no pages and grants no extra memory.
Initial RSP must be 8 modulo 16, with at least 128 bytes below it and eight bytes
at it inside the declared range. The kernel writes a zero return slot there;
entry receives the opaque argument in RDI. Entry/FS/TID validation follows the
existing creation rules. Descriptor bytes may overlap writable output storage
because the complete descriptor is copied before validation/commit.

Malformed version/size/reserved/geometry: -22. Unreadable descriptor or missing/
wrong-permission backing, entry, FS or TID: -14. Invalid authority/caller: -13.
Consumed one-child budget: -28. Failure does not write return/TID slots or publish
execution. A successful create returns 1; parent/child authority remains shared
only within the domain. All declared stack pages stay pinned through running or
blocked child execution, ending after child exit or domain stop. Caller-created
PROT_NONE guard pages remain inaccessible and consume existing quota; the kernel
does not invent a guard policy or auto-grow a faulting stack.

Select pure geometry/bounds tests, actual 256-KiB stacks with offset initial RSP,
full-range pins, first/last-page hole/permission rejection, malformed descriptor,
late invalid TID with unchanged sentinels, real guard fault with peer completion,
child exit/release, and supervisor stop/replacement. Re-run existing thread/wait,
memory/image and M4 regressions on frozen sources. Preserve every attempt and
new C's pinned format; record the reviewed upstream hashes/licenses. No dependency
or shared normative standard changes. The unsafe boundary is the existing IF=0
user-byte copy/validation/commit sequence; no user pointer escapes into scheduling.

Remaining libc gaps include distinct TIDs/parent-TID write versus clear-TID,
signal-mask/cancellation semantics, detached self-unmap, thread-list coordination,
indefinite waits, complete TLS extents and repeated thread creation. Stack-range
admission alone is not libc acceptance or a selected engine resource budget.
