# Home activation — 2026-10-24

[FS-HOME-ACTIVATION](../../proposals/FS-HOME-ACTIVATION.md) owns requirements,
status, review and continuation. From `userland/` run
`PYTHONOPTIMIZE=1 python3 -B experiments/filesystem-service/check-home-activation.py`.
The actual Owner/service/client and wrapper execute against synthetic storage and
host channels. Target libraries and existing x86_64 native-entry compatibility
compile; no native trap, matched home entry, engine fit, guest or authority proof.

## Attempts

| Attempt | Observation |
| --- | --- |
| [01](attempt-01.json) | Pre-production compiler red: existing wrapper deliberately rejects AF09 (E0080) and root service::run is absent (E0425). New six-case fixture is written but cannot compile yet; no semantic runtime-red claim. |
| [02](attempt-02.json) | Selected libraries build; fixture must import Rights explicitly after the old-only import is gated. |
| [03](attempt-03.json) | Fixture Rustc passes; Clippy requests direct Result.expect instead of ok().expect. |
| [04](attempt-04.json) | All six cases and first two semantic controls pass. Latch omission makes Failed an unused variant, so it does not compile; keep an inert variant construction and require actual named latch rejection. |
| [05](attempt-05.json) | Six cases/four compiling controls and preceding home producer checks pass. Checker incorrectly builds x86 trap assembly on the arm64 host. Scope actual entry checks to x86_64; preserve host generic API denials. This is not a product portability task. |
| [06](attempt-06.json) | Pass190 children on corrected target selection: six cases/four controls, old AF07/08 three-case wrappers, home producer regressions and explicit guards. |
| [07](attempt-07.json) | Final pass190 with clearer no-matched-home-entry scope and recorded generated selected/old activation-library hashes.167 source inputs/three tools/three native Rust libraries verify; owned generated outputs removed. No production change since06. |

The six cases cover actual two-grant Client connect, one home write/readback and
system-write denial; eight invalid-source/epoch arrangements with no publication
or transport; first/second send loss;20 malformed greeting rows; original negative
and normalized positive callback failures; ordinary replies after both grants and
failure latching/no second publication. Raw channel closes[-7,-8] stay separate
from nominal client[0,0], backend Drop and native settlement. Nominal service thread
joins; omission controls terminate normally with101 and their exact named marker.
No fixture lock is held across a failing assertion that could poison backend Drop.

Four new control recipes reject publication before attachment, wrong home-token
acceptance, lost failure latching and ignored callback status. Six inherited home-
wire controls and old default/AF05/06/07/08/sealed paths remain. Actual native entry
positive checks and unmatched-entry denial compile only for x86_64-unknown-none;
host generic probes separately enforce API absence. An AF09 native entry is still
absent. No old seal, wire, result ABI, kernel flag, quota or resource ceiling changes.

One300-second cumulative owned-process budget includes the predecessor gate.
All commands, short diagnostics, source/tool/interpreter/native-library hashes and
control recipes are retained. The selected and old activation-library hashes
identify generated outputs that are disposed, not retrievable binary bundles.
Reconstruct controls from their recorded one-replacement recipes; no per-run source,
SDK or binary archive remains. Existing source-owned dependencies remain separate.

The earlier owner22 frozen inventory now differs at activation.rs and the new
files. Its actual owner compile/link closure does not import activation; those
core sources and flags are unchanged. Reuse the unaffected component code/fit
result after that impact review, not as a fresh all-input or complete native-engine
qualification. The changed activation and its old/new wire guards are covered
here. The next engine/helper/image handoff must build and measure its actual
selected closure again. Later home/file creation also needs retained pre-greeting
mutation receipts through failure/export. This wrapper performs no bootstrap
mutation and adds no Runtime field.


[CLI/quality02](cli-quality-attempt-02.json) passes six CLI and four owned quality
reference children. [01](cli-quality-attempt-01.json) preserves the disposable
capture wrapper's missing binary-buffer error; no product or runtime failure is
claimed. Exact owned output roots were removed after retaining child outcomes;
preexisting quality roots remain untouched. Workflow41/37/190 and whitespace pass.

[Separate review](peer-review-checks.json) verifies all167 inputs, tools/libraries,
190 child outcomes, ten control recipes,24 reader links/anchors, cleanup and the
limited unchanged-owner-closure impact rationale. It records source identities,
resolved checker findings and runtime/model/native limits. No native or release
acceptance or exact routing metadata is inferred.
