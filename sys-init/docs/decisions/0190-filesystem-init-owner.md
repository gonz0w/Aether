# 0190: Own the first bounded filesystem activation slice

2026-10-20 / BG-067. Aether now supplies a linked filesystem executable and a
qualified separate AENFS003/ABI29 mechanism profile. Start a separate sys-init
entry for its exact engine0/process1–5/owner6 roles. Keep the ABI24 serial entry
and all existing locks unchanged. This first slice admits one selected process
image at slot1 after live engine readiness and a matching AF06 root greeting,
settles that process, then disconnects the filesystem and confirms clean terminal,
endpoint closure and native reclaim before halt. It performs no filesystem writes.
The selected process is the producer's small `p` image, not dash/Zsh or a
filesystem-backed runner. Their integration remains separate.

The simpler alternative is to change only the old ABI24 bootstrap number. Reject
that: its role/PID encoding, dispatch and authority layout differ. Choose a small
direct owner rather than adding a generic service framework or importing the
producer's nine-mutation conformance workload as boot policy. This removes no
existing path; it avoids coupling the serial dispatcher to storage fixtures.

Preserve the exact bootstrap tuple, d002 channel factory, transferred engine
endpoints, inherited block region and retained generation handles. Only running
status0/ready1 admits work; a greeting alone is insufficient. Readiness observation
is not atomic with later process admission. Any denied/unknown/protocol/budget or
cleanup failure closes this local path with no replay, automatic storage restart,
successful halt or speculative reclaim. Fail-stop retains unresolved resources;
it does not claim orderly error recovery. Success exit0 of the pinned filesystem
is its aggregate engine shutdown claim; it is not independent media verification.

Use one shared million-iteration poll budget, at most100000 transfers per frame,
<=16-byte transfers and the existing
16384 code/4088 usable stack limits, no writable statics. Typed synchronous buffer
borrows cross the private native trap; no pointer may escape. The production
entry never returns after failure and successful halt never returns. Host doubles
exercise actual policy source, exact order, short/EAGAIN transfers, stale/malformed
readiness/replies, real failed-status handling and denied cleanup. Omission controls
must detect weakened readiness, terminal and reply-identity guards.

Foundations O-01–05, I-01/03–06 and E-01–06/08, Distribution RL-01/02/05 and local
quality/simplicity rules apply. No public wire, new grant/ABI, vendor-byte change,
CDDL code import, new platform or broader recovery feature. Original source is
BSD-2-Clause. Source/tool and producer identities must be retained before build;
ELF/raw/stack fit is preparation only. Fresh matched native consumer and failure
witnesses remain required before declaring this slice implemented natively.
