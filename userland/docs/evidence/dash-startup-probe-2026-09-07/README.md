# UL-007 startup prerequisite probe — 2026-09-07

Six host cases pass, and the production probe links against the pinned native SDK
(11688-byte ELF). Native execution remains **NOT RUN**. The latest producer STATE
still describes the cat handoff and separate storage work; no matching dash startup
producer delivery was identified. This probe is ready for a reviewed startup pair,
not a native shell or a replacement for producer implementation.

Run `python3 -B experiments/dash-native/check-startup.py`. The driver verifies the
previous dash link evidence manifest, its captured intake and full snapshot, SDK
files and LLVM tools. The macOS host reference explicitly selects the local Xcode
SDK; its resolved path/settings hash and actual compiler identity are recorded.
This is not a complete host SDK source pin or a Linux reference execution.

| Case | Expected and observed exit | Meaning |
| --- | --- | --- |
| Normal | 0 | Positive stable PID, disposition/mask round trips, descriptors 0–2 and duplicate >=10 with CLOEXEC |
| Invalid PID | 10 | Invalid process identity rejected |
| Failed signal query | 20 | ENOSYS is not hidden |
| No-op disposition setter | 20 | Success without changed state rejected |
| No-op mask setter | 21 | Success without changed state rejected |
| Duplicate missing CLOEXEC | 30 | Descriptor flag omission rejected |

All six cases additionally verify SIGUSR1 disposition/membership restoration and
closure of an allocated duplicate. The probe restores saved state on failure;
close is not retried after uncertain completion. Cleanup failure has internal exit40.
The tests do not exercise cleanup failure, signal delivery, all mask bits, cross-child
identity, actual exec-close behavior, FD alias I/O, fork/wait or native authority.
Do not use host PID observations as native grant or identity-policy acceptance.

Attempt1 failed compilation because the host SDK include path was absent; no test
or native build ran. Attempt2 passed after selecting the explicit host SDK. Attempt3
adds and passes the restoration/duplicate-closure assertions; its eleven owned
commands all complete with cleanup and strict C17/format diagnostics. Sources,
commands, separate streams and results for every attempt are retained. The native
artifact contains only the production probe and existing adapter, no fault wrappers.

The probe is silent and uses exit status only. A future native owner must provide
an appropriate startup envelope with inherited standard descriptors and independent
terminal/cleanup observations. First qualify this subset and denied startup, then
actual dash initialization, child exec/wait and pipelines. A zero here alone is not
M3 acceptance. See [review](review.md) and [startup plan](../../../experiments/dash-native/PLAN.md).
