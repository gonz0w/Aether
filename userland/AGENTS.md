# Project guidance

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


- Read README.md, .planning/PROJECT.md, docs/ARCHITECTURE.md,
  .planning/ROADMAP.md and the canonical issue before broad work. Legacy BACKLOG/STATE
  files are read-only context; do not select assignments from them.
- Keep component intent in .planning/PROJECT.md, contracts in ARCHITECTURE and
  capability acceptance in ROADMAP. After cutover, the canonical issue owns live
  work, open decisions, status and continuation. Legacy BACKLOG/STATE files stay
  read-only; link their stable IDs without maintaining a parallel queue.
- Preserve stable UL IDs. Record dependencies, acceptance evidence, and unresolved
  follow-ons before marking a story done. Research completion is not runtime completion.
- Clang/LLVM is preferred for C. Musl is a candidate, not an available Aether libc.
  Zsh is the interactive destination; other package choices remain provisional.
- Use small shell/make/plain-file experiments. Do not duplicate pkg-mgr recipes,
  package state, or sys-init policy machinery. Coordinate interfaces explicitly and implement affected components together
  when the integration task requires it.
- Preserve native capability enforcement. POSIX identity, package metadata and
  service names do not imply native authority. Never mask unsupported semantics
  with successful no-op implementations.
- Distinguish host builds, ELF object generation, linking, Linux reference runs,
  Aether execution, and POSIX conformance. Each needs separate evidence.
- Pin inputs before consuming dependencies. Record compiler, flags, target ABI,
  hashes and runtime environment. Moving web sources are research leads, not pins.
- Test meaningful failure cases. Security, speed, reproducibility and recovery
  claims require measurements or exercised boundaries, not language/library labels.
- Keep build outputs under build/. No real-prefix installation during experiments.
- Use the affected consolidated component guidance and contracts under the system
  root; the original sibling checkouts are recovery sources. docs/archive is
  historical only. No background monitoring, cross-project acceptance, or native
  readiness is implied by this plan.

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

## Development quality adoption (UL-060)

Before new or revised work, read the local docs/quality/PROCESS.md. Required
private draft inputs are governed by the public-source boundary above. Use
docs/quality/change-review.md to record scope, risks, tests, documentation impact
and actual review evidence. Select affected checks under root DEVELOPMENT; the
quality checker needs its exact private inputs and is blocked without them. Preserve upstream/generated
style and historical evidence. Approved drafts are not published release pins.
Treat missing required checks/reviews as incomplete; track migration in UL-061–063.
Complete the command-runner source review in UL-063 before UL-058 behavior changes.


## Simplicity extension (UL-080)

Build the smallest understandable system that satisfies the current requirement
securely and correctly. Borrow proven ideas deliberately, justify added complexity,
and remove obsolete paths through scoped, compatibility-aware changes. Read the
local substantial-change questions in root docs/DEVELOPMENT.md. The referenced
standards snapshot remains private. Answer the local questions in the existing change review; routine
fixes need only proportionate explanation. Preserve authority, bounds, cleanup,
upstream style/terms and immutable evidence. Triage existing complexity by delivery
impact and risk in the backlog; this adoption authorizes no broad runtime rewrite.
