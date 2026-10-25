# Private elapsed-clock consumer and adapter — UL-003/015/081

Before code: freeze complete native-clock producer packet/archive and select
attempt4's11 images, exact original memory driver/adapter and SDK. Replay all11
with independent authority, final terminal/fault/panic, real deadline and cleanup
oracles. Build an independently authored explicit-grant C adapter/probe against
that frozen SDK, replace only native-c.bin in positive/disabled/early-completion
ISOs, read back every module and require all other modules except generated boot
catalog exact. No kernel, public musl/POSIX API, default SDK or sibling change.

Requirements: read monotonic signed64 nanoseconds with explicit thread grant;
compare/park on caller-owned aligned32-bit word with unchanged absolute deadline;
absolute sleep through a private stack word, complete only after timeout and a
fresh nonnegative reading at/after the original deadline. Unexpected successful
wake returns EIO, never early sleep success. Do not expose RDX elapsed because
immediate errors, including expired timeout, do not certify its contents. Known
native errors remain negative; unknown returns become EIO; errno is untouched.
Deadline validation stays kernel-owned (one-second future maximum). No retries,
relative timeout extension, fake UTC, busy sleep or success on unsupported calls.

O/I/E, TD/TC/TE, C/CP and SE apply. Stack word remains alive until synchronous
completion; native wait pins protect it. Held thread grant confers authority,
not package metadata/clock IDs. Source failure must reject. User MMIO fault,
missing source, virtual substitution and early completion controls require exact
semantic outcomes. Native sleep probe covers200/400ms original deadlines,
expired/mismatch/alignment/span/signed range/future bounds, foreign/disabled grants
and errno. Selected early kernel completion must be EIO rather than successful
sleep. No cancellation/signal/atomic mutex/POSIX conformance inferred.

Python3.10+, C17/Clang21.1.8, fixed environment, pinned QEMU11.1.1/firmware.
Preflight before VM owners;35s guest/45s outer,1MiB UART/4MiB stderr/16MiB owned
files; forced teardown fails. All raw attempts, source/tool/SDK/image hashes and
upstream notices retained. Check meaningful trace corruptions on actual current/
minimum Python, C formatting, syntax, quality and whitespace before completion.
No effective syscall resolution, physical accuracy, realtime or engine cost claim.

Simplicity: direct explicit-grant operations satisfy this private integration;
full libc interposition would imply unsupported semantics. Reuse existing process
ownership and frozen memory startup, remove no active path. Actual musl timed
conditions (atomic mutex release/reacquisition, unchanged deadlines, honest
interruption), sleep/POSIX policy, UTC and expanded worker clocks remain follow-ons.
Agent technical assessment is not independent human review/release approval.

Actual source assessment: trap registers include zero reserved fields and memory/
condition-code clobbers. No uninitialized RDX is read or exported. Sleep keeps its
word alive, preserves the absolute input, rejects wake0 and follows timeout with
checked observe. Source/grant/argument errors remain honest; unknown results are
EIO. Native fixed/disabled/early cases and optimized host injected UBSan controls
exercise this behavior. Frozen SDK/startup/module closure is independently read
back; it is not a complete libc/source/engine qualification. Minimum interpreter
runs the oracle/syntax selection; actual compiler execution is current Python.
