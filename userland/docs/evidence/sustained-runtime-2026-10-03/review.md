# UL-058 / UL-063 SI-07 client review, 2026-10-03

Technical reviewer: Codex, source inspection before behavior edits. Independent
reader and native implementation review remain pending; UL-063 stays active.

Scope: explicit NATIVE_SUSTAINED_V2 compile profile for the four-role parent,
two-role child, result decoder and complete static runner/bytecount artifacts.
Contract: SUSTAINED.md, AERIO002, NIO2 and 0x7b receipts, native cohort equality;
Aether review docs/evidence/si07-v2-review-2026-09-29/README.md is design clearance,
not runtime acceptance. Aether owns admission, grants, cohort selection, retirement,
cleanup and halt. sys-init owns eventual lifecycle policy. No sibling implementation.

Affected source review (UL-063 prerequisite): four-role and result decoders validate
complete records into local candidates before publishing. Both native adapters own
single-attempt bootstrap and poisoned transport; sequential trusted pointers only.
Transfer has 100000 attempts, writes at most7, reads at most5; data payload at most16.
Failed close consumes local binding before remote completion; unknown framing stops
subsequent transport. Runner admits once, polls at most100000, checks repeat ECHILD,
EOF and closes logical bindings. Native entry bootstraps before bytecount.
The generation syscall currently narrows long to unsigned before validation.
V2 must reject full-width values outside1..65535 before narrowing or record transfer;
legacy code is retained exactly. Child requires NIO2; parent requires AERIO002.
All profile-sensitive public symbols are versioned to reject mixed linking.
The startup parser, channel semantics, request layout and finite command remain
unchanged. No claims about arbitrary pointers, concurrent calls or kernel authority.

Applicable rules: Foundations O-01–05/I-01–06/E-01–08; Distribution NC/PX/OB
applicability map; approved CE-01–09, CC-01–04, CP-01–03, TD-01–03 and TE;
SE-01–05. Original work BSD-2-Clause; existing musl/channel terms preserved.
No user-facing CLI output changes or standards adoption changes.

Simpler alternative: compile-time choice in existing sources, selected here.
A second copied runtime would drift and duplicate lifecycle logic. No negotiation
or fallback is needed. Complexity removed: none now; legacy remains required for
compatibility and historical native regression, and this profile stays opt-in.

Plan: pin sources, strict native SDK receipt and absolute Clang/LLD tools before
consumption. C17 -O2 -Wall -Wextra -Werror, native freestanding/static flags retained.
Host UBSan tests use owned process.py, private build root, explicit clean environment,
30sec per host control,180sec compile/link,16MiB streams and cleanup receipts.
Test maintained v2 decoders over65535epochs, legacy decoders, mixed-link rejection,
parent/child bootstrap fragmented I/O, bounds/full-width divergence, wrong profile,
malformed late bindings, partial framing, reentry, poisoned I/O and failed close.
Build both profiles; compare old complete ELFs to frozen source rebuild before
claiming byte preservation. Native v2 execution cannot run before matching owner
hooks; native SUSTAIN01–06 remains NOT RUN. Reuse old native evidence only after
byte identity. Record all attempts, actual tools/flags/platform/hash results.

Documentation: update SUSTAINED, architecture, STATE/BACKLOG/ROADMAP and this review.
No release/public CLI/conformance completion; UL-058 stays active until owner native
five-cycle,65536pre-effect rejection and cleanup/halt witnesses plus local consumption.
