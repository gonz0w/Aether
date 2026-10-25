# Quality manual and CLI coverage — UL-071

For contributors reviewing the first original userland command manual. This is
host documentation qualification for quality 0.1.0, a slice of UL-061. The
[mdoc source](../../../man/man1/aether-userland-quality.1) is authoritative;
[the command record](../../quality/quality-command.json) binds the actual checker
hash, options and case IDs. The name is a manual label, not an installed alias.

The [plan](PLAN.md) records clauses, limits and independent oracles. The current
Codex task reviewed checker control flow, documented streams/statuses and failure
recovery. No checker behavior, release pin or sibling source changed.

## Executed results

All 16 final host invocations pass their named oracles in [results](results.json):
help/version, invalid option/operand, normal gate, blocked release preflight,
wrong-pin rejection and pre-verification help/version, repeat/abbreviated options,
mandoc lint, ASCII 78/50-column and HTML output, and host renderer environment.
Exact commands, executable hashes, environments and cleanup are in process receipts.
The platform mandoc does not support `-V`; its binary digest plus OS build identify
this renderer, without an invented upstream version. Python 3.14.7 was exercised;
3.10/3.12 are absent and remain unqualified minimum-version claims.

The final terminal renderings were inspected at both widths after removing only
backspace overstrike pairs for reading; raw renderer bytes are retained. The
50-column version now keeps every line within 50 columns, including copyable
examples, after removing unnecessary literal-block indentation. Required headings,
options, exits, paths, security and recovery text are present. HTML output has
semantic section anchors and content; browser visual inspection remains blocked.

Retained attempts:

- attempt-1: CLI cases passed; mandoc rejected section order and missing author
  markup. Corrected the source; the original source and diagnostics remain.
- attempt-2: lint passed; a raw ASCII marker check failed on overstrike formatting.
  Corrected the comparison to strip overstrike pairs, preserving original bytes.
- attempt-3: ASCII checks passed; the HTML marker assumed an unbroken heading.
  Switched to its exact section anchor. Narrow-output inspection also found the
  indented example overflow and corrected the mdoc source before the final run.

The optional browser inspection attempted the local generated HTML file and was
rejected by the browser URL policy. No alternate route was attempted. This is a
missing visual check, not a rendering failure or an independent reader review.

## Limits and follow-up

Independent technical/reader review, browser visual inspection, packaged offline
lookup and the remaining command/API/configuration manuals stay open in UL-061.
UL-062/063 retain minimum-interpreter checks and broader tooling migration.
The existing quality checker's direct-child timeouts do not prove whole-process
cleanup; its subprocess ownership remains a specific UL-063 follow-up before a
behavior change. This documentation does not silently fix or waive that boundary.

The normal gate and negative inventory-link controls are recorded separately in
QD-09 receipts. Release completeness must still reject draft inventory. No native
system, security certification or release approval is claimed. This packet retains
all attempts and source/tool identities; hashes establish identity, not review
independence or authenticity. Original work is BSD-2-Clause.
