# UL-058 / UL-074 failure-control consumer review

Scope: independently consume four sealed sys-init ABI22 private images; no
maintained C/Rust runtime, shared API, pin or sibling changes. Local source review
is separate from independent reader review and SI-07 release disposition.

Pin producer seal 51362f77dbeef4b91fe8baeadc01c5355f08dd0c9631d0af40367a1346a62866
before consumption, complete base source archive and per-case overrides, ISO,
payload, owner raw/ELF, firmware, QEMU, Python and unchanged process helper.
Exact AENSI001 parent/child closure required. No rebuild/conformance claim.

Reuse the preceding sealed consumer boot lifecycle: 90-second QEMU deadline,
2 MiB serial cap, outer helper 120 seconds/16 MiB streams, inherited owned group,
terminate/wait/kill and checked outer cleanup. Four cases fit a ten-minute budget.
Send rh once after an actual request prompt and 200 ms wait; buffered h cannot
turn failure into successful shutdown. Check exact ordered markers, terminals,
release counts, assertions, no subsequent request/effect/replay/halt; corrupt
traces must fail the host oracle. Native Unknown evidence relies on source checks
behind the marker; it does not expose an independent second resource channel.

Applicable O-04, I-03–06, E-01–08, local developer-console applicability and CP/TE
profiles: retain uncertainty, deny replay, bound ownership and retain every attempt.
ASCII internal markers remain in existing Experience scope. No presentation
adoption. Third-party files retained verbatim with existing terms; new Python BSD-2.

Simpler alternative is reuse existing drivers with a small case-specific oracle;
chosen because the ownership/deadline primitives already satisfy the requirement.
No new runtime abstraction or cleanup removal. Quality/syntax/whitespace checks,
source/raw/ELF identity review and host corruptions required before completion.
Review performed by current Codex agent; independent technical/reader review
pending. Wider syscall/race schedules, production recovery, useful session,
service/configuration and assembled-image acceptance remain follow-ons.
