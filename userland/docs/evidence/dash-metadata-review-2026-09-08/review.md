# UL-007 metadata consumer review plan

2026-09-08: review the completed documentation-only producer packet with manifest
0985952be1fb7a9ee589076be3b3eff2d92e4d6b74129edb54198bd157bb87af.
No completed runtime delivery is recorded. Do not consume moving implementation,
rerun unchanged 295 cases or create another startup probe. Preserve existing
pins, sibling ownership, raw unsupported semantics and native authority.

Applicable: already-read PROCESS/change-review, Foundations O/I/E, Distribution
NC/PX/ID, adopted TD/TC/TE/CP and documentation DW/DS/DP. Review AECAT002 admission,
version negotiation, all-fields publication, source provenance, tuple reuse and
zero-ID authority denial. Record local expectations using existing UL-007 and
workload handoff, not a competing shared standard.

Verify sealed packet/archive input hashes before review. Compare pinned upstream
dash var.c/main.c with the reference archive. Use the pinned LLVM nm to inspect
the existing main object and the recorded target/options to inspect predefined
macros without headers, linking or native execution. Require matching object and
compiler hashes, checked exits, bounded 30-second owned processes and complete
cleanup under build/. Retain raw inputs/outputs/commands and all failures.

The source's !linux ENV identity guard needs explicit configuration assessment;
source text alone does not establish that the compiled guard exists. Metadata
initializer qualification remains separate from actual-main/ENV behavior.

Simplicity: inspect existing source/objects and publish an acceptance checklist.
No new decoder, runtime facade or account service is needed. No active paths are
removed; existing reference inputs and native evidence remain immutable. Broader
source audit, independent technical/reader review, UL-016 and full M3 stay open.
Run python3 -B docs/quality/check.py after updating planning/coverage. Final findings
and evidence belong in README/results; this plan does not claim native progress.

## Actual review disposition

Codex checked the captured descriptor decoder, startup readiness/failure oracle,
metadata proposal and pinned upstream initvar/main source. Four sealed packet
files and twelve archived inputs verify. Two owned static-inspection commands
pass with cleanup; target macros and exact object imports confirm that the source
ENV identity condition is excluded in the retained Linux reference main.o.
The consumer checklist and separate full-main configuration gate are recorded.
No runtime implementation, host/kernel regression rerun or metadata acceptance
is inferred. Independent technical/reader sign-off remains pending. This review
found no need for another startup program or a new metadata decoder in userland.
