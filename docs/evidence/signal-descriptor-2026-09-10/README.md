# Signal and descriptor inheritance composition — 2026-09-10

Composed the existing opt-in signal-copy kernel profile with inherited streams.
The parent queues a coalesced signal while preparation is masked. The child queues
its own fresh post after libc/endpoint rebinding. Delivery stays masked through
receipt validation, private FD10 flag updates and completion. The handler checks
completion, matching auxv endpoints and cached/kernel identity, exact current
lifetime references/rights/roles, and private descriptor flags/counts. It duplicates
FD10 into FD11 and closes that local duplicate, preserving counts and errno without
issuing backend I/O. The existing shared byte sequence remains the application oracle.

Success and pre-copy rollback use initial mask16 and require one handler per returning
process, the original terminal ordering and six reclaims. The rollback case preserves
parent signal state until failure completion and matching copy cancellation. This
composes existing mechanisms; kernel, Rust owner, backend and shared adapters are
unchanged. No new syscall, wire schema, build flag, allocation or service is added.

Early parent restoration before preparation produces source79/owner1950. A stale
child reference after completion or omitted fresh child post produces child79/
owner1950. A corrupted decoded parent completion keeps the callback gate closed
and produces source79/owner1950. Each control requires exact terminal context and
zero reclaims. The invalid-outcome case tests the local completion-validity gate;
it is not full malformed-wire recovery qualification.

The first frozen attempt passed 109 connections, five launch cases and the host
build. Review then identified that the parent gate needed explicit completion
validity rather than treating any decoded result as completed. That attempt's
sources, reports, logs, timings and native artifacts are retained as superseded
coverage. The refinement admits parent callbacks only for outcomes67/68; the child
remains behind its exact67 check. Without that refinement, the corrupted outcome
would allow handler-local FD work before the client returned252. The new exact79
control distinguishes that ordering. Refinement changes are retained separately.
No qualified runtime suite failed; the first attempt does not qualify final bytes.

The final complete 110 connections and five launch cases are selected on frozen
sources, plus host/Zig/pin/workflow checks (98 Python tests). Reports and timings
record exact commands, source/tool/SDK identities, status and review budgets.
The [pre-code selection](../../NATIVE-SHELL-STARTUP.md#signal-and-descriptor-composition-selection--2026-09-10)
records authority, pointer lifetimes, nested masking, simplicity and test obligations.
The callback checks bounded state before descriptor mutation and preserves errno;
existing native enforcement remains the authority boundary.

Only inherit-client.c and launch_smoke.py runtime sources changed from the preceding
handler-return packet. Previous command/M4 execution remains historical. No sibling
repository, released pin or independent consumer acceptance changed. Rejected
preparation and malformed/partial completion with live handlers still need composed
recovery witnesses. Installed SDK fork/exec/wait and full dash remain unfinished;
this experiment does not establish R1 readiness or handler backend-I/O safety.

The collector verifies the previous sealed packet, both source snapshots, the
simplicity snapshot and archive readback. Native artifacts preserve musl notices.
Formatting, compatibility and final checks have separate receipts; manifest seals
the packet. Both attempts' target artifacts are retained in the combined archive.

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --connections \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

Final 110 connections and five launch cases pass. Both attempts meet their review
budgets. All 104 previous payloads match outside entropy and their kernel images
are identical. The backend is identical and maximum owner remains 5,880 bytes
within the 8,192-byte limit.

Archive readback verified 225 final source files and 3,997 native target artifacts
across both runs, plus the separately retained first-attempt source snapshot.
