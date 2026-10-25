# Quality snapshot closure evidence

Decision 0117 requires exactly the manifest-listed ordinary snapshot files plus
SHA256SUMS.json. Unlisted/missing files, symlink/special entries and more than
2,000 tree entries reject. Snapshot path components from the supplied checkout
root to the manifest are checked for symlinks. Empty ordinary directories are
allowed within the entry budget. The current retained tree already satisfies
closure: no snapshot bytes or pins needed changing.

Before success the checker repeats file membership and every listed digest,
and requires captured inventory/manifest bytes to match their final rereads.
This detects the tested late changes without changing successful output fields.

All seventeen quality tests pass: eleven previous tests plus six new snapshot
cases. New controls cover extra/missing files, file/directory symlinks and a FIFO,
a snapshot parent alias, late source/unlisted-file changes, whitespace-only
inventory/manifest changes, and a directory-only tree exceeding the entry cap.
Late mutations use controlled hooks around real local-reference/file operations;
they do not prove arbitrary race resistance. No failed validation attempt occurred.

All ten repository gates pass in out/checks/run-fh_3hr_r, retained in validation/.
Successful quality stdout is byte-identical to decision 0116's run. The reviewed
snapshot location/pin and all 24 native inputs are unchanged. No sibling, native
implementation, released/vendored bytes or historical evidence changed; no fresh
native execution is claimed.

Manual lint and 78/60-column/HTML generation pass. width-review.json records the
two existing long literal lines at 60 columns; identifiers remain complete.
Independent technical/reader approval, HTML visual review and installed-target
reference work remain open.

The traversal/check sequence is not atomic. Changes restored before comparison,
hostile directory-replacement races and changes after a final check remain
outside the guarantee. Snapshot file hashing still uses ordinary full-file reads;
source-size and filesystem-I/O bounds and general reference file/symlink policy
remain BG-056 follow-ups. Neither a complete file list nor matching hashes prove
signature authority, native behavior or independent reviewer approval.
