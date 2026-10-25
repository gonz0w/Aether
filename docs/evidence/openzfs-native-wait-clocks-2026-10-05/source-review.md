# Wait-clock source review

Inputs come only from the completely verified previous time-caller packet, pinned
OpenZFS2.4.4 commit71a9f9578616a90c3c14bb59629fb4d31bfd68d1 and guarded musl SDK.
No original archive link is extracted or followed. The177-object libzpool and113-
input support aggregate reconstruct the prior checked ELF byte-identically, then
only input145(generated kernel.c) and187(original thread_pool.c) are replaced.
Fresh original bytes match; every other object, checked header, queue selection,
compiler resource header, SDK/bootstrap/provider and diagnostic input stays fixed.
Generated kernel.c already omitted unavailable platform includes in prior work;
this patch only corrects its two timed-CV bodies and a private local addition helper.

cv_timedwait reads the existing lbolt view, validates its nonnegative domain and
compares expiry before signed subtraction. Positive differences are representable
because both absolute and current values are nonnegative signed64. Hires relative
nonpositive durations retain expiry; absolute values compare against checked
gethrtime before subtraction. Flag assertion and ignored resolution semantics remain.
The existing119 tick conversion and its inherited quantization remain; no calibrated
frequency/wakeup accuracy is inferred. A static cv_deadline helper serves just these
two callers, reads checked gethrestime and validates carry/seconds addition before
publishing the timespec or clearing mutex ownership. Original microsecond wall
truncation remains. Overflow/failed/malformed providers terminate125; they are not
expired deadlines. Wait timeout/error handling and owner restoration remain literal.

Tpool retains nanosecond realtime precision, validates provider status, nonnegative
seconds, nanoseconds [0,1e9) and unsigned32 linger addition before use. It never reads
clock output after failure. Worker loops/queues/cleanup/indefinite branch are otherwise
unchanged. This is an actual tpool clock-block correction, not qualification of all
pool lifecycle/worker scheduling or native pthread conditions. No new clock service,
retry policy, shared state or generic deadline framework is added.

Component tests slice exact audited CV functions/helper and the tpool block from
actual final source, retaining CDDL attribution. Minimal test types contain only
fields those bodies use. Host waits are controlled models, not real condition waits;
ETIMEDOUT60/EINVAL22 are Darwin values, while actual native errno constants remain
musl-owned. Test VERIFY0/ASSERT fatal126/127 are test adapters, not new native exits.
Native tests use actual SDK types/clock functions and test-only fixed lbolt5. They
qualify three real unavailable-clock125 denials and three no-clock expired outcomes,
with existing isolated-context memory/TLS/yield/output/terminal witnesses. Wait
stubs are unreachable in those selected native cases; none is linked into the engine.
Actual old-source poisoned-failure controls return/submit a deadline and reject the
required125 oracle. Their overflowing cases are intentionally not executed.

Build attempt1 loses a local quoted header when moving the tpool source; attempt2
adds -iquote for that exact original local directory, preserving angle-header/SDK
search. Host1 exposes Darwin unsigned clock_t after24 passing cases; host2 explicitly
models/asserts native signed64 ticks and passes53; host3 reruns after the final probe
change. Native1 passes two denials then -Werror catches an unused test CV in tpool;
native2 explicitly marks that unused test variable and all six cases pass. Every
attempt/source/log remains; original narrower outcomes are not promoted.

Full engine entry remains unavailable. In particular inherited delay(clock_t ticks)
in kernel.c still discards poll(0,0,ticks*(1000/hz)) outcomes; duration arithmetic and
honest blocking/delay/condition-wait semantics need qualified adaptation with real
clocks. Three corrected reads are not a whole-engine timing/security audit. Actual
provider availability, deadline progress under interruption, production helper
counts/native heap/ARC/TLS and feature closure remain before startup/fini/restart.
No native quota/ABI/SDK, owner acceptance, release pin or companion repository changes.

The first final-check recipe shadows its output-folder Path with an attempt-name
string and fails before formatter/host commands; its finally block also cannot
write a receipt. The raw traceback and exact recipe are retained with a separately
labeled infrastructure receipt. The corrected loop variable changes no native,
engine or test inputs; fresh final scoped/host checks are required before sealing.
