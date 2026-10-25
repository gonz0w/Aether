# Scoped implementation review

Implementing-agent review; no independent review or companion sign-off claimed.

The actual native observer supplies the child identity and fault. Only the new
profile accepts kind2/detail134; old normal-exit expectations are unchanged. The
terminal request drain is bounded: each positive read increases used, capped at17,
and any extra byte or error rejects. EOF after confirmed terminal closes the race
with later client sends. The exact 17-byte canonical prefix is checked before its
frame is discarded; no partial request is submitted to the pipe core.

The parent reader stays live, so releasing the child writer preserves the 256
committed bytes. The parent scheduling witness waits for child terminal in this
profile. Native EOF still comes from the pipe core's real holder state. Actual
wait-status conversion uses the existing mapping and collection acknowledgment;
child resources are not reclaimed at fault observation or at EOF.

The retained-frame control deliberately keeps the partial reference after terminal
holder release, so final retirement must reject. The false-status control changes
only the wait receipt and must make the real parent fail. Existing early-EOF and
retained-writer mutants continue to guard the data/holder boundary.

No general cancellation framework, extra buffer/channel/task, unbounded allocation,
new unsafe block, kernel primitive or signal implementation was added. Native
transport calls borrow owned stack arrays. The user-space UD2 is intentional and
must be contained; it is not evidence for kernel-instance fault containment.
Normal pipe data flow remains unchanged. Sources are frozen for final qualification.
