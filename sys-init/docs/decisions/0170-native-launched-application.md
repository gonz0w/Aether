# 0170 — Native Launched policy application

BG-057/BG-058, 2026-09-07. Consume decision 0169's fixed application owner against
an actual launch from the 0168 Driver/History path. Borrow original History
exclusively, retaining its Context, full token, worker, generation and resources.
Revalidate the source before both reservation and application. This first binding
supports only attempt zero's Launched observation; the generated attempt-one
launch obligation remains Reserved metadata and is not executed or acknowledged.

Extract the existing reservation source checks into one private shared qualifier.
Keep old reservation probes and source identity semantics. The new owner contains
one Application and the original mutable History borrow; no caller-built source
record or Applied receipt can be installed. Applied driver return and Applied
policy observation remain distinct, with their own retained states.

Launch one actual worker, apply its native return, then reserve/apply the Launched
policy observation. Launched needs no terminal observation: retain the original
empty Sample slots and verify that reads/pending history stay untouched. Check before [0,0],
after [1,0], complete dependent-effect token/disposition and exact replay without
another read, acquisition or launch. A Launched observation is historical policy
application, not readiness or evidence that the worker remains live. Keep original
history/pending position through explicit fixture disposal. Two subsequent ordinary
fixture workers satisfy the existing 100/3 finish contract; they do not execute the
journal obligation. Reject unsupported member, foreign context and substituted
launch token without policy mutation.

Skipped policy transition, dropped capture and corrupted capture must close both
application and history, retain Unknown and any actual captured token, and reject
retry/cancel/new admission. Distinct native assertion IDs 1078–1080 identify these
semantic controls. Positive completion stays 100/3. Test all 198 cases under the
pinned AENIN002 producer and strict 8192-byte image/4096-byte native stack limits.
Measure before consuming; preserve compile failures and unexpected runtime faults.
Compare old image bytes, retain all results, run full local checks and preserve
release/producer/worker pins and catalog. No source-closure exception is expanded.
No shared API, syscall, unsafe site, effect execution or lifecycle retirement is
introduced. Foundations O/I/E and existing Distribution/Experience scope apply.

## Preflight refinements

The first two layouts exceeded 8192 bytes (positive text 8616). Whole-token
folded comparisons and direct empty-history checks remove generic comparison
code and temporary Sample construction; every token field is still compared.
The third layout fit but assembly exposed a 4344-byte helper frame caused by
copying the 1992-byte application into its binding. The binding now exclusively
borrows both original History and Application; it does not copy either owner.
Fourth-layout sizes are 7344/7296/7232/7552 bytes. The positive has a 1072-byte
outer frame and 2456-byte helper frame, excluding saved registers/callees;
target execution, not those numbers alone, is the acceptance test. All four
preflight source snapshots, commands, map/assembly outputs are retained.

## Validation and handoff

Decision 0170 consumes the fixed Rust Launched application against original
native Driver/History. One binding exclusively borrows History and Application;
the shared full-source qualifier runs before reservation and application. Actual
launch return and policy application remain separate. Attempt zero's Launched
observation changes policy [0,0] -> [1,0] and retains the complete dependent-launch
token [1,2,3,1,0,5,1,6,7,1] with Reserved disposition. Exact replay is inert;
foreign Context, altered token and unsupported member deny before application.
There is no generated-effect execution, acknowledgment, readiness or retirement.

The positive finishes at 100/3. Skipped transition, dropped capture and corrupted
capture reject at 1078/0, 1079/0 and 1080/0 after checking retained Unknown,
closure of both owners, no retry/cancel/new admission, and the actual captured
output (including the corrupt token). Assertion 1082 distinguishes a broken
failure-retention postcondition from the designated semantic result. No terminal
sampling is needed for Launched: both primary histories stay empty and Driver
reads/pending stay unchanged through separate fixture disposal. The two ordinary
fixture workers completing the 100/3 contract do not execute the generated token.

All 198 fresh Aether cases pass. The prior 194 outcomes retain their exact expected
semantics; 190 images remain byte-identical. Four reservation images change due to
the extracted shared qualifier and are freshly exercised. All 151 ABI-6 rebuilds
remain byte-identical. New application images are 7344/7296/7232/7552 bytes;
the entire suite's maximum is 8152/8192 (the reservation positive). All ten
local gates pass in `run-eu5oc9o3`, including 287 model tests and ten Rust groups
with twelve reservation/application tests and seven omission controls. The same
core still compiles for x86_64-unknown-none; its storage/policy bounds are unchanged.

Preflights 1–2 exceed the image limit; preflight 3 fits but assembly exposes an
oversized stack frame. Full-token folded comparisons, direct empty-history checks
and exclusive borrowing remove unnecessary comparison code, Sample temporaries
and application copies. Preflight 4 and the eight-case restricted diagnostic pass
before the full consuming run. These are retained separately. The native stack
remains 4096 bytes, with no heap, new unsafe site, syscall or limit relaxation.
Stack/code measurements describe this probe, not a production resource budget.
Evidence: `docs/evidence/native-launched-application-2026-09-07/`.

Producer/worker/release pins remain unchanged; symbolic issuance/context labels
remain the fixed fixture domain and do not claim native journal issuance. Catalog
acceptance remains pending BG-056 complete producer source closure; the catalog
stays at 50 bundles/3019 historical outcomes without a new exception. This binding
supports only attempt zero Launched. Native mixed cuts, Terminal/Cleaned application,
per-attempt cleanup/reclaim evidence, effect acknowledgment and retirement remain
open. Additional OS provisioning and sibling edits remain outside this work.

Next BG-057/BG-058: qualify generated launch obligations for actual native execution
and retain their started/returned/applied dispositions before acknowledgment. A
Reserved token must never authorize replay or stand in for the worker return.
The generated dependent token has occurrence index zero, unlike the old synthetic
ISSUED[1] token at index one. Driver currently holds static issued-token references;
next work needs stable retained generated-token ownership and exact return binding,
not conversion to the old fixture token or authorization by matching service name.
Keep exact worker/resource ownership and bounded capacity; BG-060 sustained reuse
and BG-033 recovery remain separate. No kernel blocker was established.

Technical review: binding holds exclusive borrows of original History and the single policy/journal owner. The restricted attempt-zero API matches its reservation membership; revalidation is required even for replay. Unknown failure closes the source History and retains the core transaction; no recovery/reset is offered. Full token comparisons inspect every field without hashing or truncation. Empty Sample checks inspect semantic receipt/state fields rather than constructing temporary Samples. No independent reviewer sign-off is claimed. Documentation impact: storage/application contract, native coverage, quality and boundary inventories, CLI source digest and BG-057/058 handoff.

### Application-owner lifetime follow-on

The decision 0170 application owner is local to `check_native_application`: its
Reserved effect remains inspectable through application/replay checks, and the
owner's scope ends before the outer fixture disposal. This is the end of that
bounded probe, not effect retirement or permission to recreate an owner and replay.
Before executing generated obligations, keep the same application/journal owner
alive across execution, return capture, acknowledgment and any explicit retirement.
The next witness must inspect the retained obligation across those boundaries;
it must not copy a token out, drop its owner and substitute the synthetic ISSUED
entry. This lifetime extension is local BG-057/BG-058 work, not a kernel blocker.
