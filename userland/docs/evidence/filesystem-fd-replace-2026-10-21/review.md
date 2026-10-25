# UL-007/081/082 stream redirection plan

Before code: aefd_stream_replace(source,target) in the canonical tagged table.
Validate live generation, source and target before effects; either FILE entry
returns -38 until actual source-backed replacement exists. Stream self replacement
returns unchanged FD/flags; distinct success closes occupied target through exact
existing observed-close semantics then publishes source alias with cloexec0.
Empty or same-binding target needs no native close. Works on full logical table.
No extra ledger, temporary remote allocation, new wire opcode or POSIX dup2 claim.

Known unconsumed close error preserves map/live state. Known consumed terminal
error leaves target empty and returns error, never fabricates successful redirect;
this is deliberately not full atomic POSIX replacement. Unknown preserves existing
map/retired admission; actual target may be closed already. No retry/rollback or
source alias publication after error. Source entry/rights remain unchanged.
Callbacks/map/client/storage exclusive, valid, serialized/nonreentrant. Actual
native source rights/generation/lifetime/deadline/cleanup remain owner obligations.

Host tests use real pipe-backed source and target streams for exact redirection,
alias lifetime/flags, empty/self/same-binding/full table, both stream classes,
invalid/missing/stale/unsupported file endpoints, missing adapter, known errors
and unknown both physical states. Explicit fixture cleanup; preserve map/source
and independent actual endpoint EOF/byte/EBADF evidence. Reuse prior22 pipe/18
write/14 lifetime scenarios and269 live file cases unchanged. Compiling omissions
must fail specific assertions plus observed failed child, never generic failures.

Pin pipe28/write24/streams20/table18/routing16/bindings6/facade12/client9/wire20/
service77 plus tool/resource/library/runtime/helper closure before consumption.
C17 strict warnings/format/UBSan, Rust2021/default Clippy/rustfmt/unsafe checks,
actual minimum/current Python.60s compile/30s live/16MiB owned clean-process bounds.
Retain every attempt/checker/source/command/stream/cleanup receipt and streaming
archive readback before exact root removal. Quality/syntax/whitespace/canonical
follow-ons before completion. Independent owner/reader and native gates remain.

Simplicity: pipeline redirection needs a chosen target, not lowest-free dup. Reuse
existing close/lookup and canonical table, without separate reservation or retry
machinery. Reject FILE crossings instead of unsafe close-then-remote-dup presented
as atomic. No old path removed until coherent shell selection. Applicable O/I/E,
TD/TC/TE, CE/CD/CC/CP and SE-01–05; no new runtime dependency or shared standard.

## Implementing-agent technical review and results

Reviewed source/target validation before effects, file rejection before self path,
self flag preservation, full-table stream aliasing and delegation to existing
observed close. No temporary FD, second ledger, new grant, retry, wire opcode or
source policy. After known consumed error target remains empty; source stays usable.
Known unconsumed error permits explicit successful retry/output. Unknown preserves
map and retires admission without source publication; actual target may be closed.
Native rights/lifetimes/generations/deadlines and reconciliation stay owner duties.
This subset cannot be exposed as full POSIX dup2. Independent owner/reader pending.

Actual Python3.10.21/3.14.7 final runs each pass19 replacement+unchanged22 creation/
18 output/14 lifetime scenarios per child,269 live file cases/six compiling semantic
omissions. Strict C17 diagnostics/format/UBSan and unchanged Rust2021/default Clippy/
rustfmt/unsafe denial pass.119 SDK headers and source/dependency/tool/resource/
runtime pins verify/recheck. Earlier passing18-case scope retained. Added FILE self
rejection and actual post-error source/output checks before final reruns; production
bytes unchanged. An initial patch application failed its context check due to
formatted line wrapping and made no changes; corrected explicit patch applied.
No failing qualification attempts, warning suppressions or new runtime dependencies.

Three exact owned roots retained:17,797,690 logical file bytes removed only after
streaming hash/size readback;3,512,184 archive bytes retained. Physical reclamation
not measured. Raw commands/environment/deadlines/streams/cleanup/source/checker/
artifact hashes retained. No sibling edit/message, guest, install, monitoring,
SDK/default/limit/release pin change or native acceptance. Implementing-agent
technical review only; full UL/M3/R1/POSIX/TTY/Zsh/packages incomplete. Next actual
source-backed FILE replacement, native adapters and selected shell/startup/table;
copy/failed-exec preservation, immutable image authority, full fit/dispatcher/
native command/error/cleanup/fresh boot still required. Local quality/syntax/
whitespace and immutable-input integrity checked separately before sealing.
