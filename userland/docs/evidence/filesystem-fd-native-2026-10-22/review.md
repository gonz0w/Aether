# UL-007/081/082 native adapter batch — pre-code review

Scope: add a concrete native-call adapter behind existing C session callbacks:
16-byte channel transport, exact 32-byte stream control, bounded pipe creation,
terminal cached channel close and an outer signal-mask guard covering an entire
compound session operation. Borrow already authenticated owner-provided endpoints
and validated source records. No new startup wire, greeting consumer, dispatcher,
libc interposition, grant, shell selection or native readiness claim. Existing
session/redirect source and all older deliveries remain unchanged.

O/I/E, TD/TC/TE, CE/CD/CC/CP and SE-01–05 apply. The caller owns stable exclusive
storage, authentication, source bindings and lifetime, whole-operation serialization,
startup and native settlement. Binding labels never grant authority. Validate
selectors, rights, bound16 and pipe reference generations before publication;
unknown replies retire without replay. Known successful close alone consumes a
stream binding. Retain raw endpoint close results, never infer source cleanup.
Signal restoration failure fails stop with exit125; do not report normal failure
after committed effects. Operation-attempt bounds are not wall-time deadlines;
owner watchdog/stop remains required for native wait. No runtime dependencies.

Tests: host native-call fault injection with exact wire/argument oracles, partial
progress, EAGAIN/wait, malformed replies, close errors, pipe generations/history,
source effects and signal guard failures; UBSan/strict C17/format. Existing482
C/Rust cases unchanged. Target compile and relocatable link against exact217-header
pin, inspect actual int81 object and imports/static frames. Minimum3.10.21/current
Python, private build roots, owned process helper/60s compile/30s test/16MiB streams,
all attempts and sources retained. Missing native/owner/reader review stays open.

Simplicity: a transport-only helper is smaller but leaves each caller to reproduce
control validation and transaction-wide signal protection; grouping those shared
boundaries is justified. Reuse existing callback signatures and source protocols,
not a new startup profile or logical FD ledger. Remove no old qualified paths.
Owner startup and full shell integration remain separately reviewable follow-ons.

## Implementing-agent review and actual results

Reviewed pointer/integer ABI (uintptr_t through uint64_t; x86-64 unsigned long and
pointer8 static assertions), const-write borrow, bounded arrays/no input-driven
allocation, no writable statics, complete-before-publish reply validation, physical
source vs logical alias lifetime, generation monotonicity, transport once-only close
and retained errors. The pinned GNU inline-assembly extension is target-only;
normal host builds inject calls and do not compile x86-64 trap code. A callback
busy flag and whole-operation mask are necessary distinct boundaries. Caller must
serialize alias-only operations too; this library is not a thread-safe libc layer.

Minimum3.10.21/current3.14.7 final runs pass193 new host native-call scenarios,
482 unchanged live C/Rust cases/88 prior host scenarios per child, four new plus
eight retained semantic controls. Omitting reply padding, pipe generation advance,
close-error uncertainty or full signal mask compiles but fails the intended C
assertion. Existing controls remain assertion-specific Rust-observed C failures.
Host short/lost transfers, real pipe effects/EOF/alias close, session pipe pair/
projection/finish and actual child125 are exercised. Native-call observations and
pipe-control replies are injected and not Aether enforcement.

Eleven target objects/relocatable link and inspected int81 backend,217 pinned
native headers,166 host headers,59 static frames/max264/four memory imports are
build-only evidence. No suppression, production workaround, new wire/startup/default
or runtime dependency. The initial expected189/observed191 checker-count failure
and earlier191 pass are retained; two new session pipe scenarios strengthened the
final193 scope. Source policy and production adapters stayed unchanged. An unconsumed
identity header snapshot was removed before qualification when declining to invent
a new startup frame. One coverage-schema lookup failure changed no coverage file;
corrected the actual entries key. All dispositions retained in summary.json.

Review performed by implementing agent. Owner acceptance and independent reader
remain pending. Native startup linkage/authentication/copy/immutable exec/failed or
unknown exec parent preservation/full resource fit/dispatcher/readiness/shutdown/
native commands/errors/cleanup remain open. This batch completes its scoped
host/build implementation only, not full UL-007/081/082, M3, R1 or POSIX semantics.

Final local quality gate, minimum/current syntax, tracked diff and scoped whitespace
checks pass; thirteen prior source deliveries/four prior evidence seals and217
native headers verify unchanged. Four attempt roots removed only after streaming
readback:40,763,703 logical bytes,7,499,984 archive bytes retained. Verification
commands/cleanup retained separately. Forty-eight-member candidate seal is in
candidate.json; no source changes after final minimum/current qualification.
