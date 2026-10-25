# UL-077 — relay directional EOF handling

Local review found that transport-relay.py closes both directions on EOF once the
current buffer drains. TCP half-close does not imply the reverse stream is done.
This can discard a response or later request and invalidate the fixture's transport
fault attribution. No production lifecycle/build behavior changes are proposed.

CP-01–03, O-04 and E-01–08 apply. Reproduce with real loopback sockets before editing:
request half-close followed by a large response; server half-close followed by a
late client request. Exact received bytes and peer completion are independent oracles.
Run baseline failures and final controls on 3.14.7, final controls on 3.10.21. Relay
startup/termination and fixture server waits remain bounded; retain outputs/errors.

Implement directional read EOF and deferred write shutdown after queued data drains.
Keep the reverse direction alive and close the pair only when both read directions
end and both queues empty. Preserve limits, no payload logging and loopback-only use.
Retain original source/evidence. Run local quality and whitespace checks. VM is still
stopped, so live Podman qualification remains incomplete; no VM startup or sibling
change. Independent review and in-flight create-response tests remain open.
