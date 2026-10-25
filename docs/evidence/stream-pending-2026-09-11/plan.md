# Post-fork pending read qualification

Requirement: hold a nonempty blocking stdin request after a well-formed backend
EAGAIN while continuing the other process's requests. This is an opt-in private
process-owner experiment, before UART/dash integration. No public ABI changes.

The owner retains one validated 32-byte request per caller in its existing frame
buffer, retries at most once per caller per scheduling round, and never advances
shared positions or replies EOF on EAGAIN. No application pointer crosses into
owner storage. A terminal pending caller rejects this bounded success experiment;
general cancellation and indefinite waits remain unimplemented. The existing
100000-round watchdog and backend reply watchdog remain. Malformed/partial backend
replies are still failures, never retried as EAGAIN. Before-fork pending input is
explicitly rejected in this experiment rather than silently losing the request.

The witness parent blocks reading a; the exec replacement must write ! to stderr
before input becomes available. The backend refuses that write until it has
observed an empty read, so success requires serving the child while the parent
request is held. Child reads b, parent later reads c through FD10; shared closes,
CLOEXEC, copied mask and exact child72/parent71/backend17 remain required twice.
Controls forward EAGAIN, substitute EOF, or advance offset on EAGAIN and must
reject at parent85/owner2130 with zero reclaims.

Owners: Aether's private dispatcher/backend and C consumer witnesses. SDK,
userland, sys-init and package contracts/pins remain unchanged. Foundations O/I/E,
local TD/TE evidence and SE01–05 apply. The simpler synchronous receive would
prevent the child write that makes input available. Retaining existing frame
storage avoids a new queue, service, kernel wait API or general event framework.
No complexity removed now; UART adapter and true interactive startup stay next.

Tests: complete connections suite (new cases plus old fork/dash/descriptor
controls), launch suite (shared backend/build harness), host/pin/workflow checks,
Rust/C formatting and source freeze. No kernel or new FFI changes. Update canonical
shell reference, ROADMAP and STATE; preserve failed attempts and sealed sources.
