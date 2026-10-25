# Before-change delay contract

R1-03: correct the actual selected OpenZFS2.4.4 libzpool delay caller before
allowing full engine entry. Inputs are only the verified preceding wait-clock
packet, its pinned source/SDK/tools and current unchanged native fixture.

Allowed: zero ticks is immediate with no provider call. Negative ticks and positive
values exceeding INT_MAX/(1000/hz) terminate the scoped owner125 before arithmetic
or polling. Otherwise retain the inherited integer8ms/tick at hz119 and accept only
poll(NULL,0,timeout)==0. Unsupported/error/interrupted or unexpected positive results
terminate125, with no retry that could extend a duration. This deliberately retains
upstream coarse conversion; it is not a calibrated119Hz sleep or proof of elapsed
waiting. Real monotonic deadlines, honest native delay and timed conditions remain
required before engine execution. Interrupted delays cannot return as completed.

Forbidden: signed overflow, narrowing into negative/indefinite poll timeout, silent
unsupported/interrupted success, fake clocks/waits, ambient time-adjustment rights,
new syscall/SDK/quota, sibling edits, altered release pins or engine startup claims.
Only actual object145 changes among289 ordered engine inputs. Prior selected ELF,
aggregates and fresh original object must reproduce bytes before replacement.

Aether owns this private C port and native denial fixture. Userland retains musl/
POSIX adapter ownership; sys-init supervision and pkg-mgr installation remain
separate. Existing _Exit125 is fatal owner teardown, not restart/recovery acceptance.
No new pointers, shared state, allocation or authority. Poll receives no descriptor
array; successful model outcomes establish caller branching only. The bound limits
conversion, not an operationally reasonable service timeout or scheduler latency.

Tests: literal original/selected delay slices, host signed64 native tick model,
zero/negative/extreme/conversion boundaries, poll timeout/denial/EINTR/unexpected
outcomes and actual old-source ignored-error controls. Fresh QEMU uses actual musl
poll for positive unsupported denial, zero no-call success and pre-provider bounds.
Preserve existing isolated memory/TLS/yield/output/terminal witnesses. Relink/inspect
actual queue selection/closure and current loader/W+X/TLS controls; run full137 host,
offline pin/workflow and scoped format/source checks. Bound subprocesses180s,QEMU30s.
Freeze sources/tools; retain every failed attempt; archive/readback before owned
cleanup. No unrelated kernel target suite is required for unchanged kernel bytes.

Documentation: STATE progress/next action, R1-03 acceptance and OPENZFS-FEASIBILITY
coverage; private recipes are evidence, not new maintained entry points. CDDL source
and patch provenance remain, original probes/tooling BSD-2-Clause. Apply Foundations
O-01/O-03/O-04,I-01/I-03/I-05,E-01–E-08 and simplicity SE-01–SE-05. Simpler direct
range/result checks suffice; a retry/deadline framework lacks a truthful provider
and adds complexity now. No subsystem or dependency is removed by this narrow fix.
