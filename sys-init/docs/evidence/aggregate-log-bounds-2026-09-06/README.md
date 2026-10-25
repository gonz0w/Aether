# Aggregate log bounds evidence

Decision 0108 replaces unbounded direct gate-log writes with concurrent pipe
capture. Each gate retains separate raw stdout/stderr prefixes up to a combined
4 MiB. output_limit_bytes is additive metadata; output-limit is a failure,
separate from semantic nonzero exit, timeout, interruption or infrastructure
error. Existing schema, CLI flags, summary streams and exit meanings remain.
Per-stream byte order is preserved; ordering between streams is unspecified.

Twelve focused runner tests pass. New cases cover the exact combined boundary,
overflow on either stream, concurrent pipe flooding, early pipe closure and a
non-detaching descendant holding inherited pipes after its parent exits. The
last test verifies that its delayed file write does not occur after timeout;
this bounded observation is not proof of cleanup for arbitrary descendants.
Existing CLI/exit, missing-tool, timeout, empty/partial/skipped-suite controls
remain. Five separate capture probes retain raw logs and capture-receipts.json,
including exact 128-byte accepted prefixes and distinct timeout/failure records.

All ten aggregate gates pass in out/checks/run-5d53pv35. The largest combined
gate log in this run is 10,057 bytes, below the fixed 4 MiB budget. validation/
retains complete results and raw streams; the full suite includes the twelve
runner tests. No failed validation attempt occurred in this slice. Manual lint
and 78/60-column/HTML generation exit zero. Terminal renderings fit both widths;
HTML visual review, independent technical/reader approval and target manual
lookup are not claimed.

All 24 native source inputs match the preceding boundary-review manifest.
No compiler helper, native runner, native implementation, release pin or sibling
repository changed in this slice. No fresh native execution is claimed: this
change affects host aggregate capture and is exercised by real host processes.
The before/ and source/ copies distinguish this slice from earlier dirty work.

The 60-second command deadline includes pipe drain and direct-child exit.
On capture failure the runner kills its owned group and reaps the direct child.
Detached nested compiler groups remain open under BG-056; so do inner host/model
capture limits. Child-created artifacts, source hashing and blocking filesystem
operations are outside this byte/time guarantee. This is not a containment or
production resource-limit claim. Published pins remain fixed; candidate standards
remain unpublished review inputs.
