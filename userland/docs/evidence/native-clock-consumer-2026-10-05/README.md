# Independent elapsed-clock consumer and source-built adapter

UL-003/015/081,2026-10-05. Verify complete27-file producer manifest and26233-entry
archive; select attempt4's11 images, frozen startup/memory adapter and SDK.
Eleven fresh final binary replays pass real q35 elapsed200/400ms parks (qemu64,
max,two repeats), child wake/pins, original-deadline requeue/pins, disabled grants,
user MMIO fault, missing HPET, virtual substitution and early completion controls.
214 older producer regressions are retained source-bound evidence, not new runs.

New [C17 adapter/probe](../../../experiments/native-clock/README.md) builds against
that frozen musl SDK and startup. Three additional final native cases pass:
absolute sleep, disabled clock and actual early-completion kernel. All actual ISO
modules are read back; only native-c.bin and generated boot catalog may differ
from each selected baseline. Each actual native envelope binds its independently
built ELF; no kernel/default SDK/ABI/kit/sibling changes.

The adapter takes an explicit thread grant, returns signed monotonic nanoseconds
or negative native errors, and parks on the unchanged absolute deadline. Sleep
uses its own stack word; timeout plus fresh observe at/after the original deadline
is required for success. Unsupported calls fail. Unexpected wake and early timeout
are EIO; errno remains unchanged. RDX elapsed is intentionally not exposed because
immediate errors (including expired timeout) do not certify it. The kernel's
one-second future limit remains; no relative rearm/fallback/busy sleep is added.

The independent probe exercises real200/400ms sleeps, foreign/disabled grants,
mismatch/expired/alignment/span/signed/future bounds and errno. The early-completion
kernel produces real registrations without expiry; adapter EIO is required.
Injected host return controls under optimized Clang/UBSan cover known/unknown
errors, successful reads, unexpected wake, early timeout, exact expiry and errno.
Those injected controls are host evidence, separate from native execution.

Independent oracles require exact two-domain terminals/output, complete final
panic/fault identity, four real sleep registrations/expiries, preserved clock
arithmetic, actual idle, and requeue's original start/deadline. Current3.14.7 and
minimum3.10.21 each reject81 semantic corruptions. Fourteen final VM cases pass
with explicit interpreter, driver and oracle binding and complete owned cleanup.
Earlier14 passing cases are retained separately before final receipt strengthening;
no native product failure or source retry occurred. See harness-review.json and
[before-code scope/source assessment](source-review.md).

Reported10ns q35 period is not certified effective resolution, physical accuracy,
wake latency, UTC or full engine clocks. Expanded service-workers are excluded by
this kernel profile. POSIX/musl timed conditions require atomic mutex release/
reacquisition, unchanged deadlines and honest interruption before adoption.
General sleep/signals/cancellation, realtime/UTC, dynamic workers/resources,
engine lifecycle and wider SESSION remain open; independent reader remains pending.

Offline reproduction from a fresh owned root uses prepare.py, build.py, host.py,
run-final.py, then check.py current/minimum in that order. Copy reviewed scripts
into a fresh packet directory before execution; never overwrite sealed records.
Build commands, exact Clang21.1.8/LLD/headers/libc/source hashes are in build.json;
producer/tool/firmware closure in inputs.json. Fresh QEMU11.1.1 q35-11.1/TCG,
qemu64 or max,one CPU/256MiB/no NIC/disposable firmware variables, HPET disabled
only in the missing-source case;35s guest/45s owned group,1MiB UART/4MiB stderr/
16MiB owner files. Forced teardown fails; preflight finishes before native groups.
Quality, C formatting, minimum/current syntax, whitespace and local adoption
checks pass. BSD-2 original code; musl/firmware upstream terms preserved. Archive
readback precedes only owned duplicate cleanup; exact retention.json identifies it.
