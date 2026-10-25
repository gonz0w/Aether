# SIGPIPE adapter qualification

Requirement: pair pipe EPIPE with actual native SIGPIPE before connecting pipes
to dash. Use the existing self-signal13 and explicit poll primitives, enabling
existing actions/public/mask-delivery/termination flags only for new private
profiles. No kernel or released ABI/pin change. Public pipe() and SDK installation
remain separate; this tests public write/sigaction/sigprocmask in the private probe.

For a nonempty write to a live pipe writer that returns validated EPIPE, post13
once while the existing transaction mask is held. Restore the original mask,
then poll with signal0 (never repost). In this opt-in adapter, also poll after a
successful public mask change so deferred default termination occurs on unblock.
Preserve errno around handler delivery; publish sigprocmask output before explicit
poll. Failed mask restoration or signal primitive fails closed at exit125. Do not
signal EBADF, zero-length writes, reads, close, unknown replies or stdio errors.
Old profiles retain their existing poll/delivery behavior.

One authenticated parent and backend, no fork: create pipe, close its reader,
check zero-length success/invalid-fd rejection, ignored EPIPE, one handled EPIPE,
two blocked handled writes coalescing into one handler on unblock, and a blocked
signal discarded by installing ignore. Require original mask, handler count and
EPIPE despite handler errno changes. Finally default disposition must terminate
with actual kind4/detail13, either directly from write or on deferred unblock.
The owner requires exactly six EPIPE writes, one zero write, reader close, no
unexpected requests, then terminal and request EOF before holder retirement,
backend closes and reclaim. Three real lifetimes yield six reclaims.

Controls suppress posting (handled-write witness fails at parent94/owner2172) or
suppress explicit polls (deferred default returns incorrectly, parent94/owner2172).
Both require zero reclaims; boot failure or timeout is not a passing rejection.
Native handler delivery and supervisor forced-stop status translation stay distinct.

Scope: Aether's opt-in startup facade, C pipe probe, Rust owner and harness.
O-02–05, I-01/03–06, E-01–08 and local Coding/Testing/SE-01–05 apply. No allocation,
new service, channel/task quota, unsafe block or general signal refactor. Native
calls borrow owned stack buffers; handler uses volatile sig_atomic_t and bounded
native mask inspection. Actual musl sigaction/restorer comes from pinned libc.
The facade is single-context; arbitrary-pointer recovery and general EINTR/restart
semantics remain unqualified. Preserve legacy startup-header style; scoped new
C uses clang-format21.1.8, Rust1.98.0 edition2024/skip_children.

Simplicity: reuse the existing signal mechanism and mask boundaries rather than
create another signal service. Direct guarded branches keep old behavior intact;
no abstraction is needed for these few calls. No obsolete mechanism is removed
because old profiles remain regression coverage. Select focused direct/deferred
positives and two exact controls, full connections/launch/console, host/harness,
format/workflow and immutable pin checks. Freeze runtime sources during runs and
retain attempts. Update STATE/reference/roadmap with evidence and remaining gaps.
