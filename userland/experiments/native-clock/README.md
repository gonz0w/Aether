# Private native elapsed clock

C17 explicit-thread-grant adapter for the opt-in BSP q35 native-clock profile.
This is a userland experiment, separate from musl clock_gettime/nanosleep and
from the bounded shell SESSION ABI. Aether owns the actual grant validation,
HPET source, signed64 nanosecond range and compare/register/park operation.

- `aether_clock_observe(grant)` returns monotonic elapsed nanoseconds or a
  negative native error.
- `aether_clock_park(grant, word, expected, deadline_ns)` atomically compares and
  parks until matching wake (`0`) or absolute timeout (`-ETIMEDOUT`). The word
  must remain alive and writable through completion. Native mapping pins apply.
- `aether_clock_sleep_until(grant, deadline_ns)` uses a private stack word and
  completes only after native timeout plus a fresh read at/after the original
  deadline. Unexpected wake returns `-EIO`; it never silently extends a deadline.

The kernel admits at most one second in the future; expired deadlines are
immediate. Native errors remain negative, unknown results become `-EIO`, and
errno is unchanged. The adapter intentionally does not expose RDX elapsed:
immediate errors, including expired timeout, do not certify that register.
There is no fallback, polling sleep, retry, mutable timer or ambient authority.

[Independent qualification](../../docs/evidence/native-clock-consumer-2026-10-05/README.md)
records the exact source/SDK/tools/kernel/firmware, actual200/400ms scheduler
parks, authority/disabled/error controls and early-completion rejection.
The q35 reported period is not physical accuracy, effective syscall resolution
or latency certification. UTC, general hardware/multicore, cancellation/signals,
POSIX sleep and timed conditions remain unsupported here. Actual musl timed
conditions need atomic mutex release/reacquisition and original-deadline handling
before adoption. Production SDK/default pins and lab kit are unchanged.

Producer retention changed after this intake: Aether has disposed of historical
bulk archives and retired their old replay commands. This consumer froze the
complete source packet before that cleanup; its local retention.json/archive
index still identifies the exact captured inputs and attempts. The dated
prepare.py expects the historical producer location and must not be presented
as a current sibling entry point. Future qualification should consume Aether's
verified `.deps/native-current/current-inputs.json` set in a fresh owned scope;
archived consumer results remain evidence for their exact tested bytes only.
