# Native descriptor adapters — UL-007/081/082

This opt-in C batch supplies concrete channel, stream and pipe adapters for the
[descriptor session](FS-FD-SESSION.md) and [redirection](FS-FD-REDIRECT.md). It
builds an x86-64 native int81 backend and tests its call boundary on the host.
It does not select a shell, authenticate startup, consume a greeting or introduce
a new accepted sys-init profile. Old helpers, wire bytes and ABI29 defaults remain.

## Admission and ownership

`fd-native.h` requires fresh zeroed context, exclusively borrowed stable storage,
actual native input/output endpoints and seven already authenticated owner source
records. Input/output must be nonzero/distinct. Each occupied source carries a
nonzero reference, its exact selector, rights READ1 for0/3/5 or WRITE2 for1/2/4/6,
and bound16. Empty records are entirely zero; references cannot collide. Console
references are opaque owner-issued labels. Pipe references are exactly
`0x79000000 | object<<16 | generation<<8 | end`, object0/1, end1/2, selectors3/4
or5/6; supplied history is0..9 and occupied sources require its nonzero generation.
Only factory0 or existing parent factory0x76050001 is supported. A factory label
never grants parent authority: the owner must enforce the actual caller again.

The constructor checks these labels before publishing anything and performs no
I/O. Invalid local arguments can retry because it has borrowed no resources. Once
initialized, contexts cannot reinitialize, including after retirement. Successful
initialization is not evidence of authenticated startup. The selecting owner must
validate real native identity, one greeting consumer, tagged128-byte table/file
connection generation, source correspondence, factory rights and copied history.
No linked shell presently calls this constructor. These remain acceptance gates.

Seven source records describe physical stream endpoints; the existing canonical
16-slot logical map remains the only alias/FD ledger. Records persist behind
retired admission after an unknown outcome, for owner reconciliation. They are
not native existence probes, grants, reference counts or proof of settlement.
All pointer ranges must be valid and appropriately disjoint; exclusive serialized
nonreentrant use covers the context, map, client, callbacks, data and4096 workspace.
The adapter owns no heap, threads, writable statics, extra channel or large buffer.

## Whole-operation signal guard

Call `aefd_native_enter` before the ENTIRE session operation, then
`aefd_native_leave` after all local state and effects have settled. This includes
compound redirection's prepare/target-close/cleanup, alias-only operations, snapshot
and terminal finish. Never mask independently around individual RPC fragments.
Enter blocks all maskable signals via native0x1000e/SIG_BLOCK0 with8-byte mask,
saves prior mask and rejects reentry -16. Failed masking retires without a source
command; caller must terminally abort the file client/close borrowed channels.
Read/write/wait/control callbacks reject use outside admission and active guard;
callback busy state also prevents nested exchanges. This is not thread safety.

Leave restores the saved mask with SIG_SETMASK2, even after transport retirement.
If restoration fails, close channels once, retain both raw close statuses, invoke
native exit0x100e7/status125 and trap if it returns. A normal error return after
committed effects would be misleading. No new public diagnostic or boot marker.
The host test observes actual child exit125 through an injected native-call backend;
it does not execute a native mask operation or qualify Aether signal delivery.

## Transport and stream protocol

`aefd_native_io` uses existing native0x24001 read/0x24002 write/0x24004 wait and
0x24003 close. Transfer chunks are at most16 bytes, short progress is preserved,
invalid oversized counts retire, -11 may wait/rescan at the same offset. File
requests/replies continue through the existing AEFD0001 client and its attempt
budget; the adapter never restarts a whole operation. Both endpoint closes are
attempted once, terminal state is set before calls, and raw results are cached
including failures. Closing channels does not settle stream objects or file state.

`aefd_native_adapters` implements existing32-byte control requests op1/read,
2/write,3/close with reference@4,selector@8,count@12,payload@16. Read/write returns
one chunk at most16; exact reserved/payload tails must be zero. Private negative
errno -4095..-1, zero/EOF and short counts remain known only after a complete valid
reply. Read output publishes only then. Wrong rights reject -9 without source I/O;
FILE class cannot enter stream dispatch. No file fallback or SIGPIPE synthesis.

Control write and read each permit16384 attempts; EAGAIN waits are hints. Partial
request/reply, EOF, invalid count/padding/status or failed wait retires without
replay. A write may have reached its source before any reply is observed. Only
complete close result0 clears a source record and reports consumed. A negative
close has no reliable consumed bit in this session wire, so it conservatively
reports unknown, retains the record and retires. Do not borrow special close-error
semantics from another AEOUT/AECAT profile.

The attempt bound is NOT a timeout. Native wait has no deadline here and masked
signals do not provide cancellation. Owner stop/watchdog and bounded native cleanup
remain necessary before runtime admission. Job control/SA_RESTART are unqualified.

## Pipe creation and integration

The existing factory request is op82, factory@4,version1@8, rest zero. A successful
32-byte reply must carry status0,generation@4,ordered references@8/12,selectors@16/20,
capacity256@24,chunk16@28. Require exact3/4 or5/6, both registry endpoints unused,
and generation exactly prior+1 within1..9. Publish records/history only after all
fields validate; final C table publication still follows its existing two-slot
preflight and pair validation. History never resets on close; stale/wrap/collision
is unknown and retires. No speculative rollback after possible source creation.
Known exhaustion-23 is accepted only with the remaining28 bytes zero; other
negative creation responses conservatively retire. Factory0 returns known-38
without I/O. A child cannot gain authority by selecting a factory label.

The eventual dispatcher must serialize64-byte file requests and32-byte stream
controls on this same authenticated channel, distinguishing AEFD0001 in its first32
bytes before taking the remaining32. This batch does not install that dispatcher.
The caller must not mix another client/greeting consumer on these endpoints.
Copy/immutable executable/failed or unknown exec must preserve the canonical map,
source generation history, parent state and actual owner authority coherently.
Those contracts and full code/stack/heap/workspace/backing/channel fit remain open.

## Reproduction and evidence

From the repository root, with provisioned pinned tools/SDK, run:

```sh
python3 -B experiments/filesystem-service/check-fd-native.py
build/python-qualification/Python-3.10.21/python.exe -B experiments/filesystem-service/check-fd-native.py
python3 -B docs/quality/check.py
```

The private checker reports its owned result path on stdout; retained traceback
and nonzero exit on failure. It pins redirect41 and all earlier source inputs,
the Clang/LLVM/Rust/runtime/helper bytes, verbatim native trap header, exact217
native headers and supplemental llvm-objdump before consumption. Strict C17,
format, host UBSan, existing Rust/Clippy/unsafe checks and actual minimum/current
Python are separate from native execution. Every process uses the existing owned
runner with60s compile/30s test bounds and16MiB streams; every attempt is retained.

See [batch evidence](../evidence/filesystem-fd-native-2026-10-22/README.md) for
actual observations, source-only handoff, exact receipts and limitations. Review
is implementing-agent only; owner acceptance and independent reader remain pending.
This is a developer candidate, not native shell/POSIX/M3/R1 acceptance.
