# Build-output storage cleanup — 2026-09-14

The user requested removal of old builds, test outputs and temporary clutter.
[Results](results.json) records the actual completion state, byte accounting and
every removed path. [Selection](selection.json) identifies the completed suites;
[review](review.md) defines preservation and verification requirements.

Each completed suite is stored as a tar.gz under
`/Users/cam/DEV/Aether-userland/build/retained-artifacts`. The matching JSON index
records every original regular file's hash, size, mode and timestamp. Each archive
was read back and every file compared before the original directory was removed.
The source inventory was checked again to reject changes during compression.
Failed inner test artifacts and diagnostic logs are preserved with the rest.

To resolve a historical receipt's now-absent build path, find its suite's
`original_path` in results.json. Verify `archive_sha256` and `index_sha256`, then
extract that archive into a fresh directory and compare restored files with the
JSON index. Archive members are relative to the original suite root. Restore to
the original path only when it does not already exist. Existing sealed evidence
is deliberately unchanged; this relocation index supplements its historical paths.

Compiler .zig-cache directories under the selected inactive consumer producer
roots are disposable and recorded separately. Source files/tests, pinned SDKs,
source/tool inputs, support tool locks and sealed evidence remain in place. An
active sibling Aether test uses the shared SDK; no sibling files or shared SDK
were selected. Unrelated or unattributed files in /private/tmp were not removed.
There is no scheduled pruning or new runtime qualification.

Validation is byte-level archive readback, unchanged-source verification,
post-removal existence checks and the local quality gate. Independent review is
pending; the executing assistant reviewed the scoped selection and preservation
checks. See the final results for any incomplete operation; never treat an archive
merely existing as successful verified relocation.

## Completed result

28 suites compacted and20 disposable compiler caches removed. Reclaimed
45,618,270,208 allocated bytes (42.49 GiB); archives occupy about19 GiB.
All member readback/source stability/removal checks and the quality gate pass.
The operation completed in569 seconds. Source tests, SDKs, uncommitted files and
sealed evidence are preserved. See summary.json for the machine-readable result.
