# One authoritative shell mask — 2026-09-07

All 348 selected native cases and 98 host tests pass.

The public shell sigprocmask facade and actual linked musl block/restore helpers
now operate on the native caller's Execution.signal_mask. The former independent
C startup_mask is removed. This is a mask prerequisite; custom handlers, pending
signals, delivery/return, actual dash and exec/wait are not implemented by it.

The [review](review.md) applies the adopted simplicity questions: reuse one
context-owned transition and checked copy routine, remove duplicate state, retain
separate caller validation, and add no signal service, quota or dependency. Existing
0x28009 callers retain their grant and argument checks. Only runner-local connection
callers gain the SDK's four-argument 0x1000e transport; other profiles still return
ENOSYS. Musl does not initialize r8/r9 for four-argument calls, so those registers
are not treated as extra required-zero arguments. No identity or path supplies
access to another context.

## Target witness

The actual startup client links __block_all_sigs, __block_app_sigs and
__restore_sigs from the unchanged native musl archive. The target checks the
returned old mask, unmaskable-bit removal, app-mask reserved-bit pattern, public
to raw and raw to public observation, invalid size/how and inaccessible/overflow
pointers without changing mask state, aliased old/new storage and reset over two
fresh generations. Real descriptor I/O and four independent reclaims still pass.
An omitted internal block fails at terminal73/owner1501, while earlier no-mask,
disposition and descriptor mutants retain their original exact oracles.

The helper snapshots input and validates all output bytes before either old-state
write or mask mutation. It retains no user pointer and allocates nothing. A public
facade call still requires role admission; libc internal initialization can only
change the caller's own mask before descriptor publication. The existing SDK mask call gains scoped behavior; no grant, image limit or
signal-send authority is introduced.

## Inputs, checks and limits

runtime.patch is the exact delta from the retained dup2 source snapshot.
Musl block/mask/transport source and COPYRIGHT are copied under musl-inputs/;
check-sdk.py verifies all 4,311 SDK files plus its upstream source archive against
the prior retained archive. SDK bytes, tools, siblings and release pins are unchanged.
The preceding immutable dup2 and simplicity-adoption packets remain intact.

The selected qualification is the complete command-runner suite, both existing
native signal-mask profiles, both pthread-lifecycle and unsupported-mask preflight
profiles, and M4 regressions,
plus host/pin/workflow, source syntax and pinned C/Zig formatting checks. The
receipts retain exact build/boot commands and source hashes. The first M4 attempt
failed before boot because sandboxing denied the local QMP socket; its complete
output directory is retained. Retry permits that socket on identical sources.
No runtime failure is hidden by that infrastructure retry.

Existing harness timing-field limitations remain stated in execution-context.json;
passing this packet is not full draft evidence conformance or independent consumer
acceptance. These explicit tests do not establish signal delivery or IPC reentrancy
under handlers. Actual shell workload scripts remain NOT RUN here. Next design
checked custom-handler/pending/return behavior for actual dash initialization,
then child exec/wait and pipes; OpenZFS remains after the shell producer path.


Reproduce with the existing commands in [NATIVE-SHELL-STARTUP](../../NATIVE-SHELL-STARTUP.md)
and [NATIVE-C](../../NATIVE-C.md), using the verified SDK described in sdk-check.json.
Each `*-results.json` retains its exact command arrays and profile parameters;
qualification.json lists the eight passing suites and the separate failed M4 attempt.
Sources and all passing/failed target artifacts are archived and member-verified
by collect.py. These are retained one-off recipes, not new developer entry points;
reproduce in fresh private output roots and do not overwrite sealed packets.
