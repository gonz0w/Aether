# Composed dash SESSION producer handoff

Producer qualification passes all 121 capacity, 358 connections and 431 runner cases
(910 native), 115 Python tests and configured Rust/Zig/pin checks. This is a producer
handoff; independent userland acceptance remains open. `verification.json` and
`SHA256SUMS` attest final export/archive verification; absent those files, packaging
is still provisional.

## Delivered experiment

The unchanged pinned `composed.sh` runs through one actual dash main/jobs parent
per shell lifetime, repeated three times. It executes the unchanged helper for
quoted/wildcard argv and environment, two three-stage pipelines separated by command
substitution, descriptor closure, a stderr diagnostic and a final builtin. Each
parent preserves its PID. There is no manual job/phase sequencer or dummy worker.

Across the positive run: three parent launches, 27 native copies, 21 actual helper
exec replacements, 30 zero-status terminals and 30 reclaims. The reused child slot
reaches generation 15; repeated jobs reuse both bounded pipe objects. Peak remains four
workers plus the fixture owner. No existing profile limit is widened.

Every parent produces exactly these separate streams:

```text
stdout (65 bytes):
argv ok
pipe data
substitution ok
pipe data
closed ok
session ok
```

```text
stderr (19 bytes):
session diagnostic
```

The runtime captures actual authenticated writes; expected strings live only in
the host consumer oracle. Observation bytes are hex encoded by a bounded owner-only
007 operation after complete worker/channel cleanup, preventing program output
from forging test markers. The supervisor record is not a UART grant or a shared
application API. Existing 006 interactive serial behavior is separately regressed.

## Phase identities and collection

For parent lifetime `g = 1..3`, the parent is native slot0/generation g with
PID `6*g+1`. Child PIDs are `6*generation+slot+1`; they are selectors, never grants.
The authenticated endpoint/native-handle ledger determines ownership.

| Phase | Native child identities | Exec replacements | Positive child wait status |
| --- | --- | --- | --- |
| First argv | slot2, generation `5*g-4` | helper | 0 |
| First pipeline | builtin slot2/`5*g-3`; helpers slot3 and slot4/`2*g-1` | two helpers | all three 0 |
| Substitution | slot2, generation `5*g-2` | helper | 0 |
| Second pipeline | builtin slot2/`5*g-1`; helpers slot3 and slot4/`2*g` | two helpers | all three 0 |
| Final descriptor check | slot2, generation `5*g` | helper | 0 |

These produce eight image-admission records per parent: one fresh parent and seven
helper replacements. Native copies are counted separately; they do not emit image
admission records. Across the positive run, image records are slot0:3, slot2:9,
slot3:6 and slot4:6. Nine child wait replies per parent precede child reclamation;
the owner ledger forbids reclaim before full reply delivery. A dead parent's
abandonment is cleanup, not a successful wait delivered to that parent.

`phase-oracles.py` separately verifies exact image identities and complete terminal
groups before each parent observation from archived native logs. Eight phase checks
and eleven wrong-identity/early-observation counterexamples pass. This supplements
the ordinary exact-stream/lifecycle suite oracle; it is not consumer sign-off.

## Producer implementation and authority

- `user/native-capacity/session-owner.rs`: request-driven fork/exec/wait and bounded
  pipe/child ownership; authentic native identity replaces parent-generation inference.
- `session-client.c`: real descriptor snapshots, actual argv/env serialization,
  native fork/TLS rebinding and the unchanged dash/helper bodies.
- `scripts/session_smoke.py`: immutable consumer inputs, builds and independent
  stream/terminal/reclaim oracle inside the existing capacity suite.
- `kernel/native_session_observation.zig` plus the 007 runtime operation: full-record
  validation before output, caller/grant/range/quota/ordinal/cleanup checks; legacy
  profiles return ENOSYS and workers cannot report or access UART.

Child collection reserves the exact identity until the full wait reply is delivered.
Only confirmed terminal state permits holder disposal and backing reuse. Parent
abandonment stops and observes remaining children before discarding pending waits,
closing transport and reclaiming. Partial messages remain retained across retry.
All linked session owners stay below the existing 4088-byte usable stack; current
inspected maximum is 3688 with 400 bytes of margin (the substitution control is lower).
The inspection aid and immutable builtin-call review are scoped evidence, not a
formal whole-program proof or whole-kernel security assessment.

## Cases and rejection boundaries

| Case | Required observed result |
| --- | --- |
| `session-composed` | Exact streams, 27 copies/21 execs, 30 normal terminals/reclaims |
| `session-wrong-env` | Actual helper91, parent31, two reclaims; parser must preserve wrong WITNESS |
| `session-bad-byte` | Complete normal lifecycle; ordinary host oracle rejects exact stdout mismatch |
| `session-bad-substitution` | Mutated actual pipe read reaches parent33; six reclaims |
| `session-fd-leak` | Real inherited unflagged fd3 reaches unchanged helper95, parent35; ten reclaims |
| `session-stale-wait` | Old collected PID returns ECHILD with unchanged status while its slot is reused; full positive completion |
| `session-stale-accept` | Deliberate old-PID success is detected by parent144; five terminal/reclaims including confirmed cleanup |
| `session-retained-writer` | Real parent fd10 CLOEXEC alias keeps first-pipe EOF blocked; pending wait/read states precede three confirmed stops and five reclaims |

The retained alias is visible in real fork snapshots and removed by helper exec.
The control cannot pass from a timeout, a fictitious holder, or accepted stop alone.
Host unit counterexamples reject incomplete/duplicate/corrupted observations,
wrong terminal identities/statuses, premature success and marker-shaped input.

## Reproduction and consumption

Run from `/Users/cam/DEV/Aether` with the recorded toolchain and SDK. The full
capacity command is the producer acceptance selection; `--case` is focused only.

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py --connections --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py --command-runner --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

After sealing, verify this packet before consuming any member:

```sh
shasum -a 256 -c SHA256SUMS
```

`capacity-artifacts.tar.gz` retains each case's ISO, launch envelope, serial log,
build outputs and result record. `capacity-artifacts.json` hashes every member;
`attempt-capacity-sources.*` records the corresponding runtime sources.
`host-inputs.*` also captures host tests, including the C host fixture. Current
sources may advance; archived source and exact inputs identify this delivery.
The sealed prior `shell-streams-2026-09-24/consumer-inputs.*` supplies the six
unchanged consumer files; `scripts/session_smoke.py:INPUTS` verifies each digest.
Builds do not follow a mutable userland/standards source checkout or change pins.
SDK and tool receipts are recorded in each suite result and must match for replay.
`tool-inventory.json` records 15 resolved tool identities; `tools.lock.json` preserves
the actual compiler/linker lock. `sdk-inventory.json` records 4311 regular SDK files
matching the prior sealed consumer inventory plus the resolved contents of its
existing obj/Makefile symlink. The added symlink entry is not a changed SDK artifact
or a make invocation; `sdk-comparison.json` records the distinction.

`replay-final-inputs.*` supplies the complete 661-file repository source/support
snapshot, including boot inputs, offline standards pins, host tests and immutable
SESSION consumer inputs. It is broader than the 314-file frozen source/test inventory.
Both preliminary and final isolated exports pass 115 Python and configured
Rust/Zig/pin host checks. The final export also rebuilds and boots the unchanged
composed workload successfully; its native outputs and cleanup verification are
retained in `replay-final-native-*`. These producer-owned replay checks establish
reproducible packaging, not independent userland acceptance.

Userland owns independent SESSION-01–06 replay and the shared SDK/runtime adoption
record. Consume the unchanged script/helper and compare separate stream and
lifecycle evidence, then record acceptance or a concrete mismatch in userland.
Producer tests and linked upstream objects are not that independent acceptance.
No sibling repository was modified and no acceptance was recorded on its behalf.

## Evidence and unsuccessful attempts

Final producer qualification: 121 capacity, 358 connections and 431 runner cases
(910 native), 115 Python tests plus configured Rust/Zig/pin checks. The finalizer
checks 314 source/support files, 293 matching runtime inputs, matching tools/SDK,
archived SESSION oracles, linked-owner bindings and verified output cleanup.
`verification.json` and `SHA256SUMS` exist only after those checks succeed.

Retained attempts include:

- Attempt1: missing PT_TLS in both new adapters; native loader rejected before
  admission. Added a checked TLS cookie, preserving loader rules.
- Attempt2: missing parent-slot directory configuration; guest completed 30 reclaims
  but host rejected unexpected getcwd diagnostics on stderr. Fixed the build flag
  and made its omission a compile-time error; expected output was not relaxed.
- Attempt3: focused unchanged-session pass after those corrections.
- Controls1: seven cases passed; artificial writer retention contradicted the next
  fork snapshot and was rejected early. Replaced it with a real CLOEXEC parent alias.
- Attempt4: corrected retained-writer control passed at its intended EOF/stop boundary.
- The first auxiliary tool-inventory command assumed the wrong LLD installation path; it failed before writing an inventory. The corrected command uses the actual tools lock. No native build used that guessed path.
- `draft-attempts.*`: isolated earlier source/compile/stack/host-oracle attempts,
  including failures. Scratch iteration is not native qualification.

The runner packaging wrapper stopped on a `.DS_Store` change between inventory
and archive creation. The failed inventory/archive and complete member audit are
retained; only that metadata member differed. `recover-runner-archive.py` records
the verified retry. Native runner execution itself passed all 431 cases.

Every owned output root is removed only after archive readback and original hash
verification. Metadata-only archive races are retained and retried; no build or
runtime mismatch is excused as metadata. Earlier sealed evidence remains unchanged.

## Remaining boundary

This is a bounded scripted producer workload, not an R1 bootable distribution or
arbitrary interactive process runtime. Independent userland replay, shared native
SDK/runtime integration, assembled sys-init/serial-shell boot flow, persistent
filesystem and package installation keep their existing owners and release gates.
Released standards pins remain unchanged. No formal reader/consumer sign-off,
production security claim or full draft adoption is implied.
