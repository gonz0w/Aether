# Replacement intent hash failure review

Scope: HR-02/HR-04, private-root prepare and finish. No interface, native ABI,
release pin, successful output or runtime dependency change is planned.

Oracle: fail each of the five hash-file requests used to construct the intent
(old-record, new-record, world, others.tsv, bundle/artifact.kv). The exact helper
request must reach an injected-error marker and exit nonzero. Prepare must emit
no receipt and publish no pending transaction. Finish must emit no receipt or
advance the existing transaction. In both cases the complete target file/hash/mode
snapshot must remain identical. Existing successful prepare/finish/retry controls
establish that normal hashes still allow progress.

The PATH wrapper intercepts only sh verify-metadata.sh hash-file requests with the
selected transaction-relative suffix, and delegates all other calls to the recorded
host sh. Exit 73 represents a failed helper; it is not a physical full-disk test.

Retain a pre-fix regression under a 300-second process-group watchdog. After the
smallest correction, run scoped ShellCheck and the full 600-second sixteen-fixture
suite (including the controls and three standards gates). Record exact dirty-tree
inputs and failed outcomes. Update the owning contract, inventory and planning.
