# Shell mask ownership review

Before code, 2026-09-07: continue dash before OpenZFS. Actual musl block/restore
helpers use four-argument rt_sigprocmask, while the shell startup facade currently
stores a separate mask. Connect both to the existing native Execution.signal_mask.
This is prerequisite mask behavior, not custom handlers or asynchronous delivery.

Simplicity questions: the simpler alternative is to reuse the existing per-context
mask transition and checked eight-byte copy path. Choose that over another signal
service or synchronizing two tables: both operate on the same caller-owned state.
Remove startup_mask in production and share the native copy/transition helper with
0x28009. Keep the two caller protocols separate; do not refactor other dispatch.
Borrow only musl's actual four-argument mask contract, not a Linux authority model.

Enable 0x1000e only for existing runner-local connections. rdi=how, rsi=set,
rdx=old, r10=size(8). r8/r9 are not arguments: actual musl __syscall4 does not clear
them. Set-null query ignores how; otherwise 0/1/2 block/unblock/replace. Snapshot
input, validate the entire writable output before any mutation, preserve aliased
input/output, strip unmaskable bits 9/19, then publish old and new state under
existing owner IF=0. Invalid size/how yields EINVAL; invalid/overflow pointers
EFAULT with no state/output mutation. No process may address another context.
Existing 0x28009 grant/argument checks and non-runner ENOSYS remain unchanged.
No new slots, capabilities, buffers, allocations, dependencies or release pins.

The public facade remains admission-gated and zeroes sigset_t tail only on success.
Its existing NO_MASK control passes a null set to the kernel. Native raw masks are
available before facade admission for libc internal initialization; this accesses
only caller state and publishes no descriptor authority. Fresh context reset and
thread inheritance retain their existing lifetime rules. SDK files remain read-only.

Tests: real linked __block_all_sigs/__block_app_sigs/__restore_sigs plus bidirectional
raw/public observation, query/how, unmaskable bits, aliasing, invalid output and
overflow atomicity. Omitted internal block must fail exact terminal73/owner1501.
Run complete command-runner, default/large signal-mask and pthread-lifecycle suites,
M4 regression and host/pin/workflow checks on frozen sources; retain every attempt.
Use pinned Zig/C formatting. Update startup/NATIVE-C references and existing group.
Foundations O/I/E, approved local DEVELOPMENT and adopted SE-01–05 apply. Independent
consumer review and signal handler/return/IPC-reentrancy design remain open. No
claim that storing a handler or a mask alone runs dash; actual shell cases NOT RUN.

Follow-up source check: the pinned musl __libc_sigaction itself unblocks internal
signals through rt_sigprocmask before installing a custom handler, confirming this
shared mask path is a concrete dependency. Its next call is rt_sigaction with a
private k_sigaction layout and native __restore_rt trap. Those action/return
operations remain unsupported. Before implementing them, specify executable
handler/restorer validation, saved context/FP/mask ownership, pending delivery,
stack safety, nested delivery and IPC/descriptor reentrancy. Do not accept a
handler setter alone as actual shell initialization. Source copies are retained
for this next review; no handler ABI or default-action policy is selected here.

Additional boundary selection: run both existing pthread-preflight
profiles to prove raw mask calls remain ENOSYS outside runner-local connections.
This directly checks the new scope gate; it is not broad unrelated regression.
