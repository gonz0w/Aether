# Real SDK inputs through the read-only planner

2026-09-07. Seven outcomes pass through the [implemented planner](SDK-REBUILD-PLAN.md)
using the retained 235-file SDK, actual userland link-input receipts and actual
io_probe ELF bytes. This extends the [earlier record experiment](SDK-STATIC-BINDING.md)
with the explicit KV binding and real helper invocation. No compiler, native
program, update, replacement or service operation ran here.

[Evidence](evidence/sdk-real-plan-2026-09-07/README.md) retains 46 commands, exact
source identities, both consumer records, bindings and complete reports. All seven
planner invocations preserve both input roots; the three retained source roots
and all selected source-file hashes also remain unchanged.

| Case | Exact outcome |
| --- | --- |
| Same SDK | Exit 0; complete report with no requalification rows |
| Changed archive/SDK observation | Exit 0; sdk-static-probe direct and probe-workload transitive; unrelated-data excluded |
| Separately recorded relink bound to changed SDK | Exit 0; no requalification rows |
| Missing binding, same and changed candidates | Exit 1, empty stdout, expected regular input diagnostic |
| Stale binding, same and changed candidates | Exit 1, empty stdout, stale SDK binding diagnostic |

The real ELF is stored as 0644 data. probe-workload and unrelated-data are synthetic
scope markers, not proposed base packages. The new bindings explicitly wrap the
retained input receipts; their content is opaque to the planner. Ordinary package
state verification passes the missing/stale roots, but the planner rejects them.
Registration observation metadata includes an unvalidated minimal sbom_ref document,
not a complete or SPDX-conformant SBOM; it supplies no release qualification.

The baseline and rebound ELF hashes are equal while their input receipts and
consumer records differ. The selected candidate SDK record also includes advisory
observation metadata; its identity is not an ABI-only fingerprint. Copying its old
profile receipts neither authenticates nor admits the modified archive.

## Retained handoff

Workspace: `/Users/cam/DEV/pkg-mgr/work/sdk-real-plan-kie24pa6`.

- `installed`: freshly imported baseline SDK, KV-bound real consumer and scope markers.
- `same-sdk`: exact baseline SDK-only copy.
- `changed-sdk-observation`: exact retained changed SDK record/stage, SDK only.
- `rebound`: changed SDK plus the separately evidenced relink's new consumer binding.
- `missing` and `stale`: valid state records deliberately lacking valid SDK bindings.

[Result](evidence/sdk-real-plan-2026-09-07/result.json) supplies exact record pins;
[commands](evidence/sdk-real-plan-2026-09-07/commands.json) supplies runnable paths
and arguments. [Changed report](evidence/sdk-real-plan-2026-09-07/changed.tsv) is
an observation, never an apply token. Consumers must select pins independently
and use the helper's exit status before accepting report bytes.

## Current owner evidence and review boundary

Userland's [matched SDK-08 result](../../userland/docs/evidence/sdk08-matched-2026-09-07/README.md)
now reports two successful generations with positive reclaim, plus the exact
withheld-memory-grant denial against the matched historical producer. Its reported
ELF hash equals the ELF used here. Denial-side native reclaim is explicitly not
shown. That bounded result supersedes the earlier mismatch/NOT RUN checkpoint;
it does not qualify the current kernel or a complete native package workflow.

Userland also [reviewed the earlier direct record witness](../../userland/docs/evidence/sdk-package-review-2026-09-07/README.md).
[Local checkpoint](evidence/sdk-real-plan-2026-09-07/owner-checkpoint.json) pins the
read documents and verifies the old result/ELF identity edges. We did not rerun
native tests or invent independent approval. That earlier review does not cover
the new KV format and planner automatically.

Ready for producer/reviewer inspection: the canonical KV/report contract, the
installed/rebound bindings and records, the seven outcome receipts, and their
explicit observation limits. Review whether the retained input receipt is adequate
for this bounded consumer and record disposition of the new package-owner format.
Userland owns its [UL-005 review packet](../../userland/docs/quality/SDK-REVIEW.md);
no sibling packet was changed or review request sent. Independent acceptance,
complete build-input policy, SDK update/apply and broader native qualification
remain separate. No release pin or shared standard changed.
