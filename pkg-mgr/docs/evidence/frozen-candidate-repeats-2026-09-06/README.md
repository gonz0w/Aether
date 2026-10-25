# Frozen candidate transaction repetitions — 2026-09-06

Two additional transaction-fixture runs pass against fresh extractions of
candidate archive `9872d60f0077d132d60696c0a11ea038910bbb8512997d9ac0585e752d74e043`.
The previous full-suite witness on this same archive supplies one earlier run;
repetitions of older candidates do not count. Nothing is rebuilt, edited, signed,
tagged or published here.

The one-off repeat.py driver verifies the retained archive pin before each
extraction, verifies all selected file bytes/modes before and after testing, and
requires the unchanged source manifest. Each run invokes the candidate's own
process-group watchdog with a 300-second deadline in a fresh private root.
Extraction has a separate 60-second deadline. The two runs are sequential;
no parallel-writer or performance claim follows from their timings.

Oracle: zero status plus eleven exact completion markers for binary descriptor,
metadata reader, preflight receipt, producer/sort, intent and comparison errors;
actual human/TSV CLI receipt recovery; partial-copy/rename handling; killed
publication points; and ownership-conflict rejection. Missing markers, timeout,
failed status or changed inputs invalidate that repetition. Every result and raw
log is retained separately; failure/incomplete stays distinct from pass.

The original candidate qualification and 27-case publication/cleanup audit remain
separate evidence. These fixed-fixture repetitions are bounded repetition, not
soak, randomized fuzz, physical full-storage/power-loss, concurrent-writer,
hostile-filesystem or native-execution qualification. The driver is an evidence
artifact, not a new product command or test framework. No active inventory or
candidate source change is required.

[Independent review handoff](REVIEW-HANDOFF.md) prepares concrete review scopes and
receipt requirements. It does not assign a reviewer, send a message or provide
independent sign-off. Captured clean-builder setup, independent content/build/reader
reviews, a monitored security contact and publication approval remain release gates.


Both runs passed all eleven markers with unchanged selected bytes/modes, source
manifest and archive digest. results.json records individual timing/status and
300-second deadlines; run-1.log and run-2.log retain raw output. Together with the
[original full-suite qualification](../binary-reader-faults-2026-09-06/README.md),
this makes three transaction-fixture witnesses on this exact archive. The separate
[27-case publication audit](../publication-audit-2026-09-06/README.md) remains valid.
No candidate or runtime changes were needed. The freeze remains in effect except
for demonstrated release blockers. Independent reviews are the next human gate;
no reviewer approval has been fabricated or inferred from these runs.
