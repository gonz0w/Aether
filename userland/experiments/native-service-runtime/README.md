# Private native service runtime

UL-003/015/081. This opt-in x86-64 static supplement supplies bounded musl
threads, joins, originally detached cleanup and monotonic condition/sleep waits.
The guarded base SDK is preserved. This is a candidate for Aether's actual-engine
intake, not public POSIX conformance or a shell SESSION extension.

Initialize once from the initial thread, before creating application threads.
`aether_runtime_init()` validates the private grants and creates one ordinary
joinable reaper, charged against the 82/two native worker limit. Application
capacity is therefore 81/one. The lifetime limit is512 successful admissions,
including the reaper; retirement releases a live slot, never lifetime admission.
These counts describe this profile, not CPU reservations or physical memory.

`aether_runtime_finish()` closes admission permanently. EBUSY means application
workers remain: collect joinable workers, allow detached cleanup to settle, then
retry. Success joins and retires the reaper and leaves live count zero. The caller
must serialize init/finish and must not use pthread handles after joining. Native
retirement failures poison admission; uncertain detached cleanup terminates the
owner with125. These are private diagnostic exit semantics, not recovery policy.

Default pthread attributes and bounded normal joinable/originally detached
attributes are supported. Normal mutexes and private conditions/rwlocks are the
synchronization profile; other initialization attributes reject unchanged. Manual stacks, C11 thread markers, dynamic detach,
cancellation, nonstandard try/timed join, scheduling/priority and other attribute variants reject. UTC,
signals, robust/process-shared synchronization and unrestricted futex operations
remain unsupported. The selected musl wrappers retain their conventions;
private lifecycle API errors are positive errno values. Time conversion checks
invalid/overflowing inputs; long waits retain one deadline across one-second
native parks. Early expiry becomes EIO. No interruption/cancellation support is
claimed. This backend uses explicit native grants, not Linux kernel syscalls.

Build offline from the exact guarded SDK seal selected in `build.py`:

```sh
python3 -B experiments/native-service-runtime/build.py \
  --sdk build/native-service-runtime-eolcouau/sdk \
  --output build/my-service-runtime
```

The output must be fresh under build/. Tools, all sealed SDK members, musl source,
patch anchors and the process runner are verified before compilation. Upstream
musl files retain their style and COPYRIGHT; original backend/tool code is BSD-2.
The fixed seal is deliberate: a changed base requires explicit intake/review.

Static link with base crt objects and the supplemental archive forced first:

```text
ld.lld -static -z noexecstack --no-undefined crt1.o crti.o app.o \
  --whole-archive libaether_runtime.a --no-whole-archive libc.a crtn.o -o app.elf
```

Include `runtime.h` and the matching base SDK headers. Do not also link Aether's
private probe backend or engine's old generic syscall adapter: duplicate strong
interposition is not a supported composition. Keep engine resource, entropy and
filesystem bindings with their domain owner; this supplement does not convert
quota into physical-page sysconf or supply identity/configuration/UTC.

`build.json` binds tools, selected upstream units, patches, source and archives.
[Independent native qualification](../../docs/evidence/native-service-runtime-2026-10-06/review.md)
records source-built apps, disabled-clock and dishonest-expiry controls, capacity,
long waits, broadcast/relock, reuse and shutdown. Each native case requires exact
stop/reclaim/replacement terminals and successful emulator/group cleanup. Build
success alone is not execution. Actual OpenZFS engine entry, its full helper/ARC
lifecycle, broader interruption schedules, independent owner and
reader acceptance remain separate work. No existing SDK pin or lab kit is changed.

Final native exhaustion also exercises511 collected application workers plus the
reaper per owner, then rejects the next admission without changing its handle.
Originally detached join rejects without reading an unmapping TCB. Runtime
mutex/condition entry guards reject nondefault/shared instances before effects.
Builder results use stdout; errors use stderr, exit1 for build failure and exit2
for usage. Help/version return0. Plain text escapes terminal control characters;
original paths remain in JSON receipts. No decorative/color/progress output.


[Focused liveness witness](../../docs/evidence/runtime-liveness-2026-10-06/README.md)
adds a source-only regression probe over the separately sealed UTC variant:
eight waves of8/one joinable helpers with original monotonic deadlines and reverse
joins, then32 detached/TSD retirement cycles; stop/replacement and source denial.
Exact97/41 admissions/live0 cleanup qualify selected schedules. It does not
reproduce or resolve Aether's observed engine leap timeout; no runtime archive or
candidate pin changes. The dated recipe uses frozen native inputs and the UTC-v2
handoff, not a Linux reference run or an engine/service test.


[Corrected reaper candidate](../../docs/evidence/reaper-fix-2026-10-06/README.md)
supersedes immutable v2 after Aether reproduced overlapping detached exits holding
musl's list lock while awaiting reaper permission. The sole reaper retires stopped
detached owners without taking that lock; atomic record publication/free orders
reuse after unmap/retire and live accounting. Creators and joiners retain musl
serialization, native quotas and fail-closed cleanup. Elapsed v3 and its matching
UTC v3 require independent Aether intake; prior serial/liveness passes did not
cover this ordered overlap. No attribution of the earlier engine timeout follows.
