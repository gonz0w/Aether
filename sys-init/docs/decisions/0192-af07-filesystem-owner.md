# 0192: Prepare a separately matched AF07 filesystem owner

2026-10-21 / BG-067. Aether now supplies a qualified AF07 operational engine,
but its current metadata selector deliberately rejects sys-init composition.
Prepare a separate explicit ABI29/AFSRPC07 owner/input with the same bounded
activation, one small boot-image process and ordered shutdown as decision0190.
Do not upgrade the old AF06 owner, sealed delivery or any default/released pin.

The simpler alternative is to replace AF06 magic and engine pins in place. That
would invalidate Aether's exact accepted source/input closure. Choose a separately
named, fixed-version candidate instead of protocol negotiation or a service
framework. A small compatibility copy preserves the old delivery; no machinery
can be removed yet. Native wrapper and ownership algorithm are unchanged; the
only policy change selects AF07 in both greeting and disconnect. Reject AF06 and
unknown versions before dependent admission or engine settlement respectively.

Retain bootstrap29/a001/f101/c002/d001/c003, engine0/process1–5/owner6,
two distinct channels, region[8,2097152,7], live generation readiness and exact
64-byte frames. Root token1/kind1/size observation is data, not native authority.
Metadata16/root31 are the pinned service's selection; init grants no new rights
and performs no metadata requests or mutations. Keep one million shared polls,
100000 transfer attempts/frame, <=16-byte transfers, 16384 code/4088 stack limits,
zero writable statics and no replay/restart. Any failure retains unresolved
resources and traps; no speculative reclaim or successful halt follows.

Success requires dependent terminal0/reclaim/stale, one matching disconnect,
engine terminal0, EOF/EPIPE, endpoint closure, engine reclaim/stale and console
closure before nonreturning halt. The pinned engine's clean exit is aggregate
settlement evidence, not independent durability or device-quiescence proof.
Pool import/export can change metadata even without file-content mutations.

Validate the actual policy with partial/EAGAIN transport, existing failures,
old/future greeting and reply controls and compiling guard omissions. Pin tools,
all new/old source identities, exact dependency manifest/member bytes, ELF/raw and
scoped stack inspection. Run full local checks. Native completion requires fresh
Aether matched composition/positive/failure witnesses and separate consumer review;
no guest is run here. ABI29 shell/client/PID/FD/TTY, loader/runner/package policy
remain separate handoffs. No sibling modification or messaging is authorized.

Applicable Foundations O-01–05, I-01/03–06 and E-01–08 retain authority, bounded
state/failure and exact evidence obligations. Distribution RL-01/02/05 applies;
B-01–04 transport is a different profile, not ABI29. No new standards exception,
shared ABI, dependency or renderer behavior is introduced. Documentation impact:
new candidate guide/evidence, boundary inventory, quality inventory and BG-067
state; old historical artifacts stay fixed. No independent sign-off is claimed.
