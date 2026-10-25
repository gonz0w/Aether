# Private backing aliases (before code)

Requirement: native physical translation and kernel-only protection must work for
RAM outside the kernel image before a larger service can consume the boot-owned
reservation. Extend the isolated BSP backing experiment to prove one64MiB region
under fresh four-level roots. No native State backing/quota, child capacity, ABI,
SDK, allocator or full-engine admission changes. This is a pmap prerequisite,
not a general VM-object/map implementation or service memory grant.

Reserve through the already checked complete Limine map; reject geometry before
writing. Install one dedicated aligned upper-half alias window separate from the
kernel image and old boot HHDM window. Static off-stack page tables describe all
16,384 pages. Each selected physical address is region-relative, never inferred
by subtracting kernel_start from an external pointer. Two isolated roots share
that BSP-owned alias table; no AP, device, user service or allocator starts. Keep
kernel text RX, rodata R/NX, data RW/NX. No inherited direct map or user-visible
pool mapping is allowed. Require WP, NX, four-level paging and no PCID/global pool
translations. Use existing GDT/IDT/context entry machinery and mapped kernel
stacks instead of a separate exception framework or copying the old boot stack.

The successful experiment must switch both actual roots, read/write the first
and last reserved pages, narrow a page to R/NX in both roots, detach translations
before reuse, restore only authorized kernel write access, clear/verify the whole
retained region and repeat the root-visible pattern. IF remains clear; no remote
CPU/context can retain a translation. The region is retained until VM teardown;
this is not physical frame reclamation or DMA protection.

Separate real #PF cases must bind CR2, CPL, vector and error bits for supervisor
write to a readonly alias, supervisor execution from NX RAM, CPL3 access to a
supervisor alias, and access after detach. The CPL3 fixture is fixed test code and
stack only, with immutable code alias protection; it has no RAM authority. Actual
omitted RO/NX/U-S/detach controls must fail the specific progression oracle rather
than pass on any panic. Boot reservation's old cases and lab release exclusions
remain. All lab modes must reject release-designated artifacts. Pure geometry
checks cover alignment, bounds, wrap and first/last physical addresses; default/
large memory and two-core regressions qualify unchanged older behavior.

Unsafe obligations: prove every kernel stack/frame/table/code/descriptor is in
mapped kernel image storage before CR3/context entry. No user or external pointer
may nominate a physical frame. Alias permission changes flush the current root;
switching the other root with PCID disabled discards its prior translations.
Detach/zero/reuse ordering is owner-serialized. No stale HHDM alternative may map
the same backing writable after narrowing. Retain all failed attempts, source/
tool/artifact/command/time receipts and full archive readback before duplicate
cleanup. Independent review, physical hardware, cross-core invalidation, dynamic
metadata/ownership and actual native service binding remain unqualified.

Simplicity: retaining initial HHDM alone cannot prove native-root permissions or
remove the kernel-image-only physical assumption. Enlarging every State array
would waste memory and hide ownership. The smallest next witness is isolated
root/alias qualification using existing boot reservation and exception machinery;
no new runtime service, compatibility layer or allocator is justified. Shared
kernel alias tables give one explicit owner rather than per-root mutable copies.
A future general pmap can reuse the proven constraints; no generic VM API is
invented here. Still-local next work is explicit service backing/metadata/table
binding, resource admission and selected engine startup/fini/restart.
