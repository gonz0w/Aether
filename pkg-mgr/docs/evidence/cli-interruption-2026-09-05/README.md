# CLI interruption evidence — 2026-09-05

The previous CLI exited directly from its signal trap, deleting temporary output
before emitting a helper receipt. The controlled harness reproduced the loss:
exit 130 and UNKNOWN were present, but the helper diagnostic and prepared intent
receipt were absent. A pending operation could therefore lose its recovery pin
from the user's output.

The CLI now records a caught signal and drains the foreground helper's buffered
output before reporting UNKNOWN and selecting the signal exit code. It does not
forward a wrapper-only signal or claim that the helper was cancelled.

`sh tests/cli-interruption.sh` passes twelve cases on the current macOS host:

| Scope | Signals | Output modes | Observed helper behavior |
| --- | --- | --- | --- |
| Wrapper PID only | INT, HUP, TERM | human, TSV | Continues after test releases its FIFO; wrapper waits |
| Isolated process group | INT, HUP, TERM | human, TSV | Controlled helper traps the signal and exits |

All cases use quiet mode and assert the expected 130/129/143 exit code, retained
receipt and diagnostics, no OK label or ANSI, preserved synthetic pending state,
and wrapper scratch cleanup. TSV stdout stays byte-identical to the fixture
receipt. Readiness and release use a file/FIFO handshake; ten-second timeouts
bound failures. The driver starts and cleans up only its own process groups.

This uses a copied real CLI and renderer plus a synthetic shell helper. It does
not validate a real intent digest, test arbitrary helper descendants, prove
process-group cancellation for real transactions, or establish durability.
Existing binary transaction fixtures retain their separate SIGKILL evidence.
Signals during output delivery, SIGKILL, blocked helpers and broken output pipes
remain outside this tested guarantee. Python is a development dependency only.

The full standards/fixture run is recorded in [fixtures.txt](fixtures.txt).
