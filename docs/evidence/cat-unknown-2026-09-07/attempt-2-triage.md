# Attempt 2: existing negative-control observation race

All new CAT cases passed. pad-launch-eof later produced owner990 before its
required parent104/owner970 context. Its deliberate padding admits the child;
parent request-channel EOF can be observed after admission but before the next
terminal poll. owner.rs treated that EOF as generic990. This timing window is
visible in the control flow; the failed log does not contain a terminal event.

Before correction: scope the padded-EOF mutant only, parent only, admitted state
only. On EOF yield and continue its existing bounded poll loop to observe actual
terminal state. Do not change the expected parent104/owner970 oracle, production
EOF behavior or kernel. Rerun full command suite/host and selected regressions.
Retain this source-matched attempt archive and all raw logs; remaining cases were
not run. This is not an accepted negative result or waived flaky coverage.
