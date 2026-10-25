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


## Project North Star

`pkg-mgr/` is Aether’s source-and-binary package manager. Coordinate with the
kernel at the repository root, `../sys-init/` for lifecycle and `../userland/`
for base selection. Build a secure, readable package workflow with explicit
trust boundaries; borrow proven ideas without adding other-OS products.

Default design posture: **POSIX shell, make, plain text, small tools, and YAGNI until evidence proves a stronger tool is needed.**

This project should feel like a modernized Ports/pkgsrc system with security and reproducibility lessons from Nix/poudriere/sigstore-era supply-chain practice, not like a large opaque framework.

## Core Principles

1. **Unix philosophy first**
   - Prefer small programs and files that do one thing well.
   - Prefer line-oriented, inspectable, scriptable formats.
   - Make every important operation understandable with standard tools such as `sh`, `make`, `awk`, `sed`, `find`, `sort`, `grep`/`rg`, `diff`, and `git`/`jj`.
   - Avoid hidden framework magic. If behavior matters for trust, make it visible.

2. **YAGNI as a hard engineering constraint**
   - Do not introduce a daemon, database, custom DSL, plugin system, package language, GUI/TUI, network service, or compiled core unless current evidence shows it is needed.
   - Prototype the 80% path first: install, build, verify, remove, update, stage, manifest, and inspect.
   - Defer non-core features that do not directly serve package workflows, security, or maintainability.

3. **Security without obscurity or bloat**
   - Security is foundational, but must remain understandable and usable.
   - Prefer layered, auditable defenses: hashes, pinning, provenance, sandboxed/hermetic builds, reproducibility, signed metadata, SBOMs where useful, and easy local rebuild/verification.
   - Never claim production security, sandbox enforcement, release approval, or supply-chain safety unless backed by concrete evidence.

4. **Aether is the product target**
   - Use Aether-native contracts for runtime integration and confinement.
   - Keep host staging and validation separate from native acceptance.
   - Do not add Linux/BSD sandbox backends or platform support matrices without
     a concrete Aether development requirement.
5. **Plain recipes and critical metadata**
   - Recipes should be readable, editable, forkable, and reviewable by package maintainers with normal Unix skills.
   - Favor make variables, shell phases, patch files, manifests, lockfiles, and simple metadata over opaque generated state.
   - Recipes are part of the trusted surface; keep them boring.

## Current Architectural Bias

Treat the current POSIX shell/make baseline as the design center:

- `mk/pkg.mk` is the current make-driven phase scaffold.
- `mk/phase.sh` is the current POSIX shell helper pattern.
- `recipes/*/package.mk` is the current recipe shape.
- `tests/*.sh` are the current executable validation style.

Future agents should strengthen and test this baseline before proposing Rust, Zig, Go, Python, SQLite, SAT solvers, content-addressed stores, or services. A compiled helper may be appropriate later for crypto, dependency solving, store mutation, privilege separation, or performance-sensitive operations, but only after a narrow seam and failure mode are demonstrated.

## What We Are Trying To Build

A package manager that can eventually:

- install fast binary packages when trust policy allows;
- build from source by default or on demand;
- make local rebuild and verification easy;
- support custom options and local overlays without forking the world;
- keep build phases explicit and inspectable;
- produce manifests and audit trails for installed files;
- support reproducible-build workflows where practical;
- support Aether binary release automation with clean, reproducible builders;
- let users choose stronger trust policies without making the common path unusable.

## Evidence Already Established

Use these as current project facts unless newer artifacts supersede them:

- `.planning/PROJECT.md` defines current intent; `docs/ARCHITECTURE.md` describes implementation and Aether/sys-init boundaries. Shell/make remains the host prototype; native Aether execution is unproven.
- `docs/PM-PRD-Initial-Research-Guidance.md` routes current Aether package research; its earlier cross-OS mandate is retired.
- The foundational recipe/POSIX milestone produced a POSIX sh/make baseline prototype design and confirmed the value of simple phase + variable recipe structure.
- The executable baseline milestone materialized real shell/make scaffold files and shell tests.
- The sandbox/hermetic milestone defined capability-labeled sandbox behavior and rejected broad production-sandbox claims.

## Design Decision Rules

When making or proposing changes:

1. Start with the smallest shell/make/plain-file design that could work.
2. Show the actual command path or file format, not just architecture prose.
3. Prefer composition over centralization.
4. Prefer explicit phase boundaries over generalized hooks.
5. Prefer deterministic files over hidden mutable state.
6. Prefer append-only or reproducible logs/manifests where feasible.
7. Treat generated files as disposable unless they are declared artifacts.
8. Do not add dependencies casually. Every dependency expands the bootstrap and trust problem.
9. Do not invent security guarantees. Label capability, boundary, and runtime gaps explicitly.
10. Keep examples real enough to run, but small enough to understand.

## Implementation Guidance

- Shell should be POSIX `sh` unless there is a documented reason otherwise.
- Makefiles should avoid non-portable GNU-only features unless labeled and justified.
- Prefer checked-in fixtures and deterministic local tests over network-dependent tests.
- Keep scripts short and single-purpose; split only when the split clarifies ownership.
- Use clear exit codes and stderr diagnostics for user-facing failure modes.
- Quote shell variables carefully and assume paths may contain spaces where reasonable.
- Avoid global mutation in tests; use `work/`, `stage/`, `logs/`, `distfiles/`, and temporary directories.
- Do not write to a real prefix in tests; stage first and manifest outputs.
- Use `make`, `sh`, and focused test scripts as the default validation path.

## Security and Trust Guidance

- Build and install are separate trust boundaries.
- Fetch and build are separate network boundaries.
- Build/test/install phases should default toward no network.
- Strict sandbox mode must fail closed rather than silently downgrade.
- Lower-guarantee modes must be labeled, not hidden.
- Hash verification, provenance, signatures, SBOMs, and reproducibility should be phased in according to YAGNI and Aether evidence.
- Do not treat signatures alone as sufficient supply-chain security.
- Do not treat local dry-run sandbox evidence as live confinement proof.

## Planning and Integration Awareness

Use `.planning/PROJECT.md` for component direction, `docs/ARCHITECTURE.md` for interfaces and `.planning/ROADMAP.md` for capability acceptance and candidates. After verified cutover the canonical GitHub issue owns live work and continuation; root STATE is navigation and local STATE is read-only historical context. Do not recreate phase generators, handoff trees, or parallel status systems.

`docs/archive/` is historical reference only. Exclude it from ordinary searches. Archived instructions, workflow commands, requirements, and completion labels do not govern active work; consult specific artifacts only when their evidence is needed.

The local build path is hardened under `docs/BUILD-FIXTURE.md`. Traditional package records plus editable `world` are implemented under `docs/PACKAGE-STATE.md`. The Aether boot-pair handoff is validated under `docs/AETHER-HANDOFF.md`; sys-init’s service contract remains pending. Static zlib and the dependent zpipe utility now build and register under `docs/ZLIB-PACKAGE.md`. Local binary export/import is implemented under `docs/BINARY-PACKAGE.md`, with v2 recorded ordinary file modes and no remote authenticity claim. Explicit pinned-bundle recovery is implemented under `docs/IMPORT-RECOVERY.md`; it adopts only an exact existing stage and never repairs or deletes it. State v2 now verifies file permissions; legacy v1 records remain inspectable but cannot pass complete verification. Non-mutating update preflight is implemented under `docs/UPDATE-PREFLIGHT.md`. Three-way comparison and configuration preservation rules are defined in `docs/REPLACEMENT-POLICY.md`; its explicitly requested retained private-root replacement is implemented by `mk/replacement.sh`. Pending transactions guard normal package operations. Existing payload is retained, with deletion/pruning and live-prefix authority still unopened. Generation activation, rollback, and reachability are deferred bounded experiments. Do not add real-prefix writes, payload deletion, SQLite, a daemon, a solver, or production rollback/GC claims without explicitly reopening scope.

Aether owns kernel/loader/capability contracts; sys-init owns service lifecycle and descriptors; Aether-userland owns base-package selection (no list established as of this review); pkg-mgr owns package artifacts, records, and trust policy. Start integration on the host. Never treat package metadata as capability authority or installation as permission to start services. Consult component docs before interface work, and keep their implementation in the respective component directories.

## Non-Goals Unless Explicitly Reopened

- No other-OS package-manager products.
- No full declarative OS configuration layer.
- No heavy GUI/TUI/web frontend.
- No broad plugin ecosystem.
- No Turing-complete custom package language.
- No mandatory heavyweight container runtime.
- No production sandbox/security/release claims from research artifacts alone.

## Agent Operating Instructions

- Read this file, `.planning/PROJECT.md`, `docs/ARCHITECTURE.md`, `.planning/ROADMAP.md`, root PROJECT cutover policy and the canonical issue before major work. Read legacy STATE only for relevant history.
- Select affected checks using root DEVELOPMENT and the local development process. `sh tests/check.sh` is the bounded aggregate for current fixture validation when required; it isolates the suite and build tests use initialized private output roots.
- Inspect current shell/make patterns before proposing new architecture.
- Preserve user work and do not rewrite planning history unless the active workflow requires it.
- Keep changes small, reviewable, and validated with commands.
- If a change pulls the project away from POSIX shell/make/plain-text simplicity, call that out explicitly with the evidence and tradeoff.
- Prefer saying “not proven yet” over making claims the current artifacts do not support.

## One-Sentence Reminder

Build the simplest auditable Unix package manager that can be secure by default, source-friendly, binary-capable, native to Aether, and fast enough to enjoy using.

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

## Coding, testing and documentation review process

Read CONTRIBUTING.md and docs/DEVELOPMENT.md before new work. The 2026-09-05
standards additions are unreleased drafts; docs/standards-review.json records
reviewed identities, not release pins or owner approval. Apply the scoped local
process without claiming full draft conformance. Keep docs/development-inventory.json
current for changed commands, formats, tests and subsystems.

Before behavior changes, state the oracle, forbidden outcomes and selected tests.
Prefer meaningful test-first work. Reproduce bugs before fixing them, or record
why deterministic reproduction is unavailable and the alternative evidence.
Record the actual sequence without retrospective red claims. Run affected checks
on final bytes under root's focused cadence; use sh tests/check.sh when the aggregate
is required or no safe subset exists. Documentation-only changes select applicable available source/link/syntax
checks under root DEVELOPMENT. Required standards-dependent checks remain blocked
without the exact private inputs. Run python3 tests/check-development.py --lint
PATH ... for new/revised shell files; missing required tools are blocked. Review
existing findings in touched code, with narrow justified exceptions only. Retain
failed evidence and exact dirty-tree input hashes. Do not claim scheduled CI,
manual coverage, target support or reviewer approval without actual evidence.

The maintainer already approved the referenced draft content; do not repeat that
content-approval request. Private approval/review inputs, separate implementation
review, runtime evidence and immutable release adoption remain distinct. Obtain
required exact inputs through the owner before affected dependent work.

## Simplicity extension — explicit local adoption

Build the smallest understandable system that satisfies the current requirement
securely and correctly. Borrow proven ideas deliberately, justify added complexity,
and remove obsolete paths through scoped, compatibility-aware changes.
Use the local substantial-change questions in root docs/DEVELOPMENT.md; the
referenced standards review snapshot remains private. Count total
state, dependencies, configuration, failure/recovery and operator cost; do not use
line counts or tests alone as proof of simplicity. Ordinary small fixes need no
new review document. This is an unreleased process extension, not a release pin,
rc1 change, refactoring mandate or permission to remove safety checks/evidence.
