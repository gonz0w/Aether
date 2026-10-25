# Shared UTC private delivery — 2026-10-06

UL-003/015. Aether's new raw RTC intake unblocks userland UTC work.
The maintained [private provider](../../../experiments/native-utc/README.md)
now establishes one immutable runtime estimate from explicit unauthenticated
q35 RTC-as-UTC policy, then shares it with application helpers. Raw calendar
coherence is a kernel observation; UTC interpretation is an explicit userland
choice. Existing guarded SDK and elapsed v2 bytes are unchanged.

Selected handoff: **build/sdk-deliveries/native-utc-2026-10-06-v2**.
[Delivery receipt](delivery.json) binds314 members and seal
`15887618d50ac659da095d7a32af0255a8f382b41e40661e6ac6614e6b32645c`.
Runtime archive SHA256:
`d894b4a8f5624a265e265029a28e0b532f1e688cdb6a925cb3cd54f0ca4ee3e4`.
This archive replaces the elapsed supplement when explicitly selected, and
still links whole-archive before the same guarded libc/crt. The full sealed
base, source, helper, recipe, licenses and scoped qualification receipts are
included for offline intake. [Rebuilds](rebuilds.json) confirm actual Python
3.10.21/3.14.7 and the standalone copied recipe produce identical archive bytes.
V1 is historical before the missing-aux errno correction; never select it instead.

| Final native case | Required result | Evidence |
| --- | --- | --- |
| Normal explicit2026-10-06 date | Initial/helper shared estimate, checked libc reads, close/retire, three successful owner lifetimes | [receipt](normal.json), [UART](normal-serial.log) |
| Explicit2000-02-29 leap date | Same shared behavior with valid leap-day conversion | [receipt](leap.json), [UART](leap-serial.log) |
| Disabled RTC | ENOSYS establishment, unchanged unavailable outputs, terminal856 and supervisor401/reclaimed0 | [receipt](disabled.json), [UART](disabled-serial.log) |
| Absent policy | ENOTSUP establishment, unavailable outputs, terminal855 and supervisor401/reclaimed0 | [receipt](policy.json), [UART](policy-serial.log) |

All four final cases pass. Each positive has exact slot0/gen1, slot1/gen1 and
slot0/gen2 ordinary terminals, supervisor100/reclaimed3 and one success marker.
Denials require the primary exact code; the peer may fail-stop before printing,
but any peer line must match. Supervisor and panic identities are exact.
[Input freeze](inputs.json) binds379 current kernel/build/source members, raw RTC
producer receipt, firmware and sealed base. [Runtime recipe](runtime-build.json)
and [qualified sources](qualified-inputs.json) bind compiler flags/source/tool
identities. Exact map origins put clock, UTC and checked time/gettimeofday symbols
in the selected archive. Actual ISO kernel/envelope readback precedes execution.
The envelope's fixed test seed is developer-only, not an entropy claim.

One q35 TCG CPU/256MiB/disposable firmware/no NIC,35-second guest/45-second owner,
1MiB UART/4MiB stderr bounds; complete terminate/reap required, no forced-kill
success. Tool groups finish before the VM owner starts. Elapsed waits, native
capability validation and unsupported realtime absolute waits remain unchanged.
The final test caller permits at most16 explicit EAGAIN attempts with1ms sleeps;
the provider itself returns temporary source failure without internal retry.

The host Gregorian test compares760 independently generated Python dates in
four BCD/binary/12h/24h modes:3040 comparisons plus invalid calendar/source/mode/
reserved/overflow/regression and unchanged-output controls under UBSan. The
[injected provider test](provider-host.json) separately exercises missing grant,
errno preservation, source/clock errors, no partial publication, worker/late
establishment denial and permanent closure. These host tests do not qualify
native authority. [Minimum](host-10.json)/[current](host-14.json) each reject50
semantic trace corruptions; [builder controls](builder-10.json) and
[current controls](builder-14.json) each pass seven actual stream/exit/input/output
checks. [Checks](checks.json) cover quality/standards, syntax, format and whitespace.
[Compact retention](retention.json) preserves source changes, commands, streams,
cleanup, artifact hashes and all failed attempts without a whole-run archive.

Earlier failures remain separate: two sealed-source path assumptions, unavailable
strict-SDK stdatomic header (replaced by explicit Clang C17 atomics), missing host
SDK root, absent test TLS rejected by loader, replacement854 with unresolved exact
errno, and host missing auxv declaration. Refined diagnostics did not reproduce854;
final tests accept only the documented temporary EAGAIN and still fail every other
establishment error. An actual final review found getauxval could modify errno on
missing auxiliary data, corrected before the final archive/native rerun and seal.
Passing later attempts does not erase the earlier failure or prove its attribution.

UTC quantization is one second plus up to2ms read-bracket uncertainty. Source
accuracy/offset, elapsed drift, physical RTC, adjustment/synchronization and
cross-core accuracy are unmeasured. Nanosecond projection fields do not establish
nanosecond accuracy. Gregorian1970–9999 is supported; leap-second60 is rejected.
Current initial IDs1/2 are an explicit private profile boundary. No default SDK,
lab-kit, sibling, public POSIX, M3/R1 or release acceptance is implied.

Next Aether-owned gate: independently consume this exact handoff and rebuild/check
actual gethrestime/gethrestime_sec/getlrtime callers. Their pinned upstream inline
bodies ignore gettimeofday failures; getlrtime also requires checked signed
nanosecond range. Libc wrappers cannot make those bodies safe by themselves.
Actual pool create/import/transactions/reboot and engine resource/service recovery
remain owner work. Wider SESSION still gates continued ordinary shell use.
Deferred SSDK-06 reading is separate. [Review](review.md) records agent technical
assessment; external independent reader/owner acceptance remains pending.
