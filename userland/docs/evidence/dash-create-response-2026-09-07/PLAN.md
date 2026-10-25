# UL-077 — lost in-flight create response

Extend only test fixtures. An optional relay fault mode delays opaque server-to-client
bytes during create. A separate bounded observer uses the original connection to
verify a real created container's name/label/ID, writes a witness, then requests the
relay close its sockets. No synthetic client status, shared-service stop or PID-based
third-process kill. If the create response arrives before the cut, the test must fail
rather than claim ambiguity.

The unchanged adapter must retain create_attempted=true, create_confirmed=false,
complete=false and unresolved cleanup. The actual create client's response must fail
and provide no successful ID. Separate recovery validates the witness/owned container,
removes it and verifies absence without promoting the original receipt. No guest is
started. CP-01–03, O-04 and E-01–08 apply. Preserve output/buffer/lifetime bounds,
loopback-only relay, no payload/key logging and exact input/client identities.

Run relay EOF regressions and both outage modes on Python 3.10.21/3.14.7, retaining
all failures and successful witnesses. Start the existing VM in the same execution
session if needed (user authorization persists). Pin image/client, no pulls/siblings.
Run quality/whitespace checks. This witnesses one response-loss schedule on a trusted
live backend; delayed future creation after an absence observation and daemon failure
remain distinct. Independent review stays pending.
