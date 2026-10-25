# Scoped technical findings — 2026-10-03

Reviewer: Codex in the userland consumer work. This is source/artifact inspection
and independently implemented native replay, not human reader approval.

The frozen244-member final export is verified before inspection. success.rs emits
AERIO002, preserves AERUN001 startup, uses0x7b receipts and retires private epoch
outside1..65535 before launching another service. sustained.rs compares complete
64-bit typed task handles to the expected tag, slot and epoch; it neither truncates
native generation nor treats private receipts as grants. Divergence cleanup explicitly
stops owned peers, checks terminal143/kind3, closes both endpoints, reclaims and
checks stale denial before its rejection marker. Child cohort equality is checked
after real launch and before bootstrap/receipt publication; child-bootstrap/profile
negative coverage remains absent from this delivery.

The normal owner inspects backend6-byte input and2-byte6\n output, empty remaining
streams, then EOF beyond expected length. It closes each backend handle and confirms
subsequent read denial. It closes client endpoint pairs and reclaims both tasks;
backend terminal17 and reclaim follow. command-complete is emitted only after
those assertions plus stale client-handle denial. This binds exact bytes/cleanup to
the inspected owner and ISO, but UART exposes assertions/terminals rather than a
second independently observed backend stream. No wider direct byte visibility claim.

Input uses a real serial grant, timer park and fresh owner prompts; the consumer
sends r/h only after observing the corresponding complete prompt. Unauthorized
clock/halt/invalid-halt checks precede useful work. The halt-ready input path closes
serial then calls its delegated halt operation; post-halt kernel witness supplies
resource facts. Seeded255/256/65534/65535 fixtures are isolated copies, not a normal
reseed API or65535-command endurance claim. Both parent profile mismatch observers
check no admission/backend output and settle two peers before authorized halt.

No new defect was identified within these inspected paths. This does not close
all SUSTAIN01–06: native child-profile mismatch, additional malformed/stale/foreign
endpoint schedules, partial replies/poisoned close and real interruption policy
remain absent. Single-thread trusted buffers, bounded fixture memory and host VM
watchdogs are scoped assumptions. Owner serial write/read may wait indefinitely
on nonprogress; the external deadline is containment, not an in-guest recovery
policy. sys-init must define how outstanding work settles before shutdown/restart.
Supported SDK disposition and independent reader review remain separate.

The ISO extraction independently binds each booted kernel and AENSI001 payload to
the indexed archive. Header sizes/reserved words are checked; parent/child ELFs
match userland delivery (including the intentional legacy-parent mismatch), and
backend/owner members match exact archived artifacts. This is replay/ELF identity,
not a fresh compiler rebuild or a broad kernel audit. Producer stack models retain
only their declared conservative/immutable-builtin assumptions.
