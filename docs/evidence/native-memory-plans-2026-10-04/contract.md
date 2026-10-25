# Constant-size native memory plans (before code)

Requirement: a64MiB backing view would need16,384 page records; the existing
quota-sized array of u16 slots would occupy32KiB in each Plan, exceeding the
16KiB native exception stack. Remove that dependency before larger owner binding.
No page/table/lifetime/live-slot quota, ABI, grant, mapping policy or SDK change.

Replace the stored slot list with an address/count descriptor. A successful map
plan supplies a bounded free-slot cursor; range plans resolve the next validated
virtual page from borrowed owner metadata. Preserve full preflight of backing,
records, address geometry, tables, permissions and context pins before mutation.
Failed constructors change nothing. Only the authoritative owner under IF-clear
serialization may consume a plan; no scheduling/callback or unrelated metadata
change is allowed between preflight and commit. Commit may update/clear only
already visited records. A violated internal lifetime invariant panics instead of
reporting success or releasing resources. Plans are not user objects or authority.

Retain exact free-slot and virtual-range order, zero-before-publication, PROT_NONE
reservation, immutable/RW-NX aliases, TLB-before-clear/reuse, table hole reuse and
all ABI errors. Map/range scans remain bounded by existing quotas; this change
claims stack reduction, not a new linear allocator or larger-capacity performance.
Default128/large2048 restrictions remain. Constant-size descriptor/cursor layout,
fragmented/permuted metadata, in-place committed iteration, holes, failure/retry,
exhaustion and old boundary/pin tests must pass. Required native memory default/
large, pair/pthread and relevant entropy/block/M4 regressions prove compatibility.
Keep frozen inputs/all failures/actual commands/source/tool/artifact/time receipts;
archive readback precedes owned duplicate cleanup. Public adoption/reader review
and future metadata sizing remain separate coverage.

Simplicity/security: borrowing stable owner metadata removes large copied arrays
without a kernel heap allocator, new quota, global mutable object or chunked partial
ABI. Keeping arrays is insufficient for the documented next backing size; splitting
operations into smaller commits would weaken whole-request rejection semantics.
The new cursor/lookup cost is justified by bounded stack use; preserve checks and
avoid unrelated allocator/performance/format cleanup. Native owner physical/alias/
table/cleanup binding and actual engine admission remain later work.
