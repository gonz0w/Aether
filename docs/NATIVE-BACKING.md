# Boot-owned backing reservation experiment

Status: isolated BSP experiment,2026-10-04; native service binding is not adopted.
`-Dbacking-test=reserve|overlap|corrupt|skip_clear` requires `-Dsmp=false` and
excludes native image/block/entropy modes. Release-designated artifacts reject
all lab modes. Ordinary profile quotas and launch contracts remain unchanged.

The pure planner validates every range in a1–128-entry memory map before choosing
one page-aligned64MiB region from Limine usable memory, above low1MiB and below4GiB.
Unknown/nonusable kinds are excluded; zero/wrapped/overlapping ranges reject before
any write. Insufficient contiguous space fails explicitly. HHDM base/result/span
must be canonical and separate from the kernel-image alias window.

Only this isolated BSP boot path may use the reservation. It starts no allocator,
AP, user service or device, dirties/clears the owned region, then verifies all bytes
through volatile word reads. Ownership remains reserved until VM teardown. No
reclaimable/firmware/kernel/module/framebuffer range is released or overwritten.
This is an explicit trial ceiling, not a measured whole-engine memory guarantee.
There is no public allocation, quota-discovery or capability API in this probe.

Next native binding must install supervisor-only RW/NX aliases in active roots,
remove writable immutable-user aliases, replace kernel-image-only phys assumptions,
keep large metadata/plan arrays off the bounded native exception stacks and require
confirmed stop/translation cleanup before zero/reuse. Per-core/domain ownership
must stay explicit. Scattered frames, reclaim/DMA/IOMMU, physical hardware and
simultaneous service placement remain unqualified.

[Before-code scope and receipts](evidence/native-backing-plan-2026-10-04/README.md)
include malformed map/alias host controls and real QEMU omission/corruption checks.
Run its `native.py` with pinned offline tools, then `zig build test`. Builds180seconds,
VM30seconds and owned teardown3seconds; force-kill fails. This does not complete
engine admission, filesystem integration, production SDK adoption or R1 release.

## Constant-size memory plans

The internal native memory planner uses a16-byte address/count descriptor and a
32-byte free-record cursor on x86_64, independent of the existing128/2048-page
quotas. Full request preflight precedes mutation. Only the authoritative owner
may borrow its metadata through commit, with interrupts disabled and no scheduling
or callbacks. Map commits publish only visited free records; range commits
resolve virtual-address order even with fragmented records and may clear only
visited records. An internal lifetime violation panics. No heap allocator, new
quota, ABI or capability is introduced; range lookup remains bounded scanning,
not a claimed linear allocator. Larger metadata must still stay off the exception
stack before binding the external reservation.

Run `zig test kernel/native_memory.zig --cache-dir .zig-cache --global-cache-dir
.zig-cache/global` and both existing default/large `scripts/memory_smoke.py`
profiles with the pinned SDK inputs in [NATIVE-MEMORY](NATIVE-MEMORY.md). Select
the complete pair/pthread lifecycle suites when changing plan consumers;
[the scoped evidence packet](evidence/native-memory-plans-2026-10-04/README.md)
records those runs and a deliberately broken cursor control.

## Fresh-root alias experiment

The same isolated BSP lab adds `alias`, `alias_ro`, `alias_nx`, `alias_user`,
`alias_detach` and omission controls `alias_skip_ro`, `alias_skip_nx`,
`alias_skip_user`, `alias_skip_detach` under `-Dbacking-test=<mode>`. All require
single-core mode with no native image or block/entropy device experiment, and all
reject release-designated artifacts. No ordinary native profile is expanded.

One boot-reserved64MiB region is mapped at0xffff900000000000 through32 static
leaf tables shared by two fresh roots. All frames derive from the validated
reservation, not kernel-image pointer arithmetic. The window excludes the old
boot alias and kernel image. Kernel text stays RX, rodata R/NX, data RW/NX; pool
aliases start supervisor RW/NX. No inherited direct map or allocator exists. The
BSP disables inherited global translations, requires WP/NX/four-level paging with
no PCID and keeps interrupts disabled. Existing mapped GDT/IDT/TSS/stacks and
context entry handle activation and faults. Only the fixed U-S test admits a CPL3
code/stack fixture, with immutable code and no authority to the pool.

The positive switches both actual roots, checks first/last physical pages, narrows
one alias, detaches its translation, reloads before write restoration/whole-region
zeroing, and verifies a second pattern through both roots before final zeroing.
Other cases bind actual #PF vector/CR2/CPL/error bits for RO writes, NX execution,
CPL3 reads and detached reads. Omission controls must reach their specific
forbidden progression; any unrelated panic is failure. The pool remains retained
until VM teardown. This does not implement native service backing, cross-core
shootdown, physical reclamation, malicious DMA protection or general VM objects.

[Scope and receipts](evidence/native-backing-alias-2026-10-04/README.md) retain all
attempts. Run its `native.py`, the geometry host tests included in `zig build test`,
and selected default/large memory and two-core regressions. Builds180seconds,
VMs30seconds, owned teardown3seconds; forced teardown fails.


The [separate native binding](NATIVE-EXTERNAL-BACKING.md) now uses this same table
builder at existing quotas. The isolated lab's acceptance stays separate from
native service capacity, general VM and full-engine resource admission.
