# Bounded pending/disposition owner

Before code: implement the state needed for caller-local standard signals as a
host-qualified component. Do not enable native dispatch or replace the active C
facade before transport delivery boundaries are protected. One future domain owns
dispositions and pending bits; the current execution context continues to own its
mask. No remote PID targeting, queue allocation, active-handler token or locks.

Contract: signals 1–31 except 9/19; invalid inputs preserve state. Duplicate posts
coalesce. IGN drops new posts and discards any queued occurrence when installed.
DFL is retained as an explicit decision for the future dispatcher, never treated
as successful handling. Lowest unmasked pending signal is selected. Selection is
read-only; failed frame preparation leaves pending state intact. Under continuous
owner serialization, remove the selected bit only when the validated frame and
new mask can be published. Action changes and posts cannot interleave between
selection and commit. Reset belongs after stopped-domain teardown, not a handler
return: longjmp needs no pending-owner token cleanup.

Handler records have entry/restorer/mask only; canonical nonzero addresses are
structurally validated, but mapped RX validation remains the runtime owner's
obligation at installation and delivery. No SA_SIGINFO, alternate stacks, restart,
real-time queuing or syscall format is introduced. Default termination/ignore/stop
effects must be explicitly enumerated in dispatch integration before enabling it.

Simplicity: one fixed table plus bitset is sufficient for coalesced ordinary
signals; a service, queue, delivery-token stack or generalized event abstraction
adds no necessary behavior. Nothing is removed until the replacement owner is
native-qualified. At most 1 KiB per future domain, no heap; no live domain storage
is added in this step. Tests must cover masks/coalescing, failed preparation,
action replacement/IGN, invalid atomicity, owner isolation and reset. Test a
broken eager-dequeue version against the selection-preservation check. Run Debug,
ReleaseSafe and the full host/standards suite; no target behavior changes yet.

## Results

Five new owner tests plus nine imported frame tests pass in Debug and ReleaseSafe.
The full host suite and standards checks pass, including 98 Python tests. The
actual frame-composition test observes failed preparation without dequeue and
later delivery eligibility after mask restoration. The eager-dequeue mutant
fails the intended pending-preservation assertion. Its initial log verifier
expected FAIL immediately after the test name; Zig printed a field mismatch first.
Corrected inspection verifies the same retained failure log without rerunning it.
An earlier passing four-test run and its source are also retained.

Formatting, workflow and all four simplicity snapshot hashes pass. Sources and
mutant inputs are hash-verified in the archive. No native dispatch or domain state
is enabled, and no QEMU acceptance is claimed. The previous target packet is
unchanged. Default effects, native action parsing, transaction guarding and native
self-delivery remain required before replacing the active facade.
