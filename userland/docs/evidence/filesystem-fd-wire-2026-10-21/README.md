# AEFD0001 file RPC handler/C codec — 2026-10-21

UL-007/081/082. [Contract](../../proposals/FS-FD-WIRE.md), [plan/review](review.md),
dependency.json and summary.json bind exact scope. The new distinct file-only wire
connects a trusted opaque process key to open/read/seek/dup/close/flags. It does
not switch the linked shell, authenticate native endpoints or implement exec.
Caller-owned4096-byte workspace avoids an automatic read buffer; whole state/
frame/stack/heap placement/fit remains unqualified, including4088-byte init stack.

9 host tests/eight compiling semantic omissions pass on actual3.14.7/3.10.21.
Tests run actual ProcessFiles/AF07 client/sealed service/Owner with synthetic
storage and in-memory channels. Ten C-emitted requests execute in Rust; the C
codec validates actual Rust replies,80 header corruptions, three padded-body
denials, overlapping/max/zero/oversized body boundaries under strict C17/UBSan.
Actual4096-byte reads and907-byte multi-frame EOF bodies check exact data/count/
padding/clearing. Valid sequential consumer compiles; overlapping prepared replies
reject with Rust E0499. Current process18/eight regressions pass on both interpreters.

Strict Rust1.98/2021 warnings/unsafe denial, default Clippy/rustfmt, pinned Clang21
format/C17/conversion warnings/UBSan and native generic-library builds pass.
Per-profile native bytes and actual request/response streams match both Python
runs. Clang resource headers and the103-header host SDK closure are hashed before
C compilation and rechecked; host UBSan dylib is explicitly pinned before execution.
Host ABI/environment is recorded. Native target is x86_64-unknown-none preparation;
no monomorphized runtime link/fit, Aether IPC, original OpenZFS or shell execution.

Cases include every partial header/name body, bad version/epoch/sequence/reserved/
shape/padding, known semantic errors with zero output and later success, no source
effects before validation, full data/EOF, pending response loss/drop, forgotten
reply, stale bound processes including unsupported operations and exhaustion before
wrap. Complete delivery consumes sequence; lost/unknown delivery retires shared
file source with no replay. This does not prove actual native delivery or reclaim.
Every opcode validates current membership; no request supplies its process identity.

Eight semantic omissions target complete process binding, persistent pending,
epoch, sequence, body padding, reply Drop retirement, delivered sequence and error
clearing. Every selected omission compiles and fails actual assertion tests.
Borrow rejection is separately checked against a compiling valid consumer to avoid
counting missing crates/tools as success. No Rust sanitizer/general POSIX/security/
performance/recovery claim. C codecs require actual caller transport/body validation;
a valid negative reply is still an operation error, not successful unsupported work.

All attempts remain retained. Initial recipe setup used an incorrect pin-call
argument list and failed before compiler execution. First Drop omission failed
strict compilation due an unread field; changed the omission to compile without
suppressing warnings before accepting semantic evidence. Review found forgotten-
guard replay risk, fixed by persistent pending state. Early source v1 returned
ENOSYS for unsupported requests on a stale bound key; corrected by an explicit
pure ProcessFiles membership entry and a stale-unsupported regression/control.
An initial mutation target missed rustfmt's multiline text and was rejected.
Subsequent qualification additionally pins host C resource/SDK/runtime inputs.
No failure or earlier passing scope is hidden or promoted to native acceptance.

Selected source-only20-member v3 candidate:
`build/service-deliveries/filesystem-fd-wire-2026-10-21-v3`, seal
`ad1c8082948e08c1e2cc507dd2b069540699e20d9fe97852eadb390a63a4eabf`.
Early v1 is preserved/superseded; v2 carries the corrected runtime and v3 expands
payload/provenance coverage with identical Rust runtime/native generic bytes.
Dispositions and summaries are separate files. All preceding process/client/
service/evidence/SDK/standards pins remain immutable; only additive process
validate_binding entry differs from the earlier process source (retained diff).
No native selected owner, grant/quota/lifetime, sibling edit/message, guest or install.

Next explicit shell C facade and dispatcher startup/FD/console/pipe binding,
exact native copy/failed-exec/immutable image contract, memory placement/full fit,
then sys-init readiness/shutdown and Aether matched native command/error/cleanup/
fresh boot. Keep one greeting consumer. Readonly handles/digests authorize no
immutable executable. Independent reviews, packages/Zsh/TTY and full M3/R1 stay open.
