# OpenZFS random helpers from native workers — 2026-10-04

The [before-code contract](contract.md) exercises the exact sealed CDDL random
helper from a real child context. Four fresh cases pass: child draw; child debit
causing parent quota exhaustion125; child close causing parent draw failure125;
and post-fini draw in a child terminating the whole domain125. Both isolated
instances retain existing memory/TLS/output and exact64-yield acceptance checks.
Kernel, SDK, helper, limits and released pins are unchanged. No sibling edits.

Attempt1 used clear-TID storage after exit zeroed it: retirement failed253.
Attempt2 saved the admitted ID; both clients completed successfully, but explicit
polling yields violated the exact64-yield kernel oracle. Attempt3 parks through
the existing compare-and-wait operation until clear-TID completion, then confirms
stop, retires the saved ID and unmaps stack/FS backing. Both failures, sources,
logs and artifacts are retained. No oracle is relaxed to obtain a pass.

The child has a private4KiB stack and4KiB FS/cookie page, not a production musl
TCB. The initialized selected helper needs no libc TLS on its draw path. The
parent initializes before creation and changes phase only after confirmed child
stop; concurrent init/fini is not qualified. No entropy bytes/digests are logged.
This verifies worker use of a shared domain grant, not whole-engine execution,
cryptographic quality, physical hardware or independent consumer acceptance.

Reproduce with pinned offline tools: run `python3 docs/evidence/openzfs-native-random-workers-2026-10-04/setup.py`
then `python3 docs/evidence/openzfs-native-random-workers-2026-10-04/native.py`.
The recipes verify source/provider seals and stage only owned copies. Clang/LLD
21.1.8, Rust1.98.0, Zig0.16.0 and QEMU11.1.1/qemu64/q35/TCG tool/command/source
identities and UTC times are recorded. Each build180seconds, VM30seconds and owned
teardown3seconds; forced teardown fails. Full137 Python tests plus Zig/Rust/
pins/workflow and scoped format/simplicity/source/link checks pass. Earlier kernel
regressions remain bound to identical sources in the preceding sealed packets.
Every new archive member is read back before owned duplicate cleanup. Original
probe/recipes are BSD-2-Clause; helper and upstream notices retain their terms.

Next extend owner-local lifetime admission under an explicit opt-in bound, keeping
live-slot and memory quotas unchanged, monotonic IDs and exact-stop retirement.
The previously measured1/1 system/delay, serial ARC and one file-worker policy
still reaches82 live workers and281 creates across three lifecycles; it must not
be reinterpreted as a fit for the current8-MiB/two-child runtime. Caller-origin,
backing geometry, identity/configuration and whole-engine lifecycle remain open.
