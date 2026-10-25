# Boot-owned backing prerequisite (before code)

Current requirement: OpenZFS's selected measured profile needs82 live workers,
more than20MiB requested stacks and additional image/heap/TLS. Current static
8MiB per-domain backing cannot fit. Do not multiply a large arena across every
State or enlarge Plan arrays on the16KiB native exception stack. Before resource
binding, qualify selection/reservation of one explicit boot-owned region.

First experiment reserves64MiB for BSP ownership from validated Limine usable
memory only, below4GiB, excluding low1MiB and all other map ranges. This is an
experimental reservation ceiling, not a measured engine admission guarantee.
Reject malformed/overflowing/overlapping/oversized maps and insufficient contiguous
space before writes. Validate page alignment and HHDM canonical arithmetic. Zero
and verify only the chosen region while still on boot mappings, retain ownership
until VM teardown, and expose no allocation/syscall/grant interface yet. No DMA,
AP, service or user task is admitted in this isolated experiment. No bootloader,
kernel, module, framebuffer or reclaimable range may be selected or overwritten.

The next owner binding must separately map kernel-only RW/NX aliases in each
active CR3, preserve read-only immutable user backing aliases, replace kernel-
image-only phys assumptions, separate arena metadata from kernel stack plans,
and settle stopped execution/CPU translations before zero/reuse. Per-core/domain
ownership stays explicit; no global mutable task/capability allocator or ambient
memory discovery. Existing fixtures/default quotas/pins/SDKs remain unchanged.

Host counterexamples must cover nonusable overlap, wrap/unaligned boundaries,
low/device memory, exact64MiB fit, insufficient space and no partial claims.
Actual opt-in boot probe must verify every byte and reject malformed selections;
release-designated artifacts exclude lab controls. Existing M4/block/entropy/native
profiles and full host/pin/workflow checks precede adoption. Record commands,
artifacts/tool/source/time identities and all failed attempts; archive readback
precedes only owned duplicate cleanup. Scoped boot markers follow Experience.

Simplicity/security: use one explicit contiguous reservation before a service
allocator, avoiding dynamic frame allocation/reclaim and retained global tables.
None of the alias, W^X, overflow, quota or lifetime checks can be omitted. A smaller
static quota increase is insufficient and would retain the wrong image-relative
storage assumption. Production budgets, scattered frames, physical hardware,
IOMMU/DMA, simultaneous service placement and whole-engine execution remain open.
