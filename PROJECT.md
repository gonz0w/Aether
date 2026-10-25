# Aether engineering policy

This file records engineering policy for the kernel root, `userland/`, `sys-init/`
and `pkg-mgr/`. [Product direction](.planning/PROJECT.md) and
[architecture](docs/ARCHITECTURE.md) retain product/runtime authority.
[GitHub operating guidance](docs/GITHUB.md) describes this public consumer's
hosting and work routing. The local AT-001/AT-002 records preserve earlier method
and routing decisions; their historical branch targets are not public assignments.

## Public onboarding cutover

The owner authorized `gonz0w/Aether` with a new clean `main` from the reviewed
consolidation `0c84f5463abeb25b9cb776ad6d52d41e02f979d7`, curated source and
compact evidence, excluding AF09. Standards content remains private too.
The initial public commit is `8218ce23c0dd06f16c383374d3bb4aaca849c7bf`;
its separate review, actual hosted checks and settings readback are recorded in
[onboarding issue #1](https://github.com/gonz0w/Aether/issues/1).

The verified source and tracker cutover takes effect when the onboarding
completion PR merges. GitHub Issues are then the sole authority for live work,
priority, dependencies, ownership and continuation. All 52 planned-work issues
were reconciled against the retained legacy IDs before that handoff. This is
repository onboarding, not an OS release or native qualification.

Private AF09 work keeps its original scope, authority, pending gates and local
artifacts. It must be ported through a separately reviewed public PR after its
integration prerequisites are satisfied; this cutover neither completes nor
renews it. Do not select new public work from a historical queue.

After cutover, `.planning/STATE.md` is compatibility navigation to Issues and
contracts. Component STATE, BACKLOG, PRIORITY and captured-story files are
read-only historical context, not parallel sources of live status or priority.
Preserve their stable UL/BG/package IDs and link their durable contracts from the
canonical issues. This changes tracking, not product commitments or acceptance.

After cutover this explicit owner-approved Issues routing supersedes older
Markdown/STATE selection and status-update instructions in component guides.
Their domain, verification and approval requirements remain binding. In those
guides an “owning work record” means the canonical issue, not a revived local
queue. This is a scoped policy change, not a file-order precedence rule.

## Method and local contracts

Use the [Agent Temper method](.agent-temper/METHOD.md), pinned at
`c07af93dc99e770bf4f3ec6f30a0536cb2ae14c5`. Its
[source record](.agent-temper/SOURCE.md), [complete manifest](.agent-temper/SHA256SUMS)
and [license](.agent-temper/LICENSE) identify the unchanged import. This consumer
selects the [GitHub profile](.agent-temper/profiles/github.md) for work routing
under the cutover above and the [Codex profile](.agent-temper/profiles/codex.md)
under the role mapping below. Strict test-first remains unselected.
The pinned bundle's earlier selection notes are import history; this file owns
current consumer selection. Do not edit bundle bytes to record that selection.

[Shared Aether standards](docs/STANDARDS.md) retain domain authority through
existing immutable released pins and the identified local adoptions. The
[development process](docs/DEVELOPMENT.md), [repository guide](docs/REPOSITORY.md)
and affected component contracts remain binding. A mutable sibling checkout
cannot silently replace a pin or requirement. Ordinary public documentation and
self-contained model work follow the available local policy and affected
contracts. A change that depends on private normative inputs needs the owner and
the exact applicable inputs before that dependent work can proceed; public
onboarding neither waives the requirement nor republishes those inputs.

Apply compatible stronger requirements together. Focused testing and
[compact retention](docs/DEVELOPMENT.md#evidence-and-failures) supersede older
competing archive recipes, without relaxing contracts or release gates. The
public snapshot excludes local qualification receipts, full evidence bundles,
SDKs and the obsolete whole RC1/ADP-01 review packet. Historical prose or a digest
does not make missing bytes available for replay. Standards releases, review
snapshots and imported Git hooks remain private under the owner's decision.
Retained consumer adoption records and lock hashes do not include those bytes.
See [PUBLIC-SOURCE](docs/PUBLIC-SOURCE.md) for the maintained availability boundary.
A required missing packet, runner or review remains blocked coverage.

An unresolved required choice or policy conflict blocks dependent work for owner
Q&A; continue independent work. Record authorized decisions before relying on
them. The owner decides product, support, languages, consequential architecture,
authority, resource exceptions and policy changes. Agents resolve routine details
inside accepted scope. File order or upstream recency cannot override a requirement.

## Bounded Zsh application trial —2026-10-25

The owner approved implementing and host-testing the separately reviewed
[application profile](https://github.com/gonz0w/Aether/issues/69): a distinct
1.5 MiB application ELF cap, 384 image-plus-existing-stack pages and 640 total
backing pages in each of five fork-capable application slots. The engine retains 8192 pages and
the owner retains 128. This assigns 45 MiB within the existing 64 MiB backing
reservation; 19 MiB remains ungranted. The selected application image window is
`0x200000..0x400000`. Existing capability, TLS, stack/bootstrap and ownership
checks remain binding; older profiles retain their defaults, selectors and seals.

At the admitted image limit, at least 256 backing pages remain for all later
runtime allocations, including TLS and allocator overhead. This is a bounded
trial resource decision, not evidence of Zsh heap/stack sufficiency. Routine
implementation and host verification follow the finite issue scope, required
checks and separate review. No guest, native prompt or ISO qualification is
authorized by this decision. Exact SDK/artifact qualification evidence stays local.

## Settled choices

| Area | Decision and canonical reference |
| --- | --- |
| Product | Experimental Aether-only capability multikernel and services. Preserve [product direction](.planning/PROJECT.md), core-local ownership, minimal kernel authority and explicit service boundaries. Host tools are development inputs. |
| First release | [R1](.planning/ROADMAP.md#r1--first-release-persistent-boot-to-shell-system): sys-init into interactive serial Zsh, runner, persistent OpenZFS behind the Rust filesystem service, native packages and assembled-system qualification. Bounded fixtures, dash or a RAM-only prompt do not substitute. |
| Stack | Zig kernel, Rust services, existing C/musl/OpenZFS and host Python/shell roles. [Pinned setup](boot/DEPENDENCIES.md) and [source conventions](docs/DEVELOPMENT.md#source-conventions) own versions and flags. No language migration or generic framework follows from onboarding. |
| Work | After verified cutover, GitHub Issues own live scope, priority, dependencies, ownership and continuation. Keep stable legacy IDs and domain contracts. No second live queue or workflow runtime. |
| Verification | Use [focused checks](docs/DEVELOPMENT.md#test-selection-and-cadence), define allowed/forbidden outcomes before code, prefer meaningful test-first evidence, and record justified alternatives honestly. |
| Documentation | Reader-oriented Markdown and scoped manuals/quality inventories. Separate contracts, procedures, rationale and dated evidence where useful. No ASD-STE100 compliance claim. |
| Evidence | Retain compact commands, identities, outcomes and short failures; preserve maintained inputs, history, pins and seals privately where not published. Remove only owned generated outputs under existing rules. |
| License | Original work remains [BSD-2-Clause](LICENSE); Agent Temper remains BSD-3-Clause. Preserve third-party terms and notices; see the consumer [licensing summary](docs/LICENSING.md). |
| Integration | Accepted changes require affected checks and separate review before integration. Hosted settings do not replace these requirements. |
| Operations | Existing owner, affected-owner, native-execution and release approvals remain. A green check grants no additional publication, deployment, credential, physical-device or operational authority. |

## One work authority

After cutover, read the selected issue and its full discussion before changing
behavior. Each executable issue owns one finite outcome, non-goals, acceptance,
prerequisites, owner, actual status, verification, review and continuation.
A coordination epic gives context and child exit conditions, not an unbounded
implementation assignment. ROADMAP retains capability gates; it is not a queue.

Apply the pinned GitHub profile's six progress states and completion rules.
An open executable issue has one progress label; closed issues have no active
progress label and record why they closed. Use concrete blocking relationships,
record the priority convention and milestone order in canonical issues, and keep
Projects/wiki views subordinate to those issues.

Resume authorized active work or its review first. A historical next action,
backlog entry, roadmap gate or proposal is not permission to implement. Establish
finite acceptance, tests, prerequisites, scope authority and system order before
starting another item. Record unrelated findings before fixing them. Routine
decomposition cannot enlarge scope, change product commitments or renew consumed
execution approvals.

Use meaningful issue comments for progress and continuation, identifying source,
actual checks, remaining work and next owner/action. Durable Markdown records
hold contracts, decisions and dated evidence rather than a second task status.
Map completion to actual acceptance and review; use `Closes #NUMBER` only for an
entirely satisfied executable issue. Implementation issues close on accepted
merge, not PR creation. Reconcile dependencies and parent exit conditions after
integration. Research and coordination work close at their reviewed exit gates.

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

## Verification, instructions and maintenance

[DEVELOPMENT](docs/DEVELOPMENT.md#test-selection-and-cadence) owns the command/risk
map. Component commands run from their component directories unless stated otherwise.
The root Makefile retains aggregate entry points. `make check-system` is not an
assembled OS, boot-to-shell or release result. It and `zig build test` require
private standards and additional local inputs; they remain blocked when those
inputs are unavailable. See [PUBLIC-SOURCE](docs/PUBLIC-SOURCE.md). Sys-init's
`--current` gate leaves unavailable historical replay explicit. Missing tools, zero cases, infrastructure
failures and skipped checks are not passes.

Existing execution ceilings, stop-on-failure/no-retry rules, source freezes and
cleanup requirements remain scoped to their contracts. The required native-home
broad host aggregate retains its 300-second budget where selected; onboarding's
source-integrity/pure-Zig CI is no substitute. A failed or unavailable required gate stays
blocked coverage. No new guest disposition or expanded resource approval follows
from this policy or from hosted CI.

Prose-only changes use applicable available source/link/syntax checks and separate
reader/source review. Standards-dependent checks remain required when selected
by the affected contract; unavailable inputs are blocked coverage, never a pass.
Prose-only changes do not imply an unrelated full suite, native guest or
source/build archive. Keep public summaries separate from local qualification
receipts; missing receipts cannot be represented as fresh validation.

For a method update, compare every bundled file and the complete inventory with
the immutable source. From `.agent-temper`, run `shasum -a 256 -c SHA256SUMS` or an
equivalent SHA-256 check, reject unexpected files/symlinks and inspect internal
links offline. Existing inventories do not establish all prose/anchor coverage.
Keep consumer extensions outside the immutable bundle. A finite issue, source/
compatibility review, checks and separate review precede pin replacement.
Classify findings using the pinned [extension rules](.agent-temper/docs/reference/extensions.md).
Sanitize any authorized public upstream proposal; do not copy private source or
sensitive evidence into an issue. An upstream change updates no consumer automatically.

## Codex routing selection

The AT-002 role/model/effort selection at immutable method source
`c07af93dc99e770bf4f3ec6f30a0536cb2ae14c5` remains unchanged. Its private historical
integration target is not a public branch assignment. GitHub tracking selection
changes no model, permission, fallback, verification or external-action boundary.

| Role | Assignment | Model | Reasoning effort |
| --- | --- | --- | --- |
| `temper_workflow` | Bounded read-only inspection and evidence summaries | `gpt-6-luna` | `medium` |
| `temper_implementer` | Accepted implementation, tests and ordinary debugging | `gpt-6.1-sol` | `high` |
| `temper_analyst` | Ambiguity, architecture and difficult failures or separate review | `gpt-6-astra` | `high` |
| `temper_reviewer` | Separate examination of the final change and evidence | `gpt-6.1-sol` | `high` |

Read all four adapted files in `.codex/agents` with this policy. They set model
and effort outside the immutable bundle. No primary-chat model, personal default,
provider, trust, sandbox, approval, integration or permission setting changes.
The lead supplies finite scope, owning issue/discussion, policy, inputs,
acceptance, checks and nonoverlapping edit boundaries. The lead owns issue updates,
returned-evidence verification and integration. Required separate reviewers must
not have authored the implementation. Complexity/repeated failure returns to the
lead for a narrower task or separately assigned analyst, not automatic escalation.

At most three subagents may run simultaneously, excluding the primary and within
any lower client/task limit. No recursive helpers, higher effort or model changes
without a bounded lead assignment consistent with the existing owner policy.
Only Cam authorizes standing role/model/effort, fallback or resource changes.

If a role/model is unavailable, report it. The lead may perform the bounded task
on its current model only when that model, permissions and limits satisfy policy;
otherwise resolve the required owner decision. Never silently substitute or claim
that requested routing ran. An explicit fresh-agent mapping may be used only under
the recorded policy, with requested and observed metadata recorded separately.

Runtime routing remains unverified. File syntax/source checks do not prove role
discovery or model selection in a fresh consumer. Use the existing fallback until
trusted runtime metadata establishes each route; record client/version, source,
requested/observed settings, outcome and limits in the issue. Do not infer support
from an agent's self-description or change trust/permissions merely to enable it.
