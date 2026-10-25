# Placed descriptor context — UL-007/081/082

This opt-in batch composes the [native adapters](FS-FD-NATIVE.md) and
[descriptor session](FS-FD-SESSION.md) into one stable context with automatic
whole-operation signal protection. It validates the tagged table against the
native source registry before publishing admission. It does not implement a
startup wire, greeting consumer, libc interposition, shell selection or dispatcher.
The current linked ABI29 runtime still uses its older64-byte table; it cannot
consume this128-byte tagged context implicitly.

## Admission and placement

`fd-context.h` embeds the native adapter, one canonical tagged map, one file client,
one session and its4096-byte workspace. Internal pointers borrow those members.
Allocate the entire context in stable owner-selected storage outside init's4088
usable stack. Do not copy/move admitted storage or allocate it as an automatic
scratch object on that stack. This batch creates no global instance, allocation,
second FD ledger, worker or channel. A future shell must select concrete placement
within its own accepted mapping/backing/heap/stack limits. Target sizeof/offsetof
measurements are layout evidence, not complete placement or peak-fit acceptance.

The constructor accepts already authenticated native endpoints, source records,
pipe history/factory, tagged table and nonzero file-channel generation. The owner
must validate actual identity and issue those inputs; successful local parsing
cannot authenticate them or grant authority. It reads no greeting and performs
no native call on successful admission or local rejection. All metadata starts
fresh zeroed. Input ranges and context must remain valid, appropriately disjoint,
exclusive, stable and single-threaded; constructor cannot run concurrently with
application operations. No effectful callback is invoked to discover authority.

First decode the complete128-byte AEFDT001 table using the existing codec, then
validate native source records with the unchanged native constructor. Every
CONSOLE/PIPE table entry must refer to an occupied matching source; every occupied
source must have at least one table alias. Reject orphan/missing sources before
publishing context, map, client, workspace or callback wiring. FILE selector3 and
PIPE selector3 are separate domains and may coexist. Duplicate FILE selectors
still reject; stream aliases are permitted and share one physical source record.
Invalid local input returns-22 without publishing and can be corrected/retried.
An admitted, retired or finished context rejects reinitialization-16.

## Guarded operations

The context exposes open/read/write/dup/replace/redirect/pipe/close/flags/set_flags/
seek/snapshot and finish. It calls the unchanged session algorithms. Public
results are existing private errno/count/structured receipt contracts, not POSIX
libc signatures. In particular streams transfer at most16 bytes per call, writes
to read-only FILE descriptions return-30, and the older stream-only replace still
rejects FILE crossings. Use structured redirect for source-backed FILE replacement;
its remote-capacity and non-atomic replacement limits remain explicit.

Every operation acquires one native mask guard before touching canonical state,
including alias-only operations, validation failures and snapshot. Restore only
after the entire operation, including redirect preparation, target close, commit
or rollback cleanup. Negative reentry-16 leaves the running operation, map, client
and outputs alone. Check active/busy before retired state so reentry into an
in-flight retired operation also cannot abort its outer transaction. This is
serialized signal protection, not thread synchronization or a libc cancellation API.

A failed native mask retires and aborts the file client immediately, attempting
both raw channel closes once. It issues no source request and preserves map/source
obligations. Further operations cannot replay the command. Native restoration
failure retains existing fail-stop exit125 behavior. Known source refusal stays
known when the session contract permits; unknown outcomes retire without hiding
possible effects. Remaining entries are obligations, not proof that effects rolled
back or that the source still physically exists. No SIGPIPE/job-control semantics.

## Terminal reporting

`aefd_context_finish(context, &receipt)` returns0 only when it publishes a terminal
cached session receipt. Receipt may explicitly report unknown, remaining logical
entries and raw channel-close failures. Negative result leaves output untouched.
Fresh/invalid context cannot manufacture a completed receipt. Busy/active finish
returns-16 and does not interrupt the outer operation; retry only after it leaves.

Normal finish holds one guard across every alias/source close and transport abort.
Finish after retirement performs no source requests; it preserves unresolved map
entries and reports cached transport close results. A mask failure at finish also
retires/aborts before reporting unknown. Mark terminalizing before invoking finish
so nested context calls cannot replay it. Subsequent finish returns the identical
cached receipt without mask/transport calls; every ordinary operation then rejects.
No repeated source close or speculative cleanup is implied by a second report.

Snapshot is inert full or omit-cloexec data. It never closes descriptors or grants
copy/exec authority. A context contains self-referential borrows and cannot be
serialized by memcpy. Native fork at the same virtual addresses also requires an
explicit authenticated child-channel/source/file-generation rebind, copied pipe
history, TLS repair, parent preservation and actual native lifetime witnesses.
Exec needs immutable image admission and failed/unknown-exec preservation. None
of these are supplied by constructor/snapshot or claimed complete by this batch.

## Qualification and matching owner work

Run from the repository root with pinned offline inputs:

```sh
python3 -B experiments/filesystem-service/check-fd-context.py
build/python-qualification/Python-3.10.21/python.exe -B experiments/filesystem-service/check-fd-context.py
python3 -B docs/quality/check.py
```

The private checker pins fourteen predecessor source closures including native48,
prior tool/resource/runtime/helper inputs and217 native headers. It adds exact
scripted ABI trace tests for this context, real host stream effects/EOF, unchanged
193 native-call cases,482 live C/Rust cases and prior controls. Scripted file replies
are call-boundary fixtures, not another service policy or a native dispatcher.
New semantic omissions must compile and fail intended assertions. Strict C17,
format/UBSan and existing Rust/Clippy/unsafe checks apply on minimum/current Python.
Twelve production target objects and relocatable link include the actual int81
backend; a separate unlinked layout object measures context/workspace size/offset.
Frames/imports/layout are not executable/native/whole-fit evidence.

All attempts retain exact source/checker, tool/header identities, argv/environment,
60s compile/30s test bounds,16MiB streams and owned process cleanup. Archive/hash/
size streaming readback precedes exact root removal. See [batch evidence](../evidence/filesystem-fd-context-2026-10-22/README.md).

Next selecting userland shell/startup must supply one greeting consumer and actual
native observations/rebind, explicitly adapt the older installed table/process
snapshot formats, choose workspace/state placement and preserve immutable/copy/
failed-or-unknown-exec state. Propose changed owner-facing messages explicitly;
sys-init owns the matching dispatcher/readiness/shutdown/fit, Aether the fresh
native commands/errors/cleanup/readback. Sys-init0199's host session/redirection
consumption and the older ABI29 ELF do not accept this new composition. Owner and
independent reader reviews remain pending; full UL-007/081/082, M3 and R1 are open.
