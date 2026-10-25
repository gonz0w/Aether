# 0090 — Native init capacity consumer

Plan, 2026-09-06; BG-058 / Aether SI-05 following decision 0089.

Review and explicitly pin the delivered AENIN002 / ABI 15 producer packet. Add an
opt-in consumer profile with its exact bootstrap ABI, 8192-byte linker limit and
LARGE PASS/CLOSED markers; preserve default ABI 6, linker bytes, envelope and
oracles. No new authority or lifecycle operations are introduced. Code remains
allocation-free and immutable RX; stack stays one page RW/NX. Normal completion
is not supervisor reclamation. Shared O/I/E rules and Distribution ownership stay
unchanged; this is a local experimental contract adoption, not a shared release.

Retain a normalized producer packet with traceable original source/report/envelope
hashes for the existing harness. Verify source archive members and pinned boot
inputs before consumption. Explicit profile selection must reject the other
profile, wrong magic, oversized images and substituted receipts. Test these
boundaries on the host and execute all 151 existing semantic cases against the
fresh pinned producer. Preserve legacy build behavior and historical evidence.
No producer-only result counts as independent sys-init acceptance. Retain all
attempts, exact commands, source/tool hashes, raw logs and full local checks.

After successful profile refresh, qualify the retained conflict guard separately;
its five proposed cases, construction denial and closed reoffer remain open until
executed. Do not merge profile acceptance with unexecuted guard claims. No sibling
source or standards pin changes. Update adapter/coverage, quality and planning
records with actual results; run all nine development gates before completion.

## Results and next work

Decision 0090 accepts the explicit AENIN002 / ABI-15 profile for the existing
151-case sys-init workload. All 151 cases pass in a fresh independent target run
(457 commands, 421 frozen inputs unchanged). Exact old semantic assertions are
preserved; only the producer-defined LARGE PASS/CLOSED markers differ. All 151
ABI-6 images also rebuild byte-for-byte identically under the default profile.
The new profile has an 8192-byte bound; these refreshed images still use at most
4096 bytes. Second-page protection/cleanup evidence comes from the pinned producer;
this consumer run does not yet execute a larger guard image.

SI-05's profile dependency is now available and the compatibility refresh passes.
Next BG-058: integrate the retained conflict guard under the explicit large profile,
run all 151 regressions plus its five proposed cases, then qualify construction
denial and closed reoffer. Guard lifetime/physical capacity and PH-05–07 remain
open; profile acceptance does not accept that guard or close the whole SI-05
consumer handoff. No sibling source or shared standards pin changed.

The first native run passes without a runtime retry. A packaging-only check first
compared catalog order with execution order and failed; comparing the unique case
names confirms identical semantic oracles. That script/failure and its corrected
capture are retained. The offline audit now covers 2360 historical outcomes in
46 bundles, including this new 151-case witness. Five producer-input tests and
twelve audit tests cover explicit profile bounds and substitution/mixed markers;
all 42 harness tests pass. The native client retains the same allocation, FFI,
cleanup and operation boundaries; no writable global or new dependency is added.

Validation: all nine development gates pass in `out/checks/run-x4_z02iw`,
with no skipped gates and unchanged checked inputs. All twelve current consumer
source files match the fresh target snapshot; the legacy linker hash is unchanged.
The offline native audit covers 2360 historical outcomes across 46 bundles.
Full logs, host sample artifacts and final adoption records are retained in
`docs/evidence/native-init-capacity-consumer-2026-09-06/`.
