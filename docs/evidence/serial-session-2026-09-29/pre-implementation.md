# Serial SESSION integration — in progress

Requirement before code: consume pinned SESSION-SERIAL unchanged commands in three
interactive dash parents, with prompt-driven partial input writes, exact UART and
separate stream/lifecycle observations, owner-only serial authority, stale denial
and confirmed idle-parent cancellation. Preserve15 lifetimes, three children/two
pipes,24KiB owner and4088 stack. No sibling or released standards edits.

Use explicit private AENMX008/ABI23 to compose007 session lifetimes/observations
with006 owner UART authority. Existing envelopes and ABIs remain unchanged. The
smallest sufficient change reuses the session owner/client and kernel console
primitive; silently granting UART to007 would violate compatibility. No new service,
public SDK operation, kernel policy, scratch namespace or generic TTY is added.
The owner forwards accepted bytes only after binding/rights/identity validation;
EAGAIN keeps the current request pending. All wire buffers remain synchronously
borrowed at existing unsafe traps. No arbitrary payload gains UART authority.

Host framing recognizes only exact existing kernel record grammars after the boot
boundary; every other byte belongs to UART and must match the consumer stream.
No arbitrary-line filtering, sleep handshake, future-command preload, fabricated
prompt/EOF, or timeout-as-cancellation is allowed. Match phase terminals and native
owner collection invariants at each new stdin request. Retain raw byte offsets,
prompt/generation/input events and all attempts. Upstream prompt bytes and machine
markers remain unchanged (Experience v0.1.0 existing-output exception applies).

Select bounded parser/order counterexamples, malformed envelope/legacy tests,
native authority/negative/cancellation controls, full affected capacity plus legacy
commands, host checks and linked owner code/stack inspection. Update existing
STATE/ROADMAP/interfaces/workflow with actual results and remaining owner gates.
General TTY/job control, arbitrary transport interruption, SDK and R1 remain open.
