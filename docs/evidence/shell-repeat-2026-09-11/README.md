# Three external commands in one serial dash lifetime

The actual native dash main runs /next three times without restarting the parent.
Child slot2 is collected and reclaimed between commands; parent0 generation1 and
the UART backend remain alive. The final status command prints72 and exits0.
This is a bounded producer experiment, not the full assembled R1 shell release.

The [pre-code plan](PLAN.md) defines authority, forbidden outcomes, resource limits,
verification and documentation scope. The simpler existing path retained each
child until parent exit; that prevents repeated commands. Reusing the existing
native copy/reclaim operations removes this lifetime restriction without another
service or kernel API. The dispatcher retains one child slot, scoped holder state
and the same backend descriptions. A small admission routine covers initial and
repeated copies; still-consumed older recovery fixtures remain regression inputs.

Parent freeze tokens and child generations advance independently of parent
identity. A copied child's exec freeze starts at1. Child routes and replacement
bootstrap use its own generation; real PPID stays5. Terminal observation, exec
completion, empty pending/partial request state, released child holders and valid
wait acknowledgment all precede reclaim. The old child capability must then fail
lookup. No additional unsafe code, pool/quota change, ambient UART grant, kernel
change, SDK object/pin change or sibling mutation is part of this result.

| Check | Result |
| --- | --- |
| Connections | 244 QEMU cases pass, including all prior cases |
| Launch | Five QEMU cases pass |
| Console ABI18 | Two QEMU cases pass |
| Host | `zig build test` passes |
| Process | C/Rust format, workflow, standards, experience, simplicity and diff checks pass |
| Repeated shell | Four prompts; seven ordered host writes; one shell, three child inputs |
| Lifecycle | Child generations1/2/3 exit72; parent1 exit0; backend1/probe2 exit17; six reclaims |
| Shared streams | Exactly36 stdin,51 stdout and8 stderr bytes, without reset between children |
| Old copy token | Second copy rejects owner2151 after exactly one reclaim |
| Old bootstrap generation | Second child exits224, publication rejects owner1950 after one reclaim |

Run the live documented commands with a fresh output directory:

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json --connections
python3 scripts/launch_smoke.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/console_smoke.py --connections --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

Exact commands, elapsed times, pinned tool/firmware/build identities, artifacts,
raw serial logs and source hashes are retained in reports and archives. The two
failed attempts are retained: [compile failure](attempt-1/TRIAGE.md) and
[overly late bootstrap-rejection oracle](attempt-2/TRIAGE.md). The second attempt's
positive runtime passed; final qualification reruns the full suite after correcting
the exact oracle. No timeout, generic panic or unrun case counts as acceptance.

`run-sources.*` freezes qualification inputs; `sources.*` adds final local progress
and reference updates. `change.patch` compares the preceding shell-resume packet.
`artifacts.json` indexes the read-back-verified archive; `qualification.json` records
counts and owner size. `cleanup.json` records verified duplicate removal; all
sealed failed/accepted evidence remains. `manifest.json` seals this packet.
Recorded helper scripts are audit artifacts, not commands to rerun in this packet.

The original native main/jobs/input object candidates remain unchanged and require
independent consumer acceptance. Three generations and bounded polling do not
provide indefinite human-paced sessions, general recovery or arbitrary processes.
Redirection, pipes, substitution and executable/filesystem integration remain work;
no TTY/job-control, OpenZFS persistence, installed packages or release acceptance
is claimed. Existing fixed ASCII fixture markers and upstream prompts preserve the
scoped Experience exception. Candidate Distribution tiers remain unfulfilled.

Final inventory: 255 sources, 4,435 target artifacts, maximum
owner 9,944 bytes within16KiB. Verified duplicate cleanup
recovered 3.04 GiB; current accepted target directories remain available.

The legacy `session` field in child-input events is the child ordinal; it does
not identify a new parent process. The repeated profile supplies `child` on later
command events. Use the single SHELL READY marker, real PID/PPID validation and
ordered terminal inventory to establish the one-parent lifetime.
