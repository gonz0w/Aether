# Single-consumer descriptor startup — UL-007/081/082

This is an explicit **proposed** owner-facing startup profile and an opt-in C
consumer. It composes the pinned ABI29 identity decoder, tagged descriptor table,
native bindings/history and [placed context](FS-FD-CONTEXT.md). It does not change
the selected ABI29 shell, consume the old startup format, install a dispatcher,
authenticate arbitrary labels or implement copy/exec. Sys-init must review and
implement the matching proposal before native selection; no sibling code changed.

## Proposed AEFDB001 envelope

One authenticated delegated process channel carries exactly304 bytes. All integers
below are little-endian. No other greeting consumer may share those endpoints.

| Offset | Bytes | Required value |
| --- | --- | --- |
| 0 | 8 | Literal AEFDB001 |
| 8 | 4 | Version1 |
| 12 | 4 | Total304 |
| 16 | 32 | Existing AEFSH001 ABI29/seven-domain identity |
| 48 | 128 | Existing AEFDT001 tagged table/nonzero file generation |
| 176 | 112 | Seven16-byte native source records: reference,selector,rights,bound |
| 288 | 4 | Pipe object0 last generation0..9 |
| 292 | 4 | Pipe object1 last generation0..9 |
| 296 | 4 | Factory0x76050001 for actual shell slot1;0 for child2..4 |
| 300 | 4 | Zero reserved |

This format replaces neither AF07 engine greeting nor native kernel ABI. It is a
new private shell/dispatcher proposal within the existing seven-domain bounds.
Reject wrong magic/version/length after exactly the first16 bytes; do not wait for
an incompatible producer's remaining payload or silently fall back to its old
64-byte table. After a valid header consume the remaining288 bytes once. Extra
bytes belong to the next operation; startup never reads ahead beyond304.

The AEFSH001 bytes remain pinned verbatim. Compare actual auxv memory0xa000,
native getpid0x10027 and getppid0x1006e, all query arguments zero. Shell slot1 has
epoch=shell generation1..3, PID=epoch*7+2 and actual boot PPID7. Child slots2..4
have epoch1..15, shell generation1..3 and PPID=shell_generation*7+2. Actual memory
must equal0x40000000 | epoch<<8 | (slot+1). Reject synthetic boot parent14/21/28
even if its frame and native observation agree. PID/PPID errors cannot admit.

Reuse context validation for full map/source correspondence both ways, source
rights/bound16, class-aware FILE vs PIPE selectors, pipe reference generations and
no orphan sources. History persists even when no local pipe endpoint remains;
never reconstruct it as zero from absence. The private file generation and console
references are owner-issued opaque labels; nonzero valid alternate labels are
accepted syntactically and confer no native authority. The authenticated dispatcher
must enforce caller/file connection/source/factory rights again on each request.

## Consumer, guard and ownership

`fd-startup.h` embeds one context, identity,304-byte scratch, phase/status and
failure close receipt. Fresh zeroed stable exclusive storage must live outside
init's4088 usable stack. No allocation, worker, writable static or second FD ledger.
Never copy/move admitted storage or share a greeting reader. The target entry
`aefd_startup_native` obtains actual auxv0xa000/0xa001/0xa002 through the pinned SDK
getauxval and uses the int81 backend for mask/PID/PPID/channel operations. Host tests
inject native calls; a matching target object does not prove native execution.

Mark attempted before any native call. Valid distinct nonzero endpoints are
borrowed by a temporary native guard; mask all maskable signals around native
observations, greeting consumption, validation and context publication. Read chunks
are at most16 with preserved short progress, EAGAIN wait/rescan and16384 total read
attempts. Invalid header/identity/data returns-22; incomplete/unknown transfer or
native observation failure returns-5; mask failure preserves its private negative
error. Native wait has no deadline: the owner must provide stop/watchdog/cleanup.
The attempt limit is not a timeout or signal cancellation facility.

Only after all validation may context/map/client/workspace and decoded identity
publish. Transfer the endpoint borrow to the context and restore the exact prior
mask. The temporary guard then relinquishes channels and cannot operate again.
After successful start, use context FD operations and terminal context finish.
This publishes no readiness report and invokes no shell main; the selected shell
must call it exactly once from its new startup path before exposing application I/O.

On failed admission after endpoint borrowing, attempt both raw channel closes once,
even if one fails; preserve attempted flag and both raw results. Clear scratch on
success and failure. No source close or settlement is inferred from channel close.
Invalid/duplicate/zero endpoint arguments cannot establish a borrow and cause no
native close; owner remains responsible for its actual grant lifetimes. A failed
mask also closes borrowed channels without consuming a greeting. Restoration failure
retains native exit125 fail-stop behavior, then traps if exit returns.

Every attempted startup is terminal for greeting consumption: success/failure
readmission returns-16 without another channel/mask/query call. Reject an already
owned context before borrowing endpoints. During startup, reentrant start also
returns-16; caller must not concurrently access the embedded context until return.
Failed startup publishes no identity/context. A copied live context is not a fresh
boot object and cannot use this API as a reset or child-channel rebind.

## Qualification and handoff

```sh
python3 -B experiments/filesystem-service/check-fd-startup.py
build/python-qualification/Python-3.10.21/python.exe -B experiments/filesystem-service/check-fd-startup.py
python3 -B docs/quality/check.py
```

Run from the repository root with provisioned pinned offline tools/SDK. The checker
pins fifteen source closures including context51, native217 headers, tool/resource/
runtime/helper inputs and verbatim identity decoder before use. It exercises803
startup host scenarios plus unchanged175 context/193 native-call/482 live C/Rust
cases and five new/eighteen retained compiling controls. Host pipe bytes/EOF,
query arguments, mask/close observations, single-consumer/readmission, publication
and all304 truncated payloads have independent oracles; injected calls are not
native enforcement. Strict C17/format/UBSan and retained Rust/Clippy/unsafe apply.
Fourteen target production objects/relocatable link, int81 inspection, actual
getauxval import, separate layout object and static frames are build evidence only.
All attempts/argv/environment/bounds/process cleanup are retained; streaming readback
precedes exact owned-root removal. [Evidence](../evidence/filesystem-fd-startup-2026-10-22/README.md).

Next: userland must wire libc/shell FD entry points and this sole startup consumer
into a coherent linked shell, explicitly replace old table/process snapshot/copy/
exec framing, authenticate copied child rebind/TLS/history/file state and preserve
failed-or-unknown-exec parent/FD state and immutable image authority. Select actual
placement and complete resource fit, then sys-init supplies matching dispatcher/
readiness/shutdown and Aether fresh commands/errors/cleanup/readback. Owner/reader
review, full UL-007/081/082/M3/R1 and POSIX/TTY/Zsh remain open. A proposal and host/
object qualification do not establish cross-project acceptance or a bootable shell.
