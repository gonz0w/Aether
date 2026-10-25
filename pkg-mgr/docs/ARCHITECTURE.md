# Architecture and integration

> Shared-standards migration, 2026-09-05: [Foundations adoption](STANDARDS.md) now routes the canonical shared ownership, interface and evidence rules. Domain mechanisms and exact implementation contracts below remain owned by this project. Shared-rule changes belong in a new standards release; adoption does not change implementation status.

Reviewed: 2026-09-05. This describes the current prototype and proposed integration boundaries; it is not an implemented OS package interface.

## Release boundary

Aether is the only release target under the 2026-09-06 maintainer decision.
Host execution remains development evidence. The shell/make command path below
has not been demonstrated as a native Aether package manager. Native execution,
storage and artifact acceptance are tracked in [Aether release scope](AETHER-RELEASE.md).

## Current executable path

`recipes/hello-local/package.mk` supplies local metadata. `mk/pkg.mk` invokes `mk/phase.sh` for directories and phase logs, then runs:

```text
fetch -> verify -> extract -> patch -> configure -> build -> test -> stage-install -> manifest
```

For hello-local, fetch/extract/build copy one local text file; patch is a no-op; configure writes a prefix. Verify checks the copied input against strict source metadata before extraction. Phases form an ordered make dependency chain, including under parallel invocation. Builds require an initialized private ROOT with fixed output paths. See [the fixture contract](BUILD-FIXTURE.md). The [zlib/zpipe recipes](ZLIB-PACKAGE.md) add real native compilation and dependency use through explicit shell phase scripts. `evidence` and `register` connect these stages to the existing package records. The [local binary transport](BINARY-PACKAGE.md) exports directory bundles and imports into private stages. There is no live-prefix install operation.

Separate metadata entry points exist:

```sh
make -f mk/pkg.mk verify-source-metadata
make -f mk/pkg.mk verify-snapshot-metadata
make -f mk/pkg.mk hashed-manifest
make -f mk/pkg.mk build-record
make -f mk/pkg.mk check-sbom
```

The last three consume staged or supplied records; use explicit inputs and outputs for real experiments. Defaults are hello-local fixtures. `mk/verify-metadata.sh` validates strict source/snapshot records, SHA-256 and sizes, sorted index binding, regular-file hash manifests, build-record inputs, and advisory SPDX fields. It publishes manifest/build outputs using adjacent temporary files. These are individual checks, not an enforced end-to-end installation policy.

Snapshot self-hash and index hash-tool failures reject before the signature seam,
using snapshot-hash-unavailable and index-hash-unavailable respectively. A failed
tool that prints plausible digest text still fails; content mismatch is a distinct
result. Temporary hash inputs are removed on these ordinary failure paths.

Snapshot verification can exit zero with `result=tool-unavailable` when minisign is absent, or a warning when a configured fixture signature verifies. Exit status alone therefore cannot authorize binary installation. Authenticity policy, key governance, freshness enforcement, and binary eligibility need a separate fail-closed decision.

Hashed manifests cover regular-file content, size, and path; they do not record full filesystem semantics such as permissions, directories, symlinks, or special files. The package flow guards its private output root and rejects links/special files. Standalone metadata helpers retain caller-controlled paths; make expressions and recipes remain trusted code. Separate concurrent writers, crash durability, hostile path races, sandbox enforcement, and production installation safety are unproven.

## Inspectable staged-package state

`mk/state.sh` registers `ROOT/stage/NAME` against a matching hash manifest and canonical advisory build record. One TSV per package embeds the evidence and file rows; an editable `state/world` names requested roots. Ownership, dependency, reverse-dependency, and orphan views are derived on demand. Verification reports payload damage without repair. See [the state contract](PACKAGE-STATE.md) for schemas, commands, and limits.

There is no cache/index authority, solver, live installation, or deletion API. Identical registration is idempotent; changed evidence for an existing package is rejected. Build/clean helpers refuse to mutate a registered stage. The [recovery contract](IMPORT-RECOVERY.md) now permits explicit adoption of an exact interrupted binary stage. `check-register` validates registration without publishing state. State v2 additionally tracks ordinary file permissions, and binary v2 preserves them. Legacy v1 records remain inspectable but cannot pass complete verification. Update/remove still require broader configuration and transaction decisions.

## Four-project boundary

| Project | Responsibility | Local evidence reviewed |
| --- | --- | --- |
| Aether (`~/DEV/Aether`) | Kernel objects, capability authority, process/memory/IPC primitives, boot and executable loading contracts | README, AGENTS, docs/ARCHITECTURE.md |
| sys-init (`~/DEV/sys-init`) | Service lifecycle, supervision, start/stop ordering, eventual service descriptor contract | AGENTS, docs/PRD-SEED-SYS-INIT.md, .planning/STATE.md |
| Aether-userland (`~/DEV/Aether-userland`) | Base-package selection, userland requirements and eventual base-set definition | experiments/c-object/probe.c: compile-only C probe; no approved package list yet |
| pkg-mgr | Recipes, verified inputs, staged payloads, package records, ownership and dependency evidence; eventual install/update/remove policy | mk/, recipes/, fixtures/, tests/ |

Aether currently targets an x86_64 capability multikernel: Zig kernel, Rust user-space services, QEMU bring-up. Its September 5 STATE now records cross-core user IPC progress; general executable loading and POSIX remain unsupported. The boot-pair handoff below passed its existing two-CPU smoke test, without establishing a native shell/package runtime.

Sys-init's current STATE records completed runtime-checklist and boundary-handoff research, with BG-027 (package/service artifact and lifecycle contract) next. No descriptor schema, validator command, or runtime implementation is established yet. Its separate project owns that work.

## First integration experiment — boot handoff verified

The narrow adapter `mk/aether-boot.sh` stages an explicitly hash-pinned kernel/boot-fixture pair with a manifest and target receipt. Aether’s existing `scripts/image.py` consumed the staged files, and its two-CPU smoke test passed. See [the handoff and evidence](AETHER-HANDOFF.md). This is separate from package records and does not attest the imported binaries as source-built packages. The package core is not coupled to the ISO builder, and `x86_64-unknown-none` is not selected as a general package ABI.

Before widening this boot demo to package installation or service activation, agree and test:

1. Host tools versus target artifacts: architecture, ABI/version, executable format, toolchain inputs, and loader restrictions.
2. Filesystem/image layout: destination ownership, path grammar, modes/links, configuration handling, and the actual image consumer.
3. Service packaging: inert descriptor format and validation owned by sys-init. Installation should not implicitly start/restart services; activation requires a separate explicit lifecycle decision.
4. Authority: who may publish package state, change an image, activate a service, and delegate capabilities. Package names and metadata never convey authority themselves.
5. Failure: rejected payloads/descriptors must preserve prior state; package rollback must not claim to undo arbitrary service or external effects.

The boot-artifact demo is proven for the recorded pair. General package installation and sys-init activation remain unproven; see [the service-side proposal](SERVICE-HANDOFF.md).

Aether-userland selects what belongs in the base install; pkg-mgr supplies the build, artifact and state mechanisms. Keep candidate package names separate from approved base membership. The zlib/zpipe host experiments establish no target ABI or base inclusion. A future base-set handoff should start with explicit package names and target requirements, once that project has selected them.

[Read-only update preflight](UPDATE-PREFLIGHT.md) now reports proposed differences and installed-drift/reverse-dependent blockers. It does not apply replacements.

[Configuration/replacement policy](REPLACEMENT-POLICY.md) defines implemented three-way comparison and conservative local-file preservation. Its retained-payload private-root replacement is now implemented with prepare/finish commands, pinned recovery and a pending-state guard; pruning and live-prefix writes remain unimplemented.

## Origins source-distribution consumer proposal

The [consumer review](ORIGINS-CONSUMER.md) separates origins publication from local
trust, execution and package state. It records required schema/identity/resource
clarifications and an offline integrity-only first handoff. No runtime adapter or
shared ownership revision is implemented. Existing package formats remain authoritative.
