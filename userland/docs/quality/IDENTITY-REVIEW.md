# UL-010 principal/session consumer proposal

Prepared 2026-09-07 for affected-owner review. Status: **proposed; zero owner
approvals recorded**. This is userland's requested consumer behavior, not a
shared standard, protocol or implementation authorization. Native LI-01–10 remain
NOT RUN in the [identity plan](../IDENTITY-PLAN.md).

## Recommended first scope

Use two enrolled local principals, two disposable long-running test services and
one delegated operation: restart one specified owned live service generation.
Grant principal A that operation on service X; principal B receives status-read
access only. A's grant does not cover service Y. Successful authentication alone
gives neither principal restart authority. Names A/B/X/Y label the experiment;
they are not proposed account IDs, role names or authority-bearing strings.

This operation reuses [sys-init R-14](../../../sys-init/docs/specs/RUNTIME-V0.md):
restart means completed stop/reclaim followed by fresh launch. A one-shot or an
absent service is ineligible; unresolved cleanup prevents replacement. It does
not implement recovery of an absent service. Broader recovery remains LI-09 and
BG-051. Owner review must confirm a native operation endpoint can enforce this
scope before a userland administrative client is built.

Recommended first-slice exclusions: authorization caching, arbitrary administrative
shell execution, remote login and general authentication plugins. They can receive
separate requirements later. Keep the selected local verifier behind a narrow
interface; this proposal does not select its process home or implementation.

## Consumer decisions proposed for IAM-01 review

| Topic | Proposed consumer behavior | Decision required from owners |
| --- | --- | --- |
| Trusted principal | Obtain identity from the verified session context at the enforcing endpoint. Supplied usernames and numeric IDs remain untrusted lookup/display inputs. | Aether and policy/verifier owners: how is the binding established, protected, checked and invalidated? |
| UID/GID projection | Expose a stable, session-scoped compatibility view where supported. Treat UID 0 like any other numeric label for native authority. No successful placeholder identity-changing calls. | Userland/Aether: accepted mapping scope, unmapped values, supplementary groups, setter support and exact libc errors; do not freeze numbers here. |
| Session creation | Publish a usable session only after principal verification, policy selection, domain/namespace binding and initial grant setup succeed. Roll back partial setup while retaining ownership of uncertain cleanup. | Session/service owners: allocation bounds, readiness contract, setup order, cleanup observation and failure errors. |
| Inheritance | Default-deny undeclared child/exec/FD authority; allow explicitly reviewed inheritance within the same scope. Same numeric identity does not authorize transfer across sessions. | Aether/process/FD owners: atomic restriction enforcement, transferable objects and revocation limits. |
| Resource domain | Preserve the authenticated request's accountable domain through service work and cleanup. Logout cannot discard charges for retained work. | VIR-01/02 owners: trusted domain binding and charge transfer; native C's bounded execution domain alone does not establish the future hierarchical accounting model. |
| Revocation | Close admission for invalidated sessions/policy revisions; do not promise to undo committed effects. Retain already-admitted operations under their owning manager until terminal observation and cleanup. | Policy/Aether/sys-init: linearization point, in-flight effects, credential-change scope and service-restart invalidation. |
| Logout/disconnect | Stop admitting session work, apply the reviewed policy to actual children and delegated operations, and retain incomplete outcomes. Outliving services require an explicit authority/lifetime transfer. | Session/sys-init owners: distinguish logout cancellation policy from transport disconnect; R-15 says a client disconnect does not cancel manager work. |
| Request replay | Bind the request to trusted session, exact target/generation, operation and applicable policy. After an ambiguous result, query the owned operation rather than blindly restarting again. | Sys-init BG-050 and authority owners: deduplication, retention, stale-generation rejection and safe recovery after manager restart. |

The [approved IAM direction](../../../../Aether-standards/docs/POST-R1-IDENTITY.md)
and [VIR-01/02 direction](../../../../Aether-standards/docs/POST-R1-VIRTUALIZATION.md)
are planning inputs. Native thread IDs in
[Aether's current C contract](../../../docs/NATIVE-C.md) are bounded,
reused context labels; they cannot substitute for a stable authenticated principal
or a session lifetime. Future shared contracts go through Aether-standards review
and versioning. No release pin changes are proposed here.

## Concrete observations for the two-user experiment

Use exact producer, consumer, verifier, enrollment/policy and image identities.
Define time/resource limits before execution; no production accounts or services
are involved. The enforcing service must observe the real authenticated caller.
A host fixture with hard-coded principals cannot satisfy this native witness.

1. A requests restart of X. Observe one accepted operation, terminal old generation,
   completed reclaim and fresh generation; verify the trusted principal/policy in
   bounded audit output. Acceptance acknowledgment alone fails LI-01's success oracle.
2. B requests restart of X, and A requests restart of Y. Observe semantic denial,
   unchanged generation and no unauthorized effect, while authorized status remains
   usable (LI-02). Test direct endpoint requests as well as any future client path.
3. Supply A's display name or UID 0 from B's session. Observe that trusted caller
   context remains B and the operation stays denied (LI-03).
4. Pass undeclared handles or manipulated administrative environment through child
   creation/exec. Observe denial at the enforcing boundary; preserve permitted
   inheritance controls (LI-06).
5. Replay a request against an old generation or invalidated policy/session, and
   repeat a request after an ambiguous connection outcome. Observe the agreed
   stale/deduplication behavior without an extra restart (LI-07).
6. Interrupt logout or inject worker/verifier failure during admission and teardown.
   Observe retained ownership, bounded cleanup and no replacement while cleanup is
   incomplete; inspect outstanding charges and operations (LI-08).

LI-04/05 still require the selected verifier and enrollment/RNG/storage support.
LI-09 needs independently usable authorized recovery. LI-10 needs an agreed audit
failure policy. No planned case is waived by selecting a smaller first operation.

## Verifier selection entry criteria

Before recommending a library or password scheme, record the qualified native
randomness API/readiness, credential storage and durability/access boundary,
secure input ownership, required clock semantics, enrollment/recovery policy and
resource budget. The [RNG direction](../../../../Aether-standards/docs/POST-R1-RANDOMNESS.md)
explicitly excludes deterministic bootstrap fallback for production secrets.
The current [distribution status](../../../../Aether-dist/.planning/STATE.md) does
not establish an assembled authenticated userland profile.

Once these decisions exist, compare maintained implementations against their exact
source/license pins, parameters, dependencies, failure behavior and integration
cost. Select one with owner review, then qualify wrong/unknown credentials,
credential change, replay, attempt limits and backend failures. A library name
or host success cannot establish native login acceptance.

## Review disposition required

| Reviewer role | Concrete disposition requested | Current evidence |
| --- | --- | --- |
| Aether / enforcement and domains | Accept or revise trusted principal/session/domain binding, inheritance and invalidation semantics; identify exact producer contract. | Pending |
| sys-init / lifecycle | Accept or revise target-scoped restart, operation retention, logout/disconnect and cleanup observations; route BG-050/046/051 dependencies. | Pending |
| Distribution / enrollment and recovery | Select first local enrollment/recovery policy and applicable trust/storage/input prerequisites. | Pending |
| Userland / libc and application | Review UID/GID compatibility and first-client scope against actual process/FD/TTY support. | Pending |
| Independent technical and reader review | Check authority boundaries and whether the proposed handoff is unambiguous; record reviewer, revision, findings and disposition. | Pending |

No messages or changes to other owners' tasks were made by preparing this packet.
[Evidence](../evidence/identity-review-2026-09-07/README.md) retains the inspected
source hashes and local documentation checks. UL-010 stays active pending these
decisions; this packet makes the next review concrete without claiming agreement.
