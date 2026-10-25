# M2 local endpoint capabilities

This slice adds one boot-owned endpoint and two fresh Rust domains after the
scheduler experiment. The typed [task/memory extension](M2-LIFETIME.md) adds one fixed worker factory.

One boot-CPU owner contains twelve holder tables of eight slots, a pool of 32
derivation nodes, and a four-message FIFO. Messages contain one u64; no user
pointers, transferred capabilities, sender IDs, or remote routing are accepted.

Handles are `(generation << 32) | slot`, resolved only in the caller's table.
Generations start at one; removal increments them. A maximum-generation slot
is permanently retired rather than wrapping. Numeric task IDs grant nothing.
Trusted bootstrap alone grants initial endpoint capabilities to the two tasks.

Rights: send=1, receive=2, derive=4, revoke=8, destroy=16. Derive creates a handle
in the same holder table with a nonempty subset of the parent's rights. Both a
free slot and node are required before mutation. Revoke removes all descendants
but keeps the invoked capability. Close removes a leaf; it returns Busy if it
has descendants, requiring explicit revocation first. Destroy requires its own
right, invalidates every endpoint capability, zeros queued data, and permanently
retires the endpoint for this slice. There is no object reuse or memory release.

Operations run with interrupts disabled; scans use 96 fixed slots and 32 nodes; revocation performs at most 32
ancestry walks of at most 32 nodes. Send/receive are nonblocking: Full/Empty leave state unchanged. Kernel
entry never allocates implicitly. Revocation stops future invocations; already
queued messages remain until receive or endpoint destruction.

ABI: int 0x80, RAX operation (1 send, 2 receive, 3 derive, 4 revoke, 5 close,
6 destroy); RDI handle; RSI payload or child-rights mask. Return RAX status and
RDX value (received message or derived handle); other registers preserved.
Status: 0 success, 1 invalid/stale, 2 denied, 3 exhausted, 4 full, 5 empty,
6 busy. Operation 0 terminates the calling fixture, with its result in RSI.
These operations are active only for the two new IPC domains; old test fixtures
retain their isolated exit convention. This transitional test ABI is not public.

Acceptance: user-mode sender checks wrong rights, queue backpressure, slot
exhaustion, stale generations, derivation and revocation; the sender exits after filling the FIFO, and only then is the receiver made
runnable. The receiver checks ordered messages, an empty queue, destruction,
and rejection of the destroyed handle before exiting. This deterministic
nonblocking transport check is separate from the preceding concurrent timer
experiment; request/reply protocols and receive blocking are not implemented. Kernel-observed sends, receives, denial paths,
and destruction must agree before the final IPC marker. Host tests exercise
lifetime edges including generation exhaustion and atomic resource failures.
Task/memory authority and teardown before backing-page reuse are implemented by the lifetime extension.

The negative IPC image makes the receiver expect an incorrect message; the
user-side failure must result in a kernel acceptance failure, not a pass marker.
