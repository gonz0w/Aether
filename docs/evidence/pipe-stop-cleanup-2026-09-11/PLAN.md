# Stopping a pending pipe writer

Requirement: stop a real copied child only after the owner has received its
complete seventeenth write and the full256-byte pipe returns Pending without
applying it. The parent waits at the existing scheduling witness. Use the existing
observer-authorized stop primitive, verify terminal kind3/detail143, then clear
that exact pending frame and child holders. Keep all256 committed bytes for the
parent to drain through EOF before wait/ack. Two complete lifetimes reclaim six
tasks under existing quotas. No child normal-exit/fault serial marker is invented:
forced stop has retained observer state but no such marker in this kernel.

The private pipe wait adapter maps this exact supervisor termination to SIGTERM
status15. That is a policy translation, not proof of native SIGTERM delivery or
public kill support. Keep the shared wait-status mapping and other profiles
unchanged. The parent verifies exact status15, its original mask and memory, then
closes descriptors and exits0; backend17 follows. No fabricated normal exit143.

Forbidden: applying/replaying the blocked write, treating a stop request as
terminal evidence, releasing buffered bytes with a live reader, clearing pending
references before observed stop, or reclaiming before wait acknowledgment.
Before cleanup require the exact full32-byte write, no queued follow-up bytes,
256 committed/zero read bytes and the actual retained terminal. Controls omit the
stop (owner2171, zero reclaims) or retain its frame (parent0/owner2166, zero reclaims).

Scope: private Aether Rust owner/C probe/harness only. O-02–05, I-01/03–06, E-01–08
and scoped Coding/Testing/simplicity guidance apply. Existing stack buffers, task
handles and channel grants; no new allocation, unsafe block, kernel/ABI, SDK,
sibling, released pin or quota changes. Native calls borrow owned stack spans.
Pinned Rust1.98.0/edition2024 and clang-format21.1.8 remain in use.

Simplicity: extend the established terminal/frame loop and reuse the existing
capability stop primitive rather than add a cancellation protocol. No old path
can yet be removed; old partial-fault and normal transfer profiles are regressions.
Select focused positive/two exact controls, full connections, launch/console,
host/harness/format/workflow and immutable pin checks. Freeze runtime sources and
retain all attempts. Update STATE/ROADMAP/reference and record image bounds.
SIGPIPE, silent stalls, native copy rollback, same-client pipe reuse, actual dash
substitution and assembled R1 acceptance remain separate work.
