# Initial runner startup attempt

The first 38 native cases passed. startup-changed correctly detected changed
argv at parent exit 110 but produced broker transport failure 990, not expected
970: parent exited before the following binding frame finished sending. This is
a control-ordering failure, not a passed rejection or a timeout. The three later
suites were not run. All reports/logs and failed source archive are retained.

The final witness drains the following frame without publishing bindings before
exiting. [Final qualification](../native-runner-startup-2026-09-06/README.md).
