# Attempt1: forced-stop serial oracle mismatch

Three positive fault cases passed. Forced stop reached owner100/reclaimed4 and the
profile pass marker, including direct owner observation of143/kind3, repeat-stop
stability, backend checks and stale native handles. The harness nevertheless
expected client terminal serial lines. The existing native stop path does not emit
those lines; only the backend terminals appear. Correct the forced-stop serial
oracle to those two exact backend lines and unchanged100/reclaimed4. Retain direct
owner terminal checks and wrong-stop-kind negative control. Add no kernel marker.
This was a failed harness attempt, not accepted qualification. Remaining cases
were not run. Source-matched archive, receipt/log and timing are retained; rerun
full command/host checks and selected regressions on final sources.
