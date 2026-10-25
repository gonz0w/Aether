# Exec close-reply containment — 2026-09-10

The actual Rust exec owner now contains missing and17-byte final-CLOEXEC-close
responses after image commit. It confirms the replacement is still parked under
the matching commit/freeze identity, stops source/backend/peer, observes each exact
retained terminal as kind3/detail144, then closes owner endpoints and reclaims.
No close request is replayed, descriptor table published or old image resumed.
Queued partial reply and peer bootstrap bytes are discarded only after all stops
are confirmed. Each case repeats two generations and six reclaims.

The [pre-code selection](../../NATIVE-SHELL-STARTUP.md#exec-close-reply-containment-selection--2026-09-10)
and [native reference](../../NATIVE-CONNECTIONS.md#exec-close-reply-containment--2026-09-10)
record authority, bounds, cleanup and simplicity. This uses existing incomplete
backends, bounded record observation and lifecycle calls. No kernel/SDK ABI,
external dependency, sibling or released-pin changes are introduced.

## Qualification

All175 connections cases and five launch cases pass, as does the host suite
(including99 Python tests and five Rust descriptor tests). Commands, UTC start,
elapsed time, exit status, input/tool/firmware identities and exact case oracles
are retained in mode logs, timing files and results. Both target suites are within
their1800-second review budgets. Use the existing native reference commands to
repeat them; no new CLI entry point is introduced.

| Deliberate mutation | Required result |
| --- | --- |
| Pad the17-byte reply into apparent success | Owner2050, zero reclaims |
| Omit source stop | Owner2051, zero reclaims |

Compilation must succeed and the exact semantic check must fail; a generic panic
or timeout does not pass. Forced stops do not emit terminal log lines: the owner
checks retained records directly. The positive harness rejects spontaneous
terminal lines and requires owner100 with six reclaims. The omitted-stop control
checks that a parked but live source cannot satisfy the terminal observation.

## Preserved attempt and evidence

`attempt1/` retains the initial harness-oracle failure. The missing-reply owner
completed all six confirmed stops/reclaims, but the harness incorrectly required
printed terminal records. Only that log expectation was corrected; native runtime
bytes were unchanged. Host and launch checks passed. Its sources, artifacts and
logs remain archived and are read back for verification.

`sources.json`/`sources.tar.gz` bind final sources and documentation; `run-sources.*`
retain the frozen pre-run inputs. `change.patch` compares the verified preceding
exec-streams snapshot. `artifacts.json`/`artifacts.tar.gz` contain all final target
files. `compatibility.json` compares171 older payloads outside boot entropy bytes
32..79 and their kernel binaries. `qualification.json` records exact counts and
maximum bounded owner size:239 sources,3,299 artifacts and6,648 bytes within
the8,192-byte owner limit. `final-checks.json` retains post-documentation host,
scoped formatting, workflow, standards and whitespace checks. The preceding
manifest and simplicity snapshot's fixed digest/four files are verified.
`manifest.json` seals every packet file except itself.

## Remaining scope

Stopping these fixed in-memory backends discards their entire private state; it
is not persistent-storage recovery or preservation of another process's shared
open descriptions. Replay prevention here follows the single-close control flow;
there is no new replay mutant or general exactly-once service contract. Native
commit replies are direct traps, not an injected lost-response service protocol.

Next contain incomplete bootstrap/table delivery after publication into the
trusted startup receiver, with no application I/O before complete validation and
confirmed stop before reclaim. Cross-process shared-holder exec, live signal and
stale-mapping transitions, public execve, installed SDK/dash acceptance and R1
remain open. Earlier command/M4 evidence is historical, not rerun for this change.
