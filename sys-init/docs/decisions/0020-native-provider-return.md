# 0020 — Provider-originated normal return after admission

Accepted 2026-09-05 for the next bounded BG-032/BG-040 witness. This follows
[decision 0019](0019-native-service-dependency.md) without changing ABI 6.

Build one sys-init-owned strict-musl worker from explicitly pinned SDK, tool and
source inputs. It writes the fixture readiness byte 42, marks itself ready, then
keeps attempting bounded one-byte writes while yielding. After the dependent is
actually launched, the supervisor closes the provider's reader. The next worker
write observes native EPIPE and the worker returns 17 from `main`. This produces
normal terminal detail 18 without a supervisor stop request.

Reader closure is a deterministic test stimulus, not production health checking,
arbitrary revocation or a graceful shutdown protocol. The result demonstrates a
worker-originated normal return in the required ordering. It does not demonstrate
an unprompted crash, CPU exception, signal delivery or external service failure.

Admission retains decision 0019's worker/channel/generation binding, byte check,
liveness observation and strict interrupt-tick deadline. Before launching the
dependent, verify that the provider remains live; an early reader closure must
reject at assertion 912 with no reclamation. After dependent launch, register a
lifecycle wait, close the reader, require a changed event and terminal detail 18,
then release the wait. Retained readiness must no longer admit the provider.

Dependency invalidation requires explicit stop and terminal detail 144 for the
dependent before closing and reclaiming it. Omitting that stop must reject at
assertion 915 with no reclamation. After both resources are cleaned, launch a
fresh provider generation, reject the old evidence, accept its own frame, trigger
its normal return and reclaim it. Completion requires three reclaims, empty
adapter accounting and the established INIT PASS marker.

The build tool must verify its SDK receipt, libc archive and tool lock before
compilation; copy all inputs to a private directory, reject unsafe ELF structure,
undefined symbols and relocations, and prove captured inputs unchanged. The
consumer separately pins and verifies the worker receipt, worker bytes and every
listed build input before constructing only the new cases with that ELF. Existing
cases continue to use the producer's original helper and must remain byte-identical.

Acceptance comprises the positive normal-return path, early-trigger control,
omitted-dependent-stop control, all fourteen prior target cases, receipt mutation
tests, full offline checks and retained artifact/source correspondence. A timeout,
build error or unrelated panic cannot satisfy any semantic result.

The worker protocol and lifecycle policy remain local sys-init fixtures under
Foundations O-01–05, I-01/03–06 and E-01–08. No shared standard or Distribution
service descriptor is changed. A worker-originated exception/fault after dependent
admission remains a distinct future witness requiring an explicitly bounded
stimulus and evidence; this decision does not claim it.

## Result

[Seventeen target cases](../evidence/native-provider-return-2026-09-05/README.md)
pass. The positive and two new controls have the required exact outcomes; all
fourteen prior supervisor binaries remain byte-identical. The positive client is
2,960 bytes within the unchanged page bound. Full development checks pass with
32 harness tests and the 80-outcome offline audit. The accepted scope and future
exception distinction remain as specified above.
