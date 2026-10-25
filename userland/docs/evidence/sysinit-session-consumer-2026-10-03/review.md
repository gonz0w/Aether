# Independent owned-session replay — UL-007 / UL-012 / UL-081

Requirement: independently consume sys-init's actual ABI24 shell entry and retain
its unresolved final-phase guest failure. Kernel/userland waiting dependencies are
closed; sys-init composition acceptance is not complete merely because reruns pass.
Applicable O/I/E, Distribution B/SV/NC and Testing TE/CP requirements apply locally.

Scope: verify all sealed producer bytes, freeze the exact normal/wrong-ABI/busy/
diagnostic artifacts and original source/failed traces; compare every actual boot
component against the qualified userland kit. Reuse the unchanged owned process
helper and frozen independent userland stream/identity oracle. No kernel/client/
owner code change or source rebuild, sibling mutation/message, release/promotion.

Before native execution: pin QEMU/xorriso/firmware/input bytes and trusted helper.
Read back all six actual ISO modules, validate009 envelope bounds, unchanged three
client images/entropy and exact selected owner raw bytes. Native cases: two immediate,
byte-paced input, two35-second delayed inputs, diagnostic byte-paced and35-second
input, wrong owner ABI and actual pre-admission busy halt (nine selected cases).
Every healthy case must produce exact90UART bytes/eight admissions/ten terminals,
phase-cleanup/input order and authorized halt. Denials must reach their expected
failure marker/address before any child admission, without successful halt.
Unexpected panic/timeout remains a failure; preserve and diagnose, do not retry
until green or classify it as expected. No recovery semantics added.

Each driver inherits the outer owned process group; no detached emulator session.
105-second driver budget,90-second guest deadline,1MiB serial/16MiB helper streams,
explicit environment/TMPDIR, emulator terminate3seconds/kill3seconds/wait cleanup.
Collector drains a full panic line before stopping; partial diagnostic prefixes are
not UART data. Checker mutations must reject altered bytes/identities/reclaims,
missing/early input, missing/incorrect owner-failure markers and negative admissions.

Technical review: implementation agent source/entry/collector/oracle audit, not
independent SSDK-06 reader approval. Track original producer delayed failure as
unresolved unless direct causal evidence establishes it. A set of passing schedules
cannot erase that failure. Local evidence and concrete producer proposal belong
here; sys-init retains its supervision/dispatcher policy and acceptance decision.

Simplicity: reuse exact artifacts and existing oracle rather than port the owner
or introduce a new service framework. This isolates consuming-project evidence
without widening runtime state. No existing complexity removal; the small private
replay closes a concrete integration evidence gap. BSD notices and immutable
input packets remain unchanged. Archive/readback private work before cleanup.
Canonical docs record dependencies, evidence and unresolved follow-ons; no UL story
or whole M3/R1 is marked complete by this consumer slice.

## Results and disposition

All nine selected native cases passed their exact oracles on the first local
attempt. Seven healthy workloads yield630UART bytes,56 admissions and70 terminals/
reclaims; two negatives yield no child admissions/terminals/authorized halt.
Fifteen positive/negative trace corruptions reject semantically. Thirty actual ISO
readbacks and four ELF/raw owner comparisons close artifact matching. Tools,
firmware, clients/kernel and producer source/inspection identity remain scoped.
No native source change or rebuild, failure fix, SDK promotion or sibling acceptance.

Failure audit retains and confirms the original producer guest fail-stop; complete
host command writes do not prove every guest read. Generic UD2 and passing schedules
leave cause open. Technical reviewer is the implementation agent (source-review.md);
independent SSDK-06 review remains deferred. Canonical state/acceptance/backlog,
root/architecture/handoff docs and draft coverage now distinguish closed composition
consumption from pending diagnosis, cleanup coverage, recipe and broader M3/R1.
All selected gates and archive/member readbacks are required before packet closure.
