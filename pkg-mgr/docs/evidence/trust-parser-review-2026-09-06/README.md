# Trust parser lint review — 2026-09-06

The metadata helper is lint-clean under ShellCheck 0.11.0 without suppressions.
SC2094 findings came from passing the read-loop input path to invalid_record even
though the function only printed its second argument to stderr. Removing that
unused parameter preserves exact diagnostic text and clarifies that no input file
is written. Descriptive source_kind and snapshot identity/time/signer fields remain
required, nonempty and duplicate-checked, but their unused stored values are removed.
Comments make the existing research scope explicit: no freshness/key-selection
policy is implemented by storing those values. No external format or trust authority
changed. This is a cleanup of unused data, not a newly enforced security boundary.

verify-metadata.before.sh retains the exact pre-change helper. Differential execution
of all 71 source-corpus inputs produces identical status, stdout and stderr; the
parity inventory is retained. Source-corpus logs identify the independent retained
input/output directory. Normal suite snapshot/build/manifest cases provide additional
regression coverage. Remaining whole-repository lint diagnostics: 62. None were
suppressed by this change; the earlier 98 count is historical.

Snapshot differential checks add 43 cases: canonical input plus missing, duplicate
and empty controls for all 14 required fields. Both helpers return identical status,
stdout and stderr. Negative controls additionally require their named diagnostic.
The canonical control intentionally reports tool-unavailable, not authentication.
Inputs, outputs and results are retained in snapshot-controls.

All sixteen active fixtures and three standards checks pass under the suite watchdog,
including source corpus, snapshot verification, build records and manifest coverage.
Runtime/test inputs were rechecked unchanged after completion. This closes lint
findings for this helper; full repository review and release gates remain open.
