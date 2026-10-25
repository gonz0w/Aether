# Acknowledged launch retirement — 2026-09-07

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

witness/ retains producer/worker, thirteen frozen consumer inputs, case images/envelopes and raw logs. Exact commands and ISO hashes are retained; generated ISOs remain in private out. preflight-1/2 retain failed linker attempts and copied source; preflight-3/4 retain bounded successes, with final assembly in preflight-4. restricted-run/ retains its earlier source and five actual target results. validation/ and rust/ record final local checks; initial-rust/ is earlier focused coverage. legacy-build/ is build comparison only. adoption/ freezes the handoff; sha256.json seals the package. The inherited producer archive omits two previously recorded .DS_Store files; full producer source closure and catalog acceptance remain pending, with no new waiver.
