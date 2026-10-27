# Aether integration policy

Canonical sections extracted from [PROJECT](../../PROJECT.md). Local policy is
bound to the containing source revision; external pins retain their own identities.
Existing owner change authority and all applicable contracts remain in force.
Commands and literal repository paths below keep their original working directory;
only Markdown links were rebased for this file.

## Source control and integration authority

Public `main` is a new clean root from the approved curated snapshot, once
bootstrap is accepted. It is not a merge into or fast-forward of the original
local main. The original local main
`78c13fc5f5329bb590c2ab4772f2e1e2372dc067`, accepted private consolidation
`0c84f5463abeb25b9cb776ad6d52d41e02f979d7`, private branches, Git/JJ metadata and
unaccepted AF09 work remain untouched and local. These IDs describe local
provenance, not public ancestors or a claim of public replay.

Ongoing public work starts from the new public `main` in a separate public clone,
or a worktree of that public clone. Never use a branch or worktree of the private
historical repository as a public working base. Do not merge/push its branches,
legacy/migration refs, all refs or a mirror. Port an explicitly reviewed change
as an audited patch/file change onto the public base; review exactly what will be
published. Preserving local history does not authorize publishing it.

Use descriptive `codex/` branches and record the exact reviewed public base and
intended target in the issue. Only the repository owner opens PRs under the
current contribution policy. Keep public issue creation available. Configuration
must be verified before claiming technical enforcement; CODEOWNERS is routing,
not a PR-author restriction or review result.

Preserve configured author/signing choices. Use coherent `type(scope): summary`
commits, optional scope, subjects at most 72 characters and a blank line before a
substantive body. Never invent signatures, sign-offs, reviewers or execution.
Review working/staged diffs with `git diff` and `git diff --cached`, check the
actual proposed tree/message, and run required affected checks and public CI.
Imported hooks remain private; this public checkout has no hook-setup command. Configure only
the owner-approved public destination; ordinary local integration grants no new
remote, credential or publication authority.

Before integration, satisfy acceptance, affected checks and separate review of
the proposed change. The 2026-10-23 owner decision allowing peer-agent reviews
remains: ordinary implementation/documentation may use a separate peer agent;
required specialist or affected-owner review still applies. An implementer's
check is not independent review, and an agent review is not human runtime assurance.
Record source identity, reviewer type, findings, resolutions, evidence and limits.
The integrating agent may perform pre-merge checks under these conditions.

A solo-owner branch rule with zero mandatory GitHub approvals avoids impossible
self-approval. It does not waive project peer review. Confirm the target still
matches the reviewed base and the resulting tree matches the verified candidate.
Resolve changed inputs/conflicts and revalidate affected evidence/review. Verify
final identity and reconcile the canonical issue after accepted merge. Never
integrate an unreviewed older branch, discard another contributor's work or renew
native-run permission through onboarding.
