# 0208: Measure the existing musl byte comparison in the owner

2026-10-22 / BG-070/073. Pre-code implementation review.

Requirement: recover code space in the current in-place FILE owner without
weakening comparisons or changing the16384-byte code,4096-byte stack,8192-byte
data or other experiment limits. The selected independent roots currently need
16544 bytes. They are a measurement specimen, not a complete runnable owner.

Select a separate compact-comparison measurement in the existing checker. Borrow
only musl1.2.6's unchanged `src/string/memcmp.c` from the already provisioned SDK
archive (SHA256 d585fd3b613c66151fc3249e8ed44f77020cb5e6c1e635a616d3f9f82460512a).
Verify that archive, source, full MIT COPYRIGHT and the three required SDK headers
before consumption. Build one freestanding C17 object with pinned Clang21.1.8;
link it explicitly, without libc, dynamic loading, undefined-symbol relaxation,
new allocation, writable state or capability changes. Retain the license with
the temporary object and record its identity. Remove generated objects after
recording compact results. Future distributed images must include musl's notice.

The C ABI comparison accepts two valid readable byte ranges of length n, returns
the sign of the first differing unsigned bytes and reads nothing for zero length.
Rust's existing comparison lowering supplies the ranges; no new pointer-producing
API is exposed. The leaf does not allocate, unwind, retain pointers, synchronize,
read beyond the first difference or grant authority. All lengths, identities,
epochs, rights, message framing and cleanup checks remain in their existing owners.
It is not a constant-time primitive and must not be advertised as one.

Forbidden: hand-edited upstream logic, successful no-op comparisons, compiler
recursion into memcmp, hidden library dependencies, a quota increase, an old
delivery repin or calling subset fit complete owner/native acceptance.

Focused tests: exhaustive one-byte ordering, equality/prefix/zero-length and
unaligned ranges with first/middle/final mismatches; inaccessible guard-page
boundaries; UBSan host execution; a signed-byte semantic omission must fail the
ordering oracle. Inspect native symbols/undefineds and assembly; link the same
required roots and report code/stack observations. Reuse the unchanged producer
checks by exact source/library hashes, run consuming gate tests and inventory/
pin checks. No guest until complete actual owner composition and fit are available.

Simplicity: the simpler alternative is the existing Rust compiler-builtins
comparison; its measured closure costs more than this narrow owner can currently
fit. Reuse the existing SDK's proven byte loop instead of inventing a memory
implementation or removing validation. Added cost is one explicit, pinned C leaf
and focused qualification; it may remove the larger comparison closure only in
the new selection. If it does not improve measured fit, do not select it. Whole
transaction/entry/readiness/shutdown and peak-stack analysis remain BG-070 work.
Implementation-agent review only; independent review and native acceptance pending.
