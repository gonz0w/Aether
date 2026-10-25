# ADP-01-W02: native memory and teardown audit

## Finding and fix

The maximum roundable 64-bit length (`0xfffffffffffff000`) passed `length()`'s
bound but overflowed the intermediate `bytes + 4096` in `bytes + 4096 - 1`.
An authorized native memory caller could panic the Debug kernel instead of
receiving a bounded resource error. Grouping `(page_size - 1)` makes the
calculation agree with its guard. No ABI, quota or authority change is needed.
The target probe checks that exact map returns -12, the next length returns -22,
an overflowing unmap range returns -22, and available quota is unchanged.

`attempt-1` preserves the pre-fix host crash and failed qualification. These are
product failures, not infrastructure failures. Pure memory tests cover Debug and
ReleaseSafe; target suites use the existing Debug kernel and pinned native C build.
No optimized target-mode qualification is inferred from host ReleaseSafe.

The assembly frame previously checked only total size and CS offset. All 22 word
offsets now have compile-time assertions. `frame-reorder.log` demonstrates an
owned temporary r14/r15 swap failing for the exact r15 offset mismatch. This
protects Zig layout edits; assembly changes still require review against the list.

## Reviewed boundaries and obligations

| Source / boundary | Invariant and disposition |
| --- | --- |
| `kernel/native_memory.zig`: length/map/range | Rounding now stays within the checked bound; range checks addition before computing stop; arena containment bounds slot iteration to quota. Map resolves all backing/record slots without mutation. New tests cover maximum length, final arena page, adjacent TLS and cross-page clear-TID pins without modifying metadata. |
| `native_memory.zig`: tables/TablePlan | At most 32 tables and 512 directory indices; duplicate/out-of-range indices rejected. Full reservation precedes commit; existing tests cover late exhaustion and holes. `slot()` requires a successful plan and an address inside that plan, as supplied by map/range callers. |
| `native_c.zig`: memoryOperation | Admission, terminal state, exact memory capability and reserved fields checked before effects. Entire mapping/table/pin plan precedes PTE changes. RW/R/NONE anonymous mappings remain NX; executable requests are denied. Backing slots and page records stay domain-owned. |
| `native_c.zig`: byte/copy | `byte` resolves only present user pages with required permissions into the owner's fixed backing. `copy` chunks remain within one validated backing page; loader inputs and stack temporaries do not alias destinations. It is an internal initialization helper, not an untrusted memcpy syscall. |
| `native_c.zig`: memoryAlias/flushMemory/select | Kernel aliases follow user writability. Unmap clears leaf access, makes the backing alias writable, reloads CR3, then zeroes and releases records. PROT_NONE retains backing/quota. Native startup rejects PCID and clears PGE; no global translations are relied upon. Noncurrent domains reload CR3 before execution. This is BSP-only, not a remote shootdown design. |
| `native_c.zig`: threadOperation/set-FS/clearTid | Stored FS, TLS, stack, clear-TID and wait addresses originate from validated mapped ranges. Those bounds are preconditions for unchecked pin-end additions in helpers. Running-child stack/TLS and all blocked wait words prevent protect/unmap. Requeue transfers the registered address while preserving deadline; both addresses are checked before mutation. |
| `native_c.zig`: stopContexts/finish/control reclaim | Stop cancels waits and performs clear-TID writes while pages are still present, then stops children and revokes grants. Terminal state is required before reclaim. Root detachment and alias flush precede zeroing; metadata/CPU state reset follows. No backing reuse before those operations. Existing pair cases exercise supervisor stop with requeued waiters and new-generation reuse. |
| `protection.S`, `protection.zig`, `context.zig` | Interrupt gates clear IF; native handlers do not enable it during mapping transactions. Assembly clears DF, normalizes error/vector words, saves GPRs and aligns the C call stack. Returned Frame remains in static owner storage until iret. Full field offsets now checked. No unwinding crosses assembly. |
| `native_execution.zig`, build CPU features | FX areas are fixed 512-byte, 16-byte-aligned storage; embedded/array alignment has host checks. Kernel compilation excludes SIMD and uses soft-float before explicit FX save/restore. Native CR4 excludes OSXSAVE; AVX state is not supported. NMI/kernel faults are fatal, not resumable nested transactions. |

No new runtime allocator, lock, dependency or cross-core mutation is introduced.
Work is bounded by existing 128/2048 page arenas and fixed context/table arrays;
this is a bound review, not measured stack/latency or interrupt-duration evidence.
The native kernel is trusted; user fault containment is not kernel compromise
containment. Fixed bootstrap grants do not establish a production capability API.

## Coverage and remaining scope

`contract.md` records preimplementation selection and the discovered defect.
`results.json` records commands, source digests, timestamps and status; suite
receipts/raw logs retain their selected tools/artifacts and semantic controls.
The raw pair suites cover both memory profiles, pin transfer and stop/reuse; native
memory suites cover map/protect/unmap permissions, zeroing, quota and faults; M4
checks the separate cross-core teardown path as regression coverage.

This closes the scoped memory arithmetic defect and frame-layout check gap under
CE-02–07 and Foundations O-03/O-04. It is a contributor audit, not independent
acceptance or full W02 closure. Complete loader/device/FFI review, physical/SMT/DMA
and other shipped execution modes, measured stack/resource limits and independent
review remain required before their release claims. No new exception is approved.
The legacy compact `probe.c` style is retained for this semantic fix; no mass
format migration or pin/sibling changes were made. The existing musl condition-
waiter experiment can proceed without waiting for those unrelated release gates.

Final result: all selected commands pass on frozen runtime sources: 25 native
memory cases, 20 paired-thread cases and seven M4 cases (52 target cases total),
98 Python tests and Zig host checks, eight pure memory tests in Debug and
ReleaseSafe, exact frame-reorder rejection, format/workflow/standards checks.
The only failed attempt is retained in `attempt-1`; it reproduced the fixed
overflow. No test attempt or release pin was discarded or rewritten.
