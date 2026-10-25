# M4 separate supervisor and queued-result recovery

The [fault recovery slice](M4-FAULT-RECOVERY.md) extends this baseline to five
generations, retained terminal records and two unsolicited #UD worker faults.
The remaining text records the original two-generation experiment.

This slice supersedes the combined display/controller and drained-queue limits
of M4-REMOTE-LIFETIME. Lifecycle v1 is unchanged. A fourth boot module,
`smp-supervisor.bin`, supplies a separate fixed-entry Rust conformance supervisor
(1..4096 immutable code bytes, one private stack). It is Aether-owned test policy,
not sys-init's implementation or a new version of its accepted single-core ABI.

## Ownership and execution

BSP schedules display and supervisor in distinct user address spaces using saved
register frames, CR3 switching and its local timer. Both code/stack virtual
addresses may match, but their backing differs. Timer preemption and yield (20)
select the other runnable domain. AP owns the publisher and its teardown. All
kernel code remains trusted. Supervisor faults or a bounded BSP watchdog failure
panic with resources reserved; no automatic orphan replacement is attempted.

Only supervisor receives the remote control/observe grants (RDI initial full
handle generation<<32|0x100; slot 0x101 observe-only). Display receives framebuffer
and data grants plus a stable link-binding inspect grant: namespace 9 in the
upper 32 bits of the packed mask argument. Its syscall 54 returns the current
endpoint base, or Busy while replacement is unavailable. The static binding is
scope-limited to this publisher/display pair. It cannot stop/reclaim or discover
arbitrary tasks. Rebinding installs new handles without re-enabling old ones.
Supervisor has no framebuffer or data endpoint grants. Tests probe both syscall
rights and supervisor framebuffer mapping denial. Both BSP clients check private
stack sentinels across switches. Publisher also checks a forged control handle.

## Interrupted work

Each result encodes generation in bits 56..63, sequence in 32..55, and sum in
0..31. The display validates all three before rendering. Generation 1 delivers
and receives acknowledgments for 1..50, then queues result 51 without receiving
an acknowledgment, reports its checkpoint and spins. Display deliberately waits
for a new binding after acknowledging 50, so the old result remains in flight.
The separate supervisor observes checkpoint and explicitly stops the publisher.
Generation 2 recomputes 51..100; this is safe only for the fixture's stateless
calculation. No exactly-once side-effect or arbitrary retry guarantee is made.

Accepted stop disables BSP data access; AP disables its runnable state and
endpoint access before publishing stopped. Only then may supervisor invoke 56
with its full control grant to discard terminal-generation transport. The BSP
may take over the stopped AP's request-consumer cursor only after that published
quiescence; the reply-consumer cursor is already BSP-owned. No active producer
or consumer may touch either queue during discard. Return RDX packs discarded
request count in high 32 bits and result count in low 32 bits. The Rust supervisor
requires exactly one old result in generation 1 and none in generation 2.

Reclaim (52) is Busy until discard is confirmed for this generation; the AP also
requires empty queues before memory cleanup. Stop/reclaim/replace phases and
mapping/zeroing checks remain as in M4-REMOTE-LIFETIME. Replacement (53) is a
separate explicit request, and the fixture still caps at two generations. The
supervisor observes replacement through its old grant once, installs its new
generation, then verifies the old grant is invalid. Display refreshes through
its stable binding grant and checks its old endpoint fails. Generation 2 stops,
discards and reclaims after acknowledgment 100; supervisor exits successfully.
Display completion waits for supervisor success and AP reclaimed state.

This tests a queued, unacknowledged result at a known boundary. Stop at arbitrary
instruction points with requests on both queues, spontaneous worker-fault
recovery, dynamic routing and supervisor recovery remain separate work.

## Validation and artifacts

Default smoke requires `AETHER SMP SUPERVISOR PASS`, both terminal cleanups,
100 valid rendered results and supervisor completion. The preceding remote
lifetime marker alone cannot pass. Negative options are
`-Dskip-remote-discard=true` (transport not drained),
`-Dfail-smp-supervisor=true` (supervisor faults), and
`-Dbad-stream-generation=true` (wrong generation rejected by Rust display).
Existing mapping/zeroing and lifecycle-v1 checks remain required.

The image builder now takes KERNEL OUTPUT PROTECTION DISPLAY LIFECYCLE
SMP_SUPERVISOR and Limine loads all four modules in that order, including in the
one-core image (where the SMP supervisor is unused). Package receipt consumers
must pin all five artifacts from the same build; no sibling project is updated
or silently supplied a cached module. Build/test/smoke commands remain in README.
