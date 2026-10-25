# 0052 — Native owned attempt and cleanup-gated retry

Accepted 2026-09-06, BG-058 bounded ABI-6 native policy.

## Contract

Add a private, non-Copy Attempt record in the native fixture with local generation,
optional reader/writer/worker handles, exact adapter error and a retry-used flag.
Acquisition owns a complete channel pair. launch routes Adapter::launch's Result:
success transfers writer ownership to the worker; error retains both endpoints and
its operation/errno. A duplicate launch is denied locally. No raw trap probe is
used to generate this workload's launch failure.

cleanup closes each still-owned supervisor endpoint and reclaims a worker only
through the adapter's terminal precondition. Clear a field only after its operation
succeeds. Errors retain that handle and unprocessed handles for inspection/retry;
this fixture terminates at the relevant assertion on unexpected errors. There are
no waits, helper relationships, borrowed handles or implicit Drop cleanup in this
attempt profile. It does not replace other fixtures' wait accounting.

retry borrows the old record, requires complete cleanup, an exact launch EBUSY
(0x23001/16), first local generation and an unused retry budget, and creates one
new attempt with generation two. A failed channel acquisition retains the old clean
record and does not invent a new attempt. Successful retry consumes the budget;
reusing the old record is denied. Local policy errors use operation=0, separately
from native operation errno. No timer/backoff or automatic retry loop is added.

## Native witness and negative controls

Keep an admitted blocker in slot zero. Attempt generation one acquires another
channel and receives the real kernel EBUSY through Adapter::launch. Require retained
error and endpoints with no worker. A retry before cleanup must return local
operation=0/errno=16 and leave state unchanged. Clean the failed attempt, then the
blocker. Retry produces generation two; launch it, observe normal return 17, clean
it, and verify the old retry budget cannot be reused. One final ordinary worker
completes the existing result=100/reclaimed=3 oracle.

Omitting writer cleanup must hit assertion 961/reclaimed=0. Bypassing retry's
cleanup guard reaches the actual full channel factory and returns native 0x24000/16
instead of the required local denial, triggering 963/reclaimed=0. This proves the
pre-acquisition guard matters; a native allocation failure is not silently accepted
as equivalent to policy rejection. Both negatives require the exact designated
profile panic. Missing tools/timeouts/other failures cannot satisfy them.

Use the same pinned SI-04 producer and Rust/toolchain/4 KiB profile as decision
0051, run all 17 earlier non-custom cases plus these three, compare legacy binaries,
retain complete inputs and logs, and run full development checks. Apply Foundations
O-01/O-04, I-03–06/E-01–08 and scoped ownership/error/unsafe review. No new unsafe
code, dependency, producer ABI, shared pin or operator output contract is added.

This is one explicit busy retry after complete cleanup, not the full Python driver,
a generalized service graph, unknown-result recovery or automatic restart daemon.
Other error policy, wait-bearing attempts, cancellation/backoff and wider control
composition remain BG-058/BG-040/BG-033. No POSIX wait/signal claim follows.

Decision 0052 validation: all 20 native cases pass with 177 frozen inputs unchanged
and 17 compatibility binaries byte-identical. Full checks pass: 228 model tests /
23 mutation controls, 48 host tests, 37 harness tests and all eight offline gates.
Native catalog: 252 outcomes / 19 bundles / 5,220 listed files. Evidence:
`docs/evidence/native-attempt-retry-2026-09-06/`.
