
## Native per-context signal-mask state contract — 2026-09-06

Before implementation: add bounded signal-mask storage to each native execution
context as a prerequisite for libc creation. This is not signal delivery, pending
signals, handlers, cancellation, or POSIX compatibility. The existing Linux-numbered
rt_sigprocmask call stays ENOSYS and pthread preflight remains fail-closed. No
shared standard, sibling API or consumer adoption changes. Kernel owns storage;
userland will own the future libc adaptation.

In native-threads only, operation 0x28009 takes RDI=current domain thread grant,
RSI=how (0 block, 1 unblock, 2 replace), RDX=optional input pointer, R10=optional
old-mask output pointer; R8/R9 must be zero. Each mask is exactly eight little-endian
bytes, unaligned and overlapping pointers allowed. A null input queries only and
ignores how; null output discards the old mask. Validate grant first (-13), unused
registers/invalid mutating how next (-22), and every input/output byte next (-14).
Copy input and validate complete output before writing either mask or output,
under existing IF=0 owner execution. On failure neither changes. No retained user
pointers, allocations or backing pins. Output is the mask before mutation. Bits
8 and 18 (signals 9 and 19) are always cleared; other 62 bits are retained.

New domain masks are zero. Successful child admission copies the parent's mask
after validation, for all three creation forms. Thereafter only the calling
context changes; peers and parent are unaffected. Failed admission changes neither
mask. Stop/reclaim clears state with Execution.reset; masks do not block lifecycle
stop or synchronous fault containment. No signal-send interface is enabled here.
The state describes future delivery eligibility; this experiment cannot establish
that masked asynchronous signals are deferred until a delivery mechanism exists.

Verify host mask transitions, unsupported operations, unmaskable bits, reset and
context independence; run a target --signal-mask selection in both memory profiles
covering zero initial/replacement state, inheritance, per-thread/per-domain
isolation across yields, block/unblock/replace/query, same/partial aliasing, invalid
grant/arguments/pointers, output atomicity at a protection boundary, all mask bits,
stop/fault and existing pins. A skip-inheritance kernel mutant must reject at exact
assertion 220. Retain disabled-thread rejection and unchanged pthread preflight.
Run all older thread suites, memory/image profiles and M4 regression plus required
host/format/standards checks on frozen sources. Record all attempts. Existing
Clang21 C formatting and Zig formatting apply; no unrelated migration.
