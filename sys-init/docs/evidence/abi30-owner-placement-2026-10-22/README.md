# ABI30 owner placement consumption — 2026-10-22

[Decision0206](../../decisions/0206-abi30-owner-placement.md) consumes exact
Aether contract13e4f5bc308a5fc24cdfb9a510cdc968da9ba66feaeb526cb23bc6db081d6d01
and verifies all seven actual producer source hashes. Producer host/build geometry
uses an old activation owner placeholder; it is not a complete sys-init owner or
native mapping/permission/zeroing/isolation/entry witness. Old ABI28/29 profiles,
accepted owner/source, release/default/SDK pins and quotas stay fixed.

New no_std region helper distinguishes checked metadata from actual boot authority.
Only unsafe claim can borrow the trusted unique ABI30 mapping once until VM end.
It checks initial zero bytes before typed writes. Safe host construction takes
exclusive MaybeUninit<u8> backing, explicitly initializes it and partitions one
aligned MaybeUninit<T> slot,4096-byte workspace and spare. MaybeUninit backing is
necessary: a T write may uninitialize padding, which must never become a safe
initialized-byte read. No general allocator, restart, writable image statics,
automatic Drop/settlement or quota expansion. The gate writes each field before
creating its first Self reference, avoiding a full-gate stack temporary.

Four host tests cover every entry scalar, wrong old ABI, short/dirty/unaligned/
oversize/zero-size storage, exact4096-byte owner fit, non-overlap, NonZero/padded
objects and actual AF07/gate known-refusal/shared-offset/final-close/settlement.
Four strictly compiling omissions each fail exactly one selected assertion test:
dirty observation, alignment, bounds and scalar binding. No malformed pointer
claim, invalid-T read, unaligned typed access or native execution occurs in controls.
Strict formatting/default Clippy, host/native region/gate/stream builds pass.
preparation.json records tools, source/dependency artifact pins, commands and logs.

Native naked entry preserves six registers and stores r10/r11 as C arguments7/8
before its first call.20-byte object/disassembly captures sub rsp24, two stores,
owner_main relocation and ud2. There is no linked owner_main implementation yet.
construction.s.txt shows concrete native fieldwise construction with56 bytes of
local pushes/slot, replacing the prior2944-byte temporary plus pushes. This is
one function's local frame, excluding caller values/callees and whole stack fit.

code-study.json records the actual AEFD dispatcher/source/protocol native minimum
RPC closure, linked with static relocation/fat LTO and compiler_builtins. It is a
measurement-only Rust entry taking references from no caller, never executed and
not a kernel entry, successful boot stub, complete owner or native acceptance
specimen. Its section/disassembly evidence excludes the remaining fork/activation/
shutdown path; fitting this subset does not establish the16384-byte full bound.

Retained attempts: fixture-coverage compile failure; LLVM tool launched with the
wrong Rust DYLD path; and alignment omission compile failure from an unused
parameter. Final control uses the parameter and fails semantically. Pre-fieldwise
construction and pre-padding-review source snapshots are retained as superseded,
not accepted APIs. Rust DYLD path is scoped to Rust tools, never LLVM/C tools.

The missing BG-072 contract input is resolved. Complete owner/call-chain/resource
fit, actual native authority/entry/zeroing/NX/guard/isolation/old-profile controls,
transaction/startup/ready/parent/settlement/readiness/shutdown and fresh target
witnesses remain BG-070/072. No sibling edits/messages, guest, invented independent
review or changed release pin. Final full development checks are recorded separately.

## Continued native construction measurement

Twenty existing gate/stream/capture tests pass against the changed gate and rebuilt
trait-dependent streams/transport (regression.json). The native subset study then
retains real RPC, capture, copy/local inheritance, ready/parent delivery, connect,
settlement and disconnect. Before connect/settlement, size-s/z subsets are15112/
14080 bytes. Direct connect/settlement changes those to17016/16016; native
constructor reserves6536/6504 bytes before pushes/callees. The selected stack is
only4096. Whole opt3 reduces that local reservation but grows code to32008.

Noinline connect does not cure stack use: size-z callee reserves5328 and its caller
2208, before pushes/callees. Final noinline code is16272 (see composition-study.json).
An isolated opt3/fat-LTO static-library constructor plus size-z subset reserves280
constructor bytes plus48 pushes/callees, but total code19072 exceeds16384. It has
a real fail-stop panic handler and links with no undefined-symbol suppression.
Earlier raw-object attempts failed on dependency/panic symbol closure; none counts
as a size/behavior witness. All failed logs and complete command records remain.

The final measurement linker explicitly maps its load segment RX, uses static
relocation and has no dynamic relocations. No measurement entry receives actual
kernel startup or executes. Rust references/copy callbacks have no caller. Separate
kept roots can optimize differently from final unified code; their sizes are not
a theorem about every possible complete owner. Stack frames are measured local
reservations/lower bounds, not a complete peak-stack analysis. Debug sections are
not loaded code. measurements.json binds comparisons/logs/tools/artifacts.

[BG-073's focused handoff](../../BROKER-INITIALIZATION-HANDOFF.md) now requests
safe direct initialization of the existing opaque broker/nested state into caller
storage, with explicit partial-failure/one-greeting/actual-cleanup semantics.
The old missing kernel mapping input is resolved. Current selected composition
pauses at bounded broker construction; full routing/native transaction/fit and
native acceptance still belong to sys-init. No quota increase, guessed producer
layout, alternate stack, sibling edit/message or native guest is introduced.

Documentation impact: internal API/decision, native boundary review and22-record
inventory, quality coverage, mapping resolution/constructor handoffs, BG-070/072/
073, OQ-027/028 and current STATE/roadmap/priorities updated. No new installed or
public command/manual, user-facing output or released standards adoption change.
