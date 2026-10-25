# Complete-error replies and cleanup — 2026-09-07

The direct conformance client now routes copy errors through explicit cleanup.
This tests actual musl read/write/close over scoped AECAT001 roles, not Toybox.
The owner injects exactly one complete EIO reply at a selected request and checks
that all remaining requests are consuming closes. It independently reads backend
bytes and verifies terminal EOF, backend stale denial and four native reclaims
across two generations. No kernel ABI, resource limit or dependency changed.

| Case | Expected terminal status | Input consumed / stdout committed / stderr committed |
| --- | --- | --- |
| Read EIO after one copy | 1 | 11 / 11 / 0 |
| Write EIO after one copy | 1 | 22 / 11 / 0 |
| Usage diagnostic EIO | 64 | 0 / 0 / 16 |
| Input close EIO | 1 | 32 / 32 / 0 |
| Output close EIO | 1 | 32 / 32 / 0 |
| Diagnostic close EIO | 1 | 32 / 32 / 0 |
| Usage diagnostic close EIO | 64 | 0 / 0 / 37 |

Each byte sequence must equal the relevant fixture prefix; input storage remains
unchanged. EIO is injected before forwarding a rejected data request, after prior
successful transfers. This is not ambiguous partial commitment of that request.
Close EIO is a complete acknowledgment of owner alias consumption, allowing later
roles to close; backend destruction and native reclaim remain separate observations.
No new I/O-error message is proposed or tested. Diagnostic-prefix failure uses
the existing Aether-authored usage proposal, not an upstream Toybox string.

Three deliberately broken clients force success, omit the diagnostic close or
retry the failed write. They must reject at owner1501, 1503 and1530 respectively;
generic panic or watchdog expiration is not acceptance. The injection-occurrence
check rejects missing injection at1531. See [pre-code contract](contract.md),
[local reference](../../NATIVE-CAT.md#complete-error-replies-and-cleanup) and
[reviewed consumer request](review-inputs/TOYBOX-NATIVE-CAT.md).

## Reproduction

Run `python3 scripts/launch_smoke.py --command-runner` with
`--libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku` and
`--tools-lock /Users/cam/DEV/Aether-userland/experiments/musl-reference/tools.lock.json`.
Run `--connections` and `--inherited-launch` with the same SDK and lock for shared
header regressions. Host command: `zig build test --cache-dir .zig-cache
--global-cache-dir .zig-cache/global`. Scoped Clang21/Rust2024 formatting and
workflow checks accompany these runs. transport.h retains its legacy style for
the conditional/comment-only extension of the existing consuming-close rule.

## Limits

Actual Toybox callbacks, stdio flush/ferror, SDK initialization, EINTR behavior,
lost/malformed replies, local finalization re-entry and abnormal stop remain open.
The current complete replies do not qualify uncertain close or no-replay behavior
after a lost response. No CAT row or independent userland acceptance follows.
UL-059 stays at its independent consumer handoff boundary; assembled R1 remains
open. Release pins, the previous handoff bundle and sibling repositories are
preserved. Timing evidence covers whole runs, not per-case timestamps; independent
review and extended coverage remain unavailable.

## Qualification

All first attempts pass: 182 command cases (172 previous plus 10 new), six
connections and nine inherited-launch cases. All 98 Python host tests, Zig tests,
offline pins, workflow and scoped C/Rust formatting checks pass. Three receipts
match final frozen runtime sources; all 34 kernel/build inputs and SDK/libc/tool-lock
identities match the preceding usage qualification. Largest new owner:
5,928/8,192 bytes. No limit increased and no failed attempt was discarded.

`final-artifacts.tar.gz` retains frozen sources, compiled clients/backends,
argument artifacts, native envelopes and raw logs. ISOs, duplicate installed boot
files and kernel.elf are omitted with their identities in retained receipts.
Qualification/timing files and manifest bind the evidence. Archived source and
argument bytes are rechecked independently. The prior UL-059 bundle artifacts
remain byte-identical. Archive identity does not establish consumer acceptance.
