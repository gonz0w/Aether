# Runtime helper liveness witness — 2026-10-06

UL-003/015/081. Aether has independently consumed the exact314-member UTC-v2
handoff and executed selected checked engine timestamp/SPA/taskq cases.
[Intake](intake.json) binds that producer result and preserves its unexplained
first leap timeout. This removes the missing UTC-delivery dependency; it does
not resolve the engine liveness gate or accept persistence.

The new [focused helper probe](../../../experiments/native-service-runtime/liveness.c)
is independently compiled against the unchanged sealed UTC archive. Each ordinary
large owner runs eight waves of eight joinable helpers, reverse collection and32
detached create/reap cycles; the small owner uses one helper per wave and the same
32 detached cycles. Actual monotonic conditions retain their original10ms deadlines
and reacquire the mutex. Helpers read the shared UTC estimate and perform TLS/TSD
cleanup. Exact97/41 cumulative admissions include the charged reaper; final live0
and UTC close before runtime finish are checked in the executed source.

| Final case | Result | Evidence |
| --- | --- | --- |
| Normal date | Three completed ordinary owners and exact reclaims | [receipt](normal.json), [UART](normal-serial.log) |
| Leap date | Same complete helper schedule | [receipt](leap.json), [UART](leap-serial.log) |
| Repeated leap | Fresh VM repeats the leap schedule | [receipt](repeat.json), [UART](repeat-serial.log) |
| Stop/replacement | Initial owner stops after first cohort admission; confirmed144/kind3, peer and fresh replacement complete, reclaimed3 | [receipt](stop.json), [UART](stop-serial.log) |
| Disabled RTC | Establishment ENOSYS, terminal856, supervisor401/reclaimed0 | [receipt](disabled.json), [UART](disabled-serial.log) |

Five final native cases pass, with emulator reap/owned group cleanup and actual
ISO kernel/envelope readback. The stopped initial owner has no ordinary terminal;
its exact compiled supervisor checks native144/kind3 before reclaim. No claim is
made that every admitted helper remained parked at the stop instant. Positive
ordinary terminals and success/reclaim markers are exact; negative primary must
print856, any peer must match, and no success marker is allowed.

[Inputs](inputs.json), [source bindings](qualified-inputs.json), immutable sealed
runtime and [producer receipt](producer.json) pin the boundary. QEMU11.1.1 q35/TCG,
one CPU/256MiB/no NIC/disposable firmware; explicit normal/leap UTC dates and fixed
developer seed. Native35-second/owner45-second deadlines, UART1MiB/stderr4MiB,
tool120-second bounds. Tool groups finish before VM ownership; forced-kill cleanup
cannot pass. Nanosecond fields do not certify clock accuracy.

[Python3.10.21](host-10.json) and [Python3.14.7](host-14.json) each reject63 semantic
trace corruptions. [Checks](checks.json) record syntax, strict C format, local
quality/standards and whitespace. [Retention](retention.json) keeps every command,
stream, source and failure identity before generated output disposal. No whole-run
archive or default/sibling/SDK change. First attempt normal/leap passed, then the
disabled test failed strict compilation on unused positive-only helpers; source
and receipts remain in attempt-1. The corrected guard passed a fresh full suite.

This is a selected runtime schedule witness, **not an OpenZFS engine reproduction
or a fix for its timeout**. Runtime/provider behavior and sealed deliveries are
unchanged. Aether still owns bounded phase telemetry/native scheduling/engine
lifetime diagnosis before pool persistence. Userland runtime attribution stays
open until a matching reproduction isolates it. Wider SESSION and independent
owner/reader acceptance remain separate. [Review](review.md) records agent technical
assessment; no UL, M3/R1 or release completion is asserted.
