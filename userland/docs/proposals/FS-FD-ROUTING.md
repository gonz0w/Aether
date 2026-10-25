# Tagged C read dispatcher candidate — UL-007/081/082

`fd-routing.c` connects the [tagged map](FS-FD-BINDINGS.md) to the selected
[typed file facade](FS-FD-FACADE.md) and a trusted stream reader. It dispatches
reads by explicit class and source selector; logical FD8 can refer to file3 while
logical FD3 refers to pipe3. It never infers type from the integer or retries a
failed file operation through a stream. This is an opt-in read seam, not libc
interposition, selected shell startup/table or a complete mixed FD runtime.

Current sys-init decision0197 consumes the typed facade but still requires a
selected mixed shell/startup contract. AEFDT001 remains a local proposal requiring
owner reconciliation. This change implements no sys-init policy or accepted new
native API; old linked ABI29 shell/SDK/startup/pipe/file wire bytes stay fixed.

## Ownership and dispatch

`aefd_routed_read(map,client,streams,logical_fd,out,count)` borrows a successfully
decoded immutable map and live file client. C ranges are valid/disjoint; access
is serialized and callbacks nonreentrant. They may not mutate map/client or call
another operation borrowing the same workspace. The source must be the exact
admitted process/endpoint context selected by the trusted owner. Snapshot tags,
channel generation, FD labels and validated shape confer no native authority.
Actual stream selector/ref/generation/rights/lifetime and callback deadlines are
adapter obligations; source existence is checked by the enforcing source, not map.

Count0–4096 is accepted; NULL output is allowed only at count0. Invalid count/output
returns private -22 before I/O. An unavailable/retired client returns -5. Lookup
checks client channel generation; invalid/stale map aborts file admission and
returns -5. Absent/out-of-range logical FD returns -9 with no source call. No
callback/result is published from a failed lookup. All routed reads require a
live file client in this bounded coupled profile; wider recovery is not inferred.

File class calls the actual typed facade with the source selector. Its complete
response validation/copy and semantic status remain unchanged. Afterward the
router clears the private workspace if still borrowed; a retired file client
already cleared/released it. No file error calls the stream reader.

Console/pipe classes call `streams.read(context,kind,selector,workspace,count)`.
Missing adapter returns -38, not success. One existing caller-owned4096-byte
workspace is reused; no4096-byte automatic runtime buffer or second FD ledger.
The trusted callback may write at most count bytes and returns:

- complete1 with a nonnegative count<=requested: known read result;
- complete1 with a negative private errno>=-2147483647: known semantic failure;
- any other complete value: unknown/incomplete outcome, regardless of result.

Known errno, including a known -5 I/O error, preserves the live client and passes
through unchanged. EOF/error preserves caller bytes. Positive results copy only
validated count; bytes beyond short results remain unchanged. Workspace is cleared
after every completed stream result. A zero read still invokes the actual source;
there is no unconditional local successful no-op. Completion authenticity and
partial-error classification are trusted adapter responsibilities.

Unknown completion, oversized positive count or out-of-range negative status
aborts file admission once, clears/releases workspace and returns -5 without
caller publication or replay. Both raw file endpoint close results remain in the
client. This does not close/settle the stream's endpoints/process, revoke a native
grant, detach a service or authorize shutdown. The owner retains those separate
obligations and must not treat local file closure as native cleanup. No stream
fallback to file exists either.

Local preflight/absent/unavailable cases need not erase an earlier private
workspace result; actual dispatched results follow the clearing rules above.
This module does not allocate/open/close/dup/update flags or mutate the map. A
future selected runtime must replace legacy startup_fds, preserve truthful source
binding and implement mutations/native copy/failed-exec preservation coherently.
Readonly file handle/size/hash does not supply immutable executable admission.

## Host qualification

```
python3 -B experiments/filesystem-service/check-fd-routing.py
```

The new host C wrapper reuses the exact predecessor C consumer/Rust host server.
Valid source3/4 reads in that fixture now traverse logical8/9 tagged entries through
this dispatcher and real facade/client/Rust handler/process/AF07 service. It
reconstructs test-only maps for read calls, including deliberately absent source
FD probes; that is not actual startup admission or a mutable shell table. Other
operations remain predecessor direct facade tests, not new routed mutations.

All74 live host cases pass through the wrapped read path, covering shared offsets,
semantic denial/recovery, full4096/907-byte EOF data, malformed/partial replies and
source faults. Each child first runs13 synthetic stream modes: pipe and console
class/selector, short/EOF/semantic errors, known -5 versus unknown completion,
invalid counts/status, stale map, absent FD, missing adapter, zero read and oversized
preflight. These13 modes repeat per child; they are not962 distinct native cases.
Native streams/traps/OpenZFS and full mixed shell execution are not exercised.

Six compiling omissions must fail exact C assertions plus Rust's failed child
observation: wrong file class, stale-generation acceptance, masking known errno,
copying unused tail, omitted retirement and accepting unknown completion. Generic
compiler/sanitizer/watchdog failure is not their success oracle. The initial host
fixture's strict string-to-bool assertion diagnostics were corrected without
changing runtime policy or suppressing warnings; failed attempt retained.

Exact bindings6/facade12/client9/wire20/service77 manifests and source snapshots,
Clang/Rust tools/native libraries/resource headers,103-header host SDK closure,
UBSan runtime and owned helper are pinned before consumption/rechecked. Actual
Python3.10.21/3.14.7, C17 strict diagnostics/format/UBSan, unchanged Rust2021/default
Clippy/rustfmt/unsafe denial pass. Compile60s/live suite30s,16MiB streams, clean
owned group/private build roots with observed child and source-thread cleanup.
No native object/link/full memory or channel fit/runtime claim is made.

[Evidence](../evidence/filesystem-fd-routing-2026-10-21/README.md). Separate
source-only handoff: `build/service-deliveries/filesystem-fd-routing-2026-10-21-v1`.
Independent owner/reader, selected shell startup/table and all mutations remain
open, followed by native copy/failed-exec parent/FD preservation, immutable image
admission, full workspace/code/stack/heap/backing/channel fit, matching sys-init
dispatcher and Aether native command/error/cleanup/fresh-boot witnesses. No sibling
edits/messages, default/release pins/limits change or full UL/M3/R1 closure.
