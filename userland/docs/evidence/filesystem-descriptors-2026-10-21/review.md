# UL-007/081/082 read-only descriptor core review

Plan before implementation,2026-10-21. Aether has consumed the corrected ABI29 v2
client; sys-init's matching dispatcher remains missing. Independently implement
the assigned userland file-description semantics against the actual existing
filesystem Owner policy, without changing AF07 wire, engine, old service/client
seals, supervisor policy or native mechanisms.

One exclusive owned policy context, one trusted authenticated peer attachment,
root LOOKUP|READ only, attenuated file READ only. Reserve FD0–2 for console outside
this file-only core;13 file descriptors3–15 and13 open descriptions fit the existing
16-handle owner bound including root. No allocation, unsafe code, new dependencies,
generic transport or authority derivation from FD/PID/UID/path. One path component
only (existing255-byte policy bound). No write/create/append, directory traversal,
stat/credential translation, fork replication or executable loading implementation.

Separate descriptor binding/cloexec flags from open description/retained handle/
shared offset. Independent opens have independent offsets; duplicate aliases share
one handle/offset until final close. Check capacity before lookup. Reject directory
opens after releasing the new handle. Bound reads4096 and signed64 offset/request
range; clear output before validation and on every error, never advance on failure.
Seek uses checked signed arithmetic and current Owner stat for SEEK_END. A local
read-only subset does not promise arbitrary POSIX semantics or mutation coherence.

Keep Owner error identity. Fatal/inconsistent provider results or failed final
close retire the table, revoke references and shut down its sole backend context;
future work fails closed. No transport/retry/unknown-outcome recovery is invented.
Read known errno errors preserve offsets. Local descriptor cleanup/context Drop
is not native endpoint closure, SPA drain/export, quiescence or reclaim. Explicit
close-on-exec commit is destructive and only follows confirmed image admission;
failed/ambiguous native exec requires separate dispatcher staging, not early close.

Apply Foundations O/I/E, Distribution PX/NC, CR-01–03, TD-01–03 and SE-01–05.
Original BSD-2-Clause Rust2021, no_std, forbid unsafe; native panic abort. Pin exact
77-member AF07 dependency/Owner sources, Rust1.98/standard libraries and unchanged
owned process helper before building. Host uses real Owner and instrumented fake
storage only; no engine disk/wire/native acceptance. Native generic-library build
is type/object preparation, not executed monomorphized runtime or resource fit.

Tests: real Owner-backed independent-open/dup/shared seek/read/EOF/closure,
capacity before backend effects, invalid names/directory release, permissions,
cloexec alias/final-close, checked offsets, backend errno/bad count/data clearing,
retirement, disconnect/Drop cleanup. Add compiling semantic omissions with failures
at named test assertions. Rustfmt/default Clippy/unsafe denial, host and native
library build, actual minimum/current Python driver evidence and local quality.
Each compile<=60s/test<=30s,16MiB logs, clean env, build-only owned roots. Retain
all failures and compact/read back before removing redundant output.

Simplicity: reuse Owner directly rather than introduce a generic backend/proxy
or duplicate handle enforcement. Existing stateless explicit-offset reads cannot
express dup/shared offsets or final-close semantics, so add two fixed arrays and
scan aliases instead of introducing reference-count machinery. Remove nothing
now because accepted wire/client paths are still pinned. Owner implementation and
all existing native bounds remain authoritative. Independent review, AF07 wire/
FD dispatch, fork/exec staging and native integration remain incomplete.

Final technical assessment by implementing agent: twelve real-Owner/synthetic-
storage host tests and eight compiling semantic omissions pass on actual Python
3.10.21/3.14.7. Default Clippy, Rustfmt, warnings/unsafe denial and host/native
no_std libraries pass; the generic native library hash is identical across the
final interpreter runs. It is not monomorphized/linked engine code or native
execution. First Clippy int-plus-one finding was fixed without suppression; all
intermediate source/checker versions and the original failure are retained. Final
runs additionally pin the exact trusted tool-manifest selection and retain Rust
standard-library pin receipts. No production module behavior changed for that
receipt tightening. No Rust sanitizer or broad conformance/security claim.

Five-member source-only candidate seal is
f93c01950d710737158774b51d48f01fff2c06bb7bf97a4114d7bbb689f616e2.
Original77-member AF07 dependency, wire, engine/client seals and standards pins
stay unchanged. Scope remains one dedicated Owner context,13 file descriptors,
read-only rights, inherited exact provider-count contract and stricter signed
request ranges. Commit-close is only after confirmed admission; no native loader,
failed-exec rollback or cross-process FD sharing. Independent reviews are pending.

Quality/pins/inventory, minimum/current Python syntax and whitespace pass. Seven
exact new work roots were compacted and every retained member hash/size read back
before removing59434344 logical bytes;743873 archive bytes retained. Physical
reclamation was not measured. No historical/sibling cleanup or guest. Next wire
authenticated process FD/AF07 transport without duplicating the live Owner/SPA,
then actual filesystem exec and matched supervisor/native lifecycle qualification.
