# Source-built public fork — 2026-09-10

This isolated candidate executes actual musl `fork()` through a native staging
hook at `_Fork`'s syscall site. Upstream fork orchestration and child repair remain.
The rebind variant updates auxv and endpoints without setting cached TID or clear-TID;
libc performs that repair before returning. FD10 keeps CLOEXEC through publication;
only child application code subsequently clears its private flag.

The [pre-code selection](../../NATIVE-SHELL-STARTUP.md#public-fork-first-execution-selection--2026-09-10)
scopes this first public-call run and its follow-ons. The public client checks actual
parent/child return values, PID/getppid, cached/kernel TID, mask16, errno, private
TLS/data, rebound endpoints, shared backend offsets and independent descriptor flags.
Known cancellation returns EAGAIN after owner recovery; local refusal returns
ENOTSUP before publication through musl's normal mask/errno unwinding.

Five new cases join the full connections suite:

| Case | Required result |
| --- | --- |
| copy-inherit-public-fork | Parent71/child72/backend17, two generations, six reclaims |
| copy-inherit-rollback-public-fork | Recovered parent73/backend17/replacement17, two generations, six reclaims |
| copy-inherit-prepare-public-fork | Source78/backend17, three generations, six reclaims; vacant child and spare channels checked |
| copy-inherit-public-fork-flag | Premature child CLOEXEC clearing: child80/owner1950, zero reclaims |
| copy-inherit-public-fork-repair | Omitted libc child repair: child80/owner1950, zero reclaims |

The link map identifies source-built fork.o and _Fork.o plus the real staging hook.
The _Fork disassembly retains native set_tid_address after staging. Private fork
sources, native syscall header, upstream internal/public headers and musl COPYRIGHT
are retained among target artifacts, under upstream terms. The source archive is
verified against the existing SDK receipt before use. The original SDK and sibling
repositories are unchanged; these objects are linked only into the selected cases.
Upstream C retains its style and uses Wall without the fixture's Wextra/Werror;
first-party client diagnostics remain strict. No general warning suppression or
source reformatting was applied to musl.

Three build failures precede final qualification, all retained with runtime sources,
commands, logs, source hashes and artifact archives:

- attempt1: missing internal feature-header weak-alias definitions.
- attempt2: missing internal signal-function declarations; restored the pinned
  musl header overlay in private output.
- attempt3: first-party client used undeclared _Exit; changed to declared _exit.

These failed before QEMU connection cases, and are not successful negative tests.
Each attempt's host and launch results remain separately retained. The final run
uses frozen corrected sources. No failed attempt was deleted or relabeled.

No kernel, Rust owner, backend, installed SDK or released pin changed. A compile-time
rebind variant and the new client/harness preserve previous modes. Compatibility.json
checks all 132 previous payloads outside entropy and their exact kernel images,
backend identity and the owner bound. Prior command/M4 runs remain historical.
Live-handler/atfork-callback composition, exhaustive admission/failure cases, native
wait/exec/vfork and independent SDK/dash acceptance remain open. This does not
establish installed fork support, full POSIX semantics or R1 readiness.

Commands are recorded with UTC boundaries, status and elapsed time in timing JSON:

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --connections \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

The collector verifies prior sealed evidence, final source identities, the pinned
simplicity extension and archive readback. runtime.patch describes this change;
final-checks.json records pin/workflow/format validation and the disassembler digest.
manifest.json seals this packet including all failed-attempt archives.

Final qualification passes 137 connections and five launch cases plus host/Zig/pin/
workflow checks including 98 Python tests. All final suites met review budgets.
Archive readback verified 226 final sources and 2,681 final target artifacts, plus
all three failed source/artifact archives. All 132 previous payloads/kernel images
retain compatibility; maximum owner remains 5,880 of 8,192 bytes.
