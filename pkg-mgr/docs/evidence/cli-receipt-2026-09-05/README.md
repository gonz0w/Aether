# Prepared-transaction receipt recovery — 2026-09-05

The binary fixture now invokes `tests/cli-receipt.py` against its validated old
and proposed app packages. This uses the actual CLI, prepare/finish implementation,
package records, intent hashing and state verification. Package contents and host
receipts remain synthetic, as in the ordinary binary fixtures; no native or real
source-build claim is added.

Two isolated workflows cover human output with stdout closed, and TSV output
with both stdout/stderr closed. In each workflow:

1. Prepare returns CLI exit 1 because delivery failed, while the retained
   helper-exit is 0 and the actual pending intent matches the receipt digest.
2. Normal verification is blocked; the old active record and payload remain.
3. A forged digest in the retained receipt is rejected by ordinary finish
   validation, preserving the pending transaction and old package.
4. Finish using the original receipt digest publishes the new package. Output
   fails again; the retained completed receipt and helper exit still show what
   the helper observed.
5. Repeating finish with that digest succeeds through completed-history
   validation. Full state verification passes; new authority matches the bundle,
   old payload/record remain retained, and unrelated records/world are unchanged.

The driver uses private disposable roots and receipt directories. Each command
has a bounded timeout and a separate process group cleaned up by the driver.
Retained output is not independent authority: the normal pinned transaction
validation remains mandatory. These are single-writer host checks, not fsync,
crash-durability, arbitrary cancellation or native-runtime evidence.

The first full suite exposed an intermittent timeout in the earlier signal
fixture's unreleased FIFO read. The driver now releases its FIFO after either
signal scope, allowing shells that defer traps during reads to proceed. Ten
consecutive twelve-case runs passed, followed by the full suite. This refines
the test handshake; no production signal behavior changed in this slice.

[Full suite](fixtures.txt) and [focused binary fixture](binary.txt) record the
results. Deliberate SIGKILL diagnostics from the existing fault tests are expected.
