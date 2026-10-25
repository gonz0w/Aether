# CLI output-delivery evidence — 2026-09-05

The new harness first reproduced a closed-stdout failure in human mode: exit 141,
no helper diagnostic, and discarded scratch output. The CLI now checks delivery
results, retains raw buffers on failure or caught rendering interruption, and
reports their private location when stderr remains writable.

Eighteen controlled host cases pass:

- Human and TSV, each with stdout, stderr, or both closed; helper exits 0 and 2.
- Human and TSV, each with INT, HUP, or TERM sent to the isolated process group
  after the first rendered byte of a result larger than pipe capacity.

Assertions cover the entire retained stdout and stderr byte sequences, observed
helper exit, mode-0700 receipt directory, preserved synthetic pending state,
nonzero CLI outcome and an UNKNOWN retention diagnostic on working stderr.
No success label is emitted in these cases. Delivery failure maps to exit 1;
caught signal codes take precedence. Both-closed cases require no diagnostic to
succeed before retaining evidence.

`sh tests/cli-output.sh` uses a copied real CLI/renderer and a synthetic shell
helper. Python supplies pipes, process-group isolation and bounded timeouts only
for development testing. This proves neither real transaction authenticity nor
power-loss durability. Existing transaction tests remain the authority for
package recovery. Signals while the helper is running still pass the prior
twelve-case harness. See [CLI contract](../../CLI.md) for discovery, retention,
exit semantics and remaining failure boundaries.

The [full fixture log](fixtures.txt) records the standards gate and fifteen tests.
A focused rerun additionally verifies complete large-result bytes (the full
suite snapshot initially checked the receipt prefix).
