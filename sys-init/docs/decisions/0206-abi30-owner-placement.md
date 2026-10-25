# 0206: Consume bounded ABI30 owner data and capture entry registers

2026-10-22 / BG-070/072. Component implementation and host/build checks complete; full native composition blocked at BG-073.

Verify exact Aether contract 13e4f5bc308a5fc24cdfb9a510cdc968da9ba66feaeb526cb23bc6db081d6d01
and all seven pinned sources before selecting AENFS004/ABI30 locally. Preserve
old ABI29/default/release pins and accepted owners. The new boot mapping alone
supplies authority: exact scalar validation does not turn arbitrary input into a
memory grant. Capture all six old grants plus r10/r11 before ordinary calls.

Use a naked entry adapter to copy r10/r11 into arguments7/8, preserving original
argument registers and C stack alignment. Native object/disassembly checks do not
claim execution. One explicit memory boundary borrows the trusted unique boot
mapping as bytes, checks zero/alignment/layout and partitions a single uninitialized
owner slot,4096-byte workspace and spare bytes without overlapping live borrows.
Initialize T by writing a valid value before any T reference. No general allocator,
owner restart, writable image statics, automatic resource cleanup or quota change.

Simpler alternative: stack placement remains incompatible with the selected live
objects. A single typed slot plus workspace is chosen instead of an arena/general
allocator; no extra ledger. Unsafe obligations are explicit and locally reviewed,
not inferred from a checked numeric address. The caller owns actual boot provenance
and one-time acquisition until VM termination. Host-owned aligned byte arrays test
the safe partition core; native entry and permission/zeroing/isolation require fresh
Aether execution after complete composition.

Select checks before implementation: wrong ABI/base/size/grants, dirty/unaligned/
short/oversize regions, no construction before layout acceptance, exact fits and
non-overlap, actual native Gate size, moved owner state, buffer reuse, borrow escape,
negative controls, strict formatting/Clippy, host/native builds and entry disassembly.
Measure actual construction/call frames, full remaining layout and code before
claiming executable fit. Continue native composition after this input is consumed.


## Result and review

Exact contract and all seven source hashes verify. Four new placement tests/four
compiling omission controls,20 prior gate/stream/capture regressions and strict
format/Clippy/host+native builds pass. Object captures entry r10/r11 before call.
MaybeUninit<u8> backing fixes a review finding: writing padded T into borrowed
initialized u8 storage can invalidate subsequent safe byte reads. Raw native zero
observation occurs before typed writes. Native entry/authority/permission/zeroing/
guard/isolation and old-profile controls are still required; no guest ran.

Concrete gate fieldwise initializer reduces its measured local construction frame
from a2944-byte temporary plus pushes to56 bytes of pushes/local slot, excluding
caller values/callees. Actual by-value ProcessFiles construction remains a separate
problem: direct size-z reserves6504 bytes, beyond the4096-byte stack; noinline
still reserves5328 in the callee plus2208 in the caller. Whole opt3 and isolated
opt3 static-library + size-z subsets require32008/19072 code bytes against16384.
These are measurements of selected subsets/arrangements, not a full-owner lower-
bound theorem. Independent-root measurements may differ from final unified code.

The simpler current by-value API was tested and fails this target construction
budget. Local field initialization is chosen for our gate; do not reconstruct
producer-private Rust layout or grow generic allocation/build/stack machinery.
The removable complexity is aggregate copying and the isolated optimization/
raw-link alternative, which is retained only as a rejected measurement. Existing
AF07 transport, broker/pipe state and old APIs are deliberately reused. No new
services, queues, descriptor ledger or user-facing protocol are introduced.

BG-072's missing authority contract is resolved; native consuming acceptance stays
open. New [BG-073 handoff](../BROKER-INITIALIZATION-HANDOFF.md) requests a narrow
safe in-place constructor from the owner of the opaque FILE broker. That seam
needs explicit partial-failure/cleanup/one-greeting semantics before use. Remaining
routing/full transaction, complete fit and fresh native acceptance are sys-init
responsibilities, not claimed complete or moved wholesale to another owner.

Applicable pinned Foundations O-01–05 ownership/authority and I/E interface/error/
input/evidence rules apply; Distribution native build/resource clauses stay fixed.
No released standard/API, SDK/default pin, quota or sibling repository changes.
[Evidence](../evidence/abi30-owner-placement-2026-10-22/README.md). Independent
technical/reader review is not fabricated by these implementation checks.
