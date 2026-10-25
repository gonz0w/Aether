# UL-007/081/082 typed C file facade and live host integration

Pre-code requirement: adapt the selected AEFD0001 C transport into typed file-only
C operations and test actual request/reply streaming through the real Rust handler,
ProcessFiles and sealed AF07 service. Prior C transport replay did not invoke a live
Rust service. This facade deliberately does not interpose libc or route shell pipe/
console FDs; one trusted file client/context is explicit at every call. No sibling
implementation, native/SDK/profile/wire/authority change or new guest.

Expose component-open, bounded read, signed seek, duplicate, close and cloexec.
Return nonnegative result or negative private errno; preserve semantic error,
map local invalid arguments to -22 and retired/unknown transport to -5. Do not
claim POSIX errno/libc semantics or full pathname/cwd/exec support. Reads<=4096
copy into caller buffer only after complete validated response; errors/EOF leave
caller bytes untouched. Zero read must still validate the real bound file FD.
C callers retain the transport's valid/disjoint storage, serialized/nonreentrant
callbacks, actual endpoint authority and deadline obligations. No automatic4096
runtime array, local FD ownership ledger, authentication or successful no-op.

Live host harness starts the C consumer as a child and exchanges actual bytes over
nonblocking host OS pipes with poll wait. Rust uses the unchanged wire handler/
process source and actual AF07 service/Owner with synthetic storage. The existing
sealed fixture runs service in one bounded channel thread, not a second native SPA.
Complete reply writes confirm host-pipe delivery only. Dropped/partial replies
retire through existing guard; parent explicitly aborts on EOF/unknown outcome.
One owned outer command group/watchdog must settle the child; no detached peers.
Native endpoint/trap execution, immutable executable authority and stack/heap fit
remain separate owner gates.

Pin the nine-member C-client candidate, twenty-member wire v3,77-member AF07
service, tools/libraries/resource headers/runtime/helper before copying/building.
Use exact snapshots under build/. Rust2021/default Clippy/rustfmt/warnings/unsafe
code denial; C17 strict warnings/format/UBSan. Record host SDK closure before C
compile, recheck consumed files afterward. Owned subprocess60s compile/30s suite,
16MiB streams/clean environment; actual Python3.10.21 and3.14.7. Test healthy
shared offsets/aliases/final close, missing/invalid/closed FD, semantic read denial
then healthy read, full/EOF data, actual reply truncations/padding/identity errors,
AF07 body/count/close failures and no replay/unchanged caller output. Compiling
omissions must fail actual expected assertions, not generic infrastructure failure.
Retain all attempts; run local quality/syntax/whitespace, update canonical records.

Simpler alternative: only add typed wrappers and replay old response fixtures.
That misses live request generation, server decisions and unknown completion at
the C/Rust boundary. Reuse current fail-stop handler/transport and existing AF07
fixture rather than create another parser/broker/FFI or async runtime. Remove no
accepted old path now; wrappers centralize result conversion and safe publication
for the next explicitly selected shell consumer. Independent owner/reader and full
UL-007/081/082/M3/R1 remain open. Shared requirements remain centrally owned.

Initial live qualification retained an oracle mismatch: the healthy conversation
performs three data reads plus an explicit nonzero-length EOF read. The actual
existing description/source contract forwards that EOF observation, so four
backend read calls are expected. Corrected the host oracle only, preserving the
actual facade/runtime and the failed run51z4opwh. No zero-read shortcut assumed.

## Implementing-agent final assessment

Typed calls retain the existing client/wire contract; no independent FD allocation
or policy machinery was introduced. Shared invoke maps only local invalid=-22 and
retired/unknown=-5; validated semantic negative status is preserved. Positive result
conversion is bounded by the per-op decoder. Signed seek converts to the existing
unsigned wire representation without signed overflow. All six calls use real RPCs;
closed-FD zero reads reject and close/cloexec require actual validated replies.

Read preflight rejects count>4096 and nonzero count with NULL output before I/O.
It copies only positive validated count, preserving caller bytes on errors/EOF and
beyond short reads. C pointer lifetime/disjointness, serialization/nonreentrancy,
actual endpoint binding and callback duration remain explicit caller obligations.
A preflight rejection does not erase prior internal workspace data. No POSIX errno,
full pathname, dup2, console/pipe route, native admission or exec authority claim.

Actual C facade/client and unchanged Rust wire/process/AF07 service communicate
through host OS pipes. The host-only adapter maps EAGAIN/EWOULDBLOCK and waits via
bounded poll; no native syscall numbers or grants were introduced. The server
retains borrowed response until host write completion; client validation is a
separate observation. Partial/dirty replies drop the guard and abort admission;
source/read/request/close counters establish no replay. EOF/error explicitly
aborts; C child wait, source thread join and backend drop complete. These are host
lifetime witnesses, not native process settlement, detach or device quiescence.

Minimum3.10.21/current3.14.7 each pass74 cases/six compiling assertion-specific
omissions. Strict C17/UBSan/format and Rust2021/default Clippy/warnings/unsafe denial/
rustfmt pass. Complete dependency/tool/native-library/resource/header/runtime pins
verify before compilation;99 host SDK headers and source/runtime bytes recheck.
Prior client/wire/AF07 tests are reused only for unchanged bytes/original scope.
No new native object/link/whole memory fit/runtime or shell selection evidence.

The two harness preparation/oracle failures are preserved. Module layout was made
ordinary external Rust source so unchanged fixture resolution works, without lint
suppression. Explicit nonzero-length EOF is the fourth backend read; the incorrect
three-read oracle was corrected, not the runtime. Both final suites ran afterward.
No silently discarded attempts or generic failure substituted for a semantic control.

All three exact owned build roots were archived and every regular file hash/size
read back in one streaming pass before removal:12848051 logical bytes removed,
2989880 archive bytes retained. Physical reclamation not measured. Formatting
setup source/result remain separately retained. No unrelated build/source/evidence
roots were removed. Selected twelve-member source/contract and three dependency
closures match; preceding client evidence remains immutable. Final local quality,
syntax and scoped whitespace checks pass; quality runtime/full-audit/reader/
publication gates remain explicitly NOT RUN.

Canonical contract/architecture/acceptance/work/current evidence and contributor
coverage/review/output scope were updated. Project intent unchanged. This is
implementing-agent review only. Independent owner/reader, consuming shell startup/
file/pipe/console FD routing, native-copy/failed-exec parent/FD preservation,
immutable executable admission, matching dispatcher, concrete fit and assembled
native commands/errors/cleanup/fresh boot remain open. No sibling edits/messages,
new guests, real-prefix install, changed limits/pins or full UL/M3/R1 closure.
