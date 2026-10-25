# Archive readback failure

The initial attempt3 archive and seal were rejected: only generated output-root
`.DS_Store` changed between inventory hashing and archiving. Every other original
and archived member matched its inventory hash. Runtime source hashes and all test
results remain valid; this is macOS folder metadata, not executable/evidence drift.
The deletion guard prevented cleanup and no manifest was published.

Preserve the failed archive, initial inventory, mismatch audit and both failure
logs. The initial metadata bytes were not snapshotted before the change; only
their recorded digest remains. The archived/current metadata version is preserved
in the failed archive. Retry packaging from the retained originals and verify every
member before deletion. No native test rerun is justified by this metadata change.
