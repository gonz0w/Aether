# File/stream redirection batch — UL-007/081/082

`aefd_redirect` and `aefd_session_redirect` add receipt-based chosen-target
redirection for FILE, PIPE and CONSOLE entries in the same canonical table.
The session entry composes the [integrated descriptor API](FS-FD-SESSION.md).
The older `aefd_stream_replace`/`aefd_session_replace` remain stream-only with
unchanged signatures/restrictions. No AEFD0001/Rust service changes, new opcode,
native grant or selected linked shell/startup. This bounded operation is not
atomic POSIX dup2 and does not guarantee success at remote descriptor capacity.

## Preparation, target close and publication

All existing canonical-map/client/adapter contracts apply: decoded table, actual
matching authenticated process/channel/source context, valid disjoint ranges and
exclusive serialized/nonreentrant access. Native rights, direction, generation,
lifetime, deadline and settlement stay with the adapter/broker owner. Numeric
selectors and this local C receipt are not authority. Callback cannot mutate/reenter.

Validate source and target before effects. Missing source/out-of-range target is
-9; stale/invalid table retires admission/-5. Missing/retired client returns -5
with unknown admission. Self replacement validates local binding and returns its
FD with flags unchanged and no source effect; it is not a native existence probe.

For a distinct FILE source, first perform real remote dup(minimum3,cloexec0).
The returned selector must be3–15 and absent from every FILE map entry; PIPE3 is
independent. No spare logical slot is needed. A full logical table can work, but
thirteen occupied remote FILE selectors return -24 before target close, even if
replacing a FILE would later free one. Preparation failure preserves map/output;
unknown dup may already have created an unnamed remote allocation.

Then close an occupied target through the existing mixed source-backed close.
A stream source requires no remote preparation. Only confirmed target success
(or an empty target) permits installing the source alias with target cloexec0.
FILE aliases use the actual prepared descriptor and share the source offset;
source flags and unrelated entries stay unchanged. Distinct stream aliases use
the existing owner-issued binding, without native capability duplication.

If target close fails, never publish the replacement. A known unconsumed error
preserves metadata; a known consumed stream terminal error leaves a target hole.
If a confirmed fresh duplicate exists and admission remains live, try its actual
remote close once. Successful cleanup resolves that temporary descriptor; return
the original target error. Any cleanup error/unknown retires admission and records
its raw status and the original target error. Never clean up after unknown target
completion or close a conflicting purported selector as rollback.

## Receipt and unknown state

| Field | Meaning |
| --- | --- |
| status | Target FD on success; private negative error otherwise; cleanup trouble is -5 |
| target_attempted/target_status | Whether occupied-target close ran and its result |
| target_removed | Old logical target became empty during its close; consumed error may leave a hole |
| prepared_selector | Observed duplicate selector or -1; a collision value is untrusted, not fresh authority |
| committed | Success published an alias, or self replacement succeeded unchanged |
| cleanup_attempted/cleanup_status | Explicit cleanup of the confirmed unpublished duplicate and its result |
| unresolved | Unpublished allocation may remain, possibly unnamed after lost dup |
| unknown | Admission/outcome is unknown or retired; never replay/reinitialize |

A successful FILE operation can report a prepared selector with unresolved0
because the map now owns it. A rejected duplicate collision reports unresolved1:
the returned value may name an existing descriptor while an unreported allocation
exists elsewhere. A known stale cleanup error also retires conservatively; the
receipt cannot prove source settlement from that error alone. Keep all fields,
not just status. Unchanged map is not proof of rollback or no native source effect.

File-client retirement clears/releases workspace and preserves raw transport close
results. It does not settle native streams/tasks/mappings or supervisor shutdown.
Actual owner must reconcile unresolved allocations and target/source state. There
is no hidden second descriptor table, automatic retry, new service policy or native
copy/exec authority. This failure contract requires consuming-owner review before
selecting it for libc/full POSIX redirection.

## Combined qualification

```
python3 -B experiments/filesystem-service/check-fd-redirect.py
```

Each interpreter runs269 prior file cases plus213 new actual C/Rust redirection
cases:21 scenarios and all64 reply-header prefixes at preparation, target close
and rollback close. New scenarios cover file/file, file/stream, stream/file,
empty/self/shared-description aliases, logical-full/remote-full, denied close then
successful explicit retry, consumed terminal error, unknown with both physical
states, missing adapter, stale source/target/cleanup, collision and AF07 source
body/count/close faults. Session integration and exact unchanged service policy
are exercised together. No fake file RPC source or successful cleanup no-op.

Actual source reads establish shared offsets; probing the rolled-back FD returns
-9. Host stream byte/EOF/close observations, no source-close-before-dup request
trace, no cleanup/replay after unknown, actual AF07 close/lookup counters, child
exit, source thread join and backend/transport drop are independent oracles.
Stale cases deliberately inject invalid source state; they are rejection tests,
not admitted production startup. Console tags use real host pipe endpoints, not
a native console. Every child also executes88 preceding host integration scenarios.

Eight compiling omissions require exact C assertions plus observed failed child:
omit source dup, publish after target error, omit prepared cleanup, hide unresolved
allocation, preserve distinct target flag, attempt cleanup after unknown, ignore
selector collision and omit target close. Generic compilation/sanitizer/watchdog
failure cannot satisfy these controls. Rust service/ProcessFiles/AEFD0001 bytes
remain the exact prior pins, using synthetic AF07 storage over real host pipes.

Actual Python3.10.21/3.14.7 qualify strict C17 warnings/format/UBSan and Rust2021/
default Clippy/rustfmt/unsafe denial. Full session36/predecessor/tool/resource/
runtime/helper closures pin before consumption and relevant bytes recheck. Native
headers must exactly match the prior217-header pin before compile, not a new
implicit SDK choice. Owned clean environment,60s compile/30s suite/16MiB streams.

Separately nine production C units compile for x86_64-unknown-none and relocatably
link as ELF64, with only memcmp/memcpy/memmove/memset unresolved. Forty-three
static frame reports/max264 bytes describe individual functions only; call chains,
callbacks/libc/interrupts and total code/stack/heap/workspace/backing/channel fit
remain unqualified. This is object/link evidence, not an executable, Aether loader/
ABI/runtime witness or native console/filesystem acceptance.

[Evidence](../evidence/filesystem-fd-redirect-2026-10-21/README.md) and source-only
handoff `build/service-deliveries/filesystem-fd-redirect-2026-10-21-v1` retain all
attempts. Native adapters/coherent linked-shell/startup selection, stronger atomic/
full-capacity file replacement if required, immutable executable/copy/failed-exec
parent/FD preservation, complete fit/dispatcher/readiness/shutdown and matched
native command/error/cleanup/fresh boot remain open. Independent owner/reader and
full UL/M3/R1/POSIX/TTY/Zsh/package acceptance remain incomplete. No sibling edit/
message, new guest, real install, release pin/default/quota change or monitoring.
