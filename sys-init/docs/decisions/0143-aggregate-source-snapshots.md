# 0143 — Bounded aggregate source snapshots

BG-056 host slice, 2026-09-07; Foundations E-01–08 applies. Replace aggregate
source_hashes read_bytes/rglob reads with explicit bounded traversal and streaming
hashes. Preserve selected Python/explicit/native/lock/vendor-manifest paths and
archive-directory exclusion. Inventory: previous selected set ~1,900 files/16 MB,
maximum 809,643 bytes; scanned trees ~68,634 entries, no symlinks outside archive.

Limits: 200,000 traversed entries, 10,000 selected files, 4 MiB/file, 64 MiB total,
64 KiB read chunks. Reject symlinks/special entries under the four scanned roots,
including selected explicit paths. Do not traverse archive directories. Check
components at/below checkout root, ordinary-file identity before/after open/read
and path identity after read. Recheck selected membership after hashing. Close
file descriptors on every path. Existing source-hash output stays unchanged for
valid inputs; no source content executes and no dependency is introduced.

Use temporary inputs and controlled read mutation to test limits, links, special
files, identity changes and cleanup. Compare current snapshot map against the
legacy selection/digest algorithm; run focused/full checks. No native/sibling/pin
changes. These are sequential filesystem checks, not atomic snapshots or blocking
I/O deadlines. Ancestors above the checkout root remain outside this policy.
Initial/final snapshot error reporting and report publication remain the next
separate review; this slice retains existing failure behavior.

Validation: five snapshot tests and ten gates pass in run-9dv0gmtb; current
maps match the legacy algorithm exactly. Earlier run-9owdkqzb also passed before
completion of the documentation update. A wrong manual path interrupted that edit;
corrected without implementation changes. Final four manual commands pass after
one source-line reflow; initial lint output is retained. Native identities/pins
stay fixed. Evidence: ../evidence/aggregate-source-snapshots-2026-09-07/.
