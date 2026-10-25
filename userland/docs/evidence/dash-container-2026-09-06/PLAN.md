# UL-077 — explicit remote lifecycle prototype

First slice: implement and qualify a separate Python 3.10+ experiment adapter before
integrating dash build/test launchers. Separate create/start/remove; record random
attempt name and label before creation, bind returned immutable ID to inspection,
and use one explicit URL/identity/client digest throughout. Existing pinned image,
no pulls/network, non-root UID, read-only root, dropped capabilities and memory/PID
bounds. Only attempt-owned containers may be removed. No VM/service mutation.

CP-01–03, O-03/04, E-01–08 and local UL-063 apply. Reuse existing local process
helper unchanged; local cleanup is necessary but not remote absence. Use per-call
management deadlines, output bounds and receipts. Always attempt bounded cleanup
after create/start errors. A failed/unfinished create response is ambiguous even
if a later exists query reports absence; keep it unresolved. Labels identify our
trusted attempt, not authority against a malicious daemon or competing principal.

Controls: modeled success, nonzero guest, start timeout, foreign identity, service
loss, removal failure, ambiguous create/absence, preexisting name and late surviving
container. Real existing-VM controls: success, guest nonzero, timeout then forced
removal, followed by independent absence queries for exact attempt names/IDs.
Model controls do not qualify daemon failure or transport races. Keep raw streams,
client/source/image/connection/tool identities and every failure. No secrets copied.

Run model controls on 3.10.21 and 3.14.7; quality gate and whitespace. Live tests use
current host Python/client, explicit connection and immutable image only. Independent
review, true remote service-loss/ambiguous-create witnesses, launch integration and
full dash regression remain pending. No publication, native or whole-suite claim.
