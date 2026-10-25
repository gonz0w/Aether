# UL-082 C engine bridge and native integration review

Plan before code: implement a no_std bridge to the pinned private ZPL writer C
interface and shared UTC reader. One noncloneable SPA borrow owns one context;
context/inputs/results stay live and nonaliasing synchronously; no raw client
pointer/identity/time authority, reentry, Send/Sync or unwind across C. Register
original accounting/UTC before admission and keep SPA alive through consuming
close; producer owns registration/import/drain/export. No implicit engine setup.

Host tests link real Rust bridge/policy with a typed compiled C ABI fixture using
captured unmodified headers. Assert C/Rust sizes/alignment/field offsets, cleanup
of failed opens, valid/error buffers/counts/progress, UTC errors, alias EOF and
poisoning/drop exactly once. Fixture is an injected C provider, not OpenZFS.
Compile-fail tests enforce non-Send/non-Sync, sole SPA/context borrow and no escape.
Compile x86_64-unknown-none objects with original target core and native-policy
probe; inspect symbols/imports and actual C header layout independently. No host
or relocatable link result substitutes for native engine execution.

Pinned Rust1.98/Clang21/LLVM tools and sources before consumption. Original source
BSD-2-Clause; upstream original CDDL engine is not copied into new implementation.
Relevant Foundations O/I/E, Distribution NC/FS/OB, approved TD/TC/TE and CR/CC/CP.
Rust2021, panic=abort native, no allocator, default Clippy, explicit SAFETY contracts.
Owned60s compile/30s host bounds, private build root, retain every attempt including
negative compiler/link controls and cleanup before disposal. Minimum/current Python,
format/syntax/quality/all pins and whitespace before completion. Native uncertainty
retains existing stop/report/no-retry rule. No sibling code/SDK/wire/pin changes.

Simplicity: thin synchronous FFI wrapper and one inherited Rust policy owner;
no second backend cache, plugin framework, async/runtime or new filesystem format.
Safe Rust policy cannot enforce opaque C lifetimes by itself; one explicit unsafe
SPA constructor supplies that obligation and borrow-checked contexts preserve it.
No accepted fixture is retired; a matching native callback selection is a required
producer handoff, not silently changing its current writer/read-only consumers.
Independent owner/native/reader reviews remain pending. UL-082/M3/R1 stay active.

Actual technical review by Codex: raw node/write/time representations match
captured C and native headers; buffers/results are separately initialized and
borrowed synchronously. NonNull + exclusive phantom borrow prevents transfer,
clone, overlap and escape; compiler controls exercise those boundaries. Owned
nonnull factory errors close once. C return/progress values remain distinct;
state2 is not durability. Callback retains committed and successful progress even
when later readback fails, reserves state3 for uncertainty and initializes valid
output on null rejection. Host C fixture executes these actual wrappers but is
not the original engine. Native original C definitions resolve all six Rust ZPL
calls; deliberate omission exposes write. No full engine/VM/stack or quiescence
coverage follows. Independent owner/native/reader reviews remain pending.

Initial filename adaptation and host/native dependency search collisions failed
before native execution and are fixed using explicit output paths/separate target
roots. Probe Clippy warning is fixed with a C-string literal, no suppression.
Current producer probe source fails an old historical base equality check; it is
quarantined as proposal-only follow-on. Aether's new repeated-write native failure
is retained as a separate owner blocker. No source/current receipt is rewritten
to imply acceptance. Final gates/attempt retention are required before completion.

Completion of this slice: both actual Python versions pass the final bridge
selection over identical source; native Rust and C/Rust bytes match. Final quality,
all published pins, actual syntax, source/manifest/member readback and whitespace
pass. Nine ABI fixture tests, six compile-time restrictions, two layout and one
write-omission control pass. No suppression, guest, retry or broadened authority.
The18-member private review packet is immutable (delivery.json); eleven generated
roots are disposed after1122 compact records and every historical driver/source
are checked. Full engine execution is blocked by owner uncertainty disposition
and missing callback selection. This is incomplete native/UL-082/M3/R1 acceptance.
