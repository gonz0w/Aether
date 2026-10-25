# 0207: Consume the in-place FILE broker without expanding limits

2026-10-22 / BG-070/073. Pre-code review and the contract are in
[userland’s proposal](../../../userland/docs/proposals/FS-BROKER-INIT.md).
The consolidated repo permits one source-coherent integration change; old
component names do not require a separate checkout handoff.

The existing API was measured beyond the4096-byte stack. Owner::connect_in_place
projects its sole FILE field into unique MaybeUninit storage, invokes the additive
producer constructor, then moves streams and initializes phase/sequence. No
Owner reference exists before success. On returned nested failure, producer closes
and drops its channel once, while normal Rust cleanup drops the not-yet-moved
streams. Unknown close results remain actual obligations, never successful cleanup.
No zero-as-valid state, duplicate ledger, private-layout cast, allocator or stack
pivot. Unsafe projections stay with the owner of each private layout.

35 producer tests/15 controls and26 consuming host tests pass. See
[system evidence](../../../docs/evidence/broker-init-2026-10-22/README.md) for
failures, alternatives, hashes and exact current-source reuse. Boot local frame
192+24 pushes resolves this selected constructor’s previous6504-byte aggregate
reservation; complete peak stack is still unproven. The native required-root
subset measures16544 code against16384, so the checker reports blocked-code-fit
and exits2. Size-s and typed arrays are larger; retain the smaller elementwise
constructor. No quotas, VM, old profile or release bytes changed.

BG-073 remains active/partial. BG-070 must complete unified owner entry/transaction/
routing/readiness/shutdown and actual code/stack fit before native admission.
Independent-root measurements are not a universal full-owner lower-bound theorem.
No broader delegation or external waiting is introduced by this local fit gate.
