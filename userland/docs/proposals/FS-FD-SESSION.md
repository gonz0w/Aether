# Integrated descriptor session — UL-007/081/082

The subsequent [file/stream redirection batch](FS-FD-REDIRECT.md) adds structured
`aefd_session_redirect` for all descriptor classes, with explicit preparation/
cleanup outcomes. The older stream-only replace below keeps its original contract.
Qualification numbers/build scope in this document describe the initial session
batch; the new proposal records current redirection evidence and limitations.

This batch gives shell consumers one opt-in explicit-context C surface over the
existing tagged descriptor implementation: startup, open/read/write/dup/replace/
pipe/close, flags, seek, snapshot projection and terminal finish reporting. There
is one borrowed canonical map and one borrowed file client, not another FD ledger.
It is not libc interposition, a selected linked shell/startup, native stream driver,
POSIX conformance or a new accepted sys-init API. The existing ABI29 shell stays.

The session composes the unchanged [tagged map](FS-FD-BINDINGS.md), [file helpers](FS-FD-TABLE.md),
[read routing](FS-FD-ROUTING.md), [mixed aliases/close](FS-FD-STREAMS.md),
[stream output](FS-FD-WRITE.md), [pipe creation](FS-FD-PIPE.md) and
[chosen-target stream replacement](FS-FD-REPLACE.md). Those source/authority/error
contracts remain prerequisites. FILE replacement/full atomic dup2 remains -38;
no unsafe source-close/duplicate transaction is invented here.

## Startup and operation boundary

`aefd_session_init` requires fresh zeroed session/client storage, unowned map,
exact128-byte AEFDT001 startup data, nonzero matching channel generation, valid
IO callbacks and caller-owned4096 workspace. Decode fully before initializing the
client or publishing the map/session. Invalid startup leaves all caller outputs
and workspace untouched, calls no adapters and returns -22. An admitted session
or client with prior generation/live/workspace rejects readmission with -16,
including retired clients and another session borrowing the same client. Corrected
invalid input may retry only because no ownership was admitted on that failure.

All ranges are valid, disjoint and exclusive; adapters/native bindings outlive
the borrow. Access is serialized/nonreentrant. Callbacks must not mutate/reenter.
The actual owner authenticates source/process/channel, enforces rights, directions,
generations/deadlines and settles native resources. Tags, flags and pointers are
not authority. A trusted caller can manipulate public C storage; this is not a
sandbox against that caller. There is no new wire, grant or supervisor policy.

Methods use existing private negative errno, bounds and source operations. Missing/
retired/uninitialized/finished session returns -5 before effects. Stale generation
retires file admission. Flag query returns the canonical per-entry C cloexec bit;
source-backed file flag changes still confirm remotely before that bit commits.
Missing FD is -9; invalid flag/whence is -22. Seek forwards actual FILE operations;
PIPE/CONSOLE seek returns -29 instead of pretending to update a source position.
No POSIX errno precedence, libc -1/errno or native exec enforcement is claimed.

## Inert snapshot export

`aefd_session_snapshot` requires exactly128 output bytes and omit-cloexec0/1.
Validate the entire map, including FILE uniqueness, before projection; hiding an
invalid cloexec entry cannot make it acceptable. Publish output only on success.
Invalid arguments return -22 unchanged; invalid map retires admission/-5 unchanged.
Full export roundtrips the canonical map. Projection zeroes cloexec entries in the
serialized copy only: live map, source flags, offsets, grants and endpoints stay
unchanged. No callback or close occurs. This is not native copy, child authority,
exec admission or destructive close-on-exec commit. Actual immutable image/copy
and parent/failed-exec preservation must be supplied before using it for a child.

## Terminal local finish receipt

`aefd_session_finish` walks at most sixteen occupied logical slots using the
existing mixed close. Known errors permit later slots to run. A known consumed
terminal error counts removal but remains an error. Unknown/stale/retired admission
stops further source calls and reports unknown, even for an empty map. Finally
abort file transport once and retain both raw close results. Receipt fields:

| Field | Meaning |
| --- | --- |
| attempted | Logical close attempts, not number of native source callbacks |
| removed | Entries observed empty after their attempted close |
| remaining | Entries still present after this local pass |
| first_error | First descriptor error; initial unavailable/retired session is -5 |
| unknown | Source completion/admission became unknown/unavailable; further calls stopped |
| transport.input/output | Both raw file-endpoint close results, including negative errors |

Cache the terminal receipt; repeated finish returns the same fields without
repeating source cleanup. Later operations/readmission reject. This is terminal
for the borrow even with known leftovers: it is not a cleanup retry API. A zero
remaining count does not establish successful transport close, source detach,
mapping revoke, task settlement or supervisor shutdown. Inspect raw results,
unknown and remaining; actual owner must reconcile unresolved obligations. No
single boolean promotes the receipt into native readiness or successful cleanup.

## Batch qualification and build boundary

```
python3 -B experiments/filesystem-service/check-fd-session.py
```

Fifteen integrated host scenarios cover startup failure/no publication/readmission,
actual pipeline creation/dup/redirection/read/write, flags, stream seek, complete
and omit-cloexec roundtrips without mutation, invalid hidden duplicate FILE data,
shutdown success/known unconsumed and consumed errors/unknown with both physical
states/missing adapter, cached receipt and no retry. Both raw transport errors are
preserved. Explicit fixture endpoint cleanup is independent of file admission.

Each live C child additionally runs unchanged19 replacement/22 creation/18 output/
14 lifetime scenarios, then269 real C/Rust file cases. File open/dup/seek/flags/
close pass through the new session view borrowing the same fixture map/client;
original file-only unsupported-stream checks remain on their original API.
Rust handler/process/AF07 storage is synthetic; host pipes/processes are real.
Eight compiling omissions must fail specific C assertions and observed failed
child: readmission, missing projection, masked invalid snapshot, removed-count,
retired-empty unknown, raw transport errors, discarded cached receipt and stream
seek. Compiler/sanitizer/watchdog failures cannot substitute.

Actual Python3.10.21/3.14.7 run strict C17 warnings/format/UBSan and unchanged
Rust2021/default Clippy/rustfmt/unsafe checks. Exact replace32 and predecessor
source/tool/resource/library/runtime/helper pins verify before consumption and
recheck relevant bytes. Owned clean environment,60s compile/30s live/16MiB streams.

Separately compile eight production C units for x86_64-unknown-none with strict
C17, -O2/-ffreestanding/-fno-builtin/-fstack-usage and explicit -nostdinc musl SDK
headers. Record all217 local header hashes before use/recheck afterward. This
explicit header-only input is the existing native-service-runtime-2026-10-06-v2
SDK stage; no default SDK/pin is changed. Relocatable ELF64/x86-64 link resolves
all internal symbols; remaining imports are memcmp/memcpy/memmove/memset. The
compiler emits memmove in the existing file client. Forty-one static frame reports
have maximum264 bytes per function. This excludes call chains, callbacks, linked
libc, interrupts and total code/stack/heap/workspace/backing/channel fit. It is not
a runnable executable, native loader/ABI enforcement or Aether execution witness.

[Evidence](../evidence/filesystem-fd-session-2026-10-21/README.md) retains every
attempt and separate host/build outcomes. Source-only handoff:
`build/service-deliveries/filesystem-fd-session-2026-10-21-v1`. Source-backed full
FILE redirection, actual native stream adapters, coherent selected linked shell/
startup, immutable executable/copy/failed-exec contract, full fit and matching
sys-init dispatcher/readiness/shutdown/Aether native command/error/cleanup/fresh
boot remain open. Independent owner/reader and full UL/M3/R1/Zsh/packages/TTY
acceptance remain incomplete. No sibling edit/message, native guest or real install.
