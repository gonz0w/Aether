# 0117 — Reviewed snapshot file closure

BG-056 host checker slice, 2026-09-07. Require the reviewed snapshot tree to
contain exactly its manifest-listed ordinary files plus SHA256SUMS.json. Reject
symlink components from the checkout root to the manifest, symlinks/special files
within the snapshot, and more than 2,000 tree entries including directories.
Walk without following links. Preserve existing snapshot bytes and pinned digest.

Capture the initial inventory bytes and compare them and manifest bytes again
before success; repeat snapshot membership and listed-file digest verification.
This detects the controlled mutations tested, not atomic snapshots or changes
restored before comparison. General reference file policy, bounded source-file
reads and filesystem I/O deadlines remain separate follow-ups. No native, sibling
or release-pin changes. Test extra/missing/symlink/FIFO entries and late mutation,
then run the aggregate. Keep existing result schema and stderr failure contract.

Validation: seventeen quality tests and all ten gates pass in
out/checks/run-fh_3hr_r. Success stdout matches the previous run; snapshot pin
and all 24 native inputs are unchanged. Manual lint passes with the already
recorded long literal lines in the 60-column rendering.
