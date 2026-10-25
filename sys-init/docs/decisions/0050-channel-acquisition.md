# 0050 — Reserved channel acquisition

Accepted 2026-09-06 for BG-058's trusted two-service driver.

## Contract

Add reserve_channel(launch_token, native_slot) and channel_reply(service, reply)
to LifecycleDriver. Opting into this path requires no existing externally prepared
attempt; subsequent legacy prepare calls are rejected. Reserve attempt capacity
and the native slot before returning the acquisition context. Caller invokes the
channel factory only afterward. One outstanding channel creation is permitted;
its missing reply retains that reservation. Channel creation is still synthetic:
this code issues no syscall and assumes an initially empty, exclusively owned
ABI-6 domain. A rejected reserve leaves all counters/journal obligations unchanged.

The reply has exact schema abi6-channel-return-v1, profile, producer, original
launch token, syscall 0x24000, result and writer. Successful result/writer must be
the matching reader/writer pair for channel identity 0 or 1 and its next generation
1..3, using the producer's cap encoding. Selection of the free channel is the
producer's decision; the driver does not guess it. Retain the pair and advance
its independent channel generation before any launch binding can fail. Then bind
the already reserved native slot and initialize rejected-launch cleanup; existing
launch_reply routes either outcome. The driver never silently imports preexisting
channels or resets channel generations when service/native target generations change.

Selected channel errors -13/-22/-16/-28 are received before resource creation.
The wrapper supplies writer=None for errors: unused native output is not evidence.
Retain the exact channel errno separately from native launch results. Since launch
was never invoked, acknowledge the logical launch obligation rejected-before-effects
locally, free its native reservation without advancing native generation, and queue
denied (-13) or launch_failed (others). This is an unacquired attempt, not a forged
native launch receipt. When the model requests generation reclaim, qualify it as
local empty-inventory cleanup, acknowledge executed, then queue cleaned. No close
or native reclaim is issued for an empty inventory. Unknown/malformed channel
returns close the owner and retain the reservation/context; later returns cannot
reconcile that loss under this profile.

Any exception after reply processing begins retains the attempt and closes the
owner. Successfully decoded endpoint IDs remain retained even if subsequent
binding fails. Exact raw replies are not cached: malformed arbitrary-size input is
not retained as a new unbounded diagnostic. Trusted callers retain transport logs.
At most two attempts, one pending create and two channel generation counters bound
state. Success/rejection releases the create gate; generation/attempt ownership
persists until explicit cleanup. No automatic retry of uncertain native effects.

## Sources, review and validation

Frozen native_c.zig channelOperation (decision 0042) selects two channels for ABI-6,
checks factory/reserved inputs before creation and returns reader plus writer on
success. native_channel.zig cap/create defines identity and three-generation
retirement; retain the inspected source copy/hash with this evidence. Names and
hashes remain bookkeeping, not authority. Existing stricter trusted-owner limits
remain; no new shared ABI, dependency or POSIX channel implementation is claimed.
Foundations O-01/O-04, I-03–06 and E-04–08 apply with unchanged pins.

Test reservation before acquisition, duplicate/pending gate, malformed/unknown
retention, success into existing driver, exact create errors through empty cleanup,
post-acquisition binding failure and independent channel generations. Add a
reservation omission control. Run full development checks and retain evidence.
BG-058 next specifies and executes a fresh consuming native acquisition/rejection/
cleanup witness; larger-graph admission, stop/force automation and recovery remain
separate. Model composition does not establish native driver execution.

Decision 0050 validation: 228 model tests / 23 distinct mutation controls,
48 host tests, 37 harness tests and all eight offline gates pass. Evidence:
`docs/evidence/channel-acquisition-2026-09-06/`. No fresh native execution.
