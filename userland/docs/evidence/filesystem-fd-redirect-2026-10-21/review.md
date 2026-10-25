# UL-007/081/082 file/stream redirection batch plan

Before code: add structured aefd_redirect and session entry, retaining stream-only
replace for compatibility. FILE source prepares actual remote dup(min3,cloexec0)
before any target close; validate unused selector against FILE class. Stream source
needs no remote prepare. Self preserves flags. Known target-close success publishes
new alias; error never publishes. Known consumed stream error leaves a target hole.
After known failure, close only confirmed fresh prepared duplicate while live;
cleanup failure/unknown retires admission and records unresolved resource. Never
rollback a conflicting selector, cleanup after unknown, replay or hide allocation.

Receipt status, target attempt/status/removal, prepared selector, committed,
cleanup attempt/status, unresolved allocation and unknown remain explicit. Lost dup
may create an unnamed allocation. Map preservation is not rollback. Existing wire
and Rust policy stay pinned/unchanged. Remote-full returns -24 even replacing a
FILE; logical-full can work with spare remote capacity. Not atomic POSIX dup2.
Native rights/generation/source cleanup/immutable exec/fit remain owner obligations.

Batch tests through real unchanged Rust handler/process/AF07 policy: file/file,
file/stream, stream/file, empty/self/shared-description/full logical/remote capacity,
known target error and cleanup, consumed error, unknown both physical states,
stale source/target/cleanup and conflicting selector. All64 reply prefixes at dup,
target close and rollback close. Actual host stream endpoints/bytes/EOF/close and
source counters are independent of injected observations. Reuse269 file and88
host integration scenarios; session entry and target object link in same run.
Specific compiling fault controls, strict C17/format/UBSan and Rust/Clippy/unsafe,
minimum/current Python; exact session36/predecessor/tool/header/runtime/helper pins.
60s compile/30s suites/16MiB owned streams. Retain all attempts/receipts before
streaming archive readback/removal. No sibling edits/messages, guest or install.

Simplicity: existing dup/close operations suffice for bounded truthful redirection;
new wire/remote policy transaction would cross owners and increase scope. One
operation-local preparation receipt is not a second live FD table. Native atomic
replacement/full capacity remains deferred rather than emulated as success. No
existing API removed. O/I/E, TD/TC/TE, CE/CD/CC/CP and SE-01–05 apply. Independent
owner/reader/native acceptance remains separate; one docs/quality/handoff pass.

## Implementing-agent technical review and batch results

Reviewed preparation before target effects, FILE-class selector uniqueness,
source/target ownership, source flag preservation, distinct reset, consumed hole,
rollback only while live, cleanup-error retirement and unresolved receipt. Self
is a no-effect local binding operation, not a native existence probe. No new wire/
Rust policy/native authority/ledger. Source capacity can reject before target close;
this remains a bounded non-atomic API. Original stream-only signatures unchanged.
Native adapters/authority/generation/deadline/cleanup remain owner obligations.

Actual Python3.10.21/3.14.7 final runs each pass269 prior+213 new live C/Rust
cases (482),88 prior host scenarios per child/eight compiling semantic omissions.
192 partial header replies cover dup, target close and rollback cleanup. Shared
file offsets, source/target flags, actual rolled-back FD rejection, request ordering,
AF07 lookup/final-close counts, host stream bytes/EOF/close, no unknown replay,
actual child exit/source join/backend and transport drop are exercised. Stale
source/target/cleanup fixtures are explicit rejection cases, not admitted startup.
Rust handler/ProcessFiles/AEFD0001/service bytes exactly match prior pins. Strict
C17 warnings/format/UBSan and Rust2021/default Clippy/rustfmt/unsafe checks pass.
126 host headers and exact inputs/resource/runtime verify/recheck. Nine strict
freestanding x86-64 C objects/relocatable link pass;43 static reports/max264,
four standard memory imports. All217 native headers match the preceding immutable
pin before compile and afterward. No native runtime/loader/call-stack/whole-fit claim.

All three qualification attempts pass. Initial run recorded identical native
header hashes; final checker explicitly compares the whole set against prior
session36 pin before consumption. Final minimum/current reruns use that stronger
input-selection check. Production/API/fixture bytes unchanged between attempts;
no failing controls, skips, diagnostic suppressions or production workaround.
Raw command/environment/deadline/stream/cleanup/source/checker/artifact evidence
retained, streaming readback before exact root removal. Implementing-agent review
only; consuming-owner/reader/native acceptance remains pending, full UL/M3/R1 open.

One batch proposal/source handoff and canonical documentation/quality pass. PROJECT
intent, prior candidates/evidence and release pins unchanged. Next authenticated
native adapters and coherent linked-shell/startup selection, immutable executable/
copy/failed-exec parent/FD preservation, complete resource fit and matched sys-init
readiness/shutdown/Aether native commands/errors/cleanup/fresh boot. Stronger atomic/
full-capacity replacement is still needed before claiming that POSIX behavior.
No sibling edit/message, new guest, target install, SDK/default/quota/pin change or
background monitoring. All actual source settlement obligations stay visible.
