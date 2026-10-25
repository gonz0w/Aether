# Maintaining Aether on GitHub

This guide describes the intended public repository workflow. Record actual
configuration, verification and remaining gaps in the canonical onboarding issue;
this checklist is not a second work queue.

The repository is [gonz0w/Aether](https://github.com/gonz0w/Aether). The
[onboarding issue](https://github.com/gonz0w/Aether/issues/1) records source/history
selection, actual settings readback and remaining manual steps. This guide is an
operator procedure, not a claim that every setup step has already completed.
The [legacy routing index](WORK-INDEX.md) maps imported IDs without duplicating
live issue state.

## Publication boundary

Publish only the approved curated source snapshot for this system repository:
the kernel, `userland/`, `sys-init/` and `pkg-mgr/`. The accepted local consolidation
is `0c84f5463abeb25b9cb776ad6d52d41e02f979d7`; its selection does not authorize
uncommitted AF09 work or every file in the large historical tree.

Review the exact curated file manifest and its license/provenance audit. Exclude
credentials, downloaded SDK/source bundles, prepared images, generated binaries
and full build/evidence archives. Keep deliberately selected small regression
fixtures and non-standards dependency pins distinct from generated evidence.
Standards content, including all vendored releases and review snapshots, remains
private; consumer adoption prose and lock hashes do not publish that content.
Do not publish embedded copies of private companion repositories as incidental
files.

Keep all original local repositories, working files, history and recovery refs.
A public snapshot does not require rewriting them. Publish only explicitly
approved refs; do not push all branches, migration refs or a mirror. Record the
public snapshot's identity honestly rather than claiming that it contains all
local history.

Standards content and the standards, distribution, installer and origins companion
repositories remain private. Imported Git hooks also remain private. See the
maintained [public-source boundary](PUBLIC-SOURCE.md). This hosting step is not an OS release, a native qualification run or
permission to publish a companion project. [LICENSING](LICENSING.md) summarizes
this consumer's terms; upstream license texts remain authoritative for imports.

## Public checkout boundary

The proposed public default is a new clean `main` from the approved curated
snapshot. This does not merge the private consolidation into local main. Original
local main `78c13fc5f5329bb590c2ab4772f2e1e2372dc067`, private historical refs and
unaccepted AF09 work remain untouched. Local consolidation IDs are provenance,
not public ancestors or evidence that excluded history was published.

Once bootstrap is accepted, ongoing public work must start from public `main` in
a separate public clone, or a worktree of that clone. A worktree of the private
historical repository still shares its refs/objects and is not the public base.
Never push private historical branches, legacy/migration refs, all refs or a
mirror. Port reviewed changes explicitly as audited patches/file changes onto
the public base; inspect the exact resulting tree and approved ref before push.

Public summaries exclude the local qualification receipts they may cite. The
obsolete whole RC1/ADP-01 packet and all standards release/review byte closures
remain private. Consumer adoption records and lock hashes alone are retained. Required unavailable evidence stays
blocked coverage. The native-home broad host aggregate keeps its 300-second bound
where selected; hosted source-integrity/model jobs do not replace it, grant another guest,
or waive source freeze, stop-on-failure, cleanup or separate review.

## Access and maintenance settings

Apply and read back the actual settings before describing them as enforced:

- Make the selected repository public and enable Issues, Discussions and the wiki.
- Keep the owner as the only identity with write access. Public bug reports and
  discussions remain welcome.
- Select collaborator-only pull request submission where GitHub exposes it, with
  no other write collaborators. Check the result from an account without write
  access. If the setting is unavailable, record that gap; a contribution policy
  or CODEOWNERS file alone cannot enforce it.
- Restrict wiki editing to collaborators while keeping it publicly readable.
- Enable private vulnerability reporting and verify the **Report a vulnerability**
  route used by [SECURITY](../SECURITY.md). Do this before advertising the route.
- Protect the confirmed default branch against force pushes and deletion. After
  the bootstrap workflow has run, require pull requests and its exact required
  check names. Require conversations to be resolved.
- Keep a solo maintainer able to merge their own reviewed change: do not require
  an impossible self-approval or mandatory code-owner approval. Separate project
  review is still recorded in the PR/issue; a protection setting is not that review.

[CODEOWNERS](../.github/CODEOWNERS) names responsibility and notification routing.
It neither restricts PR authors nor proves review. Record any platform/plan limits
and necessary manual steps instead of treating a requested setting as configured.

## One live work authority

After verified migration, GitHub Issues own live scope, priority, dependencies,
ownership and continuation under the pinned
[GitHub work profile](../.agent-temper/profiles/github.md). During the bootstrap,
its single owning record remains authoritative until that handoff is verified.

Link durable contracts and evidence from issues. Preserve stable UL/BG identifiers
as references to prior work. Convert local live indexes to issue links or clearly
historical snapshots; do not maintain competing status queues in Markdown or the
wiki. GitHub Projects may display issues without introducing conflicting state.

Use exactly one of these progress labels for each open executable issue:

| Label | Meaning |
| --- | --- |
| `status:backlog` | Proposed work that does not meet start conditions |
| `status:deferred` | Explicitly deferred, outside current authorization |
| `status:ready` | Bounded, understood, authorized and unblocked |
| `status:in-progress` | An identified owner is implementing it |
| `status:blocked` | A named dependency or decision prevents progress |
| `status:review` | Ready for required examination |

Create these labels before enabling the issue forms, which start proposals in
backlog. Closed issues have no active progress label and state the closure reason.
Coordination epics describe child work and exit conditions rather than pretending
to be one executable task. Keep distant work coarse. Record the actual priority
convention and ordered capability milestones in the canonical issues.

A ready implementation issue names its outcome, non-goals, acceptance, checks,
prerequisites and owner. Record concrete blocking relationships or an explicit
`Blocked by #NUMBER` statement. Resume active work/reviews before duplicating it.
Research deliverables need not invent a code PR.

Owner PRs explain the problem, resulting behavior, executed evidence, missing
coverage and material risks. Use `Closes #NUMBER` only for fully satisfied executable
issues. Do not auto-close epics, partial work or later operational gates. Close
implementation work on accepted merge, then reconcile dependent readiness and
milestone exit conditions.

## Initial source import

Preserve selected original source and fixture bytes when creating the first
public snapshot. The reviewed local import check reports35 whitespace findings
in10 unchanged legacy files, including intentional prompt bytes and patch
context. Do not reformat these to make a new repository's initial diff look new.

Before the bootstrap commit, independently verify every exception against the
original Git blob, check all new/edited files with the normal whitespace rules,
and run the full staged secret/name/size gate. Retain the original failed check.
Only a separately reviewed, one-command initial-import exception may change that
single invocation's whitespace settings; the maintainer runs the existing
private import hooks externally and future commits retain their normal checks.
Public contributors review diffs/tree/message and run affected checks and CI;
this checkout does not include hook installation. Do not install a persistent
suppression or use this exception to hide a new change. Record the exact initial tree/message
and review in the onboarding issue before publishing.

## Hosted checks and their limits

Use standard free hosted runners, explicit read-only default permissions and
pinned action revisions. Keep jobs bounded and cancel superseded runs. Do not add
secrets, paid runners, deployments or automatic releases for this onboarding.

The planned CI jobs are **Source integrity** (Agent Temper digests, selected
Python syntax/JSON and conventional PR titles) and **Kernel models** (25 tests
across four pure Zig roots). They must run from the curated public tree without
private standards or SDK/service deliveries. They do not check standards pins.
Do not substitute `zig build test`, a full component aggregate or a broad
other-OS campaign when those inputs or qualification are absent.

Check code only from the intended trusted source/event. Do not execute issue
text or use privileged `pull_request_target` execution to run contributed code.
Read back workflow permissions and run the actual published workflow before
making a passing CI claim. A green source/model job establishes only that named
check on that source; it does not establish native execution, persistence,
recovery, installed packages or an assembled release.

## Reader routes

The README is the entry point. CONTRIBUTING routes bugs and bounded requests to
Issues, open questions to Discussions, and vulnerabilities to private reporting.
The wiki is a short navigation aid; technical contracts and evidence stay in
versioned source. Publish the supplied `Home.md`, `_Sidebar.md` and `_Footer.md`
only after their repository/default-branch links are confirmed.

Before closing onboarding, independently review the curated source and notices,
check public links, read back settings, verify migrated issue coverage, and retain
the hosted check result and exact public source identity. Keep unresolved limits
in the owning issue. Hosting completion does not close the OS release gates.
