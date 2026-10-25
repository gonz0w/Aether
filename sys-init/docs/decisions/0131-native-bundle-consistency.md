# 0131 — Complete native bundle membership and final consistency

BG-056 host slice, 2026-09-07. Require each bundle to contain exactly its listed
ordinary files plus SHA256SUMS.json. Reject symlink/special entries, walk without
following links and cap traversal at 20,000 entries including directories.
Current retained bundles have no extras and at most 1,736 total entries.

Recheck membership and manifest bytes around payload hashing; reverify the bundle
after semantic auditing. Before CLI success, verify every cataloged bundle again
and compare the catalog bytes to the parsed capture. This detects persistent late
changes including changes to earlier bundles while later bundles are audited.
Preserve pins, retained bytes and success output; no native or sibling changes.

Test extra/special files, traversal bounds and late record/payload mutations,
including cross-bundle/final checks; run focused/full gates. E-01–08 host scope.
Sequential comparisons are not an atomic filesystem view; restored mutations,
changes after final comparison, I/O deadlines and strict receipt schemas remain
open. Independent review stays pending.

Validation: 50 native-harness tests and all ten gates pass in run-djhnko6x.
The first focused run exposed old permissive test expectations; updated tests now
require final rejection. Review also corrected a missed post-hash check insertion
before the final run. Both logs are retained. Native output, catalog and 24 native
inputs stay unchanged; four manual commands pass. Evidence:
../evidence/native-bundle-consistency-2026-09-07/README.md.
