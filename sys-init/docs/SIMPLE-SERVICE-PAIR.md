# Direct two-service startup and shutdown

BG-065 composes [two service owners](../prototypes/native-supervisor/service_owner.rs)
in [service_pair.rs](../prototypes/native-supervisor/service_pair.rs). This is a
reusable fixed-order component, not yet a useful boot environment or operator CLI.
The simpler-alternative review is in the owning backlog story; SE-01–05 is applied
to this actual change without another review system or journal dependency.

## Behavior

Each owner now has a fixed slot selector passed to its backend on launch. The
selector is configuration, not authority; the backend still validates actual image,
slot and grant constraints. `Service::new(identity, slot, attempts)` makes that
selection explicit. Existing callers use slot 0; the pair uses provider 0 and
dependent 1. The existing activation-wide attempt budget and generation checks
remain; successful cleanup does not reset either counter.

`request_stop` requires an exact owner/generation key. A successful stop request
enters Stopping, and subsequent requests do not repeat the native stop. The owner
retains its worker/reader until a separate terminal observation permits cleanup.
Known failure keeps the prior state and error for explicit retry; Unknown freezes
the owner and blocks replay. A previously observed terminal worker needs cleanup,
not a new stop request. Stale and foreign keys cannot issue stop calls.

The pair starts the provider first. Dependent admission checks that the current
provider is still Live and observed nonterminal. This is a **started dependency**,
not readiness, and is not atomic with a subsequent provider death. An admitted
dependent is not automatically stopped by provider loss in this component.

Explicit provider replacement is allowed only while the dependent is Idle. It
requests stop when necessary, waits for actual termination, cleans the exact old
instance, then starts a fresh generation within budget. Busy observations return
control to the caller; they do not create another command or history record.

Shutdown closes all new admission before touching resources. It requests dependent
stop, observes termination and completes dependent cleanup before requesting provider
stop. A delayed terminal event or a known failure returns control; a retry continues
from retained state. Unknown dependent cleanup blocks progress and leaves the provider
untouched. No provider cleanup is inferred from dependent completion. Repeating a
completed shutdown performs no operations. The caller retains blocked records and
owns the polling/deadline policy; this component does not implement recovery.

## Validation

Eight owner tests include exact stop keys, stop failure and acknowledgment versus
termination. Five pair tests compare explicit expected call order, replacement,
provider loss before admission, delayed termination, stop-error retry and partial
cleanup. Three owner guard-removal controls and two pair controls (omitted provider
admission check and reversed shutdown order) fail their designated tests. The
required Rust gate has twelve test methods and thirteen named result records;
these are counts at different levels, not inconsistent receipts.

Seven fresh pinned Aether cases pass: three earlier owner regressions and four
new pair cases. The native fixture checks actual terminal kind/result and adapter
cleanup; all use the existing service worker and ordinary compiler profile.

| Pair case | Native outcome |
| --- | --- |
| simple-pair | Start provider, explicitly replace it after stop/cleanup, start dependent, reverse shutdown; 100/reclaimed3 |
| pair-provider-loss | First provider actually exits with result18/kind1; dependent admission denies; clean replacement, dependent and reverse shutdown; 100/reclaimed3 |
| pair-stop-error | After replacement and dependent start, inject a labelled pre-call Known stop error; both remain Live, provider untouched and admission closed; 1132/reclaimed1, expected profile rejection |
| pair-cleanup-error | After dependent stop, fixture externally closes its reader before the owner's close; actual operation0x24003/errno13 produces Unknown; provider remains live, replay denies; 1133/reclaimed1, expected profile rejection |

The synthetic stop error proves policy handling, not native errno provenance. The
actual stale-close failure deliberately creates an ownership mismatch; it proves
denial/retention, not recovery or successful cleanup. Positive runs use three real
policy-owned instances; no unrelated third worker is substituted for shutdown.

New images are 4,456/4,584/4,520/4,552 bytes respectively, within the unchanged
16 KiB code and 4 KiB stack profile. They execute without a guest fault. This is
neither stack high-water measurement nor a performance claim. The three earlier
owner images are freshly executed at 2,304/2,464/2,544 bytes. Compatibility results
and exact source/tool pins are recorded in the linked evidence. The first full
check attempt passed its ten gates but rejected new evidence-file membership
added during the run; no preexisting source bytes changed. That attempt is retained
and final validation runs after packaging.

## Review and remaining work

The coordinator adds two owner fields and a closing flag; the owner adds slot
selection and a stop-requested phase. Responsibility, direct control flow, errors
and ordering are visible in these two modules. Backend calls retain native ownership;
known-error classification still requires a no-effect guarantee. No allocation,
unsafe site, syscall, released pin, shared format or dependency is introduced.
The implementation borrows the existing direct service/adapter ideas; the generic
journal, checkpoint storage and recovery framework remain experimental and shelved.
Existing fixture paths are preserved for compatibility rather than deleted blindly.
Independent review and implementation-wide simplicity/conformance are not claimed.

Foundations O-01/03/04, I-01/03–06 and E-01/04–08 apply. The locally pinned SE-01–05
extension shapes this scoped review; it remains unreleased. Existing Experience
internal markers and Distribution limits remain unchanged. Native stop is not a
POSIX graceful signal, and test completion is not poweroff or durable shutdown.

Next BG-066 checks the actual image/startup and long-running boot contract needed
to connect this component to useful userland services. Configuration transport,
operator shutdown input and the profile's wait/watchdog limits remain explicit
integration work. Broader history and recovery stay shelved.

[Retained evidence](evidence/simple-service-pair-2026-09-07/README.md).
