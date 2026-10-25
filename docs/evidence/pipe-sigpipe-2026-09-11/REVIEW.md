# Scoped implementation review

Implementing-agent review; independent reader/consumer acceptance remains pending.

The new post path requires an actual validated EPIPE result, nonempty write and
live pipe-writer binding4. Existing file_io rejects malformed frames/errno before
that boundary. Posting occurs before the outer mask is restored. Delivery uses
signal0 polls, not another signal13 post. Kernel queue state supplies coalescing
and action changes; no duplicate user-space signal queue was added.

The opt-in mask-leave path saves errno before mask restoration, which can itself
deliver a handler, and restores errno after the explicit poll. Public sigprocmask
also saves errno before its native call, publishes old-mask output before polling,
and polls only when a set was supplied. Existing error returns retain their errno;
failed native delivery/restoration terminates this bounded facade with125. These
polls are behind FORK_PIPE_SIGNAL and do not change other profiles.

The handler uses bounded native mask inspection and volatile sig_atomic_t counters.
Tests intentionally change errno inside it. Real pinned musl sigaction/restorer is
used, not the startup facade's old local action table. New target flags select
existing kernel mechanisms, without changing kernel source or released ABI.

The owner accepts only the expected core operations and counts. It observes actual
signal13 terminal and request EOF before holder retirement/backend close/reclaim.
SIGPIPE termination is distinct from the preceding forced-stop policy translation.
Three fresh parent/backend generations remain inside current resource limits.

The signal-only dispatcher uses one bounded32-byte frame and one-byte EOF scratch.
No new service, heap allocation, channel/task quota, unsafe block, dependency or
general signal framework was introduced. The legacy startup header keeps its existing style;
full-header formatting migration is out of scope. The changed opt-in branches
are reviewed directly and compile with the pinned native warnings. This is not
public pipe/SDK acceptance or a claim about all signal interruption schedules.

The rebuilt76 pre-existing copied public-fork client ELF images are byte-identical
to the previous qualified set; see legacy-client-images.json. This directly checks
the guarded facade changes for those clients, not every possible build or kernel
image. The full target suite separately verifies their runtime behavior.
