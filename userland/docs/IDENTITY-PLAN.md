# UL-010 identity and session planning

Status: initial local contract inventory, 2026-09-07. Implementation and
independent review pending. All cases below are **NOT RUN**.

The canonical [post-R1 identity direction](../../../Aether-standards/docs/POST-R1-IDENTITY.md)
places IAM-01–07 after R1's persistent shell milestone. This records userland's
planning slice without enlarging R1 or selecting an authentication backend.
The pinned [ID-01–05 profile](vendor/aether-distribution/v0.1.0/IDENTITY.md)
remains unchanged. This document maps consumers and gaps; shared normative
requirements remain in Aether-standards and need its versioned adoption process.

## Current evidence and boundaries

The [native C fixture](../../docs/NATIVE-C.md) supplies developer bootstrap
identity and host-generated inputs. It is not an authenticated login or a native
entropy witness. Its successful C execution cannot satisfy any case below.
[Sys-init Runtime v0](../../sys-init/docs/specs/RUNTIME-V0.md) distinguishes
adapter authority from textual IDs (R-01), stale generation evidence (R-09),
operation acceptance from cleanup (R-15), and read from mutation authority
(R-18). Those lifecycle contracts do not define an authentication backend.

Sys-init's [BG-046](../../sys-init/.planning/backlog/captured/BG-046--define-policy-enforcement.md)
tracks policy families and enforcement availability;
[BG-051](../../sys-init/.planning/backlog/captured/BG-051--specify-recovery-workflows.md)
tracks authorized recovery with missing shell/console/storage. Both inspected
records are captured work, not accepted recovery implementations. The exact
inspected input hashes are retained in [planning evidence](evidence/identity-planning-2026-09-07/README.md).

## Decisions required before the first native experiment

| Decision / central handoff | Owner coordination | Userland consumer requirement and unresolved choice |
| --- | --- | --- |
| Principal and UID/GID compatibility / IAM-01 | Aether, userland, domain owners | Specify trusted principal-to-UID/GID projection, unmapped identities, group changes and unsupported identity setters. Numeric equality, including UID 0, supplies no native grant. Exact representation/API remains open. |
| Policy and task roles / IAM-01/04 | Aether, distribution policy owner | Select one administrative operation and target with separate inspect/mutate rights; define policy revision and delegation limits. Role names and policy-service home remain unselected. |
| Session and inherited authority / IAM-01/03/05 | Aether, sys-init, process/FD/TTY owners | Bind principal, policy revision, namespace, resource domain and initial grants. Define exec/child/FD transfer, credential-change and logout semantics; enumerate actual children and delegated work through incomplete cleanup. |
| Local verifier and enrollment / IAM-02 | Distribution owner, Aether, userland; service placement by agreement | Select maintained verifier code/parameters, trusted storage, secure input, RNG and any clock requirements. Define enrollment, credential change, attempt bounds and secret-erasure limits. No algorithm or backend selected here. |
| Startup and backend failure / IAM-03/05 | sys-init with verifier/session owners | Require readiness and failure behavior; restart cannot revive stale authorization. Diagnostics must remain usable without implicitly granting a shell. |
| Independent recovery / IAM-05 | Distribution and storage owners, sys-init, Aether | Decide verified payload, independent scoped authentication/delegation, physical-access assumptions, lost credentials and encrypted-data limits. Recovery cannot rely entirely on failed normal authentication. |
| Audit / IAM-04/07 | Policy/service owners and userland | Specify trusted principal/target/operation/policy/outcome fields, bounded retention and unavailable-sink policy; no credentials or usable grants in output. |

Service identity is independent of an interactive user's identity. Background
services need explicit authority and lifetime policy. A service intended to
outlive logout needs an authorized transfer of responsibility; inherited handles
alone are not that decision. Revocation cannot reverse already committed effects.

## First consumer witness and failure matrix

After owner decisions, select two principals and one scoped administrative
operation with exact producer/consumer/policy/verifier identities. Use disposable
target state. Define input bounds, rate limits, deadlines, cleanup inventory and
semantic error identities before implementing a harness. Missing infrastructure,
boot failure and timeout cannot count as the expected denial. No runnable login
command, protocol fields or error numbers are specified here.

| Case | Planned stimulus and independent expected observation | Prerequisite / clauses | Status |
| --- | --- | --- | --- |
| LI-01 | Enrolled principal authenticates and performs the selected operation on its authorized target; trusted audit and effects identify that principal and policy. | Selected native verifier, session and operation; ID-02/03/05, IAM-02–04 | NOT RUN |
| LI-02 | Other principal authenticates but cannot perform that operation or access another target; no unauthorized effect. | Native target/operation enforcement; ID-02/04, IAM-04 | NOT RUN |
| LI-03 | Supplied username, UID 0, service name or request identity conflicts with trusted caller context; reject attempted authority gain. | Trusted binding at enforcing endpoint; ID-01/02, IAM-01/03 | NOT RUN |
| LI-04 | Wrong secret, unknown principal and replay fail under reviewed attempt/enumeration policy; no credential or usable grant appears in logs. | Verifier/enrollment/replay contract; ID-03/05, IAM-02 | NOT RUN |
| LI-05 | Missing verifier, credential storage, required entropy or required clock prevents authentication; bounded diagnostics grant no shell. | Required backend/support inventory; ID-03, IAM-02/03 | NOT RUN |
| LI-06 | Child/exec/FD transfer and administrative environment manipulation cannot regain undeclared rights; allowed inheritance remains usable. | Process/FD/namespace contracts; ID-02, IAM-01/03/04 | NOT RUN |
| LI-07 | Concurrent sessions remain distinct; credential/policy changes and service restart reject stale session/request authority. | Explicit invalidation and admitted-work rules; ID-02/05, IAM-03–05 | NOT RUN |
| LI-08 | Logout/disconnect and worker/verifier failure inventory children, grants and delegated work; partial cleanup stays incomplete with an owner. | Lifetime and reclaim observations; ID-02/05, IAM-03/05 | NOT RUN |
| LI-09 | Authorized recovery works when normal authentication is unavailable; console/media possession alone grants no rights or encrypted-data access. | Independently usable recovery path and payload trust; ID-04, IAM-05 | NOT RUN |
| LI-10 | Audit storage unavailable or full produces the reviewed bounded outcome; inspect authority cannot mutate or erase authorization evidence. | Explicit sink-failure and retention policy; ID-05, IAM-04/07 | NOT RUN |

Host fixtures may later test request parsing or modeled transitions separately.
Native acceptance needs actual trusted identity, effects, denial and cleanup
observations. A denied request acknowledgment does not prove native reclamation.
Remote login, desktop lock, MFA and extra backends stay later IAM-06 scopes.

## Next action and acceptance routing

Review the principal/session contract first with the affected owners (IAM-01),
including current domain/resource contracts. Then select one local verifier and
enrollment policy with its RNG/storage/input prerequisites (IAM-02). UL-010
records those decisions and userland witnesses; it does not authorize changes to
sibling code. New shared requirements go through Aether-standards.

UL-009 owns TTY prerequisites; UL-003 covers native/service contract agreement;
UL-016 covers source and trust review; UL-012 consumes eventual assembled recovery
and session evidence. UL-010 remains active. Local M5's authenticated recovery
gate remains required for that claim; it is not evidence that R1 includes login.
