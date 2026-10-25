# Native Launched application — 2026-09-07

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

witness/ retains pinned producer/worker, thirteen frozen consumer inputs, case images/envelopes and raw logs. Exact commands and ISO hashes are retained; generated ISOs stay in private out. restricted-diagnostic/ is the eight-case pre-run, not full acceptance. Preflight directories retain size failures and stack diagnostics. validation/ and rust/ retain local source/tool/test records; legacy-build/ is compile equivalence only. adoption/ freezes this handoff and sha256.json seals the package.
