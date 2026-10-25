# Package/service handoff proposal

> Shared-standards migration, 2026-09-05: [Foundations adoption](STANDARDS.md) now routes the canonical shared ownership, interface and evidence rules. The [consolidated PS-01–PS-11 proposal](vendor/aether-foundations/v0.1.0/proposals/PACKAGE-SERVICE.md) is the canonical shared package/service proposal for future review; it remains candidate. The original report below is retained as dated source evidence, including its historical progress descriptions. Consult current STATE and domain contracts for implementation status.

Reviewed: 2026-09-05. Package-side proposal only; not an accepted shared API. Sys-init's current STATE identifies BG-027 (package/service artifact and lifecycle contract) as its next task. Its runtime checklist and boundary synthesis exist, but no implementation, descriptor syntax, validator command, or service runtime exists there yet.

## Ownership boundary

| Data or action | Owner | Current pkg-mgr behavior |
| --- | --- | --- |
| Staged payload and package/file ownership | pkg-mgr | Hash-bound regular-file records |
| Requested package set (`world`) | Operator through pkg-mgr state | Editable package IDs, never service enablement |
| Descriptor schema/version and validation semantics | sys-init | Pending BG-027; no parser or syntax invented here |
| Enabled service set | Operator through future sys-init interface | No state or command implemented |
| Live service identity, readiness, restart/reload | sys-init with Aether runtime primitives | No activation side effects |
| Capability grants, task/loader/IPC mechanisms | Aether | Names and package metadata convey no authority |

A future handoff must identify the owning package, exact descriptor bytes/path, schema version and service identity, with a validator result tied to those bytes. This describes required information, not a chosen serialization. Keep installed artifacts, enablement intent, and observed runtime status separate. Requested package dependencies are not service startup ordering.

## Concrete lifecycle cases to agree with BG-027

| Trigger | Proposed result | Current boundary |
| --- | --- | --- |
| Register a package containing an ordinary descriptor file | Record byte ownership only; no enable/start request | Regular files can be inventoried; no service validity claim |
| Validate an unknown/malformed descriptor version | Reject before changing enablement or runtime; preserve prior state | Validator/schema absent, so service validation is unsupported |
| Install a valid but disabled service | Leave it disabled and stopped | Live installation and service state are both unimplemented |
| Explicit operator enable/disable | Change sys-init-owned intent through its defined authority boundary | No command or implicit mapping from `world` |
| Explicit activate/reload/restart | Separate authorized sys-init operation against validated identity/bytes | Package registration cannot request it |
| Upgrade/removal while enabled or running | Preflight ownership and lifecycle policy; preserve a recoverable prior state on rejection | Package update/remove and lifecycle transactions remain deferred |
| Interrupted operation or rollback | Distinguish published package state, enablement intent, and live side effects; never claim arbitrary effects are undone | No rollback API or runtime reconciliation implemented |

These cases need executable shared fixtures once sys-init selects its contract. At that point test malformed/duplicate service identities, unknown versions, ownership conflicts, activation without authority, interrupted publication, and stale validator results. Candidate file paths must be bound to pkg-mgr's payload evidence; they must not be evaluated as shell code merely because they arrive in a package.

## Present evidence and remaining work

The boot handoff receipt fixes `service_activation=unsupported`; changes and unknown fields are rejected by its tests. This is a transport guard, not a service validator. Aether's existing image builder consumed a pinned staged boot pair and passed smoke, but that pair is a Limine kernel/module input, not a sys-init service.

BG-027 must supply the service artifact/validator and enablement contract; Aether must supply the required loader/lifecycle/authority mechanisms. Revisit the projects' current docs before implementing an adapter. Their missing interfaces do not justify inventing a POSIX process model, ambient root shortcut, or native package installation API in this repository.
