# External native backing at existing quotas (before code)

Requirement: connect the tested physical pool/alias primitive to actual native
map/protect/unmap, immutable ELF, thread storage and supervised teardown before
larger service admission. Add one explicit opt-in BSP profile for AENATC01 and
AENSUP01 with unchanged128/2048-page per-domain quotas, live/lifetime child limits,
ABI, grants and SDK. No full-engine capacity or general VM-object/map claim.

One BSP kernel instance retains a64MiB boot-reserved usable pool. Its fixed native
domains receive disjoint partitions sized by their existing quota; remaining RAM
is not an allocatable user resource. Each State remains the sole authority for
its page metadata, grants, contexts and generation. Pool tables have one BSP
owner and shared supervisor RW/NX aliases across all its active roots. No AP,
global task/capability registry, allocator, DMA grant or physical reclamation.

Keep ordinary State backing arrays/layout unchanged when the flag is off. The
opt-in State uses a fixed-length, page-aligned borrowed pointer instead of an
embedded payload array; metadata is still the existing bounded State array.
Every pointer is established from a checked reserved partition, never nominated
by a user or inferred by subtracting kernel_start from external RAM. A small
payload accessor makes whole-array loops/zeroing valid in both representations.
Pointers are bound once for the domain lifetime and survive grant-generation
reset; zeroing the pointer descriptor instead of its payload is forbidden.

Bootstrap may use the initial boot HHDM only before admitting any user. After
constructing roots/images and narrowing immutable aliases, retarget every view
to the dedicated kernel alias before first context entry, with inherited global
translations flushed and PCID disabled. No boot direct map remains in active
native roots. Physical translations derive from the partition regardless of
which bootstrap/native view is active. Kernel-image phys() remains for actual
kernel tables/stacks/metadata only. Preserve old code/stack/RELRO permissions.

Reuse the same pool table builder in the isolated alias witness rather than a
second pmap implementation. Shared alias narrowing affects every root. Map
publishes only zeroed backing; protect retains quota and validates whole range;
unmap and stop remove user mappings/flush before restoring write access and
zero/reuse. Existing context pins, exact-ID retirement, quota/resource atomicity,
stale grants, terminal records, acknowledgments and permanent entropy close
remain. No operation acquires authority from a physical/virtual address.

Qualify both existing memory matrices under embedded and external backing; all
112 old pair/pthread cases after representation/alias consumer changes. Select
existing private origin/reuse/entropy replacement witnesses on external backing,
all13 isolated pool aliases and seven M4. A real omitted immutable-kernel-alias
narrowing control must fail the named mapping invariant; release artifacts reject
that negative control. Profile prerequisites/unsupported launch envelopes reject
before any reserved RAM is consumed. Preserve every failure, exact source/tool/
artifact/command/time receipt and read all archive members before duplicate cleanup.
Independent reader/consumer/SDK adoption, broader process profiles, cross-core
invalidation, physical hardware and R1 assembly remain unqualified.

Simplicity/security: retaining image-embedded payload cannot qualify external
physical translation. Enlarging all State arrays wastes RAM and hides ownership.
A compile-time fixed-length pointer only for this opt-in profile preserves old
layout and bounds without dynamic allocation, quota discovery or lifetime views
that can escape the owner. Reuse one table builder and existing capability/stop
paths; avoid a separate scheduler, memory service, public ABI or fake sysconf.
Larger metadata/quota/live-worker admission follows only after this path passes
with actual native clients.64MiB remains a trial reservation, not an observed
whole-engine budget or physical-memory advertisement.
