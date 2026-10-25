# Scoped consumer source review

Codex inspected the restored, hash-pinned producer sources; no sibling edits.
This is technical assessment, not independent human sign-off or general security proof.

`kernel/arch/x86_64/native_c.zig:sessionObservation` is selected only in the
private SESSION profile. It checks supervisor slot and owner handle before
reading memory, then quota, exact frame size, reserved registers, ordinal and
nonwrapping readable range. The pure parser bounds lengths/copies/execs and
requires zero padding. It rejects admitted workers, channel owners/queued bytes,
and a reclaim delta different from copies+one parent before emitting anything.
Streams use lowercase hex framing, so embedded markers cannot become UART markers.
Only successful observations advance the ordinal. Owner probes exercise malformed
calls, missing reclamation, active workers, duplicate ordinal and exhausted quota.
Worker code has no new UART or observation grant.

The owner captures bytes from authenticated peer requests. Expected shell output
lives in the host oracle, not an owner-generated success transcript. Copy count,
exec replacement and memory admissions are deliberately different quantities.
The unchanged shell script checks its own PID, substitution value after another
pipeline, environment through the helper, and unexpected inherited descriptors.

In `session-owner.rs:poll`, a ready child identity stays reserved while the reply
is partially written. Only a fully delivered reply calls `children.delivered` and
marks the peer collected. Stop acceptance is followed by terminal observation;
reclaim does not follow stop acceptance alone. On parent death, pending wait state
is discarded, each remaining child is stopped/observed, its identity abandoned
through the parent-terminal ledger path, then reclaimed. Parent reclamation and
idle retirement of both pipes precede the observation syscall.

The retained-writer control uses a real parent descriptor alias preserved across
fork and closed on helper exec. Its source predicate requires four copies, three
execs, a pending parent wait, terminated builtin writer, two pending child reads,
and the parent write binding. It then confirms three stops, rather than treating
a guest watchdog as success. Stale-accept permits only the documented output
prefix race; exact lifecycle identities and completion remain mandatory.

The bad-byte control changes only the first `pipe data` occurrence to `Pipe data`
in each parent script. It must complete normally and fail the ordinary exact-byte
oracle. The independent consumer checker additionally requires that exact mutated
stream and tests wrong admission identities, duplicate observations and observations
moved ahead of cleanup. No expected result is inferred from a native PASS marker.

Stack binding will compare locally generated raw owner code against final audited
producer hashes. The retained-writer final hash differs from the earlier probe;
its final indirect-path review supersedes that earlier binding. Maximum reported
path depth is3688 of4088 bytes. This is linked-path inspection, not whole-system
stack safety. Exact build-root-dependent debug ELF identity is not assumed.
