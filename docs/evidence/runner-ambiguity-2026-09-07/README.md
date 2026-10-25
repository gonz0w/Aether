# Runner incomplete-reply containment — 2026-09-07

This bounded AEOUT001 witness separates what a client can know from what its
surviving owner can verify. See the [preimplementation contract](contract.md) and
[NATIVE-COMMAND-IO](../../NATIVE-COMMAND-IO.md) for scope and exact rules.

The owner commits a write or consumes a close, then closes its real reply endpoint
after zero or eight bytes. Incomplete receipt makes the client poison the
connection, consume local descriptors without further channel calls and exit1.
Test-only trap counters check this client boundary; the owner independently
rejects further requests and requires request EOF at confirmed termination.

Only then does the owner retire the exact remaining aliases, read back both sinks
and unchanged input, close all backend handles with stale denial and reclaim both
native instances across two generations. The client cannot infer the committed
prefix, remote alias retirement or later backend cleanup from EIO. This is not a
new reconciliation API or an assertion of client-side recovery.

## Selected cases and controls

- Zero/eight-byte stdout write replies retain exactly 16 help bytes; lost stderr
  reply retains exactly 16 usage bytes. The other sink remains empty.
- Zero/eight-byte stdout-close replies retain full help output. The owner observes
  stderr as the sole remaining alias; both aliases remain after lost write reply.
- Clearing poison and resuming traffic rejects at 1320. Reporting success after
  incomplete receipt rejects at 1301. Skipping remaining owner alias retirement
  rejects at 1321 before backend cleanup/native reclaim.

Positive completion still requires exact normal status1, no partial or queued
request, independently verified backend contents/cleanup, and four native reclaims.
The already-consumed reply writer is not closed twice. Existing deterministic
error, startup, command/child and local-empty profiles remain separate.

No kernel, ABI, capacity, dependency, release pin or sibling repository changes
are part of this slice. New partial-reply emission is a synchronous existing trap
using eight bytes of a valid stack buffer, with no retained pointer or new unsafe
block. C/Rust conventions and the legacy transport's scoped style are retained.

## Remaining coverage

This is not exhaustive disconnect coverage: pre-effect failures, other byte cuts,
owner/backend death and general reconciliation remain unqualified. Exact denied
launches, remaining startup cases, role/child composition, the complete RL matrix,
affected-owner review and immutable handoff remain ahead of independent userland
adoption. Neither UL-059, UL-067 nor the filesystem/package release is accepted.

Reproduce with the full NATIVE-COMMAND-IO command, pinned SDK
`/Users/cam/DEV/Aether-userland/build/native-c-5olokhku` and tools lock
`/Users/cam/DEV/Aether-userland/experiments/musl-reference/tools.lock.json`.
Use those arguments with `--connections` and `--inherited-launch` for regressions.

## Qualification

All selected runs pass on their first attempt: 93 command cases (previous 85 plus
five reply-cut witnesses and three exact rejection controls), nine inherited-launch
and six connections regressions. All 98 Python tests plus Zig/offline pin/workflow
checks, Rust/C formatting and diff checks pass. Sources were frozen throughout
qualification and match all three suite receipts. All 34 kernel/build inputs and
SDK/libc/tool-lock identities match the preceding failure qualification. Stream
supervisors remain at most 5,224 bytes within the existing 8,192-byte bound.

`artifacts.tar.gz` retains frozen sources, generated headers, native envelopes,
compiled artifacts, commands and serial logs. ISOs, installed boot duplicates and
kernel.elf are omitted; ISO hashes and build commands remain in receipts.
`qualification.json` records receipt modification times as filesystem observations;
exact start/per-case timestamps remain missing coverage. These receipts do not
establish full draft testing conformance, independent owner sign-off or consumer
acceptance. No failed attempts were observed or discarded in this slice.
