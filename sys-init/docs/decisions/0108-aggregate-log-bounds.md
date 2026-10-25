# 0108 — Aggregate gate log bounds

Host harness change, 2026-09-06; BG-056.
The aggregate watchdog limits elapsed command time but its direct output files
have no byte bound. Capture both pipes concurrently with a combined 4 MiB limit
per gate. Preserve separate raw stdout/stderr files and per-stream ordering;
inter-stream ordering is unspecified. Retain the accepted prefix and report
output-limit distinctly from fail, timeout, interrupted and infrastructure error.
Add output_limit_bytes to each gate record without changing existing fields,
summary schema, exits, command flags or test acceptance markers.

Keep the 60-second default wall deadline through pipe draining and process exit,
including children that close their pipes early. Kill/reap the owned direct child
and kill its group on capture failure. Trusted non-detaching descendants are in
scope; detached nested compiler groups remain a separate unresolved composition
issue from decision 0107. Disk, source hashing and child-created artifacts are
not bounded by this capture budget. No containment guarantee is added.

Use real-child exact-boundary, simultaneous-stream flood, overflow, early-pipe
closure and inherited-pipe descendant cases, plus existing CLI/nonzero/missing-
tool/timeout controls. Run all repository gates. This is host-only behavior;
no native source, release pin, sibling repository or post-R1 feature change.
Documentation impact: aggregate manual, development guide and quality inventory.
Evidence: docs/evidence/aggregate-log-bounds-2026-09-06/README.md.

Validation: twelve focused runner tests and all ten gates pass in
out/checks/run-5d53pv35. Five retained capture probes distinguish exact-boundary,
both overflow streams, closed-pipe timeout and semantic nonzero failure.
The updated manual lints cleanly and fits 78/60 columns. All 24 checked native
inputs remain unchanged. No independent review or native execution is claimed.
