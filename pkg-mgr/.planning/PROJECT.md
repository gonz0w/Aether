# Project

Updated: 2026-09-05.

## Purpose

Build a small, auditable package manager for the Aether operating-system effort, coordinated with `../sys-init/` and `../userland/` in this repository. Support source builds and trustworthy binary delivery, readable recipes, local customization, inspection, and eventual safe install/update/remove workflows. Aether is the only product target; host staging/tests do not establish native acceptance.

Learn selectively from other package managers. The existing research motivates these directions, rather than a requirement to reproduce every feature:

| Inspiration | Direction to evaluate here |
| --- | --- |
| pkgsrc and Ports | Plain recipes, explicit phases and patches |
| poudriere | Clean builders and repeatable bulk-build evidence |
| Nix and Guix | Explicit inputs, isolation, reproducibility, narrowly tested state transitions |
| Portage | Source builds, options, and local customization |
| apk | Editable requested-package roots and inspectable state |
| pacman and apt/dpkg | Ownership, dependency records, predictable package operations |

These are design themes inherited from the archived research, not a fresh comparative feature audit or a selected store architecture.

## Working decisions

- Release target: Aether only (maintainer decision, 2026-09-06). Host tooling and
  existing host evidence support development; macOS/Linux/BSD are not release
  products. No old-macOS reconstruction gate applies. Cam owns reviews, which
  remain pending until performed. See docs/AETHER-RELEASE.md for local acceptance.

- POSIX shell, make, and plain text remain the host prototype baseline. The current host driver explicitly requires GNU Make 3.81+. There is no BSD make compatibility requirement.
- Aether is the primary integration target. Begin with host-side staging and metadata; native execution requires target runtime contracts that do not exist here yet.
- Keep kernel mechanisms in Aether, service lifecycle in sys-init, base-package selection in Aether-userland, and package payload/state/trust decisions in pkg-mgr. Package metadata cannot grant kernel capabilities.
- Use traditional package records plus an editable `world` file, now implemented for staged regular-file payloads. This is a private fixture baseline, not approval of a production store.
- Keep fetch, build, stage, and installation as explicit boundaries. Recipes execute trusted maintainer code; metadata must remain inert data.
- Test local fixtures first, label missing evidence, and keep generated state disposable.

## Scope and deferred decisions

The hardened local build path now orders phases, verifies copied inputs, and guards a private root. Plain package records, editable roots, inspection, verification, and non-deleting orphan reports now work in that private root. Static zlib and its small dependent utility exercise real host builds, upstream tests, and evidence-bound registration. Local directory bundles now export/import these packages into fresh private stages with pinned integrity, exact dependency records and explicit host identity. A pinned boot-pair handoff now passes Aether’s image-builder and two-CPU smoke path. General package/image format, target ABI versioning, sys-init service descriptors, binary eligibility, and installation transaction semantics remain open.

No real-prefix writes or payload deletion in this work. Generation rollback and reachability remain optional experiments after the basic package lifecycle proves a need. No daemon, SQLite, solver, custom DSL, full declarative OS layer, Windows target, or compiled core without new evidence and an explicit scope decision. The kernel's Zig and user-space Rust choices do not by themselves require a pkg-mgr rewrite.

## How to track work

PROJECT owns intent and decisions; `docs/ARCHITECTURE.md` owns interfaces; ROADMAP owns work and acceptance; STATE owns the latest evidence and next action. Update these when behavior or direction changes. Add a focused contract only when implementation needs it. Do not recreate generated phase/handoff trees or parallel backlog/status systems.

Historical evidence lives under `docs/archive/2026-09-05-planning-reset/`. Consult specific artifacts when needed; archived instructions, approvals, and milestone statuses are not active requirements.

## Shared experience

Adopt Aether Experience v0.1.0 and the Hearth palette for new first-party user-facing work. `docs/EXPERIENCE.md` records the pin, scope and migration status. This shared presentation contract does not change kernel authority, service lifecycle, package state or upstream interfaces. Existing surfaces migrate through separately tested implementation work.
