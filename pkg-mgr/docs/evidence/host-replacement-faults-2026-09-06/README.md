# Replacement fault and lint review — 2026-09-06

The replacement helper's conjunction guards now use explicit conditional failure
branches. Predicates, diagnostics, record format and mutation authority are unchanged.
The binary fixture parses its fixed key/file pairs using quoted parameter expansion.
Both touched shell files pass ShellCheck 0.11.0 without suppressions. The remaining
repository audit has 98 diagnostics; this does not imply complete code review.

Two private-root fault injections exercise finish after stage movement:

- A record copy writes 17 bytes and returns 73. The named injection marker and exact
  status are required. Old/unrelated records, world and old payload remain preserved;
  the partial record is retained, normal operations stay guarded, and a retry must
  reject with `invalid pending record copy` without replacing partial evidence.
- A complete record copy is followed by a rename returning 73. Old state and payload
  are preserved, the pending record equals the proposed record, and an unmodified
  retry completes. Repeated finish and state verification succeed afterward.

These are ordinary command-boundary failures, not actual ENOSPC or power-loss tests.
No host disk is filled and no new repair/delete operation is introduced. The existing
five SIGKILL publication controls and full package suite provide regression coverage.
Runtime/test sources are frozen through this run and identified by inputs.json.

All sixteen fixtures, three pinned standards checks and the embedded two storage-fault
controls pass on this macOS host. Input digests were rechecked after completion.
