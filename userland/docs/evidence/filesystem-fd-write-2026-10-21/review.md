# UL-007/081/082 tagged stream write plan

Before code: add opt-in aefd_routed_write using the existing canonical map and
caller-owned4096 workspace. Source kind/selector stays explicit; read-only file
entries return -30 locally, never stream fallback. Validate size/pointer/live/
generation/lookup before source use. One trusted callback sees staged const bytes;
known short/error/zero returns unchanged, no automatic retry. Unknown/malformed
completion retires file admission once; bytes may already have reached source.
Clear/release workspace using existing abort or explicit clearing. No allocation,
new ledger, file wire opcode, pipe creation, native binding or shell selection.

Success: actual host pipe receives exact full/short/zero bytes, caller input stays
unchanged, workspace cleared; known negative remains live. Forbidden: file-to-
stream fallback, replay, treating unknown as no effect, over-count accepted,
stale source call or retained workspace bytes. Test unknown both with and without
physical write; endpoint cleanup remains explicit fixture responsibility.

Reuse exact sealed streams20/table18/routing16/bindings6/facade12/client9/wire20/
service77, tool/resource/library/runtime/helper pins. New source/test only; old
fixtures remain immutable. Host C17 strict warnings/format/UBSan, Rust2021/default
Clippy/rustfmt/unsafe denial, minimum/current Python, owned group/clean environment,
60s compile/30s suites/16MiB streams. Retain all attempts/raw argv/logs/checker/source
before streaming archive readback and exact owned-root removal. Quality/syntax/
whitespace and canonical docs before completion. No native/POSIX/whole-fit claim.

Simplicity questions: the requirement is output for mixed shell descriptors. The
smallest design is one explicit class dispatch and one borrowed staging buffer;
reuse the existing completion result and fail-stop client, not a new writer state
machine/retry policy or separate table. No added runtime dependency. Original read/
file/mixed APIs remain compatible; selected shell must later replace old routing
coherently. Actual native adapter/rights/deadline/settlement and owner/reader review
remain open; no generic cross-project standard or sibling implementation change.

## Implementing-agent technical review and final results

Applicable boundaries: Foundations O-01–04/I-01/03–06/E-01–08; Distribution
NC/PX/SV/FS applicability remains prospective native acceptance. Approved draft
TD/TC/TE, CE/CD/CC/CP and SE-01–05 select source/host integration review here.
Reviewed bounds, const staging, explicit class dispatch, early-error workspace
scope, exact complete/result validation, once-only abort and no automatic retry.
Known source errors preserve live client and subsequent real host write succeeds.
Unknown may have produced bytes; host readback confirms both physical outcomes.
Callbacks remain trusted for rights/deadlines/lifetimes and truthful observation.
No new runtime dependency, suppression, wire opcode or source grant. There is no
production automatic4096-byte array; the host fixture's bounded received array
is not target stack evidence. No existing path removed before shell selection.

Final actual Python3.10.21/3.14.7 each pass18 write scenarios plus unchanged14
stream scenarios per child,269 live C/Rust file cases/six compiling omissions.
Strict C17 warnings/format/UBSan, Rust2021/default Clippy/rustfmt/unsafe denial
pass.111 SDK headers, exact source/tool/resource/runtime pins verify/recheck.
Initial successful run predates explicit known-error-followed-by-write assertion
and precise stale-retirement control. Replaced its broad stale-branch bypass
(which could use uninitialized binding in the intentionally faulty variant) with
a direct missing-retirement omission; original retained, final runs use only the
precise control. Production implementation unchanged; fixture/control improved.
No failing qualification attempts. Actual technical reviewer is implementing agent;
independent affected-owner/reader walkthrough remains pending. Full UL/M3/R1 open.

All three owned attempts retained with raw argv/streams/process cleanup receipts,
sources/checker/binary hashes. Streaming archive readback verifies every hash/size
before exact root removal.15,821,002 logical bytes removed;3,262,536 archive bytes
retained. Physical reclamation not measured. Candidate24 source-only members; no
sibling edit/message, new guest, real install, monitoring, SDK/default/limit/pin
change or native/POSIX acceptance. Local quality/syntax/whitespace and immutable
predecessor integrity are checked separately before evidence sealing.
