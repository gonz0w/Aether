# 0172 — Retain acknowledged launch sources and retire effect capacity

BG-057/BG-058, 2026-09-07. Extend the successful decision 0171 path while keeping
its original Application, History and GeneratedLaunch alive. Retain an owner-bound
Executed occurrence, exact token and originating cut serial before making its
single effect slot unused or releasing twenty credits. Native qualification must
also retain the original generated record's Applied channel/launch, reader, worker,
writer transfer, exact target and error absence. A copied token is insufficient.

Add cached effect count and explicit retirement status to each cut using existing
repr(C) padding, preserving the 1976-byte storage bound. Historical receipt counts
must not change when a later cut occupies the shared effect pool. Retire only the
exact current Applied cut with one acknowledged effect and no other occupied
slots. Validate the owner and every occurrence field; populate caller-owned typed
retained storage before clearing occupancy. Missing retained output closes while
preserving the original effect. Repeated, foreign, unacknowledged or ambiguous
retirement denies without mutation. No blanket clear, new owner or serial reset.

The retained effect is tied to the same original owner and cut; its metadata does
not authorize native calls or substitute for the original GeneratedLaunch return.
After retirement, qualify that unchanged native source, reserve dependent Launched
with fresh serial two and apply [1,0] -> [1,1] with zero effects. Fix the existing
single-cut assumption that would regenerate the dependent launch. Preserve the
first receipt's count one and both cuts' membership/before/after/serials on replay.
An explicit owner-bound empty-cut retirement may release credits for the second
cut only after verifying no occupied effects; it does not evict either cut record.
Terminal/Cleaned, general multi-effect retirement and sustained reuse stay open.

Host tests cover retained identity, exact ack gating, old-key rejection, historical
receipt stability, a second zero-effect cut, capacity release and full denial
atomicity. Native probes keep the successful provider/dependent launch and ack;
retire before fixture disposal, revalidate the original source and apply dependent
Launched without another acquisition/launch. Positive remains 100/3. Controls omit
retention (1088), bypass ack gating (1089), forget historical counts (1090), or skip
native source qualification (1091); failure-retention postconditions use 1092.
Run 208 fresh Aether cases, relevant host tests and all local checks. Preserve old
semantics and image/stack bounds, pins, historical evidence and sibling repos.
Foundations O/I/E and scoped Experience/Distribution rules remain authoritative.

## Validation and handoff

Decision 0172 retains the acknowledged generated launch before explicit effect
retirement, then applies the dependent's Launched observation on Aether. The same
Application, History and GeneratedLaunch remain alive through the two cuts and
fixture disposal. Private retained metadata binds the original owner, complete
occurrence token and originating cut serial; it grants no native authority.
Native qualification separately checks original context, Applied channel/launch,
reader/worker retention, transferred writer, error absence and full target.

Retirement requires the current Applied cut, exact original receipt/effect key,
Executed disposition, unused remaining effect slots and empty output storage.
It writes retained metadata before clearing the occupied slot and freeing twenty
credits. Missing retained output closes while keeping the original Executed
occurrence and occupied capacity. Foreign, stale, repeated, unacknowledged and
occupied-tail denials preserve storage. Historical effect count and retirement
status use existing record padding: storage remains 1976 bytes, Application 1992.

The second cut has fresh serial/journal two, applies [1,0] -> [1,1] and generates
zero effects. The prior single-cut policy assumption is fixed so Launched does
not issue the dependent launch again. The first cut retains its original count
one, before/after state and membership. Empty-cut retirement explicitly verifies
zero occupied effects before releasing the second cut's credits; neither cut is
evicted and serials are not reset. Host tests also verify historical replay,
foreign owners, every token field, nonempty retention output and stale-key denial.

All 208 fresh Aether cases pass: the new positive finishes 100/3; controls omit
retention (1088/0), bypass acknowledgment (1089/0), forget historical effect count
(1090/0), or bypass native source qualification (1091/0). Assertion 1092 checks
failure retention and dependent postconditions. All 203 earlier semantic outcomes
pass again; 194/203 prior images and all 151 ABI-6 rebuilds are byte-identical.
The five new images are 8064/7968/8064/8096/7984 bytes; suite maximum 8152/8192.
All ten local gates pass in `run-ilflnaqs`, including 287 model tests and ten Rust
groups with eighteen core tests and twelve omission controls. The no_std core
also compiles for x86_64-unknown-none. No heap, unsafe site, syscall, dependency
or image/stack-limit increase is introduced.

The first two preflight sets failed the two-page linker bound. The retained map
identified formatted bounds-panic machinery from new dynamic indexed access;
checked record lookups remove that dependency without weakening denial. The third
preflight and focused five-case target run passed. Final ownership/closure review
adds same-Application retained-source validation, preserves History closure on
ambiguous dependent application, and retains occurrence checks through disposal.
The fourth preflight and full target run cover those final bytes. Native stack
assembly is retained; the root frame remains 3176 bytes, with the unchanged
528-byte Adapter launch frame and bounded intervening calls on the 4 KiB stack.
The target witness qualifies this concrete composition, not arbitrary call depth.

Evidence: `docs/evidence/acknowledged-launch-retirement-2026-09-07/`.
Producer/worker/release pins and catalog bytes remain unchanged. The catalog still
records 50 bundles/3019 historical outcomes pending BG-056 complete producer source
closure; no exception is extended. This is process-local retention, not storage
durability, Terminal/Cleaned application, general multi-effect retirement,
sustained reuse or recovery. Independent reviewer sign-off is not claimed.

Next BG-057/BG-058: qualify retained provider/dependent terminal observations for
native policy application under the same owner, retaining partial/error evidence
before cleanup. BG-060 owns sustained history capacity/reuse and BG-033 recovery.
No kernel blocker is established; other-platform provisioning remains deferred.

Technical review: retirement checks owner/state/identity and full occupied inventory before mutation; retaining the source precedes capacity release. Checked record lookup preserves rejection without formatted bounds-panic growth. A caller cannot overwrite an existing retained output. Source metadata cannot qualify another Application or replace its native generated return. The policy transition and expected-effect oracle both distinguish provider launch from dependent launch completion. Native code retains the original resource owners through fixture disposal; no terminal policy or durable storage claim follows. Documentation impact: storage/application contract, native coverage, quality and CLI-source inventories, standards adoption and BG-057/058 handoff.
