# Runner output-role implementation contract

2026-09-07, recorded before code. UL-059 local output prerequisite, Aether-owned
experimental domain contract; userland retains parsing and independent adoption.
No sibling writes, pin changes, new kernel ABI or shared normative standard.

AEOUT001 is a separately compiled 96-byte carrier: 32-byte header (magic8,
count=2:u32, generation:u32, zero16), followed by two 32-byte records (role,
reference, fd, rights, capacity, zero12). Role1 stdout/fd1/capacity512 and role2
stderr/fd2/capacity256 have write=2 and consuming close; reference is
0x75000000+(role<<16)+generation. Generation must equal native identity.
Full transfer and validation of both records precede publication of either.
No role derives from an ambient descriptor. Old two-binding/startup bytes unchanged.
This runner-only fixture has no child mappings; composing with child launch is
subsequent work, not silently replacing current child profiles.

The dedicated Rust backend owns input abcdef plus distinct 512/256-byte sinks.
Its private channel hello grants three connection-scoped handles; parent sees
only two scoped aliases. Owner forwards bounded writes, owns positions, verifies
both sinks by complete readback including EOF and unchanged input, then closes
all backend handles with stale denial. Parent must explicitly close both aliases,
exit with the selected action's exact normal status, then parent/backend stop and
reclaim across two generations (four native reclaims). No launch or collect legal.
Malformed carrier requires zero requests and explicit bootstrap failure, followed
by owner cleanup; arbitrary early success is forbidden.

Fixtures use copied, hash-verified proposed userland help/version/usage text, not
CLI parsing or a released version assertion. Test real musl write/close, complete
short-write suffix delivery, missing/skipped output, wrong sink/byte, missing close,
and bad carrier rights/duplicate role/stale generation. This slice does not cover
all RL delivery failures, denied admission, consumer adoption or UL-067.

No new allocator, thread, capability pool, dependency or unsafe block. Fixed backend
buffers total 768 bytes; native image/stack bounds must still pass. Existing bridge
unsafe calls remain synchronous with valid stack slices and no retained pointer.
Rust uses 1.98.0 edition 2024; new C uses pinned Clang-format21 draft config.
Legacy transport additions retain its two-space style; do not mass-format it.
Run full command suite, inherited-launch/connections regressions, Zig/host/pins,
format and workflow checks. Freeze sources, preserve failures and artifact identity;
update NATIVE-COMMAND-IO, workflow, EXPERIENCE and STATE with exact limits.

Post-preliminary review, before final edits: explicitly reject queued/partial
requests at terminal observation, including after both closes. The same issue
applies to the preceding local-empty verifier, so harden it with its own exact
post-close control. Add an early-publication mutant to malformed second-role
validation; zero traffic must be independently observed even at early exit.
Retain generated text headers per case. The first 73-case run is preliminary
passing evidence, not final qualification of these additional requirements.
