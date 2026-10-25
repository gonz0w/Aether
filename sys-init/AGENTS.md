# AGENTS.md

## Product target

This component targets Aether only. Cross-OS runtime support, portability shims
and Linux/BSD/illumos qualification matrices are not product requirements. Keep
useful host development checks and POSIX conventions; host execution does not
qualify native Aether behavior. See root [repository scope](../docs/REPOSITORY.md).

## System repository scope

Read root [AGENTS](../AGENTS.md), the pinned [Agent Temper method](../.agent-temper/METHOD.md)
and root [engineering policy](../PROJECT.md) before this component's guidance.
Apply root [PROJECT's cutover rule](../PROJECT.md#public-onboarding-cutover).
After verified onboarding/migration, GitHub Issues alone own live scope, priority,
dependencies, ownership and continuation. Root [STATE](../.planning/STATE.md) is
compatibility navigation; [ROADMAP](../.planning/ROADMAP.md) holds capability gates.
Component planning files preserve stable IDs, contracts and read-only history,
not an active queue. Before cutover, only the approved onboarding bootstrap record
selects that operation. Historical next actions never authorize public work.

The explicit cutover supersedes older component work-routing instructions only;
contracts, checks, review and operational approval remain binding. References to
an owning record in those guides mean the canonical issue after cutover. Local
qualification receipts and the obsolete whole RC1/ADP-01 packet are excluded;
required missing evidence remains blocked coverage. Consumer locks stay exact.
Read the root [public-source boundary](../docs/PUBLIC-SOURCE.md): all standards
release/review bytes and imported hooks remain private. Ordinary public prose
and self-contained model work use available local rules; changes needing private
normative inputs require the owner and exact inputs before dependent work.

Paths and commands below are relative to this component. One integration agent
may change this component and its consumers together after reading their guidance;
old sibling handoff instructions do not require stopping at a directory boundary.
Keep component responsibilities, runtime authority and native acceptance separate.
Follow root [DEVELOPMENT](../docs/DEVELOPMENT.md) for focused checks and compact
retention. Integration after required checks and separate review follows root
policy; affected-owner, native-execution and release gates still apply. Standards
remain private in Aether-standards, with retained consumer lock identities unchanged.


## Scope

This repository is for `sys-init`: a modern POSIX-oriented init system for the Aether operating-system effort.

## Product Direction

- Build a simple, powerful init system that is understandable from POSIX shell concepts but capable enough for modern systems.
- Keep the design aligned with the Aether kernel project at the repository root and the package manager at `../pkg-mgr/`.
- Prefer small, inspectable primitives over large opaque service-manager machinery.
- Research first. Do not commit to implementation architecture until the captured research backlog has produced findings.

## Current delivery priority

Maintainer decision, 2026-10-22: sys-init targets Aether only. Other-OS product
support and Linux/BSD/illumos qualification campaigns are withdrawn, superseding
decision 0153's deferral. Keep useful host tooling, POSIX authoring conventions and
focused checks for changed code. Require fresh native Aether witnesses and actual
independent review for corresponding runtime/release claims. Historical platform
results retain their original scope; retiring requirements does not mark tests run.
Hosted CI remains a development delivery decision, not another runtime target.

## Simplicity in new and changed work

Build the smallest understandable system that satisfies the current requirement
securely and correctly. Borrow proven ideas deliberately, justify added complexity,
and remove obsolete paths through scoped, compatibility-aware changes. Keep
shelved lifecycle machinery outside the active essential boot/supervision/shutdown
design. Apply the adopted SE-01–05 [process snapshot](docs/SIMPLICITY-ADOPTION.md)
and the three questions in the existing QUALITY-PROCESS substantial-change review.
Routine fixes need no new document or ceremony; do not trade away ownership,
bounds, failure handling or authority checks to shorten code.

## Repository Rules

- Treat `docs/PRD-SEED-SYS-INIT.md` as seed intent, not complete specification. It currently summarizes a richer PRD but does not contain the detailed source research.
- Follow `.planning/README.md` for durable document placement and legacy IDs. After cutover live work belongs in its canonical GitHub issue; captured backlog files are read-only historical inputs.
- Start with README.md, root PROJECT cutover policy, the canonical issue and component `.planning/ROADMAP.md`. Local STATE, backlog and archived workflow commands are historical context, not assignments.
- Put new research in `docs/research/` and accepted decisions in `docs/decisions/`; create these directories when adding real artifacts. Preserve stable backlog and question IDs.
- Distinguish the POSIX-facing distribution goal from Aether's currently demonstrated native runtime. Do not infer target APIs or the sys-init implementation language from companion-project choices.
- Research completion requires cited findings and bounded follow-up issues for unresolved questions, risks or prototypes; do not reopen a parallel Markdown backlog.
- Define Aether runtime contracts explicitly; host APIs are development mechanisms.
- Justify dependencies by an actual Aether requirement, security and whole-system cost.

## Validation Expectations

- Define expected behavior and forbidden outcomes before implementation. Prefer meaningful test-first work. Reproduce bugs before fixing them, or record why deterministic reproduction is unavailable and the alternative evidence. Record the actual sequence and run relevant checks on final bytes before completion.
- For research-only work, cite sources in the artifact and record live decisions/questions in the canonical issue. Legacy question JSON retains stable IDs as read-only context.

## Private standards and affected work

Consumer `docs/EXPERIENCE.md`, `docs/STANDARDS.md` and `docs/DISTRIBUTION.md`
record local adoption and applicability; the referenced standards release/review
inputs remain private. See root [PUBLIC-SOURCE](../docs/PUBLIC-SOURCE.md).
Before presentation, shared authority/interface, build/evidence, package/service
or distribution work that needs those inputs, involve the owner and obtain the
exact applicable inputs. Missing requirements or required checks block dependent
work. Do not reconstruct private clauses, silently change pins, weaken a gate or
claim standards/runtime conformance from public source/model checks. Existing
domain contracts, machine protocols, native approvals and component ownership
remain binding; shared normative changes stay with the private standards owner.

## Licensing

BSD-2-Clause is the default for original work across the system repository and
the separate Aether-standards repository.
Read the consumer [licensing summary](../docs/LICENSING.md), root LICENSE and
applicable upstream notices. Preserve third-party terms and
existing notices. Use `SPDX-License-Identifier: BSD-2-Clause` for new original
source files where appropriate. Do not rewrite immutable standards, fixtures or
evidence to add headers. Package recipes do not relicense their upstream payloads.
