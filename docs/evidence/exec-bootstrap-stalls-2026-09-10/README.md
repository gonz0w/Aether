# Exec bootstrap-stall containment — 2026-09-10

The actual Rust owner now contains four selected delivery stalls after successful
image commit, final CLOEXEC close and kernel publication:0/16 bytes of the128-byte
bootstrap, or0/16 bytes of the64-byte survivor table. The writer stays open. The
replacement cannot complete its startup receiver; the owner observes no application
request across256 bounded polls, verifies the live source and matching published
commit, stops source/backend/peer, checks each retained kind3/detail144 terminal,
then closes endpoints and reclaims. Four cases each repeat two generations and six
reclaims. No table resend, old-image resumption or forwarded application I/O occurs.

The [pre-code selection](../../NATIVE-SHELL-STARTUP.md#exec-bootstrap-stall-containment-selection--2026-09-10)
and [native reference](../../NATIVE-CONNECTIONS.md#exec-bootstrap-stall-containment--2026-09-10)
record authority, bounds and cleanup. Existing bounded observation and containment
helpers are reused. Kernel execution and application readiness are distinct. No
new native ABI, service, dependency, SDK change, sibling edit or release-pin update.

## Qualification

All181 connections cases, five launch cases and host checks pass. Host discovery
includes99 Python tests and the five Rust descriptor tests. Existing reference
commands reproduce the complete suite; no new CLI entry point is introduced.
Mode timing files bind command/start UTC/elapsed/exit status; reports bind target
inputs, tools/firmware and case oracles. Target suites remain within1800-second
review budgets. Prior command/M4 runs are historical, not fresh evidence here.

| Deliberate mutation | Required observation |
| --- | --- |
| Replacement reads only16 table bytes, zero-pads the rest and reaches read(0) | Owner2060, zero reclaims |
| Source stop omitted | Owner2051, zero reclaims |

The short table contains every nonzero survivor entry, so its byte comparison can
pass if receipt completeness is ignored. The first control exercises real C
application traffic, which the owner refuses to forward. Its retained log has no
spontaneous terminal lines. The stop control fails on retained state before reclaim.
Generic compilation failures, crashes or timeouts cannot replace the named checks.

## Preserved infrastructure attempts

- `attempt1/`: the workspace disk filled during compilation. Host, launch and
  connections all failed. After every process completed, only disposable build
  objects under `.zig-cache/o` were removed, freeing about4.6 GiB.
- `attempt2/`: Zig metadata still pointed to the removed build runner. All suites
  failed before target execution. After completion, the remaining disposable
  `.zig-cache` was removed. The unchanged runtime inputs passed on the clean retry.

All source snapshots, logs and generated target files from both attempts remain
archived and are read back for hash verification. No qualification evidence or
source files were removed to recover space. Cache cleanup is not evidence disposal.

`sources.json`/`sources.tar.gz` bind final source/documentation; `run-sources.*` retain
pre-run inputs. `change.patch` compares the verified close-containment snapshot.
`artifacts.json`/`artifacts.tar.gz` retain all final target files. `compatibility.json`
checks175 prior payloads outside entropy bytes32..79 and identical kernel load
segments/entry. Clean-cache rebuilds changed only the nonloaded .debug_line section;
whole ELF identity is not claimed. collector-attempt1.py/log preserve the initial
overstrict whole-file comparison and its classification correction.
`qualification.json` records 239 source files,3,376 artifact files and a6,648-byte maximum owner within
the8,192-byte limit.
`final-checks.json` records post-documentation host, Rust/C format, workflow,
standards and whitespace checks. The prior manifest and pinned simplicity digest
and four files are verified. `manifest.json` seals the packet except itself.

## Remaining scope

These streams stall with writers open; EOF and malformed bootstrap/table recovery
are not covered. Fixed private RAM backends are stopped as entire domains, which
is not persistent-storage recovery or preservation of another process's shared
open descriptions. Native commit replies remain direct traps without lost-reply
injection. Cross-process shared-holder exec, live signal/stale-mapping transitions,
public execve and independent installed SDK/dash acceptance remain open.

Next qualify EOF/malformed-record rejection with precise retained terminal and
cleanup observations. R1 remains unfinished.
