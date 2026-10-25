# Native external backing at existing quotas

Status: private BSP experiment qualifies at existing quotas, 2026-10-04.
`-Dnative-backing=true` requires native-memory, an explicit native image and
single-core mode. Only AENATC01/AENSUP01 startup is accepted, before reserved RAM
is consumed. Default/large128/2048-page quotas and all operations/grants remain.
No general VM API, larger engine capacity or production SDK adoption is supplied.

The BSP retains one checked64MiB boot-usable region. Its four fixed native State
slots get disjoint quota-sized partitions (2MiB total at128,32MiB at2048); the
remaining RAM is inaccessible to allocation/query through user grants. Each State
owns its unchanged page metadata, capabilities, contexts and generation. The
kernel instance owns the shared supervisor RW/NX pool table object. Nothing is
allocated globally across cores; AP startup and physical reclamation are absent.

Ordinary State backing stays an embedded array with the existing layout. Only
the opt-in field becomes a page-aligned pointer to an array of the same fixed
length. Whole-payload zeroing uses an accessor rather than clearing the pointer.
Partitions derive from the checked reservation, never a caller pointer. Bootstrap
uses the initial HHDM before any user admission; all views switch to the dedicated
kernel-only window after image/permission preparation and before first context
entry. Generation reset clears State authority and rebuilds the same view from its
checked partition; it never trusts a saved caller pointer. The views remain bound
to those retained physical owners until VM teardown. Initial
kernel-image phys() arithmetic remains for kernel tables/stacks/metadata only;
external payload frames come from their explicit partition.

The shared [pool alias primitive](NATIVE-BACKING.md) serves both this profile and
the isolated hardware witness. WP/NX/four-level/no-PCID and inherited-global flush
are required. Every active root attaches the same supervisor table; immutable
user code/RELRO loses writable kernel aliases. A lab omission of that narrowing
must fail the named `native backing immutable alias writable` invariant before
user publication. `-Dnative-backing-skip-alias-ro=true` is a negative control and
is rejected for release-designated artifacts.

Map/protect/unmap retain complete preflight, context pins, quota atomicity and
stale authority rejection. Removing user translations/flush precedes write
restoration, payload zeroing and reuse. Stop/ack/retained outcomes, exact-ID child
retirement and entropy grant lifetime remain. No pointer survives reclamation to
a different physical owner: the retained partitions are not reallocated here.
Broader process/launch profiles, cross-core invalidation, malicious DMA/hardware,
independent reader/consumer review and general VM objects remain unqualified.

[Before-code scope and receipts](evidence/native-external-backing-2026-10-04/README.md)
select embedded/external memory matrices, older pair/pthread compatibility,
external origin/reuse/entropy, isolated alias and two-core regressions. Run their
recorded one-off recipes with the pinned offline SDK/tools, then `zig build test`.
Builds180seconds, VMs30seconds and owned teardown3seconds; force-kill fails.
No larger State payload arrays, syscall, ABI or shared standards pin is introduced.

Fresh qualification covers 198 target cases, including both complete memory
matrices, all older pair/pthread cases and actual supervised replacement on the
external profile. The first replacement failure and fixed reset sources are
retained. Three partition/geometry tests, full host/pin checks and 18 build guards
pass. These remain bounded producer results. Next qualify one larger service's
metadata and resource geometry before live-worker admission and full engine use.
