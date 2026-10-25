# Scoped W02 memory/teardown audit contract

Review CE-02–07/CZ ownership, arithmetic, representation and execution context
against Foundations O-03/O-04. Scope: native_memory reservations, native_c memory
commit/clear-TID/stop/reclaim and protection.S/context.zig handoff. No native ABI,
quota, capability, runtime policy, sibling or pin changes are intended.

Close the representation-check gap: every assembly frame field offset must be
asserted, not just total size and CS. Reordering equal-sized registers must fail
compilation. Add boundary coverage for largest accepted length, arena end,
page-crossing clear-TID and TLS adjacent pages, preserving metadata on rejection.
These are validation improvements; no exploitable runtime defect is claimed.

Select Zig host checks (Debug and ReleaseSafe for pure memory tests), full host
suite, deliberate frame reorder rejection in an owned temporary copy, both native
memory profiles, both raw pair profiles (wait pin transfer/stop/reuse), and M4.
Record unsafe obligations, all attempts and remaining scope. No new dependencies
or runtime allocations. This review cannot supply independent owner acceptance,
physical/SMT/PCID/DMA coverage or the whole kernel/FFI/resource audit.

Confirmed during boundary testing: maximum accepted length panics because the
addition evaluates before subtraction. Fix by adding (page_size - 1), matching
the existing validation bound. Target probes must expect Exhausted for that map,
Invalid for overflowing range/next length, and unchanged available quota.
Keep the compact legacy probe.c format for this semantic fix; broader formatting
is deferred as the existing local migration exception.
