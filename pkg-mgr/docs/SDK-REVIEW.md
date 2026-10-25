# Bounded SDK handoff review packet

Prepared for Cam and the userland producer/reviewer, 2026-09-07. **Review pending.**
This packet selects the current package-owner evidence at base commit 278f0da.
It is not a release candidate, published standard, reviewer decision or approval.
[Exact review inputs](evidence/sdk-review-packet-2026-09-07/inputs-v2.json) bind the
selected source, contract and result bytes. A change to an input requires review
of that change; a newer checkout does not silently replace this selection.

## What is ready to assess

One explicitly pinned musl SDK can be transported as private build-input data,
recovered under the existing retained-stage rules, and used to record static
consumer inputs. The read-only planner rejects missing/stale bindings and reports
conservative reverse dependents. It changes no package state and provides no build
ordering, SDK replacement or service authority.

The exact target representation and literal unrecorded historical host fields
were already accepted in userland's [target decision](../../userland/docs/SDK-TARGET-DECISION.md).
This review does not reopen those settled choices or request Apple qualification.
The new matter is the KV binding/planner contract and its bounded integration
with the retained producer receipts. The prior JSON experiment's owner review is
supporting evidence, not automatic approval of this new interface.

## Read in this order

| Read | What to check | Evidence boundary |
| --- | --- | --- |
| [Target/profile](SDK-PROFILE.md) and [transport](SDK-TRANSPORT.md) | Full target pin versus native receipt hash; caller-selected descriptor; separate build-input role | Profile identity is not native/source authenticity |
| [Real transport](SDK-REAL-HANDOFF.md) | 235 files, exact records/modes, six denials and retained-stage recovery | Real private SDK; not physical durability or changed-SDK admission |
| [Planner contract](SDK-REBUILD-PLAN.md) | Seven ordered KV rows, direct binding requirement, whole-record comparison, transitive scope, cycle termination, limits, no partial validation report | Existing state verify alone does not enforce this binding |
| [Planner implementation evidence](evidence/sdk-rebuild-plan-2026-09-07/README.md) | Failed attempts, 46 controls, full suite and exact dirty inputs | Synthetic cases; not every maximum bound or hostile race |
| [Real planner handoff](SDK-REAL-PLAN.md) | Seven outcomes, exact reports and preserved roots; identical ELF with changed inputs | Real SDK/ELF plus synthetic transitive/unrelated markers |
| [Userland review packet](../../userland/docs/quality/SDK-REVIEW.md) | Imported-SDK link and matched native positive/denial evidence for the same ELF | Producer-owned acceptance; denial native reclaim not shown |

The producer packet's earlier future-planner wording is historical relative to
this packet. Its technical review covers the earlier direct record witness; no
new producer disposition has been recorded for the KV helper. Do not modify that
owner's packet here or infer consent from the cross-reference.

Userland concurrently added [receipt-preflight evidence](../../userland/docs/evidence/sdk-preflight-2026-09-07/README.md):
bounded JSON intake, explicit evidence-storage failures and a repeated startup link
with unchanged ELF. This is reported producer evidence, not a native rerun or new
KV/planner disposition. The first local packet failed its final identity check on
that owner-document change. Revision 2 explicitly selects the reviewed addition;
the original selection and failed check remain in the evidence directory.

## Concrete comparison

The [changed report](evidence/sdk-real-plan-2026-09-07/changed.tsv) must select
sdk-static-probe as direct and probe-workload as transitive, excluding unrelated-data.
The [same report](evidence/sdk-real-plan-2026-09-07/same.tsv) and
[rebound report](evidence/sdk-real-plan-2026-09-07/rebound.tsv) have no selection rows.
All successful reports still contain their full input identities.

Compare [installed binding](evidence/sdk-real-plan-2026-09-07/installed-sdk-binding.kv)
with [rebound binding](evidence/sdk-real-plan-2026-09-07/rebound-sdk-binding.kv): SDK
record and input-receipt hashes differ while the artifact hash is equal. Decide
whether the producer's opaque receipt is adequate for this single consumer. The
planner does not parse it or prove complete compiler/header/adapter/option closure.

[Command receipts](evidence/sdk-real-plan-2026-09-07/commands.json) retain all seven
actual planner invocations, their complete output and exact statuses. Missing/stale
bindings reject even for an unchanged candidate after ordinary state verification
has succeeded. To repeat an invocation, use its exact five arguments in a quiesced
retained root; compare its complete stdout and status. The roots are local evidence,
not portable release artifacts. Missing roots are unavailable evidence, not permission
to substitute new inputs or regenerate identical-looking approval receipts.

## Record disposition

Use [the blank decision record](evidence/sdk-review-packet-2026-09-07/decision-template.txt)
to record actual reviewer identity, UTC date, reviewed input-manifest SHA-256,
role, findings and bounded disposition. No fields have been preapproved.

The package-owner interface needs an explicit producer disposition of strict KV
bindings, whole-record invalidation and conservative transitive requalification.
Independent technical acceptance of the bounded handoff must name the reviewed
scope and unresolved limitations. These decisions may be made by the appropriate
reviewer but must not be conflated with release publication or reader testing.
Any finding needs an owner and a concrete correction or documented remaining gap.

SDK update/apply, automatic rebuilding, complete receipt policy, current-kernel
package execution, denial-native-reclaim, source authentication and release
assembly remain separate work. Do not reopen these merely to mark this packet
accepted. Existing pins, release bytes and the independent-review gate remain
unchanged. This packet is author preparation, not an uncoached reader walkthrough.
