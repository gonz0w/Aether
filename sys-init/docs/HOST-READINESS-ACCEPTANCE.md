# Host readiness acceptance review

Reviewed 2026-09-05 for BG-040/BG-054. [Decision 0013](decisions/0013-host-readiness-acceptance.md)
retains decision 0003's trusted, six-byte `READY\n` first-frame contract and adds
four real-child test families. No runtime/model or wire-format change was needed.
The [new evidence](evidence/host-readiness-ordering-2026-09-05/README.md) records 42 passing
host tests and an exact-deadline mutation rejection.

## Framing criterion disposition

BG-040 originally requested implementing/comparing newline and bounded versioned
frames. [Decision 0003](decisions/0003-host-readiness-fixture.md) already compares
the design choices: the existing fixed frame has a bounded parser and scoped
channel; a larger payload adds no current consumer requirement. For this bounded
fixture, decision 0013 replaces the two-implementation exercise with preserving
and testing the existing contract. No executed versioned-parser comparison or
production protocol selection is claimed. Reopen the decision if actual metadata,
compatibility or authentication requirements justify another frame.

A valid first frame followed by extra bytes is accepted once; trailing bytes are
not part of the frame. This deliberately differs from rejecting an entire write
because it is larger than six bytes. Read-call coalescing cannot determine
acceptance. Invalid prefixes and incomplete EOF reject. Channel possession allows
an explicitly inheriting helper to notify; it is not sender-PID authentication.

## Acceptance matrix

Source requirements: [readiness research matrix](research/READINESS-AND-HEALTH.md).
Test names below are in tests/test_host_runtime.py unless another file is named.
“Covered” always means the trusted macOS fixture, not all POSIX implementations.

| Requirement | Evidence/disposition | Remaining limit |
| --- | --- | --- |
| Delayed initialization blocks consumer | ready dependency, startup timeout; new deadline tests inspect unlaunched consumer | No external availability probe |
| Notification before registration | `test_notification_before_launch_registration_is_preserved` in new ordering tests writes before Popen returns to adapter | Controlled setup cut; no concurrent adapter threads |
| Incomplete EOF | `test_partial_frame_eof_is_not_readiness` | Decision 0015 distinguishes closed, incomplete and malformed observations |
| Fragmented/malformed/oversized input | single-byte reads, wrong partial prefix, partial EOF, coalesced trailing data tests | Decision 0014 adds bounded nonblocking junk pressure; not unbounded stress |
| Duplicate valid frame | First-frame reader closes after acceptance; trailing-data regression | Decision 0014 verifies second write gets EPIPE without relaunch |
| Helper inherits writer | `test_explicitly_inherited_writer_allows_helper_readiness` in wait-ownership tests | Decision 0014 verifies buffered late helper write is discarded after known main exit; orphan reaping unobserved |
| Known terminal plus buffered readiness | `test_known_exit_discards_buffered_ready` | Exit after observation cut remains a later observation |
| Before/at/after deadline | New `test_ready_before_at_and_after_deadline`: -1/0/+1 ms cuts, real buffered pipe | Injected adapter clock, not a timing/performance result |
| Stop before notification | New `test_notification_after_stop_cannot_admit_consumer` | Model admission closes; transport reader may remain until observation/reclaim |
| Old writer/event during replacement | New `test_old_writer_and_event_cannot_ready_replacement`: old real writer gets EPIPE; injected generation-one event ignored | FD/PID reuse is not forced; injected event is separate from transport |
| Stale external probe, activation listener | Outside this transport | BG-041/BG-042/BG-049 |
| One-shot evidence and config revision | Model owns completion; transport does not implement graph revision | BG-042 and descriptor/configuration work |
| Hung/flooding/outliving health probe | No health probe implementation claimed | BG-041 |
| Health hysteresis/dependent failure | Separate policy, not readiness history | BG-041/BG-042 |
| Monotonic time and overdue observation | Runtime uses monotonic; idle-budget/request-sync regressions and new boundary cuts | No suspend/resume or wall-clock-jump experiment |

The four new methods live in [test_host_readiness_ordering.py](../tests/test_host_readiness_ordering.py).
Handshakes establish writes before assertions; bounded polling only waits for
those explicit markers. Test-owned direct children are killed/reaped during
cleanup. The old-writer test duplicates a real launch pipe writer in the test
process, retaining it across replacement; it does not create an unowned helper.

## Negative control and ownership

An isolated model mutation changes both deadline predicates so an exact-boundary
notification can be accepted. Only the offset-zero subcase fails (`True != False`);
no other failures or errors occur. Production model bytes are unchanged. This
establishes that the new boundary test detects the targeted policy error, not
native timing or global correctness.

BG-040 is now tracked as active because implementation work is underway, but
remains partial. Decision 0014 now covers repeated writes, bounded junk pressure and joint
main-exit/late-helper behavior with explicit cleanup and observation limits. Cross-host
execution and production channel/delegation requirements remain open. General
native clocks, waits and supervisor recovery still require the contracts listed
in [native coverage](NATIVE-COVERAGE.md). Future shared standards belong in
Aether-standards; this exact fixture acceptance stays local.

## Writer follow-through

[Decision 0014](decisions/0014-host-readiness-writers.md) and
[retained evidence](evidence/host-readiness-writers-2026-09-05/README.md) add three
host methods. A second notification gets EPIPE after first-frame acceptance.
Bounded nonblocking junk pressure is rejected after one six-byte read, while its
SIGTERM-ignoring writer observes EPIPE. A real forked helper writes after the main
has exited but before the adapter observes that exit; the buffered frame is
discarded, no consumer launches, and the helper's next write gets EPIPE.

The direct main is reaped. The orphan helper closes its writer on a cooperative
release path and has an independent ten-second self-watchdog. Its exit-path
receipt is not proof of external reaping or crash containment. An isolated
mutation which consumes readiness despite known terminal state fails only the
late-helper test. Runtime/model bytes and wire format are unchanged. Full checks
now pass 45 host tests. Decision 0015 now distinguishes EOF/incomplete frames from malformed prefixes;
BSD/illumos and production acceptance remain open.

## Current acceptance boundary

[Decisions 0015](decisions/0015-host-readiness-diagnostics.md) and
[0016](decisions/0016-linux-host-validation.md) add bounded failure diagnostics and
actual Linux execution. All 48 host tests pass on macOS and Linux with identical
recorded source hashes. Earlier macOS-only qualifications are historical for
those tests; Linux here means the exact retained container environment, not all
Linux hosts. [Required external inputs](INTEGRATION-GATES.md) now gate further
readiness/supervision integration: BSD/illumos environments, hosted CI selection,
and native waits/deadlines, delegation and recovery contracts. This is a bounded
host acceptance checkpoint, not completion of all BG-040 production requirements.
