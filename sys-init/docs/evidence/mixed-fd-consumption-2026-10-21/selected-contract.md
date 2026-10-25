# Chosen-target stream redirection — UL-007/081/082

`aefd_stream_replace` redirects a stream onto a chosen logical descriptor in the
[same tagged table](FS-FD-BINDINGS.md), using [observed mixed close](FS-FD-STREAMS.md).
It returns the target on success or private negative errno. This opt-in API handles
stream entries only. It is not libc dup2, full atomic POSIX replacement, a native
grant duplicate or a selected shell/startup; the existing ABI29 shell is unchanged.

The owner supplies a successfully decoded canonical map, matching authenticated
process/channel/source context, live client/workspace and valid disjoint storage.
Access is exclusive, serialized and nonreentrant across lookup, source close and
publication; callback must not mutate map/client or reenter. Numeric tags/selectors
and shape validation convey no native authority. Actual rights, source generation,
direction, deadlines, endpoint lifetime and settlement remain adapter-owner duties.

Both source and target are validated before effects. Missing source or out-of-range
source/target returns -9. Invalid/stale table identity retires file admission once,
returns -5 and preserves map. Missing/retired client/workspace returns -5 before
callbacks. Any FILE source or occupied FILE target returns -38 before effects,
including FILE self replacement. Source-backed file replacement remains required;
there is no unsafe remote close-then-dup pretending to be an atomic replacement.

| Stream case | Effect |
| --- | --- |
| Source equals target | Return target, preserve flags/map, no callback |
| Distinct empty target | Install source kind/selector with cloexec0 |
| Distinct occupied target sharing a binding with source/another slot | Existing mixed close removes only that logical alias, then install source alias with cloexec0 |
| Distinct final target, known consumed successful close | Close through trusted owner, then install source alias with cloexec0 |
| Known unconsumed close error | Return error, preserve map/live admission; explicit later retry permitted |
| Known consumed terminal close error | Return error, leave target empty and source unchanged; do not publish replacement |
| Unknown/malformed close completion | Return -5, retire admission; preserve prior map and never replay/publish |
| Missing required final-close adapter | -38, preserve map/live admission |

Distinct success resets only target cloexec. Self preserves it. Source metadata
and every unrelated slot stay unchanged. A full logical table is supported because
no spare slot or remote allocation is needed. Alias identity remains kind AND
selector and uses the existing map scan, without a second reference ledger.

The consumed-error case deliberately exposes a target hole rather than fabricate
success or promise rollback. Unknown may already have physically closed the target;
its preserved metadata cannot be reused through retired admission. Owner cleanup
must reconcile actual stream state; file-client abort only clears/releases its
workspace and records raw file endpoint close results. No automatic retry, native
cleanup inference, destructive exec, new source rights, wire opcode or source policy.
The narrow failure semantics require consuming-owner review before shell selection.

## Qualification and handoff

```
python3 -B experiments/filesystem-service/check-fd-replace.py
```

Nineteen cases per live C child use actual host pipe-backed stream endpoints.
Normal pipe-to-console-tag and console-tag-to-pipe replacement verifies exact output
at the source reader and EOF on the old target reader. This is a host pipe behind
a console tag, not an actual console driver. Empty/self/same-binding/full-table,
source preservation, distinct flag reset/self flag preservation, invalid/missing/
stale inputs, FILE source/target/self rejection and missing adapter are covered.

Known unconsumed error then explicit retry produces usable redirected output.
Known consumed error leaves a hole while the original source still transfers bytes;
the old target reads EOF. Unknown is exercised with both actual endpoint states,
unchanged metadata and no repeated source call. Explicit fixture close/EBADF cleanup
handles unresolved endpoints, independently of file admission retirement.
Structured close observations are injected; OS pipe/read/write/close are real.

Each child also runs unchanged22 creation/18 output/14 lifetime scenarios and the
269 live C/Rust file cases with synthetic AF07 storage. Six compiling omissions
must fail specific C assertions plus observed failed child: omit target close,
publish after error, preserve distinct cloexec, clear self cloexec, allow FILE
source and clear target on unconsumed error. Compilation/sanitizer/watchdog failures
cannot count as semantic controls.

Actual Python3.10.21/3.14.7 qualify strict C17 diagnostics/format/UBSan and unchanged
Rust2021/default Clippy/rustfmt/unsafe denial. All pipe28/write24/streams20/table18/
routing16/bindings6/facade12/client9/wire20/service77 sources and exact tool/resource/
library/host SDK/runtime/helper closure pin before consumption, with relevant
post-run rechecks. Owned clean environment,60s compile/30s live suites/16MiB streams.
[Evidence](../evidence/filesystem-fd-replace-2026-10-21/README.md) retains initial
18-case scope and final minimum/current19-case runs. Source-only handoff:
`build/service-deliveries/filesystem-fd-replace-2026-10-21-v1`.

Next source-backed FILE replacement/full redirection, actual native creator/read/
write/close adapters and coherent selected shell/startup/table accepted by owners.
Native copy/failed-exec parent/FD preservation, immutable executable admission,
whole code/stack/heap/workspace/backing/channel fit, matched dispatcher/readiness/
shutdown and native command/error/cleanup/fresh boot remain open. Implementing-agent
technical review is separate from independent owner/reader and full UL/M3/R1/
POSIX/Zsh/packages/TTY acceptance. No sibling edit/message, native guest, target
installation, SDK/default/limit/pin change or background monitoring.
