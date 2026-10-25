# Actual OpenZFS waits: independent userland consumer

UL-003/015/081, 2026-10-06. Four fresh source-built native QEMU cases pass on
first attempt: normal, stop/reclaim/replacement, disabled clock (804), and
premature completion (OpenZFS fail-closed 125). This independently consumes
Aether’s actual CV/mutex composition with the maintained userland runtime.
It does not execute the initialized storage engine.

[Inputs](inputs.json) freeze the current 6458-member baseline, 363 kernel/build
members, firmware and sealed 282-member service SDK. [Source qualification](qualified-inputs.json)
and [port results](port-results.json) bind the rebuilt ordered baseline, actual
OpenZFS functions, adapted client, supervisor, tool identities and runtime archive.
The native client and supervisor exactly match the producer’s compiled bytes.
ISO kernel/envelope readback matches before each run. The envelope uses a
fixed developer-only test seed; no entropy/security claim follows.

| Case | Required result | Evidence |
| --- | --- | --- |
| Normal | Three ordinary terminals, supervisor 100/reclaimed3, one success marker | [receipt](normal.json), [UART](normal-serial.log) |
| Stop | Confirmed native 144/kind3 in the source-bound supervisor, peer and replacement ordinary terminals, reclaimed3 | [receipt](stop.json), [UART](stop-serial.log) |
| Disabled | Required primary 804, optional matching peer, supervisor401/reclaimed0, exact rejection panic | [receipt](disabled.json), [UART](disabled-serial.log) |
| Early | Required primary125, optional matching peer, supervisor401/reclaimed0, exact rejection panic | [receipt](early.json), [UART](early-serial.log) |

The stopped owner emits no ordinary terminal; the exact compiled supervisor
checks its native stop result before reclaim. No forced emulator kill counts as
success. Each guest has a 35-second budget and a 45-second owner bound with
terminate/reap evidence; disposable firmware, one q35 TCG CPU, 256MiB, no NIC.
Tool groups finish before emulator ownership. Compiler flags and all commands,
streams and cleanup records are retained by [compact retention](retention.json).

[Minimum Python](host-10.json) and [current Python](host-14.json) each reject47
semantic trace corruptions using [independent controls](host-check.py).
Optional peer absence remains permitted on fail-stop paths. [Review](review.md)
records the pre-execution scope and technical assessment; [checks](checks.json)
record local validation. This is scoped agent technical review; independent
human reader review and affected-owner acceptance remain separate.

The old SDK-intake dependency is superseded by actual Aether intake and this
consumer witness. Next Aether-owned work is complete provider composition,
initial-thread initialization, post-engine finish, native resource admission and
measured engine/helper/ARC lifecycle. Identity/configuration/volume/UTC and wider
SESSION remain open. No public SDK default, general POSIX conformance, M3/R1,
release acceptance or story completion is claimed. The existing finite lab kit
remains usable; deferred SSDK-06 reading does not block coding.
