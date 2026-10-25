# Package and service lifecycle boundary

> Shared-standards migration, 2026-09-05: [Foundations adoption](../STANDARDS.md) now routes the canonical shared ownership, interface and evidence rules. The [consolidated PS-01–PS-11 proposal](../vendor/aether-foundations/v0.1.0/proposals/PACKAGE-SERVICE.md) is the canonical shared package/service proposal for future review; it remains candidate. The original report below is retained as dated source evidence, including its historical progress descriptions. Consult current STATE and domain contracts for implementation status.

Date: 2026-09-05. BG-027 research complete, refreshing BG-011. This is a proposed semantic contract; no schema syntax, CLI, installer, or cross-project API is implemented or accepted by this document.

The recommended division is: pkg-mgr owns package payload and package ownership evidence; sys-init owns service validation and lifecycle state; administrator/distribution policy owns enablement choices; Aether enforces runtime authority. Installing a definition should not implicitly enable, start, reload, or restart it. A separately authorized operation may combine these steps while reporting each result.

## Current evidence

pkg-mgr now has [staged package records](../../../pkg-mgr/docs/PACKAGE-STATE.md), beyond the older text-file build demo. Its [state.sh](../../../pkg-mgr/mk/state.sh) and [schema validator](../../../pkg-mgr/mk/state-schema.awk) register matching regular-file manifests/build evidence, reject ownership conflicts, and derive package dependency views. Identical registration is idempotent; changed evidence for an existing name is rejected. No live install/update/remove or service activation API exists. Record content is not evaluated as shell code.

The current format records hashes, sizes and paths, but not executable modes, ownership bits, symlinks or configuration semantics. Thus a file hash cannot establish an executable service artifact or installation authorization. Single-writer adjacent-file publication is not a multi-project transaction or power-loss recovery guarantee. See [pkg-mgr architecture](../../../pkg-mgr/docs/ARCHITECTURE.md) and [source manifest](PACKAGE-SERVICE-SOURCES.json). Source was inspected; companion tests were not rerun.

Aether's [runtime checklist](AETHER-RUNTIME-CONTRACT.md) identifies fixed-image launch and missing general loader/ABI, grants, readiness and recovery contracts. A staged native artifact can be inspected without being launchable. sys-init currently has research only, so pkg-mgr must not call an invented validator or advertise service integration as implemented.

## Prior-art findings

| Evidence | Finding and implication |
| --- | --- |
| [Debian policy, service interfaces](https://www.debian.org/doc/debian-policy/ch-opersys.html#interfacing-with-init-systems) | Enablement and live actions use separate helper interfaces; lifecycle requests pass through local policy. Borrow mediation and explicit action results, without importing Debian's activation defaults. |
| [systemd preset manual source](https://raw.githubusercontent.com/systemd/systemd/main/man/systemd.preset.xml) | Preset policy can be centralized in a distribution and overridden by administrators. Service payload should not silently overwrite site policy. |
| [FreeBSD Porter's Handbook](https://docs.freebsd.org/en/books/porters-handbook/book/) | The rc-script example defaults enablement off, and ports are instructed not to start/stop services during install/deinstall. Separating file operations from live actions has established precedent. |
| [illumos svccfg manual source](https://raw.githubusercontent.com/illumos/illumos-gate/master/usr/src/man/man8/svccfg.8) | Validation can run without import; import preserves administrator enablement/restarter choices and reports conflicting changes. Validation and administrative policy deserve independent treatment. |
| [POSIX boundary research](BOUNDARY-HANDOFF.md) | Shell/file primitives can implement tooling, but no POSIX package/service transaction protocol follows from them. Atomic rename alone does not solve cross-record recovery. |

External primary sources consulted 2026-09-05. Debian policy identified version 4.7.4.1; FreeBSD evidence was available through indexed handbook text; systemd and illumos moving manual sources were readable. These are comparative inputs, not portable APIs. The proposal below is our synthesis, not a claim that these systems share identical semantics.

## Ownership and state

| Fact | Proposed authority | Required distinction |
| --- | --- | --- |
| Package ID/revision, payload and file owner | pkg-mgr | Package dependency satisfaction does not prove a service is ready |
| Service definition and validation result | sys-init, consuming package evidence | Valid syntax is separate from supported target, policy permission and activation |
| Vendor suggestion / distribution defaults | Distribution policy, optionally informed by package metadata | A suggestion cannot replace explicit operator intent |
| Enablement and local overrides | Administrator policy through sys-init | Enabling schedules future policy-driven activation; it does not itself start now |
| Selected definition generation | sys-init configuration authority | Can differ from running instance generation |
| Runtime instance, readiness, stop/restart result | sys-init via accepted Aether or host interface | Package registration and hashes do not grant capabilities |
| Service data and diagnostic history | Explicit data/retention policy | Remove is not purge; no implicit deletion of user data |

Recommended default: preserve explicit enable/disable and overrides through upgrades; do not reapply presets during routine upgrade. Disable prevents future automatic activation, but is not automatically a prohibition on explicit start or dependency activation. Exact enable/disable/mask vocabulary and dependency behavior must be settled in BG-037. This distinction must be visible before any API is implemented.

## Candidate artifact and validation contract

PS IDs are requirement questions, not wire fields or commands.

| ID | Candidate information / behavior | Acceptance boundary |
| --- | --- | --- |
| PS-01 Identity and ownership | Stable service ID, owning package ID/revision, descriptor path/digest, schema version | A package may own multiple services. Reject duplicate service ownership even if descriptor paths differ. Renames/transfers require explicit migration. |
| PS-02 Launch profile | Artifact reference/digest, target architecture/runtime ABI, structured arguments and environment, cwd and runtime prerequisites | Keep host tools separate from target artifacts. Do not infer executable permissions, ABI or authority from hash matches. |
| PS-03 Lifecycle metadata | Service kind, typed dependencies, readiness/stop requirements and bounded restart policy | Refer to BG-023/BG-022 semantics; no arbitrary package hook execution during parsing or validation. |
| PS-04 Requested authority | Declared dependency/resource needs | These are requests resolved against operator policy and runtime grants, never capabilities encoded as package data. |
| PS-05 Parsing/version rules | Bounded inert representation and explicitly supported schema/profile | Reject malformed, duplicate and unknown semantic fields or unsupported versions. Optional descriptive extensions need a specified namespace; never silently ignore a control field. Syntax remains BG-035 work. |
| PS-06 Validation levels | Structural validity; package binding; graph validity; target support; policy eligibility | Return each level and reason separately. An offline-valid artifact may remain target-unsupported or pending activation. No blanket “valid” implies runnable. |
| PS-07 Configuration composition | Vendor definition plus explicit local override and enablement generation | Validate the effective definition too. Conflicting overrides block selection; preserve previous valid generation and explain conflict. |
| PS-08 Queries | Owner, installed/selected/running revisions, enablement source, effective definition, dependencies, pending actions, action result | Queries must distinguish stale/unknown runtime evidence from stopped and distinguish restart-needed from failed. |

Validation must bind exact candidate bytes and ownership evidence to the effective graph/policy/target profile evaluated. Recheck those preconditions before publication or activation. A stale plan must be rejected or recomputed, not applied against a changed administrator choice. Hashes aid consistency, not authenticity; pkg-mgr remains responsible for its separate trust/eligibility policy.

First schema experiment should consume separate inert descriptors as ordinary staged files. Do not add undeclared rows to `pkg-state-v1`, whose current parser rejects unknown rows, or assume its advisory build record proves activation permission. Exact path layout, serialization, override precedence, optional fields and program mode metadata remain BG-035/BG-014 work.

## Lifecycle examples and failure outcomes

The fictional `clock` service below illustrates behavior only; names are not a chosen service-ID grammar. These are proposed semantics, not commands to execute.

| Operation | Proposed behavior | Example / failure outcome |
| --- | --- | --- |
| Stage and validate | Read candidate evidence without changing selected definitions, enablement or processes | Package v2 has an unknown control field: reject it; v1 remains selected/running |
| Install/register definition | Publish accepted package/definition state through the future coordinator; leave operator and runtime state unchanged | New clock v1 is installed, not enabled, with no instance |
| Apply defaults | Separate policy operation with recorded provenance; explicit operator choice wins | Distribution recommends clock, but an explicit disable remains effective |
| Enable | Change future activation policy after effective graph validation | Clock becomes enabled; start-now remains a separate request |
| Disable | Change future automatic policy; report any remaining runtime/dependency effects | A running clock stays running until a separately requested stop; removal cannot assume otherwise |
| Explicit start | Resolve grants and runtime support, create a current instance, enforce readiness contract | Missing loader or required grant fails with a reason; no fictitious running state |
| Upgrade, no live action | Validate candidate and overrides; preserve selected/running revision distinction and required old artifacts | v2 selected, v1 running, restart pending; if old payload retention cannot be guaranteed, defer/refuse the upgrade |
| Reload | Only request a supported reload with defined completion/compatibility semantics | Accepting a signal/request is not reload completion; executable replacement alone is not a reload |
| Restart | Planned stop then new launch/readiness, with affected dependencies identified | v2 fails readiness after v1 stops: report v2 failed and v1 stopped; do not claim rollback restored service |
| Rollback | Restore compatible configuration/artifact selection under explicit policy, then separately reconcile runtime | Database migration may prevent safely running v1; record intervention required, not automatic reversal |
| Remove | Plan reverse package and service dependency impact; establish stop/quiescence and payload retention/release rules first | Reject removal if still running, required dependents remain, or runtime state is unknown; stage a separate explicit stop/removal plan |
| Purge / rename / owner transfer | Separate explicit migration/data operation | Preserve local data and disable intent by default; reject service-ID takeover without a migration contract |

Retention must cover more than an open executable: loaders, libraries, helper programs and runtime data dependencies may still require old files. Aether has not established that storage/runtime contract. A conservative first implementation can refuse live replacement/removal rather than promise concurrent revisions. A package “orphan” report is not authorization to remove a running or enabled service.

## Publication and interruption proposal

PS-09: a future coordinator should prepare an inspectable plan containing operation identity, old/candidate package and definition generations, graph/policy inputs, proposed live actions and recovery obligations. The plan is data, not a package-supplied script. Permission to install does not imply permission to restart; combined authorization must identify both.

PS-10: commit and recovery must specify authoritative records, writer coordination, durable progress and ordering before implementation. Do not claim an atomic operation spanning package records, sys-init configuration, Aether tasks and external effects. Proposed checkpoints:

| Interruption point | Required recoverable observation |
| --- | --- |
| Before publication | Old accepted state remains; candidate is unselected |
| Package evidence published but service selection incomplete | Explicit pending reconciliation; inhibit activation of an unvalidated/mismatched generation |
| Definition selected, no live action dispatched | New selection and old/no instance reported separately; action remains pending |
| Stop/start/reload dispatched, reply lost | Query actual instance/operation state; report unknown if it cannot be recovered; never blindly repeat a side-effecting action |
| Action failed | Preserve both operation failure and actual running state; apply only explicitly supported compensation |

Operation IDs alone do not provide exactly-once execution. BG-036 must determine acknowledgment/deduplication retention and how restart after coordinator death works. Queries and guarded reconciliation are needed before safely retrying. BG-031 owns storage guarantees; BG-032 owns native instance observation. Until these exist, the checkpoint table is a requirement, not an available transaction engine.

## First fixtures and follow-ons

PS-11: proposed host fixture corpus for BG-035/BG-036: valid package with multiple services; duplicate ID across packages; descriptor digest mismatch; shell-shaped inert values; unknown version/field; missing provider/cycle; preserved administrator disable; conflicting override; unsupported target ABI; candidate change after validation; changed executable modes not represented in package evidence; upgrade with running old revision; failed readiness; ambiguous action reply; blocked removal; rollback after incompatible data migration.

Each fixture must assert package evidence, selected definition, enablement, runtime observation and action result separately. Parser fixtures execute no hooks or lifecycle actions. Lifecycle simulations use labelled fake instances; only a later accepted Aether seam can demonstrate target behavior. No sys-init executable or fixture runner is introduced by this research item.

New stories captured before completion: BG-035 descriptor/profile/schema and inert validation fixtures; BG-036 package/service publication and interruption protocol; BG-037 defaults, enablement and override semantics. Existing BG-014, BG-023, BG-027's runtime prerequisites BG-032/BG-033, and BG-031 retain layout, lifecycle, target and durability scope. OQ-002 stays open, now decomposed; OQ-012 and OQ-013 capture cross-project recovery and running-artifact retention.

BG-027 is complete as research: ownership, candidate artifacts, version/validation behavior, all requested lifecycle cases, rollback/authority limits and test follow-ons are recorded. This is not cross-project acceptance. Next is BG-003 boot-stage research, incorporating these package and Aether constraints. Stage 2 remains open; there is still no implementation architecture selection.
