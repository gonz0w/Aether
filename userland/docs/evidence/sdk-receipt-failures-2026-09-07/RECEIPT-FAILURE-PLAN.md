# SDK startup prerequisite failure retention — UL-005 / UL-063

Scope: move prerequisite receipt reads inside the startup harness's existing
failure/report boundary. Missing files and malformed JSON must produce an
incomplete summary with an error and zero process commands. Preserve pin checks,
exit 1/error stream, successful ELF bytes, source ownership and 30-second process
bounds. This implements the existing E-05/06 and CP-02 evidence contract; no new
native behavior, dependencies, shared standard or sibling change.

Tests: missing PIN, missing package layout and malformed PIN JSON under private
build directories; assert exact failure category, retained summary and zero run
calls. A prior-source regression run must fail these controls. Rerun the existing
staged-copy control and full startup link. Use Python 3.10+ syntax; qualification
is limited to the actual interpreter recorded in evidence. Test suite budget 60s;
startup budget 5 minutes using existing per-command limits. Run the local quality
gate. No native rerun because native source and ABI are unchanged.

Documentation: SDK README/coverage, backlog and STATE; retained evidence under
docs/evidence/sdk-receipt-failures-2026-09-07. Keep all earlier snapshots and logs.
Independent technical review remains pending. This handles unavailable files and
JSON syntax errors; structurally invalid but parseable receipts require separate
schema validation. Failure to create the work directory itself cannot be recorded
inside that directory. No blanket all-failure or hostile-filesystem claim.
