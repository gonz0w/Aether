# SDK review-packet preparation

2026-09-07. [Review entry](../../SDK-REVIEW.md).
[Original selection](inputs.json) binds 49 local/producer files to exact hashes at package
base commit 278f0da. These are review identities, not new release pins. The files
remain at their recorded locations; this is not a self-contained source archive.
Missing or changed inputs require inspection, not silent substitution.

[Assembly](assembly.json) records a passing one-shot identity audit using
[the observation source](assemble.py). All seven stored planner outcomes have
expected statuses and selection rows; their source identities still match; the
ELF identity matches the producer's native report. No native workload or package
command was rerun, and no independent approval follows from these checks.

[The decision record](decision-template.txt) is deliberately blank. It separates
producer agreement with the new interface from independent technical acceptance.
Cam's assignment to perform reviews is not a completed review. Existing target
representation approval remains in force and is not requested again here.

The packet does not authorize SDK update/apply, rebuilding, services, release
publication or editing producer-owned acceptance documents. Reader walkthrough,
source authentication, native package execution and denial-side native reclaim
remain separately scoped. No sibling, runtime or immutable release changed.

## Explicit revision 2

The [failed final check](failed-final-check.json) detected a concurrent userland
review-packet update and prevented staging. Its new local preflight section was
read alongside the referenced evidence; acceptance remains pending.
[Revision 2](inputs-v2.json) explicitly selects 52 inputs, including that evidence
and exact text copies of both owner documents. [Assembly result](assembly-v2.json)
records the new selection. The first selection, assembly and original local
[review entry](review-entry-v1.txt) remain intact. No failed check was erased and
no updated producer document was silently treated as the earlier reviewed bytes.

[Final revision-2 checks](checks-v2.json) confirm all 52 selected input hashes
still match and retain the passing documentation, standards and whitespace gates.
