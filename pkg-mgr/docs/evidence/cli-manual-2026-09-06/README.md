# CLI manual evidence — 2026-09-06

pkg-mgr(1) covers all 13 commands and seven options from the current help, including
output, exit status, environment, files, recovery, scope and non-destructive examples.
Mandoc strict lint, HTML and 60/80-column terminal rendering pass. Rendered terminal
text was inspected; an initial example-line overflow was shortened/wrapped and the
final checker rejects lines exceeding the requested width. The canonical mdoc source
is the authoring source; the rendered files here are retained observations.

Curated examples initialize/register hello-local, list, verify and inspect files,
then require status 64 for unsupported remove. The first example run found that
registration rejects a root outside the checkout with `package-evidence: evidence
currently requires ROOT beneath the repository`. The old docs/CLI.md example had
that same defect. Both references now use a private directory beneath the checkout.
Initial failed root: /private/var/folders/2k/hbwvd2qn4cb988kpjk1wcn800000gn/T/pkg-manual-check-9x_t2q1d.
The successful fixture root and renderer binary hash are in result.json.

Three negative controls reject a missing command, missing option and missing required
renderer. The first missing-renderer control accidentally omitted dirname/cat too;
its PATH setup was corrected before accepting the specific renderer rejection.
These are development controls, not authentic independent reader or release review.

This is a documentation change with curated host workflow testing and development/
standards gates. The unrelated full sixteen-fixture suite was not rerun. The normal
entry now invokes the manual check; a publication check must explicitly require
rendering. Packaged target lookup, format manuals and independent walkthroughs remain
open. No executable interface or release authority changed.
