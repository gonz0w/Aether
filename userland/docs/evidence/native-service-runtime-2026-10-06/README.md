# Maintained service-runtime candidate — 2026-10-06

UL-003/015/081. Aether's current engine-entry gate asks for a maintained userland
SDK/backend rather than private conformance-program definitions. The new
[opt-in runtime](../../../experiments/native-service-runtime/README.md) separates
mechanism from those test programs, preserves the guarded base SDK and requires
an explicit whole-archive supplemental link. No sibling source, SDK default pin,
lab kit, shell SESSION contract or kernel grant is changed.

Five final fresh QEMU cases pass: normal join/TLS/TSD/worker-origin/detached reuse;
actual disabled clock; actual dishonest early completion; full lifecycle; lifetime exhaustion. Each
case checks successful terminals for slot0 generations1/2 and slot1 generation1,
then exact supervisor result100/reclaimed3 and the unchanged supervision marker.
Actual ISO module readback binds both the app/supervisor envelope and kernel.
Tool groups complete before VM ownership;35-second guests/45-second outer limits,
1MiB UART/4MiB emulator logs, disposable firmware state and complete cleanup apply.
These are15 successful isolated app lifetimes, not fifteen independent VM cases.

The lifecycle app fills81 application workers plus the charged reaper in each
large owner and one application worker plus reaper in the peer. An extra creation
returns EAGAIN without changing the output handle. Broadcast without predicate
change retains the original deadline; predicate broadcast cannot complete while
the primary holds the mutex across a200ms sleep. A two-second absolute monotonic
sleep crosses the native one-second park limit without restarting its deadline.
Sixteen worker-origin detached create/retire cycles progress while the primary is
blocked in join. Exact115/three lifetime admissions remain charged after cleanup.
Busy shutdown closes admission, returns EBUSY, then succeeds after joining the
outstanding worker. Invalid/overflow/realtime/cancel/detach/manual-stack failures
remain explicit. Originally detached TSD cleanup and repeated TLS reuse pass in
the normal case. No physical-clock accuracy or performance claim follows.

[Build receipts](reproducibility.json) record byte-identical supplemental archives
on actual Python3.10.21/3.14.7 with pinned Clang21.1.8/LLD. Each interpreter also
rejects seven SDK/output/usage controls, three CLI checks and60 native trace corruptions. Base seal
verification covers every selected SDK member; current Aether base6458-entry
manifest was fully verified before intake. Source, flags, tools, patches, upstream,
firmware/kernel inputs, ISO/ELF hashes, logs and cleanup receipts remain separate.
Final receipts are normal.json, disabled.json, early.json, lifecycle.json and
exhaustion.json.
Earlier failures/passing predecessors do not substitute for final source identity.

[Findings](findings.json) retain missing-header/serialization/kernel-closure,
Rust/Clang dynamic-library collision, detached poll-bound, conditional unused
variable, private loader TLS requirement and harness-edit attempts. A per-Rust
wrapper fixes the host library lookup without changing Clang's environment.
Final detached assertions trap on failure rather than returning an unobserved
result. [Review](review.md) distinguishes actual agent technical review from
pending independent owner/reader acceptance. No sign-off is inferred.

[Delivery](delivery.json) locates the sealed candidate and exact link contract.
Aether must consume it independently, omit conflicting old adapters, initialize
before engine threads, and confirm engine teardown before final runtime shutdown.
Existing engine resource/entropy/filesystem bindings remain with their owner.
Actual OpenZFS entry, full engine/helper/ARC lifetime,
interruption/cancellation/UTC/configuration/identity, general POSIX and release
acceptance remain open. Wider SESSION still gates continued ordinary shell use.
Compact retention removes generated duplicate builds after receipt/log readback;
no new whole-run archive is created.

Exhaustion performs511 successful application create/join/retire operations plus
the reaper in each owner, then denies the513th total admission unchanged. Finish
retains exactly512 admissions and zero live workers. The corrected candidate
also rejects detached join from saved metadata, nonstandard joins, unsupported
mutex/shared condition/rwlock initialization without changing output objects,
and crafted unsupported synchronization entry. Upstream robust attribute setter
returns native ENOSYS honestly; no robust facility is supplied. Earlier736 tests
wrongly expected that setter to succeed. A200ms early-control deadline once
actually expired during scheduling; the retained failure led to a2s request with
<=1s parks, allowing an actual early-completion observation. No clock result or
expected terminal was weakened. Prior first candidate is superseded by the
corrected v2 delivery; its seal/source remains historical, never promoted.
