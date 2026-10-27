# Aether engineering policy

This file records engineering policy for the kernel root, `userland/`, `sys-init/`
and `pkg-mgr/`. [Product direction](.planning/PROJECT.md) and
[architecture](docs/ARCHITECTURE.md) retain product/runtime authority.
[GitHub operating guidance](docs/GITHUB.md) describes this public consumer's
hosting and work routing. The local AT-001/AT-002 records preserve earlier method
and routing decisions; their historical branch targets are not public assignments.

## Selected policy modules

The root [policy.toml](policy.toml) is the sole declaration of selected modules and
their dependencies. Read PROJECT first, then every selected module and the owning
work record before affected work. Directory presence does not select a module.
The selected local sections below keep their original requirements and heading
routes; canonical text now lives in `docs/policy/`. Apply compatible rules together.
An unresolved required conflict stops dependent work for the existing owner process;
manifest order or a passing helper cannot override a clause or grant authority.

Local policies bind to their containing source revision. Existing immutable
external inputs, active decisions and historical/expired evidence retain their
identities and scope. Historical or consumed decisions are not reactivated by this
selection and are not declared as active manifest exceptions. The existing owner
change process governs module, dependency, exception and policy updates.
The manual [selection checker](tools/temper/SOURCE.md) reports mechanical errors;
policy meaning, approval, event expiry, conformance and execution need review.

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
`781a4b9f71d002b93bc4ad26669d01a3b37c482e`. Its
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

See the canonical [execution policy](docs/policy/execution.md#bounded-zsh-application-trial-2026-10-25).

## AF09 diagnostic control review —2026-10-26

See the canonical [execution policy](docs/policy/execution.md#af09-diagnostic-control-review-2026-10-26).

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

See the canonical [integration policy](docs/policy/integration.md#source-control-and-integration-authority).

## Verification, instructions and maintenance

See the canonical [verification policy](docs/policy/verification.md#verification-instructions-and-maintenance).

## Complete host gate budget —2026-10-26

See the canonical [verification policy](docs/policy/verification.md#complete-host-gate-budget-2026-10-26).

## AF09 offline family budget —2026-10-26

See the canonical [execution policy](docs/policy/execution.md#af09-offline-family-budget-2026-10-26).

## Codex routing selection

See the canonical [routing policy](docs/policy/routing.md#codex-routing-selection).

## Terra product routing update — 2026-10-27

See the canonical [routing policy](docs/policy/routing.md#terra-product-routing-update--2026-10-27).
