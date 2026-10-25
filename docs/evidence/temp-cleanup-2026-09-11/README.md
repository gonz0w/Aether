# Temporary-file cleanup — 2026-09-11

The maintainer authorized removal of temporary files no longer needed after the
volume reached roughly 118 MB free. This receipt records disposal of abandoned
Git temporary packs and redundant unpacked Aether test outputs, not evidence
archive disposal, history rewriting or runtime qualification.

Removed 96 Git temporary pack files (320.64 GiB allocated) and 736 complete build
output directories containing 798,252 files (264.72 GiB allocated): 585.36 GiB in
total. Final df reported 580 GiB available. Allocated-file totals and volume free
space are separate measurements; the volume is shared with other applications.

Git marked the temporary packs as garbage. Open-file inspection excluded an active
ChatGPT-launched git add operation. A later pass removed its abandoned temporary
file only after the operation no longer held it open and its inode, size and
modification time remained unchanged across inspections. Real packs, indexes,
loose objects, refs, reflogs and working source changes were not deleted or pruned.
Final git count-objects reports zero garbage; git fsck --connectivity-only
--no-reflogs passes. This is a connectivity check, not a full object-content audit.

Build removal required an exact inventory, no symlinks or open files, and unchanged
file metadata immediately before removal. Every file matched either a SHA-256
index bound alongside an unchanged archive by its evidence manifest, or the
corresponding streamed archive member directly. Older nested JSON and SHA256SUMS
manifest formats were verified too. Archives, manifests, reports and source
snapshots remain in their original locations. Incomplete or different comparisons
were retained and are listed in duplicates.json; a preserved entry is a comparison
exception, not a newly diagnosed runtime defect.

connections-suite-hz9wuimq and launch-suite-dys6c1bi remain unpacked as the latest
baseline. The native SDK, init-capacity tools.lock.json, dependencies and current
cache remain. Other unique/unmatched outputs were not classified as disposable.
The remaining zig-out directory occupies about 95 GiB. /private/tmp was inspected;
unverified downloads, other projects' files and useful helper inputs were retained.
No sibling repository or released standard pin was modified.

See summary.json, git-temps.json and duplicates.json for counts, exact paths,
archive identities, verification methods and exceptions. Restore a removed build
from its named archive before running a historical command that expects that
unpacked path. Pass scripts are inert records of this cleanup, not installed tools
or a new automatic retention policy. The maintainer's existing evidence-retention
rule still applies to unique evidence and archives.

Checks: removal inventories, latest baseline and SDK/tool existence checks, Git
connectivity, workflow inventory, shared standards and diff whitespace. No runtime
source changed, so no QEMU or full native suite was selected for this cleanup.
