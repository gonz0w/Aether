# SDK preflight byte and storage boundaries — UL-005 / UL-063

Finish the local receipt intake slice with a 2 MiB per-receipt byte cap. The largest
current input is 959459 bytes; the others are 1163, 637 and 7620 bytes. Read at most
cap+1 bytes before decoding. Reject duplicate keys at every object level and JSON
nonfinite constants; convert decoder recursion exhaustion to an operational failure.
These local intake limits do not redefine an owner's format or establish trust.

If creating/writing the evidence directory fails, exit 1 with an explicit stderr
error rather than an uncaught traceback. Do not claim a report was retained when
storage is unavailable. Preserve existing error/success streams and process ownership;
no changed native source, tool/payload pins, command flags, sibling or dependency.
Applicable: CP-01/02, I-02/05 and E-05/06. This is a byte bound, not a measured RSS
budget, total in-process deadline or hostile concurrent filesystem defense.

Controls: exact byte cap accepted; cap+1 rejected; root/nested duplicates and
nonfinite numbers rejected; excessive nesting fails explicitly. Main-entry duplicate
and oversized receipts produce incomplete summaries and no copy/process calls.
Simulated work-directory creation and initial/later summary-write failure return 1
without successful output; no process starts in these storage controls. Earlier
receipt/schema/copy controls and full startup link must pass with unchanged ELF.
Compare the prior harness against a concrete ambiguous-input regression.

Use Python 3.10+ syntax; record actual interpreter qualification. New controls have
60-second budget. Link suite budget 5 minutes with existing 30-second process limits.
Run local quality gate; retain all attempts under docs/evidence/sdk-preflight-2026-09-07
and build/. Update README, coverage, STATE/backlog and SDK review packet. Independent
technical review remains pending. Root directory loss and failed storage prevent
complete evidence retention by definition; preserve any earlier files and report it.
