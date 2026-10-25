# File operations in the tagged C table — UL-007/081/082

`fd-table.c` adds file open/dup/close/cloexec updates and logical seek to the same
[decoded tagged map](FS-FD-BINDINGS.md) used by [read dispatch](FS-FD-ROUTING.md).
It does not create another descriptor ledger or service. Logical slots0–15 and
private remote file selectors3–15 are allocated independently, preserving console/
pipe entries whose numeric selectors overlap. This is a local opt-in table API,
not a selected shell/startup, libc interposition or accepted new sys-init profile.

The consuming owner must supply a successfully decoded canonical map, actual
matching process/channel/source bindings, and a live file client. It must manage
the map exclusively through coordinated operations and keep it stable throughout
each call. Map/client/arguments/storage ranges are valid/disjoint, serialized and
nonreentrant. Another thread/callback may not change occupancy between preflight
and commit. Arbitrary caller mutation or a shape-valid snapshot is not proof of
native authority, source existence, rights, freshness or lifecycle completion.

## Operations and commits

All functions return logical FD/nonnegative success or negative private errno,
using existing facade/source semantics rather than libc -1/errno.

| Operation | Behavior |
| --- | --- |
| aefd_table_open | Find lowest empty logical0–15, call actual component-open with cloexec0/1, commit returned unused remote selector only after complete success |
| aefd_table_dup | Validate a file entry; find lowest empty logical slot>=minimum0–15; actual remote duplicate independently uses minimum3; commit new selector/flag after success |
| aefd_table_seek | Validate file entry, forward signed64 offset/whence0–2 to actual selector; position remains source-owned and map unchanged |
| aefd_table_close | Actual close by selector, clear exactly that logical entry only after complete zero success |
| aefd_table_set_cloexec | Actual flag update by selector, update only that logical flag after complete zero success |

Read uses aefd_routed_read over this same map. A file may occupy logical0 when
that slot is empty; fixed low FD numbers do not imply console authority. Dup does
not create local aliases to one remote FD: actual ProcessFiles duplication owns
the shared description/offset and last-close behavior. Existing console/pipe slots
remain occupied and unchanged. Their close/dup/seek/flags return -38 here because
this module does not implement the required stream ownership machinery; no local
successful no-op or fallback can pretend to settle them.

Flag/minimum/whence bounds reject with -22 before source calls. Missing logical FD
is -9. Local table full is -24 before a remote open/dup, preventing an unpublishable
source allocation. A free logical slot does not guarantee remote capacity: the
existing thirteen-file source limit may return -24 independently, with no local
reservation committed. Local-full can precede name validation; no POSIX error-order
conformance is claimed. Stale generation aborts file admission, returns -5 and
preserves map bytes. All functions require a live borrowed client/workspace.

Known source errors preserve the complete map and pass through unchanged. Unknown
or retired outcomes also preserve prior map bytes, leaving occupied metadata
unreused; the retired client blocks further operations. After an unknown open/dup,
there may already be a new remote allocation that could not be published locally.
An unchanged map is not proof of no source effect or successful rollback. The
owner must reconcile actual source/process/endpoints and cannot reconnect/reset
sequence/reinitialize a client over this uncertain state.

After positive open/dup, the returned selector must be3–15 and absent from all
existing file entries. A conflicting selector is a source/protocol inconsistency:
abort file admission and preserve map. Never close the conflicting selector as
rollback; it may be an existing descriptor. Do not publish an invented fresh FD.
The exact source broker is still the enforcing authority. No file metadata, path,
size or digest authorizes immutable execution.

File admission abort retains both raw endpoint close results in the client, not
native stream cleanup, source detach, mapping revoke, task settlement or successful
supervisor shutdown. The owner retains actual lifecycle obligations. This module
allocates no4096-byte automatic array, handles no native copy/fork/exec and measures
no whole code/stack/heap/workspace/backing/channel fit. Future shell selection must
replace old startup_fds/table policy coherently rather than operate two live ledgers.

## Qualification

```
python3 -B experiments/filesystem-service/check-fd-table.py
```

The C consumer uses actual new table operations and tagged reads over host OS pipes
to the real unchanged Rust wire/ProcessFiles/AF07 policy with synthetic storage.
The new host server retains the prior source fixture/transport failure behavior
but uses explicit table-specific request/cleanup oracles. Actual child exit, source
thread join, request/lookup/read/final-close counts and one backend drop are checked.
No native IPC/stream/OpenZFS, selected shell or native object/link/fit claim.

269 live host cases comprise13 scenarios and256 reply-prefix losses: every0..63
header prefix for open, dup, close and cloexec. Scenarios cover pipe3/file3 coexistence,
logical5/6 versus source3/4, signed current/end seek, shared offset after dup/close,
independent flags, final close, logical0 file/zero read, local-full open and dup,
remote thirteen-file exhaustion, missing/stale-source preservation, semantic denial
then healthy read, stale generation, conflicting positive selector and AF07 body/
count/close failures. Unknown-operation cases preserve table and deny subsequent
requests, proving no replay/early cleanup. Deliberately stale source probes are
validation tests, not an admitted production startup snapshot.

Six compiling omissions require specific C assertions plus observed C-child failure
in Rust: alias without actual dup, missing selector-uniqueness guard, omitted known
close clearing, clearing on close error, omitted cloexec commit and publishing
logical index as remote selector. Compiler, sanitizer, watchdog or generic Rust
error cannot count as a successful omission control.

Both Python3.10.21/3.14.7 qualify strict C17/format/UBSan and Rust2021/default Clippy/
rustfmt/warnings/unsafe denial. All routing16/bindings6/facade12/client9/wire20/
service77 manifests, source snapshots, tools/native libraries/LLVM resource headers,
105-header host C SDK closure, UBSan runtime and owned process helper verify before
consumption; source/header/runtime pins recheck afterward. Compile60s/live30s,
16MiB streams, clean environment/owned build group and complete child cleanup.
Earlier passing stages before seek/final local-dup-full coverage remain retained;
final evidence selects all source changes. No new native guest or quota expansion.

[Evidence](../evidence/filesystem-fd-table-2026-10-21/README.md). Source-only handoff:
`build/service-deliveries/filesystem-fd-table-2026-10-21-v1`. Independent owner/reader
review, selected mixed shell/startup and actual console/pipe mutation adapter remain
open. Native copy/failed-exec parent/FD preservation, immutable executable admission,
complete fit/dispatcher/readiness/shutdown and matched native commands/errors/
cleanup/fresh boot remain required. Full UL-007/081/082/M3/R1/packages/Zsh/TTY open.
