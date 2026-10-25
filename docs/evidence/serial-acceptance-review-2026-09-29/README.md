# Serial session acceptance intake — 2026-09-29

Requirement before changes: verify userland's independent SERIAL-SESSION-01–06
acceptance against the unchanged sealed producer and record the remaining gates.
Foundations E-01/E-04/E-05/E-08 apply. Verify complete manifests, runtime identities,
native results, retained rebuilt owner raw/ELF pairs and source reconciliation.
Preserve release pins, sealed evidence and sibling repositories. No runtime, ABI,
authority, resource or unsafe-boundary change is needed. This scoped documentation
intake uses existing progress/reference records and local host/documentation checks;
native execution is attributed to the matched independent userland replay.

Forbidden outcomes: claiming shared SDK adoption, human reader approval, SI-07,
persistent storage/packages or assembled R1 from the private serial fixture.

Verified result: all 279 producer and
702 consumer manifest members match their seals.
Producer SHA256SUMS: `b9efc77107891502e56931e1593f1823ef7edf6ce5437a8b21141d0047084a64`.
Consumer SHA256SUMS: `485c32579591d9ff3001c82fea6705e1a7a56fdb8d052da94a73ebaeda2d55a4`.
All304 delivered runtime source hashes match this checkout. All35 rebuilt owner
raw/ELF pairs were read back from the retained consumer archive and match the
producer bindings and archive index. The archive's full hash also matches.
[review.json](review.json) binds these checks and the copied consumer receipts.
The copied consumer manifest describes the full external packet; only the selected
receipt files are copied here. This packet's own SHA256SUMS binds this local intake.

Userland accepts SERIAL-SESSION-01–06 for private AENMX008/ABI23 after a fresh
160 capacity, five legacy and four envelope cases,132 Python/configured Zig/Rust
checks,11 comparisons and151 checker controls. Actual dash parents execute nine
prompt-driven commands across three lifetimes with exact separate stream bytes,
authority denials, prompt cleanup and idle-parent cancellation. Native execution
belongs to the independently rebuilt userland replay; this intake does not rerun
those cases. Consumer source review remains scoped; independent reader approval
is pending. See [its acceptance](consumer/SERIAL-ACCEPTANCE.md),
[source review](consumer/source-review.md) and
[retained oracle correction](consumer/oracle-correction.md).

The consumer corrected its cancellation offset oracle from strict greater-than to
greater-than-or-equal: terminal output can start at the first byte after a complete
prompt. It retains the initial failed preflight and requires all preceding child
cleanup. Our first intake verification retained a stale117 host-test expectation;
it reached the final acceptance assertion after verifying seals and owner images.
[Initial failure](verification-initial.log) and [initial checker](verify-initial.py)
are retained. The corrected132 expectation passes in [verification.log](verification.log).
The initial simplicity check used the parent directory rather than `inputs/`;
its failure and successful corrected check are retained. No runtime or sealed input
was changed by either intake correction.

Local `zig build test` passes132 Python tests and configured Rust/Zig/offline pin
checks. Workflow, Foundations, simplicity snapshot and scoped whitespace checks
pass; [checks.json](checks.json) records selection. Active STATE, ROADMAP, companion
reference, shell reference and existing workflow coverage now record this acceptance.
No new ABI, authority, unsafe boundary, quota, dependency or released pin is introduced.

Next blocked inputs: userland UL-081's supported shared SDK integration boundary
and reader review; separately SI-07's complete versioned bootstrap/transport and
rebuilt sustained runner/bytecount. The existing host decoder proposal does not
provide these native payloads. Userland owns the SDK decision; sys-init owns init
and supervision policy. No sibling is modified. Persistent filesystem, package
management and assembled sys-init-to-shell R1 retain their existing release gates.
