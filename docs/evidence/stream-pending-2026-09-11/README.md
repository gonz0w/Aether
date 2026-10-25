# Pending input with child progress — 2026-09-11

The opt-in private stream owner holds a nonempty stdin request after a canonical
backend EAGAIN, retains its original caller frame, and retries once per caller
per scheduling round. Other caller requests continue. Shared positions and holders
change only on completed operations; malformed or incomplete replies still reject.
No kernel, ABI, released pin, SDK object or sibling repository changed.

The parent blocks reading a. The exec replacement writes ! to stderr; the backend
accepts that write only after observing an empty parent read, then enables input.
The owner requires a child write while the parent request is held. Child b and
parent FD10 c prove shared position continuity. Copied mask16, removed child
FD10/stdout CLOEXEC, actual wait status72, three final backend closes and exact
child72/parent71/backend17 outcomes pass in each of two generations: six reclaims.
The backend is deterministic memory-backed input, not UART. Actual dash command
cases remain regressions; the new pending-input witness is a C consumer.

| Selected check | Result |
| --- | --- |
| Complete connections suite | 235 pass, including the four new cases |
| Launch suite | Five pass |
| `zig build test` | Pass, including host/harness, workflow and three offline pins |
| Rust/C format, workflow, standards, whitespace | Pass; commands in final-checks.json |
| Simplicity snapshot | Pinned manifest and all four documents verified |

The `-reply`, `-eof` and `-position` controls deliberately forward EAGAIN,
substitute EOF and advance the offset during retries. Each rejects at parent85,
owner2130, zero reclaims and the expected native-profile panic. Their serial logs
are included here and in the artifact archive. No unexpected build or target run
failed in this qualification. All runs use the frozen implementation sources;
post-run updates affect only progress/reference documents.

[Pre-implementation plan](plan.md) records requirement, forbidden outcomes,
ownership, scope, simplicity and test selection. Existing private channel authority,
32-byte framing, six channels, three slots, per-slot generations, 16 KiB owner cap
and 4 KiB owner stack are retained. Pending requests reuse the two existing
400-byte frame buffers; there is no heap queue, new FFI or kernel event facility.
Target success is not a stack high-water measurement or a performance guarantee.
The witness requires the current single parent/child pair and promptly answering
backend; a blocked backend response still fails its existing watchdog.

Before-fork pending input and a terminal caller with a held request currently
reject this bounded experiment. They do not claim cancellation or recovery.
General interruptions, indefinite waits, zero-length pending-read controls,
concurrent reads from both callers and independent consumer review remain open.
Next connect actual dash stdio to the UART backend, add pre-fork input handling,
and retain one console-grant lifetime across the session. Interactive startup,
shell pipelines, persistent loading and assembled R1 acceptance remain separate.

`*-timing.json` binds exact commands, timestamps, return codes and durations.
`*-results.json` records cases and tool/source identities. `run-sources.*` preserves
the frozen run inputs; `sources.*` includes final reference/progress updates.
`change.patch` compares against the preceding console/process packet.
`artifacts.json` indexes the read-back-verified artifact archive; qualification.json
records directories, counts and owner size. `manifest.json` seals this packet.
`cleanup.json` records verified removal of superseded unpacked suite duplicates;
their earlier sealed archive remains unchanged. Current qualification outputs stay
available in zig-out.

The sealed snapshots cover 251 source files and 4,220 target artifacts. Maximum
compiled owner size is 9,128 bytes, within the existing 16 KiB profile limit.
Verified cleanup removed 2.42 GiB of superseded unpacked outputs.
