# Native self-upcall entry/return experiment

Preimplementation scope: connect the checked signal frame helpers to the current
single-context runner-local native profile. Aether owns CPU/memory enforcement;
userland still owns libc/shell acceptance. No pending signals/custom sigaction,
remote PID authority, thread delivery, sibling or released-pin change.

Private experimental self-upcall 0x29000 takes handler/restorer/signal/action-mask
in rdi/rsi/rdx/r10, with r8/r9 zero. It resumes the call with rax=0 after the actual
musl restorer issues 0x1000f; return reads its payload from RSP. Both are limited
to runner-local connections without native threads. Bad entry or return yields
EINVAL, other profiles ENOSYS. No other task is addressed. Malformed return must
not publish CPU state; the user must handle the error or fault normally.

Use the current exception's trusted FXSAVE MXCSR-mask field, with 0xffbf fallback
for zero. Validate/copy/publish while IF=0 under the local domain owner. Publish
only frame, FP and mask; FS/TLS, grants, mappings, waits and lifecycle stay owned.
The fixed loader stack is the entry bound. No dynamic allocation or active token.

Simplicity: reuse the existing runner-local profile and terminal/reclaim oracle.
The explicit synchronous experiment avoids unsafe asynchronous transport entry
before pending/disposition policy and reentrancy are ready. It is a temporary
mechanism to qualify entry/return; review removal when genuine signal dispatch
replaces it. Do not advertise POSIX signal support from this fixture.

Planned checks: actual musl restorer, handler mask, FP restoration, repeated entry
after longjmp, bad pointers/unsupported signal and invalid return; exact negative
client oracle. Full command-runner suite, host tests and M4 regressions; unchanged
thread profiles remain gated out. Preserve all attempts and freeze sources for
qualification. Native results remain pending until recorded below.

## Attempts and limits

The first formatter invocation rejected the reserved identifier `resume`; the
initial command build was interrupted and its entire directory/log retained. A
corrected build then timed out in the new frame case after the older startup
case passed. Disassembly showed principal Debug call-frame reservations of
25608 bytes against the existing 16384-byte stack. These are static reservations,
not measured high-water usage. Caller-owned output buffers and borrowed inputs
reduce those principal reservations to 9472 bytes; no quota was changed.
failed-sources/ reconstructs the two changed runtime inputs and matches their
original failed-run receipt hashes. Other failed-run artifacts are retained.
The initial malformed edit is represented by its log/receipt rather than a
complete standalone source closure; do not claim every attempt is reproducible.

The isolated diagnostic then passes the same real-restorer payload across two
generations. A mistaken `native_smoke.py --help` diagnostic treated --help as an
ISO and failed before boot; its separate logs are retained as infrastructure
misuse, not a semantic test. Final qualification reruns use frozen corrected
sources. The existing harness records source/artifact identity and exact oracles;
it does not add per-case timestamps or independent consumer acceptance.

Actual libc linkage is the pinned native-c-5olokhku SDK verified by the harness's
archive/receipt and tool-lock checks. Its retained SDK archive remains in the
[earlier capacity packet](../init-composed-capacity-2026-09-07/README.md). The linked
__restore_rt symbol executes mov15/add0x10000/int0x81, as retained ELF disassembly
shows. No sibling build output was written. No public custom sigaction is enabled.

The synchronous probe can return normally, or use actual musl longjmp to abandon
the frame and then enter again. It samples XMM15/mask restoration; it does not
qualify all GPR/FP/red-zone state in native execution. Host tests cover structural
CPU and mapping rejection. Native malicious flags/FP frames, mapping changes,
nesting, transport interruption and independent acceptance remain open.

Final profile results and complete retained artifacts are collected by collect.py
using the existing harness receipts. Runtime sources are archived separately;
all archive member digests are checked. Rebuilding requires the pinned tools/SDK
as described in the shell reference. No new developer entry point is added.

## Final result

All 229 command-runner cases and seven M4 target cases pass on matching frozen
sources (236 target cases). The positive frame probe completes two generations
and four reclaims; its deliberate handler-skip control produces exact terminal75
and owner1501. The full host command passes, including 98 Python tests; all eight
codec tests pass in ReleaseSafe. Format, workflow, local changed-section links
and simplicity snapshot checks pass. Previous three signal packets are unchanged.

This is producer evidence for synchronous entry/return only. It neither unblocks
the twelve complete dash scripts nor establishes general signal conformance.
STATE records the next native adversarial checks and subsequent pending delivery.
