# In-place FILE broker construction — UL-007/081/082, BG-073

Current structural follow-up: [decision0211](../../../sys-init/docs/decisions/0211-owner-structural-fit.md)
uses a private u8 description index with a compile-time capacity check and explicit
widening before checked indexing. All13 descriptions/16 FD slots, Option values,
flags, shared offsets, rights and once-only source lifetime remain unchanged.
Typed fieldwise Option initialization has the same pointer/extent obligations;
array elements use their new actual type size, with no zero-as-None or layout cast.
FILE protocol execution is separated from pending/reply ownership without changing
frames or errors.36 producer tests/15 controls and50 consuming tests, including64
actual prior/current protocol schedules, pass. Target gate2240+workspace4096
uses6336/8192; it is not complete owner fit. Same prior roots18176, expanded native
cancellation roots18384/16384 reject admission. [Results](../../../docs/evidence/owner-structural-fit-2026-10-22/README.md).
Old measurements below retain their dated scope; seals and pins stay unchanged.

Current consuming follow-up: [decisions0208/0209](../../../sys-init/docs/decisions/0209-fork-publication.md)
add bounded child startup/context-ready/parent and known-refusal delivery. The
unchanged producer passes35 tests/15 controls, consumed by34 owner/component tests
and three publication omissions. A separate pinned musl compare selection reduces
constructor-only roots from16544 to16008; adding actual publication/refusal roots
requires17440/16384. It remains a link specimen, not a complete runnable owner or
native/peak-stack acceptance. [Results](../../../docs/evidence/fork-publication-2026-10-22/README.md).
Original dated measurements below retain their scope. No producer runtime, old
API, sealed delivery, released pin or resource limit changes in this follow-up.

Requirement: construct the existing ProcessFiles ledger in unique caller-owned
MaybeUninit storage without a full broker/client/description stack temporary.
This separately selected `fs_in_place` candidate preserves by-value APIs, sealed
deliveries, AF07 bytes, capability checks and all resource/watchdog limits.

`ProcessFiles::connect_in_place(slot, channel, epoch)` returns a borrow only after
every nested field is initialized and the sole AF07 greeting is accepted. There
is no allocator, second ledger, layout cast in sys-init or native authority from
an address. Userland initializes its own private fields with raw field addresses,
elementwise empty arrays and valid Rust values. Zero bytes do not create values.

On returned failure, no usable Self reference exists: the fully initialized
innermost client attempts both endpoint closes exactly once, preserves actual
close results in ConnectFailure, then drops its channel exactly once. Other
partially initialized fields contain only non-owning scalar/Copy state. The slot
must not be assumed initialized on failure. Unknown close results retain caller
settlement duties; no reconnect/replay or success substitution follows. On success
the caller owns the initialized slot, must retain its stable address while borrowed,
settle/disconnect explicitly and eventually drop it once. As with the existing
constructor, this requires bounded, non-panicking trusted Channel operations;
panic/unwind recovery or implicit endpoint cleanup is not promised.

Unsafe boundary: each MaybeUninit field projection derives from the exclusive
aligned parent slot, remains in bounds and creates no reference to uninitialized
Self. References to MaybeUninit fields permit typed writes without claiming a
live parent. The source is written last; a valid enclosing reference is created
only after nested success. No live alias, padded-byte observation or private
layout reconstruction is permitted. The public constructor remains safe.

Simpler alternative: by-value construction was measured and exceeds the current
one-page stack. Fieldwise construction reuses existing state and handshake instead
of adding a stack pivot, allocator, ledger or optimization-specific raw linker.
Only the new candidate admits narrowly documented initialization unsafe blocks;
default checks retain unsafe denial. No changes to shared normative standards.

Selected checks before code: old API/process regressions; initialized nonzero
backing; valid/malformed/lost/wrong-epoch greetings and invalid provisioning;
failure after nested initialization; one greeting, both raw close outcomes and
once-only channel drop; no second owner; output clearing and admission invariants;
strict Rust2021/rustfmt/Clippy, host and no_std target builds, semantic omission
controls and concrete Framed<Endpoints<Native>> constructor/callee measurements.
Sys-init then consumes this API in its mapped gate and checks complete fit; host
construction and assembly measurements are not native or R1 acceptance.

Measured first candidate: required native roots are16544 bytes in size-z and
17360 in size-s, exceeding16384. Scope the next simplification to idempotent client
retirement: clear bindings only on the first shutdown, alongside once-only closes.
All public binding access already checks active state; no field can be repopulated
after cleanup. Repeated shutdown therefore need not clear the already empty array.
Preserve close order/results and malformed/stale/no-replay behavior; rerun the
affected client/process/owner checks and measure again before any fit claim.

The idempotent-retirement simplification preserves16544 bytes (no measured code
gain). Next compare typed initialization of each bounded empty array field with
per-element loops. This is simpler private initialization, not a whole-broker
temporary or zero-as-valid representation. The largest descriptor-array field is
832 bytes for four views; measure actual generated reservations and retain only
a configuration within the existing stack/code bounds. All failure and default
regressions remain required; do not enlarge limits if the comparison does not fit.

Final selection: retain elementwise initialization. The typed-array comparison
passes the same35 process and26 owner host tests, but measures16720 code bytes and
a1104-byte local reservation versus16544 and a216-byte boot prologue including
pushes for the elementwise selection. The latter is restored byte-for-byte to
its qualified source hashes. Largest observed fixed reservation is520 bytes, not
a complete peak-stack bound. No full broker temporary remains. Native admission
is still blocked: the required independent-root subset exceeds code16384 by160,
and full owner entry/dispatch/transaction/shutdown/peak fit is not qualified.
Do not call this a lower-bound theorem for every unified owner arrangement or
raise quotas. The current integration task is complete-owner code/stack fit.

Run from the system root:

```sh
python3 -B userland/experiments/filesystem-service/check-process-descriptors.py --in-place
python3 -B sys-init/scripts/check-broker-init.py --libraries userland/build/filesystem-process-fds-PRINTED
```

Use the first command's actual printed owned directory for PRINTED. This is trusted
development input, not an authenticated release receipt. All commands remain
offline with pinned tools,60-second tool bounds/16 MiB files, no guest, retry or
quota expansion. Retain compact records and remove owned generated roots afterward.
[System evidence](../../../docs/evidence/broker-init-2026-10-22/README.md) records
attempts and the narrow source-identity reuse. Independent review remains pending.

The owner checker exits2 with `blocked-code-fit` after successful host checks
when the measured required subset exceeds16384. A successful measurement command
is never implicit native admission. Current top-level blocker remains code fit.

## Concrete owner follow-up —2026-10-22

Maintainer-directed decision0212 in sys-init supersedes optimizing the new owner
against16KiB. Preserve old selections and choose the new code budget only after
completion/measurement. The concrete composition currently links34560 bytes and
uses3376 resident+4096 workspace within8192, but conservative stack6360 exceeds
4088 usable. Native admission is unavailable. Immutable exec and initial readiness
remain, so this is not a complete-owner or R1 measurement.

`Client::disconnect_checked` accepts an exclusive synchronous verification callback
after a valid disconnect ack and before either channel close. A malformed ack
never invokes it; callback failure closes once, preserves its error and actual
cleanup results, and cannot replay. `ProcessFiles::disconnect_checked` requires
every process view settled first. The concrete owner observes engine exit/kind,
same-channel EOF and EPIPE in that callback; it then checks both closes and actual
native reclaim/staleness separately. Existing disconnect APIs remain unchanged.
This API does not itself establish authority, export or native acceptance.
