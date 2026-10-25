# 0035 — Trusted single-binding authority model

Accepted for BG-050 A01–A03, 2026-09-06. Add AuthorizedStream on the existing
bounded stream, with no native endpoint, identity verifier or new wire error.
The unguarded model/Delivery/Stream APIs remain trusted test tools, not external
entry points. A caller with direct object access can bypass this policy model.

Bootstrap supplies one exact opaque object binding representing one fixture
client generation, a bounded policy revision, allowed mutation verbs, mutation
service scope and independent observation scope. Copy scopes into immutable sets
after checking at most eight existing names and three verbs. Empty scopes are
allowed and deny their respective activity. Bind to the original model epoch and
configuration revision. Mutable policy updates are unsupported: create a reviewed
replacement lifetime, not an in-place widening. No constructor default grants
authority and invalid policy must not claim the Model's Control.

Every feed/read/reconnect/direct observation checks binding identity first.
Missing/foreign binding raises local Denied('authority') without changing the
legitimate connection. A changed manager epoch/configuration invalidates the
binding by revocation. Revocation is an owner-side trusted action, monotonic and
immediate: discard partial input and unsent output by disconnecting; retain
receipts, high-water sequence, effects and owned workers. Already emitted bytes
cannot be recalled. Same-binding ordinary reconnect preserves history; revoked
or foreign binding cannot reconnect. This does not demonstrate native reassociation.

For complete valid mutation payloads, check allowed verb and the full dependency
closure for start, explicit scope for stop, entire validated domain for shutdown.
Denial closes this connection without reply, effects or sequence consumption.
Payload parsing/logical errors retain the existing fixed error path. Replays are
authorized again. Generic transport errors contain no private operation snapshot.

After admission, receipt disclosure separately checks observation rights for its
operation snapshot, including a conflicting active operation. Null-operation
receipts/unknown observations conservatively require whole-domain observation
scope, so lookup retention cannot disclose records through a partial scope.
Output denial closes without a reply but must not roll back cached sequence or
discard effects of an already authorized mutation. Check the immutable scope
again before each output chunk. No successful receipt implies completion.

Direct observe/wait helpers apply the same disclosure gate to detached snapshots;
they add no wire request format. Mutation permission never grants read permission.
Denied carries no caller, service, operation or exception detail and is not a new
network error code. The chosen close-on-denial policy precedes future transport
adoption; external error responses need their own reviewed contract.

Test invalid bootstrap, foreign binding, payload impersonation, dependency closure,
stop/shutdown scope, independent observation, out-of-scope conflict disclosure,
cached-sequence preservation after output denial, revocation before/after dispatch
and partial output, same-binding replay and stale configuration. Add a binding
identity mutation control. Run model/full checks and retain evidence. Native
binding/enforcement and driver acknowledgment/recovery remain BG-032/BG-033 gates.

Result: [retained evidence](../evidence/control-authority-model-2026-09-06/README.md)
passes 110 model tests/ten controls, 48 host tests, 37 harness tests and all offline
gates. Removing binding comparison causes an assertion failure. Native audit
checks 215 historical outcomes; no new native execution or authentication claim.
