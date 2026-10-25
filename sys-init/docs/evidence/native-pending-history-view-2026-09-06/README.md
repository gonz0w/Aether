# Bound terminal-history view evidence — 2026-09-06

Decision 0085 passes 151 native cases, preserving all 143 previous oracles.
Seven positives qualify private bound terminal views, duplicate replay, every token
field, owner/index, equal-generation cross-service token, actual other worker and
empty-session denial. Every terminal probe checks retained state before/after
queries and exact raw history afterward. Positives finish 100/reclaimed=3 after
known fixture cleanup; the token-omission control fails exactly at 1050/0.

All 184 frozen inputs remain unchanged; 87 of 143 prior
images match byte-for-byte. Every changed image has fresh target execution.
Maximum image is 4096 bytes under the unchanged 4 KiB limit. Eleven
size/layout preflights are retained. Shared pure predicates and split probes keep
all assertions; no compiler profile, linker bound or worker change was needed.

This implements PH-01/02 origin and replay within a borrowed sampling session.
The view cannot mutate Driver or Sample and exposes no arbitrary candidate API.
It does not implement independent-candidate equality/conflict, fixed diagnostic
storage, retention across session destruction or journal acknowledgment/retirement.
Next BG-058 PH-03/04 qualifies a separately labelled synthetic conflicting sample
while retaining both histories and closing admission; PH-05/06 capacity and sealing
and BG-057 PH-07 whole-cut retirement remain open. Full launch composition,
additional NT-04 O1 injections and BG-033 unknown-owner recovery remain open.

`witness/` is the accepted fresh native run, independently sealed and registered
in the native coverage catalog. `preflight-1` through `preflight-11` preserve
strict build/size revisions, including failed links. `host-checks/` retains
synthetic host runs. Full offline development checks and adoption snapshots are
retained separately. The root manifest seals every retained file except itself.
No historical evidence, release bytes or sibling repository was modified.

Validation: all nine development gates pass in `out/checks/run-6ci2bl01`, with
no skipped gates and unchanged checked sources. The offline audit now covers
2209 historical native outcomes across 45 bundles, separate from the fresh
151-case native witness. All 38 harness tests, nine existing sample tests and
three pending-view host tests pass; three omission controls fail their exact
assertions. Eleven current consumer inputs and both worker/builder inputs match
the retained execution/build snapshots. Full logs and adoption records are retained.
