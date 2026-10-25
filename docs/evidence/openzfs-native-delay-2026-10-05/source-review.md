# Delay source review

Only actual libzpool kernel.c object145 changes. The complete preceding wait-clock
packet manifest/archive is verified before selecting regular inputs; archive links
are never extracted. Original177/113 aggregates, checked baseline ELF and freshly
compiled original kernel.c are byte-identical. Actual delay compiles into the
selected engine under the same flags, header/SDK and __FILE__ mapping. The guarded
header and CV/tpool/queue changes remain untouched. New source remains CDDL-derived.

With the fixed inherited hz119,1000/hz is8. Negative ticks reject125; values above
INT_MAX/8 reject before multiplication or int conversion. Zero makes no poll call.
Remaining positive products lie1..INT_MAX, never wrapping to indefinite negative
poll timeouts. poll(NULL,0,timeout) accepts only zero; errors including EINTR and
unexpected descriptor-ready counts reject125. Without a truthful monotonic provider
there is no sound retry/remaining-duration calculation, so this port deliberately
aborts on interruption. That is availability loss, not completed delay/recovery.
The inherited8ms/tick approximation remains explicit and needs review when actual
native delay becomes enabled; it does not satisfy accurate119Hz or no-early-sleep
requirements. Extremely long representable waits are not recommended policy.

Tests compile the literal original/selected delay function with its upstream notice.
Host types explicitly match musl signed64 clock_t rather than Darwin unsigned ticks.
The poll model checks null/zero descriptors, positive in-range ticks and exact8ms
conversion, returning a distinct93 if invoked for forbidden bounds/zero. Arithmetic
bound/error cases must exit125; successful model cases report call count/timeout.
Actual old-source safe1tick controls ignore -1/EINTR and unexpected positive result,
returning0 and failing the selected125 oracle. No original overflow input is run.
These are branching tests, not a working poll backend or elapsed-time measurement.

Native probes link literal selected delay against actual unchanged musl poll, with
no poll/clock/wait stubs. A positive tick must deny125; zero continues through all
existing memory/TLS/yield/output/terminal witnesses. Negative/minimum/largest and
first narrowing overflow deny125. Whole engine and actual native timed blocking
remain unexecuted. Current large loader models/W+X/TLS, compiled queue counts and
honest discovery failure bind the final ELF; quota/heap/ARC fit remains unmeasured.

Scope respects accepted CLOCKS-TIMERS: calibrated monotonic first, required UTC
truthfully established, deadlines retained through retries and scheduler parking.
Per-core timer ownership, userland POSIX policy and capability-scoped UTC authority
remain unchanged. No service placement, universal timer API, quota raise or sibling
handoff is inferred. Release pins/normal image/kernel/musl remain fixed. Full137
host/pin/workflow/scoped checks and source freezing complete this private slice.
