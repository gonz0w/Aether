# Builtin redirection followed by repeated external commands

Actual native dash executes `echo redirected >&2; /next`, restores stdout for
`echo restored; /next`, then executes /next again in the same shell. Each child
exits72 and is collected/reclaimed. Final `echo $?;exit 0` prints72, closes the
inherited streams and completes six reclaims.

The fix canonicalizes absent FD entries in the private fork and exec wire
snapshots. The shared local facade may retain binding/flag metadata after closing
a slot; present=0 means it owns no reference. Fork preparation still rejects
invalid presence and validates every live entry/count/reference. Both zeroed
snapshots now leave absent entries empty. Receiver validation, quotas, kernel,
shared facade, upstream objects, released pins and sibling repositories are
unchanged. No new unsafe code or authority is introduced.

The [plan](PLAN.md) records the pre-code requirement, forbidden outcomes, owners,
resources, tests and simplicity assessment, plus the discovered exec boundary.
Canonicalizing the snapshots is simpler than changing the shared local table
representation for unrelated consumers. It removes an unnecessary dependency on
inactive metadata without weakening the wire contract or adding another service.

| Check | Result |
| --- | --- |
| Connections | 247 QEMU cases pass, including all prior cases |
| Launch | Five QEMU cases pass |
| Console ABI18 | Two QEMU cases pass |
| Host/process | `zig build test`, scoped C/Rust format, workflow, pins and diff checks pass |
| Redirection | Actual redirected/restored builtin markers, four prompts, seven ordered host writes |
| Stream accounting |72 stdin,60 stdout and19 stderr bytes; distinct logical descriptions over one UART |
| Lifecycle | Child generations1/2/3 exit72; parent1 exit0; backend1/probe2 exit17; six reclaims |
| Raw fork encoding | Owner2150 before child copy, zero reclaims |
| Raw exec encoding | Owner2120 after copy and before image replacement, zero reclaims |

The rejection controls first print the actual redirected builtin marker and never
reach CHILD READY. Closed saved aliases are absent from the replacement bootstrap;
FD10 remains subject to existing CLOEXEC preparation/removal checks. Normal
stdio holders remain live across the commands. The repeated-profile exchange
receipt identifies the one parent session explicitly on each child-input event;
prior sealed receipts retain their original field semantics.

Use the live commands with a fresh evidence destination:

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json --connections
python3 scripts/launch_smoke.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/console_smoke.py --connections --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

The [first native attempt](attempt-1/TRIAGE.md) is retained: fork publication passed
but exec serialization still included the copied inactive fields and rejected2120.
The fix adds canonical exec encoding and a named counterexample; the final full
suite uses the corrected frozen sources. A separate pre-run accounting assertion
expected71 stdin bytes; the explicit command lengths plus three child bytes give72.
`preflight.json` records that correction before the first native build. No failure,
timeout, generic panic or unrun case is counted as acceptance.

`run-sources.*` freezes build/runtime inputs; `sources.*` adds final progress and
reference updates. Reports bind exact commands, timings, tools/firmware, source
hashes and artifacts. `change.patch` compares the preceding shell-repeat packet.
`artifacts.json` indexes the read-back-verified archive; `qualification.json` records
counts and owner bounds. `cleanup.json` records verified duplicate deletion, with
all failed/accepted archives retained. `manifest.json` seals the packet. Recorded
helper scripts are audit artifacts; do not rerun them inside this sealed directory.

This qualifies builtin descriptor redirection restored before fork. File creation,
redirection retained across exec, real pipes, command substitution, general
pipelines and indefinite interactive sessions remain unsupported here. Independent
SDK/userland acceptance, sys-init composition, OpenZFS persistence, installed
packages and R1 release acceptance remain separate. The existing fixed ASCII
fixture-output exception applies; this does not claim TTY conformance.

Final inventory: 255 sources, 4,492 target artifacts and a
maximum owner size of9,944 bytes within16KiB. Verified duplicate
cleanup recovered 2.84 GiB; current accepted target directories remain.
