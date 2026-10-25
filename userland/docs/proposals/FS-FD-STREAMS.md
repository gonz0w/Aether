# Mixed stream aliases and observed close — UL-007/081/082

The opt-in `aefd_mixed_dup`, `aefd_mixed_set_cloexec` and `aefd_mixed_close`
functions extend [the existing tagged table](FS-FD-TABLE.md). File entries delegate
to its actual remote operations; console/pipe entries use the same canonical map.
Existing file-only APIs still reject stream operations with -38. No wire, startup
snapshot, selected shell, native profile or source authority changes here.

The consuming owner supplies a decoded canonical map, matching authenticated
process/channel/source bindings and live file client. All map/client/storage
lifetimes are valid, exclusive, serialized and nonreentrant throughout each call.
Only coordinated operations may mutate the map. Shape validation and a numeric
selector cannot establish native authority, existence, rights or lifecycle.

| Operation | Console/pipe behavior |
| --- | --- |
| aefd_mixed_dup | Lowest free logical slot at or above minimum0–15 receives the same kind/selector and requested cloexec0/1; no new native grant or process context |
| aefd_mixed_set_cloexec | Update that logical entry's flag0/1; this is C table metadata, requiring actual successful image admission and owner enforcement before exec use |
| aefd_mixed_close | Remove only the local entry while another same-kind, same-selector alias remains; otherwise require explicit trusted close observation |

Alias identity includes kind: file selector3 must never keep pipe selector3 alive.
A bounded scan of the sixteen existing entries replaces a second reference ledger.
Flags remain independent per logical alias. Local full returns -24 before effects,
invalid minimum/flag returns -22, missing FD returns -9, absent final-close adapter
returns -38 unchanged. Stale generation or retired client returns -5 with no source
call. Private negative errno is retained; these are not libc -1/errno APIs.

The closer callback receives its owner context, kind and selector and returns
`{complete, consumed, status}`. It must describe the actual source binding:

| Observation | Commit |
| --- | --- |
| complete1, consumed1, status0 | Clear entry, return0 |
| complete1, consumed1, negative status | Clear entry, return terminal error; source was consumed even though close reported error |
| complete1, consumed0, negative status | Preserve entry/live admission, return known error; caller may explicitly retry |
| Unknown or malformed observation | Preserve map, retire file admission once, return -5; no retry/reuse |

Complete/consumed are exact booleans; status must be zero or negative within
-2147483647..0. Success without consumption is invalid, never a successful no-op.
Unknown may mean the endpoint is still open OR already closed. Preserved metadata
is not rollback. File-client abort records raw file endpoint close results only;
actual stream/native cleanup, task settlement, deadlines and unknown-state
reconciliation stay with the owner. No callback reentry or map mutation is allowed.

This implements logical aliasing inside one owning context, not native capability
duplication, cross-process inheritance or a stream source implementation. There is
no pipe creation/write API, console driver, fork/copy, destructive exec commit,
immutable executable authorization, complete fit measurement or startup selection.
Do not select this proposed table over the ABI29 shell until affected owners
reconcile actual bindings and replace old table policy coherently.

## Qualification and handoff

```
python3 -B experiments/filesystem-service/check-fd-streams.py
```

Each live C child runs fourteen stream scenarios using actual host OS pipes and
injected completion observations. They cover surviving-alias read, real last close,
kind isolation, independent flags, known unconsumed retry, consumed terminal error,
unknown with both physical endpoint states, invalid booleans/status/success,
missing adapter, capacity, stale generation and argument bounds. Console alias
coverage is local metadata only. Explicit fixture cleanup closes unresolved pipe
endpoints and independently checks EBADF; file abort does not imply stream cleanup.

The exact predecessor C/Rust fixture then exercises269 live file cases through
mixed file delegation, including256 partial mutation replies. Its service/storage
is synthetic; its host transport/child exit/source cleanup are real. Six compiling
omissions must fail specific C assertions and observed C-child failure: ignoring
alias class, closing every alias, omitting consumed clearing, accepting unknown,
accepting unconsumed success and skipping stream flag update. Compiler failure,
sanitizer termination or timeout cannot satisfy these controls.

Actual Python3.10.21/3.14.7 runs use strict C17 warnings/UBSan/format and unchanged
Rust2021/default Clippy/rustfmt/unsafe denial. Table18/routing16/bindings6/facade12/
client9/wire20/service77 source pins, exact compilers/libraries/resource/SDK headers,
runtime and process helper verify before consumption; snapshots/headers/runtime
recheck afterward. Owned clean environment,60s compilation,30s live suites,16MiB
streams and completed process cleanup apply. This is host evidence, not Aether
object generation, linking, native execution, POSIX conformance or full UL/M3/R1.

[Evidence](../evidence/filesystem-fd-streams-2026-10-21/README.md) retains the initial
fault-control diagnostic mismatch and final runs. Source-only candidate:
`build/service-deliveries/filesystem-fd-streams-2026-10-21-v1`. Independent owner/
reader review, selected shell startup/table, actual native stream adapters and
pipe creation/write, native copy/failed-exec preservation, immutable image authority,
complete code/stack/heap/workspace/channel fit, matched dispatcher/readiness/
shutdown and fresh native command/error/cleanup/boot remain open.
