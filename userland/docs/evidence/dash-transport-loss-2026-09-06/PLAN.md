# UL-077 — live transport loss after creation

Test-only loopback TCP relay forwards opaque SSH bytes to the existing Podman
endpoint. The existing adapter uses one frozen relay URL. After confirmed container
creation/inspection, stop the relay before attach; the actual client must receive a
connection failure and remote cleanup must stay unresolved. No mocked client result,
shared-service interruption, VM restart or unrelated-container operation.

A separate recovery connection to the original endpoint must inspect exact owned
name/label/ID, remove that container and verify absence. Keep the original unresolved
receipt unchanged. This witnesses transport unavailability, not daemon failure or
an in-flight/lost create response. That latter ambiguity remains separate work.

CP-01–03, O-03/04 and E-01–08 apply. The relay owns only loopback sockets, no payload
logs and no private-key reads. Bound lifetime to 60 seconds, concurrent socket pairs
to eight, each pending relay buffer to 1 MiB, input chunks to 64 KiB. Parent records
relay executable/source/argv, bounded startup/termination, raw client receipts and
exit. Relay startup failure is not the intended transport denial.

Run on Python 3.14.7 and qualified 3.10.21 against the existing pinned image. Prove
successful pre-cut remote creation, post-cut client failure, original unresolved
status, owned recovery and independent absence. Quality/whitespace gates; preserve
all attempts. No maintained runtime/adapter behavior changes. Independent review,
true create-response ambiguity and broader UL-061–063 remain open.
