# Copy-profile thread identity — 2026-09-10

This is the kernel identity prerequisite for libc child rebinding described in
[NATIVE-SHELL-STARTUP](../../NATIVE-SHELL-STARTUP.md#copy-profile-thread-identity-prerequisite--2026-09-10).
All 18 connection cases, five launch cases, seven M4 cases and 431 command cases
pass: 461 target cases. Final-source host checks pass 98 Python tests plus Zig,
workflow and pin checks. The command suite took 1,413.93 seconds, within its
1,800-second budget.

The single-context connections copy profile now returns generation*4+slot+1 from
set_tid_address after existing pointer validation, agreeing with getpid. Previously
it returned slot+1. Legacy and threaded profiles retain their existing behavior.
No new syscall, mutable state, resource pool or dependency is introduced.

The copy witness verifies initial public libc gettid/getpid agreement, then
registers a separate anonymous clear-TID page before freeze. The child unmaps its
copy of that page, demonstrating that the source's registration was not inherited.
The parent still cannot unmap its registered page, including after a rejected
replacement address. Valid replacement with an owned stack word releases the old
pin and returns the correct lifetime identity in each process. Two-generation
positive and rollback fixtures preserve their six-reclaim results.

Musl gettid reads its pthread cache. The child's cache intentionally still names
the parent in this witness: making the registration call alone does not update it.
Musl's post-fork path uses the returned value to refresh that cache. This packet
fixes the kernel prerequisite; it does not claim an installed SDK child-return hook,
libc grant rebinding, inherited descriptors, public fork, exec/wait or full dash.
The reviewed owner inputs are hashed and archived, including upstream COPYRIGHT;
third-party terms remain unchanged. No sibling files or released pins were edited.

## Controls and retained failure

copy-slot-tid deliberately restores the old slot-only result. It must reject with
parent terminal 230 and supervisor 1800, with zero reclaims before publication.
The existing shared-backing, anonymous-metadata and zeroing controls retain their
exact required outcomes. Wrong panic context or a watchdog timeout is not a pass.

The first run passed the identity checks but failed the existing copy-anonymous
oracle: the new registration-isolation check encountered missing anonymous metadata
first and returned 231, instead of the established protect check's 218. The final
fixture runs that established metadata check first. Its expected result is unchanged.
The failed source snapshot, timing, logs and full target directory are retained.

## Verification

Each final suite has UTC start/end, monotonic elapsed time, exact command and exit
status receipts. Reports bind sources, tools, commands and artifacts. M4 requires
its private QMP socket permission. Formatting/Python syntax and the four-file
simplicity snapshot checks have separate receipts. collect.py verifies final
source matches, the previous copy packet's immutable manifest, the bounded source
delta and archive readback. The final manifest seals this packet.

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --connections \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/regression.py
python3 scripts/launch_smoke.py --command-runner \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

The next SDK work must update the known auxv, transport/descriptor stores and
pthread cache before child application code resumes, respecting musl's fork-lock
and signal obligations. Scanning arbitrary copied memory for grant integers or
calling a private post-fork helper without its surrounding protocol is not the
selected solution. No independent owner approval, native exhaustion/soak/hardware
coverage or assembled release readiness is established here.

Archive readback verified 228 frozen source files and 9,557 target artifacts,
including the failed run. The separate owner-input archive retains the inspected
SDK/musl source and its upstream copyright notice.
