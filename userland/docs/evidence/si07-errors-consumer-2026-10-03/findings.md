# Source and evidence findings

The sealed base connection_owner.rs retains a reader/worker Option until its
native release succeeds. cleanup validates the owner/key, observes a real
terminal, closes endpoints and reclaims the worker. A fault records first/latest
errors; Unknown prevents cleanup, stop and start from issuing another native
operation. The probes test exact operation/errno/resources before their marker.
Close: actual reader close outside ownership succeeds; subsequent owner close
returns EACCES13, retains reader+worker. Reclaim: external terminal reclaim
succeeds; subsequent owner reclaim returns EBADF9, retains worker after endpoint
closes. Both then execute the original fatal unwrap; neither recovers.

The lost-image original transfer accumulator caps actual reads to16 bytes.
For backend write operation4 it checks that the consumed first16bytes report
2bytes accepted, then closes the real borrowed reply reader. The next native
read fails; backend_exchange returns false and backend assertion952 ends the
fixture. There is no retransmission of that request or successful complete/halt.
Split uses the same accumulator without induced loss, requiring the full32bytes
before a successful return. This covers an accepted write effect and deliberate
reply-reader loss, not spontaneous kernel ambiguity, durable storage or recovery.

Each image binds the exact v2 runner and child through the AENSI001 envelope,
verified again against payload extracted from the actual pinned ISO. Fresh ELF
header/section/relocation inspection accompanies exact raw/ELF identities; stack
estimates2776/2776/2808/2808 are reused from sealed producer models. Their indirect
builtin bindings and limitations are retained, not independently all-path proved.
No fresh compilation or POSIX-conformance claim is made.

An initial host inspection script mistakenly treated helper stdout bytes as a
Path. readelf had completed; native execution was unaffected. The failed script,
receipt and correction are retained. The corrected attempt decodes bytes and
uses new labels to preserve the first receipt. No guest retry was needed.

The consumer oracle checks exact failure trace order, exact release counts2/3,
absence of a second request, command completion, backend terminal or authorized
halt, and split's bound issued/prefix pairs before transitions. Internal marker
claims rely on inspected source assertions; they are not a separate independent
native resource-observation channel. Host trace corruptions test the oracle,
not additional native schedules. Wider races, native malformed/stale/foreign and
child-profile schedules, useful-session integration and independent review remain.
