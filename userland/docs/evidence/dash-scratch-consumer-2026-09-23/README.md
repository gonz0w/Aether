# UL-007 scratch consumer qualification — 2026-09-23

The unchanged leak, redirection and denied-redirection scripts pass locally on
the frozen final denied-redirection producer fixture. Eleven focused cases plus
all355 connections cases pass:366 native executions and22 independent exact
terminal/reclaim/PASS comparisons. Both runs share266 harness source hashes.
Host checks pass, including104 Python tests. All631 restored source/support and
4311 SDK files remain unchanged. Owned-process cleanup is complete.

Focused execution took75.33seconds; full connections took1163.96seconds, within
the1800-second review ceiling and3600-second outer deadline. Native suites ran
sequentially. Substitution host checks ran during the full connections suite;
these timings are bounded-run evidence, not a performance benchmark.
No local build, host, native or retention retry was needed.

## Observed behavior and limits

- Leak: actual FD9 scratch writer survives fork/exec, unchanged helper exits95,
  dash collects it and exits22, stdout empty. Two lifetimes, backend17 and six
  reclaims. Grant/description/skip controls reject exactly as pinned.
- Redirection: shared-offset A/B writes, closed writer aliases and reopened reader
  reach the real helper; exact owner readback `AB`, helper0/dash0/backend17 twice,
  six reclaims. Lost-write, retained-stdin and skipped-helper controls reject.
  This script does not exercise append mode.
- Denied redirection: actual non-exec subshell receives authenticated EACCES with
  no handle or file mutation; child2, dash0 and backend17 twice, exact owner
  readback `denied ok\n`, six reclaims. Wrong-errno/output controls reject.

The owner verifies exact FD9 table/reference and actual denial, rather than
accepting arbitrary helper95 or any child nonzero. See source-review.md.
Zero-reclaim semantic controls abort as expected; their outer VM/process cleanup
is separately complete. This is volatile private-fixture acceptance, not general
filesystem, public SDK, POSIX, M3 or assembled R1 acceptance.

## Reproduction and retention

preparation.json pins the final producer seal, tools receipt, musl input and
isolated build root. producer-packet contains final runtime/review archives and
support-packet the verified scaffold. SDK/tool files remain external prerequisites.
run.py prepare restores support, final sources and review inputs, removing only
restored generated Python caches before source pins are captured. Actual frozen
.DS_Store bytes remain checked. focus-selector.py is the relocated producer AST
selector widened solely to the eleven scratch cases. review.md and the later
regression-plan.md preserve both scopes before their respective runs.

Run host, then timed.py focus and timed.py connections in a fresh packet/work root;
never overwrite these sealed results. retain.py and retain-regression.py compare
completed receipts before copying raw logs under cases/ and regression-cases/.
Source/SDK checks run before and after each mode. Producer historical failures
remain in the sealed producer packet; this consumer does not reclassify them.

compaction.json maps completed suites to build/retained-artifacts archives and
file indexes. Every archive member and unchanged original inventory is verified
before unpacked suites and this fixture's compiler cache are deleted. Old absolute
suite paths are therefore archival locations, not expected live directories.
Sources, tool-lock, SDK, raw retained logs and previous evidence are preserved.
SHA256SUMS seals this packet after final checks; quality.log retains the local gate.

Matching command-runner producer/consumer coverage remains pending. The later
substitution fixture has its own source identity and evidence. Pipeline and
early-reader, poisoned-close recovery, independent reviews/public SDK, persistence
and assembly remain open. No sibling implementation or release pin was changed.
